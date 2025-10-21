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


def _src_of(pkt) -> str:
    if isinstance(pkt, Ether) and getattr(pkt, "payload", None) and isinstance(pkt.payload, IP):
        return pkt.payload.src_ip
    if isinstance(pkt, IP):
        return pkt.src_ip
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

    # Determine expected protocol and ports from the outgoing packet
    def _extract_expectations(p):
        # Unwrap to IP layer
        ip_layer = p.payload if isinstance(p, Ether) else p
        l4 = getattr(ip_layer, "payload", None)
        proto = getattr(ip_layer, "proto", 0)
        src_ip = getattr(ip_layer, "src_ip", None)
        exp = {"proto": proto, "src_ip": src_ip}
        if l4 and l4.__class__.__name__ == "UDP":
            exp.update({
                "udp_sport": getattr(l4, "sport", None),
                "udp_dport": getattr(l4, "dport", None),
            })
            # If proto not set on IP, infer UDP=17
            if not proto:
                exp["proto"] = 17
        elif l4 and l4.__class__.__name__ == "TCP":
            exp.update({
                "tcp_sport": getattr(l4, "sport", None),
                "tcp_dport": getattr(l4, "dport", None),
            })
            if not proto:
                exp["proto"] = 6
        elif l4 and l4.__class__.__name__ == "ICMP":
            if not proto:
                exp["proto"] = 1
        return exp

    exp = _extract_expectations(pkt)

    # Receive at L2 on specified interface
    af_packet = getattr(socket, "AF_PACKET", None)
    if af_packet is None:
        raise NotImplementedError("sr() sniff requires Linux (AF_PACKET)")
    recv_sock = socket.socket(af_packet, socket.SOCK_RAW, socket.htons(0x0003))
    if interface:
        recv_sock.bind((interface, 0))
    recv_sock.settimeout(timeout)

    try:
        print(f"[+] Sent packet to {_dst_of(pkt)}, waiting for reply on {interface or 'any'}...")
        while True:
            try:
                frame = recv_sock.recv(65535)
            except socket.timeout:
                raise TimeoutError("No reply before timeout")
            if not frame:
                continue
            try:
                ether = Ether(raw=frame)
                ip = ether.get_layer("IP")
                if not ip:
                    continue
                if exp.get("src_ip") and getattr(ip, "dst_ip", None) != exp["src_ip"]:
                    continue
                # Protocol filter
                proto = getattr(ip, "proto", None)
                if exp.get("proto") and proto != exp["proto"]:
                    continue
                # UDP-specific port flip check (dns)
                if proto == 17:
                    udp = ether.get_layer("UDP")
                    if not udp:
                        continue
                    udp_sport = getattr(udp, "sport", None)
                    udp_dport = getattr(udp, "dport", None)
                    if (exp.get("udp_dport") is not None and udp_sport != exp["udp_dport"]) or \
                       (exp.get("udp_sport") is not None and udp_dport != exp["udp_sport"]):
                        continue
                # TCP-specific check (3whs)
                if proto == 6:
                    tcp = ether.get_layer("TCP")
                    if not tcp:
                        continue
                    tcp_sport = getattr(tcp, "sport", None)
                    tcp_dport = getattr(tcp, "dport", None)
                    if (exp.get("tcp_dport") is not None and tcp_sport != exp["tcp_dport"]) or \
                       (exp.get("tcp_sport") is not None and tcp_dport != exp["tcp_sport"]):
                        continue
                # ICMP: already filtered by proto+dst
                return ether
            except Exception:
                continue
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
    return sniff(interface=interface)