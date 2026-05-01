<!-- Parent: ../AGENTS.md -->
# AGENTS.md — docs/

> **Parent:** [../AGENTS.md](../AGENTS.md)
> **Updated:** 2026-05-01

## Purpose

Project documentation for the BPS Stat Agent. Contains developer setup guides, production deployment instructions, visual assets (logo, demo GIFs), and advanced capability specifications (superpowers). These are reference documents — the source of truth for how to develop, deploy, and operate the agent.

## Key Files

| File | Purpose |
|---|---|
| `DEVELOPMENT_GUIDE.md` | Comprehensive developer guide: project setup, architecture overview, module descriptions, contribution workflow, coding standards, testing strategy, debugging tips. Start here for understanding the codebase. (~19KB) |
| `PRODUCTION_GUIDE.md` | Production deployment guide: Docker configuration, environment variables, health checks, monitoring (Prometheus + OpenTelemetry), scaling strategies, security hardening, backup procedures, troubleshooting. (~21KB) |

## Subdirectories

| Directory | Purpose |
|---|---|
| `assets/` | Visual assets for documentation and GitHub repository |
| `superpowers/` | Advanced capability specifications and implementation plans |

### assets/

| File | Purpose |
|---|---|
| `logo.png` | Project logo used in README.md header and GitHub repository |
| `social-preview.png` | GitHub social preview image (displayed when sharing repo links) |
| `demo1-task-execution.gif` | Demo GIF: agent executing a BPS data query task |
| `demo2-claude-skill.gif` | Demo GIF: Claude skill activation and progressive disclosure |
| `demo3-web-search.gif` | Demo GIF: web search and data retrieval workflow |

### superpowers/

Advanced capability documentation organized into specs (design documents) and plans (implementation roadmaps):

| File | Purpose |
|---|---|
| `specs/2026-04-23-bps-agent-production-design.md` | Production design specification: architecture decisions, component design, API contracts, data flow diagrams, security model |
| `plans/2026-04-23-bps-agent-production-implementation.md` | Implementation plan: milestones, task breakdown, timeline, dependencies, risk assessment |

## For AI Agents

### Working In This Directory

1. **Start with DEVELOPMENT_GUIDE.md** for understanding project architecture, module relationships, and development workflow.
2. **Refer to PRODUCTION_GUIDE.md** for deployment configuration, Docker compose profiles, health check endpoints, and observability setup.
3. **Do not modify assets/** unless updating logos or creating new demo recordings.
4. **Superpowers docs** are historical design documents. They capture architectural decisions and rationale. Reference them for understanding "why" decisions were made, but check current source code for "what" is actually implemented.
5. **Documentation updates:** When making significant code changes, check if `DEVELOPMENT_GUIDE.md` or `PRODUCTION_GUIDE.md` need corresponding updates.
6. **Image references:** Assets are referenced from `README.md` via GitHub raw URLs: `https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/docs/assets/`.
7. **For code-level documentation:** Refer to docstrings in source files under `mini_agent/`, not these guides.

### Document Relationships

```
README.md (project root)
  |-- references docs/assets/ for images and GIFs
  |-- links to docs/DEVELOPMENT_GUIDE.md for detailed setup
  |-- links to docs/PRODUCTION_GUIDE.md for deployment

docs/DEVELOPMENT_GUIDE.md
  |-- references mini_agent/ source code structure
  |-- references Makefile targets
  |-- references pyproject.toml configuration

docs/PRODUCTION_GUIDE.md
  |-- references Dockerfile and docker-compose.yml
  |-- references .env.example for environment variables
  |-- references mini_agent/config/ for configuration files
  |-- references mini_agent/health.py for health checks
  |-- references mini_agent/metrics.py for Prometheus
  |-- references mini_agent/tracing.py for OpenTelemetry
```

## Dependencies

### Internal

- References `mini_agent/` source code, `Makefile`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `.env.example`
- Assets referenced by `README.md` in project root

### External

- None (static documentation and image files)
