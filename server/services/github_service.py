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
from server.models.postgres.document import Document
from server.models.postgres.task_manager import TaskManager
from requests.exceptions import HTTPError
from server.models.postgres.utils import NotFound


class GithubService:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + GITHUB_TOKEN
        }

    def create_or_update_github_file(self, json_content: dict,
                                     task_manager_id: int,
                                     update_file=False):
        project_id = json_content["project"]["id"]
        task_manager = TaskManager.get(task_manager_id)
        if task_manager is None:
            raise NotFound(f"Task Manager id {task_manager_id} not found")
        if Document.check_if_document_exists(project_id) and not update_file:
            raise HTTPError(
                f"Document for project {project_id} already exists in database"
            )
        elif not Document.check_if_document_exists(project_id) and update_file:
            raise HTTPError(
                f"Document for project {project_id} doesn't exists in database"
            )

        try:
            request_data = self.build_github_request_data(
                project_id,
                json_content,
                update_file
            )
            filename = "project" + str(project_id) + ".yaml"
            response = requests.put(
                GITHUB_API_ENDPOINT +
                f"repos/{GITHUB_REPOSITORY}/contents/github_files/{filename}",
                headers=self.headers,
                data=json.dumps(request_data)
            )
            response_content = response.json()
            response.raise_for_status()

            if update_file:
                document = Document.get(project_id)
                document.commit_hash = response_content["content"]["sha"]
                document.save()
            else:
                document = Document()
                document.commit_hash = response_content["content"]["sha"]
                document.link = response_content["content"]["html_url"]
                document.task_manager_id = task_manager.id
                document.create()
            return response_content["content"]["html_url"]
        except HTTPError:
            raise HTTPError(
                f"Document for project {project_id} already exists in github"
            )

    def build_github_request_data(self, project_id: int,
                                  json_content: dict,
                                  update_file=False):
        request_data = {
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            }
        }
        if update_file:
            yaml_dict = self.get_github_file_content(project_id)
            for key, value in json_content.items():
                yaml_dict[key] = value
            encoded_yaml = DocumentService.json_to_bytes_encoded_yaml(
                json_content
            )
            document = Document.get(project_id)
            request_data["message"] = "Update project " + str(project_id)
            request_data["sha"] = document.commit_hash
        else:
            request_data["message"] = "Add project " + str(project_id)
            encoded_yaml = DocumentService.json_to_bytes_encoded_yaml(
                json_content
            )

        request_data["content"] = encoded_yaml
        request_data["content"] = request_data["content"].decode("utf-8")
        return request_data

    def get_github_file_content(self, project_id):
        filename = "project" + str(project_id) + ".yaml"
        response = requests.get(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/github_files/{filename}",
            headers=self.headers
        )
        response_content = response.json()
        encoded_yaml = response_content["content"]
        yaml_dict = DocumentService.bytes_encoded_yaml_to_dict(encoded_yaml)
        return yaml_dict
