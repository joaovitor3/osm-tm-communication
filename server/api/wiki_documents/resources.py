from flask_restful import Resource, request
from flask import current_app
from server.services.overview_page_service import OverviewPageService
from server.services.organisation_page_service import OrganisationPageService
from server.services.project_page_service import ProjectPageService
import time
from server.models.serializers.document import (
    DocumentSchema,
    is_known_document_content_type,
    turn_fields_optional
)
from flask import current_app
from server.services.wiki_service import WikiService


class WikiDocumentApi(Resource):
    def post(self):
        try:
            start = time.time()

            overview_page = OverviewPageService()
            overview_page.create_page(request.json)

            organisation_page = OrganisationPageService()
            organisation_page.create_page(request.json)

            project_page = ProjectPageService()
            project_page.create_page(request.json)

            end = time.time()
            current_app.logger.debug(f"TIME: {end - start}")
            return {"msg": "success"}, 201
        except Exception:
            return {"Error": "Error processing request"}, 404
        # except InvalidMediaWikiToken as e:
        #     current_app.logger.debug(
        #         f"Error validating MediaWikiToken: {str(e)}"
        #     )
        #     return {"Error": str(e)}, 401
        # except PageNotFoundError as e:
        #     current_app.logger.debug(f"Error editing page: {str(e)}")
        #     return {"Error": str(e)}, 404
        # except ExistingPageError as e:
        #     current_app.logger.debug(f"Error creating page: {str(e)}")
        #     return {"Error": str(e)}, 409

    def patch(self, organisation_name: str, project_name: str):
        # method
        activities_list_page = "Organised_Editing/Activities"
        organisation_page_title = f"{activities_list_page}/{organisation_name}"
        organisation_page = OrganisationPageService()
        org_page_dictionary = organisation_page.wikitext_to_dict(organisation_page_title)
        organisation_fields = organisation_page.parse_page_to_serializer(org_page_dictionary)


        # method
        project_page = ProjectPageService()
        project_page_title = project_name.capitalize().replace(" ", "_")
        proj_page_dictionary = project_page.wikitext_to_dict(project_name)
        project_fields = project_page.parse_page_to_serializer(proj_page_dictionary)
        project_page_fields = project_page.get_page_fields()


        document_schema = DocumentSchema(
            partial=True
        )
        updated_fields = (
            document_schema.load(request.json)
        )

        # new method
        if "project" in updated_fields.keys() and "name" in updated_fields["project"].keys():
            pass
        
        # method
        all_project_fields = {
            **project_fields["project"], **organisation_fields["project"]
        }

        old_complete_document = {
            "project": all_project_fields,
            "organisation":  organisation_fields["organisation"],
            "platform":  organisation_fields["platform"]
        }


        document_schema = DocumentSchema()
        serialized_document = (
            document_schema.load(old_complete_document)
        )
        for key in updated_fields.keys():
            for nested_key, value in updated_fields[key].items():
                if isinstance(updated_fields[key][nested_key], list):
                    serialized_document[key][nested_key] = list(value)
                elif isinstance(updated_fields[key][nested_key], dict):
                    for nested_dict_key in updated_fields[key][nested_key]:
                        serialized_document[key][nested_key][nested_dict_key] = (
                             updated_fields[key][nested_key][nested_dict_key]
                        )
                else:
                    serialized_document[key][nested_key] = value


        overview_page = OverviewPageService()
        overview_page.edit_page(serialized_document, updated_fields, old_complete_document)

        organisation_page.edit_page(serialized_document, updated_fields, old_complete_document)

        project_page.edit_page(serialized_document)
        return {"msg": "success"}, 201
