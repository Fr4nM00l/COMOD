import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

from db import get_db_connection


load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

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

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)


