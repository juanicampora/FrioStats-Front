# -*- encoding: utf-8 -*-

from flask import Blueprint
from functools import wraps
from flask_login import current_user
from flask import redirect, url_for

blueprint = Blueprint(
    'authentication_blueprint',
    __name__,
    url_prefix=''
)

def role_required(rol):         # Creo un decorador para verificar el rol del usuario
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('authentication_blueprint.login'))  # Redirige al login si el usuario no está autenticado
            if current_user.rol != rol:
                return redirect(url_for('authentication_blueprint.internal_error'))  # Redirige a una página de acceso no autorizado si el rol no coincide
            return func(*args, **kwargs)
        return wrapper
    return decorator
