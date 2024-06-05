# -*- encoding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from apps.authentication import confirm_mail_required
from apps.authentication.forms import ProfileForm
from apps.home import blueprint
from flask import abort, jsonify, render_template,redirect, request, url_for
from flask_login import login_required, logout_user
from jinja2 import Template, TemplateNotFound
from apps import  login_manager

@blueprint.route('/index')
@login_required
@confirm_mail_required()
def index():
    token = request.cookies.get('token')
    url = "http://ljragusa.com.ar:3001/home"
    payload={}
    headers = { 'user-token': token }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    dataHome = respuesta.json()['elemts']
    ## verificar si supermercados['message'] existe
    if dataHome['Sucursals']==[]:
        return render_template('home/index.html', segment='index',supermercados=dataHome['Sucursals'],nombreEmpresa=dataHome['Empresa'])
    url = "http://ljragusa.com.ar:3001/notificaciones/getCantNoti"
    payload={}
    headers = { 'user-token': token }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta)
    notificaciones = respuesta.json()['elemts']
    sucursalNotificacion=[]
    for sucursal in dataHome['Sucursals']:
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
    return render_template('home/index.html', segment='index',supermercados=dataHome['Sucursals'],nombreEmpresa=dataHome['Empresa'],notificaciones=sucursalNotificacion)  #segment se usa en sidebar.html

