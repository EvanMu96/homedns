from socket import socket

__iterative_timeout = 0.5  # second


def set_iterative_timeout(sock: socket):
    sock.settimeout(__iterative_timeout)


__all__ = ["set_iterative_timeout"]
