import streamlit as st
from database import init_db, get_all_domains, get_subdomains, get_new_subdomains

# Initiate database
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# Set Page Style
st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Dashboard")

# Get all domains
domains = get_all_domains()

if domains:
    # Calculate statistics
    total_domains = len(domains)
    total_subdomains = 0
    total_new = 0
    total_dns_verified = 0
    total_http_checked = 0
    
    for domain in domains:
        subs = get_subdomains(domain['id'])
        new_subs = get_new_subdomains(domain['id'])
        
        total_subdomains += len(subs)
        total_new += len(new_subs)
        total_dns_verified += len([s for s in subs if s['dns_checked'] == 1])
        total_http_checked += len([s for s in subs if s['status_code'] is not None])
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Domains", total_domains)
    
    with col2:
        st.metric("Total Subdomains", total_subdomains)
    
    with col3:
        st.metric("New Subdomains", total_new, delta=f"+{total_new}" if total_new > 0 else None)
    
    with col4:
        st.metric("DNS Verified", total_dns_verified)
    
    st.divider()
    
    # Second row metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("HTTP Checked", total_http_checked)
    
    with col2:
        active_domains = len([d for d in domains if d['last_scan']])
        st.metric("Active Scans", active_domains)
    
    with col3:
        avg_subs = total_subdomains // total_domains if total_domains > 0 else 0
        st.metric("Avg per Domain", avg_subs)
    
    with col4:
        verification_rate = (total_dns_verified / total_subdomains * 100) if total_subdomains > 0 else 0
        st.metric("DNS Verify Rate", f"{verification_rate:.1f}%")
    
    st.divider()
    
    # Domain breakdown table
    st.subheader("Domain Overview")
    
    for domain in domains:
        subs = get_subdomains(domain['id'])
        new_subs = get_new_subdomains(domain['id'])
        dns_verified = len([s for s in subs if s['dns_checked'] == 1])
        http_checked = len([s for s in subs if s['status_code'] is not None])
        
        with st.expander(f"{domain['name']} - {len(subs)} subdomains"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Total:** {len(subs)}")
                st.write(f"**New:** {len(new_subs)}")
            
            with col2:
                st.write(f"**DNS Verified:** {dns_verified}")
                st.write(f"**HTTP Checked:** {http_checked}")
            
            with col3:
                interval_min = domain['scan_interval'] // 60
                st.write(f"**Scan Interval:** {interval_min}min")
                st.write(f"**Last Scan:** {domain['last_scan'][:10] if domain['last_scan'] else 'Never'}")
            
            with col4:
                scanners = domain['active_scanners'].split(',') if domain['active_scanners'] else []
                st.write(f"**Active Scanners:** {len(scanners)}")
                st.write(f"**DNS Check:** {'✅' if domain.get('enable_dns_check') else '❌'}")
                st.write(f"**HTTP Check:** {'✅' if domain.get('enable_http_check') else '❌'}")
    
    st.divider()
    
    # Recent activity
    st.subheader("Recent Activity")
    
    all_recent = []
    for domain in domains:
        subs = get_subdomains(domain['id'])
        for sub in subs[:5]:  # Last 5 per domain
            all_recent.append({
                'domain': domain['name'],
                'subdomain': sub['subdomain'],
                'discovered': sub['discovered_at'],
                'is_new': sub['is_new']
            })
    
    # Sort by discovery date
    all_recent.sort(key=lambda x: x['discovered'], reverse=True)
    
    if all_recent[:10]:
        for item in all_recent[:10]:
            status = "🆕" if item['is_new'] else "✅"
            st.write(f"{status} `{item['subdomain']}` - {item['discovered'][:16]}")
    else:
        st.info("No recent activity")

else:
    st.warning("⚠️ No domains configured. Add a domain to get started!")
    st.info("👉 Go to **Domains** page to add your first domain")