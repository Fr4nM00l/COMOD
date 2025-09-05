import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
from datetime import datetime, date
# from flask_moment import Moment
import json

from db import get_db_connection


load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    # moment = Moment(app)
    # moment.locale('es')
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SECRET_KEY"] = secret_key
    app.config["SESSION_PERMANENT"] = False

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

            table_name = "odontologo" if selected_role == "odontologo" else "secretario"

            try:
                connection = get_db_connection()
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    f"""
                    SELECT id, Nombre, Usuario, Contraseña
                    FROM {table_name}
                    WHERE Usuario = %s
                    LIMIT 1
                    """,
                    (username,),
                )
                user = cursor.fetchone()
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    connection.close()
                except Exception:
                    pass

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
    def odontologo_dashboard():
        if session.get("role") != "odontologo":
            flash("Acceso no autorizado.", "error")
            return redirect(url_for("login"))

        odontologo_id = session.get("user_id")

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT dt.FechaTurno, dt.HoraTurno, p.Nombre AS Paciente
                FROM detalleturno dt
                INNER JOIN paciente p ON p.id = dt.Paciente_id
                WHERE dt.Odontologo_id = %s
                  AND TIMESTAMP(dt.FechaTurno, dt.HoraTurno) >= NOW()
                ORDER BY dt.FechaTurno ASC, dt.HoraTurno ASC
                LIMIT 10
                """,
                (odontologo_id,),
            )
            upcoming_appointments = cursor.fetchall()
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

        return render_template(
            "odontologo_dashboard.html",
            nombre=session.get("nombre"),
            upcoming_appointments=upcoming_appointments,
        )

    @app.route("/secretario")
    def secretario_dashboard():
        if session.get("role") != "secretario":
            flash("Acceso no autorizado.", "error")
            return redirect(url_for("login"))

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT dt.FechaTurno, dt.HoraTurno, p.Nombre AS Paciente, o.Nombre AS Odontologo
                FROM detalleturno dt
                INNER JOIN paciente p ON p.id = dt.Paciente_id
                INNER JOIN odontologo o ON o.id = dt.Odontologo_id
                WHERE TIMESTAMP(dt.FechaTurno, dt.HoraTurno) >= NOW()
                ORDER BY dt.FechaTurno ASC, dt.HoraTurno ASC
                LIMIT 10
                """
            )
            next_appointments = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM paciente")
            patient_count = (cursor.fetchone() or {}).get("total", 0)

            cursor.execute("SELECT COUNT(*) AS total FROM odontologo")
            dentist_count = (cursor.fetchone() or {}).get("total", 0)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

        return render_template(
            "secretario_dashboard.html",
            nombre=session.get("nombre"),
            next_appointments=next_appointments,
            patient_count=patient_count,
            dentist_count=dentist_count,
        )

    # Secretary section routes
    @app.route("/secretario/pacientes")
    def secretario_pacientes():
        if session.get("role") != "secretario":
            return "Acceso no autorizado", 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM paciente ORDER BY Nombre")
            patients = cursor.fetchall()
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

        return render_template("sections/pacientes_section.html", patients=patients)

    @app.route("/secretario/turnos")
    def secretario_turnos():
        if session.get("role") != "secretario":
            return "Acceso no autorizado", 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
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
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

        return render_template("sections/turnos_section.html", 
                            appointments=appointments, 
                            today=date.today().isoformat())

    @app.route("/secretario/historias")
    def secretario_historias():
        if session.get("role") != "secretario":
            return "Acceso no autorizado", 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Get clinical histories
            cursor.execute(
                """
                SELECT hc.*, p.Nombre AS Paciente, p.DNI AS paciente_dni
                FROM historiaclinica hc
                INNER JOIN paciente p ON p.id = hc.Paciente_id
                ORDER BY hc.Fecha DESC
                """
            )
            clinical_histories = cursor.fetchall()

            # Get patients without clinical history
            cursor.execute(
                """
                SELECT p.* FROM paciente p
                LEFT JOIN historiaclinica hc ON p.id = hc.Paciente_id
                WHERE hc.id IS NULL
                ORDER BY p.Nombre
                """
            )
            patients_without_history = cursor.fetchall()
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

        return render_template("sections/historias_section.html",
                            clinical_histories=clinical_histories,
                            patients_without_history=patients_without_history)

    @app.route("/secretario/odontogramas")
    def secretario_odontogramas():
        if session.get("role") != "secretario":
            return "Acceso no autorizado", 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Get odontogramas with patient info
            cursor.execute(
                """
                SELECT o.*, p.Nombre AS Paciente, p.DNI AS paciente_dni
                FROM odontograma o
                INNER JOIN historiaclinica hc ON o.HistoriaClinica_id = hc.id
                INNER JOIN paciente p ON hc.Paciente_id = p.id
                ORDER BY o.Fecha DESC
                """
            )
            odontogramas = cursor.fetchall()

            # Get patients without odontograma
            cursor.execute(
                """
                SELECT p.* FROM paciente p
                LEFT JOIN historiaclinica hc ON p.id = hc.Paciente_id
                LEFT JOIN odontograma o ON hc.id = o.HistoriaClinica_id
                WHERE o.id IS NULL
                ORDER BY p.Nombre
                """
            )
            patients_without_odontograma = cursor.fetchall()

            # Get procedures catalog
            cursor.execute("SELECT * FROM procedimientos WHERE Activo = 1 ORDER BY NombreProcedimiento")
            procedimientos = cursor.fetchall()
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

        return render_template("sections/odontogramas_section.html",
                            odontogramas=odontogramas,
                            patients_without_odontograma=patients_without_odontograma,
                            procedimientos=procedimientos)

    # API endpoints for patients
    @app.route("/secretario/paciente", methods=["POST"])
    def create_patient():
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get("nombre") or not data.get("dni"):
                return jsonify({"success": False, "message": "Nombre y DNI son obligatorios"})

            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Check if DNI already exists
            cursor.execute("SELECT id FROM paciente WHERE DNI = %s", (data["dni"],))
            if cursor.fetchone():
                return jsonify({"success": False, "message": "Ya existe un paciente con ese DNI"})

            # Insert new patient
            cursor.execute(
                """
                INSERT INTO paciente (Nombre, FechaNacimiento, DNI) 
                VALUES (%s, %s, %s)
                """,
                (data["nombre"], data.get("fecha_nacimiento"), data["dni"])
            )
            connection.commit()
            
            return jsonify({"success": True, "message": "Paciente creado exitosamente"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    @app.route("/secretario/paciente/<int:patient_id>")
    def get_patient(patient_id):
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM paciente WHERE id = %s", (patient_id,))
            patient = cursor.fetchone()
            
            if not patient:
                return jsonify({"success": False, "message": "Paciente no encontrado"}), 404
            
            return jsonify(patient)
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    @app.route("/secretario/paciente/<int:patient_id>", methods=["DELETE"])
    def delete_patient(patient_id):
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM paciente WHERE id = %s", (patient_id,))
            connection.commit()
            
            return jsonify({"success": True, "message": "Paciente eliminado exitosamente"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    @app.route("/secretario/pacientes/lista")
    def get_patients_list():
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, Nombre, DNI FROM paciente ORDER BY Nombre")
            patients = cursor.fetchall()
            
            return jsonify(patients)
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    # API endpoints for appointments
    @app.route("/secretario/turno", methods=["POST"])
    def create_appointment():
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            data = request.get_json()
            
            # Validate required fields
            if not all([data.get("paciente_id"), data.get("odontologo_id"), data.get("fecha"), data.get("hora")]):
                return jsonify({"success": False, "message": "Todos los campos son obligatorios"})

            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Insert new appointment
            cursor.execute(
                """
                INSERT INTO detalleturno (Odontologo_id, Paciente_id, FechaTurno, HoraTurno) 
                VALUES (%s, %s, %s, %s)
                """,
                (data["odontologo_id"], data["paciente_id"], data["fecha"], data["hora"])
            )
            connection.commit()
            
            return jsonify({"success": True, "message": "Turno creado exitosamente"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    @app.route("/secretario/turno/<int:appointment_id>")
    def get_appointment(appointment_id):
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM detalleturno WHERE id = %s", (appointment_id,))
            appointment = cursor.fetchone()
            
            if not appointment:
                return jsonify({"success": False, "message": "Turno no encontrado"}), 404
            
            return jsonify(appointment)
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    @app.route("/secretario/turno/<int:appointment_id>", methods=["DELETE"])
    def delete_appointment(appointment_id):
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM detalleturno WHERE id = %s", (appointment_id,))
            connection.commit()
            
            return jsonify({"success": True, "message": "Turno eliminado exitosamente"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    @app.route("/secretario/turno/<int:appointment_id>/estado", methods=["PUT"])
    def update_appointment_status(appointment_id):
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            data = request.get_json()
            new_status = data.get("estado")
            
            if not new_status:
                return jsonify({"success": False, "message": "Estado es obligatorio"})

            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Update appointment status (you might need to add an estado column to detalleturno)
            cursor.execute(
                "UPDATE detalleturno SET estado = %s WHERE id = %s",
                (new_status, appointment_id)
            )
            connection.commit()
            
            return jsonify({"success": True, "message": "Estado actualizado exitosamente"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    # API endpoints for clinical history
    @app.route("/secretario/historia-clinica", methods=["POST"])
    def create_clinical_history():
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            data = request.get_json()
            
            # Validate required fields
            if not all([data.get("paciente_id"), data.get("fecha")]):
                return jsonify({"success": False, "message": "Paciente y fecha son obligatorios"})

            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Insert new clinical history
            cursor.execute(
                """
                INSERT INTO historiaclinica 
                (Fecha, Paciente_id, ObraSocial, NumAfiliado, Alergias, Enfermedades, 
                 Fuma, Drogas, Medicamentos, NivelDeDolor, Calmante, GolpeEnDientes, FechaGolpe) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (data["fecha"], data["paciente_id"], data.get("obra_social"), 
                 data.get("num_afiliado"), data.get("alergias"), data.get("enfermedades"),
                 data.get("fuma", False), data.get("drogas"), data.get("medicamentos"),
                 data.get("nivel_dolor"), data.get("calmante"), data.get("golpe_en_dientes", False),
                 data.get("fecha_golpe"))
            )
            connection.commit()
            
            return jsonify({"success": True, "message": "Historia clínica creada exitosamente"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    @app.route("/secretario/historia-clinica/<int:history_id>")
    def get_clinical_history(history_id):
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM historiaclinica WHERE id = %s", (history_id,))
            history = cursor.fetchone()
            
            if not history:
                return jsonify({"success": False, "message": "Historia clínica no encontrada"}), 404
            
            return jsonify(history)
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    @app.route("/secretario/historia-clinica/<int:history_id>", methods=["DELETE"])
    def delete_clinical_history(history_id):
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM historiaclinica WHERE id = %s", (history_id,))
            connection.commit()
            
            return jsonify({"success": True, "message": "Historia clínica eliminada exitosamente"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    # API endpoints for dentists
    @app.route("/secretario/odontologos/lista")
    def get_dentists_list():
        if session.get("role") != "secretario":
            return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, Nombre FROM odontologo ORDER BY Nombre")
            dentists = cursor.fetchall()
            
            return jsonify(dentists)
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)


