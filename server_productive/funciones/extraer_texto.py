from google.cloud import vision
import os
import re
from datetime import datetime
from dotenv import load_dotenv
import json


fecha_actual = datetime.now()
load_dotenv()

google_credentials = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}

# Crear un archivo JSON temporal con las credenciales
json_file_path = "google_credentials.json"
with open(json_file_path, "w") as json_file:
    json.dump(google_credentials, json_file, indent=4)

# Conectando con google
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_file_path


# Crear un cliente Vision API
client = vision.ImageAnnotatorClient()


def extraer_texto_imagen(imagen):

    content = imagen.read()  # Cargar la imagen
    # Enviar la imagen a la API para obtener descripciones
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    # Extraer las descripciones de la respuesta
    textos = [text.description for text in response.text_annotations]

    datos = organizar_textos(textos)
    return datos


def organizar_textos(textos):

    columnas_calendario = {
        "Fecha": [],
        "Actividades": [],
        "Fecha_original": [],
    }  # Creando un diccionario para guardar las columnas del calario en orden
    periodos = {
        f"Enero - Abril {fecha_actual.year}": [1, 2, 3, 4],
        f"Mayo - Agosto {fecha_actual.year}": [5, 6, 7, 8],
        f"Septimbre - Diciembre {fecha_actual.year}": [9, 10, 11, 12],
    }

    mes_calendario = ""  # Una varible para guardar el mes o periodo del calendario

    for description in textos:
        #  Si hay una descripcion con salto de linea
        if "\n" in description:
            # Destruturando los parrafos
            parrafos = description.split("\n")
            # Recorriendo los parrafo
            for parrafo in parrafos:
                # Si el parrafo esta en la lista de periodo de cuatrimetre y el mes calendario esta vacio
                if parrafo in list(periodos.keys()) and mes_calendario == "":
                    mes_calendario = parrafo  # Asignamos el mes del calendario
                else:
                    # Si el parrafo tiene mas de 11 caractere o tiene semama en el texto y no es actividad
                    if (
                        (len(parrafo) > 11 or ("Semana" in parrafo))
                        and parrafo != "Actividad(es)"
                        and "Vicerrectoría" not in parrafo
                    ):
                        parrafo_nuevo = ""

                        # Eliminando el parrafo extra por el salto de pagina en el calendario si tiene mas de 70 de len es por que hubo un salto de pagina en el calendario
                        if len(parrafo) > 70:
                            # Indice a eliminar osea de parrafo  que sigue por el salto de linea
                            indice_a_eliminar = parrafos.index(parrafo) + 1

                            # Agregando el parrafo nuevo con el la linea del salto de linea del calendario
                            parrafo_nuevo = f"{parrafo} {parrafos[indice_a_eliminar]}"

                            # Eliminando el parrafo siguiente ya que se agrego el parrafo
                            parrafos.pop(indice_a_eliminar)

                        # Si el parrafo nuevo no esta vacio lo manda si no manda el parrafo normal
                        columnas_calendario["Actividades"].append(
                            parrafo if not parrafo_nuevo else parrafo_nuevo
                        )
                    else:
                        # validar fecha y la agrega al columnas_calendario
                        validar_fecha(parrafo, columnas_calendario)

        # Validando que la imagen sea valida
        if len(columnas_calendario["Fecha"]) != 38:
            return []
        agregar_meses(
            columnas_calendario, mes_calendario, periodos
        )  # Funcion que agrega  el mes que corresponde a la fecha segun el periodo

        datos = buscar_fechas_importante(
            columnas_calendario
        )  # Funcion que solo retorna las fechas importantes

        return datos


# Validar Fechas
def validar_fecha(string_fecha, columnas_calendario):
    # Patrón de expresión regular para el formato "dd-mm"
    patron = (
        r"^\s*\d{1,2}\s*(-\s*\d{1,2}\s*[a-zA-Z]*\.?)?|\s*\d{1,2}\s+[a-zA-Z]+\s*\.?$"
    )
    # Lista de string_fechas con el formato esperado

    if re.match(patron, string_fecha):
        columnas_calendario["Fecha"].append(
            string_fecha[0:2]
        )  # Agregando solo los dos primero digitos de la fecha
        columnas_calendario["Fecha_original"].append(
            string_fecha
        )  # Agregando una fecha original para la descripcion


# Funcion para agregar  mesess
def agregar_meses(columnas_calendario, mes_calendario, periodos):

    dias = [
        0
    ]  # Creando un arreglo para guardar la secuecia de la fecha para el cambio de mes
    mes_actual = 0  # Mes actual osea la pocicion 0 del perido de meses

    columna_fecha = columnas_calendario["Fecha"]

    for fecha in columna_fecha:

        # Si la fecha tiene - o " " lo devide el arreglo
        patron_numeros = re.compile(r"\d+")
        numeros = patron_numeros.findall(fecha)

        # Si el la ultima fecha agregada al fecha es mayor a 20 y es menor al numero
        if dias[-1] > 20 and dias[-1] > int(numeros[0]) and int(numeros[0]) < 7:
            mes_actual += 1  # cambiar meses

        # Agregando el mes a la fecha
        columna_fecha[
            columna_fecha.index(fecha)  # Buscar el indice de la fecha en el arreglo
        ] = f"{fecha_actual.year}-0{periodos[mes_calendario][mes_actual]}-{fecha}"  # Agregando el mes la fecha con el mes actual

        dias.append(int(numeros[0]))  # Agregando el dia al arreglo para validar


def buscar_fechas_importante(eventos):
    fechas_importante = []
    # Recorriendo el arreglo
    for x in range(len(eventos["Actividades"])):

        # Creando un diccionario con solo la fecha que quiero tenga las fechas importantes
        descripciones_importantes = [
            "Período Evaluatorio",
            "Evaluación Final",
            "Feriado",
        ]
        descripcion_evento = eventos["Actividades"][x]
        fecha = eventos["Fecha"][x]
        # Buscando su hay un decripcion que coincida con la fecha importantes
        if (
            any(palabra in descripcion_evento for palabra in descripciones_importantes)
            and "Límite" not in descripcion_evento
        ):
            # El titulo si es evaluatorio es parcial si no es feriado
            titulo = (
                "Parciales" if "Evalua" in descripcion_evento else "Dia feriado ITLA"
            )
            # La descripcion_evento si es evaluatorio se la agrega el perido de la fecha si se queda igual
            descripcion_evento = (
                f"{descripcion_evento} perido: {eventos['Fecha_original'][x]}"
                if "Evalua" in descripcion_evento
                else descripcion_evento
            )
            # Agregando las fechas importantes
            fechas_importante.append(
                {
                    "titulo": titulo,
                    "descripcion": descripcion_evento,
                    "fecha": fecha,
                }
            )

    return (
        fechas_importante  # Retornado la fecha importantes osea dia feriado o parcial
    )
