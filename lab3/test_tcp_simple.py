#!/usr/bin/env python3
"""
Simple TCP SYN test - just send one SYN and see what happens
"""

import random
import time
from api import sr
from layers import Ether, IP, TCP

# Network config
my_ip = "172.16.191.128"
my_mac = "00:0c:29:6f:00:f1"
gateway_mac = "00:50:56:fb:73:ea"
target_ip = "173.201.179.249"  # vibrantcloud.org

# Random source port and seq
src_port = random.randint(49152, 65535)
seq_num = random.randint(0, 2**32 - 1)

print("="*60)
print("Simple TCP SYN Test")
print("="*60)
print(f"Target: {target_ip}:80")
print(f"Source Port: {src_port}")
print(f"Sequence Number: {seq_num}")
print()

# Build packet
eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
ip = IP(src_ip=my_ip, dst_ip=target_ip, ttl=64)
tcp = TCP(sport=src_port, dport=80, seq=seq_num, ack=0, flags=0x02, window=8192)

pkt = eth / ip / tcp

print("Packet to send:")
pkt.show()

# Build and inspect bytes
pkt_bytes = pkt.build()
print(f"\nTotal packet size: {len(pkt_bytes)} bytes")
print(f"Ethernet: {len(pkt_bytes[0:14])} bytes")
print(f"IP: {len(pkt_bytes[14:34])} bytes")
print(f"TCP: {len(pkt_bytes[34:])} bytes")

# Show TCP header in hex
tcp_header = pkt_bytes[34:]
print(f"\nTCP Header (hex):")
for i in range(0, len(tcp_header), 16):
    hex_str = ' '.join(f'{b:02x}' for b in tcp_header[i:i+16])
    print(f"  {i:04x}: {hex_str}")

# Extract checksum from built packet
tcp_checksum = (tcp_header[16] << 8) | tcp_header[17]
print(f"\nTCP Checksum in packet: 0x{tcp_checksum:04x}")

print("\nSending SYN...")
try:
    reply = sr(pkt, timeout=5.0)
    print("\n✓ Received reply:")
    reply.show()
    
    tcp_reply = reply.get_layer("TCP")
    if tcp_reply:
        if tcp_reply.flags == 0x12:  # SYN+ACK
            print("\n✓ SUCCESS: Received SYN+ACK")
            print(f"Server Seq: {tcp_reply.seq}")
            print(f"Server Ack: {tcp_reply.ack} (should be {seq_num + 1})")
            if tcp_reply.ack == seq_num + 1:
                print("✓ ACK number is CORRECT!")
            else:
                print("✗ ACK number is WRONG!")
        else:
            print(f"\n⚠ Received TCP with flags: 0x{tcp_reply.flags:02x}")
    else:
        print("\n⚠ No TCP layer in reply")
        
except TimeoutError:
    print("\n✗ No reply received (timeout)")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
