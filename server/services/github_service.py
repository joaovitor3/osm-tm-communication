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
    def __init__(self, project_information):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + GITHUB_TOKEN
        }
        self.organiser_name = (
            project_information["organiser"]["name"]
        )
        self.organisation_name = (
            project_information["organisation"]["name"]
        )
        self.project_id = (
            project_information["project"]["id"]
        )

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
            # Create yaml file on github
            request_data = self.generate_create_file_request_data(
                document
            )
            file_url = self.commit_file(request_data)
            return file_url
        except HTTPError:
            raise GithubServiceError(
                f"Document for project {self.project_id} "
                "already exists in github"
            )

    def update_file(self, document: dict) -> str:
        """
        Update a file in a github repository

        Keyword arguments:
        document -- The content of document being created

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        file_url -- String containing the github url of the file created
        """
        try:
            # Update yaml file available on github
            request_data = self.generate_update_file_request_data(
                document
            )
            file_url = self.commit_file(request_data)
            return file_url
        except HTTPError:
            raise GithubServiceError(
                f"Error updating project {self.project_id}"
            )

    def generate_create_file_request_data(self, document: dict) -> dict:
        """
        Generate the request data for create a file in github

        Keyword arguments:
        document -- The content of document being created

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        request_data -- The request data for create a file in github
        """
        # Parse the dictionary with yaml content into bytes
        encoded_yaml_document = DocumentService.json_to_bytes_encoded_yaml(
            document
        )

        # Build create file request data
        request_data = {
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            }
        }
        request_data["message"] = "Add project " + str(self.project_id)
        request_data["content"] = encoded_yaml_document.decode("utf-8")
        return request_data

    def generate_update_file_request_data(self, document: dict) -> dict:
        """
        Generate the request data for update a file in github

        Keyword arguments:
        document -- The content of document being updated

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        request_data -- The request data for update a file
                        in a github repository
        """
        # Get yaml file and update its content
        yaml_file_content = self.get_file_content()
        encoded_yaml_file = yaml_file_content["content"]
        new_encoded_yaml_file = self.update_yaml_dict(
            document,
            encoded_yaml_file
        )

        # Build update file request data
        request_data = {
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            }
        }
        request_data["message"] = "Update project " + str(self.project_id)
        request_data["sha"] = yaml_file_content["sha"]
        request_data["content"] = new_encoded_yaml_file.decode("utf-8")
        return request_data

    def update_yaml_dict(self, document: dict,
                         encoded_yaml_file: str) -> bytes:
        """
        Generate the request data for update a file in github

        Keyword arguments:
        document -- The content of document being updated
        encoded_yaml_file -- The string representation of the bytes
                             encoded yaml present in github that
                             is being updated

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        request_data -- The request data for update a file
                        in a github repository
        """
        # Parse encoded yaml into a dictionary
        new_yaml_dict = DocumentService.bytes_encoded_yaml_to_dict(
            encoded_yaml_file
        )

        # Update yaml dictionary with new values
        for key in document.keys():
            for nested_key, value in document[key].items():
                if isinstance(document[key], list):
                    new_yaml_dict[key][nested_key] = list(value)
                else:
                    new_yaml_dict[key][nested_key] = value

        # Parse the updated yaml dictionary into bytes
        new_encoded_yaml_file = DocumentService.json_to_bytes_encoded_yaml(
            new_yaml_dict
        )
        return new_encoded_yaml_file

    def commit_file(self, request_data: dict) -> str:
        """
        Commit a file to a github repository

        Keyword arguments:
        request_data -- The request data for update a file
                        in a github repository

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        file_url -- String containing the github url of the file created
        """
        # Commit file to github
        filename = "project_" + str(self.project_id) + ".yaml"
        file_path = f"{self.organiser_name}/{self.organisation_name}"
        response = requests.put(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/github_files/"
            f"{file_path}/{filename}",
            headers=self.headers,
            data=json.dumps(request_data)
        )
        response_content = response.json()
        response.raise_for_status()

        file_url = response_content["content"]["html_url"]
        return file_url

    def get_file_content(self) -> dict:
        """
        Generate the request data for create a file in github

        Raises:
        GithubServiceError -- Exception raised when handling github service

        Returns:
        response_content -- The reponse content containing
                            the github file information
        """
        # Get file availabe on github
        filename = "project_" + str(self.project_id) + ".yaml"
        file_path = f"{self.organiser_name}/{self.organisation_name}"
        response = requests.get(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/github_files/"
            f"{file_path}/{filename}",
            headers=self.headers
        )
        response_content = response.json()
        return response_content
