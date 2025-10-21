import socket
from typing import Optional

from layers import DNS, ICMP, IP, TCP, UDP, Ether
from utils import ip_to_bytes

# Public API: send, sendp, sr, sniff

def _ensure_ip(pkt):
    # If starts at Ether, drop L2 and return IP for L3 send
    if isinstance(pkt, Ether):
        return pkt.payload if hasattr(pkt, "payload") else None
    return pkt


def _dst_of(pkt) -> str:
    if isinstance(pkt, Ether) and getattr(pkt, "payload", None) and isinstance(pkt.payload, IP):
        return pkt.payload.dst_ip
    if isinstance(pkt, IP):
        return pkt.dst_ip
    return "?"


def send(pkt):
    ip = _ensure_ip(pkt)
    if not isinstance(ip, IP):
        raise ValueError("send() expects an IP packet or an Ether/IP stack")
    b = ip.build()
    dst = ip.dst_ip
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    try:
        sock.sendto(b, (dst, 0))
        print(f"[+] Sent packet to {dst} (Layer 3)")
    finally:
        sock.close()


def sendp(pkt, interface: str):
    if not isinstance(pkt, Ether):
        raise ValueError("sendp() requires an Ether frame as the first layer")
    frame = pkt.build()
    af_packet = getattr(socket, "AF_PACKET", None)
    if af_packet is None:
        raise NotImplementedError("Layer-2 send requires Linux (AF_PACKET)")
    sock = socket.socket(af_packet, socket.SOCK_RAW)
    try:
        sock.bind((interface, 0))
        sock.send(frame)
        print(f"[+] Sent packet on {interface} (Layer 2)")
    finally:
        sock.close()


def sr(pkt, interface: Optional[str] = None, timeout: float = 2.0):
    print("SR is sending")
    # Transmit at L3
    send(pkt)
    # Receive at L2 on any interface
    af_packet = getattr(socket, "AF_PACKET", None)
    if af_packet is None:
        raise NotImplementedError("sr() sniff requires Linux (AF_PACKET)")
    recv_sock = socket.socket(af_packet, socket.SOCK_RAW, socket.htons(0x0003))
    recv_sock.settimeout(timeout)
    try:
        print(f"[+] Sent packet to {_dst_of(pkt)}, waiting for reply...")
        frame = recv_sock.recv(65535)
        if not frame:
            raise TimeoutError("No reply")
        print(f"[+] Received reply from {interface or 'any'}")
        return Ether(raw=frame)
    finally:
        recv_sock.close()


def sniff_packet(interface: Optional[str] = None, timeout: float = 2.0):
    af_packet = getattr(socket, "AF_PACKET", None)
    if af_packet is None:
        raise NotImplementedError("sniff requires Linux (AF_PACKET)")
    sock = socket.socket(af_packet, socket.SOCK_RAW, socket.htons(0x0003))
    if interface:
        sock.bind((interface, 0))
    sock.settimeout(timeout)
    try:
        frame = sock.recv(65535)
        pkt = Ether(raw=frame)
        pkt.show()
        return pkt
    finally:
        sock.close()

# Back-compat alias expected by assignment text
sniff = sniff_packet


def create_icmp_packet(src_mac, dst_mac, src_ip, dst_ip, seq=1):
    eth = Ether(src_mac=src_mac, dst_mac=dst_mac)
    ip = IP(src_ip=src_ip, dst_ip=dst_ip)
    icmp = ICMP(type=8, code=0, id=1, seq=seq)
    return eth / ip / icmp

def create_dns_packet(src_mac, dst_mac, src_ip, dst_ip, qname):
    eth = Ether(src_mac=src_mac, dst_mac=dst_mac)
    ip = IP(src_ip=src_ip, dst_ip=dst_ip)
    udp = UDP(sport=12345, dport=53)
    dns = DNS(qname=qname)
    return eth / ip / udp / dns

def send_icmp_packet(packet):
    send(packet)

def send_dns_packet(packet):
    send(packet)

def receive_packet():
    return sr(Ether(raw=b''), timeout=1)

def sniff_packets(interface):
    return sniff(interface=interface)    return sniff(interface=interface)