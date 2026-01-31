from .db_manager import (
    init_db,
    add_domain,
    get_all_domains,
    delete_domain,
    add_subdomain,
    get_subdomains,
    update_last_scan,
    get_new_subdomains,
    get_subdomain_id,
    mark_subdomain_as_dns_checked,
    update_subdomain_http,
    mark_subdomain_as_seen
)