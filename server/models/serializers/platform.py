from server import ma
from server.models.serializers.utils import CamelCaseSchema


class PlatformSchema(CamelCaseSchema):
    name = ma.Str(required=True)
    url = ma.Url(required=True)
    # metrics = ma.Str(required=True)
    # quality_assurance = ma.Str(required=True)
