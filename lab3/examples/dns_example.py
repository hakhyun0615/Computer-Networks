from api import sr
from layers import DNS, IP, UDP, Ether


def main():
    # macOS values provided by you
    my_ip = "10.3.5.4"
    my_mac = "42:16:ac:8b:16:68"
    dst_mac = "dc:2c:6e:20:75:b0"  # gateway MAC

    eth = Ether(src_mac=my_mac, dst_mac=dst_mac)
    ip = IP(src_ip=my_ip, dst_ip="8.8.8.8")
    udp = UDP(sport=12345, dport=53)
    dns = DNS(qname="vibrantcloud.org")

    pkt = eth / ip / udp / dns

    response = sr(pkt)
    response.show()


if __name__ == "__main__":
    main()