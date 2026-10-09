"""Regras de negócio. Depende de um repositório injetado (fácil de simular em testes unitários)."""
from .errors import NotFoundError, ValidationError
from .validators import normalize_tags, validate_priority, validate_title


class TaskService:
    def __init__(self, repository):
        self.repository = repository

    def create_task(self, title, priority="medium", tags=None):
        return self.repository.add(
            validate_title(title), validate_priority(priority), normalize_tags(tags)
        )

    def get_task(self, task_id):
        task = self.repository.get(task_id)
        if task is None:
            raise NotFoundError(f"tarefa {task_id} não encontrada")
        return task

    def list_tasks(self, status=None):
        if status is None:
            return self.repository.list()
        if status not in ("open", "done"):
            raise ValidationError("status deve ser 'open' ou 'done'")
        return self.repository.list(done=(status == "done"))

    def complete_task(self, task_id):
        self.get_task(task_id)
        return self.repository.mark_done(task_id)

    def delete_task(self, task_id):
        if not self.repository.delete(task_id):
            raise NotFoundError(f"tarefa {task_id} não encontrada")

    def stats(self):
        tasks = self.repository.list()
        done = sum(1 for t in tasks if t["done"])
        total = len(tasks)
        return {
            "total": total,
            "done": done,
            "open": total - done,
            "completion_rate": round(done / total, 2) if total else 0.0,
        }
