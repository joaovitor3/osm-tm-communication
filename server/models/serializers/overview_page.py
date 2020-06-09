from schematics import Model
from schematics.types import (
    StringType
)


class OverviewPageSerializer(Model):
    organisation_name = StringType(required=True)
    organisation_link = StringType(required=True)
    organiser_name = StringType(required=True)
    organiser_link = StringType(required=True)
