from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
#from flasgger import Swagger
from helpers.docs import template
from flask_httpauth import HTTPBasicAuth


#swagger = Swagger(app,template=template)
db = SQLAlchemy()
migrate = Migrate(db)
auth = HTTPBasicAuth()
ma = Marshmallow()












