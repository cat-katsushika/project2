.PHONY: dev-build
dev-build:
	docker compose -f docker-compose-dev.yml build

.PHONY: dev-up-d
dev-up-d:
	docker compose -f docker-compose-dev.yml up -d

.PHONY: dev
dev:
	@make dev-build
	@make dev-up-d

.PHONY: down
down:
	docker compose -f docker-compose-dev.yml down

.PHONY: logs
logs:
	docker compose -f docker-compose-dev.yml logs -f

.PHONY: test
test:
	docker compose -f docker-compose-dev.yml exec django python manage.py test

.PHONY: black
black:
	docker compose -f docker-compose-dev.yml exec django black .

.PHONY: isort
isort:
	docker compose -f docker-compose-dev.yml exec django isort .

.PHONY: flake8
flake8:
	docker compose -f docker-compose-dev.yml exec django flake8 .

.PHONY: lint
lint:
	@make black
	@make isort
	@make flake8

.PHONY: exec
exec:
	docker compose -f docker-compose-dev.yml exec django bash

.PHONY: delete
delete:
	rm -rf db/
