.PHONY: help build push dev-up dev-down prod-up prod-down migrate clean test lint format check ci install install-dev install-test build-package

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development targets
install: ## Install package in development mode (base only)
	python -m pip install --upgrade pip
	pip install -e .

install-dev: ## Install package in development mode
	python -m pip install --upgrade pip
	pip install -e .

install-test: ## Install test dependencies
	python -m pip install --upgrade pip
	pip install pytest pytest-asyncio pytest-cov

lint: ## Run linter (ruff check)
	ruff check src/

format: ## Format code with ruff
	ruff format src/

format-check: ## Check code formatting without modifying
	ruff format --check src/

check: lint format-check ## Run linting and format checks

test: ## Run tests (base installation)
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=term --cov-report=xml


ci: check test-cov ## Run full CI checks locally (lint + format + test)

build-package: ## Build distribution packages (wheel and sdist)
	python -m pip install --upgrade pip build
	python -m build
	@echo "Built packages in dist/"

# Docker targets
build: ## Build Docker image
	docker build -t wisp-framework:latest .

push: ## Push Docker image to registry (set REGISTRY env var)
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Error: REGISTRY environment variable not set"; \
		exit 1; \
	fi
	docker tag wisp-framework:latest $(REGISTRY)/wisp-framework:latest
	docker push $(REGISTRY)/wisp-framework:latest

dev-up: ## Start development environment
	docker-compose up -d

dev-down: ## Stop development environment
	docker-compose down

prod-up: ## Start production environment
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down

migrate: ## Run database migrations
	@if [ -z "$(ENV)" ]; then \
		ENV=local docker-compose run --rm migrate; \
	else \
		docker-compose -f docker-compose.prod.yml run --rm migrate; \
	fi

clean: ## Clean up Docker resources and build artifacts
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
