from flask import Blueprint, g, jsonify, request

from models.tokens import TokensRevocados
from models.users import Usuarios
from seguridad import crear_token, token_requerido, DURACION_TOKEN
from validaciones import respuesta_errores, validar_login, validar_registro

auth_bp = Blueprint('auth', __name__)


# REGISTRO - Crear una cuenta nueva (registro abierto)
@auth_bp.route('/api/v1/auth/register', methods=['POST'])
def registrar():
    datos, errores = validar_registro(request.get_json(silent=True) or {})
    if errores:
        return respuesta_errores(errores)

    # Email único
    if Usuarios.obtener_por_email(datos["email"]):
        return respuesta_errores({"email": "Ya existe una cuenta con este correo."}, 409)

    total = Usuarios.contar()
    if total is None:
        return jsonify({'mensaje': 'Error de conexión con la base de datos.'}), 500

    # El primer usuario que se registra es el administrador; los demás son usuarios
    rol = "admin" if total == 0 else "usuario"

    nuevo_id = Usuarios.crear(datos["nombre"], datos["email"], datos["password"], rol)

    if nuevo_id:
        return jsonify({
            'mensaje': 'Cuenta creada correctamente.',
            'id': nuevo_id,
            'rol': rol
        }), 201

    return jsonify({'mensaje': 'Error al guardar en la base de datos.'}), 500


# LOGIN - Iniciar sesión y recibir un token
@auth_bp.route('/api/v1/auth/login', methods=['POST'])
def login():
    datos, errores = validar_login(request.get_json(silent=True) or {})
    if errores:
        return respuesta_errores(errores)

    usuario = Usuarios.verificar(datos["email"], datos["password"])

    if not usuario:
        # No decimos si falló el correo o la contraseña, por seguridad
        return jsonify({'mensaje': 'Correo o contraseña incorrectos.'}), 401

    return jsonify({
        'mensaje': 'Inicio de sesión correcto.',
        'token': crear_token(usuario),
        'expira_en_segundos': int(DURACION_TOKEN.total_seconds()),
        'usuario': usuario
    }), 200


# LOGOUT - Cerrar sesión: el token pasa a la lista negra
@auth_bp.route('/api/v1/auth/logout', methods=['POST'])
@token_requerido
def logout():
    TokensRevocados.revocar(g.usuario["jti"], g.usuario["exp"])
    return jsonify({'mensaje': 'Sesión cerrada correctamente.'}), 200


# PERFIL - Datos del usuario que tiene la sesión abierta
@auth_bp.route('/api/v1/auth/perfil', methods=['GET'])
@token_requerido
def perfil():
    return jsonify({
        'id': int(g.usuario["sub"]),
        'nombre': g.usuario["nombre"],
        'email': g.usuario["email"],
        'rol': g.usuario["rol"]
    }), 200
