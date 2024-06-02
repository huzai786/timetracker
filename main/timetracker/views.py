import json, io, calendar
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from datetime import date, datetime
from collections import defaultdict
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from timetracker.models import Schedule, Employees, Clocking
from .forms import ScheduleForm, EmployeeForm, ClockingForm, ReportForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from timetracker.user_report import generate_report_pdf
from django.http import FileResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.translation import gettext_lazy as _

def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")

def superuser_required(user):
    return user.is_superuser

# schedule part
@login_required
def list_schedules(request: HttpRequest):
    schls = Schedule.objects.all()
    return render(request, "schedule/list_schedule.html", {"schedules": schls})

@user_passes_test(superuser_required)
@login_required
def create_schedule(request: HttpRequest):
    if request.method == 'GET':
        form = ScheduleForm()
        return render(request, "schedule/create_schedule.html", {"form": form})
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            instance: Schedule = form.save()
            instance.save()
            messages.success(request, "Schedule created successfully!")
            return redirect("list_schedules")
        else:
            messages.add_message(request, messages.ERROR, "Form is Invalid!")
            return render(request, "schedule/create_schedule.html", {"form": form})

@user_passes_test(superuser_required)
@login_required
def update_schedule(request: HttpRequest, schedule_id: int):
    schedule = get_object_or_404(Schedule, pk=schedule_id)

    if request.method == 'GET':
        form = ScheduleForm(instance=schedule)
        return render(request, "schedule/update_schedule.html", {"form": form, "schedule": schedule})

    elif request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect("list_schedules")
        else:
            return render(request, "schedule/update_schedule.html", {"form": form})

@user_passes_test(superuser_required)
@login_required
def delete_schedule(request: HttpRequest, schedule_id: int):
    if request.method == 'GET':
        obj = get_object_or_404(Schedule, pk=schedule_id)
        return render(request, "schedule/delete_schedule.html", {"schedule": obj})
    
    if request.method == 'POST':
        obj = get_object_or_404(Schedule, pk=schedule_id)
        obj.delete()
        return redirect("list_schedules")

# employee part
@login_required
def list_employees(request: HttpRequest):
    employees = Employees.objects.all()
    return render(request, "employee/list_employee.html", {"employees": employees})

@login_required
def get_employee(request: HttpRequest, employee_id: int):
    emp = get_object_or_404(Employees, pk=employee_id)
    return render(request, "employee/get_employee.html", {"employee": emp})

@user_passes_test(superuser_required)
@login_required
def create_employees(request: HttpRequest):
    if request.method == 'GET':
        form = EmployeeForm()
        return render(request, "employee/create_employee.html", {"form": form})
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee created successfully!")
            return redirect("list_employees")
        else:
            messages.add_message(request, messages.ERROR, "Form is Invalid!")
            return render(request, "employee/create_employee.html", {"form": form})

@user_passes_test(superuser_required)
@login_required
def update_employees(request: HttpRequest, employee_id: int):
    emp = get_object_or_404(Employees, pk=employee_id)

    if request.method == 'GET':
        form = EmployeeForm(instance=emp)
        return render(request, "employee/update_employee.html", {"form": form, "emp": emp})

    elif request.method == 'POST':
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            return redirect("list_employees")
        else:
            return render(request, "employee/update_employee.html", {"form": form})

@user_passes_test(superuser_required)
@login_required
def delete_employees(request: HttpRequest, employee_id: int):
    if request.method == 'GET':
        obj = get_object_or_404(Employees, pk=employee_id)
        return render(request, "employee/delete_employee.html", {"emp": obj})
    
    if request.method == 'POST':
        obj = get_object_or_404(Employees, pk=employee_id)
        obj.delete()
        return redirect("list_employees")

# clocking section
@login_required
def view_clockings(request: HttpRequest, employee_id: int):
    emp = get_object_or_404(Employees, pk=employee_id)
    
    # Get the selected month and year from the request, or default to the current month and year
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    if selected_month and selected_year:
        selected_month = int(selected_month)
        selected_year = int(selected_year)
    else:
        today = date.today()
        selected_month = today.month
        selected_year = today.year
    
    clockings = emp.clockings.filter(date__year=selected_year, date__month=selected_month).order_by('date', 'time')
    
    grouped_clockings = defaultdict(lambda: {'clock_in': None, 'clock_out': None, 'clock_in_id': None, 'clock_out_id': None})
    for clocking in clockings:
        if clocking.incident == "CLOCK IN":
            grouped_clockings[clocking.date]["clock_in_id"] = clocking.id
            grouped_clockings[clocking.date]['clock_in'] = clocking.time
        elif clocking.incident == "CLOCK OUT":
            grouped_clockings[clocking.date]["clock_out_id"] = clocking.id
            grouped_clockings[clocking.date]['clock_out'] = clocking.time
    
    grouped_clockings = dict(grouped_clockings)
    
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    month_string = calendar.month_name[selected_month]
    year_now = date.today().year

    return render(request, "clocking/clocking.html", {
        "employee": emp,
        "grouped_clockings": grouped_clockings,
        "current_month": selected_month,
        "current_year": selected_year,
        "months": months,
        "year_now": year_now,
        "month_string": month_string,
    })

