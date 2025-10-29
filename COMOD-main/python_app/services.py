
"""
Servicios para operaciones de base de datos
"""
from datetime import datetime
from db_utils import get_db_cursor, get_db_cursor_with_commit
from utils import process_appointments_time, format_time_from_timedelta


class PatientService:
    """Servicio para operaciones relacionadas con pacientes"""
    
    @staticmethod
    def get_all_patients_basic():
        """Obtener ID, Nombre y DNI de todos los pacientes"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, Nombre, DNI FROM paciente ORDER BY Nombre")
            return cursor.fetchall()

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
    def update_appointment_status(appointment_id, new_status):
        """Actualiza el estado de un turno específico"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                UPDATE detalleturno 
                SET estado = %s 
                WHERE id = %s
                """,
                (new_status, appointment_id)
            )
            return cursor.rowcount


    # Dentro de AppointmentService.get_upcoming_appointments
    @staticmethod
    def get_upcoming_appointments(odontologo_id=None, limit=10):
        """Obtener próximos turnos (pendientes o en curso)"""
        print(f"DEBUG [service]: Iniciando get_upcoming_appointments para odontologo_id={odontologo_id}") # Debug
        try: # Añadir un try/except general aquí también es buena idea
            with get_db_cursor() as cursor: # Intenta obtener el cursor
                # --- NUEVO PRINT ---
                if cursor:
                    print("DEBUG [service]: Cursor obtenido DENTRO de get_upcoming_appointments.")
                else:
                    # Esto no debería pasar si get_db_cursor lanza excepción, pero por si acaso
                    print("!!!!!!!! ERROR [service]: ¡El cursor es None DENTRO de get_upcoming_appointments! !!!!!!!!")
                    raise mysql.connector.Error("Cursor no válido obtenido.")
                # --- FIN NUEVO PRINT ---

                # El resto de la lógica de la consulta como estaba...
                base_query = """
                    SELECT dt.FechaTurno, dt.HoraTurno, p.Nombre AS Paciente, dt.Paciente_id AS PacienteID
                    FROM detalleturno dt
                    INNER JOIN paciente p ON p.id = dt.Paciente_id
                    WHERE TIMESTAMP(dt.FechaTurno, dt.HoraTurno) >= NOW()
                      AND dt.estado IN ('pendiente', 'en_curso')
                    """
                params = []

                if odontologo_id:
                    query = base_query + """
                        AND dt.Odontologo_id = %s
                        ORDER BY dt.FechaTurno ASC, dt.HoraTurno ASC
                        LIMIT %s
                    """
                    params = [odontologo_id, limit]
                else:
                     query = """
                        SELECT dt.FechaTurno, dt.HoraTurno, p.Nombre AS Paciente, o.Nombre AS Odontologo, dt.id, dt.Paciente_id AS PacienteID
                        FROM detalleturno dt
                        INNER JOIN paciente p ON p.id = dt.Paciente_id
                        INNER JOIN odontologo o ON o.id = dt.Odontologo_id
                        WHERE TIMESTAMP(dt.FechaTurno, dt.HoraTurno) >= NOW()
                          AND dt.estado IN ('pendiente', 'en_curso')
                        ORDER BY dt.FechaTurno ASC, dt.HoraTurno ASC
                        LIMIT %s
                     """
                     params = [limit]

                print(f"DEBUG [service]: Ejecutando consulta de turnos...") # Debug antes de execute
                cursor.execute(query, tuple(params)) # Asegurarse que params sea tupla
                print(f"DEBUG [service]: Consulta de turnos ejecutada.") # Debug después de execute
                appointments = cursor.fetchall()
                return process_appointments_time(appointments)
        except mysql.connector.Error as db_err_service:
            # Captura errores específicos que puedan ocurrir aquí
            print(f"!!!!!!!! ERROR DE BASE DE DATOS DENTRO de get_upcoming_appointments: {db_err_service} !!!!!!!!")
            # Si el error es "Cursor is not connected", podría ser aquí.
            raise db_err_service # Relanzar para que la ruta lo maneje
        except Exception as e_service:
             print(f"ERROR GENERAL DENTRO de get_upcoming_appointments: {e_service}")
             raise e_service # Relanzar para que la ruta lo maneje
    
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
    
    @staticmethod
    def get_appointments_count_by_patient(patient_id):
        """Obtener el número total de turnos de un paciente"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) as count
                    FROM detalleturno 
                    WHERE Paciente_id = %s
                    """,
                    (patient_id,)
                )
                result = cursor.fetchone()
                if result:
                    # Manejar tanto diccionarios como tuplas
                    if isinstance(result, dict):
                        return result.get('count', 0)
                    else:
                        return result[0]
                return 0
        except Exception as e:
            print(f"Error en get_appointments_count_by_patient: {e}")
            return 0
    
    @staticmethod
    def check_patient_appointment_today(patient_id, odontologo_id, date):
        """Verificar si un paciente tiene un turno programado para una fecha específica con un odontólogo"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) as count
                    FROM detalleturno 
                    WHERE Paciente_id = %s 
                      AND Odontologo_id = %s 
                      AND FechaTurno = %s
                    """,
                    (patient_id, odontologo_id, date)
                )
                result = cursor.fetchone()
                if result:
                    # Manejar tanto diccionarios como tuplas
                    if isinstance(result, dict):
                        count = result.get('count', 0)
                    else:
                        count = result[0]
                    return count > 0
                return False
        except Exception as e:
            print(f"Error en check_patient_appointment_today: {e}")
            return False
    
    @staticmethod
    def get_patient_appointment_today(patient_id, odontologo_id, date):
        """Obtener información del turno de un paciente para una fecha específica"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT dt.FechaTurno, dt.HoraTurno, dt.id
                    FROM detalleturno dt
                    WHERE dt.Paciente_id = %s 
                      AND dt.Odontologo_id = %s 
                      AND dt.FechaTurno = %s
                    LIMIT 1
                    """,
                    (patient_id, odontologo_id, date)
                )
                result = cursor.fetchone()
                if result:
                    # Manejar tanto diccionarios como tuplas
                    if isinstance(result, dict):
                        return {
                            'fecha': result.get('FechaTurno'),
                            'hora': result.get('HoraTurno'),
                            'id': result.get('id')
                        }
                    else:
                        return {
                            'fecha': result[0],
                            'hora': result[1],
                            'id': result[2]
                        }
                return None
        except Exception as e:
            print(f"Error en get_patient_appointment_today: {e}")
            return None


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
        """
        Crear nueva historia clínica Y el odontograma asociado.
        Esta operación es transaccional.
        """
        # Extraer datos del odontograma y del odontólogo antes de procesar la historia
        odontograma_data = data.pop('odontograma_data', None)
        odontologo_id = data.pop('odontologo_id', None)
        
        with get_db_cursor_with_commit() as cursor:
            try:
                # --- PASO 1: Insertar la Historia Clínica ---
                # Esta consulta INSERT incluye TODOS los campos del formulario
                cursor.execute(
                    """
                    INSERT INTO historiaclinica 
                    (Paciente_id, Fecha, ObraSocial, NumAfiliado, Alergias, Enfermedades, 
                     Fuma, Drogas, Medicamentos, NivelDeDolor, Calmante, GolpeEnDientes, FechaGolpe,
                    domicilio, edad, tratamiento_odontologico, tratamiento_odontologico_detalle,
                    colageno, fiebre_reumatica, diabetes, cardiaco, hipertension, sifilis, transfusiones,
                    embarazada, meses_embarazo, chagas, hepatitis, renales, ulcera, convulsiones,
                    tiempo_fumando, otras_enfermedades, tomo_medicamento, medicamento_detalle,
                    dolor_tipo, dolor_localizacion, dificultades_funcionales, examen_tejidos_blandos,
                    firma_paciente, firma_profesional, motivo_consulta, diagnostico_presuntivo, plan_tratamiento)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    """, # <-- CORRECCIÓN: Ahora hay 44 %s, coincidiendo con las 44 columnas listadas
                    (
                        # CORRECCIÓN: Tupla de valores ajustada para coincidir con las columnas
                        data.get("paciente_id"),
                        data.get("fecha", datetime.now().date()),
                        data.get("obra_social"), data.get("num_afiliado"), data.get("alergias"), data.get("enfermedades"), # NumAfiliado en lugar de plan
                        data.get("fuma", False), data.get("drogas"), data.get("medicamentos_actuales"), # Medicamentos actuales en lugar de Medicamentos
                        data.get("dolor_intensidad"), data.get("dolor_detalle"), # Usar dolor_detalle para Calmante según tu comentario
                        data.get("golpe_dientes", False),
                        data.get("golpe_cuando") if data.get("golpe_dientes") else None,
                        data.get("domicilio"), data.get("edad"),
                        data.get("tratamiento_odontologico", False), data.get("tratamiento_odontologico_detalle"),
                        data.get("colageno", False), data.get("fiebre_reumatica", False), data.get("diabetes", False),
                        data.get("cardiaco", False), data.get("hipertension", False), data.get("sifilis", False),
                        data.get("transfusiones", False), data.get("embarazada", False), data.get("meses_embarazo"),
                        data.get("chagas", False), data.get("hepatitis", False), data.get("renales", False),
                        data.get("ulcera", False), data.get("convulsiones", False), data.get("tiempo_fumando"),
                        data.get("otras_enfermedades"), data.get("tomo_medicamento", False), data.get("medicamento_detalle"),
                        data.get("dolor_tipo"), data.get("dolor_localizacion"), data.get("dificultades_funcionales"),
                        data.get("examen_tejidos_blandos"), data.get("firma_paciente"), data.get("firma_profesional"),
                        data.get("motivo_consulta"), data.get("diagnostico_presuntivo"), data.get("plan_tratamiento")
                    # Campos removidos: golpe_como, golpe_recibio_tratamiento, sangrado_encias, movilidad_dentaria,
                    # calculo_detalle, enfermedad_periodontal_detalle, observaciones_dentales, cantidad_dientes
                    # Campo NumAfiliado usado en lugar de 'plan'
                    # Campo Medicamentos actualizado a 'medicamentos_actuales'
                    # Campo Calmante ahora se maneja dentro de 'dolor_detalle'
                    )
                )
                history_id = cursor.lastrowid
                
                # --- PASO 2: Procesar y guardar el Odontograma ---
                if odontograma_data and history_id:
                    # Crear el odontograma principal
                    cursor.execute(
                        """
                        INSERT INTO odontograma (Fecha, HistoriaClinica_id)
                        VALUES (%s, %s)
                        """,
                        (data.get("fecha", datetime.now().date()), history_id)
                    )
                    odontograma_id = cursor.lastrowid
                    
                    # Iterar sobre el estado del odontograma (dientes)
                    for num_diente, data_diente in odontograma_data.items():
                        # Solo crear detallediente si tiene afecciones o procedimientos
                        if data_diente.get('afecciones') or data_diente.get('procedimientos'):
                            
                            # Crear el detallediente
                            cursor.execute(
                                "INSERT INTO detallediente (Odontograma_id, NumDiente) VALUES (%s, %s)",
                                (odontograma_id, int(num_diente))
                            )
                            detallediente_id = cursor.lastrowid
                            
                            # Guardar Afecciones
                            for afeccion in data_diente.get('afecciones', []):
                                cursor.execute("SELECT id FROM afeccion WHERE NombreAfeccion = %s LIMIT 1", (afeccion['nombre'],))
                                afeccion_row = cursor.fetchone()
                                if afeccion_row:
                                    cursor.execute(
                                        "INSERT INTO detalleafeccion (DetalleDiente_id, Afeccion_id, ZonaDiente) VALUES (%s, %s, %s)",
                                        (detallediente_id, afeccion_row['id'], afeccion['zona'])
                                    )
                                    
                            # Guardar Procedimientos
                            for proc in data_diente.get('procedimientos', []):
                                cursor.execute("SELECT id FROM procedimientos WHERE NombreProcedimiento = %s LIMIT 1", (proc['nombre'],))
                                proc_row = cursor.fetchone()
                                if proc_row:
                                    cursor.execute(
                                        """
                                        INSERT INTO detalleprocedimiento 
                                        (DetalleDiente_id, Procedimiento_id, Odontologo_id, Fecha, ZonaDiente, Estado, Observaciones)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """,
                                        (
                                            detallediente_id, proc_row['id'], odontologo_id,
                                            data.get("fecha", datetime.now().date()), # Usar la fecha de la historia
                                            proc['zona'], proc['estado'],
                                            "Registrado desde odontograma interactivo"
                                        )
                                    )
                
                return history_id # Devolver el ID de la historia clínica creada

            except Exception as e:
                # La transacción se revierte automáticamente por el context manager
                raise e # Re-lanzar la excepción para que app.py la capture
    
    @staticmethod
    def update_clinical_history(history_id, data):
        """Actualizar historia clínica existente"""
        with get_db_cursor_with_commit() as cursor:
            cursor.execute(
                """
                UPDATE historiaclinica SET
                Fecha = %s, ObraSocial = %s, NumAfiliado = %s, Alergias = %s, Enfermedades = %s,
                Fuma = %s, Drogas = %s, Medicamentos = %s, NivelDeDolor = %s, Calmante = %s,
                GolpeEnDientes = %s, FechaGolpe = %s, domicilio = %s, edad = %s,
                tratamiento_odontologico = %s, tratamiento_odontologico_detalle = %s,
                colageno = %s, fiebre_reumatica = %s, diabetes = %s, cardiaco = %s,
                hipertension = %s, sifilis = %s, transfusiones = %s, embarazada = %s,
                meses_embarazo = %s, chagas = %s, hepatitis = %s, renales = %s,
                ulcera = %s, convulsiones = %s, tiempo_fumando = %s, otras_enfermedades = %s,
                tomo_medicamento = %s, medicamento_detalle = %s, dolor_tipo = %s,
                dolor_localizacion = %s, dificultades_funcionales = %s, examen_tejidos_blandos = %s,
                firma_paciente = %s, firma_profesional = %s, motivo_consulta = %s,
                diagnostico_presuntivo = %s, plan_tratamiento = %s
                WHERE id = %s
                """,
                (
                    data.get("fecha", datetime.now().date()),
                    data.get("obra_social"),
                    data.get("plan"),
                    data.get("alergias"),
                    data.get("enfermedades"),
                    data.get("fuma", False),
                    data.get("drogas", ""),
                    data.get("medicamentos_actuales"),
                    data.get("dolor_intensidad"),
                    data.get("dolor_detalle"),
                    data.get("golpe_dientes", False),
                    data.get("golpe_cuando") if data.get("golpe_dientes") else None,
                    data.get("domicilio"),
                    data.get("edad"),
                    data.get("tratamiento_odontologico", False),
                    data.get("tratamiento_odontologico_detalle"),
                    data.get("colageno", False),
                    data.get("fiebre_reumatica", False),
                    data.get("diabetes", False),
                    data.get("cardiaco", False),
                    data.get("hipertension", False),
                    data.get("sifilis", False),
                    data.get("transfusiones", False),
                    data.get("embarazada", False),
                    data.get("meses_embarazo"),
                    data.get("chagas", False),
                    data.get("hepatitis", False),
                    data.get("renales", False),
                    data.get("ulcera", False),
                    data.get("convulsiones", False),
                    data.get("tiempo_fumando"),
                    data.get("otras_enfermedades"),
                    data.get("tomo_medicamento", False),
                    data.get("medicamento_detalle"),
                    data.get("dolor_tipo"),
                    data.get("dolor_localizacion"),
                    data.get("dificultades_funcionales"),
                    data.get("examen_tejidos_blandos"),
                    data.get("firma_paciente"),
                    data.get("firma_profesional"),
                    data.get("motivo_consulta"),
                    data.get("diagnostico_presuntivo"),
                    data.get("plan_tratamiento"),
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
    def get_odontograma_details(odontograma_id):
        """
        Obtener todos los detalles de un odontograma específico para la visualización.
        """
        details = {
            'info': None,
            'dientes': {} # Diccionario para almacenar info por NumDiente (usará STRINGS como claves)
        }
        with get_db_cursor() as cursor:
            # 1. Obtener información básica del odontograma y paciente
            cursor.execute("""
                SELECT o.id, o.Fecha, hc.id as HistoriaClinica_id, p.id as Paciente_id, p.Nombre as PacienteNombre
                FROM odontograma o
                JOIN historiaclinica hc ON o.HistoriaClinica_id = hc.id
                JOIN paciente p ON hc.Paciente_id = p.id
                WHERE o.id = %s
            """, (odontograma_id,))
            details['info'] = cursor.fetchone()

            if not details['info']:
                return None # Odontograma no encontrado

            # Formatear fecha si existe
            if details['info'] and details['info'].get('Fecha'): # Usar .get() para seguridad
                 # Asegurarse que sea un objeto date/datetime antes de formatear
                 if hasattr(details['info']['Fecha'], 'strftime'):
                     details['info']['Fecha_formatted'] = details['info']['Fecha'].strftime('%d/%m/%Y')
                 else:
                     details['info']['Fecha_formatted'] = str(details['info']['Fecha']) # Fallback a string


            # 2. Obtener todos los dientes registrados en este odontograma
            cursor.execute("""
                SELECT id, NumDiente
                FROM detallediente
                WHERE Odontograma_id = %s
            """, (odontograma_id,))
            dientes_odontograma = cursor.fetchall()

            # --- MODIFICACIÓN: Usar str(NumDiente) como clave ---
            num_diente_map = {} # Mapa de detallediente_id -> NumDiente (string)
            for diente in dientes_odontograma:
                num_diente_str = str(diente['NumDiente']) # Convertir a string
                details['dientes'][num_diente_str] = { # Usar string como clave
                    'detallediente_id': diente['id'],
                    'afecciones': [],
                    'procedimientos': []
                }
                num_diente_map[diente['id']] = num_diente_str # Guardar el string en el mapa
            # --- FIN MODIFICACIÓN ---
            print(f"DEBUG: num_diente_map = {num_diente_map}") # DEBUG (ahora con strings)


            # --- CORRECCIÓN: Verificar si hay IDs antes de consultar ---
            afecciones = [] # Inicializar como lista vacía
            procedimientos = [] # Inicializar como lista vacía

            if dientes_odontograma: # Solo continuar si encontramos dientes en la tabla detallediente
                detallediente_ids = [d['id'] for d in dientes_odontograma]

                # Asegurarse de que realmente hay IDs antes de formar la consulta
                if detallediente_ids:
                    placeholders = ', '.join(['%s'] * len(detallediente_ids))
                    ids_tuple = tuple(detallediente_ids)

                    # 3. Obtener afecciones
                    print(f"DEBUG: Buscando afecciones para IDs: {ids_tuple}") # Debug
                    cursor.execute(f"""
                        SELECT da.DetalleDiente_id, da.ZonaDiente, a.id as Afeccion_id, a.NombreAfeccion, a.CodigoSNOMED
                        FROM detalleafeccion da
                        JOIN afeccion a ON da.Afeccion_id = a.id
                        WHERE da.DetalleDiente_id IN ({placeholders})
                    """, ids_tuple)
                    afecciones = cursor.fetchall()
                    print(f"DEBUG: Afecciones encontradas: {len(afecciones)}") # Debug

                    # 4. Obtener procedimientos
                    print(f"DEBUG: Buscando procedimientos para IDs: {ids_tuple}") # Debug
                    cursor.execute(f"""
                        SELECT dp.DetalleDiente_id, dp.ZonaDiente, dp.Estado, pr.id as Procedimiento_id, pr.NombreProcedimiento, pr.CodigoSNOMED
                        FROM detalleprocedimiento dp
                        JOIN procedimientos pr ON dp.Procedimiento_id = pr.id
                        WHERE dp.DetalleDiente_id IN ({placeholders})
                    """, ids_tuple)
                    procedimientos = cursor.fetchall()
                    print(f"DEBUG: Procedimientos encontrados: {len(procedimientos)}") # Debug
                else:
                    print("DEBUG: La lista detallediente_ids está vacía (posiblemente un odontograma sin dientes registrados), saltando consultas de afecciones/procedimientos.") # Debug
            else:
                 print("DEBUG: La lista dientes_odontograma está vacía (no hay entradas en detallediente para este odontograma_id), saltando consultas de afecciones/procedimientos.") # Debug
            # --- FIN CORRECCIÓN ---


            # 5. Organizar datos usando CLAVES DE TEXTO
            for afeccion in afecciones:
                detallediente_id = afeccion['DetalleDiente_id']
                num_diente_str = num_diente_map.get(detallediente_id) # Obtener el num diente como string
                print(f"DEBUG: Procesando afeccion ID {afeccion['Afeccion_id']} para detallediente_id {detallediente_id} -> num_diente_str {num_diente_str}") # DEBUG
                if num_diente_str and num_diente_str in details['dientes']: # Verificar existencia con string
                    details['dientes'][num_diente_str]['afecciones'].append({ # Usar string como clave
                        'zona': afeccion['ZonaDiente'],
                        'nombre': afeccion['NombreAfeccion'],
                        'id': afeccion['Afeccion_id']
                    })
                else:
                     print(f"WARN: No se encontró mapeo para detallediente_id {detallediente_id} o diente {num_diente_str} no inicializado (afeccion)")


            for proc in procedimientos:
                detallediente_id = proc['DetalleDiente_id']
                num_diente_str = num_diente_map.get(detallediente_id) # Obtener el num diente como string
                print(f"DEBUG: Procesando proc ID {proc['Procedimiento_id']} para detallediente_id {detallediente_id} -> num_diente_str {num_diente_str}") # DEBUG
                if num_diente_str and num_diente_str in details['dientes']: # Verificar existencia con string
                    details['dientes'][num_diente_str]['procedimientos'].append({ # Usar string como clave
                        'zona': proc['ZonaDiente'],
                        'nombre': proc['NombreProcedimiento'],
                        'estado': proc['Estado'],
                        'id': proc['Procedimiento_id']
                    })
                else:
                    print(f"WARN: No se encontró mapeo para detallediente_id {detallediente_id} o diente {num_diente_str} no inicializado (procedimiento)")

        return details
    
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
    def get_afecciones():
        """Obtener catálogo de afecciones"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM afeccion ORDER BY NombreAfeccion")
            return cursor.fetchall()

    @staticmethod
    def get_latest_odontograma_info_by_patient(patient_id):
        """Obtener la info básica del último odontograma de un paciente"""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT o.id, o.Fecha, o.HistoriaClinica_id
                FROM odontograma o
                JOIN historiaclinica hc ON o.HistoriaClinica_id = hc.id
                WHERE hc.Paciente_id = %s
                ORDER BY o.Fecha DESC, o.id DESC
                LIMIT 1
            """, (patient_id,))
            odontograma_info = cursor.fetchone()
            if odontograma_info and odontograma_info.get('Fecha'):
                # Añadir fecha formateada si existe
                odontograma_info['Fecha_formatted'] = odontograma_info['Fecha'].strftime('%d/%m/%Y')
            return odontograma_info

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
