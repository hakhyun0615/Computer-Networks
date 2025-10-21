#!/usr/bin/env python3
"""
Complete test suite for Lab 3: Packet Crafting
Tests all required functionality:
- ICMP ping with send, sendp, and sr
- DNS query with UDP
- HTTP GET with TCP 3-way handshake
"""

import random
import subprocess
import time
from api import send, sendp, sr
from layers import DNS, ICMP, IP, TCP, UDP, Ether


def get_network_info():
    """Get network information for the current system."""
    print("=== Network Configuration ===")
    print("Please configure these values for your system:")
    print()
    
    # You can update these values for your VM
    my_ip = "172.16.191.128"  # Your VM IP
    my_mac = "00:0c:29:6f:00:f1"  # Your VM MAC
    gateway_mac = "00:50:56:fb:73:ea"  # Gateway MAC from 'arp' command
    interface = "ens160"  # Your network interface
    
    print(f"Interface: {interface}")
    print(f"My IP: {my_ip}")
    print(f"My MAC: {my_mac}")
    print(f"Gateway MAC: {gateway_mac}")
    print()
    
    return interface, my_ip, my_mac, gateway_mac


def test_icmp_send(my_ip, my_mac, gateway_mac):
    """Test 1: Send ICMP ping using send() at Layer 3"""
    print("\n" + "="*60)
    print("TEST 1: ICMP Ping with send() (Layer 3)")
    print("="*60)
    
    # Create packet starting from Ether (send will extract IP layer)
    eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
    ip = IP(src_ip=my_ip, dst_ip="8.8.8.8", ttl=64)
    icmp = ICMP(type=8, code=0, id=1, seq=1, data=b"\x00" * 32)
    
    pkt = eth / ip / icmp
    
    print("\nPacket to send:")
    pkt.show()
    print("\nSending via send() at Layer 3...")
    send(pkt)
    print("✓ Packet sent! Check Wireshark for transmission and reply.")
    time.sleep(2)


def test_icmp_sendp(my_ip, my_mac, gateway_mac, interface):
    """Test 2: Send ICMP ping using sendp() at Layer 2"""
    print("\n" + "="*60)
    print("TEST 2: ICMP Ping with sendp() (Layer 2)")
    print("="*60)
    
    eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
    ip = IP(src_ip=my_ip, dst_ip="8.8.8.8", ttl=64)
    icmp = ICMP(type=8, code=0, id=2, seq=1, data=b"\x00" * 32)
    
    pkt = eth / ip / icmp
    
    print("\nPacket to send:")
    pkt.show()
    print(f"\nSending via sendp() on {interface} at Layer 2...")
    sendp(pkt, interface)
    print("✓ Packet sent! Check Wireshark for transmission and reply.")
    time.sleep(2)


def test_icmp_sr(my_ip, my_mac, gateway_mac, interface):
    """Test 3: Send ICMP ping using sr() and receive reply"""
    print("\n" + "="*60)
    print("TEST 3: ICMP Ping with sr() (Send and Receive)")
    print("="*60)
    
    eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
    ip = IP(src_ip=my_ip, dst_ip="8.8.8.8", ttl=64)
    icmp = ICMP(type=8, code=0, id=3, seq=1, data=b"\x00" * 32)
    
    pkt = eth / ip / icmp
    
    print("\nPacket to send:")
    pkt.show()
    print(f"\nSending via sr() and waiting for reply...")
    
    try:
        reply = sr(pkt, interface=interface, timeout=5.0)
        print("\n✓ Received reply:")
        reply.show()
        
        # Verify it's an ICMP echo reply
        icmp_reply = reply.get_layer("ICMP")
        if icmp_reply and icmp_reply.type == 0:
            print("\n✓ SUCCESS: Received valid ICMP Echo Reply (type=0)")
        else:
            print("\n⚠ Warning: Reply is not an ICMP Echo Reply")
    except TimeoutError:
        print("\n✗ No reply received within timeout")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def test_dns_query(my_ip, my_mac, gateway_mac, interface):
    """Test 4: DNS query for vibrantcloud.org"""
    print("\n" + "="*60)
    print("TEST 4: DNS Query for vibrantcloud.org")
    print("="*60)
    
    domain = "vibrantcloud.org"
    dns_server = "8.8.8.8"
    
    eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
    ip = IP(src_ip=my_ip, dst_ip=dns_server, ttl=64)
    udp = UDP(sport=12345, dport=53)
    dns = DNS(qname=domain, qtype=1, qclass=1)  # A record query
    
    pkt = eth / ip / udp / dns
    
    print(f"\nQuerying DNS for {domain} at {dns_server}...")
    print("\nPacket to send:")
    pkt.show()
    
    try:
        reply = sr(pkt, interface=interface, timeout=5.0)
        print("\n✓ Received DNS reply:")
        reply.show()
        
        # Extract IP address from DNS response
        dns_reply = reply.get_layer("DNS")
        if dns_reply and dns_reply.addr:
            print(f"\n✓ SUCCESS: {domain} resolves to {dns_reply.addr}")
            return dns_reply.addr
        else:
            print("\n⚠ Warning: No A record found in DNS reply")
            # Fallback IP for vibrantcloud.org
            return "173.201.179.249"
    except TimeoutError:
        print("\n✗ No DNS reply received within timeout")
        return "173.201.179.249"  # Fallback
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return "173.201.179.249"  # Fallback


def setup_firewall():
    """Setup firewall to prevent OS from sending RST packets"""
    print("\nSetting up firewall rules to prevent RST packets...")
    try:
        command = ['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'tcp', '-m', 'tcp', 
                   '--tcp-flags', 'RST', 'RST', '-j', 'DROP']
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("✓ Firewall rule added")
        return True
    except Exception as e:
        print(f"✗ Failed to add firewall rule: {e}")
        print("  You may need to run this script with sudo")
        return False


