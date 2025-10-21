from __future__ import annotations

import socket
import struct
from typing import Optional

from utils import bytes_to_ip, checksum_ones_complement, ip_to_bytes

from .base import BaseLayer

PROTO_ICMP = 1
PROTO_TCP = 6
PROTO_UDP = 17


class IP(BaseLayer):
    def __init__(self,
                 src_ip: Optional[str] = None,
                 dst_ip: Optional[str] = None,
                 ttl: int = 64,
                 proto: Optional[int] = None,
                 raw: Optional[bytes] = None,
                 payload: Optional[BaseLayer] = None):
        super().__init__(payload=payload)
        self.version = 4
        self.ihl = 5  # 20-byte header, no options
        if raw is not None:
            self._parse(raw)
        else:
            self.src_ip = src_ip or "0.0.0.0"
            self.dst_ip = dst_ip or "0.0.0.0"
            self.ttl = ttl
            self.proto = proto if proto is not None else 0

    # Operator overloading to wire L4 IPs for checksum
    def __truediv__(self, other: BaseLayer) -> "IP":
        res = super().__truediv__(other)
        # If payload is TCP/UDP, set src/dst on it for pseudo-header checksums
        lname = other.__class__.__name__
        if lname in ("TCP", "UDP"):
            try:
                setattr(other, "src_ip", self.src_ip)
                setattr(other, "dst_ip", self.dst_ip)
            except Exception:
                pass
        return res

    def _parse(self, raw: bytes) -> None:
        if len(raw) < 20:
            raise ValueError("IP packet too short")
        v_ihl, tos, total_len, ident, flags_frag, ttl, proto, chksum, src, dst = struct.unpack(
            "!BBHHHBBH4s4s", raw[:20]
        )
        self.version = v_ihl >> 4
        self.ihl = v_ihl & 0x0F
        hdr_len = self.ihl * 4
        if len(raw) < hdr_len:
            raise ValueError("IP header length exceeds provided data")
        self.ttl = ttl
        self.proto = proto
        self.src_ip = bytes_to_ip(src)
        self.dst_ip = bytes_to_ip(dst)
        payload_bytes = raw[hdr_len:total_len if total_len else None]
        # Parse next layer
        if self.proto == PROTO_ICMP and payload_bytes:
            from .icmp import ICMP
            self.payload = ICMP(raw=payload_bytes)
            # also wire IPs into L4 for convenience
            setattr(self.payload, "src_ip", self.src_ip)
            setattr(self.payload, "dst_ip", self.dst_ip)
        elif self.proto == PROTO_TCP and payload_bytes:
            from .tcp import TCP
            self.payload = TCP(raw=payload_bytes)
            setattr(self.payload, "src_ip", self.src_ip)
            setattr(self.payload, "dst_ip", self.dst_ip)
        elif self.proto == PROTO_UDP and payload_bytes:
            from .udp import UDP
            self.payload = UDP(raw=payload_bytes)
            setattr(self.payload, "src_ip", self.src_ip)
            setattr(self.payload, "dst_ip", self.dst_ip)
        else:
            self.payload = None

    def _infer_proto(self):
        """Infer protocol number from payload if not set"""
        if self.payload is not None and (self.proto is None or self.proto == 0):
            lname = self.payload.__class__.__name__
            if lname == "ICMP":
                self.proto = PROTO_ICMP
            elif lname == "TCP":
                self.proto = PROTO_TCP
            elif lname == "UDP":
                self.proto = PROTO_UDP
            else:
                self.proto = 0
        elif self.proto is None:
            self.proto = 0

    def build(self) -> bytes:
        # Infer proto if needed
        self._infer_proto()
        # Make sure L4 has IPs for checksum (works even if stacking started at Ether)
        if self.payload is not None:
            lname = self.payload.__class__.__name__
            if lname in ("TCP", "UDP"):
                try:
                    setattr(self.payload, "src_ip", self.src_ip)
                    setattr(self.payload, "dst_ip", self.dst_ip)
                except Exception:
                    pass
        payload_bytes = self.payload.build() if self.payload else b""
        v_ihl = (self.version << 4) | self.ihl
        total_len = 20 + len(payload_bytes)
        header_wo_csum = struct.pack(
            "!BBHHHBBH4s4s",
            v_ihl,
            0,  # TOS
            total_len,
            0,  # Identification
            0,  # Flags/Frag
            self.ttl,
            self.proto,
            0,  # checksum placeholder
            ip_to_bytes(self.src_ip),
            ip_to_bytes(self.dst_ip),
        )
        csum = checksum_ones_complement(header_wo_csum)
        header = struct.pack(
            "!BBHHHBBH4s4s",
            v_ihl,
            0,
            total_len,
            0,
            0,
            self.ttl,
            self.proto,
            csum,
            ip_to_bytes(self.src_ip),
            ip_to_bytes(self.dst_ip),
        )
        return header + payload_bytes

    def show(self, indent: int = 0) -> None:
        # Infer proto before showing
        self._infer_proto()
        
        pad = "  " * indent
        print(f"{pad}### IP ###")
        print(f"{pad}  version: {self.version}")
        print(f"{pad}  ihl: {self.ihl}")
        print(f"{pad}  tos: 0")
        # total_len only known on build; recompute from payload length for display
        total_len = 20 + (len(self.payload.build()) if self.payload else 0)
        print(f"{pad}  total_len: {total_len}")
        print(f"{pad}  ident: 0")
        print(f"{pad}  flags_frag: 0")
        print(f"{pad}  ttl: {self.ttl}")
        print(f"{pad}  proto: {self.proto}")
        header_wo_csum = struct.pack(
            "!BBHHHBBH4s4s",
            (self.version << 4) | self.ihl,
            0,
            total_len,
            0,
            0,
            self.ttl,
            self.proto,
            0,
            ip_to_bytes(self.src_ip),
            ip_to_bytes(self.dst_ip),
        )
        csum = checksum_ones_complement(header_wo_csum)
        print(f"{pad}  checksum: {csum}")
        print(f"{pad}  src_ip: {self.src_ip}")
        print(f"{pad}  dst_ip: {self.dst_ip}")
        if self.payload:
            self.payload.show(indent + 1)