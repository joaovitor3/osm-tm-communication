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
from requests.exceptions import HTTPError
from flask import current_app


class GithubServiceError(Exception):
    """
    Custom Exception to notify callers an error occurred when handling wiki
    """
    def __init__(self, message):
        if current_app:
            current_app.logger.error(message)


class GithubService:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + GITHUB_TOKEN
        }

    def create_or_update_github_file(self,
                                     github_document_data: dict,
                                     update_file=False,
                                     github_project_id=None):
        try:
            project_id = (
                github_document_data["project"]["id"] if not update_file
                else github_project_id
            )
            request_data = self.build_github_request_data(
                project_id,
                github_document_data,
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
            return response_content["content"]["html_url"]
        except HTTPError:
            raise GithubServiceError(
                f"Document for project {project_id} already exists in github"
            )

    def build_github_request_data(self, project_id: int,
                                  github_document_data: dict,
                                  update_file=False):
        request_data = {
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            }
        }
        if update_file:
            github_file_content = self.get_github_file_content(project_id)
            yaml_dict = self.parse_encoded_yaml_to_dict(
                github_file_content,
                project_id
            )
            for key in github_document_data.keys():
                # always a nested dictionary
                for nested_key, value in github_document_data[key].items():
                    if isinstance(github_document_data[key], list):
                        yaml_dict[key][nested_key] = list(value)
                    else:
                        yaml_dict[key][nested_key] = value

            encoded_yaml = DocumentService.json_to_bytes_encoded_yaml(
                yaml_dict
            )
            request_data["message"] = "Update project " + str(project_id)
            request_data["sha"] = github_file_content["sha"]
        else:
            request_data["message"] = "Add project " + str(project_id)
            encoded_yaml = DocumentService.json_to_bytes_encoded_yaml(
                github_document_data
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
        return response_content

    def parse_encoded_yaml_to_dict(self, response_content, project_id):
        encoded_yaml = response_content["content"]
        yaml_dict = DocumentService.bytes_encoded_yaml_to_dict(encoded_yaml)
        return yaml_dict
