install:
	. .venv/bin/activate; pip install -Ur requirements.txt

activate:
	. .venv/bin/activate

install_venv:
	python3 -m venv .venv
	. .venv/bin/activate; python -m pip install --upgrade pip
	. .venv/bin/activate; python -m pip install -r dev-requirements.txt

formatter:
	. .venv/bin/activate; command black --line-length 125 .

check_format:
	. .venv/bin/activate; command black --line-length 125 . --check

test:
	. .venv/bin/activate; command cd src; command pytest

remove_docker_containers:
	docker compose ps -q | xargs docker rm

remove_docker_images:
	docker compose config --images | xargs docker rmi

start:
	docker compose -f local-docker-compose.yml up --attach pdf_paragraphs_extraction_worker --attach pdf_paragraphs_extraction_api --build

start_mac:
	docker compose -f mac-docker-compose.yml up

start_local:
	docker compose -f local-docker-compose.yml up

start_detached:
	docker compose up --build -d

start_for_testing:
	docker compose down; docker compose up --attach pdf_paragraphs_extraction_worker --attach pdf_paragraphs_extraction_api --build

stop:
	docker compose stop

delete_queues:
	. .venv/bin/activate; python scripts/delete_queues.py
