from server.services.wiki_service import (
    WikiService
)
from server.services.templates import (
    OrgActivityPage
)
from server.services.templates import (
    OverviewPage
)
from server.services.wiki_page_service import WikiPageService
from flask import current_app
import wikitextparser as wtp
import re
from server.models.serializers.document import (
    DocumentSchema,
    is_known_document_content_type,
    turn_fields_optional
)


class OrganisationPageService(WikiPageService):
    def __init__(self):
        self.organisation_section = (
            OrgActivityPage.ORGANISATION_SECTION.value
        )
        self.organisation_url_section = (
            OrgActivityPage.ORGANISATION_SECTION.value
        )
        self.organisation_description_section = (
            OrgActivityPage.ORGANISATION_DESCRIPTION_SECTION.value
        )
        self.platform_url_section = (
            OrgActivityPage.PLATFORM_SECTION.value
        )
        self.projects_list_section = (
            OrgActivityPage.PROJECT_LIST_SECTION.value
        )
        self.page_initial_section = (
            OrgActivityPage.ACTIVITY_SECTION.value
        )
        self.projects_list_section = (
            OrgActivityPage.PROJECT_LIST_SECTION.value
        )
        self.projects_section = (
            OrgActivityPage.PROJECT_SECTION.value
        )
        self.project_page_template = (
            OrgActivityPage.PAGE_TEMPLATE.value
        )
        self.organisation_link_section = (
            f"{OrgActivityPage.ORGANISATION_LINK_SECTION.value}"
        )
        self.organisation_parent_section = (
            f"{OrgActivityPage.ORGANISATION_SECTION.value}"
        )
        self.platform_link_section = (
            f"{OrgActivityPage.PLATFORM_LINK_SECTION.value}"
        )
        self.platform_section = (
            f"{OrgActivityPage.PLATFORM_SECTION.value}"
        )
    
    def get_organisation_projects(self, organisation_name: str) -> list:
        """
        """
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)
        
        organisation_page = f"{OverviewPage.PATH.value}/{organisation_name}"
        text = wiki_obj.get_page_text(organisation_page)
        table = wiki_obj.get_section_table(text, self.projects_section)
        # ignore table header
        table_data = table.data(span=False)[1:]
        project_names = []
        for row in table_data:
            project_name_column = 0
            # fazer função para extrair texto de um com hyperlink
            extracted_project_name = row[project_name_column].replace("[", "").replace("]", "").split(" | ")[0]
            project_names.append(extracted_project_name)
        return project_names

    def filter_page_data(self, document_data: dict) -> dict:
        """
        Filter required data for the organisation page from
        document data

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        organisation_page_data -- Dict containing only the required data
                              for the organisation page
        """
        name = (
            document_data["organisation"]["name"]
        )
        description = (
            document_data["organisation"]["description"]
        )
        url = (
            document_data["organisation"]["url"]
        )
        project_name = document_data["project"]["name"]
        project_author = document_data["project"]["author"]
        project_status = document_data["project"]["status"]
        platform_name = document_data["platform"]["name"]
        platform_url = document_data["platform"]["url"]
        organisation_page_data = {
            "organisation": {
                "name": name,
                "description": description,
                "url": url,

            },
            "project": {
                "name": project_name,
                "author": project_author,
                "status": project_status
            },
            "platform": {
                "name": platform_name,
                "url": platform_url
            }
        }
        return organisation_page_data

    def get_page_fields(self) -> list:
        organisation_page_fields = [
            'project.name', 'project.author', 'project.status',
            'organisation.name', 'organisation.description',
            'organisation.url', 'platform.name', 'platform.url'
        ]
        return organisation_page_fields

    def generate_page_sections_dict(self,
                                    organisation_page_data: dict) -> dict:
        """
        Generate dict containing the document content
        parsed to wikitext for all sections present
        in the organisation page

        Keyword arguments:
        organisation_page_data -- Dictionary containing the
                                  required data for the
                                  organisation page sections

        Returns:
        organisation_page_sections -- Dictionary with the document
                                      content parsed to wikitext
                                      for the organisation page sections
        """
        wiki_obj = WikiService()

        organisation_url = wiki_obj.hyperlink_external_link(
            organisation_page_data["organisation"]["name"],
            organisation_page_data["organisation"]["url"]
        )

        organisation_url_text = (
            f"\n{organisation_url}\n"
        )

        organisation_description = (
            f"\n{organisation_page_data['organisation']['description']}\n"
        )

        platform_url = wiki_obj.hyperlink_external_link(
            organisation_page_data["platform"]["name"],
            organisation_page_data["platform"]["url"]
        )

        platform_url_text = (
            f"\n{platform_url}\n"
        )

        new_row = self.generate_projects_list_table_row(
            organisation_page_data
        )

        organisation_page_sections = {
            self.organisation_section: {
                self.organisation_link_section: organisation_url_text,
                self.organisation_description_section: organisation_description
            },
            self.platform_section: {
                self.platform_link_section: platform_url_text,
            },
            self.projects_section: {
                self.projects_list_section: new_row
            }
        }
        return organisation_page_sections

    def generate_projects_list_table_row(self,
                                         organisation_page_data: dict) -> str:
        """
        Generates a new table row for projects list table

        organisation_page_data -- Dict containing only the required data
                                  for the organisation page

        Returns:
        new_row -- String in wikitext format for a new table row
        """
        wiki_obj = WikiService()
        platform_url = wiki_obj.hyperlink_external_link(
            organisation_page_data["platform"]["name"],
            organisation_page_data["platform"]["url"]
        )

        project_name = wiki_obj.hyperlink_wiki_page(
            organisation_page_data["project"]["name"],
            organisation_page_data["project"]["name"]
        )

        project_author = (
            organisation_page_data["project"]["author"]
        )
        project_status = (
            organisation_page_data["project"]["status"]
        )

        new_row = (
            f"\n| {project_name}\n| {platform_url}\n| "
            f"{project_author}\n| {project_status}\n|-"
        )
        return new_row

    def create_page(self, document_data: dict):
        """
        Creates a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        organisation_wikitext_data = (
            self.generate_page_sections_dict(document_data)
        )
        organisation_name = document_data["organisation"]["name"]
        page_path = f"{OverviewPage.PATH.value}/{organisation_name}"

        if wiki_obj.is_existing_page(page_path):
            page_text = wiki_obj.get_page_text(page_path)
        else:
            page_text = self.project_page_template

        updated_text = wiki_obj.generate_page_text_from_dict(
            page_text,
            self.page_initial_section,
            organisation_wikitext_data,
            self.projects_list_section
        )
        if wiki_obj.is_existing_page(page_path):
            wiki_obj.edit_page(
                token,
                page_path,
                updated_text
            )
        else:
            wiki_obj.create_page(
                token,
                page_path,
                updated_text
            )

    def is_table_fields_updated(self, update_fields: dict):
        table_fields = {
            "platform": ["name", "url"],
            "project": ["name", "author", "status"]
        }
        for table_field in table_fields.keys():
            if (table_field in update_fields.keys() and
                any((True for table_column in table_fields[table_field] 
                         if table_column in list(update_fields[table_field].keys())))):
               return True
        return False

    def edit_page(self, document_data: dict, update_fields: dict, old_data: dict):
        """
        Edits a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        organisation_wikitext_data = (
            self.generate_page_sections_dict(document_data)
        )
        organisation_name = old_data["organisation"]["name"]
        page_path = f"{OverviewPage.PATH.value}/{organisation_name}"

        page_text = wiki_obj.get_page_text(page_path)
        
        if self.is_table_fields_updated(update_fields):
            # old_data = "dict com dado atual da página que será substituido"
            project_name = wiki_obj.hyperlink_wiki_page(
                old_data["project"]["name"].strip(),
                old_data["project"]["name"].strip()
            )
            updated_text = wiki_obj.generate_page_text_from_dict(
                page_text,
                self.page_initial_section,
                organisation_wikitext_data,
                self.projects_list_section,
                is_edit=True,
                edit_row_column_data=project_name
            )
        else:
            updated_text = wiki_obj.generate_page_text_from_dict(
                page_text,
                self.page_initial_section,
                organisation_wikitext_data,
                self.projects_list_section
            )
        edited_page = wiki_obj.edit_page(
            token,
            page_path,
            updated_text
        )

    def parse_page_to_serializer(self, page_dictionary: dict):
        """
        """
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)


        page_dictionary["organisation"] = (
            page_dictionary[self.organisation_parent_section]
        )
        page_dictionary["organisation"]["description"] = (
            page_dictionary["organisation"]
                           [self.organisation_description_section].replace("\n", "")
        )


        hyperlinked_organisation_url = (
            page_dictionary["organisation"]
                           [self.organisation_link_section]
        )
        organisation_url, organisation_name = (
            hyperlinked_organisation_url.replace("[", "").replace("]", "").replace("\n", "").split(" ", 1)
        )
        page_dictionary["organisation"]["url"] = (
            organisation_url
        )
        page_dictionary["organisation"]["name"] = (
            organisation_name
        )


        del page_dictionary[self.organisation_parent_section]
        del page_dictionary["organisation"][self.organisation_description_section]
        del page_dictionary["organisation"][self.organisation_link_section]

        page_dictionary["platform"] = (
            page_dictionary[self.platform_section]
        )
        hyperlinked_platform_url = (
            page_dictionary["platform"]
                           [self.platform_link_section]
        )
        platform_url, platform_name = (
            hyperlinked_platform_url.replace("[", "").replace("]", "").replace("\n", "").split(" ", 1)
        )
        page_dictionary["platform"]["url"] = (
            platform_url
        )        
        page_dictionary["platform"]["name"] =  platform_name


        del page_dictionary[self.platform_section]
        del page_dictionary["platform"][self.platform_link_section]


        projects_list_text = page_dictionary[self.projects_section][self.projects_list_section]
        projects_list_table = wtp.parse(projects_list_text).get_tables()[0]
        projects_list_data = projects_list_table.data(span=False)
        project_dict = {}


        for table_row_number, table_row_data in enumerate(projects_list_data[1:], start=1):
            project_name_column = 0
            project_author_column = 2
            project_status_column = 3

            project_wiki_page = projects_list_table.cells(
                row=table_row_number,
                column=project_name_column
            ).value
            project_name = project_wiki_page.replace("[", "").replace("\n", "").split(" | ")[0]
            project_dict["name"] = project_name

            project_dict["author"] =  projects_list_table.cells(
                row=table_row_number,
                column=project_author_column
            ).value
            project_dict["status"] =  projects_list_table.cells(
                row=table_row_number,
                column=project_status_column
            ).value

        page_dictionary["project"] = project_dict
        del page_dictionary[self.projects_section]

        # validate
        organisation_page_fields = self.get_page_fields()
        document_schema = DocumentSchema(
            partial=True,
            only=organisation_page_fields
        )
        document = (
            document_schema.load(page_dictionary)
        )

        return page_dictionary