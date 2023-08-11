# -*- encoding: utf-8 -*-

from flask_login import UserMixin

from sqlalchemy.orm import relationship
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import db, login_manager

class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(64), unique=True)
    nombre        = db.Column(db.String(64))
    apellido      = db.Column(db.String(64))
    rol           = db.Column(db.String(64))
    token         = db.Column(db.String(64))

    def __init__(self, id, email,nombre,apellido,rol,token):
        self.id = id
        self.email = email
        self.nombre= nombre
        self.apellido= apellido
        self.rol = rol
        self.token = token

    def __repr__(self):
        return str(self.username)

    @classmethod
    def find_by_email(cls, email: str) -> "User":
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_id(cls, _id: int) -> "User":
        return cls.query.filter_by(id=_id).first()
   
    def save(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()    

@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    return user if user else None