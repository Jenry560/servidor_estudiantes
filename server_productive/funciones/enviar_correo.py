import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
# Obtiene la clave de la API de SendGrid desde las variables de entorno
SENDGRID_API_KEY = os.getenv("SEND_GRID")


def enviar_notificacion(datos):
    fecha_hoy = datetime.now().date()  # Obteniendo la fecha de hoy

    fecha_evento = datetime.strptime(
        datos["fecha"], "%Y-%m-%d"
    )  # Agregando la fecha de envio a formato fecha

    # Si la de evento es mayor o igual a la fecha hoy
    if fecha_evento.date() >= fecha_hoy:
        message = Mail(
            from_email="jenrydev@gmail.com",
            to_emails=datos["correo"],
            subject=datos["titulo"],
            plain_text_content=datos["descripcion"],
        )  # Creando el objeto mensaje
        # Si la fecha del evento es mayor a la fecha de hoy
        if fecha_evento.date() > fecha_hoy:

            fecha_envio = fecha_evento - timedelta(
                days=1
            )  # Restandole un dia a la fecha de envio para que se envie el correo
            message.send_at = int(fecha_envio.timestamp())  # Conviertiendo fechas

        try:
            sg = SendGridAPIClient(
                SENDGRID_API_KEY
            )  # Creando el objeto con la crendenciales de la key para enviar el mensaje
            response = sg.send(message)  # Enviando el mensaje
            print(response.status_code)  # Imprimiendo la respuesta
        except Exception as e:
            print(e)  # Imprimiendo el error
