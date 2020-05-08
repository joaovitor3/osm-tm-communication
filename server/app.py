from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
POSTGRES_USER = "tm"
POSTGRES_PASSWORD = "tm"
POSTGRES_ENDPOINT = "localhost"
POSTGRES_PORT = "5433"
POSTGRES_DB = "tm-test"

SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{POSTGRES_USER}"
            + f":{POSTGRES_PASSWORD}"
            + f"@{POSTGRES_ENDPOINT}:"
            + f"{POSTGRES_PORT}"
            + f"/{POSTGRES_DB}"
        )
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)


@app.route('/project', methods=['POST'])
def hello_world():
    return 'Hello, World!'