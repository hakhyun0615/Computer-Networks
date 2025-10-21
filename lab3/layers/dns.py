from __future__ import annotations

import struct
from typing import Optional, Tuple

from .base import BaseLayer


class DNS(BaseLayer):
    def __init__(self, qname: Optional[str] = None, qtype: int = 1, qclass: int = 1,
                 raw: Optional[bytes] = None, payload: Optional[BaseLayer] = None):
        super().__init__(payload=payload)
        if raw is not None:
            self._parse(raw)
        else:
            self.id = 0
            self.flags = 0x0100  # RD set
            self.qdcount = 1
            self.ancount = 0
            self.nscount = 0
            self.arcount = 0
            self.qname = qname or ""
            self.qtype = qtype
            self.qclass = qclass
            self.addr = None

    def _encode_qname(self, name: str) -> bytes:
        out = b""
        for label in name.split('.'):
            out += bytes([len(label)]) + label.encode()
        return out + b"\x00"

    def _decode_qname(self, data: bytes, offset: int) -> Tuple[str, int]:
        labels = []
        i = offset
        while i < len(data):
            l = data[i]
            if l == 0:
                i += 1
                break
            # handle simple labels only (no compression for this lab parse)
            labels.append(data[i + 1:i + 1 + l].decode())
            i += 1 + l
        return ".".join(labels), i

    def _parse(self, raw: bytes) -> None:
        if len(raw) < 12:
            raise ValueError("DNS too short")
        self.id, self.flags, self.qdcount, self.ancount, self.nscount, self.arcount = struct.unpack("!HHHHHH", raw[:12])
        off = 12
        # Question
        self.qname, off = self._decode_qname(raw, off)
        self.qtype, self.qclass = struct.unpack("!HH", raw[off:off + 4])
        off += 4
        # Answers (only decode first A RR if present)
        self.addr = None
        for _ in range(self.ancount):
            # name may be a pointer; skip by reading 2 bytes and checking pointer bit
            name_ptr = raw[off:off + 2]
            off += 2
            rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", raw[off:off + 10])
            off += 10
            rdata = raw[off:off + rdlength]
            off += rdlength
            if rtype == 1 and rclass == 1 and rdlength == 4:
                self.addr = f"{rdata[0]}.{rdata[1]}.{rdata[2]}.{rdata[3]}"
                break

    def build(self) -> bytes:
        header = struct.pack("!HHHHHH", 0x030C, 0x0100, 1, 0, 0, 0)  # id random-ish, RD=1
        q = self._encode_qname(self.qname) + struct.pack("!HH", self.qtype, self.qclass)
        return header + q

    def show(self, indent: int = 0) -> None:
        pad = "  " * indent
        print(f"{pad}### DNS ###")
        if hasattr(self, "id"):
            print(f"{pad}  id: {self.id:04x}")
        print(f"{pad}  qname: {getattr(self, 'qname', '')}")
        if getattr(self, "addr", None):
            print(f"{pad}  addr: {self.addr}")