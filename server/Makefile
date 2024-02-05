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

# django縺ｮ繧ｳ繝ｳ繝�繝翫�ｮ繧ｿ繝ｼ繝溘リ繝ｫ縺ｫ蜈･繧九さ繝槭Φ繝�
.PHONY: exec
exec:
	docker compose -f docker-compose-dev.yml exec django bash
