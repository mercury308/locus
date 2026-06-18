#!/usr/bin/env python3
"""
Quick test script for Locus scanner without GUI
"""
import asyncio
from locus_scanner import scan_ips_bulk


async def main():
    test_ips = [
        '8.8.8.8',      # Google DNS
        '1.1.1.1',      # Cloudflare DNS
        '9.9.9.9',      # Quad9 DNS
        '208.67.222.222',  # OpenDNS
        '999.999.999.999',  # This should be seen as an invalid IP (should error)
    ]

    print("=" * 70)
    print("Locus IP Geolocation Scanner - Test Run")
    print("=" * 70)
    print(f"\nScanning {len(test_ips)} IP addresses...\n")

    def progress(done, total):
        pct = (done / total) * 100
        print(f"\r[{'='*int(pct/5)}{' '*(20-int(pct/5))}] {done}/{total} ({pct:.0f}%)", end='')

    results = await scan_ips_bulk(test_ips, progress_callback=progress)

    print("\n\n" + "=" * 70)
    print("Results")
    print("=" * 70)

    for result in results:
        print(f"\n{result['ip']:20} | Status: {result['status']:8}", end='')
        if result['status'] == 'success':
            print(f"\n{'':20} | Country: {result['location'].get('country', 'N/A')}")
            print(f"{'':20} | City: {result['location'].get('city', 'N/A')}")
            print(f"{'':20} | ISP: {result['isp']}")
            print(f"{'':20} | VPN/Proxy/Tor: {result['security'].get('vpn')}/{result['security'].get('proxy')}/{result['security'].get('tor')}")
        else:
            print(f"\n{'':20} | Error: {result['error']}")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    asyncio.run(main())
