#!/usr/bin/env python3
"""
Individual test runner for easier Wireshark capture
Run each test separately for clean screenshots
"""

import sys
import time
from api import send, sendp, sr
from layers import ICMP, IP, TCP, UDP, DNS, Ether

# Network configuration
my_ip = "172.16.191.128"
my_mac = "00:0c:29:6f:00:f1"
gateway_mac = "00:50:56:fb:73:ea"
interface = "ens160"

def test_icmp():
    """Test ICMP ping - all three methods"""
    print("="*60)
    print("ICMP PING TEST")
    print("="*60)
    print("Wireshark filter: icmp and ip.addr == 8.8.8.8")
    print()
    
    # Test 1: send()
    print("[1/3] Testing send() - Layer 3")
    eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
    ip = IP(src_ip=my_ip, dst_ip="8.8.8.8", ttl=64)
    icmp = ICMP(type=8, code=0, id=1, seq=1, data=b"\x00" * 32)
    pkt = eth / ip / icmp
    send(pkt)
    print("✓ Sent ICMP via send()")
    time.sleep(1)
    
    # Test 2: sendp()
    print("\n[2/3] Testing sendp() - Layer 2")
    icmp2 = ICMP(type=8, code=0, id=2, seq=1, data=b"\x00" * 32)
    pkt2 = Ether(src_mac=my_mac, dst_mac=gateway_mac) / IP(src_ip=my_ip, dst_ip="8.8.8.8", ttl=64) / icmp2
    sendp(pkt2, interface)
    print("✓ Sent ICMP via sendp()")
    time.sleep(1)
    
    # Test 3: sr()
    print("\n[3/3] Testing sr() - Send and Receive")
    icmp3 = ICMP(type=8, code=0, id=3, seq=1, data=b"\x00" * 32)
    pkt3 = Ether(src_mac=my_mac, dst_mac=gateway_mac) / IP(src_ip=my_ip, dst_ip="8.8.8.8", ttl=64) / icmp3
    reply = sr(pkt3, interface=interface, timeout=3.0)
    print("✓ Received reply:")
    reply.show()
    
    print("\n✓ ICMP test complete!")
    print("스크린샷 1, 2, 3: ICMP packets with id=1, id=2, id=3")

def test_dns():
    """Test DNS query"""
    print("\n" + "="*60)
    print("DNS QUERY TEST")
    print("="*60)
    print("Wireshark filter: dns and ip.addr == 8.8.8.8")
    print()
    
    domain = "vibrantcloud.org"
    dns_server = "8.8.8.8"
    
    eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
    ip = IP(src_ip=my_ip, dst_ip=dns_server, ttl=64)
    udp = UDP(sport=12345, dport=53)
    dns = DNS(qname=domain, qtype=1, qclass=1)
    
    pkt = eth / ip / udp / dns
    
    print(f"Querying {domain} at {dns_server}...")
    reply = sr(pkt, interface=interface, timeout=3.0)
    
    print("\n✓ Received DNS reply:")
    reply.show()
    
    dns_reply = reply.get_layer("DNS")
    if dns_reply and dns_reply.addr:
        print(f"\n✓ {domain} → {dns_reply.addr}")
    
    print("\n✓ DNS test complete!")
    print("스크린샷 4: DNS query and response")

