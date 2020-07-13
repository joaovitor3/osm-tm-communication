from server.services.wiki_service import (
    WikiService
)
from server.services.templates import (
    ProjectPage
)
from server.services.wiki_page_service import WikiPageService
from flask import current_app
import wikitextparser as wtp
from server.models.serializers.document import (
    DocumentSchema,
    is_known_document_content_type,
    turn_fields_optional
)
import re
from datetime import datetime



class ProjectPageService(WikiPageService):
    def __init__(self):
        self.short_description_section = (
            ProjectPage.SHORT_DESCRIPTION_SECTION
                       .value
        )
        self.timeframe_section = ProjectPage.TIMEFRAME_SECTION.value
        self.created_section = ProjectPage.CREATED_DATE.value
        self.url_section = ProjectPage.URL_SECTION.value
        self.external_sources_section = (
            ProjectPage.EXTERNAL_SOURCES_SECTION.value
        )
        self.instructions_section = ProjectPage.INSTRUCTIONS_SECTION.value
        self.per_task_instructions_section = (
            ProjectPage.PER_TASK_INSTRUCTIONS_SECTION.value
        )
        self.imagery_section = (
            ProjectPage.IMAGERY_SECTION.value
        )
        self.license_section = (
            ProjectPage.LICENSE_SECTION.value
        )
        self.hashtag_section = (
            ProjectPage.HASHTAG_SECTION.value
        )
        self.metrics_section = ProjectPage.METRICS_SECTION.value
        self.quality_assurance_section = (
            ProjectPage.QUALITY_ASSURANCE_SECTION.value
        )
        self.users_list_section = ProjectPage.USERS_LIST_SECTION.value
        self.project_page_template = ProjectPage.PAGE_TEMPLATE.value
        self.page_initial_section = (
            ProjectPage.PROJECT_SECTION.value
        )
        self.project_section = (
            ProjectPage.PROJECT_SECTION.value
        )
        self.team_user_section = ProjectPage.TEAM_AND_USER_SECTION.value

    def filter_page_data(self, document_data: dict) -> dict:
        """
        Filter required data for the project page from
        document data

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        project_page_data -- Dict containing only the required data
                             for the project page
        """
        name = (
            document_data["project"]["name"]
        )
        short_description = (
            document_data["project"]["shortDescription"]
        )
        created = (
            document_data["project"]["created"]
        )
        # due_date = (
        #     document_data["project"]["dueDate"]
        # )
        changeset_comment = (
            document_data["project"]["changesetComment"]
        )
        instructions = (
            document_data["project"]["externalSource"]["instructions"]
        )
        per_task_instructions = (
            document_data["project"]["externalSource"]["perTaskInstructions"]
        )
        imagery = (
            document_data["project"]["externalSource"]["imagery"]
        )
        license = (
            document_data["project"]["externalSource"]["license"]
        )
        url = (
            document_data["project"]["url"]
        )
        # metrics = (
        #     document_data["platform"]["metrics"]
        # )
        # quality_assurance = (
        #     document_data["platform"]["qualityAssurance"]
        # )
        users = (
            document_data["project"]["users"]
        )
        project_page_data = {
            "project": {
                "name": name,
                "shortDescription": short_description,
                "created": created,
                # "due_date": due_date,
                "changesetComment": changeset_comment,
                "externalSource": {
                    "instructions": instructions,
                    "perTaskInstructions": per_task_instructions,
                    "imagery": imagery,
                    "license": license
                },
                "url": url,
                "users": users
            }
            # "metrics": metrics,
            # "quality_assurance": quality_assurance,
        }
        return project_page_data

    def get_page_fields(self) -> list:
        """
        Get all required fields for the project page

        Returns:
        list -- List containing all required fields
                for the project page
        """
        project_page_fields = [
            'project.name', 'project.short_description',
            'project.created', 'project.changeset_comment',
            'project.external_source.instructions',
            'project.external_source.per_task_instructions',
            'project.external_source.imagery',
            'project.external_source.license',
            'project.url', 'project.project_id', 'project.users'
        ]
        return project_page_fields

    def generate_page_sections_dict(self, project_page_data: dict):
        """
        Generate dict containing the document content parsed to wikitext
        for all sections present in the project page

        Keyword arguments:
        project_page_data -- Dictionary containing the required data for the
                              project page sections

        Returns:
        project_page_sections -- Dictionary with the document content
                                 parsed to wikitext for the project
                                 page sections
        """
        wiki_obj = WikiService()

        short_description = (
            f"\n{project_page_data['project']['shortDescription']}\n"
        )

        created_date = wiki_obj.format_date_text(
            project_page_data['project']['created']
        )
        # created_date_text = f"\n{created_date}\n" 
        # due_date = wiki_obj.format_date_text(
        #     project_page_data['project']['due_date']
        # )
        timeframe = (
            f"\n* '''Start Date:''' {created_date}\n"
            # f"\n* '''End Date:''' Estimate {due_date}\n"
        )


        project_url = (
            f"\n{project_page_data['project']['url']}\n"
        )

        hashtag = (
            project_page_data['project']['changesetComment']
        )
        hashtag = (
            project_page_data['project']['changesetComment'].replace(
                "#", "<nowiki>#</nowiki>"
            )
        )
        hashtag_text = (
            f"\n{hashtag}\n"
        )

        instructions_text = (
            project_page_data['project']
                             ['externalSource']
                             ['instructions']
        )
        instructions = (
            f"\n{instructions_text}\n"
        )

        per_task_instructions_text = (
            project_page_data['project']
                             ['externalSource']
                             ['perTaskInstructions']
        )
        per_task_instructions = (
            f"\n{per_task_instructions_text}\n"
        )

        imagery_text = (
            project_page_data['project']
                             ['externalSource']
                             ['imagery']
        )
        imagery = (
            f"\n{imagery_text}\n"
        )

        license_text = (
            project_page_data['project']
                             ['externalSource']
                             ['license']
        )
        license = (
            f"\n{license_text}\n"
        )

        # metrics = (
        #     f"\n* {project_page_data.instructions}\n"
        # )
        # quality_assurance = (
        #     f"\n* {project_page_data.quality_assurance}\n"
        # )

        users = project_page_data['project']["users"]
        project_users = ""
        for user in users:
            project_users += (
                f"\n| {user['userId']}\n| {user['userName']}\n|-"
            )

        

        project_page_sections = {
            self.short_description_section: short_description,
            self.timeframe_section: timeframe,
            # self.timeframe_section: {
            #     self.created_section: created_date_text
            # }, # if choose use subsection for timeframe 
            self.url_section: project_url,
            self.external_sources_section: {
                self.instructions_section: instructions,
                self.per_task_instructions_section: per_task_instructions,
                self.imagery_section: imagery,
                self.license_section: license
            },
            self.hashtag_section: hashtag_text,
            # self.instructions_section: instructions,
            # self.metrics_section: metrics,
            # self.quality_assurance_section: quality_assurance,
            self.team_user_section: {
                self.users_list_section: project_users
            }
        }
        return project_page_sections

    def create_page(self, document_data: dict) -> None:
        """
        Creates a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        project_wikitext_data = self.generate_page_sections_dict(
            document_data
        )

        updated_text = wiki_obj.generate_page_text_from_dict(
            self.project_page_template,
            f"=={self.page_initial_section}==",
            project_wikitext_data,
            self.users_list_section
        )

        project_page_name = f"{document_data['project']['name']}"

        if wiki_obj.is_existing_page(project_page_name):
            wiki_obj.edit_page(
                token,
                project_page_name,
                updated_text
            )
        else:
            wiki_obj.create_page(
                token,
                project_page_name,
                updated_text
            )
    def edit_page(self, document_data: dict):
        """
        Edits a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        project_wikitext_data = self.generate_page_sections_dict(
            document_data
        )

        updated_text = wiki_obj.generate_page_text_from_dict(
            self.project_page_template,
            f"=={self.page_initial_section}==",
            project_wikitext_data,
            self.users_list_section
        )

        project_page_name = f"{document_data['project']['name']}"

        wiki_obj.edit_page(
            token,
            project_page_name,
            updated_text
        )


    def parse_page_to_serializer(self, page_dictionary: dict):
        """
        """
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        page_dictionary["project"] = (
            page_dictionary[self.project_section]
        )

        page_dictionary["project"]["shortDescription"] = (
            page_dictionary[self.project_section][self.short_description_section]
                           .replace("\n", "")
        )
        
        project_created_date = re.search(
            r"\d{2}\s\w+\s\d{4}",
            page_dictionary[self.project_section][self.timeframe_section]
                           .replace("\n", "")
        )
        parsed_created_date = datetime.strptime(
            project_created_date.group(),
            "%m %B %Y"
        ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        page_dictionary["project"]["created"] = (
            parsed_created_date
        )
        page_dictionary["project"]["url"] = (
            page_dictionary[self.project_section][self.url_section]
                           .replace("\n", "")
        )
        page_dictionary["project"]["projectId"] = (
            int(page_dictionary[self.project_section][self.url_section]
                           .replace("\n", "")
                           .split("/projects/")[-1])
        )
        page_dictionary["project"]["changesetComment"] = (
            "#" + page_dictionary[self.project_section][self.hashtag_section]
                           .replace("\n", "").split("</nowiki>")[-1]
        )

        del page_dictionary[self.project_section]
        del page_dictionary["project"][self.short_description_section]
        del page_dictionary["project"][self.timeframe_section]
        del page_dictionary["project"][self.url_section]
        del page_dictionary["project"][self.hashtag_section]
        
        
        page_dictionary["project"]["externalSource"] = (
            page_dictionary[self.external_sources_section]
        )
        page_dictionary["project"]["externalSource"]["instructions"] = (
            page_dictionary["project"]
                           ["externalSource"]
                           [self.instructions_section]
                           .replace("\n", "")
        )
        page_dictionary["project"]["externalSource"]["perTaskInstructions"] = (
            page_dictionary["project"]
                           ["externalSource"]
                           [self.per_task_instructions_section]
                           .replace("\n", "")
        )
        page_dictionary["project"]["externalSource"]["imagery"] = (
            page_dictionary["project"]
                           ["externalSource"]
                           [self.imagery_section]
                           .replace("\n", "")
        )
        page_dictionary["project"]["externalSource"]["license"] = (
            page_dictionary["project"]
                           ["externalSource"]
                           [self.license_section]
                           .replace("\n", "")
        )
        
        project_dict = page_dictionary["project"]
        del page_dictionary[self.external_sources_section]
        del project_dict["externalSource"][self.instructions_section]
        del project_dict["externalSource"][self.per_task_instructions_section]
        del project_dict["externalSource"][self.imagery_section]
        del project_dict["externalSource"][self.license_section]

        users_list_text = page_dictionary[self.team_user_section][self.users_list_section]
        users_list_table = wtp.parse(users_list_text).get_tables()[0]
        users_list_data = users_list_table.data(span=False)
        users_dict = {}
        users_list = []

        for table_row_number, table_row_data in enumerate(users_list_data[1:], start=1):
            user_id_column = 0
            user_name_column = 1

            users_dict["userId"] = users_list_table.cells(
                row=table_row_number,
                column=user_id_column
            ).value

            users_dict["userName"] =  users_list_table.cells(
                row=table_row_number,
                column=user_name_column
            ).value
            users_list.append(users_dict)

        page_dictionary["project"]["users"] = users_list
        del page_dictionary[self.team_user_section]

        # validate
        project_page_fields = self.get_page_fields()
        document_schema = DocumentSchema(
            partial=True,
            only=project_page_fields
        )
        document = (
            document_schema.load(page_dictionary)
        )
        return page_dictionary
