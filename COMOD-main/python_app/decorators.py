"""
Decoradores para la aplicación
"""
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify


def require_role(required_role):
    """
    Decorador para verificar que el usuario tenga el rol requerido
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("role") != required_role:
                if f.__name__.startswith('api_') or 'jsonify' in f.__code__.co_names:
                    # Es una API endpoint, devolver JSON
                    return jsonify({"success": False, "message": "Acceso no autorizado"}), 403
                else:
                    # Es una página web, redirigir
                    flash("Acceso no autorizado.", "error")
                    return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_secretario(f):
    """
    Decorador específico para requerir rol de secretario
    """
    return require_role("secretario")(f)


def require_odontologo(f):
    """
    Decorador específico para requerir rol de odontólogo
    """
    return require_role("odontologo")(f)
