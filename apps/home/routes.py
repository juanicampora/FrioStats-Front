# -*- encoding: utf-8 -*-
import requests
from apps.authentication import role_required
from apps.home import blueprint
from flask import abort, render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound

@blueprint.route('/prueba')
def prueba():
    token = request.cookies.get('token')
    print(token)
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
    if request.method=='POST':
        idTelegram = request.form['idTelegram']
        recibirTelegram=request.form['recibirTelegram']
        recibirEmail=request.form['recibirEmail']
        token = request.cookies.get('token')
        #enviar al api idtelegram, recibirTelegram y recibirEmail
        try:
            url = "http://ljragusa.com.ar:3001/users"
            payload={
                "telegramId": idTelegram,
                "recibirTelegram": recibirTelegram,
                "recibirEmail": recibirEmail
            }
            headers = {
                'user-token': token
            }
            respuesta = requests.request("POST", url, headers=headers, data=payload)
            
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)

        return render_template('accounts/profile.html', segment='profile')
    else:
        #pedir al api idtelegram, recibirTelegram y recibirEmail
        token = request.cookies.get('token')
        print(token)
        try:
            url = "http://ljragusa.com.ar:3001/users"
            headers = {
                'user-token': token
            }
            respuesta = requests.request("POST", url, headers=headers)
            datos = respuesta.json()
            idTelegram = datos['telegramId']
            recibirTelegram = datos['recibirTelegram']
            recibirEmail = datos['recibirEmail']
            confirmadoTelegram = datos['confirmadoTelegram']
            confirmadoEmail = datos['confirmadoEmail']
        except requests.exceptions.RequestException as e:
            print("\033[1;37;41mHUBO UN ERROR CON EL API\033[0m")
            return abort(500)
        return render_template('accounts/profile.html', segment='profile', idTelegram=idTelegram, recibirTelegram=recibirTelegram, recibirEmail=recibirEmail, confirmadoTelegram=confirmadoTelegram, confirmadoEmail=confirmadoEmail)

@blueprint.route('/<template>')
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
