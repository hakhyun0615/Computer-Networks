import time

from api import send, sr
from layers import ICMP, IP, Ether


def main():
    # VM values
    iface = "ens160"
    my_ip = "172.16.191.128"
    my_mac = "00:0c:29:6f:00:f1"
    dst_mac = "00:50:56:fb:73:ea"  # gateway MAC (172.16.191.2)

    eth = Ether(src_mac=my_mac, dst_mac=dst_mac)
    ip = IP(src_ip=my_ip, dst_ip="8.8.8.8")
    icmp = ICMP(type=8, code=0, id=1, seq=1)

    pkt = eth / ip / icmp

    print("Sending ICMP Echo Request...")
    send(pkt)  # Layer 3
    time.sleep(1)

    icmp.seq = 2
    send(pkt)

    print("Waiting for ICMP Echo Reply...")
    reply_pkt = sr(pkt, interface=iface, timeout=5.0)
    reply_pkt.show()


if __name__ == "__main__":
    main()