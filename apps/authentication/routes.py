# -*- encoding: utf-8 -*-
import requests
from flask import render_template, redirect, request, url_for, abort, make_response
from flask_login import (current_user,login_user,logout_user,login_required)

from apps import  login_manager
from apps.authentication import blueprint, role_required
from apps.authentication.forms import LoginForm, CreateAccountForm, RolesForm
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
        try:    
            respuesta = requests.request("POST", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)


        if respuesta.status_code == 401:        
            return render_template( 'accounts/login.html',
                                    msg='Email o contraseña incorrectos',
                                    form=login_form)
        elif respuesta.status_code == 200:
            respuestajson=respuesta.json()
            usuario= User(respuestajson["user"]["id"],respuestajson["user"]["email"],respuestajson["user"]["nombre"],respuestajson["user"]["apellido"],respuestajson["user"]["Rol"]["descripcion"],respuestajson["token"])
            if User.find_by_id(usuario.id) is None:
                usuario.save()
            login_user(usuario)
            token=respuestajson["token"]
            response = make_response(redirect('/index'))    
            response.set_cookie('token', token)             #guardar en una cookie el token
            return response
        elif respuesta.status_code == 403:
            return render_template( 'accounts/login.html',
                                    msg='No confirmó su mail, por favor revise su casilla de correo',
                                    form=login_form)
        else:
            print("El error obtenido es distinto a 200,401,403 y es:")
            print(respuesta.status_code)   
            return abort(500)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))
    

@blueprint.route('/register', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['name']
        apellido = request.form['surname']
        if request.form.get('recibirEmail') == None: recibirEmail = 'false' 
        else: recibirEmail = 'true'
        token = request.cookies.get('token')
        url = "http://ljragusa.com.ar:3001/users/register"
        payload={
                "email": email,
                "password": password,
                "nombre": nombre,
                "apellido": apellido,
                "recibeNotiMail": recibirEmail
            }
        headers = {
        'user-token': token
        }

        try: 
            response = requests.request("POST", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        
        print(response.text)
        print(response.status_code)

        if response.status_code == 201:
            return render_template('accounts/register.html', segment='register',
                                            msg='Usuario creado correctamente.',
                                            success=True,
                                            form=create_account_form)
        elif response.status_code == 400:
            return render_template('accounts/register.html', segment='register',
                                msg=response.json()['message'],
                                success=False,
                                form=create_account_form)
    else:
        return render_template('accounts/register.html', segment='register', form=create_account_form)

@blueprint.route('/roles', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def roles(exito=None):
    print(exito)
    if exito=='si':
        return render_template('accounts/roles.html', segment='roles',
                            msg='Rol asignado correctamente.',
                            success=True)
    elif exito=='no':
        return render_template('accounts/roles.html', segment='roles',
                            msg='Hubo un error intente nuevamente.',
                            success=False)
    else:
        return render_template('accounts/roles.html', segment='roles')

@blueprint.route('/roles/email_conocido', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def roles_email_conocido():
    if (request.method == 'GET'):
        data_roles=getRoles()
        return render_template('accounts/roles_email_conocido.html', segment='roles', data_roles=data_roles)
    elif (request.method == 'POST'):
        
        email = request.form['email']
        #PEDIR A LUCHO UNA API PARA PONER ACA QUE VERIFIQUE QUE EL EMAIL EXISTE. si existe que mande 
        idUsuario=email
        if idUsuario==None:
            data_roles=getRoles()
            return render_template('accounts/roles.html', segment='roles', data_roles=data_roles,msg='El email ingresado no existe en el sistema')
        else:
            idRol = request.form['rolSeleccionado']
            respuesta= asignarRol(idUsuario,idRol)
            print(respuesta.text)   #BORRAR
            redirect(url_for('authentication_blueprint.roles',exito='si'))
            



@blueprint.route('/roles/lista', methods=['GET'])
@login_required
@role_required('Admin')
def roles_lista():
    return True

@blueprint.route('/roles/lista/seleccionado', methods=['GET'])
@login_required
@role_required('Admin')
def roles_lista_seleccionado():
    return True
    

@blueprint.route('/mailconfirmation')
def mailconfirmation():
    return render_template('accounts/mail_confirmation.html')


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


# Funciones utilizadas varias veces
def getRoles():
    url = "http://ljragusa.com.ar:3001/roles/getRoles"
    payload={}
    headers = {
    'user-token': request.cookies.get('token')
    }
    try:
        roles = requests.request("GET", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)    
    data_roles = roles.json()
    return data_roles

def asignarRol(idUsuario,idRol):
    url = "http://ljragusa.com.ar:3001/users/"+idUsuario
    payload={
            "idUsuario": idUsuario,
            "idRol": idRol,
        }
    headers = {
    'user-token': request.cookies.get('token')
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
    return response