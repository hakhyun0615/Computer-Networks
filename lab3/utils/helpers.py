import socket
from typing import Optional


def checksum_ones_complement(data: bytes) -> int:
    """Compute the Internet checksum (one's complement sum of 16-bit words).
    Pads odd-length data with one zero byte as per RFC 1071.
    """
    if len(data) % 2 == 1:
        data += b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) + data[i + 1]
        total = (total & 0xFFFF) + (total >> 16)  # fold carry early
    # final fold and one's complement
    total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def ip_to_bytes(ip: str) -> bytes:
    """Convert dotted-quad IPv4 to 4 bytes (network byte order)."""
    return socket.inet_aton(ip)


def bytes_to_ip(b: bytes) -> str:
    """Convert 4-byte IPv4 into dotted-quad string."""
    return socket.inet_ntoa(b)


def mac_to_bytes(mac: str) -> bytes:
    """Convert colon-separated MAC (aa:bb:cc:dd:ee:ff) to 6 bytes."""
    parts = mac.split(":")
    if len(parts) != 6:
        raise ValueError(f"Invalid MAC: {mac}")
    return bytes(int(p, 16) for p in parts)


def bytes_to_mac(b: bytes) -> str:
    """Convert 6 bytes into colon-separated lower-hex MAC string."""
    if len(b) != 6:
        raise ValueError("MAC must be 6 bytes")
    return ":".join(f"{x:02x}" for x in b)