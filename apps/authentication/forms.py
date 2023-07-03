# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
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
                             validators=[DataRequired()])
    name = StringField('Name',
                        id='name_create',
                        validators=[DataRequired(),Length(min=3, max=50),Regexp('^[A-Za-z]+$')])
    surname = StringField('Surname',
                        id='surname_create',
                        validators=[DataRequired(),Length(min=3, max=50),Regexp('^[A-Za-z]+$')])
