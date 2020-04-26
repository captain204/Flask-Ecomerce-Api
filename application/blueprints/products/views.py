from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api,Resource
from helpers.http_status import HttpStatus 
from application.blueprints.products.models import Product,ProductSchema 
from application.extensions import auth
from sqlalchemy.exc import SQLAlchemyError
from helpers.pagination import PaginationHelper
from flask import g
from application.blueprints.users.models import User,UserSchema

#from helpers.auth import verify_user_password, AuthenticationRequiredResource



@auth.verify_password
def verify_user_password(name, password):
    user = User.query.filter_by(name=name).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True



product_schema = ProductSchema()
product = Blueprint('product', __name__)
api = Api(product)



class AuthenticationRequiredResource(Resource):
    method_decorators = [auth.login_required]
    user_schema = UserSchema()



#Single product Collection
class ProductResource(AuthenticationRequiredResource):
    def get(self,id):
        product = Product.query.get_or_404(id)
        dumped_product = product_schema.dump(product)
        return dumped_product

    def patch(self,id):
        product = Product.query.get_or_404(id)
        product_dict = request.get_json(force=True)
        try:
            product.update()
            response = {'message':'Product Updated successfully'}
            return response, HttpStatus.ok_200.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value

    def delete(self,id):
        product = Product.query.get_or_404(id)
        try:
            delete = product.delete(product)
            respose = make_response
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response ={"error":str(e)}
            return response, HttpStatus.unauthorized_401.value
 

#Collection of products
class ProductListResource(AuthenticationRequiredResource):
    def get(self):
        pagination_helper = PaginationHelper(request,query=Product.query,
                            resource_for_url='product.productlistresource',
                            key_name='results',
                            schema=product_schema)
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        product_collection = request.get_json
        if not product_collection:
            response = {'message':'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = product_schema.validate(product_collection)
        if errors:
            return errors,HttpStatus.bad_request_400.value
        product_name = product_collection['name']
        if not Product.is_name_unique(id=0,name=product_name):
            response = {'error':'Product already exist'.format(product_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            product = Product(
                name = product_collection['name'],
                price = product_collection['price'],
                description = product_collection['description'],
                tags =  product_collection['tags']
            )
            product.add(product)
            query = Product.query.get(product.id)
            dump_result = product_schema.dump(query)
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value



api.add_resource(ProductListResource, '/products/')
api.add_resource(ProductResource, '/products/<int:id>')
