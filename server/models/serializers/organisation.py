from server import ma
from server.models.serializers.utils import CamelCaseSchema


class OrganisationSchema(CamelCaseSchema):
    description = ma.Str(required=True)
    link = ma.Url(required=True)
    name = ma.Str(required=True)
