from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


# Clase formulario para registrar los datos del formulario
class RegistroForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Correo",
            }
        ),
    )  # Editando el campo formulario para agregarle e placer holder

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
        ]  # Campos del formulario
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "Nombre",
                    "required": True,  # El campo es requerido
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Apellido",
                    "required": True,  # El campo es requerido
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "placeholder": "Contraseña",
                    "required": True,  # El campo es requerido
                }
            ),
        }

    # Funcion para validar el formulario
    def clean(self):
        cleaned_data = super().clean()  # Tomando los datos del formulario

        # Si hay algun campo vacio
        if not all(valor != "" for valor in cleaned_data.values()):
            raise forms.ValidationError("Debe completar el formulario para el registro")
