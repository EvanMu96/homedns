from homedns.confschema import Config

# some hardcoded default config
config = Config(
    roots=[
        ("192.168.102.81", None),
        ("114.114.114.114", None),
    ],
    encrypted_roots=[
        ("1.1.1.1", "cloudflare-dns.com", "DoT"),
        ("1.1.1.1", "cloudflare-dns.com", "DoH"),
    ],
    db_path="data/dns_records.db",
    client_denylist=[
        ("192.168.56.103", "*"),
        ("192.168.56.102", "A"),
    ],
)
