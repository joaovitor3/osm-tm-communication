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
import os
from os import listdir
from os.path import isfile, join
from git import Repo
import shutil


class GithubServiceError(Exception):
    """
    Custom Exception to notify callers an error occurred when handling wiki
    """
    def __init__(self, message):
        if current_app:
            current_app.logger.error(message)


class GithubService:
    def __init__(self, project_information):
        self.file_folder = "github_files"
        self.platform_name = (
            project_information["platform"]["name"]
        )
        self.organisation_name = (
            project_information["organisation"]["name"]
        )
        self.project_id = (
            project_information["project"]["id"]
        )
        self.repo = Repo(
            current_app.config["REPORT_FILE_REPOSITORY_PATH"]
        )
        self.file_path = (
            f"{self.platform_name.replace(' ', '_')}/"
            f"{self.organisation_name.replace(' ', '_')}"
        )
        self.document_folder = (
            f'{current_app.config["REPORT_FILE_REPOSITORY_PATH"]}/'
            f'{self.file_folder}/'
            f'{self.file_path}'
        )

    def commit_file(self, commit_message: str) -> None:
        """
        Commit changes in the local git repository and push
        it to the remote repo

        Keyword arguments:
        commit_message -- The message of the commit
        """
        self.repo.index.commit(commit_message)
        origin = self.repo.remote(name='origin')
        origin.push()

    def create_file(self, document: dict) -> None:
        """
        Create a new file in a git repository

        Keyword arguments:
        document -- The string of the yaml file being created
        """
        # Parse dict to yaml and write it to the local repo
        yaml_file = DocumentService.json_to_yaml(
            document
        )
        self.write_yaml_file_to_local_repo(yaml_file, "x")

        # push the file  to the remote repo
        filename = "project_" + str(self.project_id) + ".yaml"
        self.repo.git.add([f"{self.document_folder}/{filename}"])
        commit_message = f"Add project {str(self.project_id)}"
        self.commit_file(commit_message)

    def write_yaml_file_to_local_repo(self, document: str, file_mode: str):
        """
        Write yaml file to the local git repository

        Keyword arguments:
        document -- The string of the yaml file being written
        file_mode -- The mode the file will be open
        """
        # Write the file in the local repo
        if not os.path.exists(self.document_folder):
            os.makedirs(self.document_folder)
        filename = "project_" + str(self.project_id) + ".yaml"
        f = open(f"{self.document_folder}/{filename}", file_mode)
        f.write(document)
        f.close()
            
    def update_file(self, document: dict) -> dict:
        """
        Generate the request data for update a file in github

        Keyword arguments:
        document -- The content of document being updated
        """
        # Write changes of the file in the local repo
        filename = "project_" + str(self.project_id) + ".yaml"            
        existing_yaml = self.get_file_content(f"{self.document_folder}/{filename}")
        new_yaml_file = self.update_yaml_dict(
            document,
            existing_yaml
        )
        self.write_yaml_file_to_local_repo(new_yaml_file, "w+")

        # if the platform/org name is updated it's necessary change
        # the folder structure of the repository
        if self.is_platform_or_org_name_being_updated(document):
            # Update the folder structure of the repo
            new_folder_path = self.get_new_folder_path(document)
            document_folder_files, new_document_folder_files = (
                self.get_staged_files(new_folder_path)
            )
            shutil.move(self.document_folder, new_folder_path)

            # Stage files
            self.repo.git.add(new_document_folder_files)
            self.repo.git.rm(document_folder_files)
        else:
            self.repo.git.add([f"{self.document_folder}/{filename}"])

        # push changes to the remote repo
        commit_message = f"Update project {str(self.project_id)}"
        self.commit_file(commit_message)

    def get_file_content(self, file_directory: str) -> str:
        """
        Get the content of a file and returns it as string

        Keyword arguments:
        file_directory -- The directory of the file

        Returns:
        file_content -- The content of the file as string
        """
        f = open(file_directory, "r")
        file_content = f.read()
        f.close()
        return file_content

    def is_platform_or_org_name_being_updated(self, document: dict) -> bool:
        """
        Check if a org or platform name is being updated

        Keyword arguments:
        document -- The content of document being updated

        Returns:
        bool -- Boolean indicating if a org or platform name is being updated
        """
        if ("organisation" in document.keys() and
            "name" in document["organisation"] or
            "platform" in document.keys() and
            "name" in document["platform"]):
            return True
        else:
            return False

    def get_staged_files(self, new_folder_path: str) -> tuple:
        """
        Get all files that need to be staged when a org/platform
        name is updated
        
        Keyword arguments:
        new_folder_path -- The updated folder path where files are
                           going to be stored
        
        Returns:
        tuple -- Tuple with two lists containing all files that need
                 to be staged
        """
        document_folder_files = [
            f"{self.document_folder}/{folder_file}"
            for folder_file in listdir(f"{self.document_folder}/")
                if isfile(
                    join(f"{self.document_folder}/", folder_file)
                )
        ]
        new_document_folder_files = [
            folder_file.replace(f"{self.document_folder}", f"{new_folder_path}")
            for folder_file in document_folder_files
        ]
        return document_folder_files, new_document_folder_files

    def get_new_folder_path(self, document: dict) -> str:
        """
        Generate new folder path with updated organisation / platform names

        Keyword arguments:
        document -- The content of document being updated

        Returns:
        folder_path -- The newfolder path with updated
                       organisation / platform names
        """
        if ("organisation" in document.keys()
            and "name" in document["organisation"] and
                "platform" in document.keys() and
                "name" in document["platform"]):
            platform_name = document["platform"]["name"]
            organisation_name = document["organisation"]["name"]

            folder_path = (
                f"{current_app.config['REPORT_FILE_REPOSITORY_PATH']}/"
                f"{self.file_folder}/{platform_name.replace(' ', '_')}"
                f"/{organisation_name.replace(' ', '_')}"
            )

        elif ("organisation" in document.keys()
              and "name" in document["organisation"] and
                  "platform" not in document.keys()):
            organisation_name = document["organisation"]["name"]
            folder_path = (
                f"{current_app.config['REPORT_FILE_REPOSITORY_PATH']}/"
                f"{self.file_folder}/{self.platform_name.replace(' ', '_')}/"
                f"{organisation_name.replace(' ', '_')}"
            )

        elif ("organisation" not in document.keys() and
              "platform" in document.keys() and
              "name" in document["platform"]):
            platform_name = document["platform"]["name"]
            folder_path = (
                f"{current_app.config['REPORT_FILE_REPOSITORY_PATH']}/"
                f"{self.file_folder}/{platform_name.replace(' ', '_')}/"
                f"{self.organisation_name.replace(' ', '_')}"
            )
        return folder_path

    def update_yaml_dict(self, document: dict,
                         yaml_str: str) -> str:
        """
        Generate the request data for update a file in github

        Keyword arguments:
        document -- The content of document being updated
        yaml_str -- The string representation of the bytes
                             encoded yaml present in github that
                             is being updated

        Returns:
        new_yaml_file -- The request data for update a file
                        in a github repository
        """
        new_yaml_dict = DocumentService.yaml_to_dict(yaml_str)

        # Update yaml dictionary with new values
        for key in document.keys():
            for nested_key, value in document[key].items():
                if isinstance(document[key][nested_key], list):
                    new_yaml_dict[key][nested_key] = list(value)
                elif isinstance(document[key][nested_key], dict):
                    for nested_dict_key in document[key][nested_key]:
                        new_yaml_dict[key][nested_key][nested_dict_key] = (
                             document[key][nested_key][nested_dict_key]
                        )
                else:
                    new_yaml_dict[key][nested_key] = value

        # Parse the updated yaml dictionary into yaml
        new_yaml_file = DocumentService.json_to_yaml(
            new_yaml_dict
        )
        return new_yaml_file
