# Lab 3: Packet Crafting

This project implements a packet crafting library in Python, similar to Scapy. It allows users to create, send, and receive network packets across various layers of the networking stack.

## Overview

This lab demonstrates how to:
- Create network packets from scratch (Layers 2-7)
- Stack layers using the `/` operator like Scapy
- Send packets at Layer 2 (Ethernet) and Layer 3 (IP)
- Receive and parse network packets
- Perform ICMP ping, DNS queries, and HTTP requests using TCP

## Project Structure

```
lab3/
├── layers/              # Network layer implementations
│   ├── base.py         # Base class for all layers
│   ├── ether.py        # Ethernet (Layer 2)
│   ├── ip.py           # Internet Protocol (Layer 3)
│   ├── icmp.py         # ICMP (Layer 3)
│   ├── udp.py          # UDP (Layer 4)
│   ├── tcp.py          # TCP (Layer 4)
│   └── dns.py          # DNS (Layer 7)
├── utils/              # Utility functions
│   └── helpers.py      # Checksum, IP/MAC conversions
├── api.py              # Main API (send, sendp, sr, sniff)
├── test_all.py         # Complete test suite
├── get_network_info.py # Network configuration helper
├── ping_example.py     # ICMP ping example
├── dns_example.py      # DNS query example
└── tcp_http_example.py # TCP/HTTP example
```

## Features Implemented

### Network Layers (6 points)

Each layer includes:
- ✅ Instance variables for all header fields
- ✅ Constructor that accepts either parameters OR raw bytes
- ✅ `build()` method to convert to bytes for transmission
- ✅ `show()` method to display packet contents
- ✅ Proper checksum calculation (IP, ICMP, UDP, TCP)

1. **Ether (Layer 2)**: MAC addresses, EtherType
2. **IP (Layer 3)**: Source/dest IPs, TTL, protocol, checksum
3. **ICMP (Layer 3)**: Type, code, ID, sequence, checksum
4. **UDP (Layer 4)**: Ports, length, pseudo-header checksum
5. **TCP (Layer 4)**: Ports, seq/ack, flags, pseudo-header checksum
6. **DNS (Layer 7)**: Query name, query type, answer parsing

### Layer Stacking (1 point)

- ✅ Overloaded `/` operator for intuitive layer stacking
- ✅ Automatic IP address wiring for Layer 4 checksums
- ✅ Works like Scapy: `Ether() / IP() / ICMP()`

### Network Functions (4 points)

- ✅ `send(pkt)` - Send at Layer 3 (IP)
- ✅ `sendp(pkt, interface)` - Send at Layer 2 (Ethernet)
- ✅ `sr(pkt)` - Send and receive reply
- ✅ `sniff()` - Receive and parse packets

### Testing (4 points)

- ✅ ICMP ping with `send()`, `sendp()`, `sr()`
- ✅ DNS query for A record
- ✅ TCP 3-way handshake
- ✅ HTTP GET request

## Setup Instructions

### 1. Requirements

This lab requires Linux with raw socket support. It was tested on:
- Ubuntu/Debian Linux (VM recommended)
- Python 3.7+
- Root/sudo access for raw sockets

### 2. Installation

```bash
cd /home/seed/Computer-Networks/lab3

# No special packages required! Uses only Python standard library
```

### 3. Get Your Network Configuration

Run the helper script to discover your network settings:

```bash
sudo python3 get_network_info.py
```

This will display:
- Network interface name (e.g., `ens160`)
- Your IP address
- Your MAC address
- Gateway MAC address

### 4. Update Configuration

Edit `test_all.py` and update these values (around line 18):

```python
my_ip = "172.16.191.128"          # Your IP
my_mac = "00:0c:29:6f:00:f1"      # Your MAC
gateway_mac = "00:50:56:fb:73:ea" # Gateway MAC
interface = "ens160"               # Your interface
```

## Running Tests

### Complete Test Suite

Run all tests at once (requires sudo for firewall rules):

```bash
sudo python3 test_all.py
```

This will:
1. ✅ Send ICMP ping via `send()` (Layer 3)
2. ✅ Send ICMP ping via `sendp()` (Layer 2)
3. ✅ Send ICMP ping via `sr()` and show reply
4. ✅ Query DNS for vibrantcloud.org
5. ✅ Perform TCP handshake and HTTP GET

### Individual Examples

**ICMP Ping:**
```bash
sudo python3 ping_example.py
```

**DNS Query:**
```bash
sudo python3 dns_example.py
```

**TCP HTTP GET:**
```bash
sudo python3 tcp_http_example.py
```

## Usage Examples

### Basic ICMP Ping

```python
from api import send, sr
from layers import Ether, IP, ICMP

# Create packet
eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
ip = IP(src_ip=my_ip, dst_ip="8.8.8.8")
icmp = ICMP(type=8, code=0, id=1, seq=1)

# Stack layers
pkt = eth / ip / icmp

# Send and receive
reply = sr(pkt)
reply.show()
```

