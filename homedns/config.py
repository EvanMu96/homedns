from typing import List, Optional, Tuple

# a example of root hints
roots: List[Tuple[str, Optional[int]]] = [
    ("192.168.102.81", None),
    ("114.114.114.114", None),
]
db_path: str = "data/dns_records.db"

# denylist config scheme ('ip', 'RR Type')
# deny all for an ip addr ('ip', '*')
client_denylist: List[Tuple[str, str]] = [
    ("192.168.56.103", "*"),
    ("192.168.56.102", "A"),
]
