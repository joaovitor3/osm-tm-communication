from server import ma
from server.models.serializers.utils import (
    CamelCaseSchema
)


class UserSchema(CamelCaseSchema):
    osm_id = ma.Int(required=True)
    username = ma.Str(required=True)


class ProjectSchema(CamelCaseSchema):
    title = ma.Str(required=True)
    status = ma.Str(required=True)
    changeset_comment = ma.Str(required=True)
    external_source = ma.Str(required=True)
    goal = ma.Str(required=True)
    id = ma.Int(required=True)
    link = ma.Url(required=True)
    tools = ma.Str(required=True)
    project_manager = ma.Str(required=True)
    created = ma.DateTime(required=True)
    due_date = ma.Str(required=True)
    instructions = ma.Str(required=True)
    users = ma.List(ma.Nested(UserSchema))
