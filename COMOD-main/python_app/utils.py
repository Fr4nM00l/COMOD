"""
Utilidades comunes para la aplicación
"""
from datetime import datetime, date, timedelta
from flask import jsonify


def format_time_from_timedelta(time_obj):
    """
    Convierte un objeto timedelta o time a string formato HH:MM
    """
    if hasattr(time_obj, 'total_seconds'):
        # Es un timedelta
        total_seconds = int(time_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    else:
        # Es un objeto time
        return str(time_obj)


def process_appointments_time(appointments):
    """
    Procesa una lista de appointments para convertir tiempos a formato string
    """
    processed = []
    for appointment in appointments:
        if 'HoraTurno' in appointment:
            appointment['HoraTurno'] = format_time_from_timedelta(appointment['HoraTurno'])
        processed.append(appointment)
    return processed


def validate_appointment_datetime(fecha_str, hora_str):
    """
    Valida que la fecha y hora del turno sean válidas y futuras
    """
    try:
        appointment_date = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        today = date.today()
        
        if appointment_date < today:
            return False, "No se pueden programar turnos en fechas pasadas. Por favor, selecciona una fecha actual o futura."
        
        # Validar hora si la fecha es hoy
        if appointment_date == today:
            appointment_time = datetime.strptime(hora_str, "%H:%M").time()
            now = datetime.now().time()
            
            if appointment_time <= now:
                return False, "No se pueden programar turnos en horarios pasados. Por favor, selecciona una hora futura."
        
        return True, None
        
    except ValueError as e:
        return False, f"Formato de fecha u hora inválido: {str(e)}"


def create_json_response(success=True, message="", data=None, status_code=200):
    """
    Crea una respuesta JSON estandarizada
    """
    response_data = {"success": success}
    
    if message:
        response_data["message"] = message
    
    if data is not None:
        response_data.update(data)
    
    return jsonify(response_data), status_code


def create_error_response(message, status_code=400):
    """
    Crea una respuesta de error JSON estandarizada
    """
    return create_json_response(success=False, message=message, status_code=status_code)


def create_success_response(message="", data=None):
    """
    Crea una respuesta de éxito JSON estandarizada
    """
    return create_json_response(success=True, message=message, data=data)
