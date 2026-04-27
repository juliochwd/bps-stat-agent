# Production Guide

> Deploying, operating, and monitoring BPS Stat Agent in production environments.

## Table of Contents

- [1. Overview](#1-overview)
- [2. Quick Start with Docker](#2-quick-start-with-docker)
- [3. Docker Compose](#3-docker-compose)
- [4. Makefile Reference](#4-makefile-reference)
- [5. Configuration](#5-configuration)
- [6. Observability](#6-observability)
  - [6.1 Structured Logging](#61-structured-logging)
  - [6.2 Prometheus Metrics](#62-prometheus-metrics)
  - [6.3 OpenTelemetry Tracing](#63-opentelemetry-tracing)
  - [6.4 Health Checks](#64-health-checks)
- [7. CI/CD Pipeline](#7-cicd-pipeline)
- [8. Security Hardening](#8-security-hardening)
- [9. Resource Limits](#9-resource-limits)
- [10. Kubernetes Deployment](#10-kubernetes-deployment)
- [11. Upgrade Directions](#11-upgrade-directions)
- [12. Production Checklist](#12-production-checklist)

---

## 1. Overview

BPS Stat Agent ships with production-grade infrastructure:

| Capability              | Implementation                                                                 |
| ----------------------- | ------------------------------------------------------------------------------ |
| **Container Image**     | Multi-stage Dockerfile (builder + runtime), python:3.11-slim, non-root user    |
| **Orchestration**       | docker-compose.yml with 3 service profiles (cli/mcp/acp), resource limits      |
| **Build Automation**    | Makefile with 20+ targets covering install, lint, test, build, Docker, and run  |
| **CI/CD**               | GitHub Actions — lint, test, security audit, build (Python 3.11/3.12 matrix)   |
| **Logging**             | Centralized JSON logging to stdout (12-factor compatible)                      |
| **Metrics**             | Prometheus metrics (agent runs, LLM requests, tokens, tool calls)              |
| **Tracing**             | OpenTelemetry distributed tracing with OTLP export                             |
| **Health Checks**       | HTTP endpoints (/health, /ready, /metrics) via background thread               |
| **Security**            | Bash tool disabled by default, non-root container, secrets excluded from image  |

---

## 2. Quick Start with Docker

```bash
# 1. Clone and enter the project
git clone https://github.com/juliochwd/bps-stat-agent.git
cd bps-stat-agent

# 2. Create environment file
cp .env.example .env
# Edit .env — set at least one LLM API key

# 3. Copy config
mkdir -p config
cp mini_agent/config/config-example.yaml config/config.yaml
# Edit config/config.yaml — set api_key, model, provider

# 4. Build the image
docker compose build

# 5. Run (choose a profile)
docker compose --profile cli run --rm agent          # Interactive CLI
docker compose --profile mcp up -d                   # MCP server (background)
docker compose --profile acp up -d                   # ACP server (background)
```

### Dockerfile Architecture

The image uses a **multi-stage build** to minimize the final image size:

| Stage       | Base Image          | Purpose                                                    |
| ----------- | ------------------- | ---------------------------------------------------------- |
| `builder`   | python:3.11-slim    | Install uv, sync dependencies, compile wheels              |
| `runtime`   | python:3.11-slim    | Copy venv from builder, install Playwright chromium, run    |

Key features:
- **uv** package manager (copied from `ghcr.io/astral-sh/uv:latest`) for fast, reproducible installs
- **Layer caching** — `pyproject.toml` and `uv.lock` copied before source for optimal cache hits
- **Playwright chromium** installed with OS deps in the runtime stage
- **Non-root user** `agent` with dedicated home directory `/home/agent`
- **HEALTHCHECK** built into the image (import smoke test every 30s)

---

## 3. Docker Compose

The `docker-compose.yml` defines three services, activated via **profiles**:

| Service       | Profile | Command              | Description                    |
| ------------- | ------- | -------------------- | ------------------------------ |
| `agent`       | `cli`   | `bps-stat-agent`     | Interactive CLI session        |
| `mcp-server`  | `mcp`   | `bps-mcp-server`     | MCP server (stdio, long-lived) |
| `acp-server`  | `acp`   | `bps-stat-agent-acp` | ACP server (long-lived)        |

### Usage

```bash
# Interactive CLI (one-shot)
docker compose --profile cli run --rm agent

# Start MCP server in background
docker compose --profile mcp up -d

# Start ACP server in background
docker compose --profile acp up -d

# View logs
docker compose logs -f

# Stop everything
docker compose down
```

### Environment Variables

API keys are passed via environment variables. The compose file supports two methods:

1. **Host environment** — export `ANTHROPIC_AUTH_TOKEN`, `OPENAI_API_KEY`, or `MINIMAX_API_KEY` before running
2. **`.env` file** — create a `.env` file in the project root (optional, not required)

### Volumes

| Mount                                          | Purpose                          |
| ---------------------------------------------- | -------------------------------- |
| `./config:/home/agent/.bps-stat-agent/config:ro` | Config directory (read-only)   |
| `./workspace:/app/workspace`                   | Agent workspace (read-write)     |
| Named volume for logs                          | Persistent log storage           |
| `tmpfs /tmp` (1GB)                             | Ephemeral temp files             |

### Resource Limits

Every service is constrained to:
- **CPU**: 2 cores max, 0.5 cores reserved
- **Memory**: 2GB max, 512MB reserved
- **Temp disk**: 1GB tmpfs on `/tmp`

---

## 4. Makefile Reference

Run `make help` to see all targets. Summary:

| Category        | Target          | Description                                      |
| --------------- | --------------- | ------------------------------------------------ |
| **Setup**       | `install`       | Install production deps (frozen lockfile)         |
|                 | `install-dev`   | Install all deps + dev group + Playwright         |
|                 | `setup`         | Full first-time setup (install-dev + seed config) |
| **Quality**     | `lint`          | Run ruff linter on source and tests               |
|                 | `format`        | Auto-format code with ruff                        |
|                 | `check`         | Run lint + tests (quality gate)                   |
| **Testing**     | `test`          | Run tests (excluding live/network tests)          |
|                 | `test-cov`      | Run tests with coverage report                    |
|                 | `test-live`     | Run only live BPS integration tests               |
|                 | `test-all`      | Run all tests (unit + live)                       |
| **Build**       | `build`         | Build sdist and wheel                             |
|                 | `clean`         | Remove build artifacts and caches                 |
| **Docker**      | `docker-build`  | Build Docker images via compose                   |
|                 | `docker-up`     | Start services (MCP profile) in background        |
|                 | `docker-down`   | Stop and remove all containers                    |
|                 | `docker-logs`   | Tail logs from all services                       |
| **Run**         | `run`           | Start interactive CLI                             |
|                 | `run-mcp`       | Start MCP server                                  |
|                 | `run-acp`       | Start ACP server                                  |
|                 | `run-task`      | Run agent with a task: `make run-task TASK="..."` |

---

## 5. Configuration

### Config File Locations (priority order)

1. `mini_agent/config/config.yaml` — development (current directory)
2. `~/.bps-stat-agent/config/config.yaml` — user config directory
3. `<package>/mini_agent/config/config.yaml` — package installation directory

### Environment Variables (`.env`)

Copy `.env.example` to `.env` and set your values:

```bash
# LLM API Key (required — choose one)
ANTHROPIC_AUTH_TOKEN=your-key
# OPENAI_API_KEY=your-key
# MINIMAX_API_KEY=your-key

# BPS WebAPI Key (required for BPS data access)
BPS_API_KEY=your-key

# Optional
LOG_LEVEL=INFO
LOG_JSON_OUTPUT=false
```

### Config YAML — Logging & Tracing Sections

```yaml
# ===== Logging Configuration =====
logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  json_output: false      # true for production (JSON to stdout), false for development
  # log_file: null        # Optional: path to additional log file

# ===== Tracing Configuration =====
tracing:
  enabled: false          # Enable OpenTelemetry tracing
  exporter: "none"        # "none", "console", or "otlp"
  # otlp_endpoint: "http://localhost:4317"  # OTLP gRPC endpoint
```

---

## 6. Observability

Observability features are **optional** — the agent runs without them. Install extras as needed:

```bash
pip install bps-stat-agent[metrics]        # Prometheus metrics
pip install bps-stat-agent[tracing]        # OpenTelemetry tracing
pip install bps-stat-agent[observability]  # Both
```

If the optional packages are not installed, all metric/tracing operations become **silent no-ops** — no errors, no overhead.

### 6.1 Structured Logging

**Module**: `mini_agent/logging_config.py`

The centralized logging system follows 12-factor app principles — all logs go to **stdout**.

| Mode        | Format                                          | Use Case    |
| ----------- | ----------------------------------------------- | ----------- |
| Production  | `json_output: true` — structured JSON per line  | Log aggregators (ELK, Loki, CloudWatch) |
| Development | `json_output: false` — human-readable text      | Local development |

JSON log entry example:
```json
{
  "timestamp": "2025-01-15T10:30:00.123456+00:00",
  "level": "INFO",
  "logger": "mini_agent.agent",
  "message": "Agent run completed",
  "module": "agent",
  "function": "run",
  "line": 142
}
```

Noisy loggers (`httpx`, `httpcore`, `urllib3`, `asyncio`) are automatically suppressed to WARNING level.

### 6.2 Prometheus Metrics

**Module**: `mini_agent/metrics.py`

Requires: `pip install bps-stat-agent[metrics]`

10 metrics are exposed, covering three domains:

| Metric                          | Type      | Labels                          | Description                    |
| ------------------------------- | --------- | ------------------------------- | ------------------------------ |
| `agent_runs_total`              | Counter   | `status`                        | Total agent runs               |
| `agent_steps_total`             | Counter   | —                               | Total steps executed           |
| `agent_run_duration_seconds`    | Histogram | —                               | Duration of agent runs         |
| `agent_active_runs`             | Gauge     | —                               | Currently active runs          |
| `llm_requests_total`            | Counter   | `provider`, `model`, `status`   | Total LLM API requests         |
| `llm_request_duration_seconds`  | Histogram | `provider`, `model`             | LLM request latency            |
| `llm_tokens_total`              | Counter   | `provider`, `model`, `type`     | Tokens consumed (prompt/completion) |
| `llm_retries_total`             | Counter   | `provider`, `model`             | LLM retry attempts             |
| `tool_calls_total`              | Counter   | `tool_name`, `status`           | Tool executions                |
| `tool_call_duration_seconds`    | Histogram | `tool_name`                     | Tool execution latency         |

Metrics are served at the `/metrics` endpoint of the health check server (see [6.4](#64-health-checks)).

**Prometheus scrape config**:
```yaml
scrape_configs:
  - job_name: "bps-stat-agent"
    static_configs:
      - targets: ["agent-host:8080"]
    metrics_path: /metrics
```

### 6.3 OpenTelemetry Tracing

**Module**: `mini_agent/tracing.py`

Requires: `pip install bps-stat-agent[tracing]`

Provides distributed tracing across agent runs, LLM calls, and tool executions. Three convenience functions create properly attributed spans:

| Function           | Span Name        | Attributes                              |
| ------------------ | ---------------- | --------------------------------------- |
| `trace_agent_run`  | `agent.run`      | `agent.run_id`                          |
| `trace_llm_call`   | `llm.generate`   | `llm.provider`, `llm.model`            |
| `trace_tool_call`  | `tool.execute`   | `tool.name`, `tool.argument_keys`       |

Supported exporters:

| Exporter  | Config                                    | Backend                        |
| --------- | ----------------------------------------- | ------------------------------ |
| `none`    | `exporter: "none"` (default)              | Disabled                       |
| `console` | `exporter: "console"`                     | Stdout (debugging)             |
| `otlp`    | `exporter: "otlp"` + `otlp_endpoint`     | Jaeger, Zipkin, Grafana Tempo  |

Environment variable overrides: `OTEL_EXPORTER`, `OTEL_EXPORTER_OTLP_ENDPOINT`.

### 6.4 Health Checks

**Module**: `mini_agent/health.py`

A lightweight HTTP server runs in a **background thread** alongside the main agent process.

| Endpoint   | Purpose                                    | Response                                |
| ---------- | ------------------------------------------ | --------------------------------------- |
| `/health`  | Liveness — is the process alive?           | `200` with uptime, version, timestamp   |
| `/ready`   | Readiness — can it accept work?            | `200` or `503` based on ready check     |
| `/metrics` | Prometheus metrics (if installed)           | `200` with metrics text or `404`        |

Usage in code:
```python
from mini_agent.health import start_health_server, stop_health_server

start_health_server(port=8080)
# ... agent runs ...
stop_health_server()
```

**Docker HEALTHCHECK** (built into the Dockerfile):
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import mini_agent; print(mini_agent.__version__)"]
```

---

## 7. CI/CD Pipeline

Two GitHub Actions workflows run on every push/PR to `main`/`master`:

### CI Pipeline (`.github/workflows/ci.yml`)

```
lint → test → security → build
```

| Job        | Python Matrix | Description                                              |
| ---------- | ------------- | -------------------------------------------------------- |
| **lint**   | 3.11, 3.12    | `ruff check` + `ruff format --check`                    |
| **test**   | 3.11, 3.12    | `pytest` with coverage (excludes live tests), uploads XML |
| **security** | 3.12        | `pip-audit --strict --desc` for dependency vulnerabilities |
| **build**  | 3.12          | `uv build` — produces sdist + wheel, uploads as artifact |

Jobs run sequentially: test depends on lint, build depends on test + security.

### Docker Build (`.github/workflows/docker.yml`)

| Job              | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| **docker-build** | Builds the Docker image (no push) with BuildKit layer caching |

Both workflows use `concurrency` groups to cancel in-progress runs on new pushes.

---

## 8. Security Hardening

### Bash Tool Disabled by Default

The `enable_bash` setting defaults to `false` in `config-example.yaml` and in the code (`config.py`). This prevents the agent from executing arbitrary shell commands unless explicitly enabled:

```yaml
tools:
  enable_bash: false  # Default — enable only if your use case requires it
```

### Non-Root Container

The Dockerfile creates a dedicated `agent` user and group:
```dockerfile
RUN groupadd --system agent && \
    useradd --system --gid agent --create-home --home-dir /home/agent agent
USER agent
```

The agent process, Playwright browser data, workspace, and logs are all owned by this non-root user.

### Secrets Excluded from Image

The `.dockerignore` excludes:
- `.env`, `.env.*` — environment files with API keys
- `config.yaml` — may contain `api_key`
- `mcp.json` — may contain MCP tool credentials

Secrets are injected at runtime via environment variables or mounted config volumes (read-only).

### File System Permissions

```bash
# Restrict workspace directory
mkdir -p /app/workspace
chown agent:agent /app/workspace
chmod 750 /app/workspace

# Restrict config directory
chmod 700 /etc/agent
chmod 600 /etc/agent/*.yaml
```

---

## 9. Resource Limits

### CPU and Memory

All Docker Compose services enforce identical limits:

```yaml
deploy:
  resources:
    limits:
      cpus: "2"        # Maximum 2 CPU cores
      memory: 2G       # Maximum 2GB memory
    reservations:
      cpus: "0.5"      # Guarantee at least 0.5 cores
      memory: 512M     # Guarantee at least 512MB
```

### Disk

Temporary files are constrained via tmpfs:

```yaml
tmpfs:
  - /tmp:size=1G       # Maximum 1GB for temporary files
```

Logs are stored in named Docker volumes (`agent-logs`, `mcp-logs`, `acp-logs`) to persist across container restarts.

---

## 10. Kubernetes Deployment

The health check endpoints map directly to K8s probes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bps-stat-agent
spec:
  template:
    spec:
      containers:
        - name: agent
          image: bps-stat-agent:latest
          ports:
            - containerPort: 8080
              name: health
          livenessProbe:
            httpGet:
              path: /health
              port: health
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: health
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          securityContext:
            runAsNonRoot: true
            runAsUser: 999
            readOnlyRootFilesystem: false  # Playwright needs writable dirs
          env:
            - name: ANTHROPIC_AUTH_TOKEN
              valueFrom:
                secretKeyRef:
                  name: agent-secrets
                  key: anthropic-token
```

For Prometheus metrics scraping, add the standard annotations:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

---

## 11. Upgrade Directions

These areas remain as future improvements beyond the current infrastructure:

### Advanced Context Management
- Distributed file systems for unified context persistence and backup
- More precise token counting methods
- Additional message compression strategies (recent-N, fixed metadata, recall systems)

### Model Fallback Mechanism
- Model pool with multiple accounts and providers
- Automatic health checks, failure removal, circuit breaker strategies
- Cross-provider fallback (e.g., Anthropic → OpenAI)

### Model Hallucination Detection
- Security checks on tool call input parameters
- Reflection on tool call results for reasonableness validation

---

## 12. Production Checklist

### Before First Deploy

- [ ] Set LLM API key(s) in `.env` or K8s secrets
- [ ] Set BPS API key if using BPS data access
- [ ] Copy and customize `config-example.yaml` → `config.yaml`
- [ ] Verify `enable_bash: false` unless explicitly needed
- [ ] Build Docker image: `make docker-build`
- [ ] Run tests: `make test`

### Observability

- [ ] Set `logging.json_output: true` for production
- [ ] Install metrics extra if using Prometheus: `pip install bps-stat-agent[metrics]`
- [ ] Install tracing extra if using OpenTelemetry: `pip install bps-stat-agent[tracing]`
- [ ] Configure Prometheus scrape target for `/metrics` on port 8080
- [ ] Configure tracing exporter (`otlp`) and endpoint if using distributed tracing

### Container Security

- [ ] Verify container runs as non-root (`USER agent`)
- [ ] Secrets are injected via env vars or mounted volumes, never baked into image
- [ ] Config volume mounted read-only (`:ro`)
- [ ] `.dockerignore` excludes `.env`, `config.yaml`, `mcp.json`

### Resource Limits

- [ ] CPU and memory limits set (default: 2 CPU, 2GB)
- [ ] tmpfs configured for `/tmp` (default: 1GB)
- [ ] Log volumes configured for persistence

### CI/CD

- [ ] GitHub Actions CI passing (lint, test, security, build)
- [ ] Docker build workflow passing
- [ ] Coverage reports being uploaded

### Kubernetes (if applicable)

- [ ] Liveness probe → `/health`
- [ ] Readiness probe → `/ready`
- [ ] Secrets stored in K8s Secret objects
- [ ] Resource requests and limits configured
- [ ] `runAsNonRoot: true` in security context
