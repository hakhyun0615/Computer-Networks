## TCP/IP Stack

<img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251004223945910.png" style="width:20%; float:left;" /> <img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251004224037763.png" 
     style="width:55%; float:left; margin-left:40px;"/>



















----

## Pysical Layer (Layer 1)

Send Frames to another host

Converts into Bits (0/1) and send to Link/MAC layer

- Fiber (Light)

  - Single-mode

  - Multi-mode
- Ethernet (Wires)

  - UTP/STP

  - Cat5e ~ Cat8

  - RJ-45

    - Straight

    - Crossover

  - Tapping

    - Throwing star

    - Hubs
- Radio Wave
  - Wi-Fi

## Link/MAC Layer (Layer 2)

Tacks on **Source, Destination MAC** / Strips off MAC to check if it's for me

Moves Frames inside a single LAN using **MAC** addresses

- **Switch**: Connects devices within a network
  - Remember which MAC address (unique device address) is connected to which pysical port
  - When a frame arrives, looks at destination MAC Address and forwards it only to the corresponding port

## Network/IP Layer (Layer 3)

Tacks on **Source, Destination IP** / Strips off IP to check if it's for me

Moves Packets between different LANs using **IP** addresses

- Autonomous System

  - Contains Routers

  - OSPF

    - Connet Routers within Autonomous System by Flooding

  - BGP

    - Connect Autonomous Systems

      

- **Router**: Connects networks

  - NAT

    - Internal devices on a private network share router's outside IP address, assigned by ISP, to access the internet

  - Forwarding

    - Move packets from Input Port to Output Port using table

  - Routing

    Select path from Source IP to Destination IP

    - Autonomous System

      - OSPF

        1. Each router creates its own LSA
        2. Routers flood these LSAs throughout the network
        3. Every router builds an identical Link-State Database
        4. Each router runs Dijkstra on the LSDB to compute the shortest paths
        5. From the SPT, each router constructs its own Forwarding Table

      - BGP

        - Connect Autonomous Systems

          <img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251020141250149.png" alt="image-20251020141250149" style="zoom:50%; float:left;" />

    


## Transport Layer (Layer 4)

Tacks on **Headers (Source, Destination Port)** / Grab the port 

Identify applications/processes/sockets the data should go to using ports by multiplexing/demultiplexing

- Packet

  - Unit of data including headers and payload

- Socket

  - Channel for applications to send/receive data

- Port

  - Just an integer between 0 ~ 65000 for each applications

  - De-Multiplex

    - UDP: Use only destination port number
    - TCP: Use 4-tuple (source, destination IP addresses/Port numbers)

    <img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251013175640341.png" alt="image-20251013175640341" style="zoom:45%; float:left;" />

  - Multiplex

    <img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251013175804377.png" alt="image-20251013175804377" style="zoom:45%; float:left;" />

- Client side (Source)

  - Each port of applications within a devices is ramdonly chosen by OS

- Server side (Destination)
  <img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251004235748946.png" alt="image-20251004235748946" style="zoom:33%; float:left;" />














Exchange data between applications

- TCP
  
  - EX) HTTP Request
  
  - 20 bytes Header
  
  - Handshake (SYN → SYN+ACK → ACK) O
  
    - One port = Multiple sockets (Listening socket/Main socket + Client sockets)
    - Able to communicate with clients with different sockets in one port
  
  - Each client connection blocks the server during communication, so multi-threading is used to handle multiple clients concurrently
  
    - Main thread keeps accepting new clients
    - Each thread manages one client connection independently
  
  - Missing packets are resent (Tell me if you're missing any, I'll resent any of them that are missing)
  
  - Stop-and-Wait RDT
  
    - Make sure because UDP just deliver packets (Unreliable)
      - No "bit flips" → Checksum
      - No "drops" → Timer
      - "In order" → Sequence Number (0 → 1 → 0 → 1 → 0 → 1 …) in Data (Sender) and ACK (Receiver)
      - "Flow control" → Receive Window
  
    - ACK/NAK from receiver whether data was received correctly
  
      - ACK → Wait for the next bit of data
      - NAK → Resend packet
  
      <img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251013232218711.png" alt="image-20251013232218711" style="zoom:45%; float: left;" />
  
  - GBN & SR RDT
  
    - Allow multiple packets to be in flight (sliding window) 
  
    - Sender doesn’t need to wait for each ACK before sending the next packet
  
    - More efficient than Stop-and-Wait RDT
  
      <img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251013225702574.png" alt="image-20251013225702574" style="zoom:40%; float:left;" />
  
- UDP
  - EX) DNS Request
    - Translate human-readable hostname into machine-readable IP addresses 
  - 8 bytes Header
  - Handshake X (No connection)
    - One port = One socket
    - Able to communicate with clients with one socket
  - Missing packets are not resent (Hope for the best)
  - (Twice) Smaller Header
  - Faster

## Application Layer (Layer 7)

Tacks on **Data** / Send messages between applications



--------

## ARP (Layer 2.5)

Fint a MAC address

Broadcast an ARP Request "Who has this IP address?" in order to get the MAC address of its IP address from ARP Reply and store the mapping IP -> MAC in its cached ARP table.

## Ping (Layer 3)

Check if its alive/reachable

- TTP
  - Limit hops on routers

## DHCP Server

Assign an IP address for a new client

<img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251004231125840.png" alt="image-20251004231125840" style="zoom:30%; float:left;"/>

## Socket API

<img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251005035321564.png" alt="image-20251005035321564" style="zoom:35%; float:left" />

Interface for an application to send/receive data from OS's network

- IP address (Layer 3)
- Port (Layer 4)
- TCP/UDP Protocol

-----

## Sniff

<img src="/Users/kimhakhyun/Library/Application Support/typora-user-images/image-20251005035436663.png" alt="image-20251005035436663" style="zoom:30%; float:left;" />

Promiscuous/Monitor mode will pass all frames from NIC, regardless if they were meant for me or not
Raw socket will be delivered directly

## Spoof

Send a fake packet

## 

