"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from server_productive.views import (
    UserViews,
    EventoViews,
    NotaViews,
    ContatosViews,
    SeccionViews,
    ArchivoView,
    PasswordViews,
    imagen_IA,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


# Rutas del usuario
class UsuarioRutas:
    urlpatterns = [
        path("iniciar_seccion", UserViews.iniciar_sesion_usuario),
    ]


# Rutas del evento
class EventosRutas:
    urlpatterns = [
        path("crear_evento", EventoViews.crear_evento),  #
        path("buscar_eventos", EventoViews.buscar_eventos),
        path("buscar_eventos/<int:id_usuario>", EventoViews.buscar_eventos),
        path("buscar_evento/<int:id_evento>", EventoViews.buscar_evento),
        path(
            "buscar_eventos_proximos/<int:id_usuario>",
            EventoViews.buscar_eventos_proximos,
        ),
    ]


# Rutas de las notas
class NotasRutas:
    urlpatterns = [
        path("crear_nota", NotaViews.crear_nota),
        path("actualizar_nota/<int:id_nota>", NotaViews.actualizar_nota),
        path("eliminar_nota/<int:id_nota>", NotaViews.eliminar_nota),
        path("buscar_notas", NotaViews.buscar_notas),
        path("buscar_notas/<int:id_usuario>", NotaViews.buscar_notas),
        path("buscar_nota/<int:id_nota>", NotaViews.buscar_nota),
        path(
            "buscar_notas_recientes/<int:id_usuario>", NotaViews.buscar_notas_recientes
        ),
    ]


# Rutas de la secciones
class SeccionRutas:
    urlpatterns = [
        path("crear_seccion", SeccionViews.crear_seccion_bibliteca),
        path(
            "actualizar_seccion/<int:id_seccion>",
            SeccionViews.actualizar_seccion_biblioteca,
        ),
        path(
            "eliminar_seccion/<int:id_seccion>",
            SeccionViews.eliminar_seccion_biblioteca,
        ),
        path("buscar_secciones", SeccionViews.buscar_secciones_biblioteca),
        path(
            "buscar_secciones/<int:id_usuario>",
            SeccionViews.buscar_secciones_biblioteca,
        ),
        path("buscar_seccion/<int:id_seccion>", SeccionViews.buscar_seccion_biblioteca),
    ]


# Rutas de los archivos
class ArchivoRutas:
    urlpatterns = [
        path("subir_archivo", ArchivoView.subir_archivo),
        path("buscar_archivos", ArchivoView.buscar_archivos),
        path("buscar_archivos/<int:id_seccion>", ArchivoView.buscar_archivos),
        path("eliminar_archivo/<int:id_archivo>", ArchivoView.eliminar_archivo),
    ]


# Rutas de los contactos
class ContactoRutas:
    urlpatterns = [
        path("crear_contacto", ContatosViews.crear_contacto),
        path(
            "actualizar_contacto/<int:id_contacto>", ContatosViews.actualizar_contacto
        ),
        path("eliminar_contacto/<int:id_contacto>", ContatosViews.eliminar_contacto),
        path("buscar_contactos", ContatosViews.buscar_contactos),
        path("buscar_contactos/<int:id_usuario>", ContatosViews.buscar_contactos),
        path("buscar_contacto/<int:id_contacto>", ContatosViews.buscar_contacto),
    ]


# Rutas de las contrasenas
class PasswordRutas:
    urlpatterns = [
        path("crear_password", PasswordViews.crear_password),
        path(
            "actualizar_password/<int:id_password>",
            PasswordViews.actualizar_password,
        ),
        path("eliminar_password/<int:id_password>", PasswordViews.eliminar_password),
        path("buscar_passwords", PasswordViews.buscar_passwords),
        path("buscar_passwords/<int:id_usuario>", PasswordViews.buscar_passwords),
        path("buscar_password/<int:id_password>", PasswordViews.buscar_password),
    ]


# Url principal de la rutas
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", UserViews.registrar_usuario),
    path("usuario/", include(UsuarioRutas.urlpatterns)),
    path("evento/", include(EventosRutas.urlpatterns)),
    path("notas/", include(NotasRutas.urlpatterns)),
    path("seccion/", include(SeccionRutas.urlpatterns)),
    path("archivo/", include(ArchivoRutas.urlpatterns)),
    path("contacto/", include(ContactoRutas.urlpatterns)),
    path("password/", include(PasswordRutas.urlpatterns)),
    path("imagen_ia", imagen_IA),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
