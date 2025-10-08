#!/usr/bin/env python3
"""
Script de prueba para el sistema de email de COMOD
"""
import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_email_configuration():
    """Probar la configuración de email"""
    print("🧪 Probando configuración de email...")
    
    # Verificar variables de entorno
    required_vars = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("📝 Crea un archivo .env con la configuración de email")
        return False
    
    print("✅ Variables de entorno configuradas")
    return True

def test_email_service():
    """Probar el servicio de email"""
    print("\n🧪 Probando servicio de email...")
    
    try:
        from email_service import email_service
        from flask import Flask
        
        # Crear app de prueba
        app = Flask(__name__)
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@clinica.com')
        
        # Inicializar servicio
        email_service.init_app(app)
        
        print("✅ Servicio de email inicializado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar servicio de email: {e}")
        return False

def test_email_template():
    """Probar el template de email"""
    print("\n🧪 Probando template de email...")
    
    try:
        from flask import Flask, render_template
        
        app = Flask(__name__, template_folder='templates')
        
        # Datos de prueba
        patient_name = "Juan Pérez"
        appointment_data = {
            'fecha': '2025-01-15',
            'fecha_formatted': '15/01/2025',
            'hora': '10:00',
            'hora_formatted': '10:00',
            'duracion': '30',
            'duracion_formatted': '30 minutos',
            'doctor_nombre': 'Dr. María López',
            'observaciones': 'Consulta de rutina',
            'clinica_nombre': 'Clínica Odontológica COMOD',
            'clinica_direccion': 'Av. Principal 123',
            'clinica_telefono': '+54 11 1234-5678',
            'clinica_email': 'info@clinica.com'
        }
        
        # Renderizar template
        with app.app_context():
            html = render_template(
                'emails/appointment_confirmation.html',
                patient_name=patient_name,
                appointment_data=appointment_data
            )
        
        if html and len(html) > 100:
            print("✅ Template de email renderizado correctamente")
            return True
        else:
            print("❌ Template de email vacío o con errores")
            return False
            
    except Exception as e:
        print(f"❌ Error al renderizar template: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas del sistema de email COMOD")
    print("=" * 50)
    
    tests = [
        test_email_configuration,
        test_email_service,
        test_email_template
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema de email está listo.")
        print("\n📝 Próximos pasos:")
        print("1. Configura las variables de entorno en .env")
        print("2. Instala las dependencias: pip install -r requirements.txt")
        print("3. Ejecuta la aplicación: python app.py")
        print("4. Crea un turno para probar el envío de email")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa la configuración.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

