#!/usr/bin/env python3
"""
Execute BPS Master skill to retrieve inflation data for NTT province.
"""

import asyncio
import os
import sys

# Add mini_agent to path
sys.path.insert(0, '/home/ubuntu/Mini-Agent')

from mini_agent.allstats_client import AllStatsClient


async def main():
    print("=" * 70)
    print("BPS Master Skill - Get Inflation Data for NTT Province")
    print("=" * 70)
    
    client = AllStatsClient(headless=True)
    
    try:
        # Search for inflation data in NTT (domain 5300)
        print("\n[1] Searching AllStats for 'inflasi' in NTT (domain 5300)...")
        response = await client.search(
            keyword="inflasi",
            domain="5300",
            content="all",
            sort="terbaru"
        )
        
        print(f"\nFound {len(response.results)} results")
        
        for i, result in enumerate(response.results[:10], 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result.title}")
            print(f"URL: {result.url}")
            print(f"Type: {result.content_type}")
            print(f"Snippet: {result.snippet[:200] if result.snippet else 'N/A'}...")
        
        # Try to get data page from the first relevant result
        inflation_results = [r for r in response.results 
                             if 'inflasi' in r.title.lower() or 'inflation' in r.title.lower()]
        
        if inflation_results:
            first = inflation_results[0]
            print(f"\n[2] Fetching data page from: {first.url}")
            data = await client.get_data_page(first.url)
            
            if "error" not in data:
                print(f"\nPage title: {data.get('title', 'N/A')}")
                print(f"Text content (first 1000 chars):\n")
                text = data.get('text', '')[:1000]
                print(text)
                
                # Check for tables
                if data.get('tables'):
                    print(f"\n[3] Found {len(data['tables'])} table(s)")
                    for idx, table in enumerate(data['tables'][:3]):
                        print(f"\n--- Table {idx+1} (first 5 rows) ---")
                        for row_idx, row in enumerate(table[:5]):
                            print(" | ".join(str(c).strip()[:30] for c in row))
            else:
                print(f"Error fetching data: {data.get('error')}")
        else:
            print("\nNo direct inflation result found. Checking all results for inflation-related content...")
            # Try getting data from first result anyway
            if response.results:
                first = response.results[0]
                print(f"\nFetching first result: {first.url}")
                data = await client.get_data_page(first.url)
                if "error" not in data:
                    print(f"Title: {data.get('title', 'N/A')}")
                    print(f"Text (first 800 chars):\n{data.get('text', '')[:800]}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())