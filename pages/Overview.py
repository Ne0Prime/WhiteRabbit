import streamlit as st
from database import get_all_domains, get_subdomains, get_new_subdomains, mark_subdomain_as_seen

st.set_page_config(page_title="Overview", layout="wide")
st.title("Subdomain Overview")

# Get all domains
domains = get_all_domains()

if domains:
    # Dropdown for domain selection
    domain_names = [d['name'] for d in domains]
    selected_domain_name = st.selectbox("Select Domain:", domain_names)
    
    # Find selected domain
    selected_domain = next(d for d in domains if d['name'] == selected_domain_name)
    
    # Get all subdomains and new subdomains
    all_subdomains = get_subdomains(selected_domain['id'])
    new_subdomains = get_new_subdomains(selected_domain['id'])
    
    # Filter out new subdomains from all subdomains (show only seen ones)
    seen_subdomains = [s for s in all_subdomains if s['is_new'] == 0]
    
    st.divider()
    
    # 3 Column Layout
    col1, col2, col3 = st.columns(3)
    
    # Column 1: All Subdomains (is_new = 0)
    with col1:
        # Header with copy button
        header_col1, header_col2 = st.columns([10, 1])
        with header_col1:
            st.subheader("All Subdomains")
        with header_col2:
            if seen_subdomains:
                copy_text = "\n".join([s['subdomain'] for s in seen_subdomains])
                st.download_button(
                    label="🗐",
                    data=copy_text,
                    file_name=f"{selected_domain_name}_all_subdomains.txt",
                    mime="text/plain",
                    key="download_all_1"
                )
        
        st.write(f"**Count:** {len(seen_subdomains)}")
        
        if seen_subdomains:
            for sub in seen_subdomains:
                with st.expander(sub['subdomain']):
                    st.write(f"**Discovered:** {sub['discovered_at'][:10]}")
                    st.write(f"**Status Code:** {sub['status_code'] or 'N/A'}")
                    st.write(f"**Page Size:** {sub['page_size'] or 'N/A'} bytes")
                    st.write(f"**DNS Verified:** {'Yes' if sub['dns_checked'] else 'No'}")
                    st.write(f"**Last Checked:** {sub['last_checked'][:10] if sub['last_checked'] else 'Never'}")
        else:
            st.info("No subdomains yet")
    
    # Column 2: DNS Verified Subdomains
    with col2:
        # Header with copy button
        header_col1, header_col2 = st.columns([10, 1])
        with header_col1:
            st.subheader("DNS Verified")
        with header_col2:
            verified_subs = [s for s in seen_subdomains if s['dns_checked'] == 1]
            if verified_subs:
                copy_text = "\n".join([s['subdomain'] for s in verified_subs])
                st.download_button(
                    label="🗐",
                    data=copy_text,
                    file_name=f"{selected_domain_name}_dns_verified.txt",
                    mime="text/plain",
                    key="download_verified_2"
                )
        
        st.write(f"**Count:** {len(verified_subs)}")
        
        if verified_subs:
            for sub in verified_subs:
                with st.expander(sub['subdomain']):
                    st.write(f"**Discovered:** {sub['discovered_at'][:10]}")
                    st.write(f"**Status Code:** {sub['status_code'] or 'N/A'}")
                    st.write(f"**Page Size:** {sub['page_size'] or 'N/A'} bytes")
                    st.write(f"**DNS Verified:** {'Yes' if sub['dns_checked'] else 'No'}")
                    st.write(f"**Last Checked:** {sub['last_checked'][:10] if sub['last_checked'] else 'Never'}")
        else:
            st.info("No DNS verified subdomains yet")
    
    # Column 3: New Subdomains (is_new = 1) with checkbox
    with col3:
        # Header with copy button and check all
        header_col1, header_col2 = st.columns([10, 1])
        with header_col1:
            st.subheader("New Subdomains")
        with header_col2:
            if new_subdomains:
                copy_text = "\n".join([s['subdomain'] for s in new_subdomains])
                st.download_button(
                    label="🗐",
                    data=copy_text,
                    file_name=f"{selected_domain_name}_new_subdomains.txt",
                    mime="text/plain",
                    key="download_new_3"
                )
        
        st.write(f"**Count:** {len(new_subdomains)}")
        
        # Check All button
        if new_subdomains:
            if st.button("Check All", key="check_all_new"):
                for sub in new_subdomains:
                    mark_subdomain_as_seen(sub['id'])
                st.rerun()
        
        if new_subdomains:
            for sub in new_subdomains:
                col_check, col_name = st.columns([1, 20])
                
                with col_check:
                    if st.checkbox("", key=f"check_{sub['id']}", label_visibility="collapsed"):
                        # Mark as seen
                        mark_subdomain_as_seen(sub['id'])
                        st.rerun()
                
                with col_name:
                    with st.expander(sub['subdomain']):
                        st.write(f"**Discovered:** {sub['discovered_at'][:10]}")
                        st.write(f"**Status Code:** {sub['status_code'] or 'N/A'}")
                        st.write(f"**Page Size:** {sub['page_size'] or 'N/A'} bytes")
                        st.write(f"**DNS Verified:** {'Yes' if sub['dns_checked'] else 'No'}")
                        st.write(f"**Last Checked:** {sub['last_checked'][:10] if sub['last_checked'] else 'Never'}")
        else:
            st.success("No new subdomains!")
    
else:
    st.warning("No domains available. Add a domain first!")