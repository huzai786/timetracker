from django.db import models

class Schedule(models.Model):
    schedule_name = models.CharField(max_length=200)
    starttime = models.TimeField()
    endtime = models.TimeField()
    breaktime = models.TimeField()

    def __str__(self):
        return f'{self.schedule_name} - ({self.starttime.strftime("%I:%M %p")} - {self.endtime.strftime("%I:%M %p")})'

EMPLOYEE_FLEXIBILITY = [
    ("Flexible", "Flexible"),
    ("Strict", "Strict") 
]

class Employees(models.Model):
    uid = models.IntegerField(primary_key=True, unique=True, null=False, blank=False)
    name = models.CharField(max_length=200)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True)
    # on_leave = models.BooleanField()
    employee_flexibility = models.CharField(max_length=100, choices=EMPLOYEE_FLEXIBILITY)
    created = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.name}" 
    
CLOCKING_INCIDENT = [
    ("CLOCK IN", "CLOCK IN"),
    ("CLOCK OUT", "CLOCK OUT"),
    ("CLOCK IN OVERTIME", "CLOCK IN OVERTIME"),
    ("CLOCK OUT OVERTIME", "CLOCK OUT OVERTIME"),
]

class Clocking(models.Model):
    date = models.DateField()
    time = models.TimeField()
    incident = models.CharField(max_length=200, choices=CLOCKING_INCIDENT)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name="clockings")

    def __str__(self):
        return self.time.strftime("%I:%M %p")
