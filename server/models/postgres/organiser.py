from server import db


class Organiser(db.Model):
    __tablename__ = "organiser"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    link = db.Column(db.String(200))
    task_managers = db.relationship(
        "TaskManager",
        backref="organiser",
        lazy=True
    )

    @staticmethod
    def get(organiser_id: int):
        """
        Gets specified task manager
        :param organiser_id: task manager ID in scope
        :return: Organiser if found otherwise None
        """
        return Organiser.query.get(organiser_id)

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
