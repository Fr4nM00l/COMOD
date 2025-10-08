#!/usr/bin/env python3
"""
Script para probar la validación de conflictos con fechas futuras
"""

from utils import validate_appointment_availability, check_duplicate_appointment
from db_utils import get_db_cursor
from datetime import datetime, timedelta, date

def test_future_conflict():
    """Probar la validación de conflictos con fechas futuras"""
    
    print("🔍 Probando validación de conflictos con fechas futuras...")
    
    with get_db_cursor() as cursor:
        # Usar una fecha futura (mañana)
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        hora = "11:30"
        odontologo_id = 2  # Dra. María López (basado en los datos que vimos)
        
        print(f"📅 Probando con fecha futura: {tomorrow}")
        print(f"🕐 Hora: {hora}")
        print(f"👩‍⚕️ Doctor ID: {odontologo_id}")
        
        # Primero verificar si ya existe un turno para esta fecha/hora/doctor
        print("\n🔍 Verificando turnos existentes para esta fecha/hora/doctor...")
        cursor.execute("""
            SELECT COUNT(*) as count, p.Nombre, o.Nombre as DoctorNombre
            FROM detalleturno dt
            JOIN paciente p ON dt.Paciente_id = p.id
            JOIN odontologo o ON dt.Odontologo_id = o.id
            WHERE dt.FechaTurno = %s 
            AND dt.HoraTurno = %s 
            AND dt.Odontologo_id = %s
            AND dt.estado != 'cancelado'
        """, (tomorrow, timedelta(hours=11, minutes=30), odontologo_id))
        
        result = cursor.fetchone()
        if result and result['count'] > 0:
            print(f"❌ Ya existe {result['count']} turno(s) para esta fecha/hora/doctor")
            print(f"   Paciente: {result['Nombre']}, Doctor: {result['DoctorNombre']}")
        else:
            print("✅ No hay turnos existentes para esta fecha/hora/doctor")
        
        # Ahora probar la validación
        print(f"\n🧪 Probando validación...")
        is_valid, error_message = validate_appointment_availability(
            cursor, tomorrow, hora, odontologo_id, None
        )
        
        print(f"  - Resultado: is_valid={is_valid}")
        if error_message:
            print(f"  - Mensaje: {error_message}")
        else:
            print("  - ✅ Validación pasó correctamente")
        
        # Probar crear un turno duplicado
        print(f"\n🔄 Probando crear turno duplicado...")
        
        # Primero crear un turno
        try:
            cursor.execute("""
                INSERT INTO detalleturno (Paciente_id, Odontologo_id, FechaTurno, HoraTurno, tipo_consulta, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (1, odontologo_id, tomorrow, timedelta(hours=11, minutes=30), 'Prueba', 'programado'))
            
            print("✅ Primer turno creado exitosamente")
            
            # Ahora intentar crear otro turno duplicado
            is_valid_duplicate, error_message_duplicate = validate_appointment_availability(
                cursor, tomorrow, hora, odontologo_id, None
            )
            
            print(f"  - Validación duplicado: is_valid={is_valid_duplicate}")
            if error_message_duplicate:
                print(f"  - Mensaje: {error_message_duplicate}")
            else:
                print("  - ❌ ERROR: La validación debería haber rechazado el duplicado")
            
            # Limpiar el turno de prueba
            cursor.execute("DELETE FROM detalleturno WHERE FechaTurno = %s AND HoraTurno = %s AND Odontologo_id = %s", 
                         (tomorrow, timedelta(hours=11, minutes=30), odontologo_id))
            print("🧹 Turno de prueba eliminado")
            
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    test_future_conflict()
