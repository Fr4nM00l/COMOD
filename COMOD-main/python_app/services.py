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
                    SELECT dt.FechaTurno, dt.HoraTurno, p.Nombre AS Paciente
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
                    SELECT dt.FechaTurno, dt.HoraTurno, p.Nombre AS Paciente, o.Nombre AS Odontologo, dt.id
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
    def get_patients_without_history():
        """Obtener pacientes sin historia clínica"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT p.* FROM paciente p
                LEFT JOIN historiaclinica hc ON p.id = hc.Paciente_id
                WHERE hc.id IS NULL
                ORDER BY p.Nombre
                """
            )
            return cursor.fetchall()
    
    @staticmethod
    def create_clinical_history(history_data):
        """Crear nueva historia clínica"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                INSERT INTO historiaclinica 
                (Fecha, Paciente_id, ObraSocial, NumAfiliado, Alergias, Enfermedades, 
                 Fuma, Drogas, Medicamentos, NivelDeDolor, Calmante, GolpeEnDientes, FechaGolpe) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (history_data["fecha"], history_data["paciente_id"], history_data.get("obra_social"), 
                 history_data.get("num_afiliado"), history_data.get("alergias"), history_data.get("enfermedades"),
                 history_data.get("fuma", False), history_data.get("drogas"), history_data.get("medicamentos"),
                 history_data.get("nivel_dolor"), history_data.get("calmante"), history_data.get("golpe_en_dientes", False),
                 history_data.get("fecha_golpe"))
            )
            return cursor.lastrowid
    
    @staticmethod
    def get_clinical_history_by_id(history_id):
        """Obtener historia clínica por ID"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM historiaclinica WHERE id = %s", (history_id,))
            return cursor.fetchone()
    
    @staticmethod
    def delete_clinical_history(history_id):
        """Eliminar historia clínica"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute("DELETE FROM historiaclinica WHERE id = %s", (history_id,))
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
