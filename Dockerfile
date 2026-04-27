# =============================================================================
# Dockerfile — BPS Stat Agent (bps-stat-agent)
# Multi-stage build: builder → runtime
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: builder — install deps, compile, prepare venv
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

LABEL stage="builder"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps needed for building wheels and git-based deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install uv — fast Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency manifests first (layer cache optimisation)
COPY pyproject.toml uv.lock ./

# Install production deps into the project venv
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the source tree
COPY . .

# Install the project itself into the existing venv
RUN uv sync --frozen --no-dev


# ---------------------------------------------------------------------------
# Stage 2: runtime — lean image with only what's needed
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# -- Metadata ----------------------------------------------------------------
LABEL maintainer="Julio Christian Wadu Doko <juliochwd@gmail.com>" \
      version="0.1.3" \
      description="BPS Indonesia Statistical Data Agent — search and query BPS data via AllStats Search Engine and WebAPI"

# -- Environment -------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Put venv on PATH so entry-point scripts resolve without `uv run`
    PATH="/app/.venv/bin:${PATH}" \
    # Playwright browser location (shared, not under /root)
    PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright

# -- System deps for runtime (Playwright needs libs at runtime) ---------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# -- Copy built venv + source from builder -----------------------------------
WORKDIR /app
COPY --from=builder /app /app

# -- Install Playwright Chromium + OS deps -----------------------------------
# `playwright install --with-deps` pulls the browser binary AND the required
# shared libraries (libatk, libnss3, etc.) via apt.
RUN playwright install --with-deps chromium

# -- Non-root user -----------------------------------------------------------
RUN groupadd --system agent && \
    useradd --system --gid agent --create-home --home-dir /home/agent agent

# -- Create required directories & fix ownership ------------------------------
RUN mkdir -p \
        /app/workspace \
        /home/agent/.bps-stat-agent/config \
        /home/agent/.bps-stat-agent/log && \
    chown -R agent:agent \
        /app/workspace \
        /home/agent \
        /opt/ms-playwright

# -- Switch to non-root ------------------------------------------------------
USER agent

# -- Health check (import smoke test via venv python) -------------------------
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import mini_agent; print(mini_agent.__version__)"]

# -- Default command (CLI mode) -----------------------------------------------
CMD ["bps-stat-agent"]
