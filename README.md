# WhiteRabbit - Subdomain Monitoring Tool

## Project Overview

WhiteRabbit is a subdomain enumeration and monitoring tool designed for bug bounty programs and security research. It automatically discovers subdomains through multiple OSINT sources, verifies them via DNS and performs HTTP checks.

### Core Features
- **Multi-Source OSINT Scanning**: crt.sh, AnubisDB, HackerTarget, URLScan.io
- **DNS Verification**: Alternating between Cloudflare (1.1.1.1) and Google (8.8.8.8) DNS
- **HTTP Discovery**: Status codes, page sizes
- 
## Installation
```bash
git clone [<repository-url>](https://github.com/Ne0Prime/whiterabbit.git
cd whiterabbit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x start.sh stop.sh
# Start
./start.sh

# Stop
./stop.sh

# Show logs
tail -f streamlit.log scanner.log
```
## Architecture

```
whiterabbit/
├── Dashboard.py              # Main dashboard with metrics
├── scanner_worker.py         # Background worker for automated scanning
├── requirements.txt          # Python dependencies
├── data/
│   └── subdomains.db        # SQLite database
├── database/
│   ├── __init__.py          # Database exports
│   └── db_manager.py        # Database operations
├── pages/
│   ├── Domains.py           # Domain management page
│   └── Overview.py          # Subdomain overview page
└── scanners/
    ├── __init__.py          # Scanner exports
    ├── osint_scanners.py    # OSINT data sources
    └── checks.py             # DNS and HTTP verification
```

## Database Schema

### Domains Table
```sql
CREATE TABLE domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    scan_interval INTEGER DEFAULT 3600,
    active_scanners TEXT,
    enable_dns_check INTEGER DEFAULT 1,
    enable_http_check INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_scan TEXT
)
```

### Subdomains Table
```sql
CREATE TABLE subdomains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id INTEGER NOT NULL,
    subdomain TEXT NOT NULL,
    discovered_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_checked TEXT,
    status_code INTEGER,
    dns_checked INTEGER DEFAULT 0,
    page_size INTEGER,
    screenshot_path TEXT,
    is_new INTEGER DEFAULT 1,
    FOREIGN KEY (domain_id) REFERENCES domains (id),
    UNIQUE(domain_id, subdomain)
)
```

## Usage

### Adding a Domain

1. Navigate to **Domains** page
2. Click **✚** button
3. Configure:
   - Domain name (e.g., `example.com`)
   - Scan interval (seconds)
   - OSINT sources to use
   - Enable/disable DNS and HTTP checks
4. Click **Add**

### Monitoring Subdomains

1. Navigate to **Overview** page
2. Select domain from dropdown
3. View three columns:
   - **All Subdomains**: Previously reviewed subdomains
   - **DNS Verified**: Subdomains that resolve via DNS
   - **New Subdomains**: Recently discovered, need review
4. Check off new subdomains to mark as reviewed
5. Use **copy** button to export subdomain lists

## Future Improvements

1. **Add logging**
2. **Retry logic**
3. **Search/filter**
4. **Email/Discord notifications**
5. **Screenshot capture** functionality
6. **Port Scanning**
7. **Technology detection**
8. **Subdomain takeover detection**

## Dependencies

```txt
streamlit>=1.40.0
requests>=2.32.0
dnspython>=2.4.0
urllib3>=2.0.0
```

## License

MIT License - See [LICENSE](LICENSE) file for details.