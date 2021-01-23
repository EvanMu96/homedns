import argparse

from homedns.confschema import Config
from homedns.server import HomeDNSServer

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

parser = argparse.ArgumentParser(
    description="Start a DNS Server implemented in Python."
)
parser = argparse.ArgumentParser(
    description="Start a DNS implemented in Python. Usually DNSs use UDP on port 53."
)
parser.add_argument("--port", default=8053, type=int, help="The port to listen on.")

args = parser.parse_args()

if __name__ == "__main__":
    app = HomeDNSServer(port=args.port, config=config)
    app.run()
