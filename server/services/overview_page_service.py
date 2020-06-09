from server.services.wiki_service import (
    WikiService
)
from server.services.templates import (
    OverviewPage
)


class OverviewPageService:
    def __init__(self, overview_data):
        self.overview_data = overview_data

    @staticmethod
    def parse_overview_data(complete_data):
        organisation_name = (
            complete_data["organisation"]["name"]
        )
        organisation_link = (
            complete_data["organisation"]["link"]
        )
        organiser_name = complete_data["organiser"]["name"]
        organiser_link = complete_data["organiser"]["link"]
        overview_data = {
            "organisation_name": organisation_name,
            "organisation_link": organisation_link,
            "organiser_name": organiser_name,
            "organiser_link": organiser_link
        }
        return overview_data

    def build_wikitext_data(self):
        wiki_obj = WikiService()

        organisation_page_path = (
            f"{OverviewPage.PATH.value}/"
            f"{self.overview_data.organisation_name}"
        )

        organisation_link = wiki_obj.hyperlink_wiki_page(
            organisation_page_path,
            self.overview_data.organisation_name
        )

        organiser_link = wiki_obj.hyperlink_external_link(
            self.overview_data.organiser_name,
            self.overview_data.organiser_link
        )

        new_row = (
            f"\n| {organisation_link}\n| {organiser_link}\n|-"
        )

        activities_list_section = (
            OverviewPage.ACTIVITIES_LIST_SECTION_TITLE.value
        )

        overview_page_data = {
            activities_list_section: new_row
        }
        return overview_page_data
