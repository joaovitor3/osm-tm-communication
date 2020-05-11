import logging
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restful import Api

from server.config import EnvironmentConfig


db = SQLAlchemy()

def create_app():
    app = Flask(
        __name__
    )

    # Load configuration options from environment
    app.config.from_object(f"server.config.EnvironmentConfig")

    # Connect to database
    db.init_app(app)
    
    # Add paths to API endpoints
    add_api_endpoints(app)


    # Enables CORS on all API routes, meaning API is callable from anywhere
    CORS(app)

    return app

def add_api_endpoints(app):
    api = Api(app)
    from server.api.projects.resources import ProjectApi
    api.add_resource(
        ProjectApi,
        "/document/",
        methods=["GET", "POST"],
    )