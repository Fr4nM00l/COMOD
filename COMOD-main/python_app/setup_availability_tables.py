#!/usr/bin/env python3
"""
Script para crear las tablas de disponibilidad del médico
"""

import os
import sys
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Cargar variables de entorno
load_dotenv()

def create_availability_tables():
    """Crear las tablas de disponibilidad del médico"""
    
    # Configuración de la base de datos
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'comod_db'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    try:
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Conexion exitosa!")
        
        # Crear tabla de disponibilidad del médico
        print("Creando tabla 'disponibilidad_medico'...")
        create_disponibilidad_table = """
        CREATE TABLE IF NOT EXISTS disponibilidad_medico (
            id INT AUTO_INCREMENT PRIMARY KEY,
            odontologo_id INT NOT NULL,
            fecha DATE NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            disponible BOOLEAN DEFAULT TRUE,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (odontologo_id) REFERENCES odontologo(id) ON DELETE CASCADE,
            UNIQUE KEY unique_slot (odontologo_id, fecha, hora_inicio)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_disponibilidad_table)
        print("Tabla 'disponibilidad_medico' creada exitosamente")
        
        # Crear tabla de horarios de trabajo
        print("Creando tabla 'horarios_trabajo'...")
        create_horarios_table = """
        CREATE TABLE IF NOT EXISTS horarios_trabajo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            odontologo_id INT NOT NULL,
            dia_semana TINYINT NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (odontologo_id) REFERENCES odontologo(id) ON DELETE CASCADE,
            UNIQUE KEY unique_day_schedule (odontologo_id, dia_semana)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_horarios_table)
        print("Tabla 'horarios_trabajo' creada exitosamente")
        
        # Insertar horarios por defecto para el odontólogo (si no existen)
        print("Insertando horarios por defecto...")
        insert_default_schedule = """
        INSERT IGNORE INTO horarios_trabajo (odontologo_id, dia_semana, hora_inicio, hora_fin) VALUES
        (1, 1, '09:00:00', '17:00:00'),
        (1, 2, '09:00:00', '17:00:00'),
        (1, 3, '09:00:00', '17:00:00'),
        (1, 4, '09:00:00', '17:00:00'),
        (1, 5, '09:00:00', '17:00:00'),
        (1, 6, '09:00:00', '13:00:00'),
        (1, 7, '00:00:00', '00:00:00');
        """
        cursor.execute(insert_default_schedule)
        print("Horarios por defecto insertados")
        
        # Confirmar cambios
        connection.commit()
        print("\nTodas las tablas se crearon exitosamente!")
        
        # Verificar que las tablas existen
        print("\nVerificando tablas creadas...")
        cursor.execute("SHOW TABLES LIKE 'disponibilidad_medico'")
        if cursor.fetchone():
            print("Tabla 'disponibilidad_medico' verificada")
        
        cursor.execute("SHOW TABLES LIKE 'horarios_trabajo'")
        if cursor.fetchone():
            print("Tabla 'horarios_trabajo' verificada")
        
        # Mostrar estructura de las tablas
        print("\nEstructura de las tablas:")
        cursor.execute("DESCRIBE disponibilidad_medico")
        print("\nTabla 'disponibilidad_medico':")
        for row in cursor.fetchall():
            print(f"  - {row[0]} ({row[1]})")
        
        cursor.execute("DESCRIBE horarios_trabajo")
        print("\nTabla 'horarios_trabajo':")
        for row in cursor.fetchall():
            print(f"  - {row[0]} ({row[1]})")
            
    except Error as e:
        print(f"Error al crear las tablas: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexion cerrada.")
    
    return True

if __name__ == "__main__":
    print("Script de creacion de tablas de disponibilidad del medico")
    print("=" * 60)
    
    success = create_availability_tables()
    
    if success:
        print("\nProceso completado exitosamente!")
        print("\nProximos pasos:")
        print("1. Iniciar la aplicacion Flask")
        print("2. Acceder como odontologo")
        print("3. Ir a 'Gestion de Disponibilidad'")
        print("4. Configurar horarios de trabajo")
        print("5. Generar disponibilidad mensual")
    else:
        print("\nEl proceso fallo. Revisa los errores anteriores.")
        sys.exit(1)
