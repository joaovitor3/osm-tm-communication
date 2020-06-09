from server.services.wiki_service import (
    WikiService
)
from server.services.templates import (
    OrgActivityPage
)


class OrganisationPageService:
    def __init__(self, organisation_data):
        self.organisation_data = organisation_data

    @staticmethod
    def parse_organisation_data(complete_data):
        name = (
            complete_data["organisation"]["name"]
        )
        description = (
            complete_data["organisation"]["description"]
        )
        link = (
            complete_data["organisation"]["link"]
        )
        project_title = complete_data["project"]["title"]
        project_manager = complete_data["project"]["projectManager"]
        project_status = complete_data["project"]["status"]
        organiser_name = complete_data["organiser"]["name"]
        organiser_link = complete_data["organiser"]["link"]
        organisation_data = {
            "name": name,
            "description": description,
            "link": link,
            "project_title": project_title,
            "project_manager": project_manager,
            "project_status": project_status,
            "organiser_name": organiser_name,
            "organiser_link": organiser_link
        }
        return organisation_data

    def build_wikitext_data(self):
        wiki_obj = WikiService()

        organisation_link = wiki_obj.hyperlink_external_link(
            self.organisation_data.name,
            self.organisation_data.link
        )
        # organisation_section = (
        #     OrgActivityPage.ORGANISATION_SECTION.value
        # )

        organisation_link_text = (
            f"\n{organisation_link}\n"
        )

        organisation_description = (
            f"\n{self.organisation_data.description}\n"
        )

        organiser_link = wiki_obj.hyperlink_external_link(
            self.organisation_data.organiser_name,
            self.organisation_data.organiser_link
        )

        # organiser_section = (
        #     OrgActivityPage.ORGANISER_SECTION.value
        # )
        organiser_link_text = (
            f"\n{organiser_link}\n"
        )

        project_title = (
            self.organisation_data.project_title
        )

        project_name = wiki_obj.hyperlink_wiki_page(
            project_title,
            project_title
        )

        project_manager = (
            self.organisation_data.project_manager
        )
        project_status = (
            self.organisation_data.project_status
        )

        new_row = (
            f"\n| {project_name}\n| {organiser_link}\n| "
            f"{project_manager}\n| {project_status}\n|-"
        )

        organisation_link_section = (
            # OrgActivityPage.ORGANISATION_LINK_SECTION.value
            OrgActivityPage.ORGANISATION_SECTION.value
        )
        organisation_description_section = (
            OrgActivityPage.ORGANISATION_DESCRIPTION_SECTION.value
        )
        organiser_link_section = (
            # OrgActivityPage.ORGANISER_LINK_SECTION.value
            OrgActivityPage.ORGANISER_SECTION.value
        )
        project_list_section = (
            OrgActivityPage.PROJECT_LIST_SECTION.value
        )

        orgs_activity_data = {
            organisation_link_section: organisation_link_text,
            organisation_description_section: (
                organisation_description
            ),
            organiser_link_section: organiser_link_text,
            project_list_section: new_row
        }
        return orgs_activity_data
