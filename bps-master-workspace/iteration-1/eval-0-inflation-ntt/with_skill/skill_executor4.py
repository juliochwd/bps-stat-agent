#!/usr/bin/env python3
"""
Execute BPS Master skill - Try monthly publication for detailed data.
"""

import asyncio
import os
import sys

sys.path.insert(0, '/home/ubuntu/Mini-Agent')

from mini_agent.allstats_client import AllStatsClient


async def main():
    client = AllStatsClient(headless=True)
    
    try:
        # Try to get the monthly report publication
        print("Fetching monthly socioeconomic report...")
        data = await client.get_data_page("https://ntt.bps.go.id/publication/2026/02/11/5db56501c601d1e18450a4d2/laporan-bulanan-data-sosial-ekonomi-provinsi-nusa-tenggara-timur-januari-2026.html")
        
        if "error" not in data:
            print(f"\nTitle: {data.get('title', 'N/A')}")
            text = data.get('text', '')
            print(f"Text content:\n{text[:3000]}")
            
            if data.get('tables'):
                print(f"\n[Found {len(data['tables'])} table(s)]")
                for idx, table in enumerate(data['tables'][:5]):
                    print(f"\n--- Table {idx+1} (first 10 rows) ---")
                    for row_idx, row in enumerate(table[:10]):
                        print(" | ".join(str(c).strip()[:30] for c in row))
        else:
            print(f"Error: {data.get('error')}")
            
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())