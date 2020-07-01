from server.services.wiki_service import (
    WikiService
)
from server.services.templates import (
    OverviewPage
)
from server.services.wiki_page_service import WikiPageService


class OverviewPageService(WikiPageService):
    def filter_page_data(self, document_data: dict) -> dict:
        """
        Filter required data for the overview page from
        document data

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        overview_page_data -- Dict containing only the required data
                              for the overview page
        """
        organisation_name = (
            document_data["organisation"]["name"]
        )
        organisation_url = (
            document_data["organisation"]["url"]
        )
        platform_name = document_data["platform"]["name"]
        platform_url = document_data["platform"]["url"]
        overview_page_data = {
            "organisation": {
                "name": organisation_name,
                "url": organisation_url
            },
            "platform": {
                "name": platform_name,
                "url": platform_url
            }
        }
        return overview_page_data

    def get_page_fields(self) -> list:
        """
        Get all required fields for the overview page

        Returns:
        list -- List containing all required fields
                for the overview page
        """
        overview_page_fields = [
            'organisation.name', 'organisation.url',
            'platform.name', 'platform.url'
        ]
        return overview_page_fields

    def generate_page_sections_dict(self, overview_page_data: dict) -> dict:
        """
        Generate dict containing the document content parsed to wikitext
        for all sections present in the overview page

        Keyword arguments:
        overview_page_data -- Dictionary containing the required data for the
                              overview page sections

        Returns:
        overview_page_sections -- Dictionary with the document content
                                  parsed to wikitext for the overview
                                  page sections
        """
        new_row = self.generate_activities_list_table_row(
            overview_page_data
        )
        activities_list_section = (
            OverviewPage.ACTIVITIES_LIST_SECTION_TITLE.value
        )

        overview_page_sections = {
            activities_list_section: new_row
        }
        return overview_page_sections

    def generate_activities_list_table_row(self,
                                           overview_page_data: dict) -> str:
        """
        Generates a new table row for activities list table

        overview_page_data -- Dict containing only the required data
                              for the overview page

        Returns:
        new_row -- String in wikitext format for a new table row
        """
        wiki_obj = WikiService()

        organisation_name = overview_page_data["organisation"]["name"]
        organisation_page_path = (
            f"{OverviewPage.PATH.value}/"
            f"{organisation_name}"
        )

        organisation_link = wiki_obj.hyperlink_wiki_page(
            organisation_page_path,
            organisation_name
        )

        platform_link = wiki_obj.hyperlink_external_link(
            overview_page_data["platform"]["name"],
            overview_page_data["platform"]["url"]
        )

        new_row = (
            f"\n| {organisation_link}\n| {platform_link}\n|-"
        )
        return new_row

    def create_page(self, document_data: dict) -> None:
        """
        Creates a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        # OK
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        overview_page_sections = self.document_to_page_sections(
            document_data
        )
        activities_list_section = (
            OverviewPage.ACTIVITIES_LIST_SECTION_TITLE.value
        )
        new_row = overview_page_sections[activities_list_section]
        page_title = OverviewPage.PATH.value

        if wiki_obj.is_existing_page(page_title):
            page_text = wiki_obj.get_page_text(page_title)
            updated_page_text = wiki_obj.edit_page_with_table(
                page_text,
                activities_list_section,
                new_row
            )
            wiki_obj.edit_page(token, page_title, updated_page_text)
        else:
            page_text = (
                f"={activities_list_section}=\n"
                f"{OverviewPage.ACTIVITIES_LIST_TABLE.value}"
            )
            updated_page_text = wiki_obj.edit_page_with_table(
                page_text,
                activities_list_section,
                new_row
            )

            wiki_obj.create_page(
                token, page_title, updated_page_text
            )
