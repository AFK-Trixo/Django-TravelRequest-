from django.contrib import admin
from .models import Managers, Employees, Admins, TravelRequests

admin.site.register(Managers)
admin.site.register(Employees)
admin.site.register(Admins)
admin.site.register(TravelRequests)