import os
from flask import Flask, request, send_from_directory
from config import DatabaseConfig

# Rutas (blueprints)
from routes.estudiantes import estudiantes_bp
from routes.auth import auth_bp                    

# Modelos (para crear las tablas al iniciar)
from models.models import Estudiantes
from models.users import Usuarios                   
from models.tokens import TokensRevocados           

app = Flask(
    __name__,
    static_folder='../frontend',
    static_url_path=''
)

# Cabeceras CORS manuales (Evita bloqueos estrictos en macOS)
@app.after_request
def agregar_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

    if request.method == 'OPTIONS':
        response.status_code = 200

    return response

app.config.from_object(DatabaseConfig)
DatabaseConfig.probar_conexion(app)

app.register_blueprint(estudiantes_bp)
app.register_blueprint(auth_bp)                     


@app.route('/')
def index():

    frontend_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'frontend'
    )

    return send_from_directory(
        frontend_path,
        'index.html'
    )


if __name__ == "__main__":
    Estudiantes.crear_tabla()
    Usuarios.crear_tabla()                          
    TokensRevocados.crear_tabla()                  
    print("Servidor iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)