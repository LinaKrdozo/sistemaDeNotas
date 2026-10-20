from config import DatabaseConfig
import pymysql


class Estudiantes:

    @staticmethod
    def crear_tabla():
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS estudiantes (
                            id INT PRIMARY KEY,
                            nombre VARCHAR(100) NOT NULL,
                            apellido VARCHAR(100) NOT NULL,
                            carrera VARCHAR(100),
                            edad INT
                        )
                    """)
                connection.commit()
                print("Tabla 'estudiantes' creada correctamente")

            except Exception as e:
                print(f"Error al crear la tabla: {e}")

            finally:
                connection.close()

    @staticmethod
    def obtener_todos():
        """Devuelve la lista de estudiantes, o None si hubo un error."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                # DictCursor devuelve {"id": 1, "nombre": "Ana"} en vez de (1, "Ana")
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute("SELECT id, nombre, apellido, edad, carrera FROM estudiantes ORDER BY id")
                    return list(cursor.fetchall())

            except Exception as e:
                print(f"Error al obtener estudiantes: {e}")
                return None

            finally:
                connection.close()

        return None

    @staticmethod
    def obtener_por_id(id):
        """Devuelve el estudiante como diccionario, o None si no existe."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(
                        "SELECT id, nombre, apellido, edad, carrera FROM estudiantes WHERE id = %s",
                        (id,)
                    )
                    return cursor.fetchone()

            except Exception as e:
                print(f"Error al obtener estudiante: {e}")
                return None

            finally:
                connection.close()

        return None

    @staticmethod
    def crear(id, nombre, apellido, edad, carrera):
        """Devuelve True si se guardó."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO estudiantes (id, nombre, apellido, edad, carrera) VALUES (%s, %s, %s, %s, %s)",
                        (id, nombre, apellido, edad, carrera)
                    )
                connection.commit()
                return True

            except Exception as e:
                print(f"Error al crear estudiante: {e}")
                return False

            finally:
                connection.close()

        return False

    @staticmethod
    def actualizar(id, nombre, apellido, edad, carrera):
        """Devuelve True si se guardó (la ruta revisa antes que el estudiante exista)."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE estudiantes
                        SET nombre = %s, apellido = %s, edad = %s, carrera = %s
                        WHERE id = %s
                    """, (nombre, apellido, edad, carrera, id))
                connection.commit()
                return True

            except Exception as e:
                print(f"Error al actualizar estudiante: {e}")
                return False

            finally:
                connection.close()

        return False

    @staticmethod
    def eliminar(id):
        """Devuelve True si se borró el estudiante."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM estudiantes WHERE id = %s", (id,))
                    filas_afectadas = cursor.rowcount
                connection.commit()
                return filas_afectadas > 0

            except Exception as e:
                print(f"Error al eliminar estudiante: {e}")
                return False

            finally:
                connection.close()

        return False
