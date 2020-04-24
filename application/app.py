from flask import Flask

from application.blueprints.users import user
from application.extensions import db,auth,migrate,ma

#Models
from application.blueprints.users.models import User



def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(user)
    #app.register_blueprint(product)
   
    extensions(app)
    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    db.init_app(app)
    #login_manager.init_app(app)
    migrate.init_app(app,db)
    ma.init_app(app)

    return None