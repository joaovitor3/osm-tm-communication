from server import ma
from server.models.serializers.utils import CamelCaseSchema


class OrganiserSchema(CamelCaseSchema):
    name = ma.Str(required=True)
    link = ma.Url(required=True)
    metrics = ma.Str(required=True)
    quality_assurance = ma.Str(required=True)
