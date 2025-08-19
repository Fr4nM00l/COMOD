import os
from typing import Any

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def get_db_connection() -> mysql.connector.MySQLConnection:
    """Create and return a new MySQL database connection using environment variables.

    Required env vars:
      - DB_HOST
      - DB_USER
      - DB_PASSWORD
      - DB_NAME
    Optional:
      - DB_PORT (default 3306)
    """
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "clinicaodontologica")
    db_port = int(os.getenv("DB_PORT", "3306"))

    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port,
        autocommit=False,
        use_pure=True,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
    )
    return connection


