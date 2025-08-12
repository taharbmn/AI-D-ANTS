# Makefile for AI-D-ANTS project

.PHONY: help build up down restart logs shell db-shell migrate status clean

help: ## Show this help message
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

build: ## Build the Docker containers
	docker-compose build

up: ## Start the services
	docker-compose up -d

down: ## Stop the services
	docker-compose down

restart: ## Restart the services
	docker-compose down && docker-compose up -d

logs: ## View logs
	docker-compose logs -f

shell: ## Access the web container shell
	docker-compose exec web bash

db-shell: ## Access the database shell
	docker-compose exec db psql -U user -d chat_app

migrate: ## Run database migrations
	docker-compose exec web python -m alembic upgrade head

status: ## Check migration status
	docker-compose exec web python -m alembic current

clean: ## Remove all containers and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

dev: ## Start development environment
	docker-compose down && docker-compose up --build

