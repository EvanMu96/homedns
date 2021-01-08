import argparse

from homedns.homednsserver import HomeDNSServer

parser = argparse.ArgumentParser(
    description="Start a DNS Server implemented in Python."
)
parser = argparse.ArgumentParser(
    description="Start a DNS implemented in Python. Usually DNSs use UDP on port 53."
)
parser.add_argument("--port", default=8053, type=int, help="The port to listen on.")

args = parser.parse_args()

if __name__ == "__main__":
    app = HomeDNSServer(port=args.port)
    app.run()
