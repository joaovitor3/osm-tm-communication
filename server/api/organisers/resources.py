from flask_restful import Resource, request
from server.models.postgres.organiser import Organiser
from server.models.serializers.organiser import OrganiserSchema
from server import db
from flask import make_response


class OrganiserApi(Resource):
    def get(self):
        result = Organiser.query.all()
        return make_response(OrganiserSchema(many=True).jsonify(result), 201)

    def post(self):
        organiser_schema = OrganiserSchema()
        organiser = Organiser()
        organiser.name = request.json["name"]
        organiser.link = request.json["link"]
        db.session.add(organiser)
        db.session.commit()
        return organiser_schema.dump(organiser), 201

    def delete(self):
        """ Deletes the current model from the DB """
        db.session.delete(self)
        db.session.commit()
