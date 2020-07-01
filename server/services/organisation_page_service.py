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


class OrganisationPageService(WikiPageService):
    def __init__(self):
        self.organisation_url_section = (
            # OrgActivityPage.ORGANISATION_url_SECTION.value
            OrgActivityPage.ORGANISATION_SECTION.value
        )
        self.organisation_description_section = (
            OrgActivityPage.ORGANISATION_DESCRIPTION_SECTION.value
        )
        self.platform_url_section = (
            # OrgActivityPage.platform_url_SECTION.value
            OrgActivityPage.PLATFORM_SECTION.value
        )
        self.projects_list_section = (
            OrgActivityPage.PROJECT_LIST_SECTION.value
        )
        self.page_initial_section = (
            OrgActivityPage.ACTIVITY_SECTION.value
        )
        self.projects_list_secton = (
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
        self.platform_parent_section = (
            f"{OrgActivityPage.PLATFORM_SECTION.value}"
        )

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
            self.organisation_url_section: organisation_url_text,
            self.organisation_description_section: (
                organisation_description
            ),
            self.platform_url_section: platform_url_text,
            self.projects_list_section: new_row
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

        updated_text = wiki_obj.update_table_page_from_dict(
            self.project_page_template,
            self.page_initial_section,
            organisation_wikitext_data,
            self.projects_list_secton,
            self.projects_section
        )

        new_row = organisation_wikitext_data[self.projects_list_secton]

        updated_page_text = wiki_obj.edit_page_with_table(
            updated_text,
            self.projects_list_secton,
            new_row
        )

        organisation_section_text = wiki_obj.add_children_section(
            str(updated_page_text),
            self.organisation_link_section,
            self.organisation_parent_section
        )

        platform_section_text = wiki_obj.add_children_section(
            str(organisation_section_text),
            self.platform_link_section,
            self.platform_parent_section
        )

        if wiki_obj.is_existing_page(page_path):
            wiki_obj.edit_page(
                token,
                page_path,
                platform_section_text
            )
        else:
            wiki_obj.create_page(
                token,
                page_path,
                platform_section_text
            )
