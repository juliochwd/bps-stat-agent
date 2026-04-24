"""
BPS MCP Server - Provides BPS WebAPI tools via MCP protocol.

This server provides tools for accessing BPS (Badan Pusat Statistik / Statistics Indonesia)
statistical data via the BPS WebAPI (webapi.bps.go.id).

Usage as MCP server:
    uvx --from git+https://github.com/MiniMax-AI/mini-agent-bps.git bps-mcp-server

Or as module:
    from mini_agent.bps_mcp_server import bps_list_subjects, bps_get_variables, bps_search

Environment:
    BPS_API_KEY - Your BPS WebAPI key (or set in config.yaml)
"""

import asyncio
import json
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

# Import BPSAPI from same package
sys.path.insert(0, os.path.dirname(__file__))
try:
    from bps_api import BPSAPI
except ImportError:
    # Fallback for when running as standalone
    from mini_agent.bps_api import BPSAPI
from mini_agent.bps_orchestrator import BPSOrchestrator
from mini_agent.bps_resource_retriever import BPSResourceRetriever
from mini_agent.bps_resolution import classify_search_result


# MCP Server metadata
MCP_SERVER_NAME = "bps"
MCP_SERVER_VERSION = "1.0.0"

# Default API key (can be overridden by config or environment)
DEFAULT_API_KEY = os.environ.get("BPS_API_KEY", "")
DEFAULT_SEARCH_DELAY = float(os.environ.get("BPS_SEARCH_DELAY", "3"))


def get_api_client(api_key: str | None = None) -> BPSAPI:
    """Get BPSAPI client with the given or configured API key."""
    key = api_key or DEFAULT_API_KEY
    if not key:
        raise ValueError(
            "BPS API key not provided. Set BPS_API_KEY environment variable "
            "or api_key parameter."
        )
    return BPSAPI(key)


def success_response(data: Any, message: str = "OK") -> str:
    """Create a success JSON response."""
    return json.dumps({
        "success": True,
        "message": message,
        "data": data
    }, default=str, ensure_ascii=False)


def error_response(error: str, details: Any = None) -> str:
    """Create an error JSON response."""
    return json.dumps({
        "success": False,
        "error": error,
        "details": details
    }, ensure_ascii=False)


class _RetrieverAdapter:
    """Bridge BPSDataRetriever into the orchestrator contract."""

    def __init__(self, api_key: str | None = None):
        from mini_agent.bps_data_retriever import BPSDataRetriever

        client = get_api_client(api_key)
        table_retriever = BPSDataRetriever(api_key=api_key or DEFAULT_API_KEY)
        self._resource_retriever = BPSResourceRetriever(
            api_client=client,
            table_retriever=table_retriever,
        )

    async def __call__(self, *, query: str, resolved) -> dict[str, Any]:
        """Retrieve and normalize a supported resource."""
        return await self._resource_retriever.retrieve(query=query, resolved=resolved)


def _extract_identifier_from_url(url: str, marker: str) -> str | None:
    """Extract a numeric resource identifier following a URL marker."""
    import base64
    import re

    match = re.search(rf"/{marker}/\d+/([0-9]+)/", url)
    if match:
        return match.group(1)

    encoded_match = re.search(rf"/{marker}/\d+/([^/]+)/", url)
    if not encoded_match:
        return None

    token = encoded_match.group(1)
    try:
        padding = "=" * (-len(token) % 4)
        decoded = base64.b64decode(token + padding).decode("utf-8")
    except Exception:
        return None

    decoded_match = re.match(r"([0-9]+)", decoded)
    if decoded_match:
        return decoded_match.group(1)
    return None


def _resolve_search_result(result: dict[str, Any]):
    """Classify the result and infer basic identifiers from its URL."""
    resolved = classify_search_result(result)
    if resolved.resource_type.value == "table":
        table_id = _extract_identifier_from_url(resolved.url, "statistics-table")
        if table_id:
            resolved.identifiers["table_id"] = table_id
    return resolved


def create_orchestrator(api_key: str | None = None) -> BPSOrchestrator:
    """Create the default AllStats-first orchestrator."""
    from mini_agent.allstats_client import AllStatsClient

    search_client = AllStatsClient(headless=True, search_delay=DEFAULT_SEARCH_DELAY)
    retriever = _RetrieverAdapter(api_key=api_key)
    return BPSOrchestrator(
        search_client=search_client,
        resolver=_resolve_search_result,
        retriever=retriever,
    )


