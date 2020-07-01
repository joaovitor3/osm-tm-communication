from flask_restful import Resource, request
from flask import current_app
from server.services.overview_page_service import OverviewPageService
from server.services.organisation_page_service import OrganisationPageService
from server.services.project_page_service import ProjectPageService
import time


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
