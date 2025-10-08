"""
Servicios para operaciones de base de datos
"""
from db_utils import get_db_cursor, get_db_cursor_with_commit
from utils import process_appointments_time, format_time_from_timedelta


class PatientService:
    """Servicio para operaciones relacionadas con pacientes"""
    
    @staticmethod
    def get_all_patients():
        """Obtener todos los pacientes"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM paciente ORDER BY Nombre")
            return cursor.fetchall()
    
    @staticmethod
    def get_patient_by_id(patient_id):
        """Obtener paciente por ID"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM paciente WHERE id = %s", (patient_id,))
            return cursor.fetchone()
    
    @staticmethod
    def get_patient_by_dni(dni):
        """Obtener paciente por DNI"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, Nombre FROM paciente WHERE DNI = %s", (dni,))
            return cursor.fetchone()
    
    @staticmethod
    def create_patient(patient_data):
        """Crear nuevo paciente"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                INSERT INTO paciente (Nombre, FechaNacimiento, DNI, telefono, email, direccion, contacto_emergencia, telefono_emergencia) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (patient_data["nombre"], patient_data.get("fecha_nacimiento"), patient_data["dni"], 
                 patient_data.get("telefono"), patient_data.get("email"), patient_data.get("direccion"),
                 patient_data.get("contacto_emergencia"), patient_data.get("telefono_emergencia"))
            )
            return cursor.lastrowid
    
    @staticmethod
    def update_patient(patient_id, patient_data):
        """Actualizar paciente"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                UPDATE paciente 
                SET Nombre = %s, FechaNacimiento = %s, DNI = %s, telefono = %s, 
                    email = %s, direccion = %s, contacto_emergencia = %s, telefono_emergencia = %s
                WHERE id = %s
                """,
                (patient_data["nombre"], patient_data.get("fecha_nacimiento"), patient_data["dni"], 
                 patient_data.get("telefono"), patient_data.get("email"), patient_data.get("direccion"),
                 patient_data.get("contacto_emergencia"), patient_data.get("telefono_emergencia"), patient_id)
            )
            return cursor.rowcount
    
    @staticmethod
    def delete_patient(patient_id):
        """Eliminar paciente"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute("DELETE FROM paciente WHERE id = %s", (patient_id,))
            return cursor.rowcount
    
    @staticmethod
    def get_patients_list():
        """Obtener lista básica de pacientes"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, Nombre, DNI FROM paciente ORDER BY Nombre")
            return cursor.fetchall()


