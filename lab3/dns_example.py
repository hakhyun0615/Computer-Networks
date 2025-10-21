from api import sr
from layers import DNS, IP, UDP, Ether


def main():
    # VM values
    iface = "ens160"
    my_ip = "172.16.191.128"
    my_mac = "00:0c:29:6f:00:f1"
    dst_mac = "00:50:56:fb:73:ea"  # gateway MAC (172.16.191.2)

    eth = Ether(src_mac=my_mac, dst_mac=dst_mac)
    ip = IP(src_ip=my_ip, dst_ip="8.8.8.8")
    udp = UDP(sport=12345, dport=53)
    dns = DNS(qname="vibrantcloud.org")

    pkt = eth / ip / udp / dns

    # Bind to the specific interface and wait up to 5s
    response = sr(pkt, interface=iface, timeout=5.0)
    response.show()


if __name__ == "__main__":
    main()