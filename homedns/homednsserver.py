import logging
import os
import socketserver
import threading
import time
from typing import Any, Final, List, Union

from .queryhandlers import TCPRequestHandler, UDPRequestHandler

Server_TCP = socketserver.ThreadingTCPServer
Server_UDP = socketserver.ThreadingUDPServer

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
LOG: Final = logging.getLogger(__name__)


class HomeDNSServer:
    def __init__(self, port) -> None:
        self.port = port
        self.servers: List[Union[Server_TCP, Server_UDP]] = []
        self.servers.append(Server_UDP(("", self.port), UDPRequestHandler))
        self.servers.append(Server_TCP(("", self.port), TCPRequestHandler))

    def run(self) -> Any:
        LOG.info("HomeDNS server is starting at %s", self.port)

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
