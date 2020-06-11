import requests
import json
from requests.exceptions import HTTPError
from flask import current_app

from server.constants import (
    GITHUB_TOKEN,
    GITHUB_REPOSITORY,
    GITHUB_COMMITER_NAME,
    GITHUB_COMMITER_EMAIL,
    GITHUB_API_ENDPOINT,
)
from server.services.document_service import DocumentService


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

    def create_file(self, document: dict) -> str:
        """
        Create a new file in a github repository

        Keyword arguments:
        document -- The content of document being created

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        file_url -- String containing the github url of the file created
        """
        try:
            project_id = document["project"]["id"]
            request_data = self.generate_create_file_request_data(
                project_id,
                document,
            )
            file_url = self.commit_file(project_id, request_data)
            return file_url
        except HTTPError:
            raise GithubServiceError(
                f"Document for project {project_id} already exists in github"
            )

    def update_file(self, document: dict, project_id: int) -> str:
        """
        Update a file in a github repository

        Keyword arguments:
        document -- The content of document being created
        project_id -- Id of the project document being updated

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        file_url -- String containing the github url of the file created
        """
        try:
            request_data = self.generate_update_file_request_data(
                project_id,
                document,
            )
            file_url = self.commit_file(project_id, request_data)
            return file_url
        except HTTPError:
            raise GithubServiceError(
                f"Error updating document for project {project_id}"
            )

    def generate_create_file_request_data(self, project_id: int,
                                          document: dict) -> dict:
        """
        Generate the request data for create a file in github

        Keyword arguments:
        project_id -- Id of the project document being created
        document -- The content of document being created

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        request_data -- The request data for create a file in github
        """
        encoded_yaml_document = DocumentService.json_to_bytes_encoded_yaml(
            document
        )

        request_data = {
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            }
        }
        request_data["message"] = "Add project " + str(project_id)
        request_data["content"] = encoded_yaml_document.decode("utf-8")
        return request_data

    def generate_update_file_request_data(self, project_id: int,
                                          document: dict) -> dict:
        """
        Generate the request data for update a file in github

        Keyword arguments:
        project_id -- Id of the project document being updated
        document -- The content of document being updated

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        request_data -- The request data for update a file
                        in a github repository
        """
        existing_yaml_file = self.get_file_content(project_id)
        existing_encoded_yaml_file = existing_yaml_file["content"]
        yaml_document_dict = DocumentService.bytes_encoded_yaml_to_dict(
            existing_encoded_yaml_file
        )
        for key in document.keys():
            # Always receive a nested dictionary from API request
            for nested_key, value in document[key].items():
                if isinstance(document[key], list):
                    yaml_document_dict[key][nested_key] = list(value)
                else:
                    yaml_document_dict[key][nested_key] = value

        encoded_yaml_document = DocumentService.json_to_bytes_encoded_yaml(
            yaml_document_dict
        )

        request_data = {
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            }
        }
        request_data["message"] = "Update project " + str(project_id)
        request_data["sha"] = existing_yaml_file["sha"]
        request_data["content"] = encoded_yaml_document.decode("utf-8")
        return request_data

    def commit_file(self, project_id: int, request_data: dict) -> str:
        """
        Commit a file to a github repository

        Keyword arguments:
        project_id -- Id of the project document
        request_data -- The request data for update a file
                        in a github repository

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        file_url -- String containing the github url of the file created
        """
        filename = "project_" + str(project_id) + ".yaml"
        response = requests.put(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/github_files/{filename}",
            headers=self.headers,
            data=json.dumps(request_data)
        )
        response_content = response.json()
        response.raise_for_status()

        file_url = response_content["content"]["html_url"]
        return file_url

    def get_file_content(self, project_id):
        """
        Generate the request data for create a file in github

        Keyword arguments:
        project_id -- Id of the project document being updated

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        response_content -- The reponse content containing
                            the github file information
        """
        filename = "project_" + str(project_id) + ".yaml"
        response = requests.get(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/github_files/{filename}",
            headers=self.headers
        )
        response_content = response.json()
        return response_content
