import asyncio
import aiohttp
import re
from typing import Optional, Dict, List, Any


def validate_ip(ip: str) -> bool:
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    parts = ip.split('.')
    return all(0 <= int(p) <= 255 for p in parts)


async def fetch_ip_api(session: aiohttp.ClientSession, ip: str) -> Dict[str, Any]:
    try:
        headers = {'User-Agent': 'Locus-Scanner/1.0'}
        async with session.get(
            f'https://ipinfo.io/{ip}/json',
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if 'bogon' not in data:
                    loc = data.get('loc', '0,0').split(',')
                    return {
                        'country': data.get('country'),
                        'city': data.get('city'),
                        'region': data.get('region'),
                        'latitude': float(loc[0]) if loc[0] else None,
                        'longitude': float(loc[1]) if len(loc) > 1 and loc[1] else None,
                        'isp': data.get('org', '').replace('AS' + data.get('asn', ''), '').strip() or 'N/A',
                        'vpn': False,
                        'proxy': False,
                        'tor': False,
                    }
                else:
                    return {'error': 'Bogon/Invalid IP'}
            return {'error': f'HTTP {resp.status}'}
    except asyncio.TimeoutError:
        return {'error': 'Timeout (ipinfo.io)'}
    except Exception as e:
        return {'error': f'API error: {str(e)[:50]}'}


async def fetch_fraud_api(session: aiohttp.ClientSession, ip: str) -> Dict[str, Any]:
    try:
        headers = {'User-Agent': 'Locus-Scanner/1.0'}
        async with session.get(
            f'https://ipqualityscore.com/api/json/ip/{ip}',
            params={'strictness': 1},
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    'fraud_score': data.get('fraud_score', 0),
                    'is_bot': data.get('is_bot', False),
                }
            return {'error': f'HTTP {resp.status}'}
    except asyncio.TimeoutError:
        return {'error': 'Timeout (ipqualityscore.com)'}
    except Exception as e:
        return {'error': f'API error: {str(e)[:50]}'}


async def scan_single_ip(
    session: aiohttp.ClientSession, ip: str
) -> Dict[str, Any]:
    if not validate_ip(ip):
        return {
            'ip': ip,
            'status': 'invalid',
            'error': 'Invalid IP format',
            'location': {},
            'security': {},
            'isp': None,
        }

    try:
        location_task = fetch_ip_api(session, ip)
        fraud_task = fetch_fraud_api(session, ip)

        location_data, fraud_data = await asyncio.gather(
            location_task, fraud_task, return_exceptions=False
        )

        location_error = location_data.get('error')
        fraud_error = fraud_data.get('error')

        if location_error:
            return {
                'ip': ip,
                'status': 'error' if 'Timeout' in location_error else 'error',
                'error': location_error,
                'location': {},
                'security': {},
                'isp': None,
            }

        location = {
            'country': location_data.get('country'),
            'city': location_data.get('city'),
            'region': location_data.get('region'),
            'latitude': location_data.get('latitude'),
            'longitude': location_data.get('longitude'),
        }

        security = {
            'vpn': location_data.get('vpn', False),
            'proxy': location_data.get('proxy', False),
            'tor': location_data.get('tor', False),
            'fraud_score': fraud_data.get('fraud_score', 0) if not fraud_error else None,
            'is_bot': fraud_data.get('is_bot', False) if not fraud_error else None,
        }

        return {
            'ip': ip,
            'status': 'success',
            'error': None,
            'location': location,
            'security': security,
            'isp': location_data.get('isp'),
        }

    except Exception as e:
        return {
            'ip': ip,
            'status': 'error',
            'error': f'Scan error: {str(e)[:50]}',
            'location': {},
            'security': {},
            'isp': None,
        }


async def scan_ips_bulk(
    ips: List[str],
    progress_callback: Optional[callable] = None,
) -> List[Dict[str, Any]]:
    results = []
    batch_size = 40
    delay_between_batches = 1.5

    connector = aiohttp.TCPConnector(limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        for batch_start in range(0, len(ips), batch_size):
            batch = ips[batch_start : batch_start + batch_size]
            tasks = [scan_single_ip(session, ip) for ip in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            if progress_callback:
                progress_callback(len(results), len(ips))

            if batch_start + batch_size < len(ips):
                await asyncio.sleep(delay_between_batches)

    return results


def parse_ips_from_text(text: str) -> List[str]:
    lines = text.strip().split('\n')
    ips = [ip.strip() for ip in lines if ip.strip()]
    return ips


def parse_ips_from_file(file_path: str) -> List[str]:
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return parse_ips_from_text(content)
    except Exception as e:
        raise ValueError(f'Failed to read file: {str(e)}')
