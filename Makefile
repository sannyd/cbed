build:
	docker-compose -f local.yml build

up:
	docker-compose -f local.yml up -d

down:
	docker-compose -f local.yml down

migrate:
	docker-compose -f local.yml run --rm django python manage.py makemigrations
	docker-compose -f local.yml run --rm django python manage.py migrate

shell:
	docker-compose -f local.yml run --rm  django python manage.py shell_plus

prod-migrate:
	docker-compose -f production.yml run --rm django python manage.py migrate

prod-up:
	docker-compose -f production.yml up -d --build
	docker-compose -f production.yml run --rm django python manage.py migrate

prod-down:
	docker-compose -f production.yml down

prod-shell:
	docker-compose -f production.yml run --rm  django python manage.py shell_plus

prod-backup:
	docker-compose -f production.yml run --rm postgres backup
