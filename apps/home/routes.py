# -*- encoding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
import json
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
    ## verificar si supermercados['message'] existe
    if not('elemts' in supermercados):
        return render_template('home/index.html', segment='index',supermercados=supermercados)
    url = "http://ljragusa.com.ar:3001/notificaciones/getCantNoti"
    payload={}
    headers = { 'user-token': token }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    notificaciones = respuesta.json()['elemts']
    sucursalNotificacion=[]
    for sucursal in supermercados['elemts']:
        sucuNoti = {
            'id': sucursal['id'],
            'cantLeves': 0, 
            'cantGraves': 0
        }
        for notificacion in notificaciones:
            if notificacion != None:
                if sucursal['id'] == notificacion['idSucursal']:
                    sucuNoti['cantLeves'] = notificacion['cantLeves']
                    sucuNoti['cantGraves'] = notificacion['cantGraves']
                    break
        sucursalNotificacion.append(sucuNoti)      
    return render_template('home/index.html', segment='index',supermercados=supermercados,notificaciones=sucursalNotificacion)  #segment se usa en sidebar.html

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

@blueprint.route('/medicion/<int:idSucursal>/<int:idMaquina>', methods=['GET','POST'])
@login_required
@confirm_mail_required()
def devMediciones(idSucursal,idMaquina):
    url = f'http://ljragusa.com.ar:3001/mediciones/{idMaquina}'
    payload={}
    headers = { 'user-token': request.cookies.get('token') }
    respuesta= requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    maquinas = respuesta.json()
    archivo_ruta = "apps/templates/home/tablamediciones.html"
    with open(archivo_ruta, 'r') as tabla_file:
        tabla_template = Template(tabla_file.read())
        tablamediciones = tabla_template.render(maquinas=maquinas,idSucursal=idSucursal)  # Renderizar con Jinja2
    return jsonify({'tablamediciones': tablamediciones})
    
@blueprint.route('/parametro/<int:idSucursal>/<int:idMaquina>/<string:parametro>', methods=['GET','POST'])
@login_required
@confirm_mail_required()
def parametro(idSucursal,idMaquina,parametro):
    if request.method=='GET':
        url = f'http://ljragusa.com.ar:3001/parameters/{idMaquina}'
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        respuesta= requests.request("GET", url, headers=headers, data=payload)
        verifSesión(respuesta)
        if parametro == 'sensorTempInterna':
            parametros = [respuesta.json()['elemts']['minTempInterna'],respuesta.json()['elemts']['maxTempInterna']]
            descripcionParametro='Temperatura Interna'
        elif parametro == 'sensorTempTrabajoYBulbo':
            parametros = [respuesta.json()['elemts']['minTempTrabajoYBulbo'],respuesta.json()['elemts']['maxTempTrabajoYBulbo']]
            descripcionParametro='Temperatura de Trabajo y Bulbo'
        elif parametro == 'sensorRpmCooler':
            parametros = [respuesta.json()['elemts']['minRpmCooler'],respuesta.json()['elemts']['maxRpmCooler']]
            descripcionParametro='Cooler'
        elif parametro == 'sensorPuntoRocio':
            parametros = [respuesta.json()['elemts']['minPuntoRocio'],respuesta.json()['elemts']['maxPuntoRocio']]
            descripcionParametro='Punto de Rocío'
        elif parametro == 'sensorConsumo':
            parametros = ['Nada',respuesta.json()['elemts']['maxConsumo']]
            descripcionParametro='Consumo'
        return render_template('home/editarparametro.html', segment='panel', idSucursal=idSucursal ,idMaquina=idMaquina, parametro=parametro ,descParametro=descripcionParametro, parametros=parametros)
    elif request.method=='POST':
        minimobody=parametro.replace('sensor','min')
        maximobody=parametro.replace('sensor','max')
        if request.form.get('minimo') == None: minimo='null' 
        else: minimo=request.form.get('minimo')
        if request.form.get('maximo') == None: maximo='null' 
        else: maximo=request.form.get('maximo')
        url = f'http://ljragusa.com.ar:3001/parameters/{idMaquina}'
        payload={
            minimobody: minimo,
            maximobody: maximo
        }
        headers = { 'user-token': request.cookies.get('token') }
        respuesta = requests.request("PATCH", url, headers=headers, data=payload)
        verifSesión(respuesta)
        if respuesta.status_code == 200:
            return redirect(url_for('home_blueprint.panel',id_super=idSucursal))
        else:
            return abort(500)

