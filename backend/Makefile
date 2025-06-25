.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make install          Install dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make db-upgrade       Run database migrations"
	@echo "  make db-migrate       Create a new migration"
	@echo "  make db-downgrade     Downgrade database by one revision"
	@echo "  make db-history       Show migration history"
	@echo "  make db-current       Show current database revision"
	@echo "  make db-init          Initialize database with migrations"
	@echo "  make db-reset         Reset database (drop all tables and recreate)"
	@echo "  make seed             Seed database with sample data"
	@echo "  make seed-local       Seed database for local development"
	@echo "  make test             Run tests"
	@echo "  make test-cov         Run tests with coverage"
	@echo "  make lint             Run linters"
	@echo "  make format           Format code"
	@echo "  make clean            Clean cache files"
	@echo "  make run              Run development server"
	@echo "  make shell            Open Flask shell"

.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: install-dev
install-dev:
	pip install -r requirements-dev.txt

.PHONY: db-upgrade
db-upgrade:
	alembic upgrade head

.PHONY: db-migrate
db-migrate:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

.PHONY: db-downgrade
db-downgrade:
	alembic downgrade -1

.PHONY: db-history
db-history:
	alembic history --verbose

.PHONY: db-current
db-current:
	alembic current

.PHONY: db-init
db-init:
	alembic upgrade head
	@echo "Database initialized with migrations"

.PHONY: db-reset
db-reset:
	@echo "WARNING: This will drop all tables and recreate the database!"
	@read -p "Are you sure? (y/N) " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.drop_all(); db.create_all()"; \
		alembic stamp head; \
		echo "Database reset complete"; \
	else \
		echo "Database reset cancelled"; \
	fi

.PHONY: seed
seed:
	python -m app.utils.seed

.PHONY: seed-local
seed-local:
	python -m app.utils.seed --env local

.PHONY: test
test:
	pytest -v

.PHONY: test-cov
test-cov:
	pytest -v --cov=app --cov-report=html --cov-report=term

.PHONY: lint
lint:
	black --check app/ tests/
	flake8 app/ tests/
	isort --check-only app/ tests/
	mypy app/

.PHONY: format
format:
	black app/ tests/
	isort app/ tests/

.PHONY: clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

.PHONY: run
run:
	flask run --debug

.PHONY: shell
shell:
	flask shell