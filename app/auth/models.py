from app import db
from app.deals.models import Contact
from flask import current_app
from flask_security import UserMixin, RoleMixin
from base64 import b64encode
import json
import os
from time import time

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

# Define a User model
class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)

    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    api_key = db.Column(db.String(32), index=True, unique=True, default=b64encode(os.urandom(32)).decode('utf-8'))

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(40))
    current_login_ip = db.Column(db.String(40))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    contact = db.relationship("Contact", uselist=False, back_populates="user")
    settings = db.relationship("Settings", uselist=False, back_populates="user")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.contact = Contact(email=self.email)

    def __repr__(self):
        return '%s' % (self.email)

    def get_deals(self):
        return [deal_contact.deal for deal_contact in self.contact.deal_contacts]

    def is_admin(self):
        return self.email in current_app.config['ADMINS']

    @staticmethod
    def check_api_key(api_key):
        user = User.query.filter_by(api_key=api_key).first()
        if user is None:
            return None
        return user

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return '%s' % (self.name)

class Settings(db.Model, UserMixin):

    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="settings")
    partnership_email_recipient = db.Column(db.String(255), unique=True)
