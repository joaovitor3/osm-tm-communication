from server.services.wiki_service import (
    WikiService
)
from server.services.templates import (
    ProjectPage
)


class ProjectPageService:
    def __init__(self, project_data):
        self.project_data = project_data

    @staticmethod
    def parse_project_data(complete_data):
        title = (
            complete_data["project"]["title"]
        )
        goal = (
            complete_data["project"]["goal"]
        )
        created = (
            complete_data["project"]["created"]
        )
        due_date = (
            complete_data["project"]["dueDate"]
        )
        changeset_comment = (
            complete_data["project"]["changesetComment"]
        )
        instructions = (
            complete_data["project"]["instructions"]
        )
        # tools = (
        #     complete_data["project"]["tools"]
        # )
        external_source = (
            complete_data["project"]["externalSource"]
        )
        link = (
            complete_data["project"]["link"]
        )
        metrics = (
            complete_data["organiser"]["metrics"]
        )
        quality_assurance = (
            complete_data["organiser"]["qualityAssurance"]
        )
        users = (
            complete_data["project"]["users"]
        )
        project_data = {
            "title": title,
            "goal": goal,
            "created": created,
            "due_date": due_date,
            "changeset_comment": changeset_comment,
            "instructions": instructions,
            "external_source": external_source,
            "link": link,
            "metrics": metrics,
            "quality_assurance": quality_assurance,
            "users": users
        }
        return project_data

    def build_wikitext_data(self):
        wiki_obj = WikiService()

        goal = (
            f"\n{self.project_data.goal}\n"
        )

        created_date = wiki_obj.format_date_text(
            self.project_data.created
        )
        due_date = wiki_obj.format_date_text(
            self.project_data.due_date
        )
        timeframe = (
            f"\n* '''Start Date:''' {created_date}\n"
            f"\n* '''End Date:''' Estimate {due_date}\n"
        )

        project_link = (
            f"\n{self.project_data.link}\n"
        )

        external_source = (
            f"\n{self.project_data.external_source}\n"
        )

        hashtag = (
            self.project_data.changeset_comment
        )
        hashtag = (
            self.project_data.changeset_comment.replace(
                "#", "<nowiki>#</nowiki>"
            )
        )
        hashtag_text = (
            f"\n{hashtag}\n"
        )

        instructions = (
            f"\n{self.project_data.instructions}\n"
        )

        metrics = (
            f"\n* {self.project_data.instructions}\n"
        )
        quality_assurance = (
            f"\n* {self.project_data.quality_assurance}\n"
        )

        users = self.project_data.users
        project_users = ""
        for user in users:
            osm_id = user["osmId"]
            username = user["username"]
            project_users += (
                f"\n| {osm_id}\n| {username}\n|-"
            )

        goal_section = ProjectPage.GOAL_SECTION.value
        timeframe_section = ProjectPage.TIMEFRAME_SECTION.value
        link_section = ProjectPage.LINK_SECTION.value
        external_sources_section = ProjectPage.EXTERNAL_SOURCES_SECTION.value
        hashtag_section = (
            ProjectPage.HASHTAG_SECTION.value
        )
        instructions_section = ProjectPage.INSTRUCTIONS_SECTION.value
        metrics_section = ProjectPage.METRICS_SECTION.value
        quality_assurance_section = (
            ProjectPage.QUALITY_ASSURANCE_SECTION.value
        )
        users_list_section = ProjectPage.USERS_LIST_SECTION.value

        project_page_data = {
            goal_section: goal,
            timeframe_section: timeframe,
            link_section: project_link,
            external_sources_section: external_source,
            hashtag_section: hashtag_text,
            instructions_section: instructions,
            metrics_section: metrics,
            quality_assurance_section: quality_assurance,
            users_list_section: project_users
        }
        return project_page_data
