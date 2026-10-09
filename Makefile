# Cada tipo de teste roda de forma independente.
PY ?= python

install:            ## instala todas as dependências
	$(PY) -m pip install -r requirements-dev.txt -r requirements-perf.txt

test-unit:          ## testes unitários + cobertura
	$(PY) -m pytest tests/unit -m unit --junitxml=reports/unit/junit.xml \
	  --cov=app.validators --cov=app.service --cov-report=term-missing \
	  --cov-report=xml:reports/unit/coverage.xml --cov-report=html:reports/unit/htmlcov --cov-fail-under=90

test-integration:   ## testes de integração
	$(PY) -m pytest tests/integration -m integration --junitxml=reports/integration/junit.xml

test-performance:   ## testes de performance (sobe o servidor e roda o Locust)
	$(PY) scripts/run_performance.py

test-all: test-unit test-integration test-performance

.PHONY: install test-unit test-integration test-performance test-all
