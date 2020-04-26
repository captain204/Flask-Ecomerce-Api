from marshmallow import pre_load
from marshmallow import validate
from application.extensions import db
from application.extensions import ma
from passlib.apps import custom_app_context as password_context
from flasgger import Swagger, SwaggerView, Schema, fields
#from application.blueprints.categories.models import(
    # CategorySchema) 





class ResourceAddUpdateDelete():   
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()



class Product(db.Model,ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    product_category_id = db.Column(db.Integer, db.ForeignKey('product_category.id', ondelete='CASCADE'), nullable=False)
    product_category = db.relationship('Category', backref=db.backref('products', lazy='dynamic' , order_by='Product.name'))
    tags = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)





    def __init__(self, name, price, description, tags):
        self.name = name
        self.price = price
        self.description = description
        self.tags = tags


    @classmethod
    def is_name_unique(cls, id, name):
        existing_product_name = cls.query.filter_by(name=name).first()
        if existing_product_name is None:
            return True
        else:
            if existing_product_name.id == id:
                return True
            else:
                return False




class ProductSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,validate=validate.Length(3))
    price = fields.Integer()
    description = fields.String(required=True,validate=validate.Length(3))
    tags = fields.String(required=True, validate=validate.Length(3))
    product_category = fields.Nested(CategorySchema, 
    only=['id', 'url', 'name'], required=True)
    url = ma.URLFor('product.productresource', id='<id>', _external=True)
    







