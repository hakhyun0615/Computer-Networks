# webclient.py (improved)
import socket
import sys

def run_client(server_host, server_port, filename):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))

        # HTTP/1.1 requires Host header
        request = f"GET /{filename} HTTP/1.1\r\nHost: {server_host}\r\nConnection: close\r\n\r\n"
        client_socket.sendall(request.encode("utf-8"))

        # Read until EOF
        response = b""
        while True:
            chunk = client_socket.recv(65536)
            if not chunk:
                break
            response += chunk

        # Split headers/body
        sep = response.find(b"\r\n\r\n")
        if sep == -1:
            print("[ERROR] Malformed response (no header/body separator)")
            print(response.decode("utf-8", errors="replace"))
            return

        headers = response[:sep].decode("utf-8", errors="replace")
        body = response[sep+4:]

        print("=== RESPONSE HEADERS ===")
        print(headers)
        print("\n=== RESPONSE BODY (first 1000 chars) ===")
        try:
            print(body.decode("utf-8")[:1000])
        except UnicodeDecodeError:
            print(f"[binary body: {len(body)} bytes]")
    except socket.error as e:
        print(f"[ERROR] Could not connect to server: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 webclient.py <server_host> <server_port> <filename>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]
    run_client(server_host, server_port, filename)