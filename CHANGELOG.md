# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.3] - 2026-04-26

### Added
- **BPS data retriever** with comprehensive statistics support (poverty, unemployment, HDI, life expectancy, GDP, population, inflation)
- **ANSI color module** (`colors.py`) for consistent terminal output styling
- **JSON-structured logger** for agent run tracing and debugging

### Changed
- MCP tools expanded from 55 to **62 registered tools**
- Test suite expanded from 290+ to **379 test functions** across 29 files
- Enhanced file tools with improved path traversal protection
- Enhanced note tool with better JSON persistence

### Fixed
- File tools edge cases for edit operations

## [v0.1.2] - 2026-04-24

### Added
- **20 accuracy audit tests** covering ranking, retrieval, and LLM comprehension
- **MiniMax LLM + BPS integration tests** for end-to-end validation
- **bps-master skill** enhanced with complete tool documentation and domain codes

### Changed
- Improved BPS resolution classification accuracy

## [v0.1.1] - 2026-04-24

### Fixed
- **Complete rebrand** from `mini-agent` to `bps-stat-agent` across all files
- Config path updated from `mini-agent-bps` to `bps-stat-agent`
- Clone URL and README SEO improvements
- All remaining `mini-agent` references replaced with `bps-stat-agent`

## [v0.1.0] - 2026-04-24

### Added
- **55 MCP tools** for BPS WebAPI and AllStats Search Engine access
- **BPS AllStats Search** via Playwright - search 1.6M+ statistical data points
- **AllStats-First Fallback Pipeline** - search via AllStats, then retrieve via WebAPI
- **Multi-domain support** - national (0000) and provincial data (5300=NTT, etc.)
- **Rich content types** - publications, indicators, press releases, tables, infographics
- **Auto-retry mechanism** - fresh browser context on Cloudflare blocks
- **Full BPS WebAPI coverage** - domains, subjects, variables, periods, data retrieval
- **SIMDASI support** - regional statistics for kabupaten/kota
- **CSA (Custom Statistical Areas)** - specialized area statistics
- **KBLI/KBKI classifications** - industry and commodity classifications
- **Census data access** - SP2020 and census datasets
- **SDGs/SDDS indicators** - sustainable development goal indicators
- **Glossary and news** - BPS terminology and press releases
- **Foreign trade data** - export/import statistics via dataexim
- **Python API** - `AllStatsClient` for direct programmatic access
- **MCP server mode** - run as stdio MCP server for Claude Desktop
- **CLI mode** - interactive BPS data querying session

### Features
- Domain code validation and formatting
- Pagination handling for large datasets
- Region ID decoding for dynamic data
- Multi-language support (Indonesian/English)
- Configurable search delay to avoid rate limiting
- Playwright-based browser automation for AllStats

### Installation
- Single command install via `uv` or `pip`
- Setup script for automatic configuration
- Example config files included

### Documentation
- Complete API reference in SKILL.md
- Installation and usage guides
- BPS domain codes reference
- Content types documentation
- Common query examples
- Architecture overview

---

## [v0.0.0] - 2026-04-23

### Added
- Initial project setup
- Base BPS API client
- AllStats search engine integration
- MCP server infrastructure
