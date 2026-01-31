import streamlit as st
from database import get_all_domains, delete_domain, add_domain

st.set_page_config(page_title="Domains", layout="wide")

# Load all domains
domains = get_all_domains()

# Header with title and new button
col1, col2 = st.columns([7, 1])
with col1:
    st.title("Domains")
with col2:
    st.write("")  # Spacer
    if st.button("✚", help="New Domain"):
        st.session_state.show_add = True

# New Domain Dialog
if "show_add" in st.session_state and st.session_state.show_add:
    with st.form("new_domain_form"):
        st.subheader("New Domain")
        
        name = st.text_input("Domain Name")
        
        # Scan Interval
        interval = st.number_input("Scan Interval (seconds)", min_value=60, value=3600, step=60)
        
        with st.expander("Domain Sources"):
            crt_sh = st.checkbox("crt.sh", value=True)
            anubis = st.checkbox("Anubis DB", value=True)
            hackertarget = st.checkbox("HackerTarget", value=True)
            urlscan = st.checkbox("URLScan.io", value=True)
        
        with st.expander("Check Options"):
            enable_dns = st.checkbox("Enable DNS Check", value=True)
            enable_http = st.checkbox("Enable HTTP Check", value=True)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.form_submit_button("Add"):
                # Collect Scanners
                scanners = []
                if crt_sh:
                    scanners.append("crt_sh")
                if anubis:
                    scanners.append("anubis")
                if hackertarget:
                    scanners.append("hackertarget")
                if urlscan:
                    scanners.append("urlscan")
                
                # Add domain to database
                add_domain(name, scanners, interval, enable_dns, enable_http)
                
                st.session_state.success_msg = f"Domain {name} added!"
                st.session_state.show_add = False
                st.rerun()
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_add = False
                st.rerun()

st.divider()

# Show Success Message
if "success_msg" in st.session_state:
    st.success(st.session_state.success_msg)
    del st.session_state.success_msg

# Domain list
if domains:
    for domain in domains:
        col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
        
        with col1:
            st.write(f"**{domain['name']}**")
        with col4:
            if st.button("✖", help="Delete Domain", key=f"delete_{domain['id']}"):
                delete_domain(domain['id'])
                st.rerun()
else:
    st.info("No Domains listed. Please add one!")