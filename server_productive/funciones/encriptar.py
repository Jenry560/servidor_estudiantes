from cryptography.fernet import Fernet
import base64

# Ejemplo de uso
key = b"Zps8nH7WpqF3UpK-HAD2dNtR-6JBrM7jjwJUIq_EJLM="  # llave para descriptar
clave_encriptar = Fernet(key)


# Encriptar una contraseña usando la clave
def encriptar_password(password):
    encriptada_password = clave_encriptar.encrypt(password.encode())
    return encriptada_password


# Desencriptar una contraseña usando la clave
def desencriptar_password(encrypted_password):

    encrypted_password = encrypted_password.strip('"').strip(
        "b'"
    )  # Eliminando las comilla y la b

    # Convertir la cadena a bytes
    bytes_cadena = encrypted_password.encode()

    desencriptada_password = clave_encriptar.decrypt(
        bytes_cadena
    ).decode()  # Descriptar la contrasena la la llave y convertilo en decode
    return desencriptada_password
