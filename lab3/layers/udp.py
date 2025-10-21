from __future__ import annotations

import socket
import struct
from typing import Optional

from utils import checksum_ones_complement, ip_to_bytes

from .base import BaseLayer

PROTO_UDP = 17


class UDP(BaseLayer):
    def __init__(self, sport: int = 12345, dport: int = 80, data: bytes = b"",
                 raw: Optional[bytes] = None, payload: Optional[BaseLayer] = None):
        super().__init__(payload=payload)
        self.src_ip: Optional[str] = None  # wired when stacked over IP
        self.dst_ip: Optional[str] = None
        if raw is not None:
            if len(raw) < 8:
                raise ValueError("UDP segment too short")
            self.sport, self.dport, self.length, self.checksum = struct.unpack("!HHHH", raw[:8])
            body = raw[8:self.length if self.length else None]
            # If likely DNS (ports 53), try to parse; otherwise keep raw as data
            if self.dport == 53 or self.sport == 53:
                try:
                    from .dns import DNS
                    self.payload = DNS(raw=body)
                except Exception:
                    self.payload = None
                    self.data = body
            else:
                self.payload = None
                self.data = body
        else:
            self.sport = sport
            self.dport = dport
            self.data = data
            # length will be computed at build time with payload
            self.length = 8 + (len(self.data) if data else 0)
            self.checksum = 0

    def _payload_bytes(self) -> bytes:
        if self.payload is not None:
            return self.payload.build()
        return self.data if hasattr(self, "data") and self.data else b""

    def build(self) -> bytes:
        payload_bytes = self._payload_bytes()
        self.length = 8 + len(payload_bytes)
        header_wo_csum = struct.pack("!HHHH", self.sport, self.dport, self.length, 0)
        # UDP checksum over pseudo-header + UDP header + data
        src_ip = getattr(self, "src_ip", None)
        dst_ip = getattr(self, "dst_ip", None)
        if not src_ip or not dst_ip:
            # Allow building without checksum if not wired; leave zero as many stacks do
            pseudo = b""
            udp_for_csum = header_wo_csum + payload_bytes
            csum = checksum_ones_complement(udp_for_csum)
        else:
            pseudo = struct.pack(
                "!4s4sBBH",
                ip_to_bytes(src_ip),
                ip_to_bytes(dst_ip),
                0,
                PROTO_UDP,
                self.length,
            )
            csum = checksum_ones_complement(pseudo + header_wo_csum + payload_bytes)
            if csum == 0:
                csum = 0xFFFF  # UDP checksum of zero is transmitted as 0xFFFF
        self.checksum = csum
        header = struct.pack("!HHHH", self.sport, self.dport, self.length, self.checksum)
        return header + payload_bytes

    def show(self, indent: int = 0) -> None:
        pad = "  " * indent
        print(f"{pad}### UDP ###")
        print(f"{pad}  sport: {self.sport}")
        print(f"{pad}  dport: {self.dport}")
        print(f"{pad}  length: {self.length}")
        print(f"{pad}  checksum: {self.checksum:04x}")
        if getattr(self, "src_ip", None):
            print(f"{pad}  src_ip: {self.src_ip}")
        if getattr(self, "dst_ip", None):
            print(f"{pad}  dst_ip: {self.dst_ip}")
        if self.payload:
            self.payload.show(indent + 1)            print(f"{pad}  dst_ip: {self.dst_ip}")
        if self.payload:
            self.payload.show(indent + 1)