@blueprint.route('/graficos/<int:idSucursal>/<int:idMaquina>', methods=['GET','POST'])
@login_required
@confirm_mail_required()
def graficos(idSucursal,idMaquina):
    if request.method=='GET':
        return render_template('home/pre-graficos.html', segment='panel', idSucursal=idSucursal ,idMaquina=idMaquina)
    if request.method=='POST':
        # url = f'http://ljragusa.com.ar:3001/graficos/{idSucursal}/{idMaquina}/{parametro}'   ## VER SI CON idMaquina y parametro solamente alcanza
        # payload={}
        # headers = { 'user-token': request.cookies.get('token') }
        # respuesta= requests.request("GET", url, headers=headers, data=payload)
        # verifSesión(respuesta)
        # print(respuesta.json())
        periodo_seleccionado = request.form.get('periodo')
        print(periodo_seleccionado)
        if periodo_seleccionado == '1':
            ## Crear variable hoy con fecha de hoy con date.now y fechaInicio hoy -4 dias y fechaFin hoy            
            hoy = datetime.now().strftime("%Y-%m-%d")
            fechaInicio = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
            fechaFin = hoy
            url = f'http://ljragusa.com.ar:3001/graphics/?fechaInicio={fechaInicio}&fechaFin={fechaFin}&idMaquina={idMaquina}'
            payload={}
            headers = { 'user-token': request.cookies.get('token') }
            respuesta= requests.request("GET", url, headers=headers, data=payload)
            verifSesión(respuesta)
            print(respuesta.json())

            datosString="""{
                "valuesSensorTempInterna": [12.1, 13.2, 15.3, 12.4, 16.5],
                "labelsSensorTempInterna": ["09:30 - 15/05","10:30 - 15/05","11:30 - 15/05","12:30 - 15/05","13:30 - 15/05"],
                "valuesSensorTempTrabajoYBulbo": [14.1, 15.2, 17.3, 14.4, 14.5],
                "labelsSensorTempTrabajoYBulbo": ["09:30 - 15/05","10:30 - 15/05","11:30 - 15/05","12:30 - 15/05","13:30 - 15/05"],
                "valuesSensorPuerta": [1,0,1,0,1],
                "labelsSensorPuerta": ["09:30 - 15/05","10:30 - 15/05","11:30 - 15/05","12:30 - 15/05","13:30 - 15/05"],
                "valuesSensorRpmCooler": [12.1, 14.2, 16.3, 14.4, 13.5],
                "labelsSensorRpmCooler": ["09:30 - 15/05","10:30 - 15/05","11:30 - 15/05","12:30 - 15/05","13:30 - 15/05"],
                "valuesSensorPuntoRocio": [18.1, 15.2, 12.3, 16.4, 13.5],
                "labelsSensorPuntoRocio": ["09:30 - 15/05","10:30 - 15/05","11:30 - 15/05","12:30 - 15/05","13:30 - 15/05"],
                "valuesSensorLuz": [1,0,1,0,1],
                "labelsSensorLuz": ["09:30 - 15/05","10:30 - 15/05","11:30 - 15/05","12:30 - 15/05","13:30 - 15/05"],
                "valuesSensorConsumo": [15.1, 13.2, 14.3, 16.4, 12.5],
                "labelsSensorConsumo": ["09:30 - 15/05","10:30 - 15/05","11:30 - 15/05","12:30 - 15/05","13:30 - 15/05"]
            }"""
            datos=json.loads(datosString)
            return render_template('home/graficos.html', segment='panel', idSucursal=idSucursal ,idMaquina=idMaquina, datos=datos)


@blueprint.route('/<template>')         #Cuando termine la etapa development borrar este route
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)
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

@blueprint.route('/error')         #Ruta de Error generico
def error_generico():
    return render_template('home/page-error-generico.html')

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