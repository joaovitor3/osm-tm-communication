from schematics import Model
from schematics.types import (
    StringType
)


class OrganisationPageSerializer(Model):
    name = StringType(required=True)
    link = StringType(required=True)
    description = StringType(required=True)
    project_title = StringType(required=True)
    project_manager = (
        StringType(required=True, serialized_name="projectManager")
    )
    project_status = StringType(required=True)
    organiser_name = StringType(required=True)
    organiser_link = StringType(required=True)
