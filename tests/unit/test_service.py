import pytest

from app.errors import NotFoundError, ValidationError
from app.service import TaskService
from tests.unit.fakes import InMemoryTaskRepository


@pytest.fixture
def service():
    return TaskService(InMemoryTaskRepository())


def test_cria_tarefa_com_valores_padrao(service):
    task = service.create_task("Escrever testes")
    assert task["id"] == 1
    assert task["priority"] == "medium"
    assert task["tags"] == []
    assert task["done"] is False


def test_cria_tarefa_normalizando_entrada(service):
    task = service.create_task("  Deploy ", "high", ["CI", "ci", "Infra"])
    assert task["title"] == "Deploy"
    assert task["tags"] == ["ci", "infra"]


def test_criar_com_titulo_invalido_nao_persiste(service):
    with pytest.raises(ValidationError):
        service.create_task("   ")
    assert service.list_tasks() == []


def test_buscar_inexistente_levanta_not_found(service):
    with pytest.raises(NotFoundError):
        service.get_task(99)


def test_concluir_tarefa(service):
    task = service.create_task("Revisar PR")
    assert service.complete_task(task["id"])["done"] is True


def test_concluir_inexistente_levanta_not_found(service):
    with pytest.raises(NotFoundError):
        service.complete_task(1)


def test_filtra_por_status(service):
    a = service.create_task("A")
    service.create_task("B")
    service.complete_task(a["id"])
    assert [t["title"] for t in service.list_tasks("done")] == ["A"]
    assert [t["title"] for t in service.list_tasks("open")] == ["B"]
    assert len(service.list_tasks()) == 2


def test_status_invalido(service):
    with pytest.raises(ValidationError):
        service.list_tasks("qualquer")


def test_remove_tarefa(service):
    task = service.create_task("Temporária")
    service.delete_task(task["id"])
    with pytest.raises(NotFoundError):
        service.get_task(task["id"])


def test_remover_inexistente_levanta_not_found(service):
    with pytest.raises(NotFoundError):
        service.delete_task(1)


def test_estatisticas_sem_tarefas(service):
    assert service.stats() == {"total": 0, "done": 0, "open": 0, "completion_rate": 0.0}


def test_estatisticas_com_tarefas(service):
    ids = [service.create_task(f"T{i}")["id"] for i in range(4)]
    service.complete_task(ids[0])
    assert service.stats() == {"total": 4, "done": 1, "open": 3, "completion_rate": 0.25}
