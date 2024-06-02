from django.urls import path
from timetracker import views

urlpatterns = [
    path('', views.home, name="home"),
    # categories
    path("list-schedules", views.list_schedules, name="list_schedules"), 
    path("create-schedules", views.create_schedule, name="create_schedule"),
    path("update-schedules/<int:schedule_id>/", views.update_schedule, name="update_schedule"), 
    path("delete-schedules/<int:schedule_id>/", views.delete_schedule, name="delete_schedule"), 

    # employee
    path("list-employees", views.list_employees, name="list_employees"), 
    path("employee/<int:employee_id>", views.get_employee, name="get_employee"), 
    path("create-employee", views.create_employees, name="create_employees"),
    path("update-employee/<int:employee_id>/", views.update_employees, name="update_employees"), 
    path("delete-employee/<int:employee_id>/", views.delete_employees, name="delete_employees"), 

    path("clockings/<int:employee_id>/", views.view_clockings, name="view_clockings"), 
    path("create-clocking/<int:employee_id>/", views.create_clocking, name="create_clocking"), 
    path("edit-clocking/<int:clocking_id>/", views.edit_clocking, name="edit_clocking"), 
    path("delete-clocking/<int:clocking_id>/", views.delete_clocking, name="delete_clocking"), 

    path("login", views.login_view, name="login"), 
    path("view_attendence/<int:employee_id>/", views.view_attendance, name="view_attendence"), 

    path("generate_report", views.generate_report, name="generate_report"), 
    path("view-clocking", views.view_clocking, name="view_clocking"), 
    path("view-overtime/<int:employee_id>/", views.view_overtime, name="view_overtime"), 

    # apis
    path('api/get-schedule/', views.get_schedule_api, name='get_schedule'),
    path('api/create-clockin/', views.create_clockin_api, name='create_clockin_api'),
    path('api/create-clockout/', views.create_clockout_api, name='create_clockout_api'),
]
