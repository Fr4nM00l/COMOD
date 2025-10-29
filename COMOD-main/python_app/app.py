import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
from datetime import datetime, date
import json

from db_utils import get_db_cursor, get_db_cursor_with_commit
from decorators import require_secretario, require_odontologo
from utils import validate_appointment_datetime, create_success_response, create_error_response, validate_appointment_availability, validate_required_fields, handle_load_error, handle_validation_error, handle_not_found_error
from services import (
    PatientService, AppointmentService, DentistService, 
    ClinicalHistoryService, OdontogramaService, AvailabilityService
)
from email_service import email_service
from flask_moment import Moment
from utils import format_time_from_timedelta, escapejs_filter


load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    moment = Moment(app)
    #moment.locale('es')
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SECRET_KEY"] = secret_key
    app.config["SESSION_PERMANENT"] = False
    
    # Configuración de email
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@clinica.com')
    
    # Inicializar el servicio de email
    email_service.init_app(app)
    
    # --- REGISTRAR FILTROS DE JINJA2 ---
    @app.template_filter('format_time')
    def format_time_filter_wrapper(timedelta_obj): # Renombrar para evitar conflicto
        if timedelta_obj is None: return ""
        return format_time_from_timedelta(timedelta_obj)

    # --- AÑADIR ESTA LÍNEA PARA REGISTRAR escapejs ---
    app.jinja_env.filters['escapejs'] = escapejs_filter
    # --- FIN AÑADIR LÍNEA ---


    
    @app.template_filter('format_time')
    def format_time_filter(timedelta_obj):
        """Filtro para formatear objetos timedelta como tiempo"""
        if timedelta_obj is None:
            return ""
        return format_time_from_timedelta(timedelta_obj)

    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            selected_role = request.form.get("role")
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if selected_role not in {"odontologo", "secretario"}:
                flash("Debe seleccionar un rol válido.", "error")
                return render_template("login.html")

            if not username or not password:
                flash("Usuario y contraseña son obligatorios.", "error")
                return render_template("login.html")

            try:
                user = DentistService.authenticate_user(username, password, selected_role)
            except Exception as e:
                flash("Error de conexión. Intente nuevamente.", "error")
                return render_template("login.html")

            if not user or (user.get("Contraseña") or "") != password:
                flash("Credenciales inválidas.", "error")
                return render_template("login.html")

            session.clear()
            session["role"] = selected_role
            session["user_id"] = user["id"]
            session["nombre"] = user.get("Nombre")

            if selected_role == "odontologo":
                return redirect(url_for("odontologo_dashboard"))
            return redirect(url_for("secretario_dashboard"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Sesión cerrada correctamente.", "success")
        return redirect(url_for("login"))

    @app.route("/odontologo")
    @require_odontologo
    def odontologo_dashboard():
        # Inicializar variables fuera del try para que existan en caso de error
        nombre_usuario = None
        upcoming_appointments = []
        odontologo_id = None

        try:
            # --- OBTENER DATOS DE SESIÓN Y BD DENTRO DEL TRY ---
            odontologo_id = session.get("user_id") # Acceder a session aquí dentro
            nombre_usuario = session.get("nombre")   # Acceder a session aquí dentro

            print(f"DEBUG: Intentando obtener turnos para odontólogo ID: {odontologo_id}")
            upcoming_appointments = AppointmentService.get_upcoming_appointments(odontologo_id, limit=10)
            print(f"DEBUG: Turnos obtenidos: {len(upcoming_appointments)}")

            # --- MOVER RENDER_TEMPLATE AQUÍ DENTRO ---
            # Si todo hasta aquí funcionó, renderizar la plantilla
            return render_template(
                "odontologo_dashboard.html",
                nombre=nombre_usuario, # Usar la variable obtenida
                upcoming_appointments=upcoming_appointments,
            )
            # --- FIN RENDER_TEMPLATE MOVIDO ---

        except mysql.connector.Error as db_err:
            print(f"!!!!!!!! ERROR DE BASE DE DATOS al obtener turnos: {db_err} !!!!!!!!")
            flash(f"Error de base de datos al cargar turnos: {db_err}. Verifique la conexión.", "error")
            # --- AÑADIR RETURN EN EXCEPT ---
            # Renderizar la plantilla con datos vacíos o un mensaje de error si ocurre un error de BD
            return render_template(
                "odontologo_dashboard.html",
                nombre=nombre_usuario, # Puede ser None si el error fue antes
                upcoming_appointments=[], # Lista vacía
                error_message=f"Error de BD: {db_err}" # Pasar mensaje de error (opcional)
            )
            # --- FIN RETURN EN EXCEPT ---
        except Exception as e:
            print(f"ERROR: Excepción general al obtener turnos o renderizar: {e}") # Mensaje actualizado
            handle_load_error(e, "el dashboard", flash) # Mensaje actualizado
            # --- AÑADIR RETURN EN EXCEPT ---
            # Renderizar la plantilla con datos vacíos o un mensaje de error
            return render_template(
                "odontologo_dashboard.html",
                nombre=nombre_usuario, # Puede ser None si el error fue antes
                upcoming_appointments=[], # Lista vacía
                error_message=f"Error general: {e}" # Pasar mensaje de error (opcional)
            )
            # --- FIN RETURN EN EXCEPT ---
        # No debería haber un 'return' fuera del try/except si todos los caminos devuelven algo

    # Rutas específicas para odontólogos
    @app.route("/odontologo/pacientes")
    @require_odontologo
    def odontologo_pacientes():
        """Vista de pacientes para odontólogos, incluyendo estado de historia y odontograma."""
        try:
            # 1. Obtener todos los pacientes (usamos get_all_patients que trae más datos)
            all_patients_raw = PatientService.get_all_patients()
            
            patients_with_status = []
            
            # 2. Para cada paciente, verificar historia y último odontograma
            for patient in all_patients_raw:
                patient_id = patient['id']
                
                # Verificar si tiene historias clínicas
                histories = ClinicalHistoryService.get_clinical_histories_by_patient(patient_id)
                patient['has_history'] = bool(histories) # True si la lista no está vacía
                
                # Verificar si tiene odontogramas
                odontogramas = OdontogramaService.get_odontogramas_by_patient(patient_id)
                patient['has_odontogram'] = bool(odontogramas) # True si la lista no está vacía

                # Calcular edad (si no viene ya calculada)
                if 'edad' not in patient and patient.get('FechaNacimiento'):
                    try:
                        today = date.today()
                        birth_date = patient['FechaNacimiento']
                        # Verificar que birth_date sea un objeto date
                        if isinstance(birth_date, date):
                            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                            patient['edad'] = age
                        else:
                             patient['edad'] = None
                    except:
                        patient['edad'] = None # En caso de error al calcular
                elif 'edad' not in patient:
                     patient['edad'] = None

                patients_with_status.append(patient)

            return render_template("odontologo/pacientes.html", patients=patients_with_status)

        except Exception as e:
            handle_load_error(e, "pacientes", flash)
            return render_template("odontologo/pacientes.html", patients=[])

    @app.route("/odontologo/historias-clinicas")
    @require_odontologo
    def odontologo_historias():
        """Vista de historias clínicas para odontólogos"""
        try:
            histories = ClinicalHistoryService.get_all_clinical_histories()
            return render_template("odontologo/historias_clinicas.html", histories=histories)
        except Exception as e:
            handle_load_error(e, "historias clínicas", flash)
            return render_template("odontologo/historias_clinicas.html", histories=[])

    @app.route("/odontologo/paciente/<int:patient_id>/historias")
    @require_odontologo
    def paciente_historias_clinicas(patient_id):
        """Vista de historias clínicas de un paciente específico"""
        try:
            # Obtener información del paciente
            patient = PatientService.get_patient_by_id(patient_id)
            if not patient:
                flash("Paciente no encontrado", "error")
                return redirect(url_for("odontologo_pacientes"))
            
            # Obtener todas las historias clínicas del paciente
            histories = ClinicalHistoryService.get_clinical_histories_by_patient(patient_id)
            
            return render_template("odontologo/paciente_historias.html", 
                                 patient=patient, 
                                 histories=histories)
        except Exception as e:
            handle_load_error(e, "historias del paciente", flash)
            return redirect(url_for("odontologo_pacientes"))

    @app.route("/odontologo/historia-clinica/<int:history_id>")
    @require_odontologo
    def ver_historia_clinica(history_id):
        """Vista detallada de una historia clínica específica"""
        try:
            history = ClinicalHistoryService.get_clinical_history_by_id(history_id)
            if not history:
                flash("Historia clínica no encontrada", "error")
                return redirect(url_for("odontologo_historias"))
            
            return render_template("odontologo/ver_historia_clinica.html", history=history)
        except Exception as e:
            handle_load_error(e, "historia clínica", flash)
            return redirect(url_for("odontologo_historias"))

    @app.route("/odontologo/odontogramas")
    @require_odontologo
    def odontologo_odontogramas():
        """Vista de odontogramas para odontólogos, mostrando todos los pacientes."""
        try:
            # 1. Obtener todos los pacientes
            all_patients = PatientService.get_all_patients_basic()
            
            patients_with_odontogram_status = []
            
            # 2. Para cada paciente, buscar su último odontograma
            for patient in all_patients:
                latest_odontogram = OdontogramaService.get_latest_odontograma_info_by_patient(patient['id'])
                
                patient_data = {
                    'PacienteID': patient['id'],
                    'PacienteNombre': patient['Nombre'],
                    'PacienteDNI': patient['DNI'],
                    'OdontogramaID': None,
                    'OdontogramaFecha': None,
                    'OdontogramaFechaFormatted': None,
                    'HistoriaClinicaID': None,
                    'TieneOdontograma': False
                }
                
                if latest_odontogram:
                    patient_data['OdontogramaID'] = latest_odontogram['id']
                    patient_data['OdontogramaFecha'] = latest_odontogram['Fecha']
                    patient_data['OdontogramaFechaFormatted'] = latest_odontogram.get('Fecha_formatted')
                    patient_data['HistoriaClinicaID'] = latest_odontogram['HistoriaClinica_id']
                    patient_data['TieneOdontograma'] = True
                    
                patients_with_odontogram_status.append(patient_data)

            return render_template("odontologo/odontogramas.html",
                                 patients_data=patients_with_odontogram_status) # Cambiado nombre de variable

        except Exception as e:
            handle_load_error(e, "pacientes y odontogramas", flash)
            return render_template("odontologo/odontogramas.html", patients_data=[])

    @app.route("/odontologo/consulta/<int:patient_id>")
    @require_odontologo
    def odontologo_consulta(patient_id):
        """
        Verifica si una consulta es válida (turno hoy) y REDIRIGE 
        al formulario de nueva historia clínica.
        """
        try:
            patient = PatientService.get_patient_by_id(patient_id)
            if not patient:
                flash("Paciente no encontrado", "error")
                return redirect(url_for("odontologo_pacientes"))
            
            from datetime import date
            today = date.today()
            odontologo_id = session.get('user_id')
            
            # REGLA DE NEGOCIO: Verificar si hay un turno para este paciente hoy
            appointment_info = AppointmentService.get_patient_appointment_today(patient_id, odontologo_id, today)
            
            if not appointment_info:
                flash(f"El paciente {patient['Nombre']} no tiene un turno programado para hoy. Solo se pueden realizar consultas a pacientes con turnos activos.", "warning")
                return redirect(url_for("odontologo_dashboard"))
            
            # ¡Éxito! Redirigir al formulario de nueva historia, pasando el ID del turno
            return redirect(url_for('nueva_historia_clinica', 
                                  patient_id=patient_id, 
                                  appointment_id=appointment_info['id']))

        except Exception as e:
            handle_load_error(e, "consulta", flash)
            return redirect(url_for("odontologo_pacientes"))

    @app.route("/odontologo/historia-clinica/nueva/<int:patient_id>")
    @require_odontologo
    def nueva_historia_clinica(patient_id):
        """
        Muestra el formulario para crear una nueva historia clínica.
        Carga el último odontograma del paciente para visualización.
        """
        try:
            # Obtener el ID del turno desde los argumentos de la URL (enviado por la redirección)
            appointment_id = request.args.get('appointment_id')
            patient = PatientService.get_patient_by_id(patient_id)
            
            if not patient:
                flash("Paciente no encontrado", "error")
                return redirect(url_for("odontologo_pacientes"))
            
            appointment_info = None
            if appointment_id:
                appointment_info = AppointmentService.get_appointment_by_id(appointment_id)
                # Formatear hora si es necesario (asumiendo que get_appointment_by_id devuelve objeto timedelta)
                if appointment_info and appointment_info.get('HoraTurno'):
                    appointment_info['HoraTurno'] = format_time_from_timedelta(appointment_info['HoraTurno'])

            fecha_actual = datetime.now().strftime('%d/%m/%Y')

            # --- LÓGICA DE ODONTOGRAMA MEJORADA ---
            # Cargar el ÚLTIMO odontograma existente del paciente
            odontograma_data = None
            latest_odontogram_info = OdontogramaService.get_latest_odontograma_info_by_patient(patient_id)
            
            if latest_odontogram_info:
                # Cargar los detalles completos de ESE odontograma
                odontograma_data = OdontogramaService.get_odontograma_details(latest_odontogram_info['id'])
                # Usamos la fecha de HOY para la "nueva" historia, pero los datos del odontograma son del último
                odontograma_data['info']['Fecha_formatted'] = fecha_actual
            
            # Si no hay ningún odontograma previo, preparamos uno vacío
            if not odontograma_data:
                odontograma_data = {
                    'info': {'PacienteNombre': patient['Nombre'], 'Fecha_formatted': fecha_actual, 'id': None},
                    'dientes': {} # Vacío
                }
            
            # --- NUEVO: Cargar catálogos para el modal ---
            afecciones_list = OdontogramaService.get_afecciones()
            procedimientos_list = OdontogramaService.get_procedimientos()
            # --- FIN NUEVO ---

            return render_template("odontologo/nueva_historia_clinica.html",
                                 patient=patient,
                                 fecha_actual=fecha_actual,
                                 odontograma=odontograma_data,
                                 appointment_info=appointment_info,
                                 history_id=None,
                                 afecciones_list=afecciones_list,      # <-- Pasar afecciones
                                 procedimientos_list=procedimientos_list # <-- Pasar procedimientos
                                )

        except Exception as e:
            handle_load_error(e, "formulario de historia clínica", flash)
            return render_template("odontologo/nueva_historia_clinica.html",
                                 patient=patient if patient else {},
                                 fecha_actual=datetime.now().strftime('%d/%m/%Y'),
                                 odontograma={'info': {}, 'dientes': {}},
                                 afecciones_list=[],
                                 procedimientos_list=[]
                                )

    @app.route("/odontologo/historia-clinica/editar/<int:history_id>")
    @require_odontologo
    def editar_historia_clinica(history_id):
        """Editar historia clínica existente"""
        try:
            history = ClinicalHistoryService.get_clinical_history_by_id(history_id)
            if not history:
                flash("Historia clínica no encontrada", "error")
                return redirect(url_for("odontologo_historias"))
            
            patient = PatientService.get_patient_by_id(history['Paciente_id'])
            return render_template("odontologo/editar_historia_clinica.html", 
                                 patient=patient, history=history)
        except Exception as e:
            handle_load_error(e, "historia", flash)
            return redirect(url_for("odontologo_historias"))

    @app.route("/odontologo/odontograma/<int:odontograma_id>")
    @require_odontologo
    def ver_odontograma_visual(odontograma_id):
        """Muestra el odontograma visual detallado."""
        try:
            odontograma_data = OdontogramaService.get_odontograma_details(odontograma_id)

            if not odontograma_data:
                flash(f"Odontograma con ID {odontograma_id} no encontrado.", "error")
                return redirect(url_for("odontologo_odontogramas"))

            # Pasar los datos a la plantilla
            return render_template("odontologo/odontograma_visual.html",
                                 odontograma=odontograma_data)

        except Exception as e:
            handle_load_error(e, f"odontograma {odontograma_id}", flash)
            return redirect(url_for("odontologo_odontogramas"))

    @app.route("/odontologo/historia-clinica/guardar", methods=["POST"])
    @require_odontologo
    def guardar_historia_clinica():
        """Guardar historia clínica (crear o actualizar)"""
        try:
            data = request.get_json()

            data['odontologo_id'] = session.get('user_id')

            # --- CORRECCIÓN: Validar campos obligatorios actualizados ---
            required_fields = ["paciente_id", "motivo_consulta", "plan_tratamiento", "diagnostico_presuntivo"]
            is_valid_fields, missing_fields = validate_required_fields(data, required_fields)

            if not is_valid_fields:
                error_response, status_code = handle_validation_error(missing_fields)
            return error_response

        # Guardar historia clínica
            appointment_id = data.get('appointment_id') # Obtener el ID del turno si existe

            if data.get('history_id'):
                history_id = ClinicalHistoryService.update_clinical_history(data['history_id'], data)
                message = "Historia clínica actualizada exitosamente"
            else:
            # Crear nueva historia
                history_id = ClinicalHistoryService.create_clinical_history(data)
                message = "Historia clínica creada exitosamente"

        # --- NUEVO: Actualizar estado del turno si corresponde ---
            if history_id and appointment_id:
                try:
                # Usar el servicio para actualizar el estado
                # (Necesitarás crear este método si no existe)
                    AppointmentService.update_appointment_status(appointment_id, 'completado')
                    print(f"✅ Estado del turno {appointment_id} actualizado a 'completado'")
                except Exception as e_status:
                    print(f"⚠️ Error al actualizar estado del turno {appointment_id}: {str(e_status)}")
                # No fallar la respuesta principal por esto, pero loguear el error.
        # --- FIN NUEVO ---

            return create_success_response(message, {"history_id": history_id})

        except Exception as e:
        # Imprimir el error en la consola del servidor para depuración
            print(f"Error executing guardar_historia_clinica: {str(e)}")
            import traceback
            traceback.print_exc() # Muestra el traceback completo

        # --- NUEVO: Verificar si estamos en un contexto de solicitud ---
            from flask import has_request_context
            if has_request_context():
            # Si estamos manejando una solicitud web real, devolver error JSON
            # NOTA: Asegúrate que la función create_error_response esté definida ANTES en utils.py
            # si no lo está, mueve su definición o importa flask.jsonify aquí directamente.
            # from flask import jsonify # Podrías necesitar esto si create_error_response falla aquí
            # return jsonify(success=False, message=f"Error al guardar historia clínica: {str(e)}"), 500

            # Asumiendo que create_error_response está bien definida y disponible:
                return create_error_response(f"Error al guardar historia clínica: {str(e)}", 500)
            else:
            # Si esto se ejecuta durante el inicio de la app (el error original),
            # es mejor simplemente lanzar la excepción original para que falle el inicio
            # y quede claro que el problema es de configuración/ejecución temprana.
                print("¡¡¡ ERROR CRÍTICO: La función 'guardar_historia_clinica' se ejecutó fuera de contexto durante el inicio de la app !!!")
            # No intentes devolver una respuesta aquí. Deja que la app falle al iniciar.
            # Opcional: podrías simplemente imprimir y no hacer 'raise e' si quieres
            # que intente seguir, pero fallar es más claro.
                raise e # Vuelve a lanzar el error original (RuntimeError)
        # --- FIN NUEVO ---

    # Rutas para gestión de disponibilidad

    @app.route("/odontologo/disponibilidad")
    @require_odontologo
    def odontologo_disponibilidad():
        """Vista de gestión de disponibilidad"""
        try:
            odontologo_id = session.get("user_id")
            work_schedule = AvailabilityService.get_work_schedule(odontologo_id)
            
            # Obtener mes y año actual
            from datetime import datetime
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month
            
            return render_template("odontologo/disponibilidad.html", 
                                 work_schedule=work_schedule,
                                 current_year=year,
                                 current_month=month)
        except Exception as e:
            handle_load_error(e, "disponibilidad", flash)
            return render_template("odontologo/disponibilidad.html", 
                                 work_schedule=[], 
                                 current_year=datetime.now().year,
                                 current_month=datetime.now().month)

    @app.route("/odontologo/disponibilidad/horarios", methods=["POST"])
    @require_odontologo
    def guardar_horarios_trabajo():
        """Guardar horarios de trabajo semanales"""
        try:
            odontologo_id = session.get("user_id")
            data = request.get_json()
            
            AvailabilityService.update_work_schedule(odontologo_id, data)
            
            return create_success_response("Horarios de trabajo guardados exitosamente")
            
        except Exception as e:
            return create_error_response(f"Error al guardar horarios: {str(e)}")

    @app.route("/odontologo/disponibilidad/generar-mes", methods=["POST"])
    @require_odontologo
    def generar_disponibilidad_mes():
        """Generar disponibilidad para un mes específico"""
        try:
            odontologo_id = session.get("user_id")
            data = request.get_json()
            
            year = data.get("year")
            month = data.get("month")
            
            if not year or not month:
                return create_error_response("Año y mes son requeridos")
            
            # Generar slots de disponibilidad
            availability_slots = AvailabilityService.generate_monthly_availability(odontologo_id, year, month)
            
            # Guardar en la base de datos
            AvailabilityService.save_monthly_availability(odontologo_id, year, month, availability_slots)
            
            return create_success_response(f"Disponibilidad generada para {month}/{year}", {
                "slots_generated": len(availability_slots)
            })
            
        except Exception as e:
            return create_error_response(f"Error al generar disponibilidad: {str(e)}")

    @app.route("/odontologo/disponibilidad/mes/<int:year>/<int:month>")
    @require_odontologo
    def ver_disponibilidad_mes(year, month):
        """Ver disponibilidad de un mes específico"""
        try:
            odontologo_id = session.get("user_id")
            
            # Obtener disponibilidad del mes
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT fecha, hora_inicio, hora_fin, disponible, observaciones
                    FROM disponibilidad_medico
                    WHERE odontologo_id = %s 
                    AND YEAR(fecha) = %s 
                    AND MONTH(fecha) = %s
                    ORDER BY fecha, hora_inicio
                    """,
                    (odontologo_id, year, month)
                )
                availability_raw = cursor.fetchall()
                
                # Convertir objetos timedelta a strings para el template
                availability = []
                for slot in availability_raw:
                    slot_dict = dict(slot)
                    
                    # Convertir fecha a string formateado
                    if hasattr(slot_dict['fecha'], 'strftime'):
                        fecha_str = slot_dict['fecha'].strftime('%d/%m/%Y')
                    else:
                        fecha_str = str(slot_dict['fecha'])
                    
                    # Convertir hora_inicio
                    if isinstance(slot_dict['hora_inicio'], str):
                        hora_inicio_str = slot_dict['hora_inicio']
                    else:
                        # Es un timedelta, convertir a string
                        from datetime import datetime, timedelta
                        hora_inicio_str = (datetime.min + slot_dict['hora_inicio']).time().strftime('%H:%M:%S')
                    
                    # Convertir hora_fin
                    if isinstance(slot_dict['hora_fin'], str):
                        hora_fin_str = slot_dict['hora_fin']
                    else:
                        # Es un timedelta, convertir a string
                        hora_fin_str = (datetime.min + slot_dict['hora_fin']).time().strftime('%H:%M:%S')
                    
                    slot_dict['fecha'] = fecha_str
                    slot_dict['hora_inicio'] = hora_inicio_str
                    slot_dict['hora_fin'] = hora_fin_str
                    availability.append(slot_dict)
            
            return render_template("odontologo/disponibilidad_mes.html", 
                                 availability=availability,
                                 year=year,
                                 month=month)
            
        except Exception as e:
            handle_load_error(e, "disponibilidad del mes", flash)
            return redirect(url_for("odontologo_disponibilidad"))

    @app.route("/api/disponibilidad/<int:odontologo_id>/fechas")
    def api_get_available_dates(odontologo_id):
        """API para obtener fechas disponibles de un médico"""
        try:
            with get_db_cursor() as cursor:
                # Obtener fechas únicas disponibles para el médico
                cursor.execute(
                    """
                    SELECT DISTINCT fecha
                    FROM disponibilidad_medico
                    WHERE odontologo_id = %s 
                    AND disponible = TRUE
                    AND fecha >= CURDATE()
                    ORDER BY fecha
                    """,
                    (odontologo_id,)
                )
                dates_raw = cursor.fetchall()
                
                # Formatear fechas para el frontend
                available_dates = []
                for date_row in dates_raw:
                    fecha = date_row['fecha']
                    if hasattr(fecha, 'strftime'):
                        fecha_str = fecha.strftime('%Y-%m-%d')
                    else:
                        fecha_str = str(fecha)
                    
                    # Formatear fecha para mostrar al usuario
                    if hasattr(fecha, 'strftime'):
                        fecha_display = fecha.strftime('%d/%m/%Y')
                    else:
                        fecha_display = str(fecha)
                    
                    available_dates.append({
                        'fecha': fecha_str,
                        'fecha_display': fecha_display
                    })
                
                return create_success_response("Fechas disponibles obtenidas", {
                    "fechas": available_dates
                })
                
        except Exception as e:
            return create_error_response(f"Error al obtener fechas disponibles: {str(e)}")

    @app.route("/api/disponibilidad/<int:odontologo_id>/<fecha>")
    def api_get_available_slots(odontologo_id, fecha):
        """API para obtener slots disponibles de un médico en una fecha"""
        try:
            available_slots = AvailabilityService.get_available_slots(odontologo_id, fecha)
            
            # Formatear slots para el frontend
            formatted_slots = []
            for slot in available_slots:
                # Convertir hora_inicio
                if isinstance(slot['hora_inicio'], str):
                    hora_inicio_str = slot['hora_inicio'][:5]  # Tomar solo HH:MM
                else:
                    # Es un timedelta, convertir a string
                    from datetime import datetime
                    hora_inicio_str = (datetime.min + slot['hora_inicio']).time().strftime('%H:%M')
                
                # Convertir hora_fin
                if isinstance(slot['hora_fin'], str):
                    hora_fin_str = slot['hora_fin'][:5]  # Tomar solo HH:MM
                else:
                    # Es un timedelta, convertir a string
                    hora_fin_str = (datetime.min + slot['hora_fin']).time().strftime('%H:%M')
                
                formatted_slots.append({
                    'hora_inicio': hora_inicio_str,
                    'hora_fin': hora_fin_str,
                    'observaciones': slot['observaciones']
                })
            
            return create_success_response("Slots disponibles obtenidos", {
                "slots": formatted_slots
            })
            
        except Exception as e:
            return create_error_response(f"Error al obtener slots disponibles: {str(e)}")

    @app.route("/secretario")
    @require_secretario
    def secretario_dashboard():
        try:
            next_appointments = AppointmentService.get_upcoming_appointments(limit=10)
            
            # Obtener conteos usando el contexto manager
            with get_db_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM paciente")
                patient_count = (cursor.fetchone() or {}).get("total", 0)

                cursor.execute("SELECT COUNT(*) AS total FROM odontologo")
                dentist_count = (cursor.fetchone() or {}).get("total", 0)
                
        except Exception as e:
            handle_load_error(e, "datos", flash)
            next_appointments = []
            patient_count = 0
            dentist_count = 0

        return render_template(
            "secretario_dashboard.html",
            nombre=session.get("nombre"),
            next_appointments=next_appointments,
            patient_count=patient_count,
            dentist_count=dentist_count,
        )

    # Secretary section routes
    @app.route("/secretario/pacientes")
    @require_secretario
    def secretario_pacientes():
        try:
            patients = PatientService.get_all_patients()
        except Exception as e:
            handle_load_error(e, "pacientes", flash)
            patients = []

        return render_template("sections/pacientes_section.html", patients=patients)

    @app.route("/secretario/turnos")
    @require_secretario
    def secretario_turnos():
        try:
            next_appointments = AppointmentService.get_all_appointments()
        except Exception as e:
            handle_load_error(e, "turnos", flash)
            next_appointments = []

        return render_template("sections/turnos_section.html", 
                            next_appointments=next_appointments, 
                            today=date.today().isoformat())

    @app.route("/secretario/turnos/<int:turno_id>", methods=["DELETE"])
    @require_secretario
    def delete_turno(turno_id):
        try:
            rows_affected = AppointmentService.delete_appointment(turno_id)
            
            if rows_affected == 0:
                error_response, status_code = handle_not_found_error("Turno", turno_id)
                return error_response
            
            return create_success_response("Turno eliminado correctamente")
            
        except Exception as e:
            print(f"Error deleting turno: {e}")
            return create_error_response("Error al eliminar el turno", 500)

    @app.route("/secretario/historias")
    @require_secretario
    def secretario_historias():
        try:
            clinical_histories = ClinicalHistoryService.get_all_clinical_histories()
            patients_without_history = ClinicalHistoryService.get_patients_without_history()
        except Exception as e:
            handle_load_error(e, "historias clínicas", flash)
            clinical_histories = []
            patients_without_history = []

        return render_template("sections/historias_section.html",
                            clinical_histories=clinical_histories,
                            patients_without_history=patients_without_history)

    @app.route("/secretario/odontogramas")
    @require_secretario
    def secretario_odontogramas():
        try:
            odontogramas = OdontogramaService.get_all_odontogramas()
            patients_without_odontograma = OdontogramaService.get_patients_without_odontograma()
            procedimientos = OdontogramaService.get_procedimientos()
        except Exception as e:
            handle_load_error(e, "odontogramas", flash)
            odontogramas = []
            patients_without_odontograma = []
            procedimientos = []

        return render_template("sections/odontogramas_section.html",
                            odontogramas=odontogramas,
                            patients_without_odontograma=patients_without_odontograma,
                            procedimientos=procedimientos)

    # API endpoints for patients
    @app.route("/secretario/paciente", methods=["POST"])
    @require_secretario
    def create_patient():
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get("nombre") or not data.get("dni"):
                return create_error_response("Nombre y DNI son obligatorios")
            
            # Check if DNI already exists
            existing_patient = PatientService.get_patient_by_dni(data["dni"])
            if existing_patient:
                return create_error_response(
                    f"Ya existe un paciente con el DNI {data['dni']}. Paciente registrado: {existing_patient['Nombre']}"
                )

            # Create new patient
            patient_id = PatientService.create_patient(data)
            return create_success_response("Paciente creado exitosamente", {"patient_id": patient_id})
            
        except Exception as e:
            return create_error_response(str(e), 500)

    @app.route("/secretario/paciente/<int:patient_id>", methods=["PUT"])
    @require_secretario
    def update_patient(patient_id):
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get("nombre") or not data.get("dni"):
                return create_error_response("Nombre y DNI son obligatorios")

            # Check if DNI already exists for another patient
            existing_patient = PatientService.get_patient_by_dni(data["dni"])
            if existing_patient and existing_patient["id"] != patient_id:
                return create_error_response(
                    f"Ya existe otro paciente con el DNI {data['dni']}. Paciente registrado: {existing_patient['Nombre']}"
                )

            # Update patient
            rows_affected = PatientService.update_patient(patient_id, data)
            
            if rows_affected == 0:
                return create_error_response("Paciente no encontrado", 404)
            
            return create_success_response("Paciente actualizado exitosamente")
            
        except Exception as e:
            return create_error_response(str(e), 500)

    @app.route("/secretario/paciente/<int:patient_id>")
    @require_secretario
    def get_patient(patient_id):
        try:
            patient = PatientService.get_patient_by_id(patient_id)
            
            if not patient:
                return create_error_response("Paciente no encontrado", 404)
            
            return create_success_response(data={"patient": patient})
            
        except Exception as e:
            return create_error_response(str(e), 500)

    @app.route("/secretario/paciente/check-dni/<dni>")
    @require_secretario
    def check_dni_exists(dni):
        try:
            existing_patient = PatientService.get_patient_by_dni(dni)
            
            if existing_patient:
                return create_success_response(
                    f"Ya existe un paciente con el DNI {dni}",
                    {"exists": True, "patient_name": existing_patient["Nombre"]}
                )
            else:
                return create_success_response("DNI disponible", {"exists": False})
                
        except Exception as e:
            return create_error_response(f"Error al verificar DNI: {str(e)}", 500)

    @app.route("/api/historia-clinica/detalles/<int:history_id>")
    @require_odontologo # O el rol que corresponda
    def api_get_historia_detalles(history_id):
        """API para obtener detalles completos de una historia y su odontograma"""
        try:
            history = ClinicalHistoryService.get_clinical_history_by_id(history_id)
            if not history:
                return create_error_response("Historia clínica no encontrada", 404)

        # Formatear la fecha si existe
            if history.get('Fecha'):
                history['Fecha_formatted'] = history['Fecha'].strftime('%d/%m/%Y')

        # Buscar el odontograma asociado a ESTA historia específica
            odontograma_data = None
            with get_db_cursor() as cursor:
             cursor.execute("SELECT id FROM odontograma WHERE HistoriaClinica_id = %s LIMIT 1", (history_id,))
             odontograma_info = cursor.fetchone()

            if odontograma_info:
            # Si se encontró un odontograma para ESTA historia, cargar sus detalles
                odontograma_data = OdontogramaService.get_odontograma_details(odontograma_info['id'])

            return create_success_response(data={"history": history, "odontograma": odontograma_data})

        except Exception as e:
            print(f"Error en /api/historia-clinica/detalles: {str(e)}")
            return create_error_response(f"Error al obtener detalles: {str(e)}", 500)


    @app.route("/secretario/paciente/<int:patient_id>", methods=["DELETE"])
    @require_secretario
    def delete_patient(patient_id):
        try:
            rows_affected = PatientService.delete_patient(patient_id)
            return create_success_response("Paciente eliminado exitosamente")
        except Exception as e:
            return create_error_response(str(e), 500)

    @app.route("/secretario/pacientes/lista")
    @require_secretario
    def get_patients_list():
        try:
            patients = PatientService.get_patients_list()
            return jsonify(patients)
        except Exception as e:
            return create_error_response(str(e), 500)

    # API endpoints for appointments
    @app.route("/secretario/turno", methods=["POST"])
    @require_secretario
    def create_appointment():
        try:
            data = request.get_json()
            print(f"📋 Received data: {data}")  # Debug
            
            # Validate required fields
            required_fields = ["paciente_id", "odontologo_id", "fecha", "hora"]
            is_valid_fields, missing_fields = validate_required_fields(data, required_fields)
            
            if not is_valid_fields:
                error_response, status_code = handle_validation_error(missing_fields)
                return error_response

            # Validate appointment availability (date, time, and duplicates)
            with get_db_cursor() as cursor:
                is_valid, error_message = validate_appointment_availability(
                    cursor, 
                    data["fecha"], 
                    data["hora"], 
                    data["odontologo_id"], 
                    data.get("paciente_id")
                )
                if not is_valid:
                    return create_error_response(error_message)

            # Create appointment
            appointment_id = AppointmentService.create_appointment(data)
            
            # Enviar email de confirmación si el paciente tiene email
            try:
                # Obtener datos del paciente y del turno para el email
                patient = PatientService.get_patient_by_id(data["paciente_id"])
                dentist = DentistService.get_dentist_by_id(data["odontologo_id"])
                
                if patient and patient.get('email') and dentist:
                    # Preparar datos para el email
                    appointment_data = {
                        'fecha': data["fecha"],
                        'fecha_formatted': datetime.strptime(data["fecha"], '%Y-%m-%d').strftime('%d/%m/%Y'),
                        'hora': data["hora"],
                        'hora_formatted': data["hora"],
                        'duracion': data.get("duracion", "30"),
                        'duracion_formatted': f"{data.get('duracion', '30')} minutos",
                        'doctor_nombre': dentist.get('Nombre', 'Dr. No especificado') if isinstance(dentist, dict) else (dentist[1] if dentist else 'Dr. No especificado'),
                        'observaciones': data.get("observaciones", ""),
                        'clinica_nombre': os.getenv('CLINIC_NAME', 'Clínica Odontológica COMOD'),
                        'clinica_direccion': os.getenv('CLINIC_ADDRESS', 'Dirección de la Clínica'),
                        'clinica_telefono': os.getenv('CLINIC_PHONE', '+54 11 1234-5678'),
                        'clinica_email': os.getenv('CLINIC_EMAIL', 'info@clinica.com')
                    }
                    
                    # Enviar email de confirmación
                    email_service.send_appointment_confirmation(
                        patient['email'], 
                        patient['Nombre'], 
                        appointment_data
                    )
                    
            except Exception as email_error:
                # No fallar la creación del turno por error de email
                pass
            
            return create_success_response("Turno creado exitosamente", {"appointment_id": appointment_id})
            
        except Exception as e:
            print(f"❌ Error creating appointment: {e}")  # Debug
            return create_error_response(f"Error al crear turno: {str(e)}", 500)

    @app.route("/secretario/turno/<int:appointment_id>")
    @require_secretario
    def get_appointment(appointment_id):
        try:
            appointment = AppointmentService.get_appointment_by_id(appointment_id)
            
            if not appointment:
                return create_error_response("Turno no encontrado", 404)
            
            return jsonify(appointment)
            
        except Exception as e:
            return create_error_response(str(e), 500)

    @app.route("/secretario/turno/<int:appointment_id>", methods=["PUT"])
    @require_secretario
    def update_appointment(appointment_id):
        try:
            data = request.get_json()
            print(f"📋 Updating appointment {appointment_id} with data: {data}")  # Debug
            
            # Validate required fields
            required_fields = ["paciente_id", "odontologo_id", "fecha", "hora"]
            is_valid_fields, missing_fields = validate_required_fields(data, required_fields)
            
            if not is_valid_fields:
                error_response, status_code = handle_validation_error(missing_fields)
                return error_response

            # Validate date and time
            is_valid, error_message = validate_appointment_datetime(data["fecha"], data["hora"])
            if not is_valid:
                return create_error_response(error_message)

            # Update appointment
            rows_affected = AppointmentService.update_appointment(appointment_id, data)
            
            if rows_affected == 0:
                return create_error_response("Turno no encontrado", 404)
            
            print(f"✅ Appointment {appointment_id} updated successfully")  # Debug
            
            return create_success_response("Turno actualizado exitosamente")
            
        except Exception as e:
            print(f"❌ Error updating appointment: {e}")  # Debug
            return create_error_response(f"Error al actualizar turno: {str(e)}", 500)

    @app.route("/secretario/turno/<int:appointment_id>", methods=["DELETE"])
    @require_secretario
    def delete_appointment(appointment_id):
        try:
            rows_affected = AppointmentService.delete_appointment(appointment_id)
            return create_success_response("Turno eliminado exitosamente")
        except Exception as e:
            return create_error_response(str(e), 500)

    @app.route("/api/appointments/<int:appointment_id>", methods=["GET"])
    @require_secretario
    def api_get_appointment(appointment_id):
        """Obtener un turno específico via API"""
        try:
            from utils import format_time_from_timedelta
            
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT dt.id, dt.FechaTurno, dt.HoraTurno, 
                           dt.tipo_consulta, dt.estado, dt.observaciones,
                           p.Nombre AS PacienteNombre, p.DNI AS PacienteDNI,
                           o.Nombre AS OdontologoNombre
                    FROM detalleturno dt
                    JOIN paciente p ON dt.Paciente_id = p.id
                    JOIN odontologo o ON dt.Odontologo_id = o.id
                    WHERE dt.id = %s
                """, (appointment_id,))
                
                appointment = cursor.fetchone()
                
                if not appointment:
                    return create_error_response("Turno no encontrado", 404)
                
                # Formatear hora
                if appointment['HoraTurno']:
                    appointment['HoraTurno'] = format_time_from_timedelta(appointment['HoraTurno'])
                
                return create_success_response(data={"appointment": appointment})
                
        except Exception as e:
            return create_error_response(f"Error al obtener turno: {str(e)}", 500)

    @app.route("/api/appointments/<int:appointment_id>", methods=["PUT"])
    @require_secretario
    def api_update_appointment(appointment_id):
        """Actualizar un turno via API"""
        data = request.get_json()
        
        # Validar campos obligatorios
        required_fields = ['fecha', 'hora']
        is_valid_fields, missing_fields = validate_required_fields(data, required_fields)
        if not is_valid_fields:
            return create_error_response(f"Datos incompletos: {', '.join(missing_fields)}", 400)

        try:
            from datetime import timedelta
            
            with get_db_cursor_with_commit() as cursor:
                # Convertir hora a formato de base de datos
                hora_parts = data['hora'].split(':')
                hora_timedelta = timedelta(
                    hours=int(hora_parts[0]),
                    minutes=int(hora_parts[1])
                )
                
                cursor.execute("""
                    UPDATE detalleturno 
                    SET FechaTurno = %s, HoraTurno = %s, tipo_consulta = %s, estado = %s
                    WHERE id = %s
                """, (
                    data['fecha'],
                    hora_timedelta,
                    data.get('tipo_consulta', ''),
                    data.get('estado', 'programado'),
                    appointment_id
                ))
                
                if cursor.rowcount == 0:
                    return create_error_response("Turno no encontrado", 404)
                
                return create_success_response("Turno actualizado exitosamente")
                
        except Exception as e:
            return create_error_response(f"Error al actualizar turno: {str(e)}", 500)

    @app.route("/api/appointments/<int:appointment_id>", methods=["DELETE"])
    @require_secretario
    def api_delete_appointment(appointment_id):
        """Eliminar un turno via API"""
        try:
            rows_affected = AppointmentService.delete_appointment(appointment_id)
            return create_success_response("Turno eliminado exitosamente")
        except Exception as e:
            return create_error_response(f"Error al eliminar turno: {str(e)}", 500)

    @app.route("/api/appointments/clear-all", methods=["DELETE"])
    @require_secretario
    def api_clear_all_appointments():
        """Eliminar todos los turnos via API"""
        try:
            
            with get_db_cursor_with_commit() as cursor:
                # Obtener el número de turnos antes de eliminarlos
                cursor.execute("SELECT COUNT(*) FROM detalleturno")
                count = cursor.fetchone()[0]
                
                # Eliminar todos los turnos
                cursor.execute("DELETE FROM detalleturno")
                
                return create_success_response(f"Se eliminaron {count} turnos exitosamente")
                
        except Exception as e:
            return create_error_response(f"Error al eliminar turnos: {str(e)}", 500)

    @app.route("/secretario/turno/<int:appointment_id>/estado", methods=["PUT"])
    @require_secretario
    def update_appointment_status(appointment_id):
        try:
            data = request.get_json()
            new_status = data.get("estado")
            
            if not new_status:
                return create_error_response("Estado es obligatorio")

            from db_utils import get_db_cursor_with_commit
            
            with get_db_cursor_with_commit() as cursor:
                cursor.execute(
                    "UPDATE detalleturno SET estado = %s WHERE id = %s",
                    (new_status, appointment_id)
                )
                
                if cursor.rowcount == 0:
                    return create_error_response("Turno no encontrado", 404)
                
                return create_success_response("Estado actualizado exitosamente")
                
        except Exception as e:
            return create_error_response(str(e), 500)

    # API endpoints for clinical history
    @app.route("/secretario/historia-clinica", methods=["POST"])
    @require_secretario
    def create_clinical_history():
        try:
            data = request.get_json()
            
            # Validate required fields
            if not all([data.get("paciente_id"), data.get("fecha")]):
                return create_error_response("Paciente y fecha son obligatorios")

            history_id = ClinicalHistoryService.create_clinical_history(data)
            return create_success_response("Historia clínica creada exitosamente", {"history_id": history_id})
            
        except Exception as e:
            return create_error_response(str(e), 500)

    @app.route("/secretario/historia-clinica/<int:history_id>")
    @require_secretario
    def get_clinical_history(history_id):
        try:
            history = ClinicalHistoryService.get_clinical_history_by_id(history_id)
            
            if not history:
                return create_error_response("Historia clínica no encontrada", 404)
            
            return jsonify(history)
            
        except Exception as e:
            return create_error_response(str(e), 500)

    @app.route("/secretario/historia-clinica/<int:history_id>", methods=["DELETE"])
    @require_secretario
    def delete_clinical_history(history_id):
        try:
            rows_affected = ClinicalHistoryService.delete_clinical_history(history_id)
            return create_success_response("Historia clínica eliminada exitosamente")
        except Exception as e:
            return create_error_response(str(e), 500)

    # API endpoints for dentists
    @app.route("/secretario/odontologos/lista")
    @require_secretario
    def get_dentists_list():
        try:
            dentists = DentistService.get_all_dentists()
            return jsonify(dentists)
        except Exception as e:
            return create_error_response(str(e), 500)

    # ===== RUTAS PARA TURNOS ONLINE =====
    
    @app.route("/turnos-online")
    def turnos_online():
        """Página principal de turnos online"""
        return render_template("turnos_online.html")
    
    @app.route("/api/online/specialties", methods=["GET"])
    def api_online_specialties():
        """Obtener especialidades disponibles para turnos online"""
        try:
            # Obtener especialidades desde la base de datos
            # Como no hay columna especialidad, usar datos por defecto
            specialties = [
                {"name": "Odontología", "icon": "bi-tooth", "description": "Consultas generales y limpiezas"},
                {"name": "Ortodoncia", "icon": "bi-braces", "description": "Tratamientos de ortodoncia"},
                {"name": "Cirugía Oral", "icon": "bi-scissors", "description": "Cirugías y extracciones"}
            ]
            
            return create_success_response(data={"specialties": specialties})
            
        except Exception as e:
            return create_error_response(f"Error al obtener especialidades: {str(e)}", 500)
    
    @app.route("/api/online/doctors", methods=["GET"])
    def api_online_doctors():
        """Obtener doctores disponibles para turnos online"""
        specialty = request.args.get('specialty')
        
        try:
            doctors = DentistService.get_all_dentists()
            
            # Agregar información adicional para la API online
            doctors_with_info = []
            for doctor in doctors:
                doctors_with_info.append({
                    "id": doctor["id"],
                    "name": doctor["Nombre"],
                    "specialty": "Odontología",
                    "icon": "bi-person-badge"
                })
            
            return create_success_response(data={"doctors": doctors_with_info})
            
        except Exception as e:
            return create_error_response(f"Error al obtener doctores: {str(e)}", 500)
    
    @app.route("/api/online/available-times", methods=["GET"])
    def api_online_available_times():
        """Obtener horarios disponibles para un doctor en una fecha específica"""
        doctor_id = request.args.get('doctor_id')
        fecha = request.args.get('fecha')
        
        if not doctor_id or not fecha:
            return create_error_response("doctor_id y fecha son requeridos", 400)
        
        try:
            occupied_times = AppointmentService.get_occupied_times(doctor_id, fecha)
            
            # Generar horarios disponibles (8:00 a 17:00, cada 30 minutos)
            available_slots = []
            start_hour = 8
            end_hour = 17
            
            for hour in range(start_hour, end_hour + 1):
                for minute in [0, 30]:
                    if hour == end_hour and minute > 0:
                        break
                    
                    time_str = f"{hour:02d}:{minute:02d}"
                    is_available = time_str not in occupied_times
                    
                    available_slots.append({
                        "time": time_str,
                        "available": is_available
                    })
            
            return create_success_response(data={"slots": available_slots})
            
        except Exception as e:
            return create_error_response(f"Error al obtener horarios: {str(e)}", 500)
    
    @app.route("/api/online/create-appointment", methods=["POST"])
    def api_online_create_appointment():
        """Crear un turno online"""
        data = request.get_json()
        
        # Validar campos obligatorios
        required_fields = ['doctor_id', 'fecha', 'hora', 'patient_data']
        is_valid_fields, missing_fields = validate_required_fields(data, required_fields)
        if not is_valid_fields:
            return create_error_response(f"Datos incompletos: {', '.join(missing_fields)}", 400)
        
        try:
            from datetime import timedelta
            
            with get_db_cursor_with_commit() as cursor:
                # Crear o buscar paciente
                patient_data = data['patient_data']
                
                # Verificar si el paciente ya existe por email
                cursor.execute("SELECT id FROM paciente WHERE email = %s", (patient_data['email'],))
                existing_patient = cursor.fetchone()
                
                if existing_patient:
                    patient_id = existing_patient[0]
                else:
                    # Crear nuevo paciente
                    cursor.execute("""
                        INSERT INTO paciente (Nombre, DNI, FechaNacimiento, telefono, email, direccion)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        f"{patient_data['nombre']} {patient_data['apellido']}",
                        patient_data.get('dni', '00000000'),
                        patient_data.get('fecha_nacimiento', '1990-01-01'),
                        patient_data['telefono'],
                        patient_data['email'],
                        patient_data.get('direccion', 'No especificada')
                    ))
                    patient_id = cursor.lastrowid
                
                # Validar disponibilidad del turno (fecha, hora y duplicados)
                fecha = data['fecha']
                hora = data['hora']
                
                is_valid, error_message = validate_appointment_availability(
                    cursor, 
                    fecha, 
                    hora, 
                    data['doctor_id'], 
                    patient_id
                )
                if not is_valid:
                    return create_error_response(error_message)
                
                # Convertir hora a formato de base de datos
                hora_parts = hora.split(':')
                hora_timedelta = timedelta(
                    hours=int(hora_parts[0]),
                    minutes=int(hora_parts[1])
                )
                
                cursor.execute("""
                    INSERT INTO detalleturno (Paciente_id, Odontologo_id, FechaTurno, HoraTurno, tipo_consulta, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    patient_id,
                    data['doctor_id'],
                    fecha,
                    hora_timedelta,
                    'Consulta Online',
                    'programado'
                ))
                
                appointment_id = cursor.lastrowid
                
                # Enviar email de confirmación
                try:
                    # Obtener datos del doctor
                    cursor.execute("SELECT Nombre FROM odontologo WHERE id = %s", (data['doctor_id'],))
                    doctor_result = cursor.fetchone()
                    doctor_name = doctor_result[0] if doctor_result else 'Dr. No especificado'
                    
                    # Preparar datos para el email
                    appointment_data = {
                        'fecha': fecha,
                        'fecha_formatted': datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y'),
                        'hora': hora,
                        'hora_formatted': hora,
                        'duracion': '30',
                        'duracion_formatted': '30 minutos',
                        'doctor_nombre': doctor_name,
                        'observaciones': 'Consulta Online',
                        'clinica_nombre': os.getenv('CLINIC_NAME', 'Clínica Odontológica COMOD'),
                        'clinica_direccion': os.getenv('CLINIC_ADDRESS', 'Dirección de la Clínica'),
                        'clinica_telefono': os.getenv('CLINIC_PHONE', '+54 11 1234-5678'),
                        'clinica_email': os.getenv('CLINIC_EMAIL', 'info@clinica.com')
                    }
                    
                    # Enviar email de confirmación
                    email_service.send_appointment_confirmation(
                        patient_data['email'], 
                        f"{patient_data['nombre']} {patient_data['apellido']}", 
                        appointment_data
                    )
                        
                except Exception as email_error:
                    # No fallar la creación del turno por error de email
                    pass
                
                return create_success_response(
                    "Turno creado exitosamente",
                    {"appointment_id": appointment_id}
                )
                
        except Exception as e:
            return create_error_response(f"Error al crear turno: {str(e)}", 500)

        # --- RUTAS MOVIDAS AQUÍ ---
    @app.route('/test-duplicate-appointments')
    def test_duplicate_appointments():
        """Ruta para probar la restricción de turnos duplicados"""
        return render_template('test_duplicate_appointments.html')

    @app.route('/test-notifications')
    def test_notifications():
        """Ruta para probar el sistema de notificaciones"""
        return render_template('test_notifications.html')

    # API para obtener datos del paciente
    @app.route("/api/paciente/<int:patient_id>")
    @require_odontologo # O @require_secretario si ambos pueden acceder
    def api_paciente_details(patient_id):
        """API para obtener detalles completos de un paciente"""
        try:
            patient = PatientService.get_patient_by_id(patient_id)
            if not patient:
                # Usar has_request_context por si acaso
                from flask import has_request_context
                if has_request_context():
                     return create_error_response("Paciente no encontrado", 404)
                else:
                     print(f"ERROR CRITICO: api_paciente_details ejecutado sin contexto buscando ID {patient_id}")
                     raise RuntimeError("Error interno: Contexto de solicitud no encontrado.")


            # Obtener estadísticas del paciente
            histories = ClinicalHistoryService.get_clinical_histories_by_patient(patient_id)
            histories_count = len(histories) if histories else 0

            odontogramas = OdontogramaService.get_odontogramas_by_patient(patient_id)
            odontogramas_count = len(odontogramas) if odontogramas else 0

            turnos_count = AppointmentService.get_appointments_count_by_patient(patient_id)

            # Agregar estadísticas al objeto paciente
            patient_data = dict(patient) # Convertir a dict si no lo es
            patient_data['historias_count'] = histories_count
            patient_data['odontogramas_count'] = odontogramas_count # Usar el conteo real
            patient_data['turnos_count'] = turnos_count

            return create_success_response("Datos del paciente obtenidos", {"patient": patient_data})

        except Exception as e:
             print(f"Error en api_paciente_details: {e}")
             # Usar has_request_context por si acaso
             from flask import has_request_context
             if has_request_context():
                 return create_error_response(f"Error al obtener datos del paciente: {str(e)}", 500)
             else:
                  print(f"ERROR CRITICO: api_paciente_details ejecutado sin contexto. Error: {e}")
                  raise e # Relanzar error si no hay contexto

    # --- FIN RUTAS MOVIDAS ---

    return app # Esta debe ser la ÚLTIMA línea de create_app()

if __name__ == "__main__":
        app = create_app() # <-- LLAMAR A create_app() AQUÍ DENTRO
        port = int(os.getenv("PORT", "5000"))
        # Ejecutar la app (asegúrate que 'app' sea la variable correcta)
        app.run(host="0.0.0.0", port=port, debug=True)  



