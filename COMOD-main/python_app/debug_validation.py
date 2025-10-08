#!/usr/bin/env python3
"""
Script para debuggear la función validate_appointment_availability
"""

from utils import validate_appointment_availability, validate_appointment_datetime, check_duplicate_appointment
from db_utils import get_db_cursor
from datetime import timedelta

def debug_validation():
    """Debuggear la función validate_appointment_availability"""
    
    print("🔍 Debuggeando validate_appointment_availability...")
    
    with get_db_cursor() as cursor:
        # Datos del turno duplicado
        fecha = '2025-10-16'
        hora = '09:00'
        odontologo_id = 2  # Dra. María López
        paciente_id = 8    # Segundo paciente
        
        print(f"📅 Fecha: {fecha}")
        print(f"🕐 Hora: {hora}")
        print(f"👩‍⚕️ Doctor ID: {odontologo_id}")
        print(f"👤 Paciente ID: {paciente_id}")
        
        # Paso 1: Validar fecha y hora
        print(f"\n🔍 Paso 1: Validando fecha y hora...")
        is_valid_datetime, datetime_error = validate_appointment_datetime(fecha, hora)
        print(f"  - is_valid_datetime: {is_valid_datetime}")
        if datetime_error:
            print(f"  - datetime_error: {datetime_error}")
        else:
            print(f"  - No hay error de fecha/hora")
        
        # Paso 2: Verificar duplicados
        print(f"\n🔍 Paso 2: Verificando duplicados...")
        is_duplicate, duplicate_error = check_duplicate_appointment(cursor, fecha, hora, odontologo_id, paciente_id)
        print(f"  - is_duplicate: {is_duplicate}")
        if duplicate_error:
            print(f"  - duplicate_error: {duplicate_error}")
        else:
            print(f"  - No hay error de duplicados")
        
        # Paso 3: Validación completa
        print(f"\n🔍 Paso 3: Validación completa...")
        is_valid, error_message = validate_appointment_availability(cursor, fecha, hora, odontologo_id, paciente_id)
        print(f"  - is_valid: {is_valid}")
        if error_message:
            print(f"  - error_message: {error_message}")
        else:
            print(f"  - No hay mensaje de error")
        
        # Análisis del problema
        print(f"\n📊 Análisis:")
        if is_valid_datetime and is_duplicate:
            print(f"  ❌ PROBLEMA: La fecha/hora es válida PERO hay duplicados")
            print(f"     La validación debería devolver False pero devuelve {is_valid}")
        elif not is_valid_datetime:
            print(f"  ✅ La validación falla por fecha/hora inválida")
        elif not is_duplicate:
            print(f"  ✅ No hay duplicados, validación correcta")
        else:
            print(f"  ❓ Caso no esperado")

if __name__ == "__main__":
    debug_validation()
