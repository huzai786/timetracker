from django.contrib import admin
from timetracker.models import Schedule, Employees, Clocking

# Register your models here.
admin.site.register(Schedule)
admin.site.register(Employees)
admin.site.register(Clocking)