class AppointmentService:
    """Servicio para operaciones relacionadas con turnos"""
    
    @staticmethod
    def get_upcoming_appointments(odontologo_id=None, limit=10):
        """Obtener próximos turnos"""
        with get_db_cursor() as cursor:
            if odontologo_id:
                cursor.execute(
                    """
                    SELECT dt.FechaTurno, dt.HoraTurno, p.Nombre AS Paciente, dt.Paciente_id AS PacienteID
                    FROM detalleturno dt
                    INNER JOIN paciente p ON p.id = dt.Paciente_id
                    WHERE dt.Odontologo_id = %s
                      AND TIMESTAMP(dt.FechaTurno, dt.HoraTurno) >= NOW()
                    ORDER BY dt.FechaTurno ASC, dt.HoraTurno ASC
                    LIMIT %s
                    """,
                    (odontologo_id, limit)
                )
            else:
                cursor.execute(
                    """
                    SELECT dt.FechaTurno, dt.HoraTurno, p.Nombre AS Paciente, o.Nombre AS Odontologo, dt.id, dt.Paciente_id AS PacienteID
                    FROM detalleturno dt
                    INNER JOIN paciente p ON p.id = dt.Paciente_id
                    INNER JOIN odontologo o ON o.id = dt.Odontologo_id
                    WHERE TIMESTAMP(dt.FechaTurno, dt.HoraTurno) >= NOW()
                    ORDER BY dt.FechaTurno ASC, dt.HoraTurno ASC
                    LIMIT %s
                    """,
                    (limit,)
                )
            
            appointments = cursor.fetchall()
            return process_appointments_time(appointments)
    
    @staticmethod
    def get_all_appointments():
        """Obtener todos los turnos"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT dt.*, p.Nombre AS Paciente, o.Nombre AS Odontologo
                FROM detalleturno dt
                INNER JOIN paciente p ON p.id = dt.Paciente_id
                INNER JOIN odontologo o ON o.id = dt.Odontologo_id
                ORDER BY dt.FechaTurno DESC, dt.HoraTurno DESC
                """
            )
            appointments = cursor.fetchall()
            return process_appointments_time(appointments)
    
    @staticmethod
    def get_appointment_by_id(appointment_id):
        """Obtener turno por ID"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM detalleturno WHERE id = %s", (appointment_id,))
            return cursor.fetchone()
    
    @staticmethod
    def create_appointment(appointment_data):
        """Crear nuevo turno"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                INSERT INTO detalleturno 
                (Odontologo_id, Paciente_id, FechaTurno, HoraTurno, tipo_consulta, duracion, observaciones, estado) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    appointment_data["odontologo_id"], 
                    appointment_data["paciente_id"], 
                    appointment_data["fecha"], 
                    appointment_data["hora"],
                    appointment_data.get("tipo_consulta"),
                    appointment_data.get("duracion", 30),
                    appointment_data.get("observaciones"),
                    "pendiente"
                )
            )
            return cursor.lastrowid
    
    @staticmethod
    def update_appointment(appointment_id, appointment_data):
        """Actualizar turno"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                UPDATE detalleturno 
                SET Odontologo_id = %s, Paciente_id = %s, FechaTurno = %s, HoraTurno = %s, 
                    tipo_consulta = %s, duracion = %s, observaciones = %s
                WHERE id = %s
                """,
                (
                    appointment_data["odontologo_id"], 
                    appointment_data["paciente_id"], 
                    appointment_data["fecha"], 
                    appointment_data["hora"],
                    appointment_data.get("tipo_consulta"),
                    appointment_data.get("duracion", 30),
                    appointment_data.get("observaciones"),
                    appointment_id
                )
            )
            return cursor.rowcount
    
    @staticmethod
    def delete_appointment(appointment_id):
        """Eliminar turno"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute("DELETE FROM detalleturno WHERE id = %s", (appointment_id,))
            return cursor.rowcount
    
    @staticmethod
    def get_occupied_times(doctor_id, fecha):
        """Obtener horarios ocupados para un doctor en una fecha"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT HoraTurno 
                FROM detalleturno 
                WHERE Odontologo_id = %s AND FechaTurno = %s AND estado != 'cancelado'
                """,
                (doctor_id, fecha)
            )
            occupied_times_raw = cursor.fetchall()
            occupied_times = []
            for row in occupied_times_raw:
                if row[0]:
                    time_str = format_time_from_timedelta(row[0])
                    occupied_times.append(time_str)
            return occupied_times


class DentistService:
    """Servicio para operaciones relacionadas con odontólogos"""
    
    @staticmethod
    def get_all_dentists():
        """Obtener todos los odontólogos"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, Nombre FROM odontologo ORDER BY Nombre")
            return cursor.fetchall()
    
    @staticmethod
    def get_dentist_by_id(dentist_id):
        """Obtener un odontólogo por su ID"""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, Nombre FROM odontologo WHERE id = %s",
                (int(dentist_id),)
            )
            result = cursor.fetchone()
            return result
    
    @staticmethod
    def authenticate_user(username, password, role):
        """Autenticar usuario"""
        table_name = "odontologo" if role == "odontologo" else "secretario"
        
        with get_db_cursor() as cursor:
            cursor.execute(
                f"""
                SELECT id, Nombre, Usuario, Contraseña
                FROM {table_name}
                WHERE Usuario = %s
                LIMIT 1
                """,
                (username,)
            )
            return cursor.fetchone()