@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
@confirm_mail_required()
def profile():
    profile_form = ProfileForm(request.form)
    if request.method=='POST': 
        if request.form.get('recibirTelegram') == None: recibirTelegram='False' 
        else: recibirTelegram='True'
        if request.form.get('recibirEmail') == None: recibirEmail = 'False' 
        else: recibirEmail = 'True'
        telegramId = request.form.get('idTelegram')
        token = request.cookies.get('token')
        url = "http://ljragusa.com.ar:3001/users"
        if telegramId == 'None':
            payload={
                "recibeNotiTelegram": recibirTelegram,
                "recibeNotiMail": recibirEmail,
            }
        else:    
            payload={
                "recibeNotiTelegram": recibirTelegram,
                "recibeNotiMail": recibirEmail,
                "telegramId": telegramId
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
                return render_template('accounts/profile_telegram.html', segment='profile', recibirTelegram=recibirTelegram, recibirEmail=recibirEmail, form=profile_form,)
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
        url = "http://ljragusa.com.ar:3001/users/"
        payload={
            "recibeNotiTelegram": recibirTelegram,
            "recibeNotiMail": recibirEmail,
            "telegramId": idTelegram
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
                                msg=respuesta.json()['error']['errors'][0]['message'],
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
    url = f'http://ljragusa.com.ar:3001/sucursales/{id_super}'
    respuesta2 = requests.request("GET", url, headers=headers, data=payload)
    verifSesión(respuesta2)
    nombrePlano = respuesta2.json()['nombrePlano']
    url = f'http://ljragusa.com.ar:3001/maquina/{id_super}'
    respuesta3 = requests.request("GET", url, headers=headers, data=payload)
    maquinas = respuesta3.json()
    notificaciones = respuesta.json()
    contador = {'val': 0, 'paginas': 0}
    contador2 = {'val': 0, 'paginas': 0}
    return render_template('home/panel.html', segment='index', id_super=id_super, notificaciones=notificaciones,contador = contador,contador2=contador2, nombrePlano=nombrePlano, maquinas=maquinas)

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
        return render_template('home/editarparametro.html', segment='index', idSucursal=idSucursal ,idMaquina=idMaquina, parametro=parametro ,descParametro=descripcionParametro, parametros=parametros)
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
        
@blueprint.route('/importancia/<int:idSucursal>/<int:idMaquina>/<string:parametro>', methods=['GET','POST'])
@login_required
@confirm_mail_required()
def importancia(idSucursal,idMaquina,parametro):
    if request.method=='GET':
        url = f'http://ljragusa.com.ar:3001/importanciaParametro/{idMaquina}'
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        respuesta= requests.request("GET", url, headers=headers, data=payload)
        verifSesión(respuesta)
        idAlgo=respuesta.json()['elemts']['id']
        if parametro == 'sensorTempInterna':
            parametros = respuesta.json()['elemts']['idTipoTempInterna']
            tipoImportancia='idTipoTempInterna'
            descripcionParametro='Temperatura Interna'
        elif parametro == 'sensorTempTrabajoYBulbo':
            parametros = respuesta.json()['elemts']['idTipoTempTrabajoYBulbo']
            tipoImportancia='idTipoTempTrabajoYBulbo'
            descripcionParametro='Temperatura de Trabajo y Bulbo'
        elif parametro == 'sensorPuerta':
            parametros = respuesta.json()['elemts']['idTipoEstadoPuerta']
            tipoImportancia='idTipoEstadoPuerta'
            descripcionParametro='Puerta'
        elif parametro == 'sensorRpmCooler':
            parametros = respuesta.json()['elemts']['idTipoCooler']
            tipoImportancia='idTipoCooler'
            descripcionParametro='Cooler'
        elif parametro == 'sensorPuntoRocio':
            parametros = respuesta.json()['elemts']['idTipoPuntoRocio']
            tipoImportancia='idTipoPuntoRocio'
            descripcionParametro='Punto de Rocío'
        elif parametro == 'sensorConsumo':
            parametros = respuesta.json()['elemts']['idConsumo']
            tipoImportancia='idConsumo'
            descripcionParametro='Consumo'
        return render_template('home/editarimportancia.html', segment='index', idAlgo=idAlgo, tipoImportancia=tipoImportancia, idSucursal=idSucursal ,idMaquina=idMaquina, parametro=parametro ,descParametro=descripcionParametro, parametros=parametros)
    elif request.method=='POST':
        url = f'http://ljragusa.com.ar:3001/importanciaParametro/{idMaquina}'
        payload={
            'id': request.form.get('idAlgo'),
            'idMaquina': idMaquina,
            parametro: request.form.get('importancia')
        }
        print(payload)
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
        return render_template('home/pre-graficos.html', segment='index', idSucursal=idSucursal ,idMaquina=idMaquina)
    if request.method=='POST':
        periodo_seleccionado = request.form.get('periodo')
        hoy = datetime.now().strftime("%Y-%m-%d")
        if periodo_seleccionado == '1':
            fechaInicio = (datetime.now() - relativedelta(days=7)).strftime("%Y-%m-%d")
            fechaFin = hoy
        elif periodo_seleccionado == '2':           
            fechaInicio = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")
            fechaFin = hoy
        elif periodo_seleccionado == '3':
            fechaInicio = (datetime.now() - relativedelta(months=2)).strftime("%Y-%m-%d")
            fechaFin = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")
        elif periodo_seleccionado == '4':
            fechaInicio = (datetime.now() - relativedelta(months=2)).strftime("%Y-%m-%d")
            fechaFin = hoy
        elif periodo_seleccionado == '5':
            fechaInicio = (datetime.now() - relativedelta(months=4)).strftime("%Y-%m-%d")
            fechaFin = (datetime.now() - relativedelta(months=2)).strftime("%Y-%m-%d")
        url = f'http://ljragusa.com.ar:3001/graphics/?fechaInicio={fechaInicio}&fechaFin={fechaFin}&idMaquina={idMaquina}'
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        respuesta= requests.request("GET", url, headers=headers, data=payload)
        verifSesión(respuesta)
        datos = respuesta.json()
        # Guardar en la variable datosJuntos lo mismo que datos pero en "valuesSensorRpmCooler":{ x,x,x,...} y "valuesSensorConsumo":{ x,x,x,...} los x dividirlos por 100
        datosJuntos = datos
        for key in datosJuntos:
            if key == 'valuesSensorRpmCooler':
                for i in range(len(datosJuntos[key])):
                    datosJuntos[key][i] = datosJuntos[key][i]/100
            if key == 'valuesSensorConsumo':
                for i in range(len(datosJuntos[key])):
                    datosJuntos[key][i] = datosJuntos[key][i]/100
        return render_template('home/graficos.html', segment='index', idSucursal=idSucursal ,idMaquina=idMaquina, datos=datos, datosJuntos=datosJuntos)

@blueprint.route('/reportes', methods=['GET','POST'])
@login_required
@confirm_mail_required()
def reportes():
    if request.method=='GET':
        url = "http://ljragusa.com.ar:3001/sucursales/token"
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        respuesta = requests.request("GET", url, headers=headers, data=payload)
        verifSesión(respuesta)
        sucursales = respuesta.json()
        return render_template('home/pre-reportes.html', segment='reportes',sucursales=sucursales)
    if request.method=='POST':
        idSucursal = request.form.get('idSucursalElegida')
        periodo_seleccionado = request.form.get('periodo')
        hoy = datetime.now().strftime("%Y-%m-%d")
        if periodo_seleccionado == '1':
            fechaInicio = (datetime.now() - relativedelta(days=7)).strftime("%Y-%m-%d")
            fechaFin = hoy
        elif periodo_seleccionado == '2':           
            fechaInicio = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")
            fechaFin = hoy
        elif periodo_seleccionado == '3':
            fechaInicio = (datetime.now() - relativedelta(months=2)).strftime("%Y-%m-%d")
            fechaFin = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")
        elif periodo_seleccionado == '4':
            fechaInicio = (datetime.now() - relativedelta(months=2)).strftime("%Y-%m-%d")
            fechaFin = hoy
        elif periodo_seleccionado == '5':
            fechaInicio = (datetime.now() - relativedelta(months=4)).strftime("%Y-%m-%d")
            fechaFin = (datetime.now() - relativedelta(months=2)).strftime("%Y-%m-%d")
        payload={}
        headers = { 'user-token': request.cookies.get('token') }
        url = f'http://ljragusa.com.ar:3001/graphics/pieChart?fechaInicio={fechaInicio}&fechaFin={fechaFin}&idSucursal={idSucursal}'
        respuestaPie= requests.request("GET", url, headers=headers, data=payload)
        verifSesión(respuestaPie)
        url = f'http://ljragusa.com.ar:3001/graphics/consumptionChart?fechaInicio={fechaInicio}&fechaFin={fechaFin}&idSucursal={idSucursal}'
        respuestaConsum= requests.request("GET", url, headers=headers, data=payload)
        verifSesión(respuestaConsum)
        datosP = respuestaPie.json()
        datosC = respuestaConsum.json()
        return render_template('home/reportes.html', segment='reportes', datosC=datosC, datosP=datosP, idSucursal=idSucursal)
    
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