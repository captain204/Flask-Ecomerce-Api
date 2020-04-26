from application.extensions import auth
from flask_restful import Resource
from flask import g
from application.blueprints.users.models import User,UserSchema

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

