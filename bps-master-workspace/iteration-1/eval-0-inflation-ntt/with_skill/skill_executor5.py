#!/usr/bin/env python3
"""
Execute BPS Master skill - Search for causes of inflation in NTT.
"""

import asyncio
import os
import sys

sys.path.insert(0, '/home/ubuntu/Mini-Agent')

from mini_agent.allstats_client import AllStatsClient


async def main():
    client = AllStatsClient(headless=True)
    
    try:
        # Search for causes/factors of inflation in NTT
        print("Searching for inflation causes in NTT...")
        response = await client.search(
            keyword="penyebab inflasi",
            domain="5300",
            content="all"
        )
        
        print(f"Found {len(response.results)} results")
        for i, r in enumerate(response.results[:5], 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {r.title}")
            print(f"URL: {r.url}")
            print(f"Type: {r.content_type}")
            print(f"Snippet: {r.snippet[:200] if r.snippet else 'N/A'}...")
            
        # Also search for makanan/commodiity inflation
        print("\n" + "="*70)
        print("Searching for food/commodity inflation...")
        response2 = await client.search(
            keyword="inflasi bahan makanan",
            domain="5300",
            content="all"
        )
        
        print(f"Found {len(response2.results)} results")
        for i, r in enumerate(response2.results[:5], 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {r.title}")
            print(f"URL: {r.url}")
            print(f"Snippet: {r.snippet[:200] if r.snippet else 'N/A'}...")
            
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())