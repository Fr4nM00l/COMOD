"""
Utilidades comunes para la aplicación
"""
from datetime import datetime, date, timedelta
from flask import jsonify


def validate_required_fields(data, required_fields):
    """
    Valida que los campos requeridos estén presentes en los datos
    
    Args:
        data: Diccionario con los datos a validar
        required_fields: Lista de campos requeridos
    
    Returns:
        tuple: (is_valid, missing_fields_list)
    """
    if not data:
        return False, required_fields
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    return len(missing_fields) == 0, missing_fields


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


def check_duplicate_appointment(cursor, fecha_str, hora_str, odontologo_id, paciente_id=None):
    """
    Verifica si ya existe un turno duplicado para la misma fecha, hora y odontólogo
    
    Args:
        cursor: Cursor de base de datos
        fecha_str: Fecha en formato YYYY-MM-DD
        hora_str: Hora en formato HH:MM
        odontologo_id: ID del odontólogo
        paciente_id: ID del paciente (opcional, para verificar duplicados del mismo paciente)
    
    Returns:
        tuple: (is_duplicate, error_message)
    """
    try:
        # Convertir hora a formato de base de datos (timedelta)
        hora_parts = hora_str.split(':')
        hora_timedelta = timedelta(
            hours=int(hora_parts[0]),
            minutes=int(hora_parts[1])
        )
        
        # Consulta para verificar turnos duplicados
        if paciente_id:
            # Verificar duplicados del mismo paciente
            cursor.execute("""
                SELECT COUNT(*) as count, p.Nombre, o.Nombre as OdontologoNombre
                FROM detalleturno t
                JOIN paciente p ON t.Paciente_id = p.id
                JOIN odontologo o ON t.Odontologo_id = o.id
                WHERE t.FechaTurno = %s 
                AND t.HoraTurno = %s 
                AND t.Odontologo_id = %s
                AND t.Paciente_id = %s
                AND t.estado != 'Cancelado'
            """, (fecha_str, hora_timedelta, odontologo_id, paciente_id))
        else:
            # Verificar cualquier turno duplicado para el odontólogo
            cursor.execute("""
                SELECT COUNT(*) as count, p.Nombre, o.Nombre as OdontologoNombre
                FROM detalleturno t
                JOIN paciente p ON t.Paciente_id = p.id
                JOIN odontologo o ON t.Odontologo_id = o.id
                WHERE t.FechaTurno = %s 
                AND t.HoraTurno = %s 
                AND t.Odontologo_id = %s
                AND t.estado != 'Cancelado'
            """, (fecha_str, hora_timedelta, odontologo_id))
        
        result = cursor.fetchone()
        
        if result and result['count'] > 0:
            paciente_nombre = result['Nombre']
            odontologo_nombre = result['OdontologoNombre']
            
            if paciente_id:
                error_msg = f"Ya existe un turno para el paciente {paciente_nombre} con el Dr./Dra. {odontologo_nombre} el {fecha_str} a las {hora_str}."
            else:
                error_msg = f"Ya existe un turno con el Dr./Dra. {odontologo_nombre} el {fecha_str} a las {hora_str}. Paciente: {paciente_nombre}"
            
            return True, error_msg
        
        return False, None
        
    except Exception as e:
        return False, f"Error al verificar turnos duplicados: {str(e)}"


def validate_appointment_availability(cursor, fecha_str, hora_str, odontologo_id, paciente_id=None):
    """
    Valida que el turno esté disponible (no duplicado y horario válido)
    
    Args:
        cursor: Cursor de base de datos
        fecha_str: Fecha en formato YYYY-MM-DD
        hora_str: Hora en formato HH:MM
        odontologo_id: ID del odontólogo
        paciente_id: ID del paciente (opcional)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Primero validar fecha y hora
    is_valid_datetime, datetime_error = validate_appointment_datetime(fecha_str, hora_str)
    if not is_valid_datetime:
        return False, datetime_error
    
    # Luego verificar duplicados
    is_duplicate, duplicate_error = check_duplicate_appointment(cursor, fecha_str, hora_str, odontologo_id, paciente_id)
    if is_duplicate:
        return False, duplicate_error
    
    return True, None
