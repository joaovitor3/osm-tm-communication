from schematics import Model
from schematics.types import (
    StringType,
    UTCDateTimeType,
    URLType,
    ListType,
    DictType
)


class ProjectPageSerializer(Model):
    title = StringType(required=True)
    goal = StringType(required=True)
    created = UTCDateTimeType(required=True)
    due_date = UTCDateTimeType(required=True, serialized_name="dueDate")
    changeset_comment = (
        StringType(required=True, serialized_name="changesetComment")
    )
    instructions = StringType(required=True)
    external_source = (
        StringType(required=True, serialized_name="externalSource")
    )
    link = URLType(required=True)
    metrics = StringType(required=True)
    quality_assurance = (
        StringType(required=True, serialized_name="qualityAssurance")
    )
    users = ListType(DictType(StringType), required=True)
