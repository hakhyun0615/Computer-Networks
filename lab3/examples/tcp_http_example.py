import random

from api import send, sr
from layers import IP, TCP, Ether


def create_tcp_connection(src_ip, dst_ip, src_port, dst_port, iface: str):
    seq_num = random.randint(0, 2**32 - 1)
    # VM values
    eth_syn = Ether(src_mac="00:0c:29:6f:00:f1", dst_mac="00:50:56:fb:73:ea")
    ip_syn = IP(src_ip=src_ip, dst_ip=dst_ip)
    tcp_syn = TCP(sport=src_port, dport=dst_port, seq=seq_num, flags=0x02)

    syn_pkt = eth_syn / ip_syn / tcp_syn
    ret_pkt = sr(syn_pkt, interface=iface, timeout=8.0)
    tcp_layer = ret_pkt.get_layer("TCP")
    tcp_layer.show() if tcp_layer else None

    seq_num += 1
    ack_num = (tcp_layer.seq + 1) if tcp_layer else 0

    # Fresh Ether/IP for ACK to avoid chaining the previous objects
    eth_ack = Ether(src_mac="00:0c:29:6f:00:f1", dst_mac="00:50:56:fb:73:ea")
    ip_ack = IP(src_ip=src_ip, dst_ip=dst_ip)
    tcp_ack = TCP(sport=src_port, dport=dst_port, seq=seq_num, ack=ack_num, flags=0x10)

    ack_pkt = eth_ack / ip_ack / tcp_ack
    send(ack_pkt)

    return seq_num, ack_num


def send_http_get(src_ip, dst_ip, src_port, dst_port, iface: str):
    seq, ack = create_tcp_connection(src_ip, dst_ip, src_port, dst_port, iface)

    http_get = f"GET /index.html HTTP/1.1\r\nHost: {dst_ip}\r\n\r\n".encode()

    # Fresh Ether/IP for the GET segment as well
    eth_get = Ether(src_mac="00:0c:29:6f:00:f1", dst_mac="00:50:56:fb:73:ea")
    ip_get = IP(src_ip=src_ip, dst_ip=dst_ip)
    tcp_get = TCP(sport=src_port, dport=dst_port, seq=seq, ack=ack, flags=0x18, data=http_get)

    get_pkt = eth_get / ip_get / tcp_get
    ret_pkt = sr(get_pkt, interface=iface, timeout=8.0)
    ret_pkt.show()


if __name__ == "__main__":
    iface = "ens160"
    my_ip = "172.16.191.128"
    dst_ip = "173.201.179.249"  # vibrantcloud.org
    src_port = random.getrandbits(16)
    dst_port = 80
    send_http_get(my_ip, dst_ip, src_port, dst_port, iface)