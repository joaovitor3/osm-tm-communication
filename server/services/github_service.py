from server.constants import (
    GITHUB_TOKEN,
    GITHUB_REPOSITORY,
    GITHUB_COMMITER_NAME,
    GITHUB_COMMITER_EMAIL,
    GITHUB_API_ENDPOINT,
)
from server.services.document_service import DocumentService
import requests
import json


class GithubService:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + GITHUB_TOKEN
        }

    def create_file(self, json_content):
        project_id = str(json_content["project"]["id"])
        document = DocumentService(json_content)
        encoded_yaml = document.json_to_bytes_encoded_yaml()
        
        request_data = self.build_github_request(project_id, encoded_yaml)
        filename = "project" + project_id + ".yaml"
        response = requests.put(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/github_files/{filename}",
            headers=self.headers,
            data=json.dumps(request_data)
        )
        response.raise_for_status()
        return response.json()

    def build_github_request(self, project_id: str, encoded_yaml):
        request_data = {
            "message": "Add project " + project_id,
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            },
            "content": encoded_yaml
        }
        request_data["content"] = request_data["content"].decode("utf-8")
        return request_data
