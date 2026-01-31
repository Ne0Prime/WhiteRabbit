import dns.resolver
from database import *
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# DNS Servers
CLOUDFLARE_DNS = ['1.1.1.1', '1.0.0.1']
GOOGLE_DNS = ['8.8.8.8', '8.8.4.4']

def dns_check(subdomain, use_cloudflare):
    """Check if subdomain resolves via Cloudflare or Google DNS"""
    dns_servers = CLOUDFLARE_DNS if use_cloudflare else GOOGLE_DNS
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = dns_servers
        resolver.timeout = 5
        resolver.lifetime = 5
        
        answers = resolver.resolve(subdomain, 'A')
        return bool(answers)
        
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return False
    except dns.resolver.Timeout:
        print(f"  [!] DNS timeout for {subdomain}")
        return False
    except Exception as e:
        print(f"  [!] DNS error for {subdomain}: {e}")
        return False

def http_check(subdomain):
    """Perform HTTP request and collect basic info"""
    results = {
        'status_code': None,
        'page_size': None
    }
    
    for protocol in ['https', 'http']:
        try:
            url = f"{protocol}://{subdomain}"
            
            response = requests.get(
                url, 
                timeout=10,
                allow_redirects=True,
                verify=False
            )
            
            results['status_code'] = response.status_code
            results['page_size'] = len(response.content)
            
            print(f"  ✓ HTTP {subdomain} - Status: {results['status_code']}, Size: {results['page_size']} bytes")
            
            if protocol == 'https':
                break
                
        except (requests.exceptions.SSLError, 
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            continue
        except Exception as e:
            print(f"  [!] HTTP error on {protocol}://{subdomain}: {e}")
            continue
    
    return results

def check(domain, subdomains):
    """Check DNS and HTTP for all subdomains based on domain settings"""
    use_cloudflare = True
    dns_enabled = domain.get('enable_dns_check', 1) == 1
    http_enabled = domain.get('enable_http_check', 1) == 1
    
    for subdomain in subdomains:
        # Add subdomain to database
        subdomain_id = add_subdomain(domain['id'], subdomain)
        
        if subdomain_id:
            # DNS Check (if enabled)
            if dns_enabled:
                dns_provider = "Cloudflare" if use_cloudflare else "Google"
                print(f"  [DNS:{dns_provider}] Checking {subdomain}...")
                
                if dns_check(subdomain, use_cloudflare):
                    mark_subdomain_as_dns_checked(subdomain_id)
                    print(f"  ✓ DNS resolves")
                    
                    # HTTP Check (if enabled and DNS resolves)
                    if http_enabled:
                        http_results = http_check(subdomain)
                        
                        if http_results['status_code']:
                            update_subdomain_http(
                                subdomain_id,
                                http_results['status_code'],
                                http_results['page_size']
                            )
                else:
                    print(f"  ✗ DNS does not resolve")
                
                # Toggle DNS provider
                use_cloudflare = not use_cloudflare
            
            # HTTP Check without DNS (if DNS disabled but HTTP enabled)
            elif http_enabled:
                http_results = http_check(subdomain)
                
                if http_results['status_code']:
                    update_subdomain_http(
                        subdomain_id,
                        http_results['status_code'],
                        http_results['page_size']
                    )