from server import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    osm_id = db.Column(db.Integer, nullable=False)
    documents = db.relationship('Document', backref='user', lazy=True)
    task_manager = db.Column(
        db.Integer,
        db.ForeignKey('task_manager.id'),
        nullable=False
    )
