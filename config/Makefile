.PHONY: help install dev build test clean docker-up docker-down lint format

# Colores para output
BLUE=\033[0;34m
GREEN=\033[0;32m
NC=\033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(BLUE)Sistema de Flujo de Caja - Bolívar$(NC)"
	@echo ""
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instalar todas las dependencias
	@echo "$(BLUE)Instalando dependencias del backend...$(NC)"
	cd Back-FC && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt
	@echo "$(BLUE)Instalando dependencias del frontend...$(NC)"
	cd Front-FC && npm install
	@echo "$(GREEN)✅ Instalación completada$(NC)"

dev: ## Ejecutar backend y frontend en desarrollo
	@echo "$(BLUE)Iniciando servicios de desarrollo...$(NC)"
	make dev-backend &
	make dev-frontend &

dev-backend: ## Ejecutar solo backend
	cd Back-FC && . .venv/bin/activate && python run_server.py

dev-frontend: ## Ejecutar solo frontend
	cd Front-FC && npm run dev

build: ## Build de producción
	@echo "$(BLUE)Construyendo backend...$(NC)"
	cd Back-FC && . .venv/bin/activate && black app/ && flake8 app/
	@echo "$(BLUE)Construyendo frontend...$(NC)"
	cd Front-FC && npm run build
	@echo "$(GREEN)✅ Build completado$(NC)"

test: ## Ejecutar todos los tests
	@echo "$(BLUE)Ejecutando tests del backend...$(NC)"
	cd Back-FC && . .venv/bin/activate && pytest --cov=app
	@echo "$(BLUE)Ejecutando tests del frontend...$(NC)"
	cd Front-FC && npm test
	@echo "$(GREEN)✅ Tests completados$(NC)"

test-backend: ## Ejecutar tests del backend
	cd Back-FC && . .venv/bin/activate && pytest -v

test-frontend: ## Ejecutar tests del frontend
	cd Front-FC && npm test

lint: ## Verificar código
	@echo "$(BLUE)Verificando backend...$(NC)"
	cd Back-FC && . .venv/bin/activate && flake8 app/ && black app/ --check
	@echo "$(BLUE)Verificando frontend...$(NC)"
	cd Front-FC && npm run lint
	@echo "$(GREEN)✅ Linting completado$(NC)"

format: ## Formatear código
	@echo "$(BLUE)Formateando backend...$(NC)"
	cd Back-FC && . .venv/bin/activate && black app/ && isort app/
	@echo "$(BLUE)Formateando frontend...$(NC)"
	cd Front-FC && npm run lint:fix
	@echo "$(GREEN)✅ Formato aplicado$(NC)"

clean: ## Limpiar archivos temporales
	@echo "$(BLUE)Limpiando archivos temporales...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

docker-up: ## Iniciar con Docker Compose
	@echo "$(BLUE)Iniciando contenedores...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Contenedores iniciados$(NC)"

docker-down: ## Detener Docker Compose
	@echo "$(BLUE)Deteniendo contenedores...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Contenedores detenidos$(NC)"

docker-logs: ## Ver logs de Docker
	docker-compose logs -f

db-migrate: ## Ejecutar migraciones de base de datos
	cd Back-FC && . .venv/bin/activate && alembic upgrade head

db-rollback: ## Revertir última migración
	cd Back-FC && . .venv/bin/activate && alembic downgrade -1

setup: ## Setup inicial completo del proyecto
	@echo "$(BLUE)Configurando proyecto...$(NC)"
	@if [ ! -f Back-FC/.env ]; then cp Back-FC/.env.example Back-FC/.env; echo "Creado Back-FC/.env"; fi
	@if [ ! -f Front-FC/.env ]; then cp Front-FC/.env.example Front-FC/.env; echo "Creado Front-FC/.env"; fi
	@if [ ! -f .env ]; then cp .env.example .env; echo "Creado .env"; fi
	make install
	@echo "$(GREEN)✅ Setup completado. Edita los archivos .env antes de continuar$(NC)"
