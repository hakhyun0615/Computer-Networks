from __future__ import annotations

import socket
import struct
from typing import Optional

from utils import checksum_ones_complement, ip_to_bytes

from .base import BaseLayer

PROTO_TCP = 6


class TCP(BaseLayer):
    def __init__(self, sport: int = 12345, dport: int = 80, seq: int = 0, ack: int = 0,
                 flags: int = 0x02, window: int = 8192, data: bytes = b"",
                 raw: Optional[bytes] = None, payload: Optional[BaseLayer] = None):
        super().__init__(payload=payload)
        self.src_ip: Optional[str] = None  # wired when stacked over IP
        self.dst_ip: Optional[str] = None
        if raw is not None:
            if len(raw) < 20:
                raise ValueError("TCP segment too short")
            (self.sport, self.dport, self.seq, self.ack, offset_flags,
             self.flags, self.window, self.checksum, self.urg_ptr) = struct.unpack("!HHLLBBHHH", raw[:20])
            self.offset = (offset_flags >> 4) & 0xF
            hdr_len = self.offset * 4
            self.options = raw[20:hdr_len] if hdr_len > 20 else b""
            self.data = raw[hdr_len:]
        else:
            self.sport = sport
            self.dport = dport
            self.seq = seq
            self.ack = ack
            self.flags = flags
            self.window = window
            self.checksum = 0
            self.urg_ptr = 0
            self.offset = 5  # 20 bytes, no options
            self.options = b""
            self.data = data

    def _header_wo_csum(self) -> bytes:
        offset_flags = (self.offset << 4) | 0
        return struct.pack(
            "!HHLLBBHHH",
            self.sport,
            self.dport,
            self.seq,
            self.ack,
            offset_flags,
            self.flags,
            self.window,
            0,
            self.urg_ptr,
        ) + (self.options if self.options else b"")

    def build(self) -> bytes:
        payload_bytes = self.data
        header_wo_csum = self._header_wo_csum()
        length = len(header_wo_csum) + len(payload_bytes)
        src_ip = getattr(self, "src_ip", None)
        dst_ip = getattr(self, "dst_ip", None)
        if src_ip and dst_ip:
            pseudo = struct.pack(
                "!4s4sBBH",
                ip_to_bytes(src_ip),
                ip_to_bytes(dst_ip),
                0,
                PROTO_TCP,
                length,
            )
            csum = checksum_ones_complement(pseudo + header_wo_csum + payload_bytes)
        else:
            csum = checksum_ones_complement(header_wo_csum + payload_bytes)
        self.checksum = csum
        # Repack with checksum
        offset_flags = (self.offset << 4) | 0
        header = struct.pack(
            "!HHLLBBHHH",
            self.sport,
            self.dport,
            self.seq,
            self.ack,
            offset_flags,
            self.flags,
            self.window,
            self.checksum,
            self.urg_ptr,
        ) + (self.options if self.options else b"")
        return header + payload_bytes

    def show(self, indent: int = 0) -> None:
        pad = "  " * indent
        print(f"{pad}### TCP ###")
        print(f"{pad}  sport: {self.sport}")
        print(f"{pad}  dport: {self.dport}")
        print(f"{pad}  seq: {self.seq}")
        print(f"{pad}  ack: {self.ack}")
        print(f"{pad}  flags: {self.flags}")
        print(f"{pad}  window: {self.window}")
        print(f"{pad}  checksum: {self.checksum}")
        if getattr(self, "src_ip", None):
            print(f"{pad}  src_ip: {self.src_ip}")
        if getattr(self, "dst_ip", None):
            print(f"{pad}  dst_ip: {self.dst_ip}")
        if self.data:
            print(f"{pad}  data: {self.data.hex() if isinstance(self.data, bytes) else self.data}")            print(f"{pad}  dst_ip: {self.dst_ip}")
        if self.data:
            print(f"{pad}  data: {self.data.hex() if isinstance(self.data, bytes) else self.data}")