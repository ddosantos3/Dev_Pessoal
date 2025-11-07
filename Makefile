.PHONY: install run lint format typecheck test frontend-install frontend-dev frontend-build

install:
	python -m venv .venv
	. .venv/Scripts/activate || . .venv/bin/activate; pip install -U pip
	. .venv/Scripts/activate || . .venv/bin/activate; pip install -r requirements.txt

run:
	. .venv/Scripts/activate || . .venv/bin/activate; uvicorn --app-dir src app.main:app --reload

lint:
	ruff check src

format:
	black src

typecheck:
	. .venv/Scripts/activate || . .venv/bin/activate; PYTHONPATH=src mypy src

test:
	. .venv/Scripts/activate || . .venv/bin/activate; PYTHONPATH=src pytest -q

frontend-install:
	npm ci --prefix src/app/frontend/quest-talk-gui

frontend-dev:
	npm run dev --prefix src/app/frontend/quest-talk-gui

frontend-build:
	npm run build --prefix src/app/frontend/quest-talk-gui
