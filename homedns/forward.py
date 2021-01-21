import base64
import socket
import ssl
import struct
from abc import ABC, abstractmethod
from typing import Any, Optional

import certifi
import urllib3
from dnslib import DNSRecord

from .confschema import Config
from .constants import iterative_timeout
from .utils import get_default_port, set_iterative_timeout


class Context:
    http = urllib3.PoolManager(ca_certs=certifi.where())
    ctx = ssl.create_default_context()
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_verify_locations(certifi.where())


class ABCForwarder(ABC):
    @abstractmethod
    def forward(self, data: bytes, config: Config, logger: Any) -> Optional[bytes]:
        raise NotImplementedError


class UDPForwarder(ABCForwarder):
    def forward(self, data: bytes, config: Config, logger: Any) -> Optional[bytes]:
        roots = config.roots
        recv = None
        for ip, port in roots:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            set_iterative_timeout(sock)
            if port is None:
                port = get_default_port("Plain")
            logger.info("forward query to destip: %s, dest port: %d", ip, port)
            try:
                sock.sendto(data, (ip, port))
                recv = sock.recv(8192)
            except OSError as e:
                logger.debug(e)
                continue
            else:
                logger.debug(recv)
                break
        return recv


class TCPForwarder(ABCForwarder):
    def forward(self, data: bytes, config: Config, logger: Any) -> Optional[bytes]:
        roots = config.roots  # type: ignore
        recv = None
        for ip, port in roots:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            set_iterative_timeout(sock)
            if port is None:
                port = get_default_port("Plain")
            logger.info("forward query to destip: %s, dest port: %d", ip, port)
            try:
                sock.connect((ip, port))
            except OSError as e:
                logger.error(e)
                sock.close()
                continue
            else:
                sz = struct.pack("!H", len(data))
                sock.sendall(sz + data)
                recv = sock.recv(8192)
                break
        return recv


class DoTForwarder(ABCForwarder):
    def forward(self, data: bytes, config: Config, logger: Any) -> Optional[bytes]:
        ctx = Context.ctx
        # todo : configurable DoT service
        roots = config.encrypted_roots
        if roots is None:
            return None
        for ip, hostname, etype in roots:
            if etype != "DoT":
                continue
            port = get_default_port(etype)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sslsock = ctx.wrap_socket(sock, server_hostname=hostname)
            logger.info("forward query to destip: %s, dest port: %d", ip, port)
            try:
                sslsock.connect((ip, port))
            except OSError as e:
                logger.error(e)
                sslsock.close()
                continue
            else:
                logger.debug("the cert is %s", str(sslsock.getpeercert()))
                sz = struct.pack("!H", len(data))
                sslsock.sendall(sz + data)
                recv = sslsock.recv(8192)
                logger.debug("%s \n", recv)
                break
        return recv


class DoHForwarder(ABCForwarder):
    def forward(self, data: bytes, config: Config, logger: Any) -> Optional[bytes]:
        roots = config.encrypted_roots
        if roots is None:
            return None
        query64 = base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")
        http = Context.http
        for ip, host, etype in roots:
            if etype != "DoH":
                continue
            requestURL = "https://" + host + "/dns-query?" + "dns=" + query64
            logger.debug("request URL: %s", requestURL)
            recv = http.request(
                "Get",
                requestURL,
                timeout=(iterative_timeout * 2),
                headers={"content-type": "application/dns-message"},
            ).data
            logger.debug("%s", DNSRecord.parse(recv))
            if recv:
                break
        return recv
