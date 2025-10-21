def create_raw_socket(layer):
    if layer == 2:  # Layer 2 (Ethernet)
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    elif layer == 3:  # Layer 3 (IP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    else:
        raise ValueError("Unsupported layer: {}".format(layer))
    return sock

def send_packet(sock, packet_bytes):
    sock.send(packet_bytes)

def receive_packet(sock, buffer_size=65535):
    return sock.recv(buffer_size)

def bind_socket(sock, interface):
    sock.bind((interface, 0))  # Bind to the specified interface

def close_socket(sock):
    sock.close()