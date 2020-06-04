import requests
from server.constants import (
    WIKI_API_ENDPOINT,
    BOT_NAME,
    BOT_PASSWORD
)
import re
import wikitextparser as wtp
from server.services.utils import (
    InvalidMediaWikiToken,
    PageNotFoundError,
    ExistingPageError
)


class WikiTextService:
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
            url=self.endpoint,
            params=params,
            data={
                "token": token,
                "text": str(page_text)
            }
        )
        data = r.json()
        if ("error" in list(data.keys()) and
           data["error"]["code"] == "articleexists"):
            raise ExistingPageError("The page you specified already exist")
        else:
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
            url=self.endpoint,
            params=params,
            data={
                "token": token,
                "text": str(page_text)
            }
        )
        data = r.json()
        if ("error" in list(data.keys()) and
           data["error"]["code"] == "missingtitle"):
            raise PageNotFoundError("The page you specified doesn't exist")
        else:
            return data

    def check_token(self, token):
        params = {"action": "checktoken", "type": "csrf", "format": "json"}
        r = self.session.post(
            url=self.endpoint, params=params, data={"token": token}
        )
        data = r.json()
        if data["checktoken"]["result"] == "invalid":
            raise InvalidMediaWikiToken("Invalid MediaWiki API Token")
        else:
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
            'action': "login",
            'lgname': BOT_NAME,
            'format': "json"
        }
        r = self.session.post(
            url=self.endpoint,
            params=params_login,
            data={
                'lgpassword': BOT_PASSWORD,
                'lgtoken': login_token
            }
        )
        r.raise_for_status()

    def format_date_text(self, date):
        date_month = date.strftime("%B")
        date_day = date.strftime("%m")
        date_year = date.strftime("%Y")

        text_date = f"{date_day} {date_month} {date_year}"
        return text_date

    def get_section_index(self, text, section_title):
        parsed = wtp.parse(text)
        parsed_sections = parsed.sections
        for index, section in enumerate(parsed_sections):
            if (section.title is not None and
               section.title.strip() == section_title):
                return index
        # in case of index 0 comparison could be false
        return False

    def edit_page_with_table(self, text, table_section, new_row, row_number=0):
        parsed_text = wtp.parse(text)
        table = self.get_section_table(
            text,
            parsed_text,
            table_section
        )
        str_index_new_row = self.get_new_row_index(table, row_number)

        parsed_text = self.update_table_page_source(
            parsed_text,
            new_row,
            table,
            str_index_new_row
        )
        return parsed_text

    def get_section_table(self, text, parsed_text, section_title):
        section = self.get_section_index(
            text,
            section_title
        )
        parsed_sections = parsed_text.sections
        table = (
            parsed_sections[section]
            .get_tables()[0]
        )
        return table

    def get_new_row_index(self, table, row_number=0):
        table_column_numbers = self.get_table_column_numbers(table)
        last_column_name = self.get_last_column_data(
            table,
            table_column_numbers,
            row_number
        )

        str_index_end_header = (
            re.search(last_column_name, str(table)).span()[1]
        )
        header_delimiter = "|-\n"
        str_index_new_row = str_index_end_header + len(header_delimiter)
        return str_index_new_row

    def get_last_column_data(self, table, table_column_numbers, row_number=0):
        # because indexing starts at 0
        last_column_header_index = table_column_numbers - 1
        last_column_header_data = str(
            table.cells(row=row_number, column=last_column_header_index)
        )
        last_column_name = last_column_header_data.partition("|")[-1]
        return last_column_name

    def update_table_page_source(self, parsed_text, new_row,
                                 table, str_index_new_row):
        parsed_string = str(parsed_text)
        table_string = str(table)

        updated_table = (
            table_string[:str_index_new_row] +
            new_row + table_string[str_index_new_row:]
        )

        text_before_table_index = parsed_string.find(table_string)

        parsed_text.string = (
            parsed_string[0:text_before_table_index] + updated_table
        )
        return parsed_text

    def get_table_column_numbers(self, table):
        table_column_data = table.data(span=False)
        table_header = table_column_data[0]
        table_column_numbers = len(table_header)
        return table_column_numbers

    def update_table_page_from_dict(self, template_text,
                                    page_initial_section,
                                    page_data,
                                    table_section,
                                    table_parent):
        parsed_text = wtp.parse(template_text)
        parsed_string = str(parsed_text)
        parsed_sections = parsed_text.sections
        updated_text = f"{page_initial_section}\n"

        for section in parsed_sections:
            if (section.title is not None and
               section.title.strip() in list(page_data.keys())):
                section_title_string = (
                    re.search(
                        f"(=)*({section.title})(=)*",
                        parsed_string
                    )
                )
                start_index = section_title_string.span()[0]
                end_index = section_title_string.span()[1]
                if section.title.strip() != table_section:
                    updated_text += (
                        parsed_string[start_index:end_index] +
                        page_data[section.title.strip()]
                    )
                else:
                    updated_text += f"{table_parent}\n{section.string}"
        return updated_text