class ClinicalHistoryService:
    """Servicio para operaciones relacionadas con historias clínicas"""
    
    @staticmethod
    def get_all_clinical_histories():
        """Obtener todas las historias clínicas"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT hc.*, p.Nombre AS Paciente, p.DNI AS paciente_dni
                FROM historiaclinica hc
                INNER JOIN paciente p ON p.id = hc.Paciente_id
                ORDER BY hc.Fecha DESC
                """
            )
            return cursor.fetchall()
    
    @staticmethod
    def get_clinical_history_by_id(history_id):
        """Obtener historia clínica por ID"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT hc.*, p.Nombre AS PacienteNombre, p.DNI AS paciente_dni
                FROM historiaclinica hc
                INNER JOIN paciente p ON p.id = hc.Paciente_id
                WHERE hc.id = %s
                """,
                (history_id,)
            )
            return cursor.fetchone()
    
    @staticmethod
    def create_clinical_history(data):
        """Crear nueva historia clínica"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                INSERT INTO historiaclinica 
                (Paciente_id, Fecha, MotivoConsulta, Diagnostico, PlanTratamiento, 
                 MedicamentosActuales, Alergias, Enfermedades, Observaciones,
                 Calculo, EnfermedadPeriodontal, OdontogramaData)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["paciente_id"],
                    data.get("fecha", datetime.now().date()),
                    data["motivo_consulta"],
                    data.get("diagnostico"),
                    data.get("plan_tratamiento"),
                    data.get("medicamentos_actuales"),
                    data.get("alergias"),
                    data.get("enfermedades"),
                    data.get("observaciones"),
                    data.get("calculo"),
                    data.get("enfermedad_periodontal"),
                    data.get("odontograma_data")
                )
            )
            return cursor.lastrowid
    
    @staticmethod
    def update_clinical_history(history_id, data):
        """Actualizar historia clínica existente"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                UPDATE historiaclinica SET
                Fecha = %s, MotivoConsulta = %s, Diagnostico = %s, PlanTratamiento = %s,
                MedicamentosActuales = %s, Alergias = %s, Enfermedades = %s, Observaciones = %s,
                Calculo = %s, EnfermedadPeriodontal = %s, OdontogramaData = %s
                WHERE id = %s
                """,
                (
                    data.get("fecha", datetime.now().date()),
                    data["motivo_consulta"],
                    data.get("diagnostico"),
                    data.get("plan_tratamiento"),
                    data.get("medicamentos_actuales"),
                    data.get("alergias"),
                    data.get("enfermedades"),
                    data.get("observaciones"),
                    data.get("calculo"),
                    data.get("enfermedad_periodontal"),
                    data.get("odontograma_data"),
                    history_id
                )
            )
            return history_id
    
    @staticmethod
    def get_clinical_histories_by_patient(patient_id):
        """Obtener historias clínicas de un paciente específico"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT hc.*, p.Nombre as PacienteNombre
                FROM historiaclinica hc
                JOIN paciente p ON hc.Paciente_id = p.id
                WHERE hc.Paciente_id = %s
                ORDER BY hc.Fecha DESC
                """,
                (patient_id,)
            )
            histories = cursor.fetchall()
            
            # Formatear fechas
            for history in histories:
                if history['Fecha']:
                    history['Fecha_formatted'] = history['Fecha'].strftime('%d/%m/%Y')
                else:
                    history['Fecha_formatted'] = None
            
            return histories
    
    @staticmethod
    def delete_clinical_history(history_id):
        """Eliminar historia clínica"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute("DELETE FROM historiaclinica WHERE id = %s", (history_id,))
            return cursor.rowcount


class AvailabilityService:
    """Servicio para gestionar la disponibilidad del médico"""
    
    @staticmethod
    def get_work_schedule(odontologo_id):
        """Obtener horarios de trabajo por día de la semana"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT dia_semana, hora_inicio, hora_fin, activo
                FROM horarios_trabajo
                WHERE odontologo_id = %s AND activo = TRUE
                ORDER BY dia_semana
                """,
                (odontologo_id,)
            )
            return cursor.fetchall()
    
    @staticmethod
    def update_work_schedule(odontologo_id, schedule_data):
        """Actualizar horarios de trabajo"""
        with get_db_cursor_with_commit() as cursor:
            # Eliminar horarios existentes
            cursor.execute(
                "DELETE FROM horarios_trabajo WHERE odontologo_id = %s",
                (odontologo_id,)
            )
            
            # Insertar nuevos horarios
            for day, schedule in schedule_data.items():
                if schedule.get('active', False):
                    cursor.execute(
                        """
                        INSERT INTO horarios_trabajo (odontologo_id, dia_semana, hora_inicio, hora_fin)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (odontologo_id, day, schedule['start_time'], schedule['end_time'])
                    )
    
    @staticmethod
    def generate_monthly_availability(odontologo_id, year, month):
        """Generar disponibilidad mensual basada en horarios de trabajo"""
        from datetime import datetime, timedelta
        import calendar
        
        # Obtener horarios de trabajo
        work_schedule = AvailabilityService.get_work_schedule(odontologo_id)
        schedule_dict = {day['dia_semana']: day for day in work_schedule}
        
        # Generar días del mes
        days_in_month = calendar.monthrange(year, month)[1]
        availability_slots = []
        
        for day in range(1, days_in_month + 1):
            date = datetime(year, month, day)
            day_of_week = date.weekday() + 1  # Convertir a formato 1-7
            
            if day_of_week in schedule_dict:
                schedule = schedule_dict[day_of_week]
                
                # Manejar tanto strings como objetos timedelta
                if isinstance(schedule['hora_inicio'], str):
                    start_time = datetime.strptime(schedule['hora_inicio'], '%H:%M:%S').time()
                else:
                    # Es un timedelta, convertir a time
                    start_time = (datetime.min + schedule['hora_inicio']).time()
                
                if isinstance(schedule['hora_fin'], str):
                    end_time = datetime.strptime(schedule['hora_fin'], '%H:%M:%S').time()
                else:
                    # Es un timedelta, convertir a time
                    end_time = (datetime.min + schedule['hora_fin']).time()
                
                # Generar slots de 30 minutos
                current_time = datetime.combine(date.date(), start_time)
                end_datetime = datetime.combine(date.date(), end_time)
                
                while current_time < end_datetime:
                    availability_slots.append({
                        'fecha': date.date(),
                        'hora_inicio': current_time.time(),
                        'hora_fin': (current_time + timedelta(minutes=30)).time(),
                        'disponible': True
                    })
                    current_time += timedelta(minutes=30)
        
        return availability_slots
    
    @staticmethod
    def save_monthly_availability(odontologo_id, year, month, availability_slots):
        """Guardar disponibilidad mensual en la base de datos"""
        with get_db_cursor_with_commit() as cursor:
            # Eliminar disponibilidad existente del mes
            cursor.execute(
                """
                DELETE FROM disponibilidad_medico 
                WHERE odontologo_id = %s 
                AND YEAR(fecha) = %s 
                AND MONTH(fecha) = %s
                """,
                (odontologo_id, year, month)
            )
            
            # Insertar nueva disponibilidad
            for slot in availability_slots:
                cursor.execute(
                    """
                    INSERT INTO disponibilidad_medico 
                    (odontologo_id, fecha, hora_inicio, hora_fin, disponible)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (odontologo_id, slot['fecha'], slot['hora_inicio'], slot['hora_fin'], slot['disponible'])
                )
    
    @staticmethod
    def get_available_slots(odontologo_id, fecha):
        """Obtener slots disponibles para una fecha específica"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT hora_inicio, hora_fin, observaciones
                FROM disponibilidad_medico
                WHERE odontologo_id = %s 
                AND fecha = %s 
                AND disponible = TRUE
                ORDER BY hora_inicio
                """,
                (odontologo_id, fecha)
            )
            return cursor.fetchall()
    
    @staticmethod
    def check_slot_availability(odontologo_id, fecha, hora):
        """Verificar si un slot específico está disponible"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) as count
                FROM disponibilidad_medico
                WHERE odontologo_id = %s 
                AND fecha = %s 
                AND hora_inicio = %s
                AND disponible = TRUE
                """,
                (odontologo_id, fecha, hora)
            )
            result = cursor.fetchone()
            return result['count'] > 0
    
    @staticmethod
    def mark_slot_unavailable(odontologo_id, fecha, hora_inicio, observaciones=None):
        """Marcar un slot como no disponible"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                UPDATE disponibilidad_medico 
                SET disponible = FALSE, observaciones = %s
                WHERE odontologo_id = %s 
                AND fecha = %s 
                AND hora_inicio = %s
                """,
                (observaciones, odontologo_id, fecha, hora_inicio)
            )
            return cursor.rowcount


