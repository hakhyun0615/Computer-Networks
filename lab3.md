# **Lab 3**



**Course:** Computer Networks (Fall 2025)
**Assignment:** Build a Scapy-like packet crafting library
**Student:**  Hak Hyun Kim, Michael Dean
**Date:** October 21, 2025



## **Table of Contents**

1. Project Overview
2. Environment & Assumptions
3. Design & Implementation
4. Packet I/O API (send, sendp, sr, sniff)
5. Experiments & Results (with capture guidance)
6. Discussion & Takeaways
7. Limitations & Future Work
8. Submission Artifacts & Checklist
9. References



------



## **1) Project Overview**

**Goal.** Implement a minimal Scapy-like stack that lets me construct packets as composable objects, serialize them to bytes, transmit them at Layer 2/3, and parse replies back into objects. The library supports:

- **Layers:** Ethernet (L2), IPv4 & ICMP (L3), UDP & TCP (L4), DNS (L7)
- **Operator overloading:** Ether()/IP()/ICMP() style stacking via /
- **I/O functions:** send, sendp, sr, sniff
- **Checksums:** one’s-complement, including TCP/UDP pseudo-header



**What “done” looks like.**

- ICMP echo with replies visible in Wireshark.
- DNS A-record query to 8.8.8.8 and parsing the IPv4 answer.
- TCP 3-way handshake to vibrantcloud.org:80 and an HTTP GET /index.html, with plaintext HTML returned.



------



## **2) Environment & Assumptions**

- **Host OS:** Ubuntu 20.04 LTS (class VM)
- **Python:** 3.10+ (standard library only)
- **Interface:** ens160
- **Local network:** 172.16.191.0/24 (VM NAT)
- **My IP / MAC (examples used in tests):** 172.16.191.128, 00:0c:29:6f:00:f1
- **Gateway IP/MAC (next hop):** 172.16.191.2, 00:50:56:fb:73:ea
- **Test endpoints:** Google DNS 8.8.8.8, vibrantcloud.org (173.201.179.249)
- **Privileges:** Root required for raw sockets & iptables rule.

Assumption: graders will run on Linux; send uses a raw IPv4 socket so the kernel will add L2 headers; sendp uses an AF_PACKET raw socket so I provide full Ethernet.



------



## **3) Design & Implementation**

### **3.1 Project Layout**

```
lab3/
├─ layers/
│  ├─ base.py      # Layer base class (+ `/` overloading, show())
│  ├─ ether.py     # Ethernet II
│  ├─ ip.py        # IPv4
│  ├─ icmp.py      # ICMP Echo
│  ├─ udp.py       # UDP (+ pseudo-header checksum)
│  ├─ tcp.py       # TCP (+ pseudo-header checksum)
│  └─ dns.py       # DNS query/parse (A record)
├─ utils/helpers.py # checksum, conversions (MAC/IP to bytes), encoders
├─ api.py           # send, sendp, sr, sniff
├─ ping_example.py  # ICMP demo
├─ dns_example.py   # DNS demo
└─ tcp_http_example.py # TCP 3WH + HTTP GET demo
```

### **3.2 Base Layer & Stacking**

- Every layer has payload and implements build() → bytes.
- The base Layer.__truediv__(other) chains payloads for lhs / rhs.
- When stacking IP below UDP/TCP, the operator injects src_ip/dst_ip into the L4 object (needed for the pseudo-header checksum).
- show(indent=0) prints a Scapy-like tree view (Ether → IP → …).

**Example (ICMP ping):**

```
pkt = Ether(src_mac=my_mac, dst_mac=gateway_mac) \
    / IP(src_ip=my_ip, dst_ip="8.8.8.8", ttl=64) \
    / ICMP(type=8, id=1, seq=1)
```

### **3.3 Serialization & Parsing**

- **Ethernet**: serializes dst/src/type (0x0800 for IPv4). On parse, inspects EtherType and forwards remainder to IP.
- **IPv4**: sets ihl=5, computes header checksum, sets total_len = 20 + payload_len. On parse, dispatches next protocol by proto (1=ICMP, 6=TCP, 17=UDP).
- **ICMP**: supports Echo request/reply (type 8/0), checksum over header+data (32-byte pad by default to match typical ping).
- **UDP/TCP**: compute checksum with pseudo-header: srcIP|dstIP|0x00|proto|length + L4header + data.
- **DNS**: encodes qname (label_length|label|...|0x00), qtype=A (1), qclass=IN (1). For responses, extracts A RDATA (4 bytes) from the answer section (handles the common single-answer case used here).

### **3.4 Checksums**

One’s-complement on 16-bit words with end-carry fold. For odd lengths, pad one zero byte during calculation (standard practice; stored checksum matches Wireshark validation).



------



## **4) Packet I/O API**

### **4.1** send(pkt)**

- Sends at **Layer 3** using socket(AF_INET, SOCK_RAW, IPPROTO_RAW).
- If pkt starts with Ether, it skips L2 and transmits **IP and above**; the kernel adds L2 headers and routes.

### **4.2** sendp(pkt, interface)**

- Sends at **Layer 2** using socket(AF_PACKET, SOCK_RAW) and bind((interface, 0)).
- Expects Ether at the root; caller must set src_mac and **next-hop** dst_mac.

### **4.3** sr(pkt, timeout=2)**

