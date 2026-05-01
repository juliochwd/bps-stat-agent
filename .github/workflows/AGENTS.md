<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# workflows

## Purpose
GitHub Actions CI/CD pipeline definitions. Two workflows handle continuous integration (linting, testing, security audit, package build) and Docker image verification on every push and pull request to `main`/`master`.

## Key Files
| File | Description |
|------|-------------|
| `ci.yml` | Full CI pipeline with 4 jobs: **lint** (ruff check + format on Python 3.11/3.12), **test** (pytest with coverage, excludes `@pytest.mark.live`, installs Playwright Chromium; depends on lint), **security** (pip-audit for dependency vulnerabilities), **build** (package build via `uv build`; depends on test + security). Uses `uv sync --frozen` for reproducible installs and matrix strategy across Python 3.11 and 3.12. Uploads coverage XML and dist artifacts with 30-day retention. |
| `docker.yml` | Docker image build verification. Uses Docker Buildx with GitHub Actions cache (`type=gha`). Builds the image tagged `bps-stat-agent:ci-<sha>` without pushing. Validates that the Dockerfile builds successfully on every push/PR. |

## For AI Agents

### Working In This Directory
- Both workflows use `concurrency` groups with `cancel-in-progress: true` to avoid redundant runs on rapid pushes
- Both workflows set `permissions: contents: read` (least-privilege)
- Dependencies are installed via `uv sync --frozen --group dev` using the locked `uv.lock` file
- The `astral-sh/setup-uv@v4` action is used with cache enabled, keyed on `uv.lock`
- Python versions are set up via `actions/setup-python@v5`
- The CI test job installs Playwright Chromium browsers (`uv run playwright install --with-deps chromium`) because AllStats search tests require a browser
- Tests run with `pytest -x -v --cov=mini_agent -m "not live"` (fail-fast, verbose, coverage, skip live/network tests)
- The build job only runs after both test and security jobs pass (dependency chain: lint -> test -> build, lint -> security -> build)
- Docker build uses `docker/build-push-action@v6` with `push: false` (verification only, no registry push)

### Testing Requirements
- Workflow syntax can be validated locally with `actionlint` if installed
- Changes to CI should be tested by pushing to a feature branch and observing the Actions tab
- If adding new test markers or dependencies, update the `uv sync` and `pytest` commands accordingly
- The `--frozen` flag means `uv.lock` must be committed and up-to-date; if dependencies change in `pyproject.toml`, run `uv lock` first

### Key Actions Used
| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout` | v4 | Clone repository |
| `astral-sh/setup-uv` | v4 | Install uv package manager with caching |
| `actions/setup-python` | v5 | Install Python (matrix: 3.11, 3.12) |
| `actions/upload-artifact` | v4 | Upload coverage and dist artifacts |
| `docker/setup-buildx-action` | v3 | Set up Docker Buildx builder |
| `docker/build-push-action` | v6 | Build Docker image (no push) |

## Dependencies

### Internal
- `pyproject.toml` — defines the `dev` dependency group installed by CI
- `uv.lock` — locked dependency versions used by `uv sync --frozen`
- `Dockerfile` — built and verified by `docker.yml`
- `ruff.toml` — linter/formatter configuration used by the lint job
- `mini_agent/` and `tests/` — source and test directories targeted by lint and test jobs

### External
- GitHub Actions runners (`ubuntu-latest`)
- `uv` package manager (installed via `astral-sh/setup-uv`)
- `ruff` (linter/formatter, installed as dev dependency)
- `pytest`, `pytest-asyncio`, `pytest-cov` (test framework, installed as dev dependencies)
- `pip-audit` (security vulnerability scanner, installed as dev dependency)
- `playwright` (browser automation, Chromium installed in CI for AllStats tests)
- Docker Buildx (for image build verification)

<!-- MANUAL: -->
