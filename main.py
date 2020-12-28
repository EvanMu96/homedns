import argparse
import time
import threading
import socketserver
import logging
import os
from typing import Any, Final, List, Union
from handlers import *

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
LOG: Final = logging.getLogger(__name__)

Server_TCP = socketserver.ThreadingTCPServer
Server_UDP = socketserver.ThreadingUDPServer


def main() -> Any:
    parser = argparse.ArgumentParser(description="Start a DNS implemented in Python.")
    parser = argparse.ArgumentParser(
        description="Start a DNS implemented in Python. Usually DNSs use UDP on port 53."
    )
    parser.add_argument("--port", default=5053, type=int, help="The port to listen on.")

    args = parser.parse_args()

    LOG.info("starting nameserver... %s", args.port)

    servers: List[Union[Server_TCP, Server_UDP]] = []

    servers.append(Server_UDP(("", args.port), UDPRequestHandler))
    servers.append(Server_TCP(("", args.port), TCPRequestHandler))

    def _start(s):
        thread = threading.Thread(target=s.serve_forever)
        thread.daemon = True
        thread.start()
        LOG.info(
            "%s server loop running in thread: %s"
            % (s.RequestHandlerClass.__name__[:3], thread.name)
        )

    for s in servers:
        _start(s)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        map(lambda s: s.shutdown(), servers)
        LOG.info("Bye bye")


if __name__ == "__main__":
    main()
