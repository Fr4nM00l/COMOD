"""
Utilidades para manejo de base de datos
"""
from contextlib import contextmanager
from db import get_db_connection


@contextmanager
def get_db_cursor():
    """
    Context manager para manejo seguro de conexiones de base de datos
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        yield cursor
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@contextmanager
def get_db_cursor_with_commit():
    """
    Context manager para operaciones que requieren commit
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        yield cursor
        connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
