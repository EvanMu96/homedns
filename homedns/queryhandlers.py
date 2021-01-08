import datetime
import logging
import os
import socket
import socketserver
import struct
import sys
import traceback
from typing import Any, Final, List

from .config import client_denylist, roots
from .lib import *

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
Log: Final = logging.getLogger(__name__)

# Base class for two types of DNS Handler
# implement common log operations and define interfaces
class BaseRequestHandler(socketserver.BaseRequestHandler):
    def get_data(self) -> Any:
        raise NotImplementedError

    def send_data(self, data: bytes) -> Any:
        raise NotImplementedError

    def forward_roots(self, data: bytes) -> Any:
        raise NotImplementedError

    def handle(self) -> None:
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        Log.info(
            "\n\n%s request %s (%s %s):"
            % (
                self.__class__.__name__[:3],
                now,
                self.client_address[0],
                self.client_address[1],
            )
        )
        denylist = self.get_denied_types(self.client_address[0])
        Log.debug(denylist)
        try:
            data = self.get_data()
            retcode, retdata = dns_response(
                data, (self.__class__.__name__[:3]).lower(), denylist
            )

            Log.debug(retcode)
            if retcode == 0:
                if retdata is not None:
                    Log.info("Find record in local db")
                    self.send_data(retdata)
            elif retcode == 1:
                Log.info("Need forwarding")
                self.forward_roots(data)
            elif retcode == 2:
                Log.info("blocked.")
                return
            else:
                Log.error("undefined error code ")
        except Exception:
            traceback.print_exc(file=sys.stderr)

    def get_denied_types(self, search_ip: str) -> List:
        ret = []
        for ip, type in client_denylist:
            Log.debug("ip: %s, search_ip: %s", ip, search_ip)
            if ip == search_ip:
                ret.append(type)
        return ret


# handle tcp request is necessary
class TCPRequestHandler(BaseRequestHandler):
    def get_data(self) -> Any:
        data = self.request.recv(8192).strip()
        sz = struct.unpack(">H", data[:2])[0]
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data: bytes) -> Any:
        sz = struct.pack(">H", len(data))
        return self.request.sendall(sz + data)

    def forward_roots(self, data: bytes) -> Any:
        recv = None
        for ip, port in roots:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if port is None:
                port = 53
            try:
                sock.connect((ip, port))
            except OSError as e:
                Log.error(e)
                sock.close()
                continue
            sz = struct.pack(">H", len(data))
            sock.sendall(sz + data)
            recv = sock.recv(8192)
            break
        Log.debug(recv)
        self.request.sendall(recv)


class UDPRequestHandler(BaseRequestHandler):
    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data: bytes) -> Any:
        return self.request[1].sendto(data, self.client_address)

    def forward_roots(self, data: bytes) -> Any:
        recv = None
        for ip, port in roots:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if port is None:
                port = 53
            Log.info("forward query to destip: %s, dest port: %d", ip, port)
            sock.sendto(data, (ip, port))
            recv = sock.recv(8192)
            if recv:
                break
        Log.debug(recv)
        self.request[1].sendto(recv, self.client_address)


__all__ = ["TCPRequestHandler", "UDPRequestHandler"]