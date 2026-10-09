"""Camada HTTP (Flask)."""
import os

from flask import Flask, jsonify, request

from .errors import NotFoundError, ValidationError
from .repository import SqliteTaskRepository
from .service import TaskService


def create_app(db_path=None):
    app = Flask(__name__)
    db_path = db_path or os.environ.get("DB_PATH", "tasks.db")
    service = TaskService(SqliteTaskRepository(db_path))

    @app.errorhandler(ValidationError)
    def _validation(err):
        return jsonify(error=str(err)), 400

    @app.errorhandler(NotFoundError)
    def _not_found(err):
        return jsonify(error=str(err)), 404

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.post("/tasks")
    def create_task():
        body = request.get_json(silent=True) or {}
        task = service.create_task(
            body.get("title"), body.get("priority", "medium"), body.get("tags")
        )
        return jsonify(task), 201

    @app.get("/tasks")
    def list_tasks():
        return jsonify(service.list_tasks(request.args.get("status")))

    @app.get("/tasks/<int:task_id>")
    def get_task(task_id):
        return jsonify(service.get_task(task_id))

    @app.patch("/tasks/<int:task_id>/complete")
    def complete_task(task_id):
        return jsonify(service.complete_task(task_id))

    @app.delete("/tasks/<int:task_id>")
    def delete_task(task_id):
        service.delete_task(task_id)
        return "", 204

    @app.get("/stats")
    def stats():
        return jsonify(service.stats())

    return app
