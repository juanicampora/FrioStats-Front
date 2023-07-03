# -*- encoding: utf-8 -*-

from flask_login import UserMixin

from apps import login_manager

class User(UserMixin):
    def __init__(self, id, email,nombre,rol):
        self.id = id
        self.email = email
        self.nombre= nombre
        self.rol = rol

    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True  
