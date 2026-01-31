from database import *
from datetime import datetime, timedelta
import time
from scanners import *
import signal
import sys

def should_scan(domain):
    """Check if domain should be scanned"""
    if not domain['last_scan']:
        return True
    
    last = datetime.fromisoformat(domain['last_scan'])
    interval = timedelta(seconds=domain['scan_interval'])

    return datetime.now() > last + interval

def signal_handler(sig, frame):
    """Handle graceful shutdown"""
    print('\n[*] Shutting down gracefully...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    try:
        domains = get_all_domains()
        print(f"[*] Checking {len(domains)} domains...")
        
        for domain in domains:
            if should_scan(domain):
                try:
                    print(f"[*] Scanning {domain['name']}...")
                    subdomains = scan_subdomains_osint(domain)
                    
                    if subdomains:
                        print(f"[+] Found {len(subdomains)} subdomains")
                        check(domain, subdomains)
                        update_last_scan(domain['id'])
                    else:
                        print(f"[-] No subdomains found")
                        
                except Exception as e:
                    print(f"[!] Error scanning {domain['name']}: {e}")
                    continue
        
        time.sleep(60)
        
    except Exception as e:
        print(f"[!] Critical error in main loop: {e}")
        time.sleep(60)
        continue