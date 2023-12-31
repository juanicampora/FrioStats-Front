# -*- encoding: utf-8 -*-

from flask import Blueprint, abort
from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, render_template

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
                return abort(403)  # Redirige a una página de acceso no autorizado si el rol no coincide
            return func(*args, **kwargs)
        return wrapper
    return decorator

def confirm_mail_required():         # Creo un decorador para verificar si confirmo su mail
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.confirmado:
                return render_template( 'home/faltaconfirmar.html') # Redirige a la pagina de falta confirmar
            return func(*args, **kwargs)
        return wrapper
    return decorator