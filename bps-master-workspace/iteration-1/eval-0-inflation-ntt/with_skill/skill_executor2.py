#!/usr/bin/env python3
"""
Execute BPS Master skill to retrieve inflation data for NTT province.
Try the news article directly for more details.
"""

import asyncio
import os
import sys

sys.path.insert(0, '/home/ubuntu/Mini-Agent')

from mini_agent.allstats_client import AllStatsClient


async def main():
    client = AllStatsClient(headless=True)
    
    try:
        # Try to get the January 2026 inflation news page
        print("Fetching news article: Januari 2026, NTT Inflasi (y-on-y) 3,34%")
        data = await client.get_data_page("https://ntt.bps.go.id/news/2026/02/02/819/januari-2026-ntt-inflasi-y-on-y-3-34-.html")
        
        if "error" not in data:
            print(f"\nTitle: {data.get('title', 'N/A')}")
            print(f"Text content:\n")
            text = data.get('text', '')
            print(text)
        else:
            print(f"Error: {data.get('error')}")
            
        # Also try the September 2025 article
        print("\n" + "="*70)
        print("Fetching: September 2025 inflation article")
        data2 = await client.get_data_page("https://ntt.bps.go.id/news/2025/10/01/735/september-2025-di-ntt-terjadi-inflasi-y-on-y-sebesar-2-30-persen.html")
        
        if "error" not in data2:
            print(f"\nTitle: {data2.get('title', 'N/A')}")
            print(f"Text content:\n")
            text2 = data2.get('text', '')
            print(text2)
        else:
            print(f"Error: {data2.get('error')}")
            
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())