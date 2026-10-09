"""Serviço + repositório SQLite reais (sem camada HTTP)."""
import pytest

from app.errors import NotFoundError
from app.service import TaskService


@pytest.fixture
def service(repo):
    return TaskService(repo)


def test_persiste_e_recupera_tarefa(service):
    created = service.create_task("Persistir", "high", ["db"])
    fetched = service.get_task(created["id"])
    assert fetched == created
    assert fetched["tags"] == ["db"]


def test_dados_sobrevivem_a_nova_conexao(db_path):
    from app.repository import SqliteTaskRepository

    TaskService(SqliteTaskRepository(db_path)).create_task("Duradouro")
    reopened = TaskService(SqliteTaskRepository(db_path))
    assert [t["title"] for t in reopened.list_tasks()] == ["Duradouro"]


def test_ids_sao_incrementais(service):
    ids = [service.create_task(f"T{i}")["id"] for i in range(3)]
    assert ids == [1, 2, 3]


def test_filtro_por_status_no_banco(service):
    a = service.create_task("A")
    service.create_task("B")
    service.complete_task(a["id"])
    assert len(service.list_tasks("done")) == 1
    assert len(service.list_tasks("open")) == 1


def test_remocao_efetiva(service):
    task = service.create_task("Apagar")
    service.delete_task(task["id"])
    with pytest.raises(NotFoundError):
        service.get_task(task["id"])
