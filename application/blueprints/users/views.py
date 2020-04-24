from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api,Resource
from helpers.http_status import HttpStatus 
from application.blueprints.users.models import User,UserSchema 
from sqlalchemy.exc import SQLAlchemyError
from application.extensions import auth
from helpers.pagination import PaginationHelper
from flask import g



user_schema = UserSchema()
user = Blueprint('user', __name__)
api = Api(user)

@auth.verify_password
def verify_user_password(name, password):
    user = User.query.filter_by(name=name).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class AuthenticationRequiredResource(Resource):
    method_decorators = [auth.login_required]
    user_schema = UserSchema()



class UsersResource(AuthenticationRequiredResource):
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
            resource_for_url='users.userlistresource',
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
        user_name = user_dict['name']
        email = user_dict['email']
        existing_user = User.query.filter_by(name=user_name).first()
        if existing_user is not None:
            response = {'user': 'A user with the name {} already exists'.format(user_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            user=User(name=user_dict['name'],email=user_dict['email'])
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






api.add_resource(UserListResource, '/users/')
api.add_resource(UsersResource, '/users/<int:id>')

