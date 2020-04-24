from marshmallow import pre_load
from marshmallow import validate
from application.extensions import db
from application.extensions import ma
from passlib.apps import custom_app_context as password_context
from flasgger import Swagger, SwaggerView, Schema, fields
import re







class ResourceAddUpdateDelete():   
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()


class User(db.Model, ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    creation_date = db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp(), nullable=False)

    def verify_password(self, password):
        return password_context.verify(password, self.password_hash)

    def check_password_strength_and_hash_if_ok(self, password):
        if len(password) < 8:
            return 'The password is too short. Please, specify a password with at least 8 characters.', False
        if len(password) > 32:
            return 'The password is too long. Please, specify a password with no more than 32 characters.', False

        if re.search(r'[A-Z]', password) is None:
            return 'The password must include at least one uppercase letter.', False

        if re.search(r'[a-z]', password) is None:
            return 'The password must include at least one lowercase letter.', False

        if re.search(r'\d', password) is None:
            return 'The password must include at least one number.', False

        if re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]',password) is None:
            return 'The password must include at least one symbol.', False

        self.password_hash = password_context.hash(password)
        return '', True

    def __init__(self, name,email):
        self.name = name
        self.email = email




class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,validate=validate.Length(3))
    email = fields.String(required=True,validate=validate.Length(3))
    password = fields.String(required=True,validate=validate.Length(6))
    url = ma.URLFor('users.userresource',id='<id>',_external=True)

