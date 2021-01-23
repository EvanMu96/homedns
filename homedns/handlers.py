import datetime
import logging
import os
import socketserver
import struct
import sys
import traceback
from typing import Any, Final, List

from .forward import DoHForwarder, DoTForwarder, TCPForwarder, UDPForwarder
from .lib import dns_response

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger: Final = logging.getLogger(__name__)

# Base class for two types of DNS Handler
# implement common log operations and define interfaces
class BaseRequestHandler(socketserver.BaseRequestHandler):
    dot_fwder = DoTForwarder()
    doh_fwder = DoHForwarder()

    def get_data(self) -> Any:
        raise NotImplementedError

    def send_data(self, data: bytes) -> Any:
        raise NotImplementedError

    def forward_roots(self, data: bytes) -> Any:
        raise NotImplementedError

    def handle(self) -> None:
        # ignore dynamic assigned attribute
        config = self.server.dns_config  # type: ignore

        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        logger.info(
            "\n\n%s request %s (%s %s):"
            % (
                self.__class__.__name__[:3],
                now,
                self.client_address[0],
                self.client_address[1],
            )
        )
        denylist = self.get_denied_types(self.client_address[0])
        logger.debug(denylist)
        try:
            data = self.get_data()
            if not data:
                return
            retcode, retdata = dns_response(
                data,
                config.db_path,
                (self.__class__.__name__[:3]).lower(),
                denylist,
            )

            logger.debug(retcode)
            if retcode == 0:
                if retdata is not None:
                    logger.info("Find record in local db")
                    self.send_data(retdata)
            elif retcode == 1:
                logger.info("Need forwarding")
                self.forward_roots(data)
            elif retcode == 2:
                logger.info("blocked.")
                return
            else:
                logger.error("undefined error code ")
        except Exception:
            traceback.print_exc(file=sys.stderr)

    def get_denied_types(self, search_ip: str) -> List:
        client_denylist = self.server.dns_config.client_denylist  # type: ignore
        ret = []
        for ip, type in client_denylist:
            logger.debug("ip: %s, search_ip: %s", ip, search_ip)
            if ip == search_ip:
                ret.append(type)
        return ret


# handle tcp request is necessary
class TCPRequestHandler(BaseRequestHandler):
    tcp_fwder = TCPForwarder()

    def get_data(self) -> Any:
        data = self.request.recv(8192).strip()
        sz = struct.unpack("!H", data[:2])[0]
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data: bytes) -> Any:
        sz = struct.pack("!H", len(data))
        return self.request.sendall(sz + data)

    def forward_roots(self, data: bytes) -> Any:
        config = self.server.dns_config  # type: ignore
        recv = None
        if config.encrypted_roots:
            recv = self.doh_fwder.forward(data, config, logger)
            if not recv:
                recv = self.dot_fwder.forward(data, config, logger)
        else:
            recv = self.tcp_fwder.forward(data, config, logger)
        if recv is not None:
            self.request.sendall(recv)


class UDPRequestHandler(BaseRequestHandler):
    udp_fwder = UDPForwarder()

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data: bytes) -> Any:
        return self.request[1].sendto(data, self.client_address)

    def forward_roots(self, data: bytes) -> Any:
        config = self.server.dns_config  # type: ignore
        if config.encrypted_roots:
            recv = self.doh_fwder.forward(data, config, logger)
            if not recv:
                recv = self.dot_fwder.forward(data, config, logger)
                if recv is not None:
                    recv = recv[2:]
        else:
            recv = self.udp_fwder.forward(data, config, logger)
        if recv is not None:
            self.request[1].sendto(recv, self.client_address)


__all__ = ["TCPRequestHandler", "UDPRequestHandler"]
