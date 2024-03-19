# -*- encoding: utf-8 -*-
import requests
from apps.authentication import confirm_mail_required
from apps.authentication.forms import ProfileForm
from apps.home import blueprint
from flask import abort, jsonify, render_template,redirect, request, url_for
from flask_login import login_required, logout_user
from jinja2 import Template, TemplateNotFound
from apps import  login_manager

@blueprint.route('/prueba',methods=['GET', 'POST'])     #borrar
def prueba():
    return render_template('home/prueba.html', segment='prueba')

@blueprint.route('/index')
@login_required
@confirm_mail_required()
def index():
    token = request.cookies.get('token')
    url = "http://ljragusa.com.ar:3001/sucursales"
    payload={}
    headers = { 'user-token': token }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    supermercados = respuesta.json()
    url = "http://ljragusa.com.ar:3001/notificaciones/getCantNoti"
    payload={}
    headers = { 'user-token': token }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    notificaciones=respuesta.json()
    return render_template('home/index.html', segment='index',supermercados=supermercados,notificaciones=notificaciones)  #segment se usa en sidebar.html

@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
@confirm_mail_required()
def profile():
    profile_form = ProfileForm(request.form)
    if request.method=='POST': 
        if request.form.get('recibirTelegram') == None: recibirTelegram='false' 
        else: recibirTelegram='true'
        if request.form.get('recibirEmail') == None: recibirEmail = 'false' 
        else: recibirEmail = 'true'
        token = request.cookies.get('token')
        url = "http://ljragusa.com.ar:3001/users"
        payload={
            "recibeNotiTelegram": recibirTelegram,
            "recibeNotiMail": recibirEmail
        }
        headers = { 'user-token': token }
        try:
            respuesta = requests.request("PATCH", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        verifSesión(respuesta)
        if respuesta.status_code == 200:
            datos=getOne(token)
            idTelegram = datos[0]
            recibirTelegram = datos[1]
            recibirEmail = datos[2]
            if recibirTelegram == True and idTelegram == None:
                return render_template('accounts/profile_telegram.html', segment='profile')
            else:    
                return render_template('accounts/profile.html', segment='profile', idTelegram=idTelegram, recibirTelegram=recibirTelegram, recibirEmail=recibirEmail, form=profile_form,
                                msg='Datos actualizados correctamente.',
                                success=True)
        else:
            return render_template('accounts/profile.html', segment='profile', form=profile_form,
                                msg='Error al actualizar los datos.',
                                success=False)
    else:
        token = request.cookies.get('token')
        try:
            datos=getOne(token)
            idTelegram = datos[0]
            recibirTelegram = datos[1]
            recibirEmail = datos[2]
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        return render_template('accounts/profile.html', segment='profile', idTelegram=idTelegram, recibirTelegram=recibirTelegram, recibirEmail=recibirEmail, form=profile_form)

@blueprint.route('/profile/telegram', methods=['GET', 'POST'])
@login_required
@confirm_mail_required()
def profile_telegram():
    if request.method=='POST': 
        idTelegram = request.form.get('idTelegram')
        try:
            token = request.cookies.get('token')
            datos=getOne(token)
            recibirTelegram = datos[1]
            recibirEmail = datos[2]
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        token = request.cookies.get('token')
        url = "http://ljragusa.com.ar:3001/users"
        payload={
            "telegramId": idTelegram,
            "recibeNotiTelegram": recibirTelegram,
            "recibeNotiMail": recibirEmail
        }
        headers = { 'user-token': token }
        try:
            respuesta = requests.request("PATCH", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        if respuesta.status_code == 200:
            profile_form = ProfileForm(request.form)
            return render_template('accounts/profile.html', segment='profile', idTelegram=idTelegram, recibirTelegram=recibirTelegram, recibirEmail=recibirEmail,
                                msg=respuesta.json()['message'],
                                success=True, form=profile_form)
        else:
            return render_template('accounts/profile_telegram.html', segment='profile', idTelegram=idTelegram, recibirTelegram=recibirTelegram, recibirEmail=recibirEmail,
                                msg=respuesta.json()['message'],
                                success=False)
    else:
        return render_template('accounts/profile_telegram.html', segment='profile')

@blueprint.route('/panel/<int:id_super>', methods=['GET','POST'])
@login_required
@confirm_mail_required()
def panel(id_super):
    token = request.cookies.get('token')
    url = f'http://ljragusa.com.ar:3001/notificaciones/getNotificaciones/{id_super}'
    payload={}
    headers = { 'user-token': token }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    notificaciones = respuesta.json()
    return render_template('home/panel.html', segment='panel', id_super=id_super, notificaciones=notificaciones)

@blueprint.route('/medicion/<int:idMaquina>', methods=['GET','POST'])
@login_required
@confirm_mail_required()
def devMediciones(idMaquina):
    url = f'http://ljragusa.com.ar:3001/mediciones/{idMaquina}'
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    respuesta= requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    maquinas = respuesta.json()
    archivo_ruta = "apps/templates/home/tablamediciones.html"
    with open(archivo_ruta, 'r') as tabla_file:
        tabla_template = Template(tabla_file.read())
        tablamediciones = tabla_template.render(maquinas=maquinas)  # Renderizar con Jinja2
    return jsonify({'tablamediciones': tablamediciones})
    
blueprint.route('/parametro/<int:idMaquina>/<string:parametro>', methods=['GET','POST'])
@login_required
@confirm_mail_required()
def parametro(idMaquina,parametro):
    if request.method=='GET':
        url = f'http://ljragusa.com.ar:3001/parameters/{idMaquina}/{parametro}'
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        respuesta= requests.request("GET", url, headers=headers, data=payload)
        verifSesión(respuesta)
        parametros = respuesta.json()
        #ESPERAR A LUCHO PARA CONTINUARLO
        return render_template('home/editarparametro.html', segment='panel', idMaquina=idMaquina, parametros=parametros)
    if request.method=='POST':
        #LEER LAS COSAS DEL POST Y GUARDAR CAMBIOS EN BBDD
        return redirect(url_for('home.panel')    )#,id_super=id_super))


@blueprint.route('/<template>')         #Cuando termine la etapa development borrar este route
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("accounts/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


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


#Funciones usadas varias veces
def verifSesión(respuesta):
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


def getOne(token):
    url = "http://ljragusa.com.ar:3001/users/"
    payload={}
    headers = { 'user-token': token }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    datos = respuesta.json()
    idTelegram = datos['elemt']['telegramId']
    recibirTelegram = datos['elemt']['recibeNotiTelegram']
    recibirEmail = datos['elemt']['recibeNotiMail']
    return idTelegram, recibirTelegram, recibirEmail