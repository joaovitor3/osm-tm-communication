import base64
import yaml
import requests
import wikitextparser as wtp
from server.constants import (
    WIKI_API_ENDPOINT,
    PageTables,
    ActivitiesTable,
    HOT_OEG_ACTIVITIES_PAGE,
    BOT_NAME,
    BOT_PASSWORD,
    COORDINATION_SECTION
)
import datetime
import re
from server.services.templates import (
    PAGE_TEMPLATE,
    PROJECT_PAGE_HEADER
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
    def __init__(self):
        self.endpoint = WIKI_API_ENDPOINT
        self.session = requests.Session()
        self.login()

    def get_page_text(self, page_title):
        params = {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
        }
        r = self.session.get(url=self.endpoint, params=params)
        
        data = r.json()

        text = data["parse"]["wikitext"]["*"]

        return text


    def create_page(self, token, page_title, page_text):
        params = {
            "action": "edit",
            "title": page_title,
            "createonly": "true",
            "contentmodel": "wikitext",
            "bot": "true",
            "format": "json"
        }
        
        r = self.session.post(
            url=self.endpoint, params=params, data={"token": token,"text": page_text}
        )

        data = r.json()

        return data

    def edit_page(self, token, page_title, page_text):
        params = {
            "action": "edit",
            "title": page_title,
            "nocreate": "true",
            "contentmodel": "wikitext",
            "bot": "true",
            "format": "json"
        }

        r = self.session.post(
            url=self.endpoint, params=params, data={"token": token, "text": str(page_text)}
        )

        data = r.json()

        return data

    def check_token(self, token):
        params = {"action": "checktoken", "type": "csrf", "format": "json"}
        r = self.session.post(
            url=self.endpoint, params=params, data={"token": token}
        )
        data = r.json()
        return data

    def get_token(self):
        params = {"action": "query", "meta": "tokens", "format": "json"}
        r = self.session.get(url=self.endpoint, params=params)

        data = r.json()

        token = data["query"]["tokens"]["csrftoken"]
        return token


    def get_login_token(self):
        params_token = {
            "action": "query",
            "format": "json",
            "meta": "tokens",
            "type": "login"
        }
        r = self.session.get(url=self.endpoint, params=params_token)
        data = r.json()
        login_token = data['query']['tokens']['logintoken']
        return login_token

    def login(self):
        login_token = self.get_login_token()
        params_login = {
            'action':"login",
            'lgname':BOT_NAME,
            'format':"json"
        }
        r = self.session.post(
            url=self.endpoint,
            params=params_login,
            data={
                'lgpassword': BOT_PASSWORD,
                'lgtoken': login_token
            }
        )

    def add_project_table(self, text, json_content, token):
        parsed = wtp.parse(text)
        parsed_sections = parsed.sections

        activity_table = parsed_sections[PageTables.ACTIVITIES_TABLE.value].get_tables()[0]
        updated_table = self.add_table_row(activity_table, json_content)
        parsed.sections[PageTables.ACTIVITIES_TABLE.value].string = updated_table

        edited = self.edit_page(token, HOT_OEG_ACTIVITIES_PAGE, parsed)

    def add_table_row(self, table, json_content):
        table_string = str(table)
        disaster_project_header = f"'''{ActivitiesTable.DISASTER_PROJECTS.value}'''"

        title = json_content["title"]
        contact = json_content["contact"]

        start_date = self.format_date_text(datetime.datetime.now())
        end_datetime = datetime.datetime.strptime(
            json_content["timestamp"],
            "%d/%m/%Y"
        )
        end_date = "Estimate " + self.format_date_text(end_datetime)

        purpose = json_content["purpose"]
        details = json_content["title"].replace(" ", "_")
        hashtag = json_content["changesetComment"]
        tools = json_content["tools"]
        training = json_content["training"]

        new_project_row = (
            f"\n|-\n|{title}||{contact}||{start_date}"
            f"||{end_date}||{purpose}||[[{details}]]||"
            f"{hashtag}||{tools}||{training}"
        )
        index_end_header = re.search(disaster_project_header, table_string).span()[1]
        updated_table = table_string[:index_end_header] + new_project_row + table_string[index_end_header:]
        updated_section = (
            "=== Current Activities ===\n</div>\n" + updated_table +
            '\n<div style="clear:both; background:beige;box-shadow:3px 3px 2px red;padding:0.4em;">\n'
        )
        return updated_section
    
    def update_coordination(self, text, coordinator, page_title, token):
        parsed = wtp.parse(text)
        updated_coordinators = (
            f"=== Coordination ===\n* {coordinator}\n"
        )
        parsed.sections[COORDINATION_SECTION].string = updated_coordinators
        edited = self.edit_page(token, page_title, parsed)

    def format_date_text(self, date):
        date_month = date.strftime("%B")
        date_day = date.strftime("%m")
        date_year = date.strftime("%Y")

        text_date = f"{date_day} {date_month} {date_year}"
        return text_date    

    def format_project_page(self, project_title):
        project_description = (
            f"'''{project_title}''' decription.\n__TOC__\n"
        )
        complete_page = PROJECT_PAGE_HEADER + project_description + PAGE_TEMPLATE
        return complete_page
