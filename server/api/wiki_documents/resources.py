from flask_restful import Resource, request

from server.services.document_service import WikiDocumentService
from server.services.wiki_service import WikiServiceError


class WikiDocumentApi(Resource):
    def post(self):
        try:
            wiki_document = WikiDocumentService()

            wiki_document.update_overview_page(request.json)
            wiki_document.update_orgs_activity_page(
                request.json
            )
            wiki_document.create_project_page(request.json)
            return {"msg": "success"}, 201
        except WikiServiceError as e:
            return {"Error": str(e)}, 400
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
