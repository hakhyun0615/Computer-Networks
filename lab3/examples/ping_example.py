import time

from api import send, sr
from layers import ICMP, IP, Ether


def main():
    # macOS values provided by you
    my_ip = "10.3.5.4"
    my_mac = "42:16:ac:8b:16:68"
    dst_mac = "dc:2c:6e:20:75:b0"  # gateway MAC

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
    reply_pkt = sr(pkt)
    reply_pkt.show()


if __name__ == "__main__":
    main()