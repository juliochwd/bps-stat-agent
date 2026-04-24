#!/usr/bin/env python3
"""
Execute BPS Master skill to retrieve inflation data for NTT province.
Try to get the monthly inflation table data.
"""

import asyncio
import os
import sys

sys.path.insert(0, '/home/ubuntu/Mini-Agent')

from mini_agent.allstats_client import AllStatsClient


async def main():
    client = AllStatsClient(headless=True)
    
    try:
        # Get the m-to-m inflation table
        print("Fetching m-to-m inflation table data...")
        data = await client.get_data_page("https://ntt.bps.go.id/statistics-table/2/MTUyMSMy/inflasi-menurut-bulan-m-to-m-ihk-2022-100-.html")
        
        if "error" not in data:
            print(f"\nTitle: {data.get('title', 'N/A')}")
            text = data.get('text', '')
            print(f"Text content:\n{text}")
            
            if data.get('tables'):
                print(f"\n[Found {len(data['tables'])} table(s)]")
                for idx, table in enumerate(data['tables']):
                    print(f"\n--- Table {idx+1} ---")
                    for row_idx, row in enumerate(table[:20]):
                        print(" | ".join(str(c).strip()[:25] for c in row))
        else:
            print(f"Error: {data.get('error')}")
            
        print("\n" + "="*70)
        
        # Also try to get the y-on-y table
        print("Fetching y-on-y inflation table data...")
        data2 = await client.get_data_page("https://ntt.bps.go.id/statistics-table/2/MTc5MyMy/inflasi-menurut-bulan-y-on-y-ihk-2022-100-.html")
        
        if "error" not in data2:
            print(f"\nTitle: {data2.get('title', 'N/A')}")
            text2 = data2.get('text', '')
            print(f"Text content:\n{text2}")
        else:
            print(f"Error: {data2.get('error')}")
            
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())