#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos MySQL
"""

import sys
import os
sys.path.append('python_app')

from python_app.db import get_db_connection

def test_database_connection():
    """Probar la conexión a la base de datos"""
    print("🔍 Probando conexión a la base de datos...")
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Probar consulta básica
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Conexión a la base de datos exitosa")
            
            # Verificar que las tablas principales existen
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            required_tables = [
                'paciente', 'odontologo', 'secretario', 'historiaclinica',
                'odontograma', 'detalleturno', 'procedimientos'
            ]
            
            missing_tables = []
            for table in required_tables:
                if table not in table_names:
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"⚠️  Tablas faltantes: {', '.join(missing_tables)}")
                print("💡 Asegúrate de importar el archivo clinicaodontologica.sql")
            else:
                print("✅ Todas las tablas principales están presentes")
                
                # Verificar datos de prueba
                cursor.execute("SELECT COUNT(*) FROM paciente")
                patient_count = cursor.fetchone()[0]
                print(f"📊 Pacientes en la base de datos: {patient_count}")
                
                cursor.execute("SELECT COUNT(*) FROM odontologo")
                dentist_count = cursor.fetchone()[0]
                print(f"📊 Odontólogos en la base de datos: {dentist_count}")
                
                cursor.execute("SELECT COUNT(*) FROM secretario")
                secretary_count = cursor.fetchone()[0]
                print(f"📊 Secretarios en la base de datos: {secretary_count}")
            
            cursor.close()
            connection.close()
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        print("💡 Verifica que:")
        print("   - MySQL esté ejecutándose")
        print("   - La base de datos 'clinicaodontologica' exista")
        print("   - Las credenciales en el archivo .env sean correctas")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
