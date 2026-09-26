"""Connectionless UDP endpoint (charter R5) with injectable loss and corruption for tests."""
import random
import socket


class EndpointStats:
    def __init__(self):
        self.sent = 0
        self.dropped = 0
        self.corrupted = 0


class UdpEndpoint:
    def __init__(self, bind=("127.0.0.1", 0), drop=0.0, corrupt=0.0, seed=0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 << 20)
        except OSError:
            pass
        # Windows: an ICMP port-unreachable from an earlier sendto surfaces as
        # WSAECONNRESET on the next recvfrom. Turn that off where the ioctl exists.
        if hasattr(socket, "SIO_UDP_CONNRESET"):
            self.sock.ioctl(socket.SIO_UDP_CONNRESET, False)
        self.sock.bind(bind)
        self.addr = self.sock.getsockname()
        self.drop, self.corrupt = drop, corrupt
        self._rng = random.Random(seed)
        self.stats = EndpointStats()

    def send(self, data, addr):
        if self.drop and self._rng.random() < self.drop:
            self.stats.dropped += 1
            return
        if self.corrupt and self._rng.random() < self.corrupt:
            b = bytearray(data)
            b[self._rng.randrange(len(b))] ^= 1 << self._rng.randrange(8)
            data = bytes(b)
            self.stats.corrupted += 1
        try:
            self.sock.sendto(data, addr)
            self.stats.sent += 1
        except OSError:
            self.stats.dropped += 1  # peer gone or buffer full: the NAK path repairs it

    def recv(self, timeout):
        self.sock.settimeout(timeout)
        while True:
            try:
                return self.sock.recvfrom(65535)
            except socket.timeout:
                return None
            except ConnectionResetError:
                continue

    def close(self):
        self.sock.close()
