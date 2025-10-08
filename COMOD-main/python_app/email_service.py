"""
Servicio de email para confirmaciones de turnos
"""
import os
from flask import current_app, render_template
from flask_mail import Mail, Message
from datetime import datetime

class EmailService:
    """Servicio para el envío de emails de confirmación"""
    
    def __init__(self, app=None):
        self.mail = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar Flask-Mail con la aplicación"""
        self.mail = Mail(app)
    
    def send_appointment_confirmation(self, patient_email, patient_name, appointment_data):
        """
        Enviar email de confirmación de turno
        
        Args:
            patient_email (str): Email del paciente
            patient_name (str): Nombre del paciente
            appointment_data (dict): Datos del turno
        """
        try:
            # Verificar que el email esté configurado
            if not current_app.config.get('MAIL_SERVER'):
                print("WARNING: Configuración de email no encontrada. Saltando envío de email.")
                return False
            
            # Crear el mensaje
            msg = Message(
                subject=f"Confirmación de Turno - {appointment_data.get('fecha', '')}",
                recipients=[patient_email],
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@clinica.com')
            )
            
            # Renderizar el template HTML del email
            msg.html = render_template(
                'emails/appointment_confirmation.html',
                patient_name=patient_name,
                appointment_data=appointment_data
            )
            
            # Enviar el email
            self.mail.send(msg)
            print(f"OK: Email de confirmación enviado a {patient_email}")
            return True
            
        except Exception as e:
            print(f"ERROR: Error al enviar email de confirmación: {str(e)}")
            return False
    
    def send_appointment_reminder(self, patient_email, patient_name, appointment_data):
        """
        Enviar email de recordatorio de turno (para implementar en el futuro)
        
        Args:
            patient_email (str): Email del paciente
            patient_name (str): Nombre del paciente
            appointment_data (dict): Datos del turno
        """
        try:
            if not current_app.config.get('MAIL_SERVER'):
                print("⚠️ Configuración de email no encontrada. Saltando envío de recordatorio.")
                return False
            
            msg = Message(
                subject=f"Recordatorio de Turno - {appointment_data.get('fecha', '')}",
                recipients=[patient_email],
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@clinica.com')
            )
            
            msg.html = render_template(
                'emails/appointment_reminder.html',
                patient_name=patient_name,
                appointment_data=appointment_data
            )
            
            self.mail.send(msg)
            print(f"✅ Email de recordatorio enviado a {patient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error al enviar email de recordatorio: {str(e)}")
            return False
    
    def send_appointment_cancellation(self, patient_email, patient_name, appointment_data):
        """
        Enviar email de cancelación de turno
        
        Args:
            patient_email (str): Email del paciente
            patient_name (str): Nombre del paciente
            appointment_data (dict): Datos del turno cancelado
        """
        try:
            if not current_app.config.get('MAIL_SERVER'):
                print("⚠️ Configuración de email no encontrada. Saltando envío de cancelación.")
                return False
            
            msg = Message(
                subject=f"Turno Cancelado - {appointment_data.get('fecha', '')}",
                recipients=[patient_email],
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@clinica.com')
            )
            
            msg.html = render_template(
                'emails/appointment_cancellation.html',
                patient_name=patient_name,
                appointment_data=appointment_data
            )
            
            self.mail.send(msg)
            print(f"✅ Email de cancelación enviado a {patient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error al enviar email de cancelación: {str(e)}")
            return False

# Instancia global del servicio de email
email_service = EmailService()
