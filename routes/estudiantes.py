from flask import Blueprint, jsonify, request

from models.models import Estudiantes
from seguridad import rol_requerido, token_requerido
from validaciones import respuesta_errores, validar_estudiante

estudiantes_bp = Blueprint('estudiantes', __name__)

# Permisos:
#   - Admin y usuario pueden VER estudiantes (@token_requerido)
#   - Solo el administrador puede CREAR, EDITAR y ELIMINAR (@rol_requerido('admin'))


# CREATE - Crear estudiante (solo admin)
@estudiantes_bp.route('/api/v1/estudiantes', methods=['POST'])
@rol_requerido('admin')
def crear_estudiante():
    datos, errores = validar_estudiante(request.get_json(silent=True) or {})
    if errores:
        return respuesta_errores(errores)

    if Estudiantes.obtener_por_id(datos["id"]):
        return respuesta_errores({"id": "Ya existe un estudiante con este código."}, 409)

    if Estudiantes.crear(**datos):
        return jsonify({
            'mensaje': 'Estudiante creado exitosamente.',
            'id': datos["id"]
        }), 201

    return jsonify({'mensaje': 'Error al guardar en la base de datos.'}), 500


# READ - Obtener todos los estudiantes (admin y usuario)
@estudiantes_bp.route('/api/v1/estudiantes', methods=['GET'])
@token_requerido
def obtener_estudiantes():
    estudiantes = Estudiantes.obtener_todos()

    if estudiantes is not None:
        return jsonify(estudiantes), 200

    return jsonify({'mensaje': 'Error de conexión con la base de datos.'}), 500


# READ - Obtener un estudiante por ID (admin y usuario)
@estudiantes_bp.route('/api/v1/estudiantes/<int:id>', methods=['GET'])
@token_requerido
def obtener_estudiante(id):
    estudiante = Estudiantes.obtener_por_id(id)

    if estudiante:
        return jsonify(estudiante), 200

    return jsonify({'mensaje': 'Estudiante no encontrado.'}), 404


# UPDATE - Actualizar estudiante (solo admin)
@estudiantes_bp.route('/api/v1/estudiantes/<int:id>', methods=['PUT'])
@rol_requerido('admin')
def actualizar_estudiante(id):
    datos, errores = validar_estudiante(request.get_json(silent=True) or {}, incluir_id=False)
    if errores:
        return respuesta_errores(errores)

    if not Estudiantes.obtener_por_id(id):
        return jsonify({'mensaje': 'Estudiante no encontrado.'}), 404

    if Estudiantes.actualizar(id=id, **datos):
        return jsonify({'mensaje': 'Estudiante actualizado exitosamente.'}), 200

    return jsonify({'mensaje': 'Error al guardar en la base de datos.'}), 500


# DELETE - Eliminar estudiante (solo admin)
@estudiantes_bp.route('/api/v1/estudiantes/<int:id>', methods=['DELETE'])
@rol_requerido('admin')
def eliminar_estudiante(id):
    if Estudiantes.eliminar(id):
        return jsonify({'mensaje': 'Estudiante eliminado exitosamente.'}), 200

    return jsonify({'mensaje': 'Estudiante no encontrado.'}), 404
