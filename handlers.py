import traceback
import socketserver
import datetime
import struct
import sys
import logging
import os
from typing import Any, AnyStr
from lib import *

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
Log = logging.getLogger(__name__)

# Base class for two types of DNS Handler
# implement common log operations and define interfaces
class BaseRequestHandler(socketserver.BaseRequestHandler):

    def get_data(self) -> Any:
        raise NotImplementedError

    def send_data(self, data: str) -> Any:
        raise NotImplementedError

    def handle(self) -> None:
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        print("\n\n%s request %s (%s %s):" % (self.__class__.__name__[:3], now, self.client_address[0],
                                               self.client_address[1]))
        try:
            data = self.get_data()
            print(len(data), data)  # repr(data).replace('\\x', '')[1:-1]
            self.send_data(dns_response(data, (self.__class__.__name__[:3]).lower()))
        except Exception:
            traceback.print_exc(file=sys.stderr)

# handle tcp request is necessary
class TCPRequestHandler(BaseRequestHandler):

    def get_data(self) -> Any:
        data = self.request.recv(8192).strip()
        # unserialzed data
        sz = struct.unpack('>H', data[:2])[0]
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data: AnyStr) -> Any:
        # serialize data
        sz = struct.pack('>H', len(data))
        return self.request.sendall(sz + data)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data: str) -> Any:
        return self.request[1].sendto(data, self.client_address)


__all__ = ['TCPRequestHandler', 'UDPRequestHandler']