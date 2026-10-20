from config import DatabaseConfig
import pymysql
from seguridad import cifrar_password, verificar_password


class Usuarios:

    @staticmethod
    def crear_tabla():
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS usuarios (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            nombre VARCHAR(100) NOT NULL,
                            email VARCHAR(150) NOT NULL UNIQUE,
                            password VARCHAR(255) NOT NULL,
                            rol VARCHAR(20) NOT NULL DEFAULT 'usuario',
                            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # Si la tabla ya existía de antes sin la columna "rol", la agregamos
                    cursor.execute("""
                        SELECT COLUMN_NAME FROM information_schema.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'usuarios'
                          AND COLUMN_NAME = 'rol'
                    """)
                    if cursor.fetchone() is None:
                        cursor.execute("ALTER TABLE usuarios ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT 'usuario'")

                connection.commit()
                print("Tabla 'usuarios' creada correctamente")

            except Exception as e:
                print(f"Error al crear la tabla usuarios: {e}")

            finally:
                connection.close()

    @staticmethod
    def obtener_por_email(email):
        """Devuelve el usuario como diccionario, o None si no existe."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                    return cursor.fetchone()

            except Exception as e:
                print(f"Error al buscar usuario: {e}")
                return None

            finally:
                connection.close()

        return None

    @staticmethod
    def contar():
        """Cuántos usuarios hay. None si hubo un error."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
                    return cursor.fetchone()["total"]

            except Exception as e:
                print(f"Error al contar usuarios: {e}")
                return None

            finally:
                connection.close()

        return None

    @staticmethod
    def crear(nombre, email, password, rol="usuario"):
        """Guarda el usuario con la contraseña cifrada. Devuelve su id o None."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)",
                        (nombre, email, cifrar_password(password), rol)
                    )
                    nuevo_id = cursor.lastrowid
                connection.commit()
                return nuevo_id

            except Exception as e:
                print(f"Error al crear usuario: {e}")
                return None

            finally:
                connection.close()

        return None

    @staticmethod
    def verificar(email, password):
        """Si el correo y la contraseña son correctos, devuelve el usuario (sin la contraseña)."""
        usuario = Usuarios.obtener_por_email(email)

        if usuario and verificar_password(password, usuario["password"]):
            return {
                "id": usuario["id"],
                "nombre": usuario["nombre"],
                "email": usuario["email"],
                "rol": usuario["rol"],
            }

        return None
