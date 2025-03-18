"""
Serializers for the Travel Request project.

This module defines serializers that convert model instances into JSON format and 
validate incoming data for the following models:
    - Managers: Handles manager data.
    - Employees: Handles employee data.
    - Admins: Handles admin data.
    - TravelRequests: Handles travel request data.
"""

from rest_framework import serializers
from .models import Managers, Employees, Admins, TravelRequests

class ManagerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Managers model.

    Converts Manager model instances to JSON and validates input data for Manager records.
    """
    class Meta:
        model = Managers
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Employees model.

    Converts Employee model instances to JSON and validates input data for Employee records.
    """
    class Meta:
        model = Employees
        fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for the Admins model.

    Converts Admin model instances to JSON and validates input data for Admin records.
    """
    class Meta:
        model = Admins
        fields = '__all__'

class TravelRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the TravelRequests model.

    Converts TravelRequests model instances to JSON and validates incoming data 
    for travel request operations.
    """
    class Meta:
        model = TravelRequests
        fields = '__all__'
