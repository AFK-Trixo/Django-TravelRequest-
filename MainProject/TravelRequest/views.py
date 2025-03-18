"""
This file contains endpoints for:
    - Authentication (login, logout)
    - Employee travel request CRUD operations
    - Manager travel request operations (listing, approving, rejecting, etc.)
    - Admin operations for travel requests, employees, and managers

Each view uses Django REST Framework’s token authentication and permission
classs to ensure only authenticated users can access protected endpoints
"""

from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token

from .models import TravelRequests, Employees, Managers, Admins
from .serializers import TravelRequestSerializer, EmployeeSerializer, ManagerSerializer, AdminSerializer

User = get_user_model()

def get_employee_from_user(user):
    """
    Retrieve an Employee profile matching the provided Django User's email.

    Args:
        user (User): The Django User object.

    Returns:
        Employees or None: The corresponding Employee record, or None if not found.
    """
    try:
        return Employees.objects.get(email=user.email)
    except Employees.DoesNotExist:
        return None

def get_manager_from_user(user):
    """
    Retrieve a Manager profile matching the provided Django User's email.

    Args:
        user (User): The Django User object.

    Returns:
        Managers or None: The corresponding Manager record, or None if not found.
    """
    try:
        return Managers.objects.get(email=user.email)
    except Managers.DoesNotExist:
        return None

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Log in a user and return a token.

    Expects a JSON body with 'username' and 'password'. Uses Django's authenticate
    to verify credentials. If successful, returns a token.

    Returns:
        Response: JSON with the token and success message, or error message.
    """
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response({'error': 'Please provide username and password'},
                        status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'message': 'Login successful'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Log out the current user by deleting their token.

    Returns:
        Response: JSON message confirming logout.
    """
    request.auth.delete()  
    return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def employee_requests_list_create(request):
    """
    List or create travel requests for the logged-in employee.

    GET:
        Returns all travel requests associated with the employee.
    POST:
        Creates a new travel request with provided data.

    Returns:
        Response: JSON data of travel requests or error messages.
    """
    employee = get_employee_from_user(request.user)
    if not employee:
        return Response({'error': 'Employee profile not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        qs = TravelRequests.objects.filter(employee=employee)
        serializer = TravelRequestSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    serializer = TravelRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def employee_requests_detail(request, pk):
    """
    Retrieve, update, or delete a specific travel request for the logged-in employee.

    Args:
        pk (int): Primary key of the travel request.

    Returns:
        Response: JSON data of the travel request, updated data, or deletion confirmation.
    """
    employee = get_employee_from_user(request.user)
    if not employee:
        return Response({'error': 'Employee profile not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        travel_request = TravelRequests.objects.get(pk=pk, employee=employee)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = TravelRequestSerializer(travel_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'PUT':
        if travel_request.status not in ['pending', 'FI_required']:
            return Response({'error': 'Cannot update request'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TravelRequestSerializer(travel_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        if travel_request.status not in ['pending', 'FI_required']:
            return Response({'error': 'Cannot delete request'}, status=status.HTTP_400_BAD_REQUEST)
        travel_request.delete()
        return Response({'message': 'Request deleted'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_requests_list(request):
    """
    List travel requests assigned to the logged-in manager, with optional filtering.

    Optional query parameters:
        - id: Filter by travel request ID.
        - name: Filter by employee name (first or last).
        - from_date: Filter for travel requests with a from_date greater than or equal to this date.
        - to_date: Filter for travel requests with a to_date less than or equal to this date.
        - status: Filter by travel request status.
        - sort_by: Sort the results by a specific field (use a minus sign for descending order).

    Returns:
        Response: JSON list of filtered travel requests.
    """
    manager = get_manager_from_user(request.user)
    if not manager:
        return Response({'error': 'Manager profile not found'}, status=status.HTTP_404_NOT_FOUND)
    qs = TravelRequests.objects.filter(manager=manager)
    if request.GET.get('id'):
        qs = qs.filter(id=request.GET.get('id'))
    if request.GET.get('name'):
        name = request.GET.get('name')
        qs = qs.filter(Q(employee__first_name__icontains=name) | Q(employee__last_name__icontains=name))
    if request.GET.get('from_date'):
        qs = qs.filter(from_date__gte=request.GET.get('from_date'))
    if request.GET.get('to_date'):
        qs = qs.filter(to_date__lte=request.GET.get('to_date'))
    if request.GET.get('status'):
        qs = qs.filter(status=request.GET.get('status'))
    if request.GET.get('sort_by'):
        qs = qs.order_by(request.GET.get('sort_by'))
    serializer = TravelRequestSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_requests_detail(request, pk):
    """
    Retrieve details of a specific travel request assigned to the logged-in manager.

    Args:
        pk (int): The primary key of the travel request.

    Returns:
        Response: JSON data of the travel request.
    """
    manager = get_manager_from_user(request.user)
    if not manager:
        return Response({'error': 'Manager profile not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        travel_request = TravelRequests.objects.get(pk=pk, manager=manager)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TravelRequestSerializer(travel_request)
    return Response(serializer.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manager_requests_approve(request, pk):
    """
    Approve a travel request assigned to the logged-in manager.

    Args:
        pk (int): The primary key of the travel request.

    Expects:
        A JSON body with an optional "manager_note".

    Returns:
        Response: Confirmation message if approved.
    """
    manager = get_manager_from_user(request.user)
    if not manager:
        return Response({'error': 'Manager profile not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        travel_request = TravelRequests.objects.get(pk=pk, manager=manager)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    travel_request.status = 'approved'
    travel_request.manager_note = request.data.get('manager_note', '')
    travel_request.save()
    return Response({'message': 'Request approved'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manager_requests_reject(request, pk):
    """
    Reject a travel request assigned to the logged-in manager.

    Args:
        pk (int): The primary key of the travel request.

    Expects:
        A JSON body with an optional "manager_note".

    Returns:
        Response: Confirmation message if rejected.
    """
    manager = get_manager_from_user(request.user)
    if not manager:
        return Response({'error': 'Manager profile not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        travel_request = TravelRequests.objects.get(pk=pk, manager=manager)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    travel_request.status = 'rejected'
    travel_request.manager_note = request.data.get('manager_note', '')
    travel_request.save()
    return Response({'message': 'Request rejected'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manager_requests_fi_request(request, pk):
    """
    Request further information for a travel request assigned to the logged-in manager.

    Args:
        pk (int): The primary key of the travel request.

    Expects:
        A JSON body with an optional "manager_note".

    Returns:
        Response: Confirmation message if updated.
    """
    manager = get_manager_from_user(request.user)
    if not manager:
        return Response({'error': 'Manager profile not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        travel_request = TravelRequests.objects.get(pk=pk, manager=manager)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    travel_request.status = 'FI_required'
    travel_request.manager_note = request.data.get('manager_note', '')
    travel_request.save()
    return Response({'message': 'Further information requested'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def manager_requests_update(request, pk):
    """
    Update details of a travel request assigned to the logged-in manager.

    Args:
        pk (int): The primary key of the travel request.

    Expects:
        JSON data with the fields to update.

    Returns:
        Response: Updated travel request data or error messages.
    """
    manager = get_manager_from_user(request.user)
    if not manager:
        return Response({'error': 'Manager profile not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        travel_request = TravelRequests.objects.get(pk=pk, manager=manager)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TravelRequestSerializer(travel_request, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_requests_list(request):
    """
    Retrieve a list of all travel requests (admin view) with optional filtering.

    Optional query parameters:
        - id: Filter by request ID.
        - name: Filter by employee's first or last name.
        - from_date: Filter requests with a from_date on or after this date.
        - to_date: Filter requests with a to_date on or before this date.
        - status: Filter by request status.
        - sort_by: Field to sort the results.

    Returns:
        Response: JSON list of travel requests.
    """
    qs = TravelRequests.objects.all()
    if request.GET.get('id'):
        qs = qs.filter(id=request.GET.get('id'))
    if request.GET.get('name'):
        name = request.GET.get('name')
        qs = qs.filter(Q(employee__first_name__icontains=name) | Q(employee__last_name__icontains=name))
    if request.GET.get('from_date'):
        qs = qs.filter(from_date__gte=request.GET.get('from_date'))
    if request.GET.get('to_date'):
        qs = qs.filter(to_date__lte=request.GET.get('to_date'))
    if request.GET.get('status'):
        qs = qs.filter(status=request.GET.get('status'))
    if request.GET.get('sort_by'):
        qs = qs.order_by(request.GET.get('sort_by'))
    serializer = TravelRequestSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_requests_detail(request, pk):
    """
    Retrieve details of a specific travel request for admin.

    Args:
        pk (int): The primary key of the travel request.

    Returns:
        Response: JSON data of the travel request.
    """
    try:
        travel_request = TravelRequests.objects.get(pk=pk)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TravelRequestSerializer(travel_request)
    return Response(serializer.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_requests_close(request, pk):
    """
    Close an approved travel request (admin view).

    Args:
        pk (int): The primary key of the travel request.

    Returns:
        Response: Confirmation message if closed, or error message if not approved.
    """
    try:
        travel_request = TravelRequests.objects.get(pk=pk)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if travel_request.status == 'approved':
        travel_request.status = 'closed'
        travel_request.is_closed = True
        travel_request.save()
        return Response({'message': 'Request closed'}, status=status.HTTP_200_OK)
    return Response({'error': 'Request is not approved'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_requests_update(request, pk):
    """
    Update a travel request in the admin view.

    Args:
        pk (int): The primary key of the travel request.

    Expects:
        JSON data with the updated fields.

    Returns:
        Response: Updated travel request data or error messages.
    """
    try:
        travel_request = TravelRequests.objects.get(pk=pk)
    except TravelRequests.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TravelRequestSerializer(travel_request, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_employees_list_create(request):
    """
    List all employees or create a new employee (admin view).

    GET:
        Returns a list of all employees.
    POST:
        Creates a new employee and automatically creates a corresponding Django User
        if one does not already exist.
    
    Returns:
        Response: Employee data or error messages.
    """
    if request.method == 'GET':
        employees = Employees.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        employee = serializer.save()
        if not User.objects.filter(username=employee.email).exists():
            User.objects.create_user(username=employee.email, email=employee.email, password=request.data.get("password"))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_employees_detail(request, pk):
    """
    Retrieve, update, or delete a specific employee (admin view).

    Args:
        pk (int): The primary key of the employee.

    Returns:
        Response: Employee data or confirmation/error message.
    """
    try:
        employee = Employees.objects.get(pk=pk)
    except Employees.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'PUT':
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    employee.delete()
    return Response({'message': 'Employee deleted'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_managers_list_create(request):
    """
    List all managers or create a new manager (admin view).

    GET:
        Returns a list of all managers.
    POST:
        Creates a new manager and automatically creates a corresponding Django User
        if one does not already exist.
    
    Returns:
        Response: Manager data or error messages.
    """
    if request.method == 'GET':
        managers = Managers.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    serializer = ManagerSerializer(data=request.data)
    if serializer.is_valid():
        manager = serializer.save()
        if not User.objects.filter(username=manager.email).exists():
            User.objects.create_user(username=manager.email, email=manager.email, password=request.data.get("password"))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_managers_detail(request, pk):
    """
    Retrieve, update, or delete a specific manager (admin view).

    Args:
        pk (int): The primary key of the manager.

    Returns:
        Response: Manager data or confirmation/error message.
    """
    try:
        manager = Managers.objects.get(pk=pk)
    except Managers.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = ManagerSerializer(manager)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'PUT':
        serializer = ManagerSerializer(manager, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    manager.delete()
    return Response({'message': 'Manager deleted'}, status=status.HTTP_200_OK)
