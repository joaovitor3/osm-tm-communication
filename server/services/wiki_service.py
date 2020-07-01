import requests
import re
from flask import current_app
import wikitextparser as wtp
import datetime

from server.constants import (
    WIKI_API_ENDPOINT,
    BOT_NAME,
    BOT_PASSWORD
)


class WikiServiceError(Exception):
    """
    Custom Exception to notify callers an error occurred when handling wiki
    """

    def __init__(self, message):
        if current_app:
            current_app.logger.error(message)


class WikiService:
    def __init__(self):
        self.endpoint = WIKI_API_ENDPOINT
        self.session = requests.Session()
        self.login()

    def get_page_text(self, page_title: str) -> str:
        """
        Get the page content of a page parsed as Wikitext

        Keyword arguments:
        page_title -- The title of the page

        Returns:
        text -- The text of the page
        """
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

    def is_existing_page(self, page_title: str) -> str:
        """
        Get the page content of a page parsed as Wikitext

        Keyword arguments:
        page_title -- The title of the page

        Returns:
        text -- The text of the page
        """
        params = {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
        }
        r = self.session.get(url=self.endpoint, params=params)
        data = r.json()
        if ("error" in list(data.keys()) and
           data["error"]["code"] == "missingtitle"):
            return False
        else:
            return True

    def create_page(self, token: str, page_title: str, page_text: str) -> dict:
        """
        Create a new wiki page

        Keyword arguments:
        token -- The MediaWiki API token
        page_title -- The title of the page being created
        page_text -- The text of the page being created

        Raises:
        WikiServiceError -- Exception raised when handling wiki

        Returns:
        data -- Dictionary with result of post request for creating
                the page
        """
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
            raise WikiServiceError("The page you specified already exist")
        else:
            return data

    def edit_page(self, token: str, page_title: str, page_text: str) -> dict:
        """
        Edit a existing wiki page

        Keyword arguments:
        token -- The MediaWiki API token
        page_title -- The title of the page being created
        page_text -- The text of the page being created

        Raises:
        WikiServiceError -- Exception raised when handling wiki

        Returns:
        data -- Dictionary with result of post request for creating
                the page
        """
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
            raise WikiServiceError("The page you specified doesn't exist")
        else:
            return data

    def check_token(self, token: str) -> dict:
        """
        Check if MediaWiki API Token is valid

        Keyword arguments:
        token -- The MediaWiki API token

        Raises:
        WikiServiceError -- Exception raised when handling wiki

        Returns:
        data -- Dictionary with result of post request for checking
                the MediaWiki API Token
        """
        params = {"action": "checktoken", "type": "csrf", "format": "json"}
        r = self.session.post(
            url=self.endpoint, params=params, data={"token": token}
        )
        data = r.json()
        if data["checktoken"]["result"] == "invalid":
            raise WikiServiceError("Invalid MediaWiki API Token")
        else:
            return data

    def get_token(self) -> str:
        """
        Get MediaWiki API Token for an active Session

        Returns:
        token -- MediaWiki API Token for an active Session
        """
        params = {"action": "query", "meta": "tokens", "format": "json"}
        r = self.session.get(url=self.endpoint, params=params)
        data = r.json()
        token = data["query"]["tokens"]["csrftoken"]
        return token

    def generate_login_token(self) -> str:
        """
        Generate Login Token for MediaWiki API

        Returns:
        token -- Login Token for MediaWiki API
        """
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
        """
        Login into MediaWiki API
        """
        login_token = self.generate_login_token()
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

    def format_date_text(self, date: datetime) -> str:
        """
        Format a date into the format "%dd month_name %YYYY"

        Keyword arguments:
        date -- Date being formatted

        Returns:
        text_date -- Dictionary with result of post request for checking
                the MediaWiki API Token
        """
        date_month = date.strftime("%B")
        date_day = date.strftime("%m")
        date_year = date.strftime("%Y")

        text_date = f"{date_day} {date_month} {date_year}"
        return text_date

    def get_section_index(self, text: str, section_title: str) -> int:
        """
        Get the index of a section in a wiki page

        Keyword arguments:
        text -- The text of a wiki page
        section_title -- the title of the section
                         in which the index is searched

        Raises:
        WikiServiceError -- Exception raised when handling wiki

        Returns:
        index -- The index of the section
        """
        parsed = wtp.parse(text)
        parsed_sections = parsed.sections
        for index, section in enumerate(parsed_sections):
            if (section.title is not None and
               section.title.strip() == section_title):
                return index
        raise WikiServiceError("The section you specified doesn't exist")

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

    def get_section_table(self, text: str, parsed_text: str,
                          section_title) -> wtp.Table:
        """
        Get the first table of a section in a wiki page

        Keyword arguments:
        text -- The text of a wiki page
        section_title -- the title of the section
                         in which the index is searched

        Raises:
        WikiServiceError -- Exception raised when handling wiki

        Returns:
        index -- The index of the section
        """
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
        """
        Returns the position of the string where the new
        table row will be added
        """
        table_column_numbers = self.get_table_column_numbers(table, row_number)
        last_column_name = self.get_table_last_column_data(
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

    def get_table_last_column_data(self, table: wtp.Table,
                                   table_column_numbers: int,
                                   row_number: int = 0) -> str:
        """
        Returns data from the last column of a table row

        Keyword arguments:
        table -- The table which the data is
                 being searched
        table_column_numbers -- The number of columns of
                                the table
        row_number -- The row number of the table which
                      the data is being searched

        Returns:
        table_last_column_data -- Data from the last column
                                  of a table row
        """
        # because indexing starts at 0 (moved to method to get col numbers)
        # table_last_column_index = table_column_numbers - 1
        table_last_column_data = str(
            table.cells(row=row_number, column=table_column_numbers)
        )
        table_last_column_data = table_last_column_data.partition("|")[-1]
        return table_last_column_data

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

    def get_table_column_numbers(self, table: wtp.Table,
                                 row_number: int = 0) -> int:
        """
        Returns the number of columns in a table

        Keyword arguments:
        table -- The table which the number of columns is
                 being searched
        row_number -- The row number of the table which
                      the number of columns is being
                      searched

        Returns:
        table_column_numbers -- The number of columns in the
                                table
        """
        table_data = table.data(span=False)
        table_row = table_data[row_number]

        # because indexing starts at 0
        table_column_numbers = len(table_row) - 1
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

    def hyperlink_external_link(self, text: str, link: str) -> str:
        """
        Hyperlink an external page to a text

        Keyword arguments:
        text -- The text that will hyperlink to an external page
        link -- The external link that is going to be present in
                text

        Returns:
        hyperlinked_text -- The text with a hyperlink to an
                            external page
        """
        hyperlinked_text = f"[{link} {text}]"
        return hyperlinked_text

    def hyperlink_wiki_page(self, wiki_page: str, text: str) -> str:
        """
        Hyperlink a wiki page to a text

        Keyword arguments:
        text -- The text that will hyperlink to a wiki page
        link -- The wiki page link that is going
                to be present in text

        Returns:
        hyperlinked_page -- The text with a hyperlink to a
                            wiki page
        """
        hyperlinked_page = f"[[{wiki_page} | {text}]]"
        return hyperlinked_page

    def format_section_children_title(self, parent_section_level,
                                      section_children_title):
        section_children_level = parent_section_level + 1
        section_delimiter = "="
        section_children_text = (
            " " + (section_delimiter * parent_section_level) + "\n" +
            (section_delimiter * section_children_level) +
            f" {section_children_title} " +
            (section_delimiter * section_children_level)
        )
        return section_children_text

    def add_children_section(self, text, section_children_title,
                             section_parent_title):
        try:
            parsed_text = wtp.parse(text)
            parsed_string = str(parsed_text)
            section_title_string = (
                re.search(
                    f"(=)*({section_parent_title})(=)*",
                    parsed_string
                )
            )

            parent_section_index = (
                self.get_section_index(text, section_parent_title)
            )
            parent_section_level = (
                parsed_text.sections[parent_section_index].level
            )

            parent_section_new_index = (
                section_title_string.span()[1] + parent_section_level + 1
            )
            end_text = parsed_string[parent_section_new_index:-1]

            end_index = section_title_string.span()[1]

            section_children_text = self.format_section_children_title(
                parent_section_level,
                section_children_title
            )
            parsed_string = (
                parsed_string[0:end_index] + section_children_text
                + end_text
            )
            return parsed_string
        except WikiServiceError as e:
            raise WikiServiceError(str(e))
