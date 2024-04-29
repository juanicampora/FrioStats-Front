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
    notificaciones = respuesta.json()['elemts']
    sucursalNotificacion=[]
    print(supermercados)
    print(notificaciones)
    print('ARRANCAAAAAAAAAAAA')
    for sucursal in supermercados['elemts']:
        print(sucursal)
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
        print(respuesta.json())
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
        print(parametros)
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
        print(respuesta.json())
        verifSesión(respuesta)
        if respuesta.status_code == 200:
            return redirect(url_for('home_blueprint.panel',id_super=idSucursal))
        else:
            return abort(500)

@blueprint.route('/graficos/<int:idSucursal>/<int:idMaquina>/<string:parametro>', methods=['GET'])
@login_required
@confirm_mail_required()
def graficos(idSucursal,idMaquina,parametro):
    if request.method=='GET':
        # url = f'http://ljragusa.com.ar:3001/graficos/{idSucursal}/{idMaquina}/{parametro}'   ## VER SI CON idMaquina y parametro solamente alcanza
        # payload={}
        # headers = { 'user-token': request.cookies.get('token') }
        # respuesta= requests.request("GET", url, headers=headers, data=payload)
        # verifSesión(respuesta)
        # print(respuesta.json())
        descParametro='Temperatura Interna'
        datos = [('15-44-23-04', 12), ('15-49-23-04', 13.01), ('15-54-23-04', 13.12), ('15-59-23-04', 12.02), ('16-04-23-04', 13.56), ('16-09-23-04', 14.11), ('16-14-23-04', 16.73), ('16-19-23-04', 15.43), ('16-24-23-04', 16.13), ('16-29-23-04', 16.83), ('16-34-23-04', 15.53), ('16-39-23-04', 14.23), ('16-44-23-04', 14.93), ('16-49-23-04', 13.93), ('16-54-23-04', 14.63), ('16-59-23-04', 15.22), ('17-04-23-04', 16.03), ('17-09-23-04', 16.73), ('17-14-23-04', 16.43)]
        labels = [dato[0] for dato in datos]
        values = [dato[1] for dato in datos]
        return render_template('home/graficos.html', segment='panel', idSucursal=idSucursal ,idMaquina=idMaquina, descParametro=descParametro, labels=labels, values=values)


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