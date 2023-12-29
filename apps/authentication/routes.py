# -*- encoding: utf-8 -*-
import requests
from flask import render_template, redirect, request, url_for, abort, make_response
from flask_login import (current_user,login_user,logout_user,login_required)

from apps import  login_manager
from apps.authentication import blueprint, role_required, confirm_mail_required
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
            usuario= User(respuestajson["user"]["id"],respuestajson["user"]["email"],respuestajson["user"]["nombre"],respuestajson["user"]["apellido"],respuestajson["user"]["Rol"]["descripcion"],respuestajson["token"],respuestajson["user"]["emailConfirmado"])
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
@confirm_mail_required()
@role_required('Admin')
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['name']
        apellido = request.form['surname']
        token = request.cookies.get('token')
        url = "http://ljragusa.com.ar:3001/users/"
        payload={
                "email": email,
                "password": password,
                "nombre": nombre,
                "apellido": apellido,
            }
        headers = { 'user-token': token }

        try: 
            response = requests.request("POST", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)

        if response.status_code == 201:
            return render_template('accounts/register.html', segment='register',
                                            msg='Usuario creado correctamente.',
                                            success=True,
                                            form=create_account_form)
        if response.status_code == 403:
            respuesta=response.json()
            #recorrer el arreglo errors y guardar en el arreglo mensaje los 'msg' de cada error
            mensaje=[]
            for error in respuesta['errors']:
                mensaje.append(error['msg'])
            return render_template('accounts/register.html', segment='register',
                                msg=mensaje,
                                success=False,
                                form=create_account_form)
        else:
            return render_template('accounts/register.html', segment='register',
                                msg=response.json(),
                                success=False,
                                form=create_account_form)
    else:
        return render_template('accounts/register.html', segment='register', form=create_account_form)

@blueprint.route('/roles', methods=['GET', 'POST'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def roles(exito=None):
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
@confirm_mail_required()
@role_required('Admin')
def roles_email_conocido(): 
    email_empleado = request.args.get('email_empleado')

    if (request.method == 'GET'):
        data_roles=getRoles()   
        if email_empleado != None:
            return render_template('accounts/roles_email_conocido.html', segment='roles', data_roles=data_roles,email_empleado=email_empleado)        
        return render_template('accounts/roles_email_conocido.html', segment='roles', data_roles=data_roles)
        
    elif (request.method == 'POST'):
        
        email = request.form['email']
        url = "http://ljragusa.com.ar:3001/users/checkEmail"
        payload={
            "email": email
        }
        headers = { 'user-token': request.cookies.get('token') }
        try:
            respuesta = requests.request("POST", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        if respuesta.status_code == 200:
            idUsuario=email
            idRol = request.form['rolSeleccionado']
            asignarRol(idUsuario,idRol)
            redirect(url_for('authentication_blueprint.roles',exito='si'))
        else:
            data_roles=getRoles()  
            return render_template('accounts/roles_email_conocido.html', segment='roles', data_roles=data_roles, msg=respuesta.json()['message'])

@blueprint.route('/roles/lista', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def roles_lista():
    url = "http://ljragusa.com.ar:3001/users/getEmployees"
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    empleados=respuesta.json()
    return render_template('accounts/roles_lista.html', segment='roles', empleados=empleados)

@blueprint.route('/roles/lista/<string:email_empleado>', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def roles_lista_seleccionado(email_empleado):
    return redirect(url_for('authentication_blueprint.roles_email_conocido',email_empleado=email_empleado))

@blueprint.route('/mailconfirmation')
def mailconfirmation():
    return render_template('accounts/mail_confirmation.html')

@blueprint.route('/asignar_sucursales', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def asignar_sucursales(): 
    url = "http://ljragusa.com.ar:3001/users/getEmployees"
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    empleados=respuesta.json()
    return render_template('accounts/sucursales_lista_emails.html', segment='asignacionsucursales', empleados=empleados)
    
@blueprint.route('/asignar_sucursales/<string:email_empleado>', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def asignar_sucursales_email_seleccionado(email_empleado): 
    if (request.method == 'GET'):
        data_sucursales=getSucursales()     
        return render_template('accounts/sucursales_email_seleccionado.html', segment='asignacionsucursales', email_empleado=email_empleado, data_sucursales=data_sucursales)
    elif (request.method == 'POST'):
        idUsuario=email
        idRol = request.form['rolSeleccionado']
        asignarRol(idUsuario,idRol)


@blueprint.route('/confirmEmail/<string:token>', methods=['GET'])
def confirmEmail(token):
    url = "http://ljragusa.com.ar:3001/users/confirmEmail/"+token
    payload={}
    headers = {}
    try:
        respuesta = requests.request("GET", url, headers=headers, data=payload)
        print(respuesta)
    except requests.exceptions.RequestException as e:
        print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
        return abort(500)
    if respuesta.status_code == 200:
        print(respuesta)
        return render_template('accounts/mail_confirmed',email=respuesta.json()['email'])
    else:   
        return errorGenerico(respuesta)

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

def errorGenerico(respuesta):
    mensaje=respuesta.json()['message']
    return render_template('home/page-error-generico.html',mensaje=mensaje)
    
# Funciones utilizadas varias veces
def verifSesión(respuesta):
    if respuesta.status_code==403:
        if respuesta.json()['message']=='Sesion expirada':
            logout_user()
            return abort(403)

def getRoles():
    url = "http://ljragusa.com.ar:3001/roles/"
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
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
    headers = { 'user-token': request.cookies.get('token') }
    try:
        respuesta = requests.request("POST", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
    verifSesión(respuesta)
    return respuesta

def getSucursales():
    url = "http://ljragusa.com.ar:3001/sucursales/"
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    try:
        sucursales = requests.request("GET", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)    
    data_sucursales = sucursales.json()
    return data_sucursales