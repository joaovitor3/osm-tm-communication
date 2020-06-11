from marshmallow.exceptions import ValidationError

from server import ma
from server.models.serializers.statuses import DocumentContentType
from server.models.serializers.utils import CamelCaseSchema
from server.models.serializers.organisation import OrganisationSchema
from server.models.serializers.organiser import OrganiserSchema
from server.models.serializers.project import ProjectSchema


def is_known_document_content_type(value):
    """ Validates that Project Status is known value """
    for doc_content_type in value:
        try:
            DocumentContentType[doc_content_type.upper()]
        except KeyError:
            raise ValidationError(
                f"Unknown contentType: {doc_content_type}. "
                f"Valid values are {DocumentContentType.PROJECT.name}, "
                f"{DocumentContentType.ORGANISATION.name}, "
                f"{DocumentContentType.ORGANISER.name}"
            )


def build_schema_dict():
    project = (
        DocumentContentType["PROJECT"].name.lower()
    )
    organisation = (
        DocumentContentType["ORGANISATION"].name.lower()
    )
    organiser = (
        DocumentContentType["ORGANISER"].name.lower()
    )
    schema_dict = {
        project: ProjectSchema(),
        organisation: OrganisationSchema(),
        organiser: OrganiserSchema()
    }
    return schema_dict


def turn_fields_optional(url_parameters):
    schema_dict = build_schema_dict()
    optional_fields = []
    for parameter in url_parameters:
        for schema_field in schema_dict[parameter].fields.keys():
            optional_fields.append(
                f"{parameter}.{schema_field}"
            )
    return tuple(optional_fields)


class DocumentSchema(CamelCaseSchema):
    project = ma.Nested(ProjectSchema)
    organisation = ma.Nested(OrganisationSchema)
    organiser = ma.Nested(OrganiserSchema)
