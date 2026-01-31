import requests
import json


def scan_subdomains_osint(domain):
    """Execute passive subdomain enumeration via OSINT sources"""

    subdomains = set()
    use_scanners = domain['active_scanners'].split(',')
    
    # crt.sh
    if "crt_sh" in use_scanners:
        print(f"[*] Querying crt.sh for {domain['name']}")
        try:
            url = f"https://crt.sh/?q=%.{domain['name']}&output=json"
            response = requests.get(url, timeout=40)
            response.raise_for_status()
            data = response.json()
            
            for entry in data:
                name_value = entry.get('name_value', '')
                names = name_value.split('\n')
                for subdomain in names:
                    subdomain = subdomain.strip().lower()
                    if subdomain and not subdomain.startswith('*'):
                        subdomains.add(subdomain)
                        
        except requests.exceptions.RequestException as e:
            print(f"[!] crt.sh error: {e}")
        except json.JSONDecodeError as e:
            print(f"[!] crt.sh JSON error: {e}")
    
    # HackerTarget
    if "hackertarget" in use_scanners:
        print(f"[*] Querying HackerTarget for {domain['name']}")
        try:
            url = f"https://api.hackertarget.com/hostsearch/?q={domain['name']}"
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.text.strip()
            
            if "error" not in data.lower() and "no records" not in data.lower():
                for line in data.split('\n'):
                    line = line.strip()
                    if line and ',' in line:
                        subdomain = line.split(',')[0].strip().lower()
                        if subdomain:
                            subdomains.add(subdomain)
                            
        except requests.exceptions.RequestException as e:
            print(f"[!] HackerTarget error: {e}")
    
    # URLScan.io
    if "urlscan" in use_scanners:
        print(f"[*] Querying URLScan.io for {domain['name']}")
        try:
            url = f"https://urlscan.io/api/v1/search/?q=domain:{domain['name']}"
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            for result in results:
                page = result.get('page', {})
                subdomain = page.get('domain', '')
                if subdomain:
                    subdomain = subdomain.strip().lower()
                    subdomains.add(subdomain)
                    
        except requests.exceptions.RequestException as e:
            print(f"[!] URLScan.io error: {e}")
        except json.JSONDecodeError as e:
            print(f"[!] URLScan.io JSON error: {e}")
    
    # AnubisDB
    if "anubis" in use_scanners:
        print(f"[*] Querying AnubisDB for {domain['name']}")
        try:
            url = f"https://jldc.me/anubis/subdomains/{domain['name']}"
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                for subdomain in data:
                    subdomain = subdomain.strip().lower()
                    if subdomain:
                        subdomains.add(subdomain)
                        
        except requests.exceptions.RequestException as e:
            print(f"[!] AnubisDB error: {e}")
        except json.JSONDecodeError as e:
            print(f"[!] AnubisDB JSON error: {e}")
    
    return subdomains