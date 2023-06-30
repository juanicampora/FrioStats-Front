# -*- encoding: utf-8 -*-

from flask_login import UserMixin

from sqlalchemy.orm import relationship
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import db, login_manager

class Users(db.Model, UserMixin):

    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(64), unique=True)
    nombre        = db.Column(db.String(64))
