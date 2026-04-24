# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0] - 2026-04-24

### Added
- **55+ MCP tools** for BPS WebAPI and AllStats Search Engine access
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