- Transmit like send (L3) and then open a **promiscuous** AF_PACKET socket to receive one matching reply (timeout guarded).
- Returns a parsed Ether(...) object.
- In practice, the reply is found by correlating IPs/ports/ICMP id+seq.

### **4.4** sniff(timeout=5)**

- AF_PACKET socket with htons(0x0003) (ETH_P_ALL), one packet only.
- Returns Ether(...) parsed from raw bytes.



------



## **5) Experiments & Results**

> Note: All packet fields validated in Wireshark (checksums OK; expected flags/sequence numbers present). Below I include **what to capture** and **how I verified**. The six screenshot labels below must remain in Korean (as requested).



### **5.1 ICMP Echo (Ping) — three ways**

**Setup snippet:**

```
eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
ip  = IP(src_ip=my_ip, dst_ip="8.8.8.8", ttl=64)
icmp = ICMP(type=8, id=1, seq=1)
pkt = eth / ip / icmp
```



#### **5.1.1 Using** send() (Layer 3)**

- Command prints a brief “sent L3” line.
- In Wireshark, filter icmp and ip.addr == 8.8.8.8.
- I observe Echo Request (me → 8.8.8.8) and Echo Reply (8.8.8.8 → me).
- L2 addresses are provided by the OS (gateway MAC as next hop).



![image-20251021044247364](/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251021044247364.png)



#### **5.1.2 Using** sendp() **(Layer 2)**

- I bind to ens160 and transmit **Ether/IP/ICMP** with explicit MACs.
- Filter as above; both request and reply show.
- This confirms manual L2 works (and MAC spoofing experiments still transmit, though replies follow the actual source MAC/ARP state).

![image-20251021044228523](/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251021044228523.png)



#### **5.1.3 Using** sr() (send & receive)**

- The function returns the parsed reply and I print it via show():

```
### Ether ###
  dst_mac: 00:0c:29:6f:00:f1
  src_mac: 00:50:56:fb:73:ea
  type: 0x0800
  ### IP ###
    ttl: 128
    proto: 1
    src_ip: 8.8.8.8
    dst_ip: 172.16.191.128
  ### ICMP ###
    type: 0
    code: 0
    id: 1
    seq: 1
```

![image-20251021044205697](/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251021044205697.png)



### **5.2 DNS A-record Query to 8.8.8.8**

**Packet:** Ether / IP(dst=8.8.8.8) / UDP(sport=12345, dport=53) / DNS(qname="vibrantcloud.org", qtype=A)

- sr() returns a UDP/DNS reply with a single A answer: 173.201.179.249.
- I parse the last 4-byte RDATA into dotted-quad.

**Wireshark filter:** dns and ip.addr == 8.8.8.8

- Verify: matching Transaction ID, Standard query → Standard query response, Answers: 1, A record contains 173.201.179.249.

![image-20251021045938833](/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251021045938833.png)



### **5.3 TCP Three-Way Handshake (port 80)**

To prevent the kernel from RST’ing my userland handshake, I temporarily drop outbound RST:

```
import subprocess
subprocess.run([
  'sudo','iptables','-A','OUTPUT','-p','tcp','-m','tcp',
  '--tcp-flags','RST','RST','-j','DROP'
], check=True)
```

**SYN:** Ether/IP(dst=173.201.179.249)/TCP(dport=80, flags=SYN, seq=x)

**Expect:** server replies SYN,ACK with ack = x+1, seq = y.

**ACK:** I respond with ACK (seq = x+1, ack = y+1).

**Wireshark filter:** tcp and ip.addr == 173.201.179.249 and tcp.port == 80

- I see the three packets in order with correct seq/ack evolution.

![image-20251021050254646](/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251021050254646.png)

After the HTTP exchange (next section), I remove the rule:

```
sudo iptables -D OUTPUT -p tcp --tcp-flags RST RST -j DROP
```



### **5.4 HTTP GET over the established TCP flow**

**Request payload (as TCP data):**

```
GET /index.html HTTP/1.1\r\n
Host: vibrantcloud.org\r\n
Connection: close\r\n
\r\n
```

**Packet:** Ether/IP/TCP(flags=PSH|ACK, …, data=http_request_bytes)

- The reply arrives as one or more PSH,ACK segments. I concatenate TCP payloads and UTF-8 decode (ignore errors) to print the HTML.

**Wireshark filter:** http or (tcp.port == 80 and tcp.len > 0)

- Verify 200 OK, Content-Type: text/html, and visible HTML body.

![image-20251021050338579](/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251021050338579.png)



------



## **6) Discussion & Takeaways**

- **Encapsulation in practice.** The / operator made it natural to layer headers and pass serialization down the chain (Ether.build() → IP.build() → …).
- **Checksums matter.** Without correct pseudo-header checksums for UDP/TCP, remote hosts drop packets silently—Wireshark validation was essential.
- **send vs sendp.** Layer-3 send is convenient (kernel fills L2), while sendp is necessary when I want explicit MAC control (e.g., gateway next-hop).
- **Userland TCP is brittle.** The Linux RST issue is non-obvious at first; the iptables workaround is mandatory for clean 3WH/HTTP.
- **Parsing flow.** Starting from Ether, each constructor slices bytes for its header and instantiates the appropriate next-layer object based on EtherType/Protocol/Ports/Type.

