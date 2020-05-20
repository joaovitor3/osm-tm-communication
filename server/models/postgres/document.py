from server import db
from server.models.utils import timestamp


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(200))
    commit_hash = db.Column(db.String(500))
    creation_date = db.Column(db.DateTime, default=timestamp)
    task_manager_id = db.Column(
        db.Integer,
        db.ForeignKey('task_manager.id'),
        nullable=False
    )

    def create(self):
        """ Creates and saves the current model to the DB """
        db.session.add(self)
        db.session.commit()

    def save(self):
        """ Save changes to db"""
        db.session.commit()

    @staticmethod
    def get(document_id: int):
        """
        Gets specified document
        :param document_id: document ID in scope
        :return: Document if found otherwise None
        """
        return Document.query.get(document_id)

    def delete(self):
        """ Deletes the current model from the DB """
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def check_if_document_exists(document_id: int):
        document = Document.get(document_id)
        if document is not None:
            return True
        return False
