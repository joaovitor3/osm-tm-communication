from server.services.wiki_service import (
    WikiService
)
from server.services.templates import (
    OverviewPage
)
from server.services.wiki_page_service import WikiPageService
from flask import current_app
import wikitextparser as wtp
from server.models.serializers.organisation import OrganisationListSchema
from server.models.serializers.platform import PlatformListSchema


class OverviewPageService(WikiPageService):
    def __init__(self):
        self.activities_list_section = (
            OverviewPage.ACTIVITIES_LIST_SECTION_TITLE.value
        )

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
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        overview_page_sections = self.document_to_page_sections(
            document_data
        )
        activities_list_section = (
            OverviewPage.ACTIVITIES_LIST_SECTION_TITLE.value
        )
        page_title = OverviewPage.PATH.value

        if wiki_obj.is_existing_page(page_title):
            page_text = wiki_obj.get_page_text(page_title)
            updated_page_text = wiki_obj.generate_page_text_from_dict(
                page_text,
                "",
                overview_page_sections,
                activities_list_section
            )
            wiki_obj.edit_page(token, page_title, updated_page_text)
        else:
            page_text = (
                f"=={activities_list_section}==\n"
                f"{OverviewPage.ACTIVITIES_LIST_TABLE.value}"
            )
            updated_page_text = wiki_obj.generate_page_text_from_dict(
                page_text,
                "",
                overview_page_sections,
                activities_list_section
            )

            wiki_obj.create_page(
                token, page_title, updated_page_text
            )

    def is_table_fields_updated(self, update_fields: dict):
        table_fields = {
            "platform": ["name", "url"],
            "organisation": ["name", "url"]
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

        overview_page_sections = self.document_to_page_sections(
            document_data
        )
        activities_list_section = (
            OverviewPage.ACTIVITIES_LIST_SECTION_TITLE.value
        )
        page_title = OverviewPage.PATH.value

        overview_page_sections = (
            self.generate_page_sections_dict(document_data)
        )
        page_text = wiki_obj.get_page_text(page_title)
        
        if self.is_table_fields_updated(update_fields):
            organisation_name = old_data["organisation"]["name"].strip()
            organisation_page_path = (
                f"{OverviewPage.PATH.value}/"
                f"{organisation_name}"
            )
            organisation_name = wiki_obj.hyperlink_wiki_page(
                organisation_page_path,
                organisation_name
            )
            updated_text = wiki_obj.generate_page_text_from_dict(
                page_text,
                "",
                overview_page_sections,
                self.activities_list_section,
                is_edit=True,
                edit_row_column_data=organisation_name
            )
        else:
            updated_text = wiki_obj.generate_page_text_from_dict(
                page_text,
                "",
                overview_page_sections,
                self.activities_list_section
            )
        edited_page = wiki_obj.edit_page(
            token,
            page_title,
            updated_text
        )


    def parse_page_to_serializer(self, page_dictionary: dict):
        """
        """
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        overview_page_text = page_dictionary[self.activities_list_section]
        overview_page_table = wtp.parse(overview_page_text).get_tables()[0]
        overview_page_data = overview_page_table.data(span=False)

        page_dictionary["organisation"] = []
        page_dictionary["platform"] = []

        for table_row_number, table_row_data in enumerate(overview_page_data[1:], start=1):
            organisation_column = 0
            platform_column = 1

            hyperlinked_organisation_url = overview_page_table.cells(
                row=table_row_number,
                column=organisation_column
            ).value

            hyperlinked_platform_url = overview_page_table.cells(
                row=table_row_number,
                column=platform_column
            ).value.strip()

            organisation_name = (
                hyperlinked_organisation_url.replace("[", "").replace("]", "")
                                            .replace("\n", "").split(" | ")[1]
            )

            page_dictionary["organisation"].append(
                {
                    "name": organisation_name
                }
            )

            platform_url, platform_name = (
                hyperlinked_platform_url.replace("[", "").replace("]", "").replace("\n", "").split(" ", 1)
            )
            page_dictionary["platform"].append(
                {
                    "name": platform_name,
                    "url": platform_url
                }
            )
        del page_dictionary[self.activities_list_section]

        # validates platform and organisation
        organisation_list_schema = OrganisationListSchema(partial=True)
        organisation = (
            organisation_list_schema.load({"organisation":page_dictionary["organisation"]})
        )

        platform_list_schema = PlatformListSchema()
        platform = (
            platform_list_schema.load({"platform": page_dictionary["platform"]})
        )
        return page_dictionary