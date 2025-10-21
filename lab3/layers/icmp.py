from __future__ import annotations

import struct
from typing import Optional

from utils import checksum_ones_complement

from .base import BaseLayer


class ICMP(BaseLayer):
    def __init__(self, type: int = 8, code: int = 0, id: int = 0, seq: int = 0,
                 data: bytes = b"", raw: Optional[bytes] = None, payload: Optional[BaseLayer] = None):
        super().__init__(payload=payload)
        if raw is not None:
            if len(raw) < 8:  # Standard Echo header is 8 bytes including checksum
                raise ValueError("ICMP packet too short")
            self.type, self.code, self.checksum, self.id, self.seq = struct.unpack("!BBHHH", raw[:8])
            self.data = raw[8:]
        else:
            self.type = type
            self.code = code
            self.id = id
            self.seq = seq
            self.data = data
            self.checksum = 0

    def build(self) -> bytes:
        header_wo_csum = struct.pack("!BBHHH", self.type, self.code, 0, self.id, self.seq)
        csum = checksum_ones_complement(header_wo_csum + self.data)
        self.checksum = csum
        header = struct.pack("!BBHHH", self.type, self.code, self.checksum, self.id, self.seq)
        return header + self.data

    def show(self, indent: int = 0) -> None:
        pad = "  " * indent
        print(f"{pad}### ICMP ###")
        print(f"{pad}  type: {self.type}")
        print(f"{pad}  code: {self.code}")
        print(f"{pad}  checksum: {self.checksum:04x}")
        print(f"{pad}  id: {self.id}")
        print(f"{pad}  seq: {self.seq}")
        if self.data:
            print(f"{pad}  data: {self.data.hex()}")
        if self.payload:
            self.payload.show(indent + 1)            print(f"{pad}  data: {self.data.hex()}")
        if self.payload:
            self.payload.show(indent + 1)