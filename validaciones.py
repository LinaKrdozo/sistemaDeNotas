"""
Validaciones del backend con expresiones regulares.

Cada función devuelve dos cosas:
  - datos:   los valores limpios y listos para guardar
  - errores: un diccionario {campo: "mensaje"}; si está vacío, todo está bien
"""
import re
from flask import jsonify

# Letras, incluidas tildes, ñ y ü
LETRAS = "A-Za-zÁÉÍÓÚáéíóúÑñÜü"

# Palabras de letras separadas por un solo espacio. Ej: "María José"
RE_PALABRAS = re.compile(rf"^[{LETRAS}]+( [{LETRAS}]+)*$")
# Solo números, de 1 a 10 dígitos. Ej: "1001"
RE_CODIGO = re.compile(r"^\d{1,10}$")
# Número entero de 1 a 3 dígitos
RE_ENTERO = re.compile(r"^\d{1,3}$")
# Correo: algo@dominio.ext
RE_EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
# Contraseña: 8 a 64 caracteres, al menos una minúscula, una mayúscula y un número
RE_PASSWORD = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,64}$")

EDAD_MINIMA = 15
EDAD_MAXIMA = 99


def texto(datos, campo):
    """Lee un campo como texto y le quita los espacios de los extremos."""
    return str(datos.get(campo) or "").strip()


def revisar(valor, minimo, maximo, patron, mensaje_patron):
    """Devuelve el mensaje de error del campo, o None si está bien."""
    if not valor:
        return "Este campo es obligatorio."
    if not minimo <= len(valor) <= maximo:
        return f"Debe tener entre {minimo} y {maximo} caracteres."
    if not patron.match(valor):
        return mensaje_patron
    return None


def respuesta_errores(errores, codigo=400):
    """Respuesta estándar cuando hay errores en los campos."""
    return jsonify({"mensaje": "Revisa los campos marcados.", "errores": errores}), codigo


# =========================================================
# ESTUDIANTES
# =========================================================
def validar_estudiante(entrada, incluir_id=True):
    datos, errores = {}, {}

    if incluir_id:
        codigo = texto(entrada, "id")
        mensaje = revisar(codigo, 1, 10, RE_CODIGO, "El código solo puede tener números.")
        if mensaje:
            errores["id"] = mensaje
        else:
            datos["id"] = int(codigo)

    for campo in ("nombre", "apellido"):
        valor = texto(entrada, campo)
        mensaje = revisar(valor, 2, 50, RE_PALABRAS, "Solo se permiten letras y espacios.")
        if mensaje:
            errores[campo] = mensaje
        else:
            datos[campo] = valor

    edad = texto(entrada, "edad")
    if not edad:
        errores["edad"] = "Este campo es obligatorio."
    elif not RE_ENTERO.match(edad):
        errores["edad"] = "La edad debe ser un número entero."
    elif not EDAD_MINIMA <= int(edad) <= EDAD_MAXIMA:
        errores["edad"] = f"La edad debe estar entre {EDAD_MINIMA} y {EDAD_MAXIMA} años."
    else:
        datos["edad"] = int(edad)

    carrera = texto(entrada, "carrera")
    mensaje = revisar(carrera, 3, 100, RE_PALABRAS, "Solo se permiten letras y espacios.")
    if mensaje:
        errores["carrera"] = mensaje
    else:
        datos["carrera"] = carrera

    return datos, errores


# =========================================================
# REGISTRO E INICIO DE SESIÓN
# =========================================================
def validar_registro(entrada):
    datos, errores = {}, {}

    nombre = texto(entrada, "nombre")
    mensaje = revisar(nombre, 3, 100, RE_PALABRAS, "Solo se permiten letras y espacios.")
    if mensaje:
        errores["nombre"] = mensaje
    else:
        datos["nombre"] = nombre

    email = texto(entrada, "email").lower()
    mensaje = revisar(email, 5, 150, RE_EMAIL, "Escribe un correo válido, por ejemplo nombre@correo.com.")
    if mensaje:
        errores["email"] = mensaje
    else:
        datos["email"] = email

    # La contraseña no se recorta: los espacios cuentan
    password = str(entrada.get("password") or "")
    if not password:
        errores["password"] = "Este campo es obligatorio."
    elif not RE_PASSWORD.match(password):
        errores["password"] = "Mínimo 8 caracteres, con una mayúscula, una minúscula y un número."
    elif len(password.encode("utf-8")) > 72:
        # bcrypt solo admite hasta 72 bytes
        errores["password"] = "La contraseña es demasiado larga."
    else:
        datos["password"] = password

    return datos, errores


def validar_login(entrada):
    datos, errores = {}, {}

    email = texto(entrada, "email").lower()
    if not email:
        errores["email"] = "Este campo es obligatorio."
    elif not RE_EMAIL.match(email):
        errores["email"] = "Escribe un correo válido."
    else:
        datos["email"] = email

    password = str(entrada.get("password") or "")
    if not password:
        errores["password"] = "Este campo es obligatorio."
    else:
        datos["password"] = password

    return datos, errores
