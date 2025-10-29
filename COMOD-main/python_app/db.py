# En db.py
import os
import mysql.connector
from mysql.connector import Error # Asegúrate que Error esté importado
from dotenv import load_dotenv
from typing import Union

load_dotenv()

def get_db_connection() -> Union[mysql.connector.MySQLConnection, None]:# Puede retornar None si falla
    """Crea y retorna una nueva conexión MySQL verificada."""
    connection = None # Inicializar como None
    try:
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "clinicaodontologica")
        db_port = int(os.getenv("DB_PORT", "3306"))

        print(f"DEBUG [db]: Conectando -> Host={db_host}, User={db_user}, DB={db_name}, Port={db_port}")

        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            autocommit=False, # Mantenemos autocommit=False
            use_pure=True,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            connection_timeout=10 # Timeout corto para detectar rápido si no conecta
        )

        # --- VERIFICACIÓN ADICIONAL ---
        if connection.is_connected():
            print("DEBUG [db]: Conexión establecida y verificada.")
            return connection # Retorna solo si está conectada
        else:
            # Esto no debería pasar si connect() no lanzó error, pero por si acaso
            print("!!!!!!!! ERROR [db]: connect() no lanzó error, pero is_connected() es False.")
            return None
        # --- FIN VERIFICACIÓN ---

    except Error as e:
        print(f"!!!!!!!! ERROR DE CONEXIÓN A BD [db]: {e} !!!!!!!!")
        print(f"Verifica .env: HOST={os.getenv('DB_HOST')}, USER={os.getenv('DB_USER')}, DB={os.getenv('DB_NAME')}, PORT={os.getenv('DB_PORT')}")
        # No relanzar 'e' aquí, simplemente retornamos None o dejamos que el context manager lo maneje
        return None # Indicar fallo retornando None
    except Exception as general_e:
        print(f"!!!!!!!! ERROR GENERAL DURANTE CONEXIÓN A BD [db]: {general_e} !!!!!!!!")
        # No relanzar 'general_e' aquí
        return None # Indicar fallo retornando None