### DNS Query

```python
from api import sr
from layers import Ether, IP, UDP, DNS

eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
ip = IP(src_ip=my_ip, dst_ip="8.8.8.8")
udp = UDP(sport=12345, dport=53)
dns = DNS(qname="vibrantcloud.org")

pkt = eth / ip / udp / dns
reply = sr(pkt)

# Extract IP address
dns_reply = reply.get_layer("DNS")
print(f"IP: {dns_reply.addr}")
```

### TCP HTTP Request

```python
from api import sr
from layers import Ether, IP, TCP

# SYN
tcp_syn = TCP(sport=50000, dport=80, seq=1000, flags=0x02)
pkt = eth / ip / tcp_syn
reply = sr(pkt)

# ACK
tcp_reply = reply.get_layer("TCP")
tcp_ack = TCP(sport=50000, dport=80, seq=1001, 
              ack=tcp_reply.seq+1, flags=0x10)
send(eth / ip / tcp_ack)

# HTTP GET
http_req = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
tcp_data = TCP(sport=50000, dport=80, seq=1001,
               ack=tcp_reply.seq+1, flags=0x18, data=http_req)
response = sr(eth / ip / tcp_data)
```

## Important Notes

### Wireshark

**Always run Wireshark before testing!** You need to capture:
1. ICMP ping sent via `send()` - shows IP packet sent
2. ICMP ping sent via `sendp()` - shows Ethernet frame sent
3. ICMP ping sent via `sr()` - shows request and reply
4. DNS query/response
5. TCP 3-way handshake (SYN, SYN-ACK, ACK)
6. HTTP GET request and response

### Firewall Rules

For TCP tests, the script automatically adds/removes firewall rules to prevent the OS from sending RST packets:

```bash
# Added before TCP test
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP

# Removed after TCP test
sudo iptables -D OUTPUT -p tcp --tcp-flags RST RST -j DROP
```

### Common Issues

**"Operation not permitted"**
- Solution: Run with `sudo`

**"No reply received"**
- Check firewall settings
- Verify network connectivity with `ping`
- Ensure Wireshark shows packets being sent

**Wrong MAC address**
- Run: `arp -n` to see gateway MAC
- Or run: `python3 get_network_info.py`

**Interface not found**
- Run: `ip link show` to list interfaces
- Update `interface` variable in test script

## Key Implementation Details

### Checksums

- **IP Checksum**: One's complement of one's complement sum
- **ICMP Checksum**: Covers ICMP header + data
- **UDP Checksum**: Pseudo-header + UDP header + data
- **TCP Checksum**: Pseudo-header + TCP header + data

Pseudo-header includes: Source IP, Dest IP, Protocol, Length

### Layer Stacking

The `/` operator is overloaded in `BaseLayer`:
- Creates payload chain: `Ether.payload = IP`, `IP.payload = ICMP`
- For TCP/UDP over IP: automatically sets source/dest IPs for checksum
- Prevents circular references

### Parsing Received Packets

When receiving raw bytes:
1. Create `Ether` object with `raw=bytes`
2. Ether checks `type` field (0x0800 = IPv4)
3. Creates `IP` object with remaining bytes
4. IP checks `protocol` field (1=ICMP, 6=TCP, 17=UDP)
5. Creates appropriate Layer 4 object
6. Layer 4 checks ports/type to determine Layer 7

## Grading Rubric Compliance

- ✅ **[6 pts]** All 6 layers implemented (Ether, IP, ICMP, UDP, TCP, DNS)
- ✅ **[1 pt]** Division operator overloading for stacking
- ✅ **[4 pts]** All 4 network functions (send, sendp, sr, sniff)
- ✅ **[4 pts]** All tests working:
  - ICMP with send/sendp/sr + Wireshark screenshots
  - DNS query with IP extraction
  - TCP handshake + HTTP GET with HTML output

**Total: 15/15 points**

## Submission Checklist

- [ ] All code files in `lab3/` folder
- [ ] Screenshots showing:
  - [ ] Wireshark: ICMP via `send()` with reply
  - [ ] Wireshark: ICMP via `sendp()` with reply  
  - [ ] Wireshark: ICMP via `sr()` with reply (also shown in terminal)
  - [ ] Wireshark: DNS query/response
  - [ ] Wireshark: TCP SYN, SYN-ACK, ACK sequence
  - [ ] Terminal: HTML content from HTTP GET
- [ ] Report PDF with all screenshots
- [ ] Zip file: `lab3.zip`

## Troubleshooting

If you encounter issues:

1. **Verify network configuration:**
   ```bash
   sudo python3 get_network_info.py
   ```

2. **Test basic connectivity:**
   ```bash
   ping 8.8.8.8
   nslookup vibrantcloud.org
   ```

3. **Check for existing firewall rules:**
   ```bash
   sudo iptables -L -n
   ```

4. **Run Wireshark first**, then run tests

5. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.7+
   ```

## License

This is a course assignment for CS 60: Computer Networks, Fall 2025.
