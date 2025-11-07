.PHONY: run test lint

run:
	uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff src/