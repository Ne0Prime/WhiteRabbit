import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "data/subdomains.db"

def init_db():
    """Create database and tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Domains Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            scan_interval INTEGER DEFAULT 3600,
            active_scanners TEXT,
            enable_dns_check INTEGER DEFAULT 1,
            enable_http_check INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_scan TEXT
        )
    """)
    
    # Subdomains Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subdomains (
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
    """)
    
    conn.commit()
    conn.close()

def add_domain(name: str, scanners: List[str], interval: int = 3600, 
               enable_dns: bool = True, enable_http: bool = True) -> int:
    """Add new domain"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    scanners_str = ",".join(scanners)
    cursor.execute("""
        INSERT INTO domains (name, scan_interval, active_scanners, enable_dns_check, enable_http_check)
        VALUES (?, ?, ?, ?, ?)
    """, (name, interval, scanners_str, 1 if enable_dns else 0, 1 if enable_http else 0))
    
    domain_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return domain_id

def get_all_domains() -> List[Dict]:
    """Get all domains"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM domains")
    domains = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return domains

def delete_domain(domain_id: int):
    """Delete domain and all subdomains"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM subdomains WHERE domain_id = ?", (domain_id,))
    cursor.execute("DELETE FROM domains WHERE id = ?", (domain_id,))
    
    conn.commit()
    conn.close()

def add_subdomain(domain_id: int, subdomain: str) -> int:
    """Add subdomain"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO subdomains (domain_id, subdomain)
            VALUES (?, ?)
        """, (domain_id, subdomain))
        sub_id = cursor.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        sub_id = None
    
    conn.close()
    return sub_id

def get_subdomains(domain_id: int) -> List[Dict]:
    """Get all subdomains of a domain"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM subdomains 
        WHERE domain_id = ? 
        ORDER BY discovered_at DESC
    """, (domain_id,))
    
    subdomains = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return subdomains

def update_last_scan(domain_id: int):
    """Update last_scan timestamp"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE domains 
        SET last_scan = ? 
        WHERE id = ?
    """, (datetime.now().isoformat(), domain_id))
    
    conn.commit()
    conn.close()

def get_subdomain_id(domain_id: int, subdomain: str) -> int:
    """Get subdomain ID by domain_id and subdomain name"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id FROM subdomains 
        WHERE domain_id = ? AND subdomain = ?
    """, (domain_id, subdomain))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def mark_subdomain_as_dns_checked(subdomain_id: int):
    """Mark subdomain as DNS checked"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE subdomains 
        SET dns_checked = 1 
        WHERE id = ?
    """, (subdomain_id,))
    
    conn.commit()
    conn.close()

def update_subdomain_http(subdomain_id: int, status_code: int, page_size: int):
    """Update HTTP check results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE subdomains 
        SET status_code = ?, page_size = ?, last_checked = ?
        WHERE id = ?
    """, (status_code, page_size, datetime.now().isoformat(), subdomain_id))
    
    conn.commit()
    conn.close()

def mark_subdomain_as_dns_checked(subdomain_id: int):
    """Set dns_checked to 1"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE subdomains 
        SET dns_checked = 1
        WHERE id = ?
    """, (subdomain_id,))
    
    conn.commit()
    conn.close()

def get_new_subdomains(domain_id: int) -> List[Dict]:
    """Get only new subdomains"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM subdomains 
        WHERE domain_id = ? AND is_new = 1
        ORDER BY discovered_at DESC
    """, (domain_id,))
    
    return [dict(row) for row in cursor.fetchall()]

def mark_subdomain_as_seen(subdomain_id: int):
    """Mark subdomain as not new anymore"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE subdomains 
        SET is_new = 0 
        WHERE id = ?
    """, (subdomain_id,))
    
    conn.commit()
    conn.close()