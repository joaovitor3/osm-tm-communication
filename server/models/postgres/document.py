from server import db
from server.models.utils import timestamp
from server.models.postgres.task_manager import TaskManager


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

    def create_document(self, link, commit_hash, task_manager_id):
        task_manager = TaskManager.get(task_manager_id)
        self.task_manager_id = task_manager.id
        self.link = link
        self.commit_hash = commit_hash
        self.task_manager_id = task_manager.id
        self.create()
