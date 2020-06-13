from flask_restful import Resource, request
from flask import current_app
from marshmallow.exceptions import ValidationError

from server.services.github_service import (
    GithubService,
    GithubServiceError
)
from server.models.serializers.document import (
    DocumentSchema,
    is_known_document_content_type,
    turn_fields_optional
)


class DocumentApi(Resource):
    def post(self):
        """
        Create a new file in a github repository
        ---
        tags:
            - documents
        produces:
            - application/json
        parameters:
            - in: body
              name: body
              required: true
              description: JSON object for creating a document file in github
              schema:
                properties:
                    project:
                        type: object
                        properties:
                            title:
                                type: string
                                example: HOT Project
                            status:
                                type: string
                                example: Active
                            changesetComment:
                                type: string
                                example: "#hotProject"
                            externalSource:
                                type: string
                                example: https://learnosm.org/en/
                            goal:
                                type: string
                                example: Goal example
                            id:
                                type: int
                                example: 1
                            link:
                                type: string
                                example: tasks.hotosm.org/projects/1
                            tools:
                                type: string
                                example: Standard TM projects
                            projectManager:
                                type: string
                                example: Admin
                            created:
                                type: string
                                format: date-time
                                example: 2020-01-01T01:01:01.001Z
                            dueDate:
                                type: string
                                format: date-time
                                example: 2020-02-02T01:02:02.002Z
                            instructions:
                                type: string
                                example: Project instructions
                            users:
                                type: array
                                items:
                                    properties:
                                        osmId:
                                            type: int
                                            example: 1
                                        username:
                                            type: string
                                            example: mapper
                    organisation:
                        type: object
                        properties:
                            description:
                                type: string
                                example: Humanitarian mapping
                            link:
                                type: string
                                example: https://hotosm.org
                            name:
                                type: string
                                example: Humanitarian OpenStreetMap Team
                    organiser:
                        type: object
                        properties:
                            name:
                                type: string
                                example: Humanitarian OpenStreetMap Team
                            link:
                                type: string
                                example: https://tasks.hotosm.org
                            metrics:
                                type: string
                                example: Description of metrics
                            metrics:
                                type: string
                                example: Description of quality assurance
        responses:
            201:
                description: Document created in github
            409:
                description: Document already exists in github
            400:
                description: Error validating request
        """
        try:
            document_schema = DocumentSchema()
            document = (
                document_schema.load(request.json)
            )

            project_information = {
                "organiser": {
                    "name": document["organiser"]["name"]
                },
                "organisation": {
                    "name": document["organisation"]["name"]
                },
                "project": {
                    "id": document["project"]["id"]
                }
            }
            print("#"*30)
            print(project_information)
            print("#"*30)
            github = GithubService(project_information)
            github_file = github.create_file(
                document
            )
            return {"Success": f"File created {github_file}"}, 201
        except GithubServiceError as e:
            current_app.logger.error(f"Error validating document: {str(e)}")
            return {"Error": f"{str(e)}"}, 409
        except ValidationError as e:
            return {"Error": f"{str(e)}"}, 400

    def patch(self, organiser_name, organisation_name, project_id):
        """
        Update a existing file in a github repository
        ---
        tags:
            - documents
        produces:
            - application/json
        parameters:
            - in: path
              name: organiser_name
              description: The Organiser name
              required: true
              type: string
            - in: path
              name: organisation_name
              description: The Organisation name
              required: true
              type: string
            - in: path
              name: project_id
              description: The ID of the project
              required: true
              type: integer
            - in: query
              name: contentType
              type: string
              required: true
              enum: [project, organisation, organiser]
            - in: body
              name: body
              required: true
              description: JSON object for updating a yaml file on github
              schema:
                properties:
                    project:
                        type: object
                        properties:
                            status:
                                type: string
                                example: Archived
        responses:
            201:
                description: Document updated in github
            409:
                description: Document already exists in github
            400:
                description: Error validating request
        """
        try:
            content_type = request.args.getlist('contentType')
            is_known_document_content_type(content_type)

            optional_fields = turn_fields_optional(content_type)
            document_schema = DocumentSchema(
                partial=optional_fields,
                only=optional_fields
            )
            document = (
                document_schema.load(request.json)
            )

            project_information = {
                "organiser": {
                    "name": organiser_name
                },
                "organisation": {
                    "name": organisation_name
                },
                "project": {
                    "id": project_id
                }
            }
            github = GithubService(project_information)
            github_file = github.update_file(
                document
            )
            return {"Success": f"File updated {github_file}"}, 200
        except ValidationError as e:
            return {"Error": f"{str(e)}"}, 404
