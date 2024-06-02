from django import forms
from django.forms import ModelForm
from .models import Schedule, Employees, Clocking
import calendar
from datetime import date

class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'
        widgets = {
            'starttime': forms.TimeInput(attrs={'type': 'time'}),
            'endtime': forms.TimeInput(attrs={'type': 'time'}),
            'breaktime': forms.TimeInput(attrs={'type': 'time'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.fields.items():
            self.fields[k].widget.attrs.update({"class": "form-control w-25"})
            
class EmployeeForm(ModelForm):
    class Meta:
        model = Employees
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.fields.items():
            self.fields[k].widget.attrs.update({"class": "form-control w-25"})
            
class ClockingForm(ModelForm):
    class Meta:
        model = Clocking
        fields = ("date", "time", "incident")
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.fields.items():
            self.fields[k].widget.attrs.update({"class": "form-control w-25"})


class ReportForm(forms.Form):
    employees = forms.ModelMultipleChoiceField(
        queryset=Employees.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Select Employees'
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End Date'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'employees':
                field.widget.attrs.update({'class': 'form-control w-25'})