from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from application.http_status import HttpStatus
from application.models import db,Product,ProductSchema,ProductCategory,ProductCategorySchema
from sqlalchemy.exc import SQLAlchemyError
from application.helpers import PaginationHelper
from flask_httpauth import HTTPBasicAuth
from flask import g
from application.models import User, UserSchema

auth = HTTPBasicAuth()



product_blueprint = Blueprint('product', __name__)
user_schema = UserSchema()
product_schema = ProductSchema(many=True)
product_category_schema = ProductCategorySchema()


product = Api(product_blueprint)

@auth.verify_password
def verify_user_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

    

class AuthenticationRequiredResource(Resource):
    method_decorators = [auth.login_required]
    user_schema = UserSchema()



class UserResource(AuthenticationRequiredResource):
    def get(self, id):
        user = User.query.get_or_404(id)
        result = user_schema.dump(user)
        return result




class UserListResource(Resource):
    @auth.login_required
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=User.query,
            resource_for_url='tracker.userlistresource',
            key_name='results',
            schema=user_schema)
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        user_dict = request.get_json()
        if not user_dict:
            response = {'user': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = user_schema.validate(user_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        user_name = user_dict['username']
        existing_user = User.query.filter_by(username=user_name).first()
        if existing_user is not None:
            response = {'user': 'A user with the name {} already exists'.fdbat(user_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            user = User(username=user_name)
            error_message, password_ok = \
                user.check_password_strength_and_hash_if_ok(user_dict['password'])
            if password_ok:
                user.add(user)
                query = User.query.get(user.id)
                dump_result = user_schema.dump(query)
                return dump_result, HttpStatus.created_201.value
            else:
                return {"error": error_message}, HttpStatus.bad_request_400.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value

#Single product collection
class ProductResource(AuthenticationRequiredResource):
    def get(self, id):
        product = Product.query.get_or_404(id)
        dumped_product = product_schema.dump(product)
        return dumped_product

    def patch(self, id):
        product = Product.query.get_or_404(id)
        product_dict = request.get_json(force=True)
        print(product_dict)
        if 'name' in product_dict and product_dict['name'] is not None:
            product_name = product_dict['name']
            if not Product.is_name_unique(id=0, name=product_name):
                response = {'error': 'A product with this name {} already exists'.fdbat(product_name)}
                return response, HttpStatus.bad_request_400.value
            product.name = product_name
        if 'price' in product_dict and product_dict['price'] is not None:
            product.price = product_dict['price']
        if 'description' in product_dict and product_dict['description'] is not None:
           product.description = product_dict['description']
        if 'product_category' in product_dict and product_dict['product_category'] is not None:
               product.product_category = product_dict['product_category']
        if 'tags' in product_dict and product_dict['tags'] is not None:
            product.tags = product_dict['tags']
        dumped_product, dump_errors = product_schema.dump(product)
        if dump_errors:
            return dump_errors, HttpStatus.bad_request_400.value
        validate_errors = product_schema.validate(dumped_product)
        if validate_errors:
            return validate_errors, HttpStatus.bad_request_400.value
        try:
            product.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value

             
    def delete(self, id):
        product = Product.query.get_or_404(id)
        try:
            delete = product.delete(product)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
                db.session.rollback()
                response = {"error": str(e)}
                return response, HttpStatus.unauthorized_401.value


#A collection of products
class ProductListResource(AuthenticationRequiredResource):
    def get(self):
        pagination_helper = PaginationHelper(request,query=Product.query,                                                        resource_for_url='service.productlistresource',                                              key_name='results',             
                                      schema=product_schema)
        pagination_result = pagination_helper.paginate_query()
        return pagination_result
    
    def post(self):
        product_collection = request.get_json()
        if not product_collection:        
            response = {'message':'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = product_schema.validate(product_collection)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        product_name = product_collection['name']
        if not Product.is_name_unique(id=0,name=product_name):
            response = {'error':'Product already exist'.format(product_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            product_category_name = product_collection['product_category']['name'] 
            category = ProductCategory.query.filter_by(name=product_category_name).first()
            if category is None:
                category = ProductCategory(name=product_category_name)
                db.session.add(category)
            product=Product(
                name = product_collection['name'],
                price = product_collection['price'],
                description = product_collection['description'],
                product_category = category,
                tags = product_collection['tags']
            )
            product.add(product)
            query = Product.query.get(product.id)
            dump_result = product_schema.dump(query)
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value


class ProductCategoryResource(AuthenticationRequiredResource):
    def get(self, id):
        product_category = ProductCategory.query.get_or_404(id)
        dump_result = product_category_schema.dump(product_category)
        return dump_result

    def patch(self, id):
        product_category = ProductCategory.query.get_or_404(id)
        product_category_dict = request.get_json()
        if not product_category_dict:
            response = {'message': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = product_category_schema.validate(product_category_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        product_category_name = product_category_dict['name']
        if not ProductCategory.is_name_unique(id=0,name=product_category_name):
            response = {'error': 'A product category with the name {} already exists'.fdbat(product_category_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            if 'name' in product_category_dict and product_category_dic['name'] is not None:
                product_category.name = product_category_dict['name']
            product_category.update()
            return self.get(id)
        except SQLAlchemyError as e:
                db.session.rollback()
                response = {"error": str(e)}
                return response, HttpStatus.bad_request_400.value
         
    def delete(self, id):
        product_category = ProductCategory.query.get_or_404(id)
        try:
            product_category.delete(product_category)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
                db.session.rollback()
                response = {"error": str(e)}
                return response, HttpStatus.unauthorized_401.value


class ProductCategoryListResource(AuthenticationRequiredResource):
    def get(self):
        product_categories = ProductCategory.query.all()
        dump_results = product_category_schema.dump(product_categories, many=True)
        return dump_results

    def post(self):
        print("Processing")
        product_category_dict = request.get_json()
        if not product_category_dict:
            response = {'message': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = product_category_schema.validate(product_category_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        product_category_name = product_category_dict['name']
        if not ProductCategory.is_name_unique(id=0,name=product_category_name):
            response = {'error': 'A product category with the name {} already exists'.format(product_category_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            product_category = ProductCategory(product_category_dict['name'])
            product_category.add(product_category)
            query = ProductCategory.query.get(product_category.id)
            dump_result = product_category_schema.dump(query)
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            print("Error")
            print(e)
            db.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value


        




product.add_resource(UserListResource, '/users/')
product.add_resource(UserResource, '/users/<int:id>')
product.add_resource(ProductListResource,'/products/')
product.add_resource(ProductResource,'/products/<int:id>')
product.add_resource(ProductCategoryListResource,'/category/')
product.add_resource(ProductCategoryResource,'/category/<int:id>')