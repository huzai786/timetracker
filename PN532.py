import time
import pygame 
import csv, os  # noqa
from datetime import datetime, date

# Pygame initialization
pygame.init()

# Load sound
sonido_fichaje = pygame.mixer.Sound("fichaje.mp3")

# Function to load employee data from a CSV file
def cargar_trabajadores(desde_archivo):
    empleados = {}
    with open(desde_archivo, mode='r') as archivo_csv:
        csv_reader = csv.reader(archivo_csv)
        next(csv_reader)  # Skip the first row (header)
        for row in csv_reader:
            id_empleado = int(row[0])  # Convert ID to integer
            uid_empleado = row[1]
            nombre_empleado = row[2]
            empleados[id_empleado] = {'uid': uid_empleado, 'nombre': nombre_empleado}
    return empleados

# Function to check for duplicate clock-ins
def verificar_fichaje_duplicado(id_empleado, hora_actual, archivo_fichajes, intervalo_segundos=120):
    if os.path.exists(archivo_fichajes):
        with open(archivo_fichajes, mode='r') as fichajes_file:
            csv_reader = csv.reader(fichajes_file, delimiter=';')
            ultima_hora_fichaje = None
            for row in csv_reader:
                if row[0] == str(id_empleado):
                    # Find the last recorded clock-in time for the employee
                    ultima_hora_fichaje = row[-1] if len(row) > 0 else None

            if ultima_hora_fichaje:
                # Calculate the time difference between the last clock-in time and the current time
                ultima_hora_fichaje_dt = datetime.strptime(ultima_hora_fichaje, "%H:%M:%S")
                hora_actual_dt = datetime.strptime(hora_actual, "%H:%M:%S")
                diferencia_tiempo = (hora_actual_dt - ultima_hora_fichaje_dt).total_seconds()
                # If the time difference is less than the specified interval, it's a duplicate clock-in
                if diferencia_tiempo < intervalo_segundos:
                    return True
    return False

# Function to record clock-ins
def registrar_fichaje(id_empleado, nombre_empleado, archivo_fichajes):
    fecha_actual = date.today().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M:%S")

    # Play clocking sound
    sonido_fichaje.play()

    # Check if there's already a row for the employee on the same day
    fila_actualizada = False
    filas = []

    if os.path.exists(archivo_fichajes):
        with open(archivo_fichajes, mode='r') as fichajes_file:
            csv_reader = csv.reader(fichajes_file, delimiter=';')
            filas = list(csv_reader)

    for row in filas:
        if row[0] == str(id_empleado) and row[2] == fecha_actual:
            # If the row exists, add the clock-in time to the existing row
            row.append(hora_actual)
            fila_actualizada = True
            break

    # If no row was found to update, add a new row
    if not fila_actualizada:
        filas.append([id_empleado, nombre_empleado, fecha_actual, hora_actual])

    # Write the updated rows to the CSV file
    with open(archivo_fichajes, mode='w') as fichajes_file:
        csv_writer = csv.writer(fichajes_file, delimiter=';')
        csv_writer.writerows(filas)

# PN532 initialization
pn532 = PN532_I2C(debug=False, reset=20, req=16)
pn532.SAM_configuration()

# File containing employee data
archivo_trabajadores = 'datos_trabajadores.csv'

try:
    print("Waiting for cards...")

    # Load employee data from CSV file
    empleados = cargar_trabajadores(archivo_trabajadores)

    while True:
        uid = pn532.read_passive_target(timeout=0.5)

        if uid is not None:
            uid_str = ''.join(['{:02X}'.format(x) for x in uid])  # Convert UID to hexadecimal string

            for id_empleado, datos_empleado in empleados.items():
                if uid_str == datos_empleado['uid']:
                    nombre_empleado = datos_empleado['nombre']
                    # Create CSV file name for the current day
                    archivo_fichajes = date.today().strftime("%Y-%m-%d") + ".csv"
                    # Check if the file exists, if not, create it
                    if not os.path.exists(archivo_fichajes):
                        with open(archivo_fichajes, mode='w'): pass
                    # Record the clock-in in the file for the current day
                    registrar_fichaje(id_empleado, nombre_empleado, archivo_fichajes)
                    print("Clocking:", id_empleado)
                    break
            else:
                sonido_fichaje = pygame.mixer.Sound("invalida.mp3")
                print("Unregistered card:", uid_str)

        time.sleep(4)

except KeyboardInterrupt:
    print("Program terminated by the user.")

finally:
    GPIO.cleanup()