class OdontogramaService:
    """Servicio para operaciones relacionadas con odontogramas"""
    
    @staticmethod
    def get_all_odontogramas():
        """Obtener todos los odontogramas"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT o.*, p.Nombre AS Paciente, p.DNI AS paciente_dni
                FROM odontograma o
                INNER JOIN historiaclinica hc ON o.HistoriaClinica_id = hc.id
                INNER JOIN paciente p ON hc.Paciente_id = p.id
                ORDER BY o.Fecha DESC
                """
            )
            return cursor.fetchall()
    
    @staticmethod
    def get_patients_without_odontograma():
        """Obtener pacientes sin odontograma"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT p.* FROM paciente p
                LEFT JOIN historiaclinica hc ON p.id = hc.Paciente_id
                LEFT JOIN odontograma o ON hc.id = o.HistoriaClinica_id
                WHERE o.id IS NULL
                ORDER BY p.Nombre
                """
            )
            return cursor.fetchall()
    
    @staticmethod
    def get_procedimientos():
        """Obtener catálogo de procedimientos"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM procedimientos WHERE Activo = 1 ORDER BY NombreProcedimiento")
            return cursor.fetchall()
    
    @staticmethod
    def get_odontogramas_by_patient(patient_id):
        """Obtener odontogramas de un paciente específico"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT o.*, p.Nombre as PacienteNombre, hc.Fecha as HistoriaFecha
                FROM odontograma o
                JOIN historiaclinica hc ON o.HistoriaClinica_id = hc.id
                JOIN paciente p ON hc.Paciente_id = p.id
                WHERE hc.Paciente_id = %s
                ORDER BY o.Fecha DESC
                """,
                (patient_id,)
            )
            odontogramas = cursor.fetchall()
            
            # Formatear fechas
            for odontograma in odontogramas:
                if odontograma['Fecha']:
                    odontograma['Fecha_formatted'] = odontograma['Fecha'].strftime('%d/%m/%Y')
                else:
                    odontograma['Fecha_formatted'] = None
                    
                if odontograma['HistoriaFecha']:
                    odontograma['HistoriaFecha_formatted'] = odontograma['HistoriaFecha'].strftime('%d/%m/%Y')
                else:
                    odontograma['HistoriaFecha_formatted'] = None
            
            return odontogramas
