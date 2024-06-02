from datetime import datetime, timedelta
from .models import Employees, Clocking
from django.template.loader import render_to_string
from weasyprint import HTML
import io

def convert_html_to_pdf(html_content):
    # Create a WeasyPrint HTML object
    html = HTML(string=html_content)
    
    # Create an in-memory bytes buffer to store the PDF
    pdf_buffer = io.BytesIO()
    
    # Write the PDF to the bytes buffer
    html.write_pdf(target=pdf_buffer)
    
    # Get the byte data from the buffer
    pdf_data = pdf_buffer.getvalue()
    
    # Close the buffer
    pdf_buffer.close()
    
    return pdf_data

    

def generate_report_pdf(employees: list[Employees], startdate: datetime, enddate: datetime) -> bytes:
    # Prepare the context for the template
    context = {'employees': []}
    
    # Iterate through each employee to collect their clocking data
    for employee in employees:
        records = []
        current_date = startdate
        while current_date <= enddate:
            clock_in = Clocking.objects.filter(employee=employee, date=current_date, incident="CLOCK IN").first()
            clock_out = Clocking.objects.filter(employee=employee, date=current_date, incident="CLOCK OUT").first()
            clock_in_time = clock_in.time.strftime("%I:%M %p") if clock_in else "N/A"
            clock_out_time = clock_out.time.strftime("%I:%M %p") if clock_out else "N/A"
            
            records.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'clock_in': clock_in_time,
                'clock_out': clock_out_time
            })
            current_date += timedelta(days=1)
        
        context['employees'].append({
            'name': employee.name,
            'records': records
        })
    
    # Render the template with the context
    html_string = render_to_string('render_pdf.html', context)
    pdf_bytes = convert_html_to_pdf(html_string)
    return pdf_bytes


