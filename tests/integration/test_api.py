"""API HTTP + serviço + SQLite funcionando juntos."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_criar_tarefa_retorna_201(client):
    resp = client.post("/tasks", json={"title": "Integrar", "priority": "high", "tags": ["API"]})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["id"] == 1
    assert body["tags"] == ["api"]
    assert body["done"] is False


def test_criar_sem_titulo_retorna_400(client):
    resp = client.post("/tasks", json={})
    assert resp.status_code == 400
    assert "title" in resp.get_json()["error"]


def test_criar_com_prioridade_invalida_retorna_400(client):
    resp = client.post("/tasks", json={"title": "X", "priority": "urgent"})
    assert resp.status_code == 400


def test_buscar_tarefa_existente(client):
    created = client.post("/tasks", json={"title": "Buscar"}).get_json()
    resp = client.get(f"/tasks/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Buscar"


def test_buscar_inexistente_retorna_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_concluir_e_filtrar(client):
    first = client.post("/tasks", json={"title": "A"}).get_json()
    client.post("/tasks", json={"title": "B"})
    assert client.patch(f"/tasks/{first['id']}/complete").get_json()["done"] is True

    done = client.get("/tasks?status=done").get_json()
    open_ = client.get("/tasks?status=open").get_json()
    assert [t["title"] for t in done] == ["A"]
    assert [t["title"] for t in open_] == ["B"]


def test_filtro_com_status_invalido_retorna_400(client):
    assert client.get("/tasks?status=foo").status_code == 400


def test_remover_tarefa(client):
    created = client.post("/tasks", json={"title": "Remover"}).get_json()
    assert client.delete(f"/tasks/{created['id']}").status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_remover_inexistente_retorna_404(client):
    assert client.delete("/tasks/42").status_code == 404


def test_fluxo_completo_e_estatisticas(client):
    ids = [client.post("/tasks", json={"title": f"T{i}"}).get_json()["id"] for i in range(4)]
    client.patch(f"/tasks/{ids[0]}/complete")
    client.patch(f"/tasks/{ids[1]}/complete")
    client.delete(f"/tasks/{ids[3]}")
    assert client.get("/stats").get_json() == {
        "total": 3, "done": 2, "open": 1, "completion_rate": 0.67,
    }
