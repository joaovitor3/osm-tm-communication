from enum import Enum


class OverviewPage(Enum):
    ACTIVITIES_LIST_SECTION_TITLE = "Activities list"
    ACTIVITIES_LIST_TABLE = (
        "{|class='wikitable sortable'\n"
        "|-\n"
        '! scope="col" | Organisation\n'
        '! scope="col" | Organiser\n'
        '|-\n'
        '|}\n'
    )
    PATH = "Organised_Editing/Activities"


class OrgActivityPage(Enum):
    PAGE_TEMPLATE = (
        "= Activity =\n"
        "== Organisation ==\n"
        "=== Link ===\n"
        "=== Description ===\n"
        "== Platform ==\n"
        "=== Link ===\n"
        "== Projects ==\n"
        "=== Project list ===\n"
        "{|class='wikitable sortable'\n"
        "|-\n"
        '! scope="col" | Name\n'
        '! scope="col" | Platform\n'
        '! scope="col" | Project Manager or Team\n'
        '! scope="col" | Status\n'
        "|-\n"
        "|}\n"
    )
    ORGANISATION_SECTION = "Organisation"
    PLATFORM_SECTION = "Platform"
    ORGANISATION_LINK_SECTION = "Link"
    ORGANISATION_DESCRIPTION_SECTION = "Description"
    PLATFORM_LINK_SECTION = "Link"
    PROJECT_LIST_SECTION = "Project list"
    PROJECT_SECTION = "== Projects =="
    ACTIVITY_SECTION = "= Activity ="


class ProjectPage(Enum):
    PAGE_TEMPLATE = (
        "= Project =\n"
        "=== Short Description ===\n"
        "=== Timeframe ===\n"
        "=== Url ===\n"
        "=== Tools ===\n"
        "==== Default tools ====\n"
        "==== External Sources ====\n"
        "=== Standard changeset comment ===\n"
        "==== Hashtag ====\n"
        "=== Instructions ===\n"
        "=== Metrics ===\n"
        "=== Quality assurance ===\n"
        "= Team and User =\n"
        "=== List of Users ===\n"
        '{|class="wikitable sortable"\n'
        "|-\n"
        '! scope="col" | OSM ID\n'
        '! scope="col" | Name\n'
        "|-\n"
        "|}\n"
    )
    PROJECT_SECTION = "= Project ="
    SHORT_DESCRIPTION_SECTION = "Short Description"
    TIMEFRAME_SECTION = "Timeframe"
    URL_SECTION = "Url"
    TOOLS_SECTION = "Tools"
    DEFAULT_TOOLS_SECTION = "=Default tools"
    EXTERNAL_SOURCES_SECTION = "=External sources"
    STANDARD_CHANGESET_COMMENT_SECTION = "Standard changeset comment"
    HASHTAG_SECTION = "Hashtag"
    INSTRUCTIONS_SECTION = "Instructions"
    METRICS_SECTION = "Metrics"
    QUALITY_ASSURANCE_SECTION = "Quality assurance"
    TEAM_AND_USER_SECTION = "= Team and User ="
    USERS_LIST_SECTION = "List of Users"

    STANDARD_TOOLS = "Standard TM Projects"
