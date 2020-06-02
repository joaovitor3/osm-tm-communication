from server.models.postgres.task_manager import TaskManager
from server import ma


class TaskManagerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaskManager
        include_fk = True
