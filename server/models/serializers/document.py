from server.models.postgres.document import Document
from server import ma


class DocumentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Document
        include_fk = True
