from flask_restful import Resource, request
from server.models.postgres.task_manager import TaskManager
from server.models.serializers.task_manager import TaskManagerSchema
from server import db
from flask import make_response


class TaskManagerApi(Resource):
    def get(self):
        result = TaskManager.query.all()
        return make_response(TaskManagerSchema(many=True).jsonify(result), 201)

    def post(self):
        tm_schema = TaskManagerSchema()
        task_manager = TaskManager()
        task_manager.name = request.json["name"]
        db.session.add(task_manager)
        db.session.commit()
        return tm_schema.dump(task_manager), 201

    def delete(self):
        """ Deletes the current model from the DB """
        db.session.delete(self)
        db.session.commit()
