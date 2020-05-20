from server import db


class TaskManager(db.Model):
    __tablename__ = "task_manager"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    documents = db.relationship('Document', backref='taskmanager', lazy=True)

    @staticmethod
    def get(task_manager_id: int):
        """
        Gets specified task manager
        :param task_manager_id: task manager ID in scope
        :return: TaskManager if found otherwise None
        """
        return TaskManager.query.get(task_manager_id)

    def create(self):
        """ Creates and saves the current model to the DB """
        db.session.add(self)
        db.session.commit()

    def save(self):
        """ Save changes to db"""
        db.session.commit()

    def delete(self):
        """ Deletes the current model from the DB """
        db.session.delete(self)
        db.session.commit()