def cleanup_firewall():
    """Remove firewall rule"""
    print("\nCleaning up firewall rules...")
    try:
        command = ['sudo', 'iptables', '-D', 'OUTPUT', '-p', 'tcp', '-m', 'tcp',
                   '--tcp-flags', 'RST', 'RST', '-j', 'DROP']
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("✓ Firewall rule removed")
    except Exception as e:
        print(f"⚠ Warning: Failed to remove firewall rule: {e}")


def test_tcp_http(my_ip, my_mac, gateway_mac, interface, dst_ip):
    """Test 5: TCP 3-way handshake and HTTP GET request"""
    print("\n" + "="*60)
    print("TEST 5: TCP 3-Way Handshake and HTTP GET")
    print("="*60)
    
    if not setup_firewall():
        print("⚠ Skipping TCP test due to firewall setup failure")
        return
    
    try:
        src_port = random.randint(49152, 65535)
        dst_port = 80
        seq_num = random.randint(0, 2**32 - 1)
        
        eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
        ip = IP(src_ip=my_ip, dst_ip=dst_ip, ttl=64)
        
        # Step 1: Send SYN
        print(f"\n[1/4] Sending SYN to {dst_ip}:80...")
        tcp_syn = TCP(sport=src_port, dport=dst_port, seq=seq_num, ack=0, flags=0x02)
        pkt_syn = eth / ip / tcp_syn
        pkt_syn.show()
        
        reply_syn_ack = sr(pkt_syn, interface=interface, timeout=5.0)
        print("\n✓ Received SYN-ACK:")
        reply_syn_ack.show()
        
        tcp_reply = reply_syn_ack.get_layer("TCP")
        if not tcp_reply:
            print("✗ No TCP layer in reply")
            return
        
        # Step 2: Send ACK
        print("\n[2/4] Sending ACK...")
        seq_num += 1
        ack_num = tcp_reply.seq + 1
        tcp_ack = TCP(sport=src_port, dport=dst_port, seq=seq_num, ack=ack_num, flags=0x10)
        pkt_ack = eth / ip / tcp_ack
        send(pkt_ack)
        print("✓ ACK sent, connection established!")
        time.sleep(0.5)
        
        # Step 3: Send HTTP GET request
        print("\n[3/4] Sending HTTP GET request...")
        http_request = f"GET /index.html HTTP/1.1\r\nHost: {dst_ip}\r\nConnection: close\r\n\r\n".encode()
        tcp_http = TCP(sport=src_port, dport=dst_port, seq=seq_num, ack=ack_num, 
                       flags=0x18, data=http_request)  # PSH+ACK
        pkt_http = eth / ip / tcp_http
        
        reply_http = sr(pkt_http, interface=interface, timeout=5.0)
        print("\n✓ Received HTTP response:")
        reply_http.show()
        
        # Step 4: Extract and display HTML
        print("\n[4/4] Extracting HTML content...")
        tcp_data = reply_http.get_layer("TCP")
        if tcp_data and tcp_data.data:
            try:
                response_text = tcp_data.data.decode('utf-8', errors='ignore')
                print("\n" + "="*60)
                print("HTTP RESPONSE:")
                print("="*60)
                print(response_text)
                
                # Extract just the HTML body if present
                if "\r\n\r\n" in response_text:
                    headers, body = response_text.split("\r\n\r\n", 1)
                    print("\n" + "="*60)
                    print("HTML BODY:")
                    print("="*60)
                    print(body)
                
                print("\n✓ SUCCESS: HTTP GET completed and HTML retrieved!")
            except Exception as e:
                print(f"✗ Error decoding response: {e}")
        else:
            print("⚠ No data in TCP response")
            
    except TimeoutError:
        print("\n✗ Timeout waiting for response")
    except Exception as e:
        print(f"\n✗ Error during TCP test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup_firewall()


def main():
    """Run all tests"""
    print("="*60)
    print("Lab 3: Packet Crafting - Complete Test Suite")
    print("="*60)
    
    # Get network configuration
    interface, my_ip, my_mac, gateway_mac = get_network_info()
    
    print("\n⚠ IMPORTANT NOTES:")
    print("1. Make sure to run Wireshark before starting tests")
    print("2. Tests 1 and 2 will send packets but not wait for replies")
    print("3. Test 3 will send and receive ICMP replies")
    print("4. Test 4 will perform DNS lookup")
    print("5. Test 5 requires sudo for firewall rules")
    print()
    print("Starting tests in 2 seconds...")
    time.sleep(2)
    
    # Run ICMP tests
    test_icmp_send(my_ip, my_mac, gateway_mac)
    time.sleep(1)  # Wait between tests
    
    test_icmp_sendp(my_ip, my_mac, gateway_mac, interface)
    time.sleep(1)  # Wait between tests
    
    test_icmp_sr(my_ip, my_mac, gateway_mac, interface)
    time.sleep(2)  # Wait before DNS
    
    # Run DNS test and get IP
    vibrant_ip = test_dns_query(my_ip, my_mac, gateway_mac, interface)
    time.sleep(2)  # Wait before TCP
    
    # Run TCP/HTTP test
    if vibrant_ip:
        test_tcp_http(my_ip, my_mac, gateway_mac, interface, vibrant_ip)
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)
    print("\nPlease capture screenshots from Wireshark showing:")
    print("1. ICMP ping sent via send() with reply")
    print("2. ICMP ping sent via sendp() with reply")
    print("3. ICMP ping sent via sr() with reply displayed")
    print("4. DNS query and response with IP address")
    print("5. TCP 3-way handshake and HTTP GET/response")


if __name__ == "__main__":
    main()
