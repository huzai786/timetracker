import time
import pygame 
import csv, os  
from datetime import datetime, date
# from pn532pi import Pn532I2c, Pn532

# Pygame initialization
pygame.init()

# Load sound
clock_in_sound = pygame.mixer.Sound("clock_in.mp3")

# Function to load employee data from a CSV file
def load_employees(from_file):
    employees = {}
    with open(from_file, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the first row (header)
        for row in csv_reader:
            employee_id = int(row[0])  # Convert ID to integer
            employee_uid = row[1]
            employee_name = row[2]
            employees[employee_id] = {'uid': employee_uid, 'name': employee_name}
    return employees
 
# Function to check for duplicate clock-ins
def check_duplicate_clock_in(employee_id, current_time, clock_ins_file, interval_seconds=120):
    if os.path.exists(clock_ins_file):
        with open(clock_ins_file, mode='r') as clock_ins_file:
            csv_reader = csv.reader(clock_ins_file, delimiter=';')
            last_clock_in_time = None
            for row in csv_reader:
                if row[0] == str(employee_id):
                    # Find the last recorded clock-in time for the employee
                    last_clock_in_time = row[-1] if len(row) > 0 else None

            if last_clock_in_time:
                # Calculate the time difference between the last clock-in time and the current time
                last_clock_in_time_dt = datetime.strptime(last_clock_in_time, "%H:%M:%S")
                current_time_dt = datetime.strptime(current_time, "%H:%M:%S")
                time_difference = (current_time_dt - last_clock_in_time_dt).total_seconds()
                # If the time difference is less than the specified interval, it's a duplicate clock-in
                if time_difference < interval_seconds:
                    return True
    return False

# Function to record clock-ins
def record_clock_in(employee_id, employee_name, clock_ins_file):
    current_date = date.today().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    # Play clocking sound
    clock_in_sound.play()

    # Check if there's already a row for the employee on the same day
    row_updated = False
    rows = []

    if os.path.exists(clock_ins_file):
        with open(clock_ins_file, mode='r') as clock_ins_file:
            csv_reader = csv.reader(clock_ins_file, delimiter=';')
            rows = list(csv_reader)

    for row in rows:
        if row[0] == str(employee_id) and row[2] == current_date:
            # If the row exists, add the clock-in time to the existing row
            row.append(current_time)
            row_updated = True
            break

    # If no row was found to update, add a new row
    if not row_updated:
        rows.append([employee_id, employee_name, current_date, current_time])

    # Write the updated rows to the CSV file
    with open(clock_ins_file, mode='w') as clock_ins_file:
        csv_writer = csv.writer(clock_ins_file, delimiter=';')
        csv_writer.writerows(rows)

# PN532 initialization (assuming this part exists elsewhere in the code)
pn532 = PN532_I2C(debug=False, reset=20, req=16)
pn532.SAM_configuration()

# File containing employee data
employee_file = 'employee_data.csv'

try:
    print("Waiting for cards...")

    # Load employee data from CSV file
    employees = load_employees(employee_file)

    while True:
        uid = pn532.read_passive_target(timeout=0.5)

        if uid is not None:
            uid_str = ''.join(['{:02X}'.format(x) for x in uid])  # Convert UID to hexadecimal string

            for employee_id, employee_data in employees.items():
                if uid_str == employee_data['uid']:
                    employee_name = employee_data['name']
                    # Create CSV file name for the current day
                    clock_ins_file = date.today().strftime("%Y-%m-%d") + ".csv"
                    # Check if the file exists, if not, create it
                    if not os.path.exists(clock_ins_file):
                        with open(clock_ins_file, mode='w'): pass
                    # Record the clock-in in the file for the current day
                    record_clock_in(employee_id, employee_name, clock_ins_file)
                    print("Clocking:", employee_id)
                    break
                else:
                    clock_in_sound = pygame.mixer.Sound("invalid.mp3")
                    print("Unregistered card:", uid_str)

        time.sleep(4)

except KeyboardInterrupt:
    print("Program terminated by the user.")

finally:
    GPIO.cleanup()
