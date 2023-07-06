# -*- encoding: utf-8 -*-
import requests
from apps.authentication import role_required
from apps.authentication.forms import ProfileForm
from apps.home import blueprint
from flask import abort, render_template,redirect, request, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound

@blueprint.route('/prueba',methods=['GET', 'POST'])
def prueba():

    return render_template('home/prueba.html', segment='prueba')

@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')  #segment se usa en sidebar.html

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
        idTelegram = request.form['idTelegram'] 
        if request.form.get('recibirTelegram') == None: recibirTelegram='false' 
        else: recibirTelegram='true'
        if request.form.get('recibirEmail') == None: recibirEmail = 'false' 
        else: recibirEmail = 'true'
        token = request.cookies.get('token')

        
        print(request.form.get('recibirEmail'))
        print(request.form.get('recibirTelegram'))
        try:
            url = "http://ljragusa.com.ar:3001/users"
            payload={
                "telegramId": idTelegram,
                "recibeNotiTelegram": recibirTelegram,
                "recibeNotiMail": recibirEmail
            }
            headers = {
                'user-token': token
            }
            respuesta = requests.request("PATCH", url, headers=headers, data=payload)
            print(respuesta.text)
            datos=getOne(token)
            idTelegram = datos[0]
            recibirTelegram = datos[1]
            recibirEmail = datos[2]
            return render_template('accounts/profile.html', segment='profile', idTelegram=idTelegram, recibirTelegram=recibirTelegram, recibirEmail=recibirEmail, form=profile_form,
                               msg='Datos actualizados correctamente.',
                               success=True)

        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
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
    print(respuesta.text)
    datos = respuesta.json()
    idTelegram = datos['elemt']['telegramId']
    recibirTelegram = datos['elemt']['recibeNotiTelegram']
    recibirEmail = datos['elemt']['recibeNotiMail']
    return idTelegram, recibirTelegram, recibirEmail