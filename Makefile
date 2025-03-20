local-build:
	docker compose -f local.yml build

local-up:
	docker compose -f local.yml up -d

local-down:
	docker compose -f local.yml down

format:
	/usr/bin/black cbed config --exclude "migrations"
	/usr/bin/isort cbed config --profile black

migrate:
	docker compose -f local.yml run --rm django python manage.py makemigrations
	docker compose -f local.yml run --rm django python manage.py migrate

bash:
	docker compose -f local.yml run --rm  django  bash

test:
	docker compose -f local.yml run --rm  django  pytest

local-shell:
	docker compose -f local.yml run --rm  django python manage.py shell_plus

prod-migrate:
	docker compose -f production.yml run --rm django python manage.py migrate

prod-up:
	docker compose -f production.yml up -d --build
	docker compose -f production.yml run --rm django python manage.py migrate
	#docker compose -f production.yml run --rm django python manage.py fill_users_drill

prod-down:
	docker compose -f production.yml down

prod-shell:
	docker compose -f production.yml run --rm  django python manage.py shell_plus

prod-backup:
	docker compose -f production.yml run --rm postgres backup
