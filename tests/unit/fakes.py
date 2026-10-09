"""Repositório em memória: permite testar o serviço sem banco de dados."""


class InMemoryTaskRepository:
    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def add(self, title, priority, tags):
        task = {
            "id": self._next_id,
            "title": title,
            "priority": priority,
            "tags": tags,
            "done": False,
            "created_at": "2025-01-01T00:00:00+00:00",
        }
        self._tasks[self._next_id] = task
        self._next_id += 1
        return dict(task)

    def get(self, task_id):
        task = self._tasks.get(task_id)
        return dict(task) if task else None

    def list(self, done=None):
        tasks = [dict(t) for t in self._tasks.values()]
        if done is None:
            return tasks
        return [t for t in tasks if t["done"] == done]

    def mark_done(self, task_id):
        self._tasks[task_id]["done"] = True
        return dict(self._tasks[task_id])

    def delete(self, task_id):
        return self._tasks.pop(task_id, None) is not None
