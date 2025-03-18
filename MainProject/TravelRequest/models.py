"""
This file defines four models:
    1. Managers: Represents a manager with basic personal and departmental information.
    2. Employees: Represents an employee, who is linked to a manager.
    3. Admins: Represents an admin user.
    4. TravelRequests: Represents a travel request submitted by an employee, processed by a manager/admin.
"""



from django.db import models

class Managers(models.Model):
    """
    Model representing a manager.

    Fields:
        first_name (CharField): The manager's first name.
        last_name (CharField): The manager's last name.
        email (EmailField): Unique email address for the manager.
        password (CharField): The manager's password (should be stored as a hash in practice).
        department (CharField): The department the manager oversees (optional).
        status (CharField): The manager's status (default is 'active').
        created_at (DateTimeField): Timestamp of when the record was created.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    department = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the Manager."""
        return f"{self.first_name} {self.last_name} ({self.department})"


class Employees(models.Model):
    """
    Model representing an employee.

    Fields:
        first_name (CharField): The employee's first name.
        last_name (CharField): The employee's last name.
        email (EmailField): Unique email address for the employee.
        password (CharField): The employee's password (should be stored as a hash).
        department (CharField): The department the employee belongs to (optional).
        manager (ForeignKey): Links the employee to a Manager; can be null.
        status (CharField): The employee's status (default is 'active').
        created_at (DateTimeField): Timestamp of when the record was created.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    department = models.CharField(max_length=100, blank=True, null=True)
    manager = models.ForeignKey(Managers, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees_managed')
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the Employee."""
        return f"{self.first_name} {self.last_name} ({self.department})"


class Admins(models.Model):
    """
    Model representing an admin user.

    Fields:
        first_name (CharField): The admin's first name.
        last_name (CharField): The admin's last name.
        email (EmailField): Unique email address for the admin.
        password (CharField): The admin's password (should be hashed).
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        """Return a string representation of the Admin."""
        return f"Admin: {self.first_name} {self.last_name}"


class TravelRequests(models.Model):
    """
    Model representing a travel request.

    Fields:
        STATUS_CHOICES (list): The allowed statuses for a travel request.
        employee (ForeignKey): The employee who created the travel request.
        manager (ForeignKey): The manager responsible for processing the travel request.
        from_date (DateField): The start date of the travel period (optional).
        to_date (DateField): The end date of the travel period (optional).
        location (CharField): The starting location for travel.
        destination (CharField): The destination location.
        travel_mode (CharField): The mode of travel (e.g., Flight, Train).
        lodging_required (BooleanField): Indicates whether lodging is required.
        purpose_of_travel (CharField): The purpose of the travel.
        status (CharField): The current status of the travel request.
        manager_note (TextField): Optional note from the manager.
        admin_note (TextField): Optional note from the admin.
        further_information (TextField): Optional extra information about the travel.
        processed_by (ForeignKey): The admin who processed the travel request (optional).
        resubmission_count (IntegerField): Number of times the request was resubmitted.
        is_closed (BooleanField): Indicates if the request is closed.
        created_at (DateTimeField): Timestamp of when the travel request was created.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('FI_required', 'Further Information Required'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ]
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    manager = models.ForeignKey(Managers, on_delete=models.CASCADE)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    travel_mode = models.CharField(max_length=50)
    lodging_required = models.BooleanField(default=False)
    purpose_of_travel = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    manager_note = models.TextField(blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)
    further_information = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(Admins, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests_processed')
    resubmission_count = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the Travel Request."""
        return f"Travel Request #{self.id} by {self.employee} to {self.destination}"
