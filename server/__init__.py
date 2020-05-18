from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate


db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# Import all models so that they are registered with SQLAlchemy
from server.models.postgres import document, task_manager   # noqa


def create_app():
    app = Flask(
        __name__
    )

    # Load configuration options from environment
    app.config.from_object("server.config.EnvironmentConfig")

    # Database configuration
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # Add paths to API endpoints
    add_api_endpoints(app)

    # Swagger configuration
    Swagger(app)

    # Enables CORS on all API routes, meaning API is callable from anywhere
    CORS(app)
    return app


def add_api_endpoints(app):
    api = Api(app)
    from server.api.documents.resources import DocumentApi
    from server.api.task_managers.resources import TaskManagerApi
    from server.api.authentication.resources import AuthenticationApi
    api.add_resource(
        DocumentApi,
        "/document/",
        methods=["GET", "POST"],
    )
    api.add_resource(
        TaskManagerApi,
        "/task-manager/",
        methods=["GET", "POST"],
    )
    api.add_resource(
        AuthenticationApi,
        "/gen-token/",
        methods=["POST", "GET"],
    )
