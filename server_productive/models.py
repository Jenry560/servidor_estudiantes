from django.db import models
from django.contrib.auth.models import User


class Evento(models.Model):
    titulo = models.CharField(
        max_length=20
    )  # Titulo tipo charfield con un lenght maximo de 20 caraceteres
    descripcion = models.CharField(
        max_length=100
    )  # Descripcion tipo charfield con un lenght maximo de 100 caraceteres
    fecha = models.DateField()  # fecha tipo fecha
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # llave foronea del usuario con eliminacion en cascada


class SeccionBiblioteca(models.Model):
    nombre_seccion = models.CharField(
        max_length=50
    )  # nombre_seccion tipo charfield con un lenght maximo de 50 caraceteres
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # llave foronea del usuario con eliminacion en cascada


class Biblioteca(models.Model):
    archivo = models.FileField()  # archivo tipo archivo
    seccion = models.ForeignKey(
        SeccionBiblioteca, on_delete=models.CASCADE
    )  # llave foronea de la seccion con eliminacion en cascada


class Passwords(models.Model):
    etiqueta = models.CharField(
        max_length=50
    )  # etiqueta tipo charfield con un lenght maximo de 50 caraceteres
    contrasena = models.CharField(
        max_length=500
    )  # contrasena tipo charfield con un lenght maximo de 500 caraceteres
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # llave foronea del usuario con eliminacion en cascada


class Notas(models.Model):
    titulo = models.CharField(
        max_length=20
    )  # titulo tipo charfield con un lenght maximo de 20 caraceteres
    descripcion = models.TextField()  # descripcion tipo campo texto
    fecha_creacion = models.DateTimeField(
        auto_now=True
    )  # fecha de creacion tipo datetime y se modifica cada vez el usuario hace una modificacion
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # llave foronea del usuario con eliminacion en cascada


class Contactos(models.Model):
    contacto = models.CharField(
        max_length=100
    )  # contacto tipo charfield con un lenght maximo de 100 caraceteres
    campo_contacto = models.TextField()  # campo_contacto tipo campo texto
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )  # fecha de creacion tipo datetime y se modifica cada vez el usuario hace una modificacion
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # llave foronea del usuario con eliminacion en cascada
