# -*- encoding: utf-8 -*-
import requests
from apps.authentication import role_required
from apps.authentication.forms import ProfileForm
from apps.home import blueprint
from flask import abort, render_template,redirect, request, url_for
from flask_login import login_required, logout_user
from jinja2 import TemplateNotFound

@blueprint.route('/prueba',methods=['GET', 'POST'])
def prueba():

    return render_template('home/prueba.html', segment='prueba')

@blueprint.route('/index')
@login_required
def index():
    token = request.cookies.get('token')
    url = "http://ljragusa.com.ar:3001/locals/getLocals"
    payload={}
    headers = { 'user-token': token }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    supermercados = respuesta.json()
    notificaciones=[]
    return render_template('home/index.html', segment='index',supermercados=supermercados,notificaciones=notificaciones)  #segment se usa en sidebar.html

@blueprint.route('/roles')          #Hay que implementarlo (es para que un admin cambie los roles de los usuarios)
@login_required
@role_required('Admin')
def roles():
    return render_template('home/roles.html', segment='roles') 

@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
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
        headers = {
            'user-token': token
        }
        try:
            respuesta = requests.request("PATCH", url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        if respuesta.status_code == 200:
            datos=getOne(token)
            idTelegram = datos[0]
            recibirTelegram = datos[1]
            recibirEmail = datos[2]
            print(idTelegram)
            print(recibirTelegram)
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
        headers = {
            'user-token': token
        }
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
def panel(id_super):
    return render_template('home/panel.html', segment='panel', id_super=id_super)


@blueprint.route('/<template>')         #Cuando termine la etapa development borrar este route
@login_required
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


#Funciones usadas varias veces

def getOne(token):
    url = "http://ljragusa.com.ar:3001/users/getOne"
    payload={}
    headers = {
    'user-token': token
    }
    respuesta = requests.request("GET", url, headers=headers, data=payload)
    if respuesta.status_code == 403:
        logout_user()
        return abort(403)
    datos = respuesta.json()
    idTelegram = datos['elemt']['telegramId']
    recibirTelegram = datos['elemt']['recibeNotiTelegram']
    recibirEmail = datos['elemt']['recibeNotiMail']
    return idTelegram, recibirTelegram, recibirEmail