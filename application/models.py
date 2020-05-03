from marshmallow import Schema, fields, pre_load
from marshmallow import validate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from passlib.apps import custom_app_context as password_context
import re


db = SQLAlchemy()
ma = Marshmallow()


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
    username = db.Column(db.String(50), unique=True, nullable=False)
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

    def __init__(self, username):
        self.username = username




class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True,validate=validate.Length(3))
    password = fields.String(required=True,validate=validate.Length(6))
    url = ma.URLFor('product.userresource',id='<id>',_external=True)

class Product(db.Model,ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), unique=True, nullable=False)
    product_category_id = db.Column(db.Integer, db.ForeignKey('product_category.id', ondelete='CASCADE'), nullable=False)
    product_category = db.relationship('ProductCategory', backref=db.backref('products', lazy='dynamic' , order_by='Product.description'))
    tags = db.Column(db.String(250), nullable=False)
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def __init__(self,name,price,description,tags):
        self.name = name
        self.price = price
        self.description = description
        self.tags = tags

    @classmethod
    def is_name_unique(cls, id, description):
        existing_product_name = cls.query.filter_by(name=name).first()
        if existing_product_name is None:
            return True
        else:
            if existing_product_name.id == id:
                return True
            else:
                return False





class ProductCategory(db.Model,ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def is_name_unique(cls, id, name):
        existing_product_category = cls.query.filter_by(name=name).first()
        if existing_product_category is None:
            return True
        else:
            if existing_product_category.id == id:
                return True
            else:
                return False




class ProductCategorySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    # Minimum length = 3 characters
    name = fields.String(required=True, 
        validate=validate.Length(3))
    url = ma.URLFor('product.productresource', 
        id='<id>', 
        _external=True)
    interventions = fields.Nested('ProductSchema', 
        many=True, 
        exclude=('product_category',))



class ProductSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, 
        validate=validate.Length(3))
    price = fields.Integer()
    description= fields.String(required=True, 
        validate=validate.Length(3)),
    product_category = fields.Nested(ProductCategorySchema, 
        only=['id', 'url', 'name'], 
        required=True)
    tags = fields.String(required=True, 
        validate=validate.Length(3))
    url = ma.URLFor('application.productresource', 
        id='<id>', 
        _external=True)
    








    