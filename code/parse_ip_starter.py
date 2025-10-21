import struct

''' 
    Given a series of bytes from an IP layer packet (containing a TCP payload)
        Parse the bytes into their IP fields

	Author: Tim Pierson, Dartmouth CS60, Fall 2025
            Assisted by Microsoft Copilot
	
	run: python3 parse_ip_starter.py
'''

def get_bits(byte, start_bit, end_bit):
    """
    Extracts a range of bits from a byte.

    Args:
        byte (int): The byte from which to extract bits.
        start_bit (int): The starting bit position (inclusive, 0-indexed from LSB).
        end_bit (int): The ending bit position (exclusive, 0-indexed from LSB).

    Returns:
        int: The integer value represented by the extracted bits.
    """
    num_bits = end_bit - start_bit
    mask = (1 << num_bits) - 1  # Create a mask with 'num_bits' ones
    shifted_byte = byte >> start_bit  # Shift the desired bits to the rightmost position
    extracted_value = shifted_byte & mask  # Apply the mask to isolate the bits
    return extracted_value

def parse_ip_tcp_packet(packet_bytes):
   #TODO: extract version, ip header length, protocol (TCP, UDP), TTL, source and destination IP address from header bytes

    print(f"IP Version: {version}")
    print(f"IHL (Header Length): {ip_header_length} bytes")
    print(f"Protocol: {protocol}")
    print(f"TTL: {ttl}")
    print(f"Source IP: {src_ip}")
    print(f"Destination IP: {dest_ip}")


if __name__ == "__main__":
    ip_header = b"\x45\x00\x00\x28\xf8\xd1\x40\x00\x2e\x06\x27\xb0\x80\x77\xf5\x0c\x0a\x87\xac\x43" #taken random packet from book's website
    parse_ip_tcp_packet(ip_header)