async def _answer_query(
    *,
    keyword: str,
    domain: str,
    content: str,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Run the shared AllStats-first query pipeline."""
    orchestrator = create_orchestrator(api_key)
    try:
        return await orchestrator.answer_query(keyword, domain=domain, content=content)
    finally:
        search_client = getattr(orchestrator, "_search_client", None)
        close = getattr(search_client, "close", None)
        if callable(close):
            await close()


# ============================================================================
# MCP Tools - BPS WebAPI Functions
# ============================================================================

def year_to_th(year: int) -> int:
    """Convert year to BPS time period ID (th).

    BPS uses a custom numbering: th = year - 1900.
    Examples: 2017 -> 117, 2024 -> 124

    Args:
        year: Year (e.g., 2024)

    Returns:
        BPS th ID
    """
    return year - 1900


def th_to_year(th: int) -> int:
    """Convert BPS time period ID (th) to year.

    Args:
        th: BPS th ID (e.g., 124)

    Returns:
        Year (e.g., 2024)
    """
    return th + 1900


async def bps_year_to_th(year: int, api_key: str | None = None) -> str:
    """
    Convert year to BPS time period ID (th).

    BPS uses a custom numbering system where th = year - 1900.
    Examples: 2017 -> 117, 2024 -> 124

    Args:
        year: Year (e.g., 2024)
        api_key: Optional BPS API key override

    Returns:
        JSON string with the th value
    """
    th = year_to_th(year)
    return success_response({
        "year": year,
        "th": th,
        "note": f"BPS th={th} corresponds to year {year}"
    }, f"year {year} -> th {th}")


async def bps_list_years(
    domain: str = "5300",
    var: int | None = None,
    api_key: str | None = None
) -> str:
    """
    List available years (th values) for a variable/domain.

    Args:
        domain: Domain code (default "5300" for NTT)
        var: Variable ID to check available years for
        api_key: Optional BPS API key override

    Returns:
        JSON string with available years
    """
    try:
        client = get_api_client(api_key)

        if var:
            # Try to get available periods for a specific variable
            years = []
            for th in range(117, 130):  # 2017-2029
                try:
                    result = client.get_data(var=var, th=th, domain=domain)
                    if result.get("datacontent"):
                        year = th + 1900
                        years.append({"th": th, "year": year})
                except:
                    pass

            return success_response({
                "variable": var,
                "domain": domain,
                "available_years": years
            }, f"Found {len(years)} available years for variable {var}")
        else:
            # Return general year range
            return success_response({
                "domain": domain,
                "year_range": {
                    "min_year": 2017,
                    "max_year": 2025,
                    "min_th": 117,
                    "max_th": 125
                },
                "note": "Most variables available from 2017 (th=117) onwards"
            }, "Year/th mapping available 2017-2025")

    except Exception as e:
        return error_response(str(e))


async def bps_list_domains(type: str = "all", prov: str | None = None, api_key: str | None = None) -> str:
    """
    Get list of BPS statistic domains (provinces, cities, national).
    
    Args:
        type: Domain type - 'all', 'prov', 'kab', 'kabbyprov'
        prov: Province ID (required when type='kabbyprov')
        api_key: Optional BPS API key override
    
    Returns:
        JSON string with list of domains
    """
    try:
        client = get_api_client(api_key)
        domains = client.get_domains(type=type, prov=prov)
        return success_response(domains, f"Found {len(domains)} domains")
    except Exception as e:
        return error_response(str(e))


async def bps_list_provinces(api_key: str | None = None) -> str:
    """
    Get list of all province domains.
    
    Returns:
        JSON string with list of provinces
    """
    try:
        client = get_api_client(api_key)
        provinces = client.get_provinces()
        return success_response(provinces, f"Found {len(provinces)} provinces")
    except Exception as e:
        return error_response(str(e))


async def bps_list_subjects(
    domain: str = "5300",
    subcat: int | None = None,
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get list of statistical subjects for a domain.
    
    Args:
        domain: Domain code (default "5300" for NTT, "0000" for national)
        subcat: Subject category ID filter
        lang: Language - 'ind' (Indonesian) or 'eng' (English)
        page: Page number
        api_key: Optional BPS API key override
    
    Returns:
        JSON string with subjects and pagination info
    """
    try:
        client = get_api_client(api_key)
        result = client.get_subjects(domain=domain, subcat=subcat, lang=lang, page=page)
        return success_response(result, f"Page {page} of subjects")
    except Exception as e:
        return error_response(str(e))


async def bps_get_variables(
    domain: str = "5300",
    subject: int | None = None,
    year: int | None = None,
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get list of statistical variables for a domain/subject.
    
    Args:
        domain: Domain code (default "5300" for NTT)
        subject: Subject ID filter
        year: Year filter
        lang: Language - 'ind' or 'eng'
        page: Page number
        api_key: Optional BPS API key override
    
    Returns:
        JSON string with variables and pagination info
    """
    try:
        client = get_api_client(api_key)
        result = client.get_variables(
            domain=domain,
            subject=subject,
            year=year,
            lang=lang,
            page=page
        )
        return success_response(result, f"Page {page} of variables")
    except Exception as e:
        return error_response(str(e))


async def bps_get_decoded_data(
    var: int,
    th: int,
    domain: str = "5300",
    api_key: str | None = None
) -> str:
    """
    Get actual statistical data values with human-readable decoded format.

    This function retrieves data for a variable (indicator) and decodes it
    into structured data with region labels and actual values.

    Args:
        var: Variable ID (required) - from search results
        th: Time period ID (required) - use year_to_th(year) to convert
        domain: Domain code (default "5300" for NTT)
        api_key: Optional BPS API key override

    Returns:
        JSON string with decoded data (region labels + values)

    Example:
        bps_get_decoded_data(var=522, th=124, domain="5300")
        # Returns TPT data for NTT 2024
    """
    try:
        client = get_api_client(api_key)
        data = client.get_decoded_data(var=var, th=th, domain=domain)

        if data.get("status") != "OK":
            return error_response(f"API error: {data.get('status')}")

        # Format as readable table
        lines = []
        lines.append(f"📊 {data.get('variable', {}).get('label', 'Data')}")
        lines.append(f"Tahun: {data.get('year')}")
        lines.append(f"Unit: {data.get('variable', {}).get('unit', '-')}")
        lines.append(f"Sumber: {data.get('variable', {}).get('note', '').replace('<br>', ' ').strip()}")
        lines.append("")
        lines.append(f"{'No':<3} {'Kabupaten/Kota':<25} {data.get('variable', {}).get('unit', 'Value'):<10}")
        lines.append("-" * 50)

        for i, item in enumerate(data.get("data", [])):
            lines.append(f"{i+1:<3} {item['region_label']:<25} {item['value']:.2f}")

        lines.append("-" * 50)
        lines.append(f"Total: {len(data.get('data', []))} wilayah")

        return success_response({
            "status": "OK",
            "variable": data.get("variable"),
            "year": data.get("year"),
            "data": data.get("data"),
            "table_formatted": "\n".join(lines)
        }, "\n".join(lines))
    except Exception as e:
        return error_response(str(e))


async def bps_get_data(
    var: int,
    th: int | None = None,
    domain: str = "5300",
    api_key: str | None = None
) -> str:
    """
    Get raw statistical data values for a variable.

    Args:
        var: Variable ID (required)
        th: Time period ID (required for dynamic data) - use year_to_th(year) to convert
        domain: Domain code (default "5300" for NTT)
        api_key: Optional BPS API key override

    Returns:
        JSON string with raw data values
    """
    try:
        client = get_api_client(api_key)
        data = client.get_data(var=var, th=th, domain=domain)
        return success_response(data, "Data retrieved successfully")
    except Exception as e:
        return error_response(str(e))


async def bps_search(
    keyword: str,
    domain: str = "5300",
    content: str = "all",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Search BPS data using WebAPI static tables with keyword.
    
    This function searches static tables for matching keywords
    and returns downloadable Excel file URLs.
    
    Args:
        keyword: Search keyword
        domain: Domain code (default "5300" for NTT)
        content: Content type filter - not used for WebAPI search
        page: Page number
        api_key: Optional BPS API key override
    
    Returns:
        JSON string with search results (tables with download URLs)
    """
    try:
        client = get_api_client(api_key)
        
        # Search static tables by keyword
        result = client.get_static_tables(domain=domain, keyword=keyword, page=page)
        
        items = result.get("items", [])
        pagination = result.get("pagination", {})
        
        # Extract safe info (don't expose the encrypted download URLs directly)
        tables = []
        for item in items:
            tables.append({
                "table_id": item.get("table_id"),
                "title": item.get("title"),
                "subject": item.get("subj"),
                "update_date": item.get("updt_date"),
                "size": item.get("size"),
            })
        
        return success_response({
            "keyword": keyword,
            "domain": domain,
            "tables_count": len(tables),
            "tables": tables,
            "pagination": pagination
        }, f"Found {len(tables)} tables for '{keyword}'")
    except Exception as e:
        return error_response(str(e))


async def bps_search_allstats(
    keyword: str,
    domain: str = "5300",
    content: str = "all",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Search BPS AllStats Search Engine using Playwright.
    
    This is a fallback when WebAPI doesn't return results.
    Uses Playwright with anti-detection measures to bypass Cloudflare.
    
    Args:
        keyword: Search keyword
        domain: Domain code (default "5300" for NTT)
        content: Content type filter - all, publication, table, pressrelease, infographic, etc.
        page: Page number
        api_key: Optional BPS API key override
    
    Returns:
        JSON string with search results from AllStats
    """
    try:
        # Import here to avoid dependency if not needed
        from mini_agent.allstats_client import AllStatsClient
        
        async with AllStatsClient(headless=True, search_delay=3) as client:
            result = await client.search(keyword=keyword, domain=domain, content=content, page=page)
            
            results_data = []
            for r in result.results:
                results_data.append({
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                    "content_type": r.content_type,
                    "domain_name": r.domain_name,
                    "domain_code": r.domain_code,
                    "year": r.year,
                })
            
            return success_response({
                "keyword": keyword,
                "domain": domain,
                "content_type": content,
                "results_count": len(results_data),
                "total_results": result.total_results,
                "per_page": result.per_page,
                "has_next": result.has_next,
                "has_prev": result.has_prev,
                "results": results_data,
                "source": "allstats"
            }, f"Found {len(results_data)} results from AllStats")
    except ImportError:
        return error_response("AllStats client not available", "Playwright may not be installed")
    except Exception as e:
        return error_response(f"AllStats search failed: {str(e)}")


async def bps_search_ntt(keyword: str, page: int = 1, api_key: str | None = None) -> str:
    """
    Search BPS data specifically for NTT province (domain 5300).
    
    Convenience function for bps_search with domain='5300'.
    """
    return await bps_search(keyword, domain="5300", page=page, api_key=api_key)


async def bps_get_table_data(
    table_id: int,
    domain: str = "5300",
    format: str = "json",
    api_key: str | None = None
) -> str:
    """
    Get actual data from a BPS static table.

    This is the key function that retrieves the ACTUAL DATA from BPS tables.
    Complete flow: search -> get table_id -> get_table_data -> actual data!

    Args:
        table_id: BPS table ID (from bps_search results)
        domain: Domain code (default "5300" for NTT)
        format: Output format - 'json' or 'csv'
        api_key: Optional BPS API key override

    Returns:
        JSON string with actual table data (headers + rows)
    """
    try:
        client = get_api_client(api_key)
        
        # Get table detail with data
        result = client.get_static_table_detail(table_id=table_id, domain=domain)
        
        data_section = result.get("data", {})
        title = data_section.get("title", "")
        subject = data_section.get("subcsa", "")
        update_date = data_section.get("updt_date", "")
        
        # Parse HTML table
        import re
        html_content = data_section.get("table", "")
        headers, data_rows = _parse_html_table(html_content)
        
        if not headers or not data_rows:
            return error_response("No data found in table", {
                "table_id": table_id,
                "title": title
            })
        
        # Convert to list of dicts
        data = []
        for row in data_rows:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = row[i]
            data.append(row_dict)
        
        response_data = {
            "table_id": table_id,
            "title": title,
            "subject": subject,
            "update_date": update_date,
            "domain": domain,
            "columns": len(headers),
            "rows": len(data),
            "headers": headers,
            "data": data,
        }
        
        if format == "csv":
            # Add CSV representation
            csv_lines = [",".join(headers)]
            for row in data:
                values = [str(row.get(h, "")) for h in headers]
                csv_lines.append(",".join(values))
            response_data["csv"] = "\n".join(csv_lines)
        
        return success_response(response_data, f"Retrieved {len(data)} rows from table {table_id}")
    except Exception as e:
        return error_response(f"Failed to get data: {str(e)}")


def _parse_html_table(html: str) -> tuple[list[str], list[list[str]]]:
    """
    Parse HTML table to headers and data rows.
    
    Args:
        html: HTML content with table
        
    Returns:
        Tuple of (headers list, data rows list)
    """
    import re
    # Unescape HTML entities
    html = html.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&amp;', '&')
    
    # Find all rows
    row_matches = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
    
    rows = []
    for row_html in row_matches:
        # Find all cells
        cell_matches = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row_html, re.DOTALL | re.IGNORECASE)
        
        # Clean cells
        cells = []
        for cell in cell_matches:
            # Remove HTML tags but preserve text
            text = re.sub(r'<[^>]+>', '', cell)
            # Decode HTML entities and clean whitespace
            text = (text.replace('&nbsp;', ' ')
                   .replace('\r', ' ')
                   .replace('\n', ' ')
                   .replace('  ', ' ')
                   .strip())
            cells.append(text)
        
        if cells:
            rows.append(cells)
    
    # First row with actual content is headers (typically row 3)
    headers = []
    data_rows = []
    
    if len(rows) > 3:
        potential_headers = rows[3]
        headers = [h for h in potential_headers if h.strip()]
        data_rows = rows[4:]
    
    return headers, data_rows


async def bps_search_and_get_data(
    keyword: str,
    domain: str = "5300",
    max_tables: int = 3,
    format: str = "json",
    api_key: str | None = None
) -> str:
    """
    Complete flow: Search for tables then get actual data from each.
    
    This is the main function for getting actual BPS data.
    Flow: search tables -> get table_id -> retrieve actual data!
    
    Args:
        keyword: Search keyword
        domain: Domain code (default "5300" for NTT)
        max_tables: Maximum number of tables to fetch (default 3)
        format: Output format - 'json' or 'csv'
        api_key: Optional BPS API key override
    
    Returns:
        JSON string with search results AND actual data for each table
    """
    try:
        client = get_api_client(api_key)
        
        # Step 1: Search for tables
        search_result = client.get_static_tables(domain=domain, keyword=keyword, page=1)
        items = search_result.get("items", [])
        
        if not items:
            return error_response(f"No tables found for keyword '{keyword}'")
        
        # Step 2: Get data from first N tables
        results = []
        for item in items[:max_tables]:
            table_id = item.get("table_id")
            if not table_id:
                continue
                
            try:
                table_result = client.get_static_table_detail(table_id=table_id, domain=domain)
                data_section = table_result.get("data", {})
                title = data_section.get("title", "")
                subject = data_section.get("subcsa", "")
                update_date = data_section.get("updt_date", "")
                
                # Parse HTML table
                import re
                html_content = data_section.get("table", "")
                headers, data_rows = _parse_html_table(html_content)
                
                # Convert to list of dicts
                parsed_data = []
                for row in data_rows:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            row_dict[header] = row[i]
                    parsed_data.append(row_dict)
                
                table_entry = {
                    "table_id": table_id,
                    "title": title,
                    "subject": subject,
                    "update_date": update_date,
                    "columns": len(headers),
                    "rows": len(parsed_data),
                    "headers": headers,
                    "data": parsed_data[:50] if parsed_data else [],  # Limit rows
                    "data_truncated": len(parsed_data) > 50
                }
                
                if format == "csv" and parsed_data:
                    csv_lines = [",".join(headers)]
                    for row in parsed_data[:100]:
                        values = [str(row.get(h, "")) for h in headers]
                        csv_lines.append(",".join(values))
                    table_entry["csv_sample"] = "\n".join(csv_lines)
                
                results.append(table_entry)
                
            except Exception as e:
                results.append({
                    "table_id": table_id,
                    "error": str(e)
                })
        
        return success_response({
            "keyword": keyword,
            "domain": domain,
            "tables_found": len(items),
            "tables_retrieved": len(results),
            "tables": results
        }, f"Found {len(items)} tables, retrieved data from {len(results)}")
    except Exception as e:
        return error_response(f"Search and get data failed: {str(e)}")


async def bps_answer_query(
    keyword: str,
    domain: str = "5300",
    content: str = "all",
    api_key: str | None = None,
) -> str:
    """Answer a BPS query through the shared AllStats-first pipeline."""
    try:
        result = await _answer_query(
            keyword=keyword,
            domain=domain,
            content=content,
            api_key=api_key,
        )
        return success_response(
            result,
            f"Retrieved {result.get('resource_type', 'resource')} for '{keyword}'",
        )
    except Exception as e:
        return error_response(str(e))


async def bps_search_nasional(keyword: str, page: int = 1, api_key: str | None = None) -> str:
    """
    Search BPS data for national level (domain 0000).
    
    Convenience function for bps_search with domain='0000'.
    """
    return await bps_search(keyword, domain="0000", page=page, api_key=api_key)


async def bps_get_press_releases(
    year: int = 2024,
    domain: str = "0000",
    api_key: str | None = None
) -> str:
    """
    Get BPS press releases (Berita Resmi Statistik).
    
    Args:
        year: Year of press releases
        domain: Domain code (default "0000" for national)
        api_key: Optional BPS API key override
    
    Returns:
        JSON string with press releases
    """
    try:
        client = get_api_client(api_key)
        result = client.get_press_releases(year=year, domain=domain)
        return success_response(result, f"Found press releases for {year}")
    except Exception as e:
        return error_response(str(e))


async def bps_get_publications(
    domain: str = "5300",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get BPS publications for a domain.
    
    Args:
        domain: Domain code (default "5300" for NTT)
        page: Page number
        api_key: Optional BPS API key override
    
    Returns:
        JSON string with publications
    """
    try:
        client = get_api_client(api_key)
        result = client.get_publications(domain=domain, page=page)
        return success_response(result, f"Page {page} of publications")
    except Exception as e:
        return error_response(str(e))


async def bps_get_indicators(
    domain: str = "5300",
    year: int | None = None,
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get BPS statistical indicators.

    Args:
        domain: Domain code (default "5300" for NTT)
        year: Optional year filter
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with indicators
    """
    try:
        client = get_api_client(api_key)
        result = client.get_indicators(domain=domain, page=page)
        return success_response(result, f"Page {page} of indicators")
    except Exception as e:
        return error_response(str(e))


async def bps_list_subject_categories(
    domain: str = "5300",
    lang: str = "ind",
    api_key: str | None = None
) -> str:
    """
    Get BPS subject categories (subjek statistik).

    Args:
        domain: Domain code (default "5300" for NTT)
        lang: Language - 'ind' (Indonesian) or 'eng' (English)
        api_key: Optional BPS API key override

    Returns:
        JSON string with subject categories
    """
    try:
        client = get_api_client(api_key)
        categories = client.get_subject_categories(domain=domain, lang=lang)
        return success_response(categories, f"Found {len(categories)} subject categories")
    except Exception as e:
        return error_response(str(e))


async def bps_list_periods(
    domain: str = "5300",
    var: int | None = None,
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get available time periods (tahun) for a variable.

    Args:
        domain: Domain code (default "5300" for NTT)
        var: Variable ID to get periods for
        lang: Language - 'ind' or 'eng'
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with available periods
    """
    try:
        client = get_api_client(api_key)
        result = client.get_periods(domain=domain, var=var, lang=lang, page=page)
        return success_response(result, f"Page {page} of periods")
    except Exception as e:
        return error_response(str(e))


async def bps_list_vertical_variables(
    domain: str = "5300",
    var: int | None = None,
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get vertical variables (regional breakdowns) for a variable.

    Args:
        domain: Domain code (default "5300" for NTT)
        var: Variable ID to get vertical variables for
        lang: Language - 'ind' or 'eng'
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with vertical variables (kabupaten/kota breakdowns)
    """
    try:
        client = get_api_client(api_key)
        result = client.get_vertical_variables(domain=domain, var=var, lang=lang, page=page)
        return success_response(result, f"Page {page} of vertical variables")
    except Exception as e:
        return error_response(str(e))


async def bps_list_derived_variables(
    domain: str = "5300",
    var: int | None = None,
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get derived variables (sub-categories) for a variable.

    Args:
        domain: Domain code (default "5300" for NTT)
        var: Variable ID to get derived variables for
        lang: Language - 'ind' or 'eng'
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with derived variables
    """
    try:
        client = get_api_client(api_key)
        result = client.get_derived_variables(domain=domain, var=var, lang=lang, page=page)
        return success_response(result, f"Page {page} of derived variables")
    except Exception as e:
        return error_response(str(e))


async def bps_list_derived_periods(
    domain: str = "5300",
    var: int | None = None,
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get derived periods (monthly/quarterly) for a variable.

    Args:
        domain: Domain code (default "5300" for NTT)
        var: Variable ID to get derived periods for
        lang: Language - 'ind' or 'eng'
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with derived periods (monthly/quarterly breakdowns)
    """
    try:
        client = get_api_client(api_key)
        result = client.get_derived_periods(domain=domain, var=var, lang=lang, page=page)
        return success_response(result, f"Page {page} of derived periods")
    except Exception as e:
        return error_response(str(e))


async def bps_list_units(
    domain: str = "5300",
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get units of measurement for variables.

    Args:
        domain: Domain code (default "5300" for NTT)
        lang: Language - 'ind' or 'eng'
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with units
    """
    try:
        client = get_api_client(api_key)
        result = client.get_units(domain=domain, lang=lang, page=page)
        return success_response(result, f"Page {page} of units")
    except Exception as e:
        return error_response(str(e))


async def bps_list_infographics(
    domain: str = "5300",
    keyword: str | None = None,
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get BPS infographics list.

    Args:
        domain: Domain code (default "5300" for NTT)
        keyword: Optional keyword filter
        lang: Language - 'ind' or 'eng'
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with infographics
    """
    try:
        client = get_api_client(api_key)
        result = client.get_infographics(domain=domain, keyword=keyword, lang=lang, page=page)
        return success_response(result, f"Page {page} of infographics")
    except Exception as e:
        return error_response(str(e))


async def bps_get_infographic_detail(
    infographic_id: str,
    domain: str = "5300",
    lang: str = "ind",
    api_key: str | None = None
) -> str:
    """
    Get detail of a BPS infographic.

    Args:
        infographic_id: Infographic ID
        domain: Domain code (default "5300" for NTT)
        lang: Language - 'ind' or 'eng'
        api_key: Optional BPS API key override

    Returns:
        JSON string with infographic detail including image URL
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_infographic_detail(infographic_id=infographic_id, domain=domain, lang=lang)
        return success_response(detail, "Infographic detail retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_list_glossary(
    prefix: str | None = None,
    perpage: int = 10,
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get BPS statistical glossary (glosarium).

    Args:
        prefix: Filter by prefix letter
        perpage: Results per page
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with glossary terms
    """
    try:
        client = get_api_client(api_key)
        result = client.get_glossary(prefix=prefix, perpage=perpage, page=page)
        return success_response(result, f"Page {page} of glossary")
    except Exception as e:
        return error_response(str(e))


async def bps_get_glossary_detail(
    glossary_id: int,
    lang: str = "ind",
    api_key: str | None = None
) -> str:
    """
    Get detail of a glossary term.

    Args:
        glossary_id: Glossary term ID
        lang: Language - 'ind' or 'eng'
        api_key: Optional BPS API key override

    Returns:
        JSON string with glossary term detail
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_glossary_detail(glossary_id=glossary_id, lang=lang)
        return success_response(detail, "Glossary detail retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_list_sdgs(
    goal: str | None = None,
    api_key: str | None = None
) -> str:
    """
    Get BPS SDGs (Sustainable Development Goals) indicators.

    Args:
        goal: Goal number "1" to "17" (optional)
        api_key: Optional BPS API key override

    Returns:
        JSON string with SDG indicators
    """
    try:
        client = get_api_client(api_key)
        result = client.get_sdgs(goal=goal)
        return success_response(result, f"SDGs{' goal ' + goal if goal else ''} retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_list_sdds(api_key: str | None = None) -> str:
    """
    Get BPS SDDS (Strategic Development Goals) indicators.

    Args:
        api_key: Optional BPS API key override

    Returns:
        JSON string with SDDS indicators
    """
    try:
        client = get_api_client(api_key)
        result = client.get_sdds()
        return success_response(result, "SDDS indicators retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_get_news_detail(
    news_id: int,
    domain: str = "5300",
    lang: str = "ind",
    api_key: str | None = None
) -> str:
    """
    Get detail of a BPS news article.

    Args:
        news_id: News article ID
        domain: Domain code (default "5300" for NTT)
        lang: Language - 'ind' or 'eng'
        api_key: Optional BPS API key override

    Returns:
        JSON string with news article detail
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_news_detail(news_id=news_id, domain=domain, lang=lang)
        return success_response(detail, "News detail retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_list_news_categories(
    domain: str = "5300",
    lang: str = "ind",
    api_key: str | None = None
) -> str:
    """
    Get BPS news categories.

    Args:
        domain: Domain code (default "5300" for NTT)
        lang: Language - 'ind' or 'eng'
        api_key: Optional BPS API key override

    Returns:
        JSON string with news categories
    """
    try:
        client = get_api_client(api_key)
        categories = client.get_news_categories(domain=domain, lang=lang)
        return success_response(categories, f"Found {len(categories)} news categories")
    except Exception as e:
        return error_response(str(e))


async def bps_get_census_topics(
    kegiatan: str,
    api_key: str | None = None
) -> str:
    """
    Get census data topics/topics for a census event.

    Args:
        kegiatan: Census event ID (e.g., 'sp2020' for Population Census 2020)
        api_key: Optional BPS API key override

    Returns:
        JSON string with census topics
    """
    try:
        client = get_api_client(api_key)
        topics = client.get_census_topics(kegiatan=kegiatan)
        return success_response(topics, f"Found {len(topics)} census topics")
    except Exception as e:
        return error_response(str(e))


async def bps_get_census_areas(
    kegiatan: str,
    api_key: str | None = None
) -> str:
    """
    Get census event areas (wilayah sensus).

    Args:
        kegiatan: Census event ID (e.g., 'sp2020')
        api_key: Optional BPS API key override

    Returns:
        JSON string with census areas
    """
    try:
        client = get_api_client(api_key)
        areas = client.get_census_areas(kegiatan=kegiatan)
        return success_response(areas, f"Found {len(areas)} census areas")
    except Exception as e:
        return error_response(str(e))


async def bps_get_census_datasets(
    kegiatan: str,
    topik: int,
    api_key: str | None = None
) -> str:
    """
    Get available census datasets.

    Args:
        kegiatan: Census event ID (e.g., 'sp2020')
        topik: Topic ID from bps_get_census_topics
        api_key: Optional BPS API key override

    Returns:
        JSON string with available census datasets
    """
    try:
        client = get_api_client(api_key)
        datasets = client.get_census_datasets(kegiatan=kegiatan, topik=topik)
        return success_response(datasets, f"Found {len(datasets)} census datasets")
    except Exception as e:
        return error_response(str(e))


async def bps_get_census_data(
    kegiatan: str,
    wilayah_sensus: int,
    dataset: int,
    api_key: str | None = None
) -> str:
    """
    Get actual census microdata.

    Args:
        kegiatan: Census event ID (e.g., 'sp2020')
        wilayah_sensus: Area code (00 for national, or district code)
        dataset: Dataset ID from bps_get_census_datasets
        api_key: Optional BPS API key override

    Returns:
        JSON string with census microdata
    """
    try:
        client = get_api_client(api_key)
        data = client.get_census_data(kegiatan=kegiatan, wilayah_sensus=wilayah_sensus, dataset=dataset)
        return success_response(data, "Census data retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_get_simdasi_regencies(
    parent: str,
    api_key: str | None = None
) -> str:
    """
    Get SIMDASI regency codes by province.

    Note: Some regional calls may be blocked by WAF. Use national level if blocked.

    Args:
        parent: 7-digit province MFD code (e.g., '5300000' for NTT)
        api_key: Optional BPS API key override

    Returns:
        JSON string with regency codes
    """
    try:
        client = get_api_client(api_key)
        regencies = client.get_simdasi_regencies(parent=parent)
        return success_response(regencies, f"Found {len(regencies)} regencies")
    except Exception as e:
        return error_response(str(e))


async def bps_get_simdasi_districts(
    parent: str,
    api_key: str | None = None
) -> str:
    """
    Get SIMDASI district codes by regency.

    Note: Some regional calls may be blocked by WAF.

    Args:
        parent: 7-digit regency MFD code
        api_key: Optional BPS API key override

    Returns:
        JSON string with district codes
    """
    try:
        client = get_api_client(api_key)
        districts = client.get_simdasi_districts(parent=parent)
        return success_response(districts, f"Found {len(districts)} districts")
    except Exception as e:
        return error_response(str(e))


async def bps_get_simdasi_subjects(
    wilayah: str,
    api_key: str | None = None
) -> str:
    """
    Get SIMDASI subjects for an area.

    Args:
        wilayah: Area code (e.g., '5300000' for NTT province)
        api_key: Optional BPS API key override

    Returns:
        JSON string with SIMDASI subjects
    """
    try:
        client = get_api_client(api_key)
        subjects = client.get_simdasi_subjects(wilayah=wilayah)
        return success_response(subjects, f"Found {len(subjects)} subjects")
    except Exception as e:
        return error_response(str(e))


async def bps_get_simdasi_master_tables(api_key: str | None = None) -> str:
    """
    Get SIMDASI master tables list.

    Args:
        api_key: Optional BPS API key override

    Returns:
        JSON string with master tables
    """
    try:
        client = get_api_client(api_key)
        tables = client.get_simdasi_master_tables()
        return success_response(tables, f"Found {len(tables)} master tables")
    except Exception as e:
        return error_response(str(e))


async def bps_get_simdasi_table_detail(
    wilayah: str,
    tahun: int,
    id_tabel: str,
    api_key: str | None = None
) -> str:
    """
    Get SIMDASI table detail with data.

    Args:
        wilayah: Area code
        tahun: Year
        id_tabel: Table ID
        api_key: Optional BPS API key override

    Returns:
        JSON string with table detail and data
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_simdasi_table_detail(wilayah=wilayah, tahun=tahun, id_tabel=id_tabel)
        return success_response(detail, "SIMDASI table detail retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_get_simdasi_tables_by_area(
    wilayah: str,
    api_key: str | None = None
) -> str:
    """
    Get SIMDASI tables for an area.

    Args:
        wilayah: Area code (e.g., '5300000' for NTT)
        api_key: Optional BPS API key override

    Returns:
        JSON string with tables for the area
    """
    try:
        client = get_api_client(api_key)
        tables = client.get_simdasi_tables_by_area(wilayah=wilayah)
        return success_response(tables, f"Found {len(tables)} tables")
    except Exception as e:
        return error_response(str(e))


async def bps_get_simdasi_tables_by_area_and_subject(
    wilayah: str,
    id_subjek: str,
    api_key: str | None = None
) -> str:
    """
    Get SIMDASI tables for an area and subject.

    Args:
        wilayah: Area code
        id_subjek: Subject ID
        api_key: Optional BPS API key override

    Returns:
        JSON string with tables
    """
    try:
        client = get_api_client(api_key)
        tables = client.get_simdasi_tables_by_area_and_subject(wilayah=wilayah, id_subjek=id_subjek)
        return success_response(tables, f"Found {len(tables)} tables")
    except Exception as e:
        return error_response(str(e))


async def bps_get_simdasi_master_table_detail(
    id_tabel: str,
    api_key: str | None = None
) -> str:
    """
    Get SIMDASI master table detail.

    Args:
        id_tabel: Table ID
        api_key: Optional BPS API key override

    Returns:
        JSON string with master table detail
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_simdasi_master_table_detail(id_tabel=id_tabel)
        return success_response(detail, "Master table detail retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_list_csa_categories(
    domain: str = "5300",
    api_key: str | None = None
) -> str:
    """
    Get CSA (Custom Statistical Areas) subject categories.

    Args:
        domain: Domain code (default "5300" for NTT)
        api_key: Optional BPS API key override

    Returns:
        JSON string with CSA categories
    """
    try:
        client = get_api_client(api_key)
        categories = client.get_csa_categories(domain=domain)
        return success_response(categories, f"Found {len(categories)} CSA categories")
    except Exception as e:
        return error_response(str(e))


async def bps_list_csa_subjects(
    domain: str = "5300",
    subcat: str | None = None,
    api_key: str | None = None
) -> str:
    """
    Get CSA subjects.

    Args:
        domain: Domain code (default "5300" for NTT)
        subcat: Optional category filter
        api_key: Optional BPS API key override

    Returns:
        JSON string with CSA subjects
    """
    try:
        client = get_api_client(api_key)
        result = client.get_csa_subjects(domain=domain, subcat=subcat)
        return success_response(result, "CSA subjects retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_list_csa_tables(
    domain: str = "5300",
    subject: int | None = None,
    page: int = 1,
    perpage: int = 10,
    api_key: str | None = None
) -> str:
    """
    Get CSA table statistics.

    Args:
        domain: Domain code (default "5300" for NTT)
        subject: Optional subject filter
        page: Page number
        perpage: Results per page
        api_key: Optional BPS API key override

    Returns:
        JSON string with CSA tables
    """
    try:
        client = get_api_client(api_key)
        result = client.get_csa_tables(domain=domain, subject=subject, page=page, perpage=perpage)
        return success_response(result, f"Page {page} of CSA tables")
    except Exception as e:
        return error_response(str(e))


async def bps_get_csa_table_detail(
    table_id: str,
    year: int | None = None,
    lang: str = "ind",
    domain: str = "5300",
    api_key: str | None = None
) -> str:
    """
    Get detail of a CSA table.

    Args:
        table_id: CSA table ID
        year: Optional year filter
        lang: Language - 'ind' or 'eng'
        domain: Domain code
        api_key: Optional BPS API key override

    Returns:
        JSON string with CSA table detail
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_csa_table_detail(table_id=table_id, year=year, lang=lang, domain=domain)
        return success_response(detail, "CSA table detail retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_list_kbli(
    year: int = 2020,
    level: str | None = None,
    page: int = 1,
    perpage: int = 10,
    api_key: str | None = None
) -> str:
    """
    Get KBLI (Indonesian Standard Industrial Classification) codes.

    Args:
        year: Classification year - 2009, 2015, 2017, or 2020
        level: Classification level - 'kategori', 'golongan pokok', 'golongan', 'subgolongan', 'kelompok'
        page: Page number
        perpage: Results per page
        api_key: Optional BPS API key override

    Returns:
        JSON string with KBLI codes
    """
    try:
        client = get_api_client(api_key)
        result = client.get_kbli(year=year, level=level, page=page, perpage=perpage)
        return success_response(result, f"Page {page} of KBLI {year} codes")
    except Exception as e:
        return error_response(str(e))


async def bps_get_kbli_detail(
    kbli_id: str,
    year: int = 2020,
    lang: str = "ind",
    api_key: str | None = None
) -> str:
    """
    Get detail of a KBLI classification.

    Args:
        kbli_id: KBLI code ID
        year: Classification year - 2009, 2015, 2017, or 2020
        lang: Language - 'ind' or 'eng'
        api_key: Optional BPS API key override

    Returns:
        JSON string with KBLI detail
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_kbli_detail(kbli_id=kbli_id, year=year, lang=lang)
        return success_response(detail, "KBLI detail retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_list_kbki(
    year: int = 2015,
    page: int = 1,
    perpage: int = 10,
    api_key: str | None = None
) -> str:
    """
    Get KBKI (Indonesian Classification of Education) codes.

    Args:
        year: Classification year (default 2015)
        page: Page number
        perpage: Results per page
        api_key: Optional BPS API key override

    Returns:
        JSON string with KBKI codes
    """
    try:
        client = get_api_client(api_key)
        result = client.get_kbki(year=year, page=page, perpage=perpage)
        return success_response(result, f"Page {page} of KBKI codes")
    except Exception as e:
        return error_response(str(e))


async def bps_get_kbki_detail(
    kbki_id: str,
    year: int = 2015,
    lang: str = "ind",
    api_key: str | None = None
) -> str:
    """
    Get detail of a KBKI classification.

    Args:
        kbki_id: KBKI code ID
        year: Classification year (default 2015)
        lang: Language - 'ind' or 'eng'
        api_key: Optional BPS API key override

    Returns:
        JSON string with KBKI detail
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_kbki_detail(kbki_id=kbki_id, year=year, lang=lang)
        return success_response(detail, "KBKI detail retrieved")
    except Exception as e:
        return error_response(str(e))


async def bps_get_foreign_trade(
    sumber: int,
    kodehs: int,
    tahun: str,
    periode: int = 1,
    jenishs: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get foreign trade (export/import) data.

    Args:
        sumber: 1=Export, 2=Import
        kodehs: HS Code (2-digit for summary, full code for detail)
        tahun: Year (e.g., "2024")
        periode: 1=monthly, 2=annually
        jenishs: 1=Two digit HS summary, 2=Full HS Code
        api_key: Optional BPS API key override

    Returns:
        JSON string with foreign trade data
    """
    try:
        client = get_api_client(api_key)
        data = client.get_foreign_trade(
            sumber=sumber,
            kodehs=kodehs,
            tahun=tahun,
            periode=periode,
            jenishs=jenishs
        )
        return success_response(data, f"Foreign trade data retrieved for {tahun}")
    except Exception as e:
        return error_response(str(e))


async def bps_list_dynamic_tables(
    domain: str = "5300",
    year: int | None = None,
    keyword: str | None = None,
    lang: str = "ind",
    page: int = 1,
    api_key: str | None = None
) -> str:
    """
    Get dynamic tables list.

    Args:
        domain: Domain code (default "5300" for NTT)
        year: Optional year filter
        keyword: Optional keyword filter
        lang: Language - 'ind' or 'eng'
        page: Page number
        api_key: Optional BPS API key override

    Returns:
        JSON string with dynamic tables
    """
    try:
        client = get_api_client(api_key)
        result = client.get_dynamic_tables(domain=domain, year=year, keyword=keyword, lang=lang, page=page)
        return success_response(result, f"Page {page} of dynamic tables")
    except Exception as e:
        return error_response(str(e))


async def bps_get_dynamic_table_detail(
    table_id: int,
    domain: str = "5300",
    lang: str = "ind",
    api_key: str | None = None
) -> str:
    """
    Get dynamic table detail.

    Args:
        table_id: Dynamic table ID
        domain: Domain code (default "5300" for NTT)
        lang: Language - 'ind' or 'eng'
        api_key: Optional BPS API key override

    Returns:
        JSON string with dynamic table detail
    """
    try:
        client = get_api_client(api_key)
        detail = client.get_dynamic_table_detail(table_id=table_id, domain=domain, lang=lang)
        return success_response(detail, "Dynamic table detail retrieved")
    except Exception as e:
        return error_response(str(e))


# ============================================================================
# Main MCP Server (for uvx execution)
# ============================================================================

def build_mcp_server() -> FastMCP:
    """Build the FastMCP server and register core BPS tools."""
    server = FastMCP(
        name=MCP_SERVER_NAME,
        instructions=(
            "BPS data tools. Start discovery from AllStats search, then retrieve "
            "structured data or detail metadata through the best available path."
        ),
    )

    tool_functions = [
        # Core BPS tools
        bps_year_to_th,
        bps_list_years,
        bps_list_domains,
        bps_list_provinces,
        bps_list_subjects,
        bps_list_subject_categories,
        bps_get_variables,
        bps_list_periods,
        bps_list_vertical_variables,
        bps_list_derived_variables,
        bps_list_derived_periods,
        bps_list_units,
        bps_get_decoded_data,
        bps_get_data,
        # Search
        bps_search,
        bps_search_allstats,
        bps_search_ntt,
        bps_search_nasional,
        bps_search_and_get_data,
        bps_answer_query,
        # Data retrieval
        bps_get_table_data,
        # Publications & Press
        bps_get_press_releases,
        bps_get_publications,
        # News & Media
        bps_list_news_categories,
        bps_get_news_detail,
        # Indicators & Infographics
        bps_get_indicators,
        bps_list_infographics,
        bps_get_infographic_detail,
        # Glossary
        bps_list_glossary,
        bps_get_glossary_detail,
        # SDGs & SDDS
        bps_list_sdgs,
        bps_list_sdds,
        # Census data
        bps_get_census_topics,
        bps_get_census_areas,
        bps_get_census_datasets,
        bps_get_census_data,
        # SIMDASI data
        bps_get_simdasi_regencies,
        bps_get_simdasi_districts,
        bps_get_simdasi_subjects,
        bps_get_simdasi_master_tables,
        bps_get_simdasi_table_detail,
        bps_get_simdasi_tables_by_area,
        bps_get_simdasi_tables_by_area_and_subject,
        bps_get_simdasi_master_table_detail,
        # CSA (Custom Statistical Areas)
        bps_list_csa_categories,
        bps_list_csa_subjects,
        bps_list_csa_tables,
        bps_get_csa_table_detail,
        # Classifications
        bps_list_kbli,
        bps_get_kbli_detail,
        bps_list_kbki,
        bps_get_kbki_detail,
        # Foreign trade
        bps_get_foreign_trade,
        # Dynamic tables
        bps_list_dynamic_tables,
        bps_get_dynamic_table_detail,
    ]

    for tool_fn in tool_functions:
        server.add_tool(tool_fn, name=tool_fn.__name__, description=tool_fn.__doc__)

    return server


def main():
    """Run the BPS MCP server over STDIO."""
    server = build_mcp_server()
    print(f"BPS MCP Server v{MCP_SERVER_VERSION} starting...", file=sys.stderr)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
