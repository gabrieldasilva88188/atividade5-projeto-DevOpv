# Projeto de testes automatizados com CI (GitHub Actions)

API REST de tarefas (Flask + SQLite) usada para demonstrar **três tipos de teste independentes**
e uma pipeline de **Integração Contínua** que os executa a cada push na branch `main`.

## Estrutura

```
.
├── app/                         # Código da aplicação
│   ├── validators.py            #   funções puras de validação
│   ├── service.py               #   regras de negócio
│   ├── repository.py            #   persistência SQLite
│   ├── api.py                   #   rotas HTTP (Flask)
│   └── server.py                #   servidor waitress (usado no teste de performance)
├── tests/
│   ├── unit/                    # Unitários: sem I/O, repositório simulado (fakes.py)
│   ├── integration/             # Integração: API + serviço + SQLite reais
│   └── performance/locustfile.py# Performance: Locust com limites (SLOs)
├── scripts/
│   ├── run_performance.py       # sobe o servidor, roda o Locust e encerra
│   └── summarize_results.py     # gera resumo em Markdown dos relatórios
├── .github/workflows/ci.yml     # Pipeline de CI
├── requirements.txt             # runtime
├── requirements-dev.txt         # + pytest, pytest-cov
└── requirements-perf.txt        # + locust
```

## Como executar cada tipo de teste (de forma independente)

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
```

| Tipo | Dependências | Comando | Relatórios |
|---|---|---|---|
| Unitário | `pip install -r requirements-dev.txt` | `make test-unit` ou `pytest tests/unit -m unit` | `reports/unit/` (JUnit, cobertura XML/HTML) |
| Integração | `pip install -r requirements-dev.txt` | `make test-integration` ou `pytest tests/integration -m integration` | `reports/integration/` (JUnit) |
| Performance | `pip install -r requirements-perf.txt` | `make test-performance` ou `python scripts/run_performance.py` | `reports/performance/` (HTML, CSV) |

Sem `make` (ex.: Windows), use os comandos `pytest`/`python` da coluna "Comando".
Também é possível filtrar por marcador em qualquer pasta: `pytest -m unit` ou `pytest -m integration`.

### Parâmetros do teste de performance (variáveis de ambiente)

| Variável | Padrão | Significado |
|---|---|---|
| `USERS` / `SPAWN_RATE` / `RUN_TIME` | 20 / 5 / 20s | usuários simultâneos, taxa de entrada, duração |
| `P95_MS` | 500 | latência P95 máxima (ms) |
| `MAX_FAIL_RATIO` | 0.01 | proporção máxima de falhas |
| `MIN_RPS` | 20 | vazão mínima (req/s) |

Se algum limite for violado, o script retorna código de saída 1 e a pipeline falha.

## Pipeline de CI (`.github/workflows/ci.yml`)

Disparada em **push na `main`** (e manualmente via *workflow_dispatch*). Quatro jobs:

1. **Testes unitários** — instala dependências, roda `pytest` com cobertura (mínimo 90%).
2. **Testes de integração** — instala dependências e roda `pytest` contra API + SQLite.
3. **Testes de performance** — instala Locust, sobe o servidor e valida os limites.
4. **Resultado final** — consolida o status e falha se qualquer etapa falhou.

Os três jobs de teste rodam **em paralelo** e são independentes entre si.

**Onde ver os resultados:** na aba *Actions* → execução → *Summary*. Cada job publica uma tabela
de resultados (testes aprovados/falhos, latências por endpoint) e anexa os relatórios completos
como *artifacts* (JUnit, cobertura HTML, relatório HTML do Locust).
git push -u origin main      # o push na main dispara a pipeline
```
