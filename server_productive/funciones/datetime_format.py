from datetime import datetime


# Funcion para cambiar la fecha a 12 hora
def time_formant(fecha_string):

    # Conviertiendo de string a fecha
    fecha = datetime.strptime(fecha_string, "%Y-%m-%dT%H:%M:%S.%f")

    # Cambiando el formato de la fecha a 12 horas
    fecha_doce_hora = fecha.strftime("%Y-%m-%d %I:%M %p")

    return str(fecha_doce_hora)
