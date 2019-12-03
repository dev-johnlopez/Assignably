from app import db
from app.deals.models import Contact, Deal
from flask import current_app
from flask_security import UserMixin, RoleMixin
from base64 import b64encode
import json
import os
from time import time

roles_users = db.Table('roles_users',
                       db.Column('user_id',
                                 db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id',
                                 db.Integer(),
                                 db.ForeignKey('role.id')))


class Tenant(db.Model):
    __tablename__ = 'tenant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    users = db.relationship("User", back_populates="tenant")
    deals = db.relationship("Deal", back_populates="tenant", foreign_keys='Deal.tenant_id')
    subdomain = db.Column(db.String(64), unique=True)
    investors = db.relationship("Investor", back_populates="tenant")
    settings = db.relationship("Settings",
                               uselist=False,
                               back_populates="tenant")

    def add_user(self, user):
        if self.users is None:
            self.users = []
        self.users.append(user)

    def get_investors(self):
        return self.investors

    def add_investor(self, investor):
        if self.investors is None:
            self.investors = []
        self.investors.append(investor)

    def get_deals(self):
        return self.deals

    def add_deal(self, deal):
        if self.deals is None:
            self.deals = []
        self.deals.append(deal)

    def get_settings(self):
        if self.settings is None:
            self.settings = Settings()
        return self.settings


class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    #username = db.Column(db.String(400), unique=True)

    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    api_key = db.Column(db.String(255),
                        index=True,
                        unique=True,
                        default=b64encode(os.urandom(32)).decode('utf-8'))

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(40))
    current_login_ip = db.Column(db.String(40))
    login_count = db.Column(db.Integer)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    tenant = db.relationship("Tenant", back_populates="users")
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    contact = db.relationship("Contact", uselist=False, back_populates="user")

    def __init__(self, **kwargs):
        kwargs.pop('contact', None)
        print("****** ******")
        print(kwargs)
        super(User, self).__init__(**kwargs)
        self.contact = Contact(
            first_name='John',
            last_name='Lopez',
            phone='8477030013'
        )

    def __repr__(self):
        return '{} {}'.format(self.contact.first_name, self.contact.last_name)

    def get_deals(self):
        return self.tenant.get_deals()

    def is_admin(self):
        return self.email.upper() in \
            (email.upper() for email in current_app.config['ADMINS'])

    def get_settings(self):
        return self.tenant.get_settings()

    def add_role(self, role):
        if self.roles is None:
            self.roles = []
        self.roles.append(role)

    def get_roles_string(self):
        return ""
        if self.roles is None:
            return ""
        return ", ".join(self.roles)

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
        return '{}'.format(self.name)


class Settings(db.Model, UserMixin):

    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    tenant = db.relationship("Tenant", back_populates="settings")
    partnership_email_recipient = db.Column(db.String(255))