@user_passes_test(superuser_required)
@login_required
def create_clocking(request: HttpRequest, employee_id: int):
    emp = get_object_or_404(Employees, pk=employee_id)
    if request.method == 'GET':
        form = ClockingForm(initial={'employee': emp})
        return render(request, "clocking/create_clocking.html", {"form": form, "employee": emp})
    
    if request.method == 'POST':
        form = ClockingForm(request.POST)
        if form.is_valid():            
            clocking: Clocking = form.save(commit=False)
            clocking.employee = emp
            try:
                c = Clocking.objects.get(date=clocking.date, employee=emp)
                if clocking.incident == "CLOCK IN":
                    if c.incident == 'CLOCK IN' and clocking.time < c.time:
                        c.time = clocking.time
                        c.save()
                    else:
                        clocking.save()

                elif clocking.incident == "CLOCK OUT":
                    if clocking.incident == 'CLOCK OUT' and clocking.time > c.time:
                        c.time = clocking.time
                        c.save()
                    else:
                        clocking.save()
                    
            except Clocking.DoesNotExist:
                clocking.employee = emp
                clocking.save()

            messages.success(request, "Clocking created successfully!")
            return redirect("view_clockings", employee_id=employee_id)
        else:
            messages.add_message(request, messages.ERROR, "Form is Invalid!")
            return render(request, "clocking/create_clocking.html", {"form": form, "employee": emp})

@user_passes_test(superuser_required)
@login_required
def edit_clocking(request: HttpRequest, clocking_id: int):
    clocking = get_object_or_404(Clocking, pk=clocking_id)
    if request.method == 'POST':
        form = ClockingForm(request.POST, instance=clocking)
        if form.is_valid():
            form.save()
            messages.success(request, "Clocking record updated successfully!")
            return redirect('view_clockings', employee_id=clocking.employee.uid)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ClockingForm(instance=clocking)

    return render(request, "clocking/edit_clocking.html", {
        "form": form,
        "clocking": clocking
    })

@user_passes_test(superuser_required)
@login_required
def delete_clocking(request: HttpRequest, clocking_id: int):
    clocking = get_object_or_404(Clocking, pk=clocking_id)
    if request.method == 'GET':
        return render(request, "clocking/delete_clocking.html", {"clocking": clocking})
    
    if request.method == 'POST':
        clocking.delete()
        return redirect('view_clockings', employee_id=clocking.employee.uid)

# attendance part

@login_required
def view_attendance(request, employee_id):
    emp = get_object_or_404(Employees, pk=employee_id)
    # Get the selected month and year from the request, or default to current month and year
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    if selected_month and selected_year:
        selected_month = int(selected_month)
        selected_year = int(selected_year)
    else:
        today = date.today()
        selected_month = today.month
        selected_year = today.year
    
    # Get all clocking dates with incident "CLOCK IN"
    clockings = emp.clockings.filter(incident="CLOCK IN").values_list('date', flat=True)
    
    # Generate a list of all days in the selected month
    days_in_month = calendar.monthrange(selected_year, selected_month)[1]
    calendar_days = [date(selected_year, selected_month, day) for day in range(1, days_in_month + 1)]
    
    # Filter the calendar days to start from the employee's creation date
    creation_date = emp.created
    today = date.today()
    calendar_days = [day for day in calendar_days if day >= creation_date and day <= today]
    
    # Create attendance records
    attendance = {}
    for day in calendar_days:
        attendance[day] = "Present" if day in clockings else "Absent"
    
    # Prepare months for the select dropdown
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    month_string = calendar.month_name[selected_month]
    year_now = date.today().year
    return render(request, "attendence.html", {
        "employee": emp,
        "attendance": attendance,
        "current_month": selected_month,
        "current_year": selected_year,
        "months": months,
        "year_now": year_now,
        "month_string": month_string
    })

