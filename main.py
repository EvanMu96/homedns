import argparse
import logging
import os
import socketserver
import threading
import time
from typing import Any, Final, List, Union

from homedns.queryhandlers import TCPRequestHandler, UDPRequestHandler

Server_TCP = socketserver.ThreadingTCPServer
Server_UDP = socketserver.ThreadingUDPServer

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
LOG: Final = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Start a DNS Server implemented in Python."
)
parser = argparse.ArgumentParser(
    description="Start a DNS implemented in Python. Usually DNSs use UDP on port 53."
)
parser.add_argument("--port", default=5153, type=int, help="The port to listen on.")

args = parser.parse_args()


class App:
    def __init__(self, port) -> None:

        self.servers: List[Union[Server_TCP, Server_UDP]] = []
        self.servers.append(Server_UDP(("", args.port), UDPRequestHandler))
        self.servers.append(Server_TCP(("", args.port), TCPRequestHandler))

    def run(self) -> Any:
        LOG.info("HomeDNS server is starting at %s", args.port)

        def _start(s):
            thread = threading.Thread(target=s.serve_forever)
            thread.daemon = True
            thread.start()
            LOG.info(
                "%s server loop running in thread: %s",
                s.RequestHandlerClass.__name__[:3],
                thread.name,
            )

        for s in self.servers:
            _start(s)

        try:
            while True:
                # log interval
                time.sleep(1)
        except KeyboardInterrupt:
            map(lambda s: s.shutdown(), self.servers)
            LOG.info("Shutting down servers. Bye bye")
        finally:
            exit(0)


if __name__ == "__main__":
    app = App(port=args.port)
    app.run()
