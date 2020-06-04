import base64
import yaml
import datetime
from server.services.wikitext_service import (
    WikiTextService
)
from server.models.postgres.task_manager import TaskManager
from server.services.templates import (
    OverviewPage,
    OrganisationActivitiesPage,
    ActivityPage,
    ProjectPage,
    TaskingManagerDefaults
)
from server.models.postgres.organiser import Organiser
from server.models.postgres.utils import NotFound


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
    def update_overview_page(self, task_manager_id):
        wiki_obj = WikiTextService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        title = OverviewPage.PATH.value
        page_text = wiki_obj.get_page_text(title)
        task_manager = TaskManager.get(task_manager_id)

        if task_manager:
            organisation = self.build_organisation_data(task_manager)
            organiser = self.build_organiser_data(task_manager)

            new_row = (
                f"\n| {organisation}\n| {organiser}\n|-"
            )
        else:
            raise NotFound(f"Task Manager id {task_manager_id} not found")

        updated_page_text = wiki_obj.edit_page_with_table(
            page_text,
            OverviewPage.ACTIVITIES_LIST_SECTION_TITLE.value,
            new_row
        )
        edited_page = wiki_obj.edit_page(token, title, updated_page_text)
        return edited_page

    def build_organisation_data(self, task_manager):
        organisation_name = task_manager.name
        organisation_data = (
            f"[[{OverviewPage.PATH.value}/{organisation_name}"
            f"|{organisation_name}]]"
        )
        if organisation_name == OverviewPage.HOT_ORGANISATION_NAME.value:
            organisation_display = (
                OverviewPage.HOT_ORGANISATION_DISPLAY.value
            )
            organisation_data = (
                f"[[{OverviewPage.PATH.value}/{organisation_name}"
                f"|{organisation_display}]]"
            )
        return organisation_data

    def build_organiser_data(self, task_manager):
        organiser_id = task_manager.organiser_id
        organiser = Organiser.get(organiser_id)
        if organiser:
            organiser_name = organiser.name
            organiser_link = organiser.link
            organiser_data = (
                f"[{organiser_link} {organiser_name}]"
            )
        else:
            raise NotFound(f"Organiser id {organiser_id} not found")
        return organiser_data

    def update_orgs_activity_page(self, json_content, task_manager_id):
        wiki_obj = WikiTextService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        title = json_content["organisation"]["name"]
        hashtag = json_content["project"]["changesetComment"]
        hashtag = hashtag.replace("#", "<nowiki>#</nowiki>")
        hashtag_text = (
            f"{hashtag}"
        )

        tools = OrganisationActivitiesPage.DEFAULT_TOOLS.value

        start_date = wiki_obj.format_date_text(datetime.datetime.now())

        task_manager = TaskManager.get(task_manager_id)
        if task_manager:
            organisation_name = task_manager.name
            page_path = f"{OverviewPage.PATH.value}/{organisation_name}"
            page_text = wiki_obj.get_page_text(page_path)
            new_row = (
                f"\n| [[{title}]]\n| {hashtag_text}\n| "
                f"{tools}\n| {start_date}\n|-"
            )
            updated_page_text = wiki_obj.edit_page_with_table(
                page_text,
                OrganisationActivitiesPage.CURRENT_ACTIVITIES.value,
                new_row
            )
            edited_page = wiki_obj.edit_page(
                token,
                page_path,
                updated_page_text
            )
            return edited_page
        else:
            raise NotFound(f"Task Manager id {task_manager_id} not found")

    def create_activity_page(self, json_content, task_manager_id):
        wiki_obj = WikiTextService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        task_manager = TaskManager.get(task_manager_id)
        organisation_name = self.build_organisation_data(task_manager)
        organiser_link = self.build_organiser_data(task_manager)

        activity_name = json_content["organisation"]["name"]
        project_title = json_content["project"]["title"]
        project_name_column = (
            f"[[{activity_name}/{project_title}|{project_title}]]"
        )
        project_manager = json_content["project"]["projectManager"]
        project_status = (
            ActivityPage.DEFAULT_ACTIVE_STATUS.value
        )

        project_list_section = (
            ActivityPage.PROJECT_LIST_SECTION.value
        )
        projects_section = ActivityPage.PROJECTS_SECTION.value

        new_row = (
            f"\n| {project_name_column}\n| {organiser_link}\n| "
            f"{project_manager}\n| {project_status}\n|-"
        )

        name_section = ActivityPage.ORG_NAME_SECTION.value
        description_section = ActivityPage.ORG_DESCRIPTION_SECTION.value
        link_section = ActivityPage.ORG_LINK_SECTION.value

        activity_page_data = {
            name_section: f"\n{organisation_name}\n",
            description_section: "\nExample of description from "
                                 "My Humanitarian mapping\n",
            link_section: f"\n{organiser_link}\n",
            project_list_section: new_row
        }
        updated_text = f"{ActivityPage.ORGANISATION_SECTION.value}\n"

        activity_page_template = ActivityPage.PAGE_TEMPLATE.value
        page_initial_section = (
            ActivityPage.ORGANISATION_SECTION.value
        )

        updated_text = wiki_obj.update_table_page_from_dict(
            activity_page_template,
            page_initial_section,
            activity_page_data,
            project_list_section,
            projects_section
        )
        updated_page_text = wiki_obj.edit_page_with_table(
            updated_text,
            project_list_section,
            new_row
        )
        # create page
        wiki_obj.create_page(token, activity_name, updated_page_text)

    def create_project_page(self, json_content):
        wiki_obj = WikiTextService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        users_list_section = ProjectPage.USERS_LIST_SECTION.value
        team_user_section = ProjectPage.TEAM_AND_USER_SECTION.value

        project_page_data = self.build_project_page_data(json_content)
        new_row = project_page_data[users_list_section]

        project_page_template = ProjectPage.PAGE_TEMPLATE.value
        page_initial_section = (
            ProjectPage.PROJECT_SECTION.value
        )

        updated_text = wiki_obj.update_table_page_from_dict(
            project_page_template,
            page_initial_section,
            project_page_data,
            users_list_section,
            team_user_section
        )

        updated_page_text = wiki_obj.edit_page_with_table(
            updated_text,
            users_list_section,
            new_row
        )
        activity_name = json_content["organisation"]["name"]
        project_title = json_content["project"]["title"]
        project_page_name = f"{activity_name}/{project_title}"
        # create page
        wiki_obj.create_page(token, project_page_name, updated_page_text)

    def build_project_page_data(self, json_content):
        wiki_obj = WikiTextService()

        goal = json_content["project"]["goal"]
        goal_text = (
            f"\n{goal}\n"
        )
        start_date = wiki_obj.format_date_text(datetime.datetime.now())
        end_date = datetime.datetime.strptime(
            json_content["project"]["timeframe"],
            "%d/%m/%Y"
        )
        formatted_end_date = wiki_obj.format_date_text(end_date)
        timeframe = (
            f"\n* '''Start Date:''' {start_date}\n"
            f"\n* '''End Date:''' Estimate {formatted_end_date}\n"
        )

        project_id = json_content["project"]["id"]
        link = f"{TaskingManagerDefaults.WEBSITE.value}/projects"
        project_link = (
            f"\n{link}/{project_id}\n"
        )

        tools = ProjectPage.STANDARD_TOOLS.value
        tools_text = (
            f"\n{tools}\n"
        )

        external_links = (
            json_content["project"]["externalSource"]
        )
        external_links_text = (
            f"\n{external_links}\n"
        )

        hashtag = (
            json_content["project"]["changesetComment"]
        )
        hashtag = hashtag.replace("#", "<nowiki>#</nowiki>")
        hashtag_text = (
            f"\n{hashtag}\n"
        )

        instructions = (
            f"\n* {TaskingManagerDefaults.INSTRUCTIONS.value}\n"
            f"\n* {link}/{project_id}/tasks\n"
        )

        metrics = (
            f"\n* {TaskingManagerDefaults.METRICS.value}\n"
        )
        quality_assurance = (
            f"\n* {TaskingManagerDefaults.QUALITY_ASSURANCE.value}\n"
        )

        users = json_content["project"]["users"]
        project_users = ""
        for user in users:
            osm_id = user["osmId"]
            username = user["username"]
            project_users += (
                f"\n| {osm_id}\n| {username}\n|-"
            )
        # project_section = ProjectPage.PROJECT_SECTION.value
        goal_section = ProjectPage.GOAL_SECTION.value
        timeframe_section = ProjectPage.TIMEFRAME_SECTION.value
        link_section = ProjectPage.LINK_SECTION.value
        # tools_section = ProjectPage.TOOLS_SECTION.value
        default_tools_section = ProjectPage.DEFAULT_TOOLS_SECTION.value
        external_sources_section = ProjectPage.EXTERNAL_SOURCES_SECTION.value
        # std_changeset_section = (
        #     ProjectPage.STANDARD_CHANGESET_COMMENT_SECTION.value
        # )
        hashtag_section = (
            ProjectPage.HASHTAG_SECTION.value
        )
        instructions_section = ProjectPage.INSTRUCTIONS_SECTION.value
        metrics_section = ProjectPage.METRICS_SECTION.value
        quality_assurance_section = (
            ProjectPage.QUALITY_ASSURANCE_SECTION.value
        )
        # team_user_section = ProjectPage.TEAM_AND_USER_SECTION.value
        users_list_section = ProjectPage.USERS_LIST_SECTION.value

        project_page_data = {
            goal_section: goal_text,
            timeframe_section: timeframe,
            link_section: project_link,
            default_tools_section: tools_text,
            external_sources_section: external_links_text,
            hashtag_section: hashtag_text,
            instructions_section: instructions,
            metrics_section: metrics,
            quality_assurance_section: quality_assurance,
            users_list_section: project_users
        }
        return project_page_data
