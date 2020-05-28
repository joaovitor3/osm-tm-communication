import os
from enum import Enum

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_COMMITER_NAME = os.getenv("GITHUB_COMMITER_NAME")
GITHUB_COMMITER_EMAIL = os.getenv("GITHUB_COMMITER_EMAIL")
GITHUB_API_ENDPOINT = "https://api.github.com/"
WIKI_API_ENDPOINT = os.getenv("WIKI_API_ENDPOINT")
BOT_NAME = os.getenv("MEDIAWIKI_BOT_NAME")
BOT_PASSWORD = os.getenv("MEDIAWIKI_BOT_PASSWORD")
HOT_OEG_ACTIVITIES_PAGE = "Organised_Editing/Activities/Humanitarian_OpenStreetMap_Team"
COORDINATION_SECTION = 10

class PageTables(Enum):
    ACTIVITIES_TABLE = 4

class ActivitiesTable(Enum):
    DISASTER_PROJECTS = "Disaster Mapping Projects"
    COMMUNITY_PROJECTS = "Community Mapping Projects"
