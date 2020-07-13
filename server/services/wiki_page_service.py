from abc import ABC, abstractmethod
from server.models.serializers.document import (
    DocumentSchema
)
from server.services.wiki_service import (
    WikiService
)
import re
from flask import current_app


class WikiPageService(ABC):
    def document_to_page_sections(self, document_data: dict) -> dict:
        """
        Generate dict containing the document content
        parsed to wikitext for all sections present
        in a page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        page_sections_data -- Dictionary containing the document
                              content parsed to wikitext
                              for all page sections
        """
        # Filter page data from document data
        page_data = self.filter_page_data(document_data)
        page_fields = self.get_page_fields()

        # Serialize document with page content
        document_schema = DocumentSchema(
            only=page_fields
        )
        serialized_page_data = (
            document_schema.load(page_data)
        )

        # Generate page sections dictionary
        page_sections_data = self.generate_page_sections_dict(
            serialized_page_data
        )
        return page_sections_data

    def wikitext_to_dict(self, page_title):
        wiki_obj = WikiService()
        token = wiki_obj.get_token()
        wiki_obj.check_token(token)

        text = wiki_obj.get_page_text(page_title)
        sections = wiki_obj.get_sections(text)

        dictionary = {}
        for section in sections:
            # fazer função com esse if
            if section.title is not None: #and section.title != self.page_initial_section.replace("=", ""):
                parent_section_level = 2
                section_title_string = (
                    re.search(
                        f"(=){{{parent_section_level}}}({section.title})(=){{{parent_section_level}}}\n",
                        section.string
                    )
                )
                if section_title_string is not None:
                    start_index, end_index = section_title_string.span()
                    removed_section_parent = section.string[end_index:len(section.string)]
                    children_sections = wiki_obj.get_sections(removed_section_parent)
                    children_dict = {}
                    
                    for child_section in children_sections:
                        if child_section.title is not None:
                            child_section_title_string = (
                                re.search(
                                    f"(=){{{parent_section_level + 1}}}({child_section.title})(=){{{parent_section_level + 1}}}",
                                    child_section.string
                                )
                            )
                            child_end_index = child_section_title_string.span()[-1]
                            
                            teste = child_section.string[child_end_index:len(child_section.string)]

                            children_dict[child_section.title] = teste                               
                            dictionary[section.title] = children_dict

                    if not children_dict:
                        dictionary[section.title] = removed_section_parent
        return dictionary

    @abstractmethod
    def get_page_fields(self) -> list:
        """
        Get all required fields for a specific page

        Returns:
        list -- List containing all required fields
        for a specific page
        """
        ...

    @abstractmethod
    def filter_page_data(self, document_data: dict) -> dict:
        """
        Filter required data for a specific page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        dict -- Dict containing only the required data
        for a specific page
        """
        ...

    @abstractmethod
    def generate_page_sections_dict(self, serialized_page_data: dict) -> dict:
        """
        Generate dict containing the document content parsed to wikitext
        for all sections present in a page

        Keyword arguments:
        serialized_page_data -- Dictionary containing the required data for the
                                page sections

        Returns:
        dict -- Dictionary with the document content parsed to wikitext
                for all sections present in a page
        """
        ...

    @abstractmethod
    def create_page(self, document_data: dict) -> None:
        """
        Creates a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        ...
