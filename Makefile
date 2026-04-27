# ============================================================================
# BPS Stat Agent — Makefile
# ============================================================================
# Package : bps-stat-agent
# Manager : uv (https://docs.astral.sh/uv/)
# Python  : >=3.10
# ============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Paths
SRC_DIR     := mini_agent
TEST_DIR    := tests
CONFIG_DIR  := $(HOME)/.bps-stat-agent/config
CONFIG_DEST := $(CONFIG_DIR)/config.yaml
CONFIG_SRC  := $(SRC_DIR)/config/config-example.yaml

# Colors (only when stdout is a terminal)
ifneq ($(TERM),dumb)
  CYAN  := \033[36m
  GREEN := \033[32m
  BOLD  := \033[1m
  RESET := \033[0m
else
  CYAN  :=
  GREEN :=
  BOLD  :=
  RESET :=
endif

# ============================================================================
# Help
# ============================================================================

.PHONY: help
help: ## Show this help message
	@printf "\n$(BOLD)BPS Stat Agent$(RESET) — available targets:\n\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-16s$(RESET) %s\n", $$1, $$2}'
	@printf "\n"

# ============================================================================
# Setup
# ============================================================================

.PHONY: install install-dev setup

install: ## Install production dependencies (frozen lockfile)
	uv sync --frozen

install-dev: ## Install all dependencies including dev group + Playwright
	uv sync --frozen --group dev
	uv run playwright install --with-deps chromium

setup: install-dev ## Full first-time setup (install-dev + seed config)
	@mkdir -p $(CONFIG_DIR)
	@if [ ! -f $(CONFIG_DEST) ]; then \
		cp $(CONFIG_SRC) $(CONFIG_DEST); \
		printf "$(GREEN)✓$(RESET) Config seeded → $(CONFIG_DEST)\n"; \
	else \
		printf "  Config already exists → $(CONFIG_DEST) (skipped)\n"; \
	fi

# ============================================================================
# Code Quality
# ============================================================================

.PHONY: lint format check

lint: ## Run ruff linter on source and tests
	uvx ruff check $(SRC_DIR)/ $(TEST_DIR)/

format: ## Auto-format code with ruff
	uvx ruff format $(SRC_DIR)/ $(TEST_DIR)/

check: lint test ## Run lint + tests (quality gate)

# ============================================================================
# Testing
# ============================================================================

.PHONY: test test-cov test-live test-all

test: ## Run tests (excluding live/network tests)
	uv run pytest $(TEST_DIR)/ -x -v -m "not live"

test-cov: ## Run tests with coverage report
	uv run pytest $(TEST_DIR)/ \
		--cov=$(SRC_DIR) \
		--cov-report=term-missing \
		--cov-report=html \
		-m "not live"

test-live: ## Run only live BPS integration tests
	uv run pytest $(TEST_DIR)/ -x -v -m live

test-all: ## Run all tests (unit + live)
	uv run pytest $(TEST_DIR)/ -x -v

# ============================================================================
# Build & Clean
# ============================================================================

.PHONY: build clean

build: clean ## Build sdist and wheel
	uv build

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info $(SRC_DIR)/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache workspace/.pytest_cache htmlcov/
	rm -f .coverage coverage.xml coverage.json coverage.lcov

# ============================================================================
# Docker
# ============================================================================

.PHONY: docker-build docker-up docker-down docker-logs

docker-build: ## Build Docker images via compose
	docker compose build

docker-up: ## Start services (MCP profile) in background
	docker compose --profile mcp up -d

docker-down: ## Stop and remove all containers
	docker compose down

docker-logs: ## Tail logs from all services
	docker compose logs -f

# ============================================================================
# Run
# ============================================================================

.PHONY: run run-mcp run-acp run-task

run: ## Start the BPS Stat Agent (interactive CLI)
	uv run bps-stat-agent

run-mcp: ## Start the BPS MCP Server
	uv run bps-mcp-server

run-acp: ## Start the BPS ACP Server
	uv run bps-stat-agent-acp

run-task: ## Run agent with a task — usage: make run-task TASK="your query"
	@if [ -z "$(TASK)" ]; then \
		printf "$(CYAN)Usage:$(RESET) make run-task TASK=\"Cari data IPM NTT 2023\"\n"; \
		exit 1; \
	fi
	uv run bps-stat-agent --task "$(TASK)"
