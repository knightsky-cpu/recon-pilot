from typing import List, Set
import requests
import time

CRT_URL = "https://crt.sh/?q=%25.{domain}&output=json"

def fetch_ct_domains(domain: str, delay: float = 1.0) -> List[str]:
    """Fetch subdomains from crt.sh for a given base domain.
    Returns a list of unique, lowercased FQDNs.
    """
    url = CRT_URL.format(domain=domain)
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return []
    try:
        data = r.json()
    except Exception:
        return []
    names: Set[str] = set()
    for row in data:
        # common_name and name_value can both contain entries; split by newlines
        for key in ("name_value","common_name"):
            v = row.get(key, "") or ""
            for line in str(v).splitlines():
                s = line.strip().lower()
                if s and s != domain and not s.startswith("*."):
                    names.add(s)
    time.sleep(delay)  # polite
    return sorted(names)
