#!/usr/bin/env python3
"""
Script simple para probar el envío de emails
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_send_email():
    """Probar el envío de un email de prueba"""
    print("Probando envío de email de confirmación...")
    
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
        
        # Usar el email configurado como destinatario
        patient_email = os.getenv('MAIL_USERNAME', 'luciano240503@gmail.com')
        patient_name = "Paciente de Prueba"
        appointment_data = {
            'fecha': '2025-01-15',
            'fecha_formatted': '15/01/2025',
            'hora': '10:00',
            'hora_formatted': '10:00',
            'duracion': '30',
            'duracion_formatted': '30 minutos',
            'doctor_nombre': 'Dr. María López',
            'observaciones': 'Email de prueba del sistema COMOD',
            'clinica_nombre': os.getenv('CLINIC_NAME', 'Clínica Odontológica COMOD'),
            'clinica_direccion': os.getenv('CLINIC_ADDRESS', 'Dirección de la Clínica'),
            'clinica_telefono': os.getenv('CLINIC_PHONE', '+54 11 1234-5678'),
            'clinica_email': os.getenv('CLINIC_EMAIL', 'info@clinica.com')
        }
        
        print(f"Enviando email de prueba a: {patient_email}")
        
        # Enviar email
        with app.app_context():
            success = email_service.send_appointment_confirmation(
                patient_email, 
                patient_name, 
                appointment_data
            )
        
        if success:
            print("EXITO: Email enviado correctamente!")
            print("Revisa tu buzón de correo (y la carpeta de spam)")
            return True
        else:
            print("ERROR: No se pudo enviar el email")
            return False
            
    except Exception as e:
        print(f"ERROR: Error al enviar email: {e}")
        return False

def main():
    """Función principal"""
    print("=== PRUEBA DE ENVÍO DE EMAIL ===")
    print()
    
    # Probar envío
    success = test_send_email()
    
    print("\n" + "=" * 50)
    if success:
        print("RESULTADO: Email enviado exitosamente!")
        print("INSTRUCCIONES:")
        print("1. Revisa tu buzón de correo: luciano240503@gmail.com")
        print("2. Si no lo ves, revisa la carpeta de SPAM")
        print("3. El asunto será: 'Confirmación de Turno - 15/01/2025'")
        print("4. El email tendrá un diseño profesional con todos los detalles")
    else:
        print("RESULTADO: Error al enviar email")
        print("VERIFICA:")
        print("1. Que la contraseña de aplicación sea correcta")
        print("2. Que tengas conexión a internet")
        print("3. Que el email esté bien configurado")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)