.PHONY: help build push dev-up dev-down prod-up prod-down migrate clean test lint

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

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

clean: ## Clean up Docker resources
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f

test: ## Run tests
	pytest tests/ -v

lint: ## Run linter
	ruff check src/

install: ## Install package in development mode
	pip install -e .

install-dev: ## Install package with all extras
	pip install -e .[all]
