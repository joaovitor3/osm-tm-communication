import requests
import re
from flask import current_app
import wikitextparser as wtp
from datetime import datetime

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

    def format_date_text(self, str_date: str) -> str:
        """
        Format a date into the format "%dd month_name %YYYY"

        Keyword arguments:
        date -- Date being formatted

        Returns:
        text_date -- Dictionary with result of post request for checking
                the MediaWiki API Token
        """
        parsed_date = datetime.strptime(
            str_date,
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        date_month = parsed_date.strftime("%B")
        date_day = parsed_date.strftime("%m")
        date_year = parsed_date.strftime("%Y")

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
               section.title == section_title):
                return index
        raise WikiServiceError("The section you specified doesn't exist")

    def get_section_table(self, text: str, section_title: str) -> wtp.Table:
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
        parsed_text = wtp.parse(text)
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
        table_last_column_data = str(
            table.cells(row=row_number, column=table_column_numbers)
        )
        table_last_column_data = table_last_column_data.partition("|")[-1]
        return table_last_column_data

    def add_table_row(self, page_text: str, new_row: str,
                      table_section_title: str,
                      table_template: str) -> str:
        """
        Add a row to table
        """
        page_text += f"{table_template}"
        table = self.get_section_table(
            page_text,
            table_section_title
        )

        table_string = str(table)
        str_index_new_row = self.get_new_row_index(table)

        updated_table = (
            table_string[:str_index_new_row] +
            new_row + table_string[str_index_new_row:]
        )

        text_before_table_index = page_text.find(table_string)
        wtp_page_text = wtp.parse(page_text)
        wtp_page_text.string = (
            page_text[0:text_before_table_index] + updated_table
        )
        return str(wtp_page_text)

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

    def generate_page_text_from_dict(self, template_text: str,
                                     page_initial_section: str,
                                     page_data: dict,
                                     table_section: str):
        """
        Returns the number of columns in a table

        Keyword arguments:
        template_text --
        page_initial_section --
        page_data --
        table_section --

        Returns:
        table_column_numbers -- The number of columns in the
                                table
        """
        parsed_text = wtp.parse(template_text)
        parsed_sections = parsed_text.sections
        updated_text = f"{page_initial_section}\n"

        for section in parsed_sections:
            if self.is_section_being_updated(section, page_data):
                # Get the starting and ending position of a section's title
                start_index, end_index = self.get_section_title_str_index(
                    section, template_text
                )
                page_section_data = page_data[section.title]

                if self.contains_child_section(page_section_data):
                    for (children_section_number,
                         child_section) in enumerate(page_section_data):
                        child_section_title = self.add_child_section_markers(
                            section,
                            child_section
                        )

                        # If the section has more than one child section
                        # this child's section data must be placed after
                        # the predecessor child section
                        if children_section_number > 0:
                            end_index = self.fix_child_section_string_position(
                                page_data,
                                section,
                                children_section_number
                            )

                        # Update page text
                        if child_section != table_section:
                            updated_text += (
                                template_text[start_index:end_index] +
                                child_section_title +
                                page_section_data[child_section]
                            )
                        else:
                            updated_text = self.add_table_row(
                                updated_text,
                                page_section_data[child_section],
                                table_section,
                                section.string
                            )
                else:
                    # Update page text
                    if section.title != table_section:
                        updated_text += (
                            template_text[start_index:end_index] +
                            page_section_data
                        )
                    else:
                        updated_text = self.add_table_row(
                            updated_text,
                            page_section_data,
                            table_section,
                            section.string
                        )
        return updated_text

    def is_section_being_updated(self, section: wtp.Section,
                                 page_data: dict) -> bool:
        """
        Check if the section is being updated or if it is
        just a section title

        Keyword arguments:
        section -- The section being checked
        page_data -- Dict containing the data for a page

        Returns:
        bool -- Boolean indicating if the section is being updated
        """
        if (section.title is not None and
           section.title in list(page_data.keys())):
            return True
        else:
            return False

    def contains_child_section(self, page_section_data):
        """
        Check if the section contains child section

        Keyword arguments:
        page_section_data -- The page section data

        Returns:
        bool -- Boolean indicating if the section contains child section
        """
        if isinstance(page_section_data, dict):
            return True
        else:
            return False

    def get_section_title_str_index(self, section: wtp.Section,
                                    template_text: str) -> tuple:
        """
        Get the starting and ending position of
        a section's title string

        Keyword arguments:
        section --
        template_text --

        Returns:
        start_end_index,end_index --
        """
        section_title_string = (
            re.search(
                f"(=)*({section.title})(=)*",
                template_text
            )
        )
        start_index = section_title_string.span()[0]
        end_index = section_title_string.span()[1]
        return start_index, end_index

    def add_child_section_markers(self,
                                  parent_section: wtp.Section,
                                  child_section: str) -> str:
        """
        Parse text from child section by adding section
        markers according to parent section level

        Keyword arguments:
        parent_section -- The parent section
        child_section -- The text of the child section

        Returns:
        child_section_title -- The parsed text of the child section
        """
        child_section_markers = (
            "=" * (parent_section.level + 1)
        )
        child_section_title = (
            f"\n{child_section_markers} "
            f"{child_section} "
            f"{child_section_markers}"
        )
        return child_section_title

    def fix_child_section_string_position(self, page_data: dict,
                                          section: wtp.Section,
                                          child_section_index: int) -> int:
        """
        Updates the position of the string in which the child section is
        going to be added for right after the predecessor
        child section, instead of adding it right after the
        parent section title

        Keyword arguments:
        page_data -- Dict containing the data for a page
        child_section_index -- Index indicating the position
                                  in which the child section should
                                  be added in the text of the page

        Returns:
        new_end_index -- The parsed text of the children section
        """
        children_section_keys = list(
            page_data[section.title].keys()
        )
        predecessor_child_section_title = children_section_keys[
            child_section_index - 1
        ]
        new_end_index = len(predecessor_child_section_title)
        return new_end_index

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
