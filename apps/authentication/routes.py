# -*- encoding: utf-8 -*-
import requests
from flask import render_template, redirect, request, url_for
from flask_login import (current_user,login_user,logout_user,login_required)

from apps import  login_manager
from apps.authentication import blueprint, role_required
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import User


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        # read form data
        email  = request.form['email']
        password = request.form['password']

        url = "http://ljragusa.com.ar:3001/users/login"
        payload={
            "email": email,
            "password": password
        }
        headers = {}
        respuesta = requests.request("POST", url, headers=headers, data=payload)
        
        if respuesta.status_code == 404:        
            return render_template( 'accounts/login.html',
                                    msg='Email o contraseña incorrectos',
                                    form=login_form)
        elif respuesta.status_code == 200:
            respuestajson=respuesta.json()
            usuario= User(respuestajson["user"]["id"],respuestajson["user"]["email"],respuestajson["user"]["nombre"],respuestajson["user"]["Rol"]["descripcion"])
            if User.find_by_id(usuario.id) is None:
                usuario.save()
            login_user(usuario)
            token=respuestajson["token"]
            return redirect(url_for('authentication_blueprint.store_token',token=token))
        else:
            print("El error obtenido es distinto a 404 y es:")
            print(respuesta.status_code)   
            return redirect(url_for('authentication_blueprint.internal_error'))

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))
    
@blueprint.route('/store_token/<token>')
def store_token(token):
    return '''
        <script>
            var token = '{}';
            localStorage.setItem('token', token);
            // Redirigir a la página de destino
            window.location.href = '/index';
        </script>
    '''.format(token)

@blueprint.route('/register', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Nombre de usuario ya utilizado',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email ya utilizado',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = User(**request.form)

        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg='Usuario creado correctamente.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login')) 

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
