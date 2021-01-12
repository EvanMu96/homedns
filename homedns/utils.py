from socket import socket
from typing import Any, Optional

from dnslib import AAAA, CNAME, MX, NS, A

from .constants import iterative_timeout


def set_iterative_timeout(sock: socket) -> None:
    sock.settimeout(iterative_timeout)


def get_default_port(mode: str) -> Optional[int]:
    if mode == "DoT":
        return 853
    elif mode == "DoH":
        return 443
    elif mode == "Plain":
        return 53
    else:
        return None


def RecordFactory(qtype: str, data: str, logger: Any) -> Any:
    if qtype == "A":
        return A(data)
    elif qtype == "CNAME":
        return CNAME(data)
    elif qtype == "AAAA":
        return AAAA(data)
    elif qtype == "NS":
        return NS(data)
    elif qtype == "MX":
        pref, entry = data.split()
        print(pref, entry)
        return MX(preference=int(pref), label=entry)
    else:
        logger.error("not implemented query type")


__all__ = ["set_iterative_timeout", "get_default_port", "RecordFactory"]
