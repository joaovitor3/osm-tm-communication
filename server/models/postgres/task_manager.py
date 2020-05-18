from server import db


class TaskManager(db.Model):
    __tablename__ = "task_manager"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    user_id = db.relationship('User', backref='taskmanager', lazy=True)
