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
        
        url = "http://186.13.28.124:3001/users/login"
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
            else:
                usuarioBorrar= User.find_by_id(usuario.id)
                usuarioBorrar.delete_from_db()
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
            print("El error obtenido es distinto a 200,401,403 y es:"+ str(respuesta.status_code))
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
        url = "http://186.13.28.124:3001/users/"
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
            mensajes=[]
            mensajes.append(response.json()['message'])
            return render_template('accounts/register.html', segment='register',
                                msg=mensajes,
                                success=False,
                                form=create_account_form)
    else:
        return render_template('accounts/register.html', segment='register', form=create_account_form)

@blueprint.route('/roles', methods=['GET', 'POST'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def roles():
    return render_template('accounts/roles.html', segment='roles')
        

@blueprint.route('/roles/email_conocido', methods=['GET', 'POST'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def roles_email_conocido(): 
    email_empleado = request.args.get('email_empleado')
    rol_actual = request.args.get('rol_actual')
    if (request.method == 'GET'):
        data_roles=getRoles()   
        if email_empleado != None:
            return render_template('accounts/roles_email_conocido.html', segment='roles', data_roles=data_roles,email_empleado=email_empleado,rol_actual=rol_actual)        
        return render_template('accounts/roles_email_conocido.html', segment='roles', data_roles=data_roles)
        
    elif (request.method == 'POST'):        
        email = request.form['email']
        url = "http://186.13.28.124:3001/users/checkEmail"
        payload={
            "email": email
        }
        headers = { 'user-token': request.cookies.get('token') }
        try:
            respuesta = requests.request("GET", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        if respuesta.status_code == 200:
            idUsuario=respuesta.json()['elemt']['id']
            idRol = request.form['rolSeleccionado']
            respuestaActualizacion=asignarRol(idUsuario,idRol)
            mensaje=respuestaActualizacion.json()['message']
            return render_template('accounts/roles.html', segment='roles', msg=mensaje, success=True)
        else:
            data_roles=getRoles()  
            return render_template('accounts/roles_email_conocido.html', segment='roles', data_roles=data_roles, msg=respuesta.json()['message'])

@blueprint.route('/roles/lista', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def roles_lista():
    url = "http://186.13.28.124:3001/users/getEmployees"
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    empleados=respuesta.json()['empleados']
    return render_template('accounts/roles_lista.html', segment='roles', empleados=empleados)

@blueprint.route('/roles/lista/<string:email_empleado>/<string:rol_actual>', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def roles_lista_seleccionado(email_empleado,rol_actual):
    return redirect(url_for('authentication_blueprint.roles_email_conocido',email_empleado=email_empleado,rol_actual=rol_actual))

@blueprint.route('/baja', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def baja_usuario():
    url = "http://186.13.28.124:3001/users/getEmployees"
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    empleados=respuesta.json()
    return render_template('accounts/baja.html', segment='baja', empleados=empleados['empleados'], empleadosBaja=empleados['empleadosBaja'])

@blueprint.route('/baja/<string:idUsuario>', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def baja_usuario_accion(idUsuario):
    url = "http://186.13.28.124:3001/users/"+idUsuario
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    try:
        respuesta = requests.request("DELETE", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
        return abort(500)
    if respuesta.status_code == 200:
        url = "http://186.13.28.124:3001/users/getEmployees"
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        respuesta2 = requests.request("GET", url, headers=headers, data=payload)
        empleados=respuesta2.json()
        return render_template('accounts/baja.html', segment='baja', empleados=empleados['empleados'], empleadosBaja=empleados['empleadosBaja'], msg=respuesta.json()['message'], success=True)
    else:
        print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
        return abort(500)
    
@blueprint.route('/alta/<string:idUsuario>', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def alta_usuario_accion(idUsuario):
    url = "http://186.13.28.124:3001/users/restore/"+idUsuario
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    try:
        respuesta = requests.request("PATCH", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
        return abort(500)
    if respuesta.status_code == 200:
        url = "http://186.13.28.124:3001/users/getEmployees"
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        respuesta2 = requests.request("GET", url, headers=headers, data=payload)
        empleados=respuesta2.json()
        return render_template('accounts/baja.html', segment='baja', empleados=empleados['empleados'], empleadosBaja=empleados['empleadosBaja'], msg=respuesta.json()['message'], success=True)
    else:
        print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
        return abort(500)

@blueprint.route('/mailconfirmation')
def mailconfirmation():
    return render_template('accounts/mail_confirmation.html')

@blueprint.route('/asignar_sucursales', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def asignar_sucursales(): 
    url = "http://186.13.28.124:3001/users/getEmployees"
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    empleados=respuesta.json()
    return render_template('accounts/sucursales_lista_emails.html', segment='asignacionsucursales', empleados=empleados['empleados'])
    
@blueprint.route('/asignar_sucursales/<string:email_empleado>', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def asignar_sucursales_email_seleccionado(email_empleado): 
    if (request.method == 'GET'):
        url = "http://186.13.28.124:3001/sucursales/email/"+email_empleado
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        try:
            sucursales = requests.request("GET", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
                print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
                return abort(500)    
        data_sucursales = sucursales.json()
        return render_template('accounts/sucursales_email_seleccionado.html', segment='asignacionsucursales', email_empleado=email_empleado, data_sucursales=data_sucursales)

@blueprint.route('/actualizar_sucursal/<string:email_empleado>/<int:sucursalId>/<string:estado>', methods=['GET'])
@login_required
@confirm_mail_required()
@role_required('Admin')
def actualizar_sucursal(email_empleado,sucursalId,estado):
    url = "http://186.13.28.124:3001/sucursales/"
    payload={
        "email": email_empleado,
        "idSucursal": sucursalId,
        "asignada": estado
    }
    headers = { 'user-token': request.cookies.get('token') }
    try:
        respuesta = requests.request("PUT", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
    if respuesta.status_code == 200:
        return redirect(url_for('authentication_blueprint.asignar_sucursales_email_seleccionado',email_empleado=email_empleado))
    

@blueprint.route('/confirmEmail/<string:token>', methods=['GET'])
def confirmEmail(token):
    url = "http://186.13.28.124:3001/users/confirmEmail/"+token
    payload={}
    headers = {}
    try:
        respuesta = requests.request("GET", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
        return abort(500)
    if respuesta.status_code == 200:
        return render_template('accounts/mail_confirmed.html',mensaje=respuesta.json()['message'])
    elif respuesta.status_code == 409:
        return render_template('accounts/mail_confirmed.html',mensaje=respuesta.json()['message'])
    else:   
         return abort(500)

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
    return render_template('home/page-403.html',mensaje=error.description), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500

    
# Funciones utilizadas varias veces
def verifSesion(respuesta):
    if respuesta.status_code==200:
        return True
    elif respuesta.status_code==403:
        if respuesta.json()['msg']=='Sesion expirada':
            logout_user()            
            return abort(403,respuesta.json()['msg'])
        else:
            logout_user()
            return abort(403)
    else:
        return abort(500)

def getRoles():
    url = "http://186.13.28.124:3001/roles/"
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
    idUsuarioStr=str(idUsuario)
    url = "http://186.13.28.124:3001/users/"+idUsuarioStr
    payload={
            "idRol": idRol,
        }
    headers = { 'user-token': request.cookies.get('token') }
    try:
        respuesta = requests.request("PATCH", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
    verifSesion(respuesta)
    return respuesta

def getSucursales():
    url = "http://186.13.28.124:3001/sucursales/"
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    try:
        sucursales = requests.request("GET", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)    
    data_sucursales = sucursales.json()
    return data_sucursales