def login_view(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect("home")  
        else:
            messages.error(request, "email or password invalid")
            return render(request, 'accounts/login.html') 
    return render(request, 'accounts/login.html')

@user_passes_test(superuser_required)
@login_required
def generate_report(request: HttpRequest):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            employees = form.cleaned_data['employees']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            print(employees)
            pdf_page_bytes = generate_report_pdf(list(employees), start_date, end_date) 
            response = FileResponse(io.BytesIO(pdf_page_bytes), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="employee_report.pdf"'
            return response
        
    else:
        form = ReportForm()

    return render(request, "reports/generate_reports.html", {'form': form})


@login_required
def view_clocking(request: HttpRequest):
    # Get the selected month and year from the request, or default to the current month and year
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    if selected_month and selected_year:
        selected_month = int(selected_month)
        selected_year = int(selected_year)
    else:
        today = date.today()
        selected_month = today.month
        selected_year = today.year
    
    # Get all clockings for the selected month and year
    clockings = Clocking.objects.filter(date__year=selected_year, date__month=selected_month).order_by('date', 'time')
    
    grouped_clockings = defaultdict(lambda: {'clock_in': None, 'clock_out': None, 'employee': None, 'date': None})
    
    for clocking in clockings:
        key = (clocking.employee.uid, clocking.date)
        if clocking.incident == "CLOCK IN":
            grouped_clockings[key]['clock_in'] = clocking
        elif clocking.incident == "CLOCK OUT":
            grouped_clockings[key]['clock_out'] = clocking
        grouped_clockings[key]['employee'] = clocking.employee
        grouped_clockings[key]['date'] = clocking.date

    grouped_clockings = {k: v for k, v in grouped_clockings.items()}
    
    # Prepare months for the select dropdown
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    month_string = calendar.month_name[selected_month]
    
    # Prepare a list of years around the current year
    current_year = date.today().year
    years = list(range(current_year - 5, current_year + 5 + 1))

    return render(request, "clocking_records.html", {
        "grouped_clockings": grouped_clockings,
        "current_month": selected_month,
        "current_year": selected_year,
        "months": months,
        "years": years,
        "month_string": month_string,
    })

@login_required
def view_overtime(request: HttpRequest, employee_id: int):
    emp = get_object_or_404(Employees, pk=employee_id)
    
    # Get the selected month and year from the request, or default to the current month and year
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    if selected_month and selected_year:
        selected_month = int(selected_month)
        selected_year = int(selected_year)
    else:
        today = date.today()
        selected_month = today.month
        selected_year = today.year
    
    # Get all overtime clock-ins and clock-outs for the selected month and year
    clockings = emp.clockings.filter(
        date__year=selected_year,
        date__month=selected_month,
        incident__in=["CLOCK IN OVERTIME", "CLOCK OUT OVERTIME"]
    ).order_by('date', 'time')
    
    grouped_clockings = defaultdict(lambda: {'clock_in': None, 'clock_out': None, 'employee': None, 'date': None})
    
    for clocking in clockings:
        key = (clocking.employee.uid, clocking.date)
        if clocking.incident == "CLOCK IN OVERTIME":
            grouped_clockings[key]['clock_in'] = clocking
        elif clocking.incident == "CLOCK OUT OVERTIME":
            grouped_clockings[key]['clock_out'] = clocking
        grouped_clockings[key]['employee'] = clocking.employee
        grouped_clockings[key]['date'] = clocking.date

    grouped_clockings = {k: v for k, v in grouped_clockings.items()}
    
    # Prepare months for the select dropdown
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    month_string = calendar.month_name[selected_month]
    year_now = date.today().year

    return render(request, "overtime.html", {
        "employee": emp,
        "grouped_clockings": grouped_clockings,
        "current_month": selected_month,
        "current_year": selected_year,
        "months": months,
        "year_now": year_now,
        "month_string": month_string,
    })


# apis
@csrf_exempt
def get_schedule_api(request: HttpRequest):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            uid = data.get("uid")
            if not uid:
                return JsonResponse({"error": "UID not provided"}, status=400)

            employee = get_object_or_404(Employees, uid=uid)
            schedule = employee.schedule

            response_data = {
                "schedule": {
                    "employee_name": employee.name,
                    "employee_flexibility": employee.employee_flexibility,
                    "starttime": schedule.starttime,
                    "endtime": schedule.endtime,
                    "breaktime": schedule.breaktime
                }
            }
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Employees.DoesNotExist:
            return JsonResponse({"schedule": None})

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)

@csrf_exempt
def create_clockin_api(request: HttpRequest):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            uid = data.get("uid")
            overtime = data.get("overtime")
            time_str = data.get("time")

            dt_obj = datetime.combine(datetime.now().date(), datetime.strptime(time_str, "%H:%M:%S").time())
            employee = get_object_or_404(Employees, pk=uid)

            if overtime:
                clocking = Clocking.objects.create(employee=employee, date=dt_obj.date(), time=dt_obj.time(), incident="CLOCK IN OVERTIME")
            else:
                clocking = Clocking.objects.create(employee=employee, date=dt_obj.date(), time=dt_obj.time(), incident="CLOCK IN")
            clocking.save()
            return JsonResponse({"status": "success"}, status=200)

        except KeyError as e:
            return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)

@csrf_exempt
def create_clockout_api(request: HttpRequest):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            uid = data.get("uid")
            overtime = data.get("overtime")
            time_str = data.get("time")

            dt_obj = datetime.combine(datetime.now().date(), datetime.strptime(time_str, "%H:%M:%S").time())
            
            employee = get_object_or_404(Employees, pk=uid)

            if overtime:
                clocking = Clocking.objects.create(employee=employee, date=dt_obj.date(), time=dt_obj.time(), incident="CLOCK OUT OVERTIME")
            else:
                clocking = Clocking.objects.create(employee=employee, date=dt_obj.date(), time=dt_obj.time(), incident="CLOCK OUT")
            clocking.save()

            return JsonResponse({"status": "success"}, status=200)

        except KeyError as e:
            return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)
    
