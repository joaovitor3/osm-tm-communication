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
import re
import json
import base64
import yaml


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
            "Authorization": "Bearer " + GITHUB_TOKEN,
            'User-Agent': GITHUB_COMMITER_NAME
        }
        self.file_folder = "github_files"
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
        try:
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
        except KeyError:
            raise GithubServiceError("Error getting updated page content")

    def get_new_folder_path(self, document):
        if ("organisation" in document.keys() and "name" in document["organisation"] and
            "organiser" in document.keys() and "name" in document["organiser"]):
            organiser_name = document["organiser"]["name"]
            organisation_name = document["organisation"]["name"]

            folder_path = f"{self.file_folder}/{organiser_name}/{organisation_name}"

        elif ("organisation" in document.keys() and "name" in document["organisation"] and
              "organiser" not in document.keys()):
            organisation_name = document["organisation"]["name"]
            folder_path = f"{self.file_folder}/{self.organiser_name}/{organisation_name}"

        elif ("organisation" not in document.keys() and
              "organiser" in document.keys() and "name" in document["organiser"]):
            organiser_name = document["organiser"]["name"]
            folder_path = f"{self.file_folder}/{organiser_name}/{self.organisation_name}"
        return folder_path


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

        if ("organisation" in document.keys() and "name" in document["organisation"] or
            "organiser" in document.keys() and "name" in document["organiser"]):

            new_folder_path = self.get_new_folder_path(document)
            folder_files = self.get_folders_files()
            

            last_commit_sha = self.get_last_commit()
            tree_request_data = self.generate_tree_request_data(
                folder_files,
                last_commit_sha,
                new_folder_path
            )
            new_tree = self.create_tree(
                tree_request_data
            )

            
            file_commit = self.create_commit(
                new_tree,
                last_commit_sha,
                new_folder_path
            )
            self.push_commit(file_commit)
            self.delete_folder_files(folder_files, new_folder_path)

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
            f"repos/{GITHUB_REPOSITORY}/contents/{self.file_folder}/"
            f"{file_path}/{filename}",
            headers=self.headers,
            data=json.dumps(request_data)
        )
        response_content = response.json()
        response.raise_for_status()

        file_url = response_content["content"]["html_url"]
        return file_url

    def get_folders_files(self) -> dict: # melhorar nome
        """
        Get files contained in a folder

        Returns:
        tree_files -- Dict containing data of files placed in folders which 
                      name is being updated
        """
        folder_tree_request = self.get_folder_tree_request()
        response = requests.get(
            folder_tree_request,
            headers=self.headers
        )

        tree_sha = response.json()["sha"]
        trees = response.json()["tree"]

        file_path = (
            f"{self.file_folder}/{self.organiser_name}/"
            f"{self.organisation_name}"
        )
        file_path_regex = f"({file_path})(.+?)(?=.yaml)"
        tree_files = {
            "tree_sha": tree_sha,
            "tree": []
        }

        for i, tree in enumerate(trees):
            filename = tree["path"]
            project_id = re.search("\d+", filename)
            tree_files["tree"].append({
                "id": project_id.group(),
                "path": file_path,
                "api_url": tree["url"],
                "sha": tree["sha"]
            })
        return tree_files

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
            f"repos/{GITHUB_REPOSITORY}/contents/{self.file_folder}/"
            f"{file_path}/{filename}",
            headers=self.headers
        )
        response_content = response.json()
        return response_content

    def generate_tree_request_data(self, folders: dict,
                                   last_commit_sha: str,
                                   new_folder_path: str) -> dict:
        """
        Generate the request data for creating tree with
        new folder structure containing new 
        organiser/organisation names

        Keyword arguments:
        folders -- Dict containing data of files placed in folders which 
                   name is being updated
        last_commit_sha -- Commit hash of the last commit in the repository
        new_folder_path -- New folder path containing the updated names 
                           for organisation/organiser

        Returns:
        tree_request_data -- The request data for the new tree containing
                             new organiser/organisation names
        """
        # Initiate tree request data
        tree_request_data = {
            "base_tree": last_commit_sha,
            "tree": []
        }

        for project in folders["tree"]:
            # Load tree request data 
            project_id = project["id"]
            file_mode = "100644"
            filename = f"project_{project_id}.yaml"

            # Append data to tree request data dict
            tree_request_data["tree"].append(
                {
                    "path": f"{new_folder_path}/{filename}",
                    "mode": file_mode,
                    "type": "blob",
                    "sha": project["sha"]
                }
            )
        return tree_request_data

    def get_last_commit(self) -> str:
        """
        Get repository last commit

        Returns:
        decoded_commit_hash -- Commit hash of last commit in 
                               the repository
        """
        last_commit_header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + GITHUB_TOKEN,
            "Accept": "application/vnd.github.VERSION.sha",
            'User-Agent': GITHUB_COMMITER_NAME
        }
        response = requests.get(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/commits/heads/master",
            headers=last_commit_header
        )
        decoded_commit_hash = response.content.decode("utf-8")
        return decoded_commit_hash

    def create_tree(self, tree_request_data: dict) -> str:
        """
        Create tree with new folder structure containing new 
        organiser/organisation names

        Keyword arguments:
        tre_request_data -- The request data for the new tree containing
                            new organiser/organisation names
        
        Returns:
        tree_sha: Hash of the created tree
        """
        response = requests.post(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/git/trees",
            headers=self.headers,
            data=json.dumps(tree_request_data)
        )
        response_content = response.json()
        tree_sha = response_content["sha"]
        return tree_sha


    def create_commit(self, new_tree_sha: str, 
                      last_commit_sha: str,
                      new_folder_path: str) -> str:
        """
        Create commit for a new tree

        Keyword arguments:
        new_tree_sha -- Hash of new tree
        last_commit_sha -- Commit hash of the last commit in the repository

        
        Returns:
        commit_sha: Hash of the created commit
        """
        file_path = f"{self.organiser_name}/{self.organisation_name}"
        commit_message = (
            f"Update folder structure from {file_path} to {new_folder_path}"
        )
        commit_data = {
            "message": commit_message,
            "tree": new_tree_sha,
            "parents": [last_commit_sha]
        }
        response = requests.post(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/git/commits",
            headers=self.headers,
            data=json.dumps(commit_data)
        )
        response_content = response.json()
        commit_sha = response_content["sha"]
        return commit_sha
    
    def delete_folder_files(self, folder_tree: dict, new_folder_path: str):
        """
        Delete files of tree with outaded organisation/organiser names
        
        Keyword arguments:
        folder_tree -- Dict containing data of files placed in folders which 
                       name is being updated
        new_folder_path -- New folder path containing the updated names 
                           for organisation/organiser
        """
        file_path = f"{self.organiser_name}/{self.organisation_name}"
        folder_path, organiser_name, organisation_name =(
            new_folder_path.split("/")
        ) 
        self.organisation_name = organisation_name
        self.organiser_name = organiser_name
        for project in folder_tree["tree"]:
            
            
            project_id = project["id"]
            filename = f"project_{project_id}.yaml"
            
            commit_message = (
                f"Move {project_id} to {new_folder_path}"
            )
            delete_data = {
                "message": commit_message,
                "sha": project["sha"]
            }
            delete_url = (
                GITHUB_API_ENDPOINT +
                f"repos/{GITHUB_REPOSITORY}/contents/{self.file_folder}/"
                f"{file_path}/{filename}"
            )
            response = requests.delete(
                delete_url,
                headers=self.headers,
                data=json.dumps(delete_data)
            )


    def push_commit(self, commit_sha: str):
        """
        Push commit to repository

        Keyword arguments:
        commit_sha -- Commit hash being pushed to repository
        """
        ref_data = {
            "sha": commit_sha
        }
        response = requests.patch(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/git/refs/heads/master",
            headers=self.headers,
            data=json.dumps(ref_data)
        )
        # add return

    def get_folder_tree_request(self) -> str:
        """
        Get GithHub API request from tree which
        organisation/organiser name is being updated

        Returns:
        tree_request_url -- GitHub API request string of
                            tree which organisation/organiser
                            name is being updated
        """

        file_path = f"{self.organiser_name}/{self.organisation_name}"
        response = requests.get(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/{self.file_folder}/"
            f"{self.organiser_name}",
            headers=self.headers
        )
        response_content = response.json()


        for item in response_content:
            if item["path"] == f"{self.file_folder}/{file_path}":
                tree_request_url = (
                    response_content[0]["git_url"] +
                    "?recursive=true"
                )
                return tree_request_url
