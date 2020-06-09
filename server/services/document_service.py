import base64
import yaml
from server.services.wiki_service import (
    WikiService
)
from server.services.project_page_service import (
    ProjectPageService
)
from server.services.organisation_page_service import (
    OrganisationPageService
)
from server.services.overview_page_service import (
    OverviewPageService
)
from server.services.templates import (
    OverviewPage,
    ProjectPage,
    OrgActivityPage
)
from server.models.serializers.project_page import (
    ProjectPageSerializer
)
from server.models.serializers.organisation_page import (
    OrganisationPageSerializer
)
from server.models.serializers.overview_page import (
    OverviewPageSerializer
)


class DocumentService:
    @staticmethod
    def json_to_bytes_encoded_yaml(json):
        document_yaml = yaml.dump(json, allow_unicode=True)
        encoded_yaml = base64.b64encode(bytes(document_yaml, 'utf-8'))
        return encoded_yaml

    @staticmethod
    def bytes_encoded_yaml_to_dict(encoded_yaml):
        decoded_yaml = base64.b64decode(encoded_yaml).decode('utf-8')
        dict_from_yaml = yaml.load(decoded_yaml, Loader=yaml.FullLoader)
        return dict_from_yaml


class WikiDocumentService:
    def update_overview_page(self, json_content):
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        overview_data = OverviewPageService.parse_overview_data(json_content)
        serialized_overview_page = OverviewPageSerializer(overview_data)
        serialized_overview_page.validate()

        overview_page = OverviewPageService(
            serialized_overview_page
        )
        overview_wikitext_data = (
            overview_page.build_wikitext_data()
        )

        activities_list_section = (
            OverviewPage.ACTIVITIES_LIST_SECTION_TITLE.value
        )
        new_row = overview_wikitext_data[activities_list_section]

        title = OverviewPage.PATH.value
        page_text = wiki_obj.get_page_text(title)
        updated_page_text = wiki_obj.edit_page_with_table(
            page_text,
            activities_list_section,
            new_row
        )
        wiki_obj.edit_page(token, title, updated_page_text)

    def update_orgs_activity_page(self, json_content):
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        organisation_data = (
            OrganisationPageService.parse_organisation_data(json_content)
        )
        serialized_organisation_page = (
            OrganisationPageSerializer(organisation_data)
        )
        serialized_organisation_page.validate()

        organisation_page = OrganisationPageService(
            serialized_organisation_page
        )
        organisation_wikitext_data = (
            organisation_page.build_wikitext_data()
        )

        project_page_template = (
            OrgActivityPage.PAGE_TEMPLATE.value
        )

        organisation_name = serialized_organisation_page.name
        page_path = f"{OverviewPage.PATH.value}/{organisation_name}"

        page_initial_section = (
            OrgActivityPage.ACTIVITY_SECTION.value
        )
        projects_list_secton = (
            OrgActivityPage.PROJECT_LIST_SECTION.value
        )
        projects_section = (
            OrgActivityPage.PROJECT_SECTION.value
        )

        updated_text = wiki_obj.update_table_page_from_dict(
            project_page_template,
            page_initial_section,
            organisation_wikitext_data,
            projects_list_secton,
            projects_section
        )

        new_row = organisation_wikitext_data[projects_list_secton]

        updated_page_text = wiki_obj.edit_page_with_table(
            updated_text,
            projects_list_secton,
            new_row
        )

        organisation_link_section = (
            f"{OrgActivityPage.ORGANISATION_LINK_SECTION.value}"
        )
        organisation_parent_section = (
            f"{OrgActivityPage.ORGANISATION_SECTION.value}"
        )
        organisation_section_text = wiki_obj.add_children_section(
            str(updated_page_text),
            organisation_link_section,
            organisation_parent_section
        )

        organiser_link_section = (
            f"{OrgActivityPage.ORGANISER_LINK_SECTION.value}"
        )
        organiser_parent_section = (
            f"{OrgActivityPage.ORGANISER_SECTION.value}"
        )
        organiser_section_text = wiki_obj.add_children_section(
            str(organisation_section_text),
            organiser_link_section,
            organiser_parent_section
        )

        wiki_obj.edit_page(
            token,
            page_path,
            organiser_section_text
        )

    def create_project_page(self, json_content):
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        project_data = ProjectPageService.parse_project_data(json_content)
        serialized_project_page = ProjectPageSerializer(project_data)
        serialized_project_page.validate()
        project_page = ProjectPageService(
            serialized_project_page
        )

        users_list_section = ProjectPage.USERS_LIST_SECTION.value
        team_user_section = ProjectPage.TEAM_AND_USER_SECTION.value

        project_wikitext_data = project_page.build_wikitext_data()
        new_row = project_wikitext_data[users_list_section]

        project_page_template = ProjectPage.PAGE_TEMPLATE.value
        page_initial_section = (
            ProjectPage.PROJECT_SECTION.value
        )

        updated_text = wiki_obj.update_table_page_from_dict(
            project_page_template,
            page_initial_section,
            project_wikitext_data,
            users_list_section,
            team_user_section
        )

        updated_page_text = wiki_obj.edit_page_with_table(
            updated_text,
            users_list_section,
            new_row
        )
        project_page_name = f"{serialized_project_page.title}"

        wiki_obj.create_page(token, project_page_name, updated_page_text)
