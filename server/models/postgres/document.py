from server import db
from server.models.utils import timestamp


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(200))
    commit_hash = db.Column(db.String(500))
    creation_date = db.Column(db.DateTime, default=timestamp)
    created_by = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )
