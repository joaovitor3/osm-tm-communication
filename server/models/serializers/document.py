from marshmallow.exceptions import ValidationError

from server import ma
from server.models.serializers.statuses import DocumentContentType
from server.models.serializers.utils import CamelCaseSchema
from server.models.serializers.organisation import OrganisationSchema
from server.models.serializers.platform import PlatformSchema
from server.models.serializers.project import (
    ProjectSchema,
    ExternalSourceSchema
)


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
                f"{DocumentContentType.PLATFORM.name}"
            )


def build_schema_dict():
    project = (
        DocumentContentType["PROJECT"].name.lower()
    )
    organisation = (
        DocumentContentType["ORGANISATION"].name.lower()
    )
    platform = (
        DocumentContentType["PLATFORM"].name.lower()
    )
    schema_dict = {
        project: ProjectSchema(),
        organisation: OrganisationSchema(),
        platform: PlatformSchema(),
        "external_source": ExternalSourceSchema()
    }
    return schema_dict


def turn_fields_optional(url_parameters):
    schema_dict = build_schema_dict()
    optional_fields = []
    for parameter in url_parameters:
        for schema_field in schema_dict[parameter].fields.keys():
            field_type = (
                schema_dict[parameter].fields[schema_field]
            )
            if type(field_type) == ma.Nested:
                external_source_fields = (
                    schema_dict["external_source"].fields.keys()
                )
                for nested_field in external_source_fields:
                    optional_fields.append(
                        f"{parameter}.{schema_field}.{nested_field}"
                    )
            else:
                optional_fields.append(
                    f"{parameter}.{schema_field}"
                )
    return tuple(optional_fields)


class DocumentSchema(CamelCaseSchema):
    project = ma.Nested(ProjectSchema)
    organisation = ma.Nested(OrganisationSchema)
    platform = ma.Nested(PlatformSchema)
