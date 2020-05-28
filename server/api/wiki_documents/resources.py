from flask_restful import Resource, request
from server.services.document_service import WikiDocumentService
from server.constants import HOT_OEG_ACTIVITIES_PAGE


class WikiDocumentApi(Resource):
    def post(self):
        wiki_obj = WikiDocumentService()
        token = wiki_obj.get_token()
        page_title = request.json["title"]
        project_page_text = wiki_obj.format_project_page(page_title)
        project_page = wiki_obj.create_page(
            token, page_title,
            project_page_text
        )
        
        hot_oeg_activities_page_text = wiki_obj.get_page_text(HOT_OEG_ACTIVITIES_PAGE)
        project_table_row = wiki_obj.add_project_table(
            hot_oeg_activities_page_text,
            request.json,
            token
        )
        return {"Success": "msg"}, 201
    
    def put(self, project_name):
        wiki_obj = WikiDocumentService()
        token = wiki_obj.get_token()
        project_page_text = wiki_obj.get_page_text(project_name)
        coordinators = request.json["coordinators"]
        wiki_obj.update_coordination(project_page_text, coordinators, project_name, token)
        return {"Success": "msg"}, 201
    
