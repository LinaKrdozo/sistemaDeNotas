import pymysql
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DatabaseConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/universidad_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_connection():
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database='universidad_db',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection

        except Exception as e:
            print("❌ Error de conexión:")
            print(e)
            return None

    @staticmethod
    def probar_conexion(app):
        db.init_app(app)

        with app.app_context():
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Conexión exitosa a la base de datos")
            except Exception as e:
                print("❌ Error al conectar a la base de datos:")
                print(e)
