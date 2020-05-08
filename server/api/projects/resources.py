from flask_restful import Resource, request

class ProjectApi(Resource):
    def get(self):
        return {"Success": "Hello"}, 200