def test_tcp_http():
    """Test TCP handshake and HTTP GET"""
    import random
    import subprocess
    
    print("\n" + "="*60)
    print("TCP + HTTP TEST")
    print("="*60)
    print("Wireshark filter: tcp and ip.addr == 173.201.179.249 and tcp.port == 80")
    print()
    
    dst_ip = "173.201.179.249"  # vibrantcloud.org
    dst_port = 80
    src_port = random.randint(49152, 65535)
    seq_num = random.randint(0, 2**32 - 1)
    
    # Add firewall rule
    print("Adding firewall rule...")
    subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'tcp',
                    '--tcp-flags', 'RST', 'RST', '-j', 'DROP'],
                   check=True, capture_output=True)
    
    try:
        eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
        ip = IP(src_ip=my_ip, dst_ip=dst_ip, ttl=64)
        
        # Step 1: SYN
        print(f"\n[1/4] Sending SYN to {dst_ip}:{dst_port}...")
        tcp_syn = TCP(sport=src_port, dport=dst_port, seq=seq_num, ack=0, flags=0x02)
        pkt_syn = eth / ip / tcp_syn
        
        reply_syn_ack = sr(pkt_syn, interface=interface, timeout=3.0)
        print("✓ Received SYN-ACK:")
        reply_syn_ack.show()
        
        tcp_reply = reply_syn_ack.get_layer("TCP")
        
        # Step 2: ACK
        print("\n[2/4] Sending ACK...")
        seq_num += 1
        ack_num = tcp_reply.seq + 1
        tcp_ack = TCP(sport=src_port, dport=dst_port, seq=seq_num, ack=ack_num, flags=0x10)
        pkt_ack = eth / ip / tcp_ack
        send(pkt_ack)
        print("✓ Connection established!")
        time.sleep(0.5)
        
        # Step 3: HTTP GET
        print("\n[3/4] Sending HTTP GET...")
        http_request = f"GET /index.html HTTP/1.1\r\nHost: vibrantcloud.org\r\nConnection: close\r\n\r\n".encode()
        tcp_http = TCP(sport=src_port, dport=dst_port, seq=seq_num, ack=ack_num,
                       flags=0x18, data=http_request)
        pkt_http = eth / ip / tcp_http
        
        reply_http = sr(pkt_http, interface=interface, timeout=3.0)
        print("✓ Received HTTP response:")
        reply_http.show()
        
        # Step 4: Extract HTML
        print("\n[4/4] Extracting HTML...")
        tcp_data = reply_http.get_layer("TCP")
        if tcp_data and tcp_data.data:
            response_text = tcp_data.data.decode('utf-8', errors='ignore')
            print("\n" + "="*60)
            print("HTTP RESPONSE:")
            print("="*60)
            print(response_text[:500])  # First 500 chars
            print("✓ HTTP GET complete!")
        else:
            print("⚠ No data in first response (may need to wait for next packet)")
        
        print("\n✓ TCP/HTTP test complete!")
        print("스크린샷 5: TCP 3-way handshake (SYN, SYN-ACK, ACK)")
        print("스크린샷 6: HTTP GET request and response")
        
    finally:
        # Remove firewall rule
        print("\nRemoving firewall rule...")
        subprocess.run(['sudo', 'iptables', '-D', 'OUTPUT', '-p', 'tcp',
                        '--tcp-flags', 'RST', 'RST', '-j', 'DROP'],
                       check=True, capture_output=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: sudo python3 test_individual.py [icmp|dns|tcp|all]")
        print()
        print("Examples:")
        print("  sudo python3 test_individual.py icmp    # Test ICMP only")
        print("  sudo python3 test_individual.py dns     # Test DNS only")
        print("  sudo python3 test_individual.py tcp     # Test TCP+HTTP only")
        print("  sudo python3 test_individual.py all     # Test all")
        sys.exit(1)
    
    test = sys.argv[1].lower()
    
    print("="*60)
    print("Lab 3: Individual Test Runner")
    print("="*60)
    print(f"Test: {test}")
    print(f"Network: {my_ip} ({my_mac})")
    print("="*60)
    print()
    print("⚠ Make sure Wireshark is running and capturing!")
    print()
    time.sleep(2)
    
    if test == "icmp" or test == "all":
        test_icmp()
    
    if test == "dns" or test == "all":
        if test == "all":
            time.sleep(3)  # Wait between tests
        test_dns()
    
    if test == "tcp" or test == "all":
        if test == "all":
            time.sleep(3)  # Wait between tests
        test_tcp_http()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE!")
    print("="*60)
    print("\nNow capture screenshots from Wireshark:")
    print("1. icmp and ip.addr == 8.8.8.8 (스크린샷 1, 2, 3)")
    print("2. dns and ip.addr == 8.8.8.8 (스크린샷 4)")
    print("3. tcp and ip.addr == 173.201.179.249 (스크린샷 5, 6)")

if __name__ == "__main__":
    main()
