from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api,Resource
from photo.http_status import HttpStatus
from photo.models import db,Photo,PhotoSchema,PhotoCategory,PhotoCategorySchema, User, UserSchema
from sqlalchemy.exc import SQLAlchemyError
from photo.helpers import PaginationHelper
from flask_httpauth import HTTPBasicAuth
from flask import g




auth = HTTPBasicAuth()


photo_blueprint = Blueprint('photo', __name__)
user_schema = UserSchema()
photo_schema = PhotoSchema()
photo_category_schema = PhotoCategorySchema()


photo = Api(photo_blueprint)

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



class UserResource(AuthenticationRequiredResource):
    def get(self, id):
        """
            Getting a single user resource requires authentication
        ---
        parameters:
            - in: path
            id: id
            type: integer
            required: true
        responses:
            200:
            description: A single user item
            schema:
                id: User
                properties:
                id:
                    type: integer
                    description: The id of the user
                    default: 1
        """
        user = User.query.get_or_404(id)
        result = user_schema.dump(user)
        return result




class UserListResource(Resource):
    @auth.login_required
    def get(self):
        """
        Get all users
        ---
        description: Get all users.
        tags:
            - users
        responses:
            200:
            description: List of all users.
            content:
                application/json:
                schema:
                    type: array
                    items:
                        $ref: '#/components/schemas/User'           
        """
        pagination_helper = PaginationHelper(
            request,
            query=User.query,
            resource_for_url='photo.userlistresource',
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


#Single photo resource

class PhotoResource(AuthenticationRequiredResource):
    def get(self,id):
        """
        Getting a single photo resource requires authentication
        ---
        parameters:
            - in: path
            id: id
            type: integer
            required: true
        responses:
            200:
            description: A single photo item
            schema:
                id: Photo
                properties:
                id:
                    type: integer
                    description: The id of the photo
                    default: 1
        """
        photo = Photo.query.get_or_404(id)
        dumped_photo = photo_schema.dump(photo)
        return dumped_photo

    def patch(self,id):
    
        photo = Photo.query.get_or_404(id)
        photo_dict = request.get_json(force=True)
        print(photo_dict)
        if 'link' in photo_dict and photo_dict['link'] is not None:
            photo_link = photo_dict['link']
            #Check if image link exist in database  already
            if not Photo.is_link_unique(id = 0, link = photo_link):
                response = {'error':'An image with this link{} already exist'.format(photo_link)}
                return response, HttpStatus.bad_request_400.value
            photo.link = photo_link
        if 'description' in photo_dict and photo_dict['description'] is not None:
            photo.description = photo_dict['description']
        try:
            photo.update()
            response = {'update':'Update successfull'}
            return response, HttpStatus.ok_200.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value

    def delete(self,id):
        photo = Photo.query.get_or_404(id)
        try:
            delete = photo.delete(photo)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response ={"error":str(e)}
            return response, HttpStatus.unauthorized_401.value
            

#Collection of resources
class PhotoListResource(AuthenticationRequiredResource):
    def get(self):
        """
        Get all photos
        ---
        description: Get all photos.
        tags:
            - photos
        responses:
            200:
            description: List of all photos.
            content:
                application/json:
                schema:
                    type: array
                    items:
                        $ref:'#/components/schemas/Photo'           
        """
        pagination_helper = PaginationHelper(
            request,
            query=Photo.query,
            resource_for_url='photo.photolistresource',
            key_name='results',
            schema=photo_schema)
        result = pagination_helper.paginate_query()
        return result
        
    def post(self):
        photo_collection = request.get_json()
        #check if photo Collection is empty
        if not photo_collection:
            response = {'message':'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = photo_schema.validate(photo_collection)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        photo_link = photo_collection['link']
        if not Photo.is_link_unique(id=0,link=photo_link):
            response = {'error':'Photo already exist'.format(photo_link)}
            return response, HttpStatus.bad_request_400.value
        try:
            #check if photo category exist
            #Retreive photo category name from collection
            photo_category_name = photo_collection['photo_category']['name']
            category = PhotoCategory.query.filter_by(name=photo_category_name).first()
            if category is None:
                category = PhotoCategory(name=photo_category_name)
                db.session.add(category)
            # Add new photo
            photo=Photo(
                    link = photo_collection['link'],
                    description = photo_collection['description'],
                    photo_category = category
                )
            photo.add(photo)
            query = Photo.query.get(photo.id)
            dump_result = photo_schema.dump(query)
            return dump_result, HttpStatus.created_201.value

        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value
        
#Single photo resource
class PhotoCategoryResource(AuthenticationRequiredResource):
    def get(self,id):
        """
            Getting a single photo category resource requires authentication
        ---
        parameters:
            - in: path
            id: id
            type: integer
            required: true
        responses:
            200:
            description: A single photo item
            schema:
                id: Photo
                properties:
                id:
                    type: integer
                    description: The id of the photo category
                    default: 1
        """
        photo_category = PhotoCategory.query.get_or_404(id)
        dump_result = photo_category_schema.dump(photo_category)
        return dump_result

    def patch(self,id):
        photo_category = PhotoCategory.query.get_or_404(id)
        photo_category_collection = request.get_json()
        if not photo_category_collection:
            response = {'message':'Enter photo category'}
            return response, HttpStatus.bad_request_400.value
        errors = photo_category_schema.validate(photo_category_collection)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        #photo_category_name = photo_category_collection['name']
        try:
            if 'name' in photo_category_collection and photo_category_collection['name'] is not None:
                photo_category.name = photo_category_collection['name']
            if not PhotoCategory.is_name_exist(id=id,name=photo_category.name):
                response = {'error':'Category already exist'.format(photo_category.name)}
                return response, HttpStatus.bad_request_400.value        
            photo_category.update()
            response = {'update':'Update successfull'}
            return response, HttpStatus.ok_200.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {'error':str(e)}
            return response, HttpStatus.bad_request_400.value
            
    def delete(self,id):
        photo_category = PhotoCategory.query.get_or_404(id)
        try:
            photo_category.delete(photo_category)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.unauthorized_401.value
    
#Collection of photoCategorry resource
class PhotoCategoryListResource(AuthenticationRequiredResource):
    def get(self):
        """
        Get all categories
        ---
        description: Get all categories.
        tags:
            - categories
        responses:
            200:
            description: List of all categories.
            content:
                application/json:
                schema:
                    type: array
                    items:
                        $ref: '#/components/schemas/Category' 
                                      
        """
        photo_categories = PhotoCategory.query.all()
        dump_results = photo_category_schema.dump(photo_categories,many=True)
        return dump_results
    def post(self):
        photo_category_collection = request.get_json()
        if not photo_category_collection:
            response = {'message':'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = photo_category_schema.validate(photo_category_collection)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        photo_category_name = photo_category_collection['name'] 
        #Check if category name already exist
        if  PhotoCategory.is_name_exist(id=id,name=photo_category_name):
            response = {'error':'A photo category with name {} already exist'.format(photo_category_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            photo_category = PhotoCategory(photo_category_collection['name'])
            photo_category.add(photo_category) 
            query = PhotoCategory.query.get(photo_category.id)
            dump_result = photo_category_schema.dump(query)
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value
               


photo.add_resource(PhotoCategoryListResource,'/photo_category/')
photo.add_resource(PhotoCategoryResource,'/photo_category/<int:id>')
photo.add_resource(PhotoListResource,'/photos/')
photo.add_resource(PhotoResource,'/photos/<int:id>')
photo.add_resource(UserListResource, '/users/')
photo.add_resource(UserResource, '/users/<int:id>')