# -*- encoding: utf-8 -*-

from flask_login import UserMixin

from apps import login_manager

class Users(UserMixin):
    def __init__(self, id, email,nombre=''):
        self.id = id
        self.email = email
        self.nombre= nombre

    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True  
