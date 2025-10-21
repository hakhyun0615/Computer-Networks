#!/usr/bin/env python3
"""
Test TCP checksum calculation by comparing with known good values
"""

import struct
from utils import checksum_ones_complement, ip_to_bytes

def test_tcp_checksum():
    """Test TCP checksum with known values"""
    
    # Test parameters
    src_ip = "172.16.191.128"
    dst_ip = "173.201.179.249"
    sport = 50607
    dport = 80
    seq = 3692667264
    ack = 0
    flags = 0x02  # SYN
    window = 8192
    
    # Build TCP header without checksum
    offset_flags = (5 << 4) | 0  # 5 words = 20 bytes, no flags in offset
    header_wo_csum = struct.pack(
        "!HHLLBBHHH",
        sport,     # source port
        dport,     # dest port
        seq,       # sequence
        ack,       # acknowledgment
        offset_flags,  # offset + reserved
        flags,     # flags
        window,    # window
        0,         # checksum (0 for now)
        0          # urgent pointer
    )
    
    data = b""  # SYN has no data
    
    # Build pseudo-header
    pseudo = struct.pack(
        "!4s4sBBH",
        ip_to_bytes(src_ip),
        ip_to_bytes(dst_ip),
        0,         # zero
        6,         # TCP protocol
        len(header_wo_csum) + len(data)  # TCP length
    )
    
    print("="*60)
    print("TCP Checksum Test")
    print("="*60)
    print(f"Source IP: {src_ip}")
    print(f"Dest IP: {dst_ip}")
    print(f"Source Port: {sport}")
    print(f"Dest Port: {dport}")
    print(f"Seq: {seq}")
    print(f"Ack: {ack}")
    print(f"Flags: {hex(flags)}")
    print(f"Window: {window}")
    print()
    
    print("Pseudo-header (12 bytes):")
    print(" ".join(f"{b:02x}" for b in pseudo))
    print()
    
    print("TCP Header without checksum (20 bytes):")
    print(" ".join(f"{b:02x}" for b in header_wo_csum))
    print()
    
    # Calculate checksum
    full_packet = pseudo + header_wo_csum + data
    csum = checksum_ones_complement(full_packet)
    
    print(f"Calculated Checksum: {hex(csum)} ({csum})")
    print()
    
    # Build final header with checksum
    final_header = struct.pack(
        "!HHLLBBHHH",
        sport,
        dport,
        seq,
        ack,
        offset_flags,
        flags,
        window,
        csum,  # checksum
        0
    )
    
    print("Final TCP Header with checksum (20 bytes):")
    print(" ".join(f"{b:02x}" for b in final_header))
    print()
    
    # Verify checksum
    verify = checksum_ones_complement(pseudo + final_header + data)
    print(f"Verification (should be 0): {hex(verify)}")
    
    if verify == 0:
        print("✓ Checksum is CORRECT!")
    else:
        print("✗ Checksum is WRONG!")
    
    return csum

if __name__ == "__main__":
    test_tcp_checksum()
