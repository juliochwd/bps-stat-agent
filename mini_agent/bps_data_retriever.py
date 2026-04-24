"""
BPS Data Retriever - Full flow: Search → Get Table → Parse Data

This module provides complete data retrieval from BPS WebAPI:
1. Search for tables by keyword
2. Get table details with actual data
3. Parse HTML table to structured format (CSV/JSON)

Usage:
    from bps_data_retriever import BPSDataRetriever
    
    retriever = BPSDataRetriever(api_key="your-api-key")
    results = await retriever.search("inflasi", domain="5300")
    data = await retriever.get_table_data(table_id=1501, domain="5300")
"""

import os
import json
import re
from html import unescape
from dataclasses import dataclass, field
from typing import Any

try:
    from mini_agent.bps_api import BPSAPI
except ImportError:
    raise ImportError("bps_api module required. Install bps-stat-agent package.")


@dataclass
class BPSDataResult:
    """Structured data from BPS table."""
    table_id: int
    title: str
    subject: str
    update_date: str
    headers: list[str]
    data: list[dict]
    raw_rows: list[list[str]]
    source: str = "webapi"
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps({
            "table_id": self.table_id,
            "title": self.title,
            "subject": self.subject,
            "update_date": self.update_date,
            "headers": self.headers,
            "data": self.data,
            "source": self.source
        }, indent=2, ensure_ascii=False)
    
    def to_csv(self) -> str:
        """Convert to CSV string."""
        lines = []
        lines.append(",".join(self.headers))
        for row in self.data:
            values = [str(row.get(h, "")) for h in self.headers]
            lines.append(",".join(values))
        return "\n".join(lines)
    
    def summary(self) -> str:
        """Get human-readable summary."""
        return f"""Table {self.table_id}: {self.title}
Subject: {self.subject}
Updated: {self.update_date}
Rows: {len(self.data)}
Columns: {len(self.headers)}
Preview:
{self._preview()}"""
    
    def _preview(self, max_rows: int = 5) -> str:
        """Get data preview."""
        lines = [" | ".join(self.headers[:5])]
        for row in self.data[:max_rows]:
            vals = [str(row.get(h, ""))[:15] for h in self.headers[:5]]
            lines.append(" | ".join(vals))
        return "\n".join(lines)


