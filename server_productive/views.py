from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import render
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from server_productive.form import RegistroForm
from server_productive.funciones.datetime_format import time_formant
from server_productive.funciones.encriptar import (
    desencriptar_password,
    encriptar_password,
)
from server_productive.funciones.enviar_correo import enviar_notificacion
from server_productive.funciones.extraer_texto import extraer_texto_imagen
from server_productive.models import (
    Biblioteca,
    Contactos,
    Evento,
    Notas,
    Passwords,
    SeccionBiblioteca,
)
from server_productive.serialiazers import (
    BibliotecaSerializer,
    ContactoSerializer,
    EventoSerializer,
    NotasSerializer,
    PasswordSerializer,
    SeccionBibliotecaSerializer,
    UserSerializer,
)
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib import messages


# Clase con la rutas del usuario
class UserViews:

    def registrar_usuario(request):

        # Validamos si el motodo es post
        if request.method == "POST":
            form = RegistroForm(request.POST)  # Tomamos los datos del formulario
            # Validamos si el formulario es valido
            if form.is_valid():
                corro_formulario = form.data[
                    "email"
                ]  # Tomamos el correo del formulario

                # Si el correo esta registrado le enviamos al usario que el correo ya fue registrado
                if User.objects.filter(email=corro_formulario).exists():
                    return render(
                        request,
                        "index.html",
                        {"form": form, "mensaje": "El correo ya esta registrado"},
                    )

                # Si no guardamos los datos en la base de dato
                else:
                    form.save()

                    user = User.objects.get(
                        email=form.data["email"]
                    )  # Buscando el usuario por el email
                    user.set_password(form.data["password"])
                    user.username = form.data["email"]
                    # Encriptando la contrasena
                    user.save()  # Guardo la contrasena encriptada

                    Token.objects.create(user=user)  # Creando un token

                    return render(
                        request,
                        "index.html",
                        {"mensaje_success": "Usuario registrado exitosamente"},
                    )  # Retornamos el mensaje de usuario registrado
            return render(
                request, "index.html", {"form": form}
            )  # Retornando el formulario en caso de que no se valido

        else:
            form = RegistroForm()  # Creando un objeto formulario

        return render(
            request, "index.html", {"form": form}
        )  # Enviamos en formulario a la vista

    @api_view(["POST"])  # La peticion tiene que ser post
    def iniciar_sesion_usuario(request):
        try:

            user = User.objects.get(
                email=request.data["email"]
            )  # Buscando el usuario por el correo

            # Si la contrasena no es valida retornamos la contrasena no es valida
            if not user.check_password(request.data["password"]):
                return Response(
                    {"error": "password no es valido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token, created = Token.objects.get_or_create(
                user=user
            )  # Buscando o creando un token con las credenciales del usuario
            usuario_serializado = UserSerializer(
                instance=user
            )  # Serializando el usuario a tipo json

            return Response(
                {"token": token.key, "usuario": usuario_serializado.data},
                status=status.HTTP_201_CREATED,
            )  # Enviando los datos del usuario con su token correspondiente
        except:
            return Response(
                {"error": "email no es valido"}, status=status.HTTP_400_BAD_REQUEST
            )  # Retornando el caso de que el email no es valido


# Evento rutas
class EventoViews:
    @api_view(["POST"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def crear_evento(request):

        # Serializando el objeto json a diccionario
        evento_serializado = EventoSerializer(data=request.data)

        # Si los datos son validos
        if evento_serializado.is_valid():
            evento_serializado.save()  # Guardando el evento en la base de dato
            # Enviando el correo
            usuario = User.objects.get(
                pk=evento_serializado.data["usuario"]
            )  # Buscando los datos del usuario mediante el id
            evento_notificacion = (
                evento_serializado.data
            )  # Copiamos los datos de evento serializado
            evento_notificacion["correo"] = (
                usuario.email
            )  # Agregamos al evento el correo del usuario
            enviar_notificacion(
                evento_notificacion
            )  # Enviamos la notificacion al usuario

            return Response(
                {"mensaje": "Evento creado exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            evento_serializado.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_eventos(request, id_usuario=None):
        # Si me pasa el id
        if id_usuario is not None:
            eventos = Evento.objects.filter(
                usuario_id=id_usuario
            )  # Buscando los eventos registrado por el usuario
        else:
            eventos = Evento.objects.all()  # Buscando todos los eventos

        serializer = EventoSerializer(
            eventos, many=True
        )  # Serializando todos lo eventos
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )  # Retornando los eventos

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_evento(request, id_evento):
        try:
            evento = Evento.objects.get(pk=id_evento)  # Buscar un evento por su id
            serializer = EventoSerializer(evento)  # Serializando el evento
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )  # Eviando los datos del evento
        except:
            return Response(
                {"error": "El id del evento no es valido"},
                status=status.HTTP_404_NOT_FOUND,
            )  # Retornado el error

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_eventos_proximos(request, id_usuario):

        # Obtener la fecha de hoy
        fecha_de_hoy = datetime.today().date()

        # Agregar 10 días a la fecha de hoy
        fecha_en_10_dias = fecha_de_hoy + timedelta(days=10)
        eventos = Evento.objects.filter(
            Q(fecha__gt=fecha_de_hoy)  # Eventos apartir de la fecha de hoy
            & Q(fecha__lt=fecha_en_10_dias)  # Eventos menores a la fecha de 10 dias
            & Q(usuario_id=id_usuario)  # Eventos del usuario
        ).order_by(
            "fecha"
        )  # Ordenando por la fecha
        serializer = EventoSerializer(
            eventos, many=True
        )  # Serializando todos los eventos
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )  # Retornandos los eventos


# Notas rutas
class NotaViews:
    @api_view(["POST"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def crear_nota(request):

        # Serializando el objeto json a diccionario
        nota_serializada = NotasSerializer(data=request.data)

        # Si los datos son validos
        if nota_serializada.is_valid():

            nota_serializada.save()  # Guardadando el evento en la base de dato

            return Response(
                {"mensaje": "Nota creada exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            nota_serializada.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["PUT"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def actualizar_nota(request, id_nota):

        try:
            contacto_actulizar = Notas.objects.get(
                pk=id_nota
            )  # Buscando la nota por el id de la nota
        except:
            return Response(
                {"error": "La nota no existe"}, status=status.HTTP_400_BAD_REQUEST
            )  # Retornado el error si no existe

        nota_serializada = NotasSerializer(
            contacto_actulizar, request.data
        )  # Actulizando la nota con los datos
        # Si los datos son validos
        if nota_serializada.is_valid():

            nota_serializada.save()  # Guardadando el evento en la base de dato

            return Response(
                {"mensaje": "Nota ha sido actualizada exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            nota_serializada.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["DELETE"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def eliminar_nota(request, id_nota):

        try:
            nota_eliminar = Notas.objects.get(pk=id_nota)  # Buscando la nota por el id
        except:
            return Response(
                {"error": "La nota no existe"}, status=status.HTTP_400_BAD_REQUEST
            )  # Retornando el error si la nota no existe

        nota_eliminar.delete()  # Eliminando la nota

        return Response(
            {"mensaje": "Nota ha sido eliminada exitosamente"},
            status=status.HTTP_201_CREATED,
        )  # Enviando mensaje y status 201 como respuesta

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_notas(request, id_usuario=None):
        if id_usuario is not None:
            notas = Notas.objects.filter(
                usuario_id=id_usuario
            )  # Buscando las notas del usuario
        else:
            notas = Notas.objects.all()  # Buscando todas la notas

        serializer = NotasSerializer(notas, many=True)  # Serializando las notas
        # Formateando la fecha a 12 horas
        for nota in serializer.data:
            nota["fecha_creacion"] = time_formant(nota["fecha_creacion"])

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )  # Retornado los datos

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_nota(request, id_nota):
        try:
            nota = Notas.objects.get(pk=id_nota)  # Buscando la nota por el id
            serializer = NotasSerializer(nota)  # Serializando la nota
            dato = serializer.data  # Clonado la datos para mutar los datos
            dato["fecha_creacion"] = time_formant(
                dato["fecha_creacion"]
            )  # Formateando la fecha a 12 horas

            return Response(dato, status=status.HTTP_200_OK)  # Rertornado la nota
        except:
            return Response(
                {"error": "El id de la nota no es valida"},
                status=status.HTTP_400_BAD_REQUEST,
            )  # Enviando un mensaje de error como repsuta

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_notas_recientes(request, id_usuario):

        fecha_de_hoy = datetime.today().date()  # Obtener la fecha de hoy
        fecha_en_3_atras = fecha_de_hoy - timedelta(
            days=3
        )  # Conviertiendo la fecha de hoy menos 3 dias

        eventos = Notas.objects.filter(
            Q(fecha_creacion__gt=fecha_en_3_atras) & Q(usuario_id=id_usuario)
        ).order_by(
            "fecha_creacion"
        )  # Filtrado las notas por la fecha de creacion de los ultimos 3 dias y ordenandolas
        serializer = NotasSerializer(eventos, many=True)  # Serializandos las notas

        for nota in serializer.data:
            nota["fecha_creacion"] = time_formant(
                nota["fecha_creacion"]
            )  # Formateando a 12 horas

        return Response(
            serializer.data, status=status.HTTP_200_OK
        )  # Retornado los datos


# rutas seccion_libreria
class SeccionViews:
    @api_view(["POST"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def crear_seccion_bibliteca(request):

        # Serializando el objeto json a diccionario
        seccion_serializada = SeccionBibliotecaSerializer(data=request.data)

        # Si los datos son validos
        if seccion_serializada.is_valid():

            seccion_serializada.save()  # Guardadando el evento en la base de dato

            return Response(
                {"mensaje": "seccion creada creada exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            seccion_serializada.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["PUT"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def actualizar_seccion_biblioteca(request, id_seccion):

        try:
            seccion_actulizar = SeccionBiblioteca.objects.get(
                pk=id_seccion
            )  # Buscando la seccion por el id
        except:
            return Response(
                {"error": "La nota no existe"}, status=status.HTTP_404_NOT_FOUND
            )  # Enviando error si la nota no existe

        seccion_serializada = SeccionBibliotecaSerializer(
            seccion_actulizar, request.data
        )  # Serializando la seccion
        # Si los datos son validos
        if seccion_serializada.is_valid():

            seccion_serializada.save()  # Guardadando la seccion en la base de dato

            return Response(
                {"mensaje": "Seccion ha sido actualizada exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            seccion_serializada.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["DELETE"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def eliminar_seccion_biblioteca(request, id_seccion):

        try:
            seccion_eliminar = SeccionBiblioteca.objects.get(
                pk=id_seccion
            )  # Buscando la seccion por el id
        except:
            return Response(
                {"error": "La Seccion no existe"}, status=status.HTTP_404_NOT_FOUND
            )  # Enviando error si la nota no existe

        seccion_eliminar.delete()  # Eliminado la nota

        return Response(
            {"mensaje": "Seccion ha sido eliminada exitosamente"},
            status=status.HTTP_201_CREATED,
        )  # Enviando mensaje y status 201 como respuesta

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_secciones_biblioteca(request, id_usuario=None):
        if id_usuario is not None:
            seccion = SeccionBiblioteca.objects.filter(
                usuario_id=id_usuario
            )  # Buscando la seccion por el id del usuario
        else:
            seccion = SeccionBiblioteca.objects.all()  # Buscando todas la notas

        serializer = SeccionBibliotecaSerializer(
            seccion, many=True
        )  # Serializando la notas
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )  # Retornando los datos

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_seccion_biblioteca(request, id_seccion):
        try:
            seccion = SeccionBiblioteca.objects.get(
                pk=id_seccion
            )  # Buscando la seccion por su id
            serializer = SeccionBibliotecaSerializer(seccion)  # Serializando la seccion
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )  # Retornado la seccion
        except:
            return Response(
                {"error": "El id de la seccion no es valida"},
                status=status.HTTP_404_NOT_FOUND,
            )  # Retornado si error si el id no es valido


# Subir archivos bibibliotecas
class ArchivoView:
    @api_view(["POST"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def subir_archivo(request):

        # Serializando el objeto json a diccionario
        biblioteca_serializada = BibliotecaSerializer(data=request.data)

        # Si los datos son validos
        if biblioteca_serializada.is_valid():

            biblioteca_serializada.save()  # Guardadando el evento en la base de dato

            return Response(
                {"mensaje": "El archivo se ha guardado exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            biblioteca_serializada.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_archivos(request, id_seccion=None):

        # Si el usuario envia el id la biblioteca
        if id_seccion is not None:
            biblioteca = Biblioteca.objects.filter(
                seccion_id=id_seccion
            )  # Filtrado el archivo por el id de la seccion
        else:
            biblioteca = Biblioteca.objects.all()  # Fitrando todos los archivos

        serializer = BibliotecaSerializer(
            biblioteca, many=True
        )  # Serializando la biblioteca
        return Response(serializer.data)  # Retornado los datos

    @api_view(["DELETE"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def eliminar_archivo(request, id_archivo):

        try:
            archivo_eliminar = Biblioteca.objects.get(
                pk=id_archivo
            )  # Bucando el archivo por el id
        except:
            return Response(
                {"error": "El archivo no existe"}, status=status.HTTP_404_NOT_FOUND
            )  # Retornado el archivo en caso de no sea valido

        archivo_eliminar.delete()  # Eliminado el archivo

        return Response(
            {"mensaje": "Archivo ha sido eliminada exitosamente"},
            status=status.HTTP_201_CREATED,
        )  # Enviando mensaje y status 201 como respuesta


# Contactos rutas
class ContatosViews:
    @api_view(["POST"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def crear_contacto(request):

        # Serializando el objeto json a diccionario
        contacto_serializado = ContactoSerializer(data=request.data)

        # Si los datos son validos
        if contacto_serializado.is_valid():

            contacto_serializado.save()  # Guardadando el evento en la base de dato

            return Response(
                {"mensaje": "Contacto creado exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            contacto_serializado.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["PUT"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def actualizar_contacto(request, id_contacto):

        try:
            contacto_actulizar = Contactos.objects.get(
                pk=id_contacto
            )  # Buscando el contacto por su id
        except:
            return Response(
                {"error": "El contacto no existe"}, status=status.HTTP_404_NOT_FOUND
            )  # si no existe retorna error

        contacto_serializado = ContactoSerializer(
            contacto_actulizar, request.data
        )  # Serializando los datos del contacto
        # Si los datos son validos
        if contacto_serializado.is_valid():

            contacto_serializado.save()  # Guardadando el evento en la base de dato

            return Response(
                {"mensaje": "Contacto ha sido actualizado exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            contacto_serializado.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["DELETE"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def eliminar_contacto(request, id_contacto):

        try:
            contacto_eliminar = Contactos.objects.get(
                pk=id_contacto
            )  # Buscando el contacto por el id
        except:
            return Response(
                {"error": "La contacto no existe"}, status=status.HTTP_404_NOT_FOUND
            )  # si no existe retorna error

        contacto_eliminar.delete()  # Eliminado la nota

        return Response(
            {"mensaje": "El contacto ha sido eliminada exitosamente"},
            status=status.HTTP_201_CREATED,
        )  # Enviando mensaje y status 201 como respuesta

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_contactos(request, id_usuario=None):

        # Si el usuario envia el id
        if id_usuario is not None:
            contactos = Contactos.objects.filter(
                usuario_id=id_usuario
            )  # Filtrado los contactos por el id del usuario
        else:
            contactos = Contactos.objects.all()  # Buscando todos lo contactos

        serializer = ContactoSerializer(
            contactos, many=True
        )  # Seralizando los contactos

        # Restableciendo la fecha a 12 horas
        for contacto in serializer.data:
            contacto["fecha_creacion"] = time_formant(contacto["fecha_creacion"])

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )  # Retornando los datos

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_contacto(request, id_contacto):

        try:
            contacto = Contactos.objects.get(
                pk=id_contacto
            )  # Retornando los datos el id del contacto
            serializer = ContactoSerializer(contacto)  # Serializando el contacto

            return Response(
                serializer.data, status=status.HTTP_200_OK
            )  # Retornado los datos

        except:
            return Response(
                {"error": "El id del contacto no es validor"},
                status=status.HTTP_404_NOT_FOUND,
            )


# Contrasenas
class PasswordViews:
    @api_view(["POST"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def crear_password(request):

        # Serializando el objeto json a diccionario
        password_serializado = PasswordSerializer(data=request.data)

        # Si los datos son validos
        if password_serializado.is_valid():

            data_validada = (
                password_serializado.validated_data
            )  # Tomando los campo del objeto
            data_validada["contrasena"] = encriptar_password(
                data_validada["contrasena"]
            )  # Encripatando la contrasena

            password_serializado.save()  # Guardadando el evento en la base de dato

            return Response(
                {"mensaje": "password creado exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            password_serializado.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["PUT"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def actualizar_password(request, id_password):

        try:
            password_actulizar = Passwords.objects.get(
                pk=id_password
            )  # Buscando las contrasena por el id
        except:
            return Response(
                {"error": "El password no existe"}, status=status.HTTP_404_NOT_FOUND
            )  # Retornando la contrasena

        password_serializado = PasswordSerializer(
            password_actulizar, request.data
        )  # Serializando la contrasena
        # Si los datos son validos
        if password_serializado.is_valid():

            data_validada = (
                password_serializado.validated_data
            )  # Tomando los datos de la contrasena
            data_validada["contrasena"] = encriptar_password(
                data_validada["contrasena"]
            )  # Encriptando contrasena

            password_serializado.save()  # Guardadando el evento en la base de dato

            return Response(
                {"mensaje": "password ha sido actualizado exitosamente"},
                status=status.HTTP_201_CREATED,
            )  # Enviando mensaje y status 201 como respuesta

        return Response(
            password_serializado.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Enviando al usuario el error de los campos

    @api_view(["DELETE"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def eliminar_password(request, id_password):

        try:
            password_eliminar = Passwords.objects.get(
                pk=id_password
            )  # Buscando la contrasena por el id
        except:
            return Response(
                {"error": "La password no existe"}, status=status.HTTP_404_NOT_FOUND
            )

        password_eliminar.delete()  # Elimiando la contrasena

        return Response(
            {"mensaje": "El password ha sido eliminada exitosamente"},
            status=status.HTTP_201_CREATED,
        )  # Enviando mensaje y status 201 como respuesta

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_passwords(request, id_usuario=None):

        # Si el usuario me pasa la id
        if id_usuario is not None:
            passwords = Passwords.objects.filter(
                usuario_id=id_usuario
            )  # Buscando todas las contrasena por el id del usuario
        else:
            passwords = Passwords.objects.all()  # Buscando todas las contrasena

        serializer = PasswordSerializer(
            passwords, many=True
        )  # Serilizando todas las contrasenas
        for datos in serializer.data:
            datos["contrasena"] = desencriptar_password(
                f"{datos['contrasena']}"
            )  # Densecriptando la contrasena
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )  # Retornados los datos de la contrasena

    @api_view(["GET"])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def buscar_password(request, id_password):
        try:
            password = Passwords.objects.get(
                pk=id_password
            )  # Bucando la contrasena por el id
            serializer = PasswordSerializer(password)  # Serializando la contrasena
            dato = serializer.data  # Mutando los datos
            dato["contrasena"] = desencriptar_password(
                dato["contrasena"]
            )  # Descriptando la contrasena
            return Response(dato, status=status.HTTP_200_OK)  # Retornando los datos

        except:
            return Response(
                {"error": "El id del password no es valido"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def imagen_IA(request):
    try:
        imagen_peticion = request.data.get("imagen")  # Tomando la imagen de la peticion
        id_usuario = request.data.get("usuario")  # Tomando el id de la peticion

        datos = extraer_texto_imagen(
            imagen_peticion
        )  # Extrayendo los datos de la imagen

        usuario = User.objects.get(pk=id_usuario)  # Buscando los datos del usuario
        # Si los datos son valido
        if len(datos) > 0:
            for dato in datos:
                titulo = dato["titulo"]  # Declarando el titulo
                descripcion = dato["descripcion"]  # Declarando la descripcion
                fecha = dato["fecha"]  # Declarando la fecha
                nuevo_evento_itla = Evento(
                    titulo=titulo,
                    descripcion=descripcion,
                    fecha=fecha,
                    usuario_id=id_usuario,
                )  # Creando un nuevo objeto evento con los datos

                nuevo_evento_itla.save()  # Guardando el evento
                mensaje_correo = {
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "fecha": fecha,
                    "correo": usuario.email,
                }  # Creando un diccionario los datos para el mensaje
                enviar_notificacion(mensaje_correo)  # Enviando la notificacion

            return Response(
                {
                    "mensaje": "Los evento han sido agregando a su calendario correctamente"
                },
                status=status.HTTP_201_CREATED,
            )  # Retornando mensaje que todo se hizo correctamente

        return Response(
            {"error": "Imagen no es valida"}, status=status.HTTP_400_BAD_REQUEST
        )

    except:
        return Response(
            {"error": "Oh no ha ocurrido un error"},
            status=status.HTTP_400_BAD_REQUEST,
        )
