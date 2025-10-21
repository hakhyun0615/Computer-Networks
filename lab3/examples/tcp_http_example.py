import random

from api import send, sr
from layers import IP, TCP, Ether


def create_tcp_connection(src_ip, dst_ip, src_port, dst_port):
    seq_num = random.randint(0, 2**32 - 1)
    # VM values
    eth = Ether(src_mac="00:0c:29:6f:00:f1", dst_mac="00:50:56:fb:73:ea")
    ip = IP(src_ip=src_ip, dst_ip=dst_ip)
    tcp = TCP(sport=src_port, dport=dst_port, seq=seq_num, flags=0x02)

    pkt = eth / ip / tcp
    ret_pkt = sr(pkt)
    tcp_layer = ret_pkt.get_layer("TCP")
    tcp_layer.show() if tcp_layer else None

    seq_num += 1
    ack_num = (tcp_layer.seq + 1) if tcp_layer else 0
    tcp2 = TCP(sport=src_port, dport=dst_port, seq=seq_num, ack=ack_num, flags=0x10)
    pkt2 = eth / ip / tcp2
    send(pkt2)

    return seq_num, ack_num


def send_http_get(src_ip, dst_ip, src_port, dst_port):
    seq, ack = create_tcp_connection(src_ip, dst_ip, src_port, dst_port)

    http_get = f"GET /index.html HTTP/1.1\r\nHost: {dst_ip}\r\n\r\n".encode()
    tcp = TCP(sport=src_port, dport=dst_port, seq=seq, ack=ack, flags=0x18, data=http_get)
    eth = Ether(src_mac="00:0c:29:6f:00:f1", dst_mac="00:50:56:fb:73:ea")
    ip = IP(src_ip=src_ip, dst_ip=dst_ip)

    pkt = eth / ip / tcp
    ret_pkt = sr(pkt)
    ret_pkt.show()


if __name__ == "__main__":
    my_ip = "172.16.191.128"
    dst_ip = "173.201.179.249"  # vibrantcloud.org
    src_port = random.getrandbits(16)
    dst_port = 80
    send_http_get(my_ip, dst_ip, src_port, dst_port)