class BPSDataRetriever:
    """
    Complete BPS data retrieval with search + data fetch.
    
    Usage:
        retriever = BPSDataRetriever()
        # Search for tables
        tables = await retriever.search("inflasi", domain="5300")
        # Get actual data from first table
        data = await retriever.get_table_data(tables[0]['table_id'], domain="5300")
    """
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("BPS_API_KEY", "")
        if not self.api_key:
            raise ValueError("BPS API key required. Set BPS_API_KEY environment variable or pass api_key parameter.")
        self._api = BPSAPI(self.api_key)
    
    async def search(
        self,
        keyword: str,
        domain: str = "5300",
        page: int = 1
    ) -> list[dict]:
        """
        Search for BPS tables by keyword.
        
        Args:
            keyword: Search keyword
            domain: Domain code (5300=NTT, 0000=National)
            page: Page number
            
        Returns:
            List of table info dicts with table_id, title, etc.
        """
        result = self._api.get_static_tables(
            domain=domain,
            keyword=keyword,
            page=page
        )
        
        items = result.get("items", [])
        return [
            {
                "table_id": item.get("table_id"),
                "title": item.get("title"),
                "subject": item.get("subj"),
                "update_date": item.get("updt_date"),
                "size": item.get("size"),
            }
            for item in items
        ]
    
    async def get_table_data(
        self,
        table_id: int,
        domain: str = "5300"
    ) -> BPSDataResult:
        """
        Get actual data from a BPS table.
        
        Args:
            table_id: BPS table ID
            domain: Domain code
            
        Returns:
            BPSDataResult with parsed table data
        """
        result = self._api.get_static_table_detail(
            table_id=table_id,
            domain=domain
        )
        
        data_section = result.get("data", {})
        title = data_section.get("title", "")
        subject = data_section.get("subcsa", "")
        update_date = data_section.get("updt_date", "")
        
        # Parse HTML table
        html_content = data_section.get("table", "")
        headers, raw_rows = self._parse_html_table(html_content)
        
        # Convert to list of dicts
        data_rows = []
        for row in raw_rows:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = row[i]
            data_rows.append(row_dict)
        
        return BPSDataResult(
            table_id=table_id,
            title=title,
            subject=subject,
            update_date=update_date,
            headers=headers,
            data=data_rows,
            raw_rows=raw_rows,
            source="webapi"
        )
    
    def _parse_html_table(self, html: str) -> tuple[list[str], list[list[str]]]:
        """
        Parse HTML table to headers and data rows.
        
        Args:
            html: HTML content with table
            
        Returns:
            Tuple of (headers list, data rows list)
        """
        html = unescape(html)
        row_matches = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE)

        parsed_rows: list[tuple[list[str], bool]] = []
        for row_html in row_matches:
            cell_matches = re.findall(
                r"<(th|td)[^>]*>(.*?)</(?:th|td)>",
                row_html,
                re.DOTALL | re.IGNORECASE,
            )
            cells = []
            has_td = False
            for cell_type, cell in cell_matches:
                has_td = has_td or cell_type.lower() == "td"
                text = re.sub(r"<[^>]+>", "", cell)
                text = self._normalize_cell(unescape(text))
                if text:
                    cells.append(text)
            if cells:
                parsed_rows.append((cells, has_td))

        header_index = -1
        first_data_index = None
        for index, (cells, has_td) in enumerate(parsed_rows):
            if has_td:
                first_data_index = index
                break
            if len(cells) > 1:
                header_index = index

        if header_index == -1:
            for index, (cells, _) in enumerate(parsed_rows):
                if len(cells) > 1:
                    header_index = index
                    break

        if header_index == -1:
            return [], []

        headers = parsed_rows[header_index][0]
        if first_data_index is not None and first_data_index > header_index:
            data_start = first_data_index
        else:
            data_start = header_index + 1
        data_rows = [cells for cells, _ in parsed_rows[data_start:] if cells]

        return headers, data_rows

    @staticmethod
    def _normalize_cell(text: str) -> str:
        """Normalize a cell's whitespace and non-breaking spaces."""
        return " ".join(text.replace("\xa0", " ").split()).strip()
    
    async def search_and_get_data(
        self,
        keyword: str,
        domain: str = "5300",
        max_tables: int = 3
    ) -> list[BPSDataResult]:
        """
        Complete flow: Search for tables and retrieve data from each.
        
        Args:
            keyword: Search keyword
            domain: Domain code
            max_tables: Maximum number of tables to fetch data for
            
        Returns:
            List of BPSDataResult with actual data
        """
        # Search for tables
        tables = await self.search(keyword, domain)
        
        results = []
        for table_info in tables[:max_tables]:
            table_id = table_info.get("table_id")
            if table_id:
                try:
                    data = await self.get_table_data(table_id, domain)
                    results.append(data)
                except Exception as e:
                    print(f"Error fetching table {table_id}: {e}")
        
        return results


async def main():
    """Test the data retriever."""
    import os
    os.environ["BPS_API_KEY"] = "80a6bd62b0007e3c9f685346544e6afa"
    
    print("=" * 70)
    print("BPS Data Retriever - Full Flow Test")
    print("=" * 70)
    
    retriever = BPSDataRetriever()
    
    # Step 1: Search
    print("\n[Step 1] Searching for 'inflasi' tables...")
    tables = await retriever.search("inflasi", domain="5300")
    print(f"Found {len(tables)} tables")
    
    if tables:
        print(f"\nFirst table: {tables[0]['title'][:60]}")
        print(f"Table ID: {tables[0]['table_id']}")
        
        # Step 2: Get actual data
        print("\n[Step 2] Fetching actual data...")
        data = await retriever.get_table_data(tables[0]['table_id'], domain="5300")
        
        print(f"\n[Step 3] Data Retrieved Successfully!")
        print(data.summary())
        
        # Show JSON output
        print("\n[Step 4] JSON output:")
        print(data.to_json()[:1000] + "...")
        
        # Show CSV output
        print("\n[Step 5] CSV output:")
        print(data.to_csv()[:800])
    
    # Test complete flow
    print("\n" + "=" * 70)
    print("Testing search_and_get_data (complete flow)")
    print("=" * 70)
    
    all_results = await retriever.search_and_get_data("kemiskinan", domain="5300")
    print(f"\nGot {len(all_results)} data results")
    for result in all_results:
        print(f"\n{result.summary()}")


if __name__ == "__main__":
    asyncio.run(main())
