# Locus - Async IP Geolocation Scanner with Tkinter GUI

Modern bulk IP geolocation scanner with concurrent API requests, comprehensive security intelligence, and a professional GUI.

## Features

- **Bulk Processing**: Scan multiple IPs concurrently with asyncio
- **Geolocation Data** (via ipinfo.io):
  - Country, City, Region
  - Latitude & Longitude
  - ISP information
- **Security Intelligence** (via ipqualityscore.com):
  - Fraud Score
  - Bot Detection
- **Error Handling**: Robust per-IP error handling with timeouts
- **GUI Application**: Tkinter-based interface with:
  - Manual IP input or file upload
  - Real-time progress bar
  - Results in sortable table
  - CSV export functionality
- **Modern Python**: asyncio, aiohttp, type hints, Python 3.11+

## Installation

```bash
# Clone repository
cd locus

# Install dependencies
pip install -r requirements.txt
```

## Usage

### GUI Application (Recommended)

```bash
python locus.py
```

Opens a tkinter window where you can:
1. **Input IPs**: Type IPs manually (one per line) or click "Load from File" to import a CSV/TXT
2. **Start Scan**: Click "Start Scan" button - progress updates in real-time
3. **View Results**: Switch to "Results" tab to see detailed information
4. **Export**: Click "Export to CSV" to save results

### Command-Line Test

```bash
python test_scanner.py
```

Demonstrates the scanner with 5 sample IPs.

### Programmatic Usage

```python
import asyncio
from locus_scanner import scan_ips_bulk

async def main():
    ips = ['8.8.8.8', '1.1.1.1']
    results = await scan_ips_bulk(ips)
    for result in results:
        print(f"{result['ip']}: {result['location'].get('country')}")

asyncio.run(main())
```

## API Rate Limits

- **ipinfo.io**: 50,000 free requests/month
- **ipqualityscore.com**: Free tier available
- Batching: Respects rate limits with configurable delays

## Sample Input File

See `sample_ips.txt` for format (one IP per line).

## Output Format

Results include:
- IP Address
- Geolocation (country, city, region, coordinates)
- ISP
- Security Flags (VPN, Proxy, Tor, Fraud Score)
- Status (success/error/timeout/invalid)

## Architecture

- **locus_scanner.py**: Async core engine with API integrations
- **locus_gui.py**: Tkinter GUI application
- **locus.py**: Entry point
