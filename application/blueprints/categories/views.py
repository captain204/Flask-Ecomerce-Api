from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api,Resource
from helpers.http_status import HttpStatus 
from application.blueprints.categories.models import Category,CategorySchema 
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



category_schema = CategorySchema()
category = Blueprint('category', __name__)
api = Api(category)



class AuthenticationRequiredResource(Resource):
    method_decorators = [auth.login_required]
    user_schema = UserSchema()
















class CategoryResource(AuthenticationRequiredResource):
    def get(self, id):
        category = Category.query.get_or_404(id)
        dump_result = category_schema.dump(category)
        return dump_result

    def patch(self, id):
        category = Category.query.get_or_404(id)
        category_dict = request.get_json()
        if not category_dict:
            response = {'message': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = category_schema.validate(category_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        category_name = category_dict['name']
        if not Category.is_name_unique(id=0,name=category_name):
            response = {'error': 'A category with the name {} already exists'.format(category_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            if 'name' in category_dict and category_dic['name'] is not None:
                category.name = category_dict['name']
            category.update()
            return self.get(id)
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value
         
    def delete(self, id):
        category = Category.query.get_or_404(id)
        try:
            category.delete(category)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.unauthorized_401.value


class CategoryListResource(AuthenticationRequiredResource):
    def get(self):
        categories = NotificationCategory.query.all()
        dump_results = category_schema.dump(categories, many=True)
        return dump_results

    def post(self):
        print("Processing")
        category_dict = request.get_json()
        if not category_dict:
            response = {'message': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = category_schema.validate(category_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        category_name = category_dict['name']
        if not Category.is_name_unique(id=0,name=category_name):
            response = {'error': 'A category with the name {} already exists'.format(category_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            category = Category(category_dict['name'])
            category.add(category)
            query = Category.query.get(category.id)
            dump_result = category_schema.dump(query)
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value




api.add_resource(CategoryListResource, '/categories/')
api.add_resource(CategoryResource, '/categories/<int:id>')