from flask_cors import CORS
from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from flask_marshmallow import Marshmallow


ma = Marshmallow()


def create_app():
    app = Flask(
        __name__
    )

    # Load configuration options from environment
    app.config.from_object("server.config.EnvironmentConfig")

    # Database configuration
    ma.init_app(app)

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
    from server.api.wiki_documents.resources import WikiDocumentApi

    api.add_resource(
        DocumentApi,
        "/document/",
        methods=["POST"],
        endpoint="create_document"
    )
    api.add_resource(
        DocumentApi,
        "/document/<string:platform_name>/"
        "<string:organisation_name>/<int:project_id>/",
        methods=["PATCH"],
        endpoint="update_doc"
    )
    api.add_resource(
        WikiDocumentApi,
        "/wiki-document/",
        methods=["POST"],
    )
    api.add_resource(
        WikiDocumentApi,
        "/wiki-document/"
        "<string:organisation_name>/<string:project_name>/",
        methods=["PATCH"],
        endpoint="update_wiki_doc"
    )
