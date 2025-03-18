"""
This file defines the following endpoints:
    1. Authentication Endpoints:
        - POST /login/   : Logs a user in and returns a token.
        - POST /logout/  : Logs out the current user by deleting their token.
    
    2. Employee Endpoints:
        - GET  /employee/requests/            : List all travel requests for the logged-in employee.
        - POST /employee/requests/            : Create a new travel request (employee).
        - GET/PUT/DELETE /employee/requests/<pk>/ : Retrieve, update, or delete a specific travel request for the employee.
    
    3. Manager Endpoints:
        - GET  /manager/requests/                     : List all travel requests assigned to the logged-in manager with optional filtering.
        - GET  /manager/requests/<pk>/                : Retrieve details for a specific travel request (manager view).
        - POST /manager/requests/<pk>/approve/        : Approve a travel request.
        - POST /manager/requests/<pk>/reject/         : Reject a travel request.
        - POST /manager/requests/<pk>/fi_request/       : Request further information for a travel request.
        - PUT  /manager/requests/<pk>/update/          : Update a travel request.
    
    4. Admin Endpoints for Requests:
        - GET  /myadmin/requests/                     : List all travel requests in the system with filtering.
        - GET  /myadmin/requests/<pk>/                : Retrieve details for a specific travel request.
        - POST /myadmin/requests/<pk>/close/           : Close an approved travel request.
        - PUT  /myadmin/requests/<pk>/update/          : Update a travel request (admin view).
    
    5. Admin Endpoints for Employee Management:
        - GET  /myadmin/employees/                    : List all employees.
        - POST /myadmin/employees/                    : Create a new employee (also creates a corresponding Django User if needed).
        - GET/PUT/DELETE /myadmin/employees/<pk>/       : Retrieve, update, or delete a specific employee.
    
    6. Admin Endpoints for Manager Management:
        - GET  /myadmin/managers/                     : List all managers.
        - POST /myadmin/managers/                     : Create a new manager (also creates a corresponding Django User if needed).
        - GET/PUT/DELETE /myadmin/managers/<pk>/        : Retrieve, update, or delete a specific manager.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication Endpoints:
    path('login/', views.login_view, name='login_api'),
    path('logout/', views.logout_view, name='logout_api'),

    # Employee Endpoints:
    path('employee/requests/', views.employee_requests_list_create, name='employee-requests-list-create'),
    path('employee/requests/<int:pk>/', views.employee_requests_detail, name='employee-requests-detail'),

    # Manager Endpoints:
    path('manager/requests/', views.manager_requests_list, name='manager-requests-list'),
    path('manager/requests/<int:pk>/', views.manager_requests_detail, name='manager-requests-detail'),
    path('manager/requests/<int:pk>/approve/', views.manager_requests_approve, name='manager-requests-approve'),
    path('manager/requests/<int:pk>/reject/', views.manager_requests_reject, name='manager-requests-reject'),
    path('manager/requests/<int:pk>/fi_request/', views.manager_requests_fi_request, name='manager-requests-fi-request'),
    path('manager/requests/<int:pk>/update/', views.manager_requests_update, name='manager-requests-update'),

    # Admin Endpoints for Requests:
    path('myadmin/requests/', views.admin_requests_list, name='admin-requests-list'),
    path('myadmin/requests/<int:pk>/', views.admin_requests_detail, name='admin-requests-detail'),
    path('myadmin/requests/<int:pk>/close/', views.admin_requests_close, name='admin-requests-close'),
    path('myadmin/requests/<int:pk>/update/', views.admin_requests_update, name='admin-requests-update'),

    # Admin Endpoints for Employee Management:
    path('myadmin/employees/', views.admin_employees_list_create, name='admin-employees-list-create'),
    path('myadmin/employees/<int:pk>/', views.admin_employees_detail, name='admin-employees-detail'),

    # Admin Endpoints for Manager Management:
    path('myadmin/managers/', views.admin_managers_list_create, name='admin-managers-list-create'),
    path('myadmin/managers/<int:pk>/', views.admin_managers_detail, name='admin-managers-detail'),
]
