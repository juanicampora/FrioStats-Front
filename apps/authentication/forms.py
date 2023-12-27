# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import Email, DataRequired,Length,Regexp

# login and registration


class LoginForm(FlaskForm):
    email = StringField('Email',
                         id='Email_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired(),Length(min=6, max=50)])
    name = StringField('Name',
                        id='name_create',
                        validators=[DataRequired(),Length(min=3, max=50),Regexp(r'^[a-zA-Z]+$', message='Ingrese solo letras.')])
    surname = StringField('Surname',
                        id='surname_create',
                        validators=[DataRequired(),Length(min=3, max=50),Regexp(r'^[a-zA-Z]+$', message='Ingrese solo letras.')])


class ProfileForm(FlaskForm):
    idTelegram = StringField('idTelegram',id='idTelegram')
    recibirTelegram = StringField('recibirTelegram',id='recibirTelegram')
    recibirEmail = StringField('recibirEmail',id='recibirEmail')

class RolesForm(FlaskForm):
    idUsuario = StringField('idUsuario',id='idUsuario')
    idRol = StringField('idRol',id='idRol')