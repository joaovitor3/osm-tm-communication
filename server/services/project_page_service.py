from server.services.wiki_service import (
    WikiService
)
from server.services.templates import (
    ProjectPage
)
from server.services.wiki_page_service import WikiPageService


class ProjectPageService(WikiPageService):
    def __init__(self):
        self.short_description_section = (
            ProjectPage.SHORT_DESCRIPTION_SECTION
                       .value
        )
        self.timeframe_section = ProjectPage.TIMEFRAME_SECTION.value
        self.url_section = ProjectPage.URL_SECTION.value
        self.external_sources_section = (
            ProjectPage.EXTERNAL_SOURCES_SECTION
                       .value
        )
        self.hashtag_section = (
            ProjectPage.HASHTAG_SECTION.value
        )
        self.instructions_section = ProjectPage.INSTRUCTIONS_SECTION.value
        self.metrics_section = ProjectPage.METRICS_SECTION.value
        self.quality_assurance_section = (
            ProjectPage.QUALITY_ASSURANCE_SECTION.value
        )
        self.users_list_section = ProjectPage.USERS_LIST_SECTION.value
        self.project_page_template = ProjectPage.PAGE_TEMPLATE.value
        self.page_initial_section = (
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
            'project.external_source.license',
            'project.url', 'project.users'
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
            f"\n{project_page_data['project']['short_description']}\n"
        )

        created_date = wiki_obj.format_date_text(
            project_page_data['project']['created']
        )
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

        external_source = (
            f"\n{project_page_data['project']['external_source']}\n"
        )

        hashtag = (
            project_page_data['project']['changeset_comment']
        )
        hashtag = (
            project_page_data['project']['changeset_comment'].replace(
                "#", "<nowiki>#</nowiki>"
            )
        )
        hashtag_text = (
            f"\n{hashtag}\n"
        )

        instructions_text = (
            project_page_data['project']
                             ['external_source']
                             ['instructions']
        )
        instructions = (
            f"\n{instructions_text}\n"
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
                f"\n| {user['user_id']}\n| {user['user_name']}\n|-"
            )

        project_page_sections = {
            self.short_description_section: short_description,
            self.timeframe_section: timeframe,
            self.url_section: project_url,
            self.external_sources_section: external_source,
            self.hashtag_section: hashtag_text,
            self.instructions_section: instructions,
            # self.metrics_section: metrics,
            # self.quality_assurance_section: quality_assurance,
            self.users_list_section: project_users
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

        project_wikitext_data = self.document_to_page_sections(
            document_data
        )
        new_row = project_wikitext_data[self.users_list_section]

        updated_text = wiki_obj.update_table_page_from_dict(
            self.project_page_template,
            self.page_initial_section,
            project_wikitext_data,
            self.users_list_section,
            self.team_user_section
        )

        updated_page_text = wiki_obj.edit_page_with_table(
            updated_text,
            self.users_list_section,
            new_row
        )
        project_page_name = f"{document_data['project']['name']}"

        wiki_obj.create_page(token, project_page_name, updated_page_text)
