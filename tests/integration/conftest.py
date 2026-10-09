import pytest

from app.api import create_app
from app.repository import SqliteTaskRepository


@pytest.fixture
def db_path(tmp_path):
    """Banco SQLite real, novo e isolado a cada teste."""
    return str(tmp_path / "test.db")


@pytest.fixture
def repo(db_path):
    return SqliteTaskRepository(db_path)


@pytest.fixture
def client(db_path):
    app = create_app(db_path)
    app.config["TESTING"] = True
    return app.test_client()
