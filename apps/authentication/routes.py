# -*- encoding: utf-8 -*-
import requests
from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from flask_dance.contrib.github import github

from apps import  login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users

#from apps.authentication.util import verify_pass

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route("/github")
def login_github():
    """ Github login """
    if not github.authorized:
        return redirect(url_for("github.login"))

    res = github.get("/user")
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        # read form data
        email  = request.form['email']
        password = request.form['password']

        url = "http://ljragusa.com.ar:3001/usuario/login"
        payload='email='+email+'&password='+password
        headers = {}
        respuesta= requests.request("POST", url, headers=headers, data=payload)

        print(respuesta.text)

        if 1==2:    #aca si es incorrecto
            return render_template( 'accounts/login.html',
                                    msg='Usuario o Email no encontrado (respetar Mayúsculas y Minúsculas)',
                                    form=login_form)
        #    <script>
        #        // Obtén el token del usuario desde la respuesta de la API y guárdalo en el LocalStorage
        #        var token = 'token_del_usuario'; // Aquí debes obtener el token de la respuesta de la API
        #        localStorage.setItem('userToken', token);
        #    </script>

        # esto tengo que usar en el HTML para meter el token en el navegador


        login_user(user)
        return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Usuario o contraseña incorrectos',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/prueba', methods=['GET', 'POST'])
def prueba():
    response = requests.get('http://ljragusa.com.ar:3001/usuario')

    if response.status_code == 200:
        data = response.json()
        ##mensaje = data["message"]
        return render_template('accounts/prueba.html',data=data)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Nombre de usuario ya utilizado',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email ya utilizado',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

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
