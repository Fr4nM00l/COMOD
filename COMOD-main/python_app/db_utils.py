# En db_utils.py
from contextlib import contextmanager
from db import get_db_connection
import mysql.connector # Importar

@contextmanager
def get_db_cursor():
    """Context manager revisado con mejor manejo de conexión None."""
    connection = None
    cursor = None
    print("DEBUG [db_utils]: Intentando obtener cursor...")
    try:
        connection = get_db_connection()
        # --- VERIFICAR SI LA CONEXIÓN ES VÁLIDA ---
        if connection and connection.is_connected():
            print("DEBUG [db_utils]: Conexión obtenida y verificada. Creando cursor.")
            cursor = connection.cursor(dictionary=True)
            yield cursor # Pasa el control
        else:
            # Si get_db_connection retornó None o una conexión no válida
            print("!!!!!!!! ERROR [db_utils]: get_db_connection() no retornó una conexión válida. !!!!!!!!")
            raise mysql.connector.Error("Fallo al obtener conexión válida desde get_db_connection()") # Lanza error específico
        # --- FIN VERIFICAR ---
    except mysql.connector.Error as db_err:
        print(f"!!!!!!!! ERROR DE BASE DE DATOS en get_db_cursor [db_utils]: {db_err} !!!!!!!!")
        # Código de log de estado de conexión puede ir aquí si quieres
        raise db_err
    except Exception as e:
        print(f"ERROR: Excepción general en get_db_cursor [db_utils]: {e}")
        raise e
    finally:
        # El finally permanece igual para cerrar lo que se haya abierto
        print("DEBUG [db_utils]: Entrando al bloque 'finally' de get_db_cursor.")
        if cursor:
            try: cursor.close(); print("DEBUG [db_utils]: Cursor cerrado.")
            except Exception as e: print(f"ERROR [db_utils] al cerrar cursor: {e}")
        if connection:
            try:
                if connection.is_connected(): connection.close(); print("DEBUG [db_utils]: Conexión cerrada.")
                else: print("DEBUG [db_utils]: Conexión ya estaba cerrada en 'finally'.")
            except Exception as e: print(f"ERROR [db_utils] al cerrar conexión: {e}")

# (Aplica cambios similares de verificación de 'connection' en get_db_cursor_with_commit si es necesario)
@contextmanager
def get_db_cursor_with_commit():
    """Context manager (con commit) revisado."""
    connection = None
    cursor = None
    print("DEBUG [db_utils]: Intentando obtener cursor (con commit)...")
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            print("DEBUG [db_utils]: Conexión (commit) obtenida y verificada. Creando cursor.")
            cursor = connection.cursor(dictionary=True)
            yield cursor
            # Intentar commit
            print("DEBUG [db_utils]: Intentando commit...")
            if connection.is_connected(): # Re-verificar antes del commit
                connection.commit()
                print("DEBUG [db_utils]: Commit realizado.")
            else:
                print("!!!!!!!! ERROR [db_utils]: Conexión perdida ANTES del commit !!!!!!!!")
                raise mysql.connector.Error("Conexión perdida antes del commit.")
        else:
            print("!!!!!!!! ERROR [db_utils]: get_db_connection() no retornó una conexión válida (commit). !!!!!!!!")
            raise mysql.connector.Error("Fallo al obtener conexión válida (commit)")
    except mysql.connector.Error as db_err:
        print(f"!!!!!!!! ERROR DE BASE DE DATOS en commit [db_utils]: {db_err} !!!!!!!!")
        if connection and connection.is_connected():
            try: connection.rollback(); print("DEBUG [db_utils]: Rollback realizado.")
            except Exception as rb_e: print(f"ERROR [db_utils] durante rollback: {rb_e}")
        raise db_err
    except Exception as e:
        print(f"ERROR: Excepción general en commit [db_utils]: {e}")
        if connection and connection.is_connected():
            try: connection.rollback(); print("DEBUG [db_utils]: Rollback (general) realizado.")
            except Exception as rb_e: print(f"ERROR [db_utils] durante rollback general: {rb_e}")
        raise e
    finally:
        print("DEBUG [db_utils]: Entrando al bloque 'finally' (commit).")
        if cursor:
            try: cursor.close(); print("DEBUG [db_utils]: Cursor cerrado (commit).")
            except Exception as e: print(f"ERROR [db_utils] al cerrar cursor (commit): {e}")
        if connection:
            try:
                if connection.is_connected(): connection.close(); print("DEBUG [db_utils]: Conexión cerrada (commit).")
                else: print("DEBUG [db_utils]: Conexión ya estaba cerrada en 'finally' (commit).")
            except Exception as e: print(f"ERROR [db_utils] al cerrar conexión (commit): {e}")
