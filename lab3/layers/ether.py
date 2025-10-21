from __future__ import annotations

import struct
from typing import Optional

from utils import bytes_to_mac, mac_to_bytes

from .base import BaseLayer

ETH_P_IP = 0x0800


class Ether(BaseLayer):
    def __init__(self, src_mac: Optional[str] = None, dst_mac: Optional[str] = None,
                 eth_type: int = ETH_P_IP, raw: Optional[bytes] = None, payload: Optional[BaseLayer] = None):
        super().__init__(payload=payload)
        if raw is not None:
            # Parse Ethernet header (14 bytes)
            if len(raw) < 14:
                raise ValueError("Ether frame too short")
            dst_b, src_b, etype = struct.unpack("!6s6sH", raw[:14])
            self.dst_mac = bytes_to_mac(dst_b)
            self.src_mac = bytes_to_mac(src_b)
            self.type = etype
            # Only handle IPv4 payload for this lab
            rest = raw[14:]
            if self.type == ETH_P_IP and rest:
                from .ip import IP
                parsed = IP(raw=rest)
                self.payload = parsed
            else:
                self.payload = None
        else:
            if src_mac is None or dst_mac is None:
                raise ValueError("src_mac and dst_mac are required when not parsing raw bytes")
            self.src_mac = src_mac
            self.dst_mac = dst_mac
            self.type = eth_type

    def build(self) -> bytes:
        dst_b = mac_to_bytes(self.dst_mac)
        src_b = mac_to_bytes(self.src_mac)
        header = struct.pack("!6s6sH", dst_b, src_b, self.type)
        payload_bytes = self.payload.build() if self.payload else b""
        return header + payload_bytes

    def show(self, indent: int = 0) -> None:
        pad = "  " * indent
        print(f"{pad}### Ether ###")
        print(f"{pad}  dst_mac: {self.dst_mac}")
        print(f"{pad}  src_mac: {self.src_mac}")
        print(f"{pad}  type: {self.type:04x}")
        if self.payload:
            self.payload.show(indent + 1)        