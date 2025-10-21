#!/usr/bin/env python3
"""
Quick verification that all modules work correctly
Run this to ensure everything is set up properly
"""

import sys

print("="*60)
print("Lab 3: Quick Verification Test")
print("="*60)
print()

# Test 1: Import all layers
print("[1/5] Testing layer imports...")
try:
    from layers import Ether, IP, ICMP, UDP, TCP, DNS
    print("      ✅ All layers imported successfully")
except ImportError as e:
    print(f"      ❌ Failed to import layers: {e}")
    sys.exit(1)

# Test 2: Import API
print("[2/5] Testing API imports...")
try:
    from api import send, sendp, sr, sniff
    print("      ✅ All API functions imported successfully")
except ImportError as e:
    print(f"      ❌ Failed to import API: {e}")
    sys.exit(1)

# Test 3: Import utilities
print("[3/5] Testing utility imports...")
try:
    from utils import checksum_ones_complement, ip_to_bytes, mac_to_bytes
    print("      ✅ All utilities imported successfully")
except ImportError as e:
    print(f"      ❌ Failed to import utilities: {e}")
    sys.exit(1)

# Test 4: Create a simple packet
print("[4/5] Testing packet creation...")
try:
    eth = Ether(src_mac="aa:bb:cc:dd:ee:ff", dst_mac="11:22:33:44:55:66")
    ip = IP(src_ip="192.168.1.1", dst_ip="8.8.8.8")
    icmp = ICMP(type=8, code=0, id=1, seq=1)
    pkt = eth / ip / icmp
    print("      ✅ Packet created successfully")
except Exception as e:
    print(f"      ❌ Failed to create packet: {e}")
    sys.exit(1)

# Test 5: Build packet bytes
print("[5/5] Testing packet building...")
try:
    packet_bytes = pkt.build()
    print(f"      ✅ Packet built successfully ({len(packet_bytes)} bytes)")
except Exception as e:
    print(f"      ❌ Failed to build packet: {e}")
    sys.exit(1)

# Show packet
print()
print("="*60)
print("Sample Packet:")
print("="*60)
pkt.show()

print()
print("="*60)
print("✅ All verification tests passed!")
print("="*60)
print()
print("Next steps:")
print("1. Configure network settings:")
print("   sudo python3 get_network_info.py")
print()
print("2. Update test_all.py with your network configuration")
print()
print("3. Run debug helper:")
print("   sudo python3 debug_helper.py")
print()
print("4. Start Wireshark and run tests:")
print("   sudo python3 test_all.py")
print()
