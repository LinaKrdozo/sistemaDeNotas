from datetime import datetime, timezone
from config import DatabaseConfig


class TokensRevocados:
    """
    Lista negra de tokens.
    Cuando alguien cierra sesión, guardamos el identificador (jti) de su token
    para que no se pueda volver a usar aunque todavía no haya vencido.
    """

    @staticmethod
    def crear_tabla():
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tokens_revocados (
                            jti VARCHAR(64) PRIMARY KEY,
                            expira_en DATETIME NOT NULL
                        )
                    """)
                connection.commit()
                print("Tabla 'tokens_revocados' creada correctamente")

            except Exception as e:
                print(f"Error al crear la tabla tokens_revocados: {e}")

            finally:
                connection.close()

    @staticmethod
    def revocar(jti, exp):
        """Agrega el token a la lista negra. Devuelve True si se guardó."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                # exp viene del token como un número (segundos); lo pasamos a fecha UTC
                expira_en = datetime.fromtimestamp(exp, timezone.utc).replace(tzinfo=None)

                with connection.cursor() as cursor:
                    # De paso borramos los que ya vencieron: esos ya no sirven de todos modos
                    cursor.execute("DELETE FROM tokens_revocados WHERE expira_en < UTC_TIMESTAMP()")
                    cursor.execute(
                        "INSERT IGNORE INTO tokens_revocados (jti, expira_en) VALUES (%s, %s)",
                        (jti, expira_en)
                    )
                connection.commit()
                return True

            except Exception as e:
                print(f"Error al revocar token: {e}")
                return False

            finally:
                connection.close()

        return False

    @staticmethod
    def esta_revocado(jti):
        """Devuelve True si el token está en la lista negra."""
        connection = DatabaseConfig.get_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT jti FROM tokens_revocados WHERE jti = %s", (jti,))
                    return cursor.fetchone() is not None

            except Exception as e:
                print(f"Error al revisar token: {e}")
                return False

            finally:
                connection.close()

        return False
