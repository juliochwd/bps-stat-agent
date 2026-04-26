#!/usr/bin/env python3
"""
Quick BPS data query tool - for common Indonesian statistics queries.

Usage:
    python3 scripts/query_bps.py --query inflation --domain 5300
    python3 scripts/query_bps.py --query gdp --domain 0000
    python3 scripts/query_bps.py --query hdi --domain 5300 --format json

Domains:
    0000 = Nasional, 5300 = NTT, etc.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mini_agent.bps_mcp_server import bps_answer_query


def main():
    parser = argparse.ArgumentParser(description="Quick BPS data query")
    parser.add_argument("--query", required=True, help="Search keyword (e.g., inflation, PDB, IPM)")
    parser.add_argument("--domain", default="5300", help="Domain code (default: 5300 for NTT)")
    parser.add_argument("--format", default="text", choices=["text", "json"], help="Output format")
    parser.add_argument("--year", default=None, help="Filter by year (e.g., 2024)")

    args = parser.parse_args()

    # Run the query
    result = await_bps_answer_query(args.query, args.domain)

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text(result, domain=args.domain))


def await_bps_answer_query(query: str, domain: str):
    """Sync wrapper for the async BPS query function."""
    import asyncio
    return asyncio.run(bps_answer_query(query, domain=domain))


def format_text(result: str, domain: str = "unknown") -> str:
    """Format BPS query result as human-readable text."""
    try:
        data = json.loads(result)
    except Exception:
        return f"Raw response: {result[:500]}"

    if not data.get("success"):
        return f"Error: {data.get('error', 'Unknown error')}"

    bps_data = data.get("data", {})
    lines = []
    lines.append(f"# {bps_data.get('title', 'BPS Data')}")
    lines.append(f"Resource Type: {bps_data.get('resource_type', 'unknown')}")
    lines.append(f"Domain: {bps_data.get('domain_code', domain)}")
    lines.append(f"Retrieval Method: {bps_data.get('retrieval_method', 'unknown')}")
    lines.append("")

    if bps_data.get("summary"):
        lines.append("## Summary")
        lines.append(bps_data["summary"])
        lines.append("")

    if bps_data.get("source_url"):
        lines.append(f"Source: {bps_data['source_url']}")

    if bps_data.get("rows"):
        lines.append(f"\n## Data ({len(bps_data['rows'])} rows)")
        for row in bps_data["rows"][:10]:  # Show first 10 rows
            if isinstance(row, dict):
                lines.append(f"  {row}")
            else:
                lines.append(f"  {row}")

    return "\n".join(lines)


if __name__ == "__main__":
    main()