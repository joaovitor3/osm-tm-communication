from server.models.postgres.organiser import Organiser
from server import ma


class OrganiserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Organiser
        include_fk = True
