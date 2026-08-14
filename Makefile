PY ?= python
RUN := PYTHONPATH=src $(PY) -m operational_agents

.DEFAULT_GOAL := help
.PHONY: help install check lint test validate eval sync sync-check serve docker clean

help:  ## Muestra esta ayuda
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Instala el paquete en modo editable
	$(PY) -m pip install -e ".[dev]"

check: sync-check validate eval test  ## Verificación completa: lo mismo que ejecuta CI

lint:  ## Analiza el código con ruff
	$(PY) -m ruff check .

test:  ## Ejecuta las pruebas deterministas
	$(PY) -m unittest discover -s tests -v

validate:  ## Valida la integridad de los paquetes de agente
	$(RUN) validate

eval:  ## Ejecuta las evaluaciones deterministas
	$(RUN) eval --all

sync:  ## Regenera las vistas derivadas del catálogo
	$(RUN) sync

sync-check:  ## Falla si alguna vista generada tiene drift
	$(RUN) sync --check

serve:  ## Levanta el control center en loopback
	$(RUN) serve

docker:  ## Construye y levanta el control center en Docker
	docker compose up --build

clean:  ## Elimina artefactos de build y caches
	rm -rf dist build .ruff_cache src/*.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
