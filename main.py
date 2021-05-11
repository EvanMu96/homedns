import argparse

import dns_config
from homedns.server import HomeDNSServer

config = dns_config.config

parser = argparse.ArgumentParser(
    description="A DNS toy DNS service."
)
parser.add_argument("--port", default=8053, type=int)

args = parser.parse_args()

if __name__ == "__main__":
    app = HomeDNSServer(port=args.port, config=config)
    app.run()
