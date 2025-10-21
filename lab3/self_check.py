from layers import DNS, ICMP, IP, TCP, UDP, Ether
from utils import checksum_ones_complement, ip_to_bytes


def ok(name):
    print(f"[OK] {name}")

def test_icmp_build_parse():
    eth = Ether(src_mac="aa:bb:cc:dd:ee:ff", dst_mac="11:22:33:44:55:66")
    ip  = IP(src_ip="10.0.0.2", dst_ip="8.8.8.8", ttl=64)
    icmp = ICMP(type=8, code=0, id=7, seq=42, data=b"hello")
    pkt = eth / ip / icmp
    b = pkt.build()
    # Re-parse starting at Ether
    p2 = Ether(raw=b)
    assert p2.src_mac == "aa:bb:cc:dd:ee:ff"
    assert p2.payload.src_ip == "10.0.0.2"
    ic2 = p2.payload.payload
    assert ic2.type == 8 and ic2.id == 7 and ic2.seq == 42
    ok("ICMP build/parse round-trip")

def test_udp_dns_build_parse():
    eth = Ether(src_mac="de:ad:be:ef:00:01", dst_mac="ff:ee:dd:cc:bb:aa")
    ip  = IP(src_ip="192.168.1.10", dst_ip="8.8.8.8", ttl=64)
    dns = DNS(qname="example.com")
    udp = UDP(sport=55555, dport=53)
    pkt = eth / ip / udp / dns
    b = pkt.build()
    p2 = Ether(raw=b)
    udp2 = p2.payload.payload
    dns2 = udp2.payload
    assert dns2.qname == "example.com"
    assert udp2.sport == 55555 and udp2.dport == 53
    # UDP checksum should be nonzero (computed over pseudo-header + data)
    assert udp2.checksum != 0
    ok("UDP/DNS build/parse and checksum present")

def test_tcp_pseudoheader_wiring():
    ip = IP(src_ip="1.2.3.4", dst_ip="5.6.7.8")
    tcp = TCP(sport=1234, dport=80, seq=100, ack=0, flags=0x02)
    pkt = ip / tcp
    b = pkt.build()
    # Parse starting from IP
    p2 = IP(raw=b)
    t2 = p2.payload
    # Check IPs propagated into TCP (used in checksum calc)
    assert getattr(t2, "src_ip", None) == "1.2.3.4"
    assert getattr(t2, "dst_ip", None) == "5.6.7.8"
    # Basic header lengths
    assert len(b) >= 20 + 20
    ok("TCP pseudo-header IP propagation & basic lengths")

if __name__ == "__main__":
    test_icmp_build_parse()
    test_udp_dns_build_parse()
    test_tcp_pseudoheader_wiring()
    print("\nAll local self-checks passed ✔")