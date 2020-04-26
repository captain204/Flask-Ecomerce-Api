from marshmallow import pre_load
from marshmallow import validate
from application.extensions import db
from application.extensions import ma
#from application.blueprints.products.models import ProductSchema
from passlib.apps import custom_app_context as password_context
from flasgger import Swagger, SwaggerView, Schema, fields
from application.blueprints.products.models import(
     ProductSchema) 



class ResourceAddUpdateDelete():   
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()





class Category(db.Model,ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def is_name_unique(cls, id, name):
        existing_category = cls.query.filter_by(name=name).first()
        if existing_category is None:
            return True
        else:
            if existing_category.id == id:
                return True
            else:
                return False


class CategorySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    # Minimum length = 3 characters
    name = fields.String(required=True, 
        validate=validate.Length(3))
    url = ma.URLFor('categories.categoryresource', 
        id='<id>', 
        _external=True)
    products = fields.Nested('ProductSchema', 
        many=True, 
        exclude=('product_category',))



