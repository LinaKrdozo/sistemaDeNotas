"""
Todo lo relacionado con seguridad:
  - Cifrar y comprobar contraseñas con bcrypt
  - Crear tokens JWT que vencen en 1 hora
  - Decoradores para proteger rutas: @token_requerido y @rol_requerido("admin")
"""
import os
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import g, jsonify, request

from models.tokens import TokensRevocados

# La clave secreta firma los tokens. En producción ponla en una variable de entorno:
#   export JWT_SECRET="una-frase-larga-y-dificil-de-adivinar"
CLAVE_SECRETA = os.environ.get("JWT_SECRET", "cambia-esta-clave-por-una-larga-y-secreta")
ALGORITMO = "HS256"
DURACION_TOKEN = timedelta(hours=1)


# =========================================================
# CONTRASEÑAS (bcrypt)
# =========================================================
def cifrar_password(password):
    """Convierte la contraseña en un hash. Nunca guardamos la contraseña real."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password, hash_guardado):
    """Devuelve True si la contraseña coincide con el hash guardado."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hash_guardado.encode("utf-8"))
    except ValueError:
        # El hash no es de bcrypt (por ejemplo, un usuario creado antes del cambio)
        return False


# =========================================================
# TOKENS JWT
# =========================================================
def crear_token(usuario):
    """Crea un token con los datos del usuario que vence en 1 hora."""
    ahora = datetime.now(timezone.utc)

    datos = {
        "sub": str(usuario["id"]),   # id del usuario
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "rol": usuario["rol"],
        "jti": uuid.uuid4().hex,     # identificador único del token (para la lista negra)
        "iat": ahora,                # fecha de creación
        "exp": ahora + DURACION_TOKEN,  # fecha de vencimiento
    }
    return jwt.encode(datos, CLAVE_SECRETA, algorithm=ALGORITMO)


def error(mensaje, codigo):
    return jsonify({"mensaje": mensaje}), codigo


# =========================================================
# DECORADORES (el "middleware" que protege las rutas)
# =========================================================
def token_requerido(funcion):
    """
    Uso:
        @estudiantes_bp.route(...)
        @token_requerido
        def mi_ruta(): ...

    Revisa que la petición traiga un token válido, que no esté vencido
    y que no esté en la lista negra. Los datos del usuario quedan en g.usuario
    """
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        encabezado = request.headers.get("Authorization", "")

        if not encabezado.startswith("Bearer "):
            return error("Debes iniciar sesión para continuar.", 401)

        token = encabezado.split(" ", 1)[1]

        try:
            datos = jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])
        except jwt.ExpiredSignatureError:
            return error("Tu sesión expiró. Inicia sesión de nuevo.", 401)
        except jwt.InvalidTokenError:
            return error("Token inválido. Inicia sesión de nuevo.", 401)

        if TokensRevocados.esta_revocado(datos["jti"]):
            return error("Esta sesión fue cerrada. Inicia sesión de nuevo.", 401)

        g.usuario = datos
        return funcion(*args, **kwargs)

    return envoltura


def rol_requerido(*roles):
    """
    Uso:
        @rol_requerido("admin")
        def borrar_algo(): ...

    Primero revisa el token (igual que @token_requerido)
    y luego que el usuario tenga uno de los roles permitidos.
    """
    def decorador(funcion):
        @wraps(funcion)
        @token_requerido
        def envoltura(*args, **kwargs):
            if g.usuario.get("rol") not in roles:
                return error("No tienes permiso para realizar esta acción.", 403)
            return funcion(*args, **kwargs)

        return envoltura

    return decorador
