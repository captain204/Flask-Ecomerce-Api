template = {
  "swagger": "2.0",
  "info": {
    "title": "My API",
    "description": "API for my data",
    "contact": {
      "responsibleOrganization": "ME",
      "responsibleDeveloper": "Me",
      "email": "me@me.com",
      "url": "www.me.com",
    },
    "termsOfService": "http://me.com/terms",
    "version": "0.0.1"
  },
  "host": "https://favouritephotoapi.herokuapp.com/apidocs/",  # overrides localhost:500
  "basePath": "/photo",  # base bash for blueprint registration
  "schemes": [
    "http",
    "https"
  ],
  "operationId": "getmyData"
}