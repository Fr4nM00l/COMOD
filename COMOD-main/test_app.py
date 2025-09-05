#!/usr/bin/env python3
"""
Script de prueba para verificar que la aplicación COMOD funciona correctamente.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Verificar que las dependencias estén instaladas."""
    print("🔍 Verificando dependencias...")
    
    try:
        import flask
        import mysql.connector
        import dotenv
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("💡 Ejecuta: pip install -r python_app/requirements.txt")
        return False

def check_env_file():
    """Verificar que existe el archivo .env."""
    print("🔍 Verificando archivo .env...")
    
    env_path = Path("python_app/.env")
    if env_path.exists():
        print("✅ Archivo .env encontrado")
        return True
    else:
        print("❌ Archivo .env no encontrado")
        print("💡 Crea el archivo python_app/.env con la configuración de la base de datos")
        return False

def check_database():
    """Verificar conexión a la base de datos."""
    print("🔍 Verificando conexión a la base de datos...")
    
    try:
        from python_app.db import get_db_connection
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        connection.close()
        print("✅ Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        print("💡 Verifica que MySQL esté ejecutándose y que la base de datos 'clinicaodontologica' exista")
        return False

def test_app_startup():
    """Probar que la aplicación se inicia correctamente."""
    print("🔍 Probando inicio de la aplicación...")
    
    try:
        # Cambiar al directorio de la aplicación
        os.chdir("python_app")
        
        # Importar la aplicación
        from app import app
        
        # Crear un cliente de prueba
        with app.test_client() as client:
            # Probar la ruta de login
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Aplicación se inicia correctamente")
                return True
            else:
                print(f"❌ Error en la aplicación: código {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        return False
    finally:
        # Volver al directorio original
        os.chdir("..")

def main():
    """Función principal de prueba."""
    print("🚀 Iniciando pruebas del sistema COMOD...\n")
    
    tests = [
        ("Dependencias", check_dependencies),
        ("Archivo .env", check_env_file),
        ("Base de datos", check_database),
        ("Inicio de aplicación", test_app_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ¡Todas las pruebas pasaron! La aplicación está lista para usar.")
        print("💡 Para ejecutar la aplicación: cd python_app && python app.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("💡 Consulta el archivo CONFIGURACION.md para más detalles.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
