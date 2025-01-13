from rest_framework import serializers
from django.contrib.auth.models import User
from server_productive.models import (
    Biblioteca,
    Contactos,
    Evento,
    Notas,
    Passwords,
    SeccionBiblioteca,
)


## -------Serialaizer de los modelos para convertir de los datos --------##
# Los class meta es el contructor para paserles los parametros de que va recibir como
# Como los campo model que es modelo y fields que son los campo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name"]


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = "__all__"


class NotasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notas
        fields = "__all__"


class SeccionBibliotecaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeccionBiblioteca
        fields = "__all__"


class BibliotecaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biblioteca
        fields = "__all__"


class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passwords
        fields = "__all__"


class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contactos
        fields = "__all__"
