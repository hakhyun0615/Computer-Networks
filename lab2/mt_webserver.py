import socket
import os
import threading
from urllib.parse import unquote
from typing import Optional

HOST = "0.0.0.0"       # listen on all interfaces so teammates can reach you
PORT = 8080
BACKLOG = 50           # allow a burst of pending connections
BUF_SIZE = 64 * 1024   # 64KB chunks for large files

WWW_ROOT = os.path.abspath(".")  # serve files from current dir only

def safe_path(url_path: str) -> str:
    """
    Map a URL path like '/helloworld.html' to a safe filesystem path
    rooted at WWW_ROOT, preventing path traversal.
    """
    # strip leading '/', decode %xx, default to 'index.html' if '/'
    rel = unquote(url_path.lstrip("/")) or "index.html"
    # normalize and join
    candidate = os.path.abspath(os.path.join(WWW_ROOT, rel))
    # enforce jail
    if not candidate.startswith(WWW_ROOT + os.sep) and candidate != WWW_ROOT:
        return None
    return candidate

def build_header(status_line: str, content_length: Optional[int]) -> bytes:
    # minimal headers are fine for this lab
    lines = [status_line]
    if content_length is not None:
        lines.append(f"Content-Length: {content_length}")
    lines.append("Connection: close")
    # blank line to end headers
    lines.append("")
    lines.append("")
    return ("\r\n".join(lines)).encode("utf-8")

def handle_client(client_sock: socket.socket, client_addr):
    try:
        # Receive request bytes (don’t assume it arrives in one recv)
        client_sock.settimeout(2.0)
        data = b""
        while b"\r\n\r\n" not in data and len(data) < 8192:
            chunk = client_sock.recv(4096)
            if not chunk:
                break
            data += chunk

        if not data:
            return

        try:
            first_line = data.split(b"\r\n", 1)[0].decode("utf-8", errors="replace").strip()
            parts = first_line.split()
            if len(parts) < 2:
                # malformed request
                client_sock.sendall(build_header("HTTP/1.1 400 Bad Request", 0))
                return

            method, path = parts[0], parts[1]
        except Exception:
            client_sock.sendall(build_header("HTTP/1.1 400 Bad Request", 0))
            return

        if method != "GET":  # rubric: process only GET
            hdr = build_header("HTTP/1.1 405 Method Not Allowed", 0)
            client_sock.sendall(hdr)
            return

        fs_path = safe_path(path)
        if fs_path is None or not os.path.exists(fs_path) or not os.path.isfile(fs_path):
            body = b"<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n"
            hdr = build_header("HTTP/1.1 404 Not Found", len(body))
            client_sock.sendall(hdr + body)
            print(f"[{client_addr}] 404 {path}")
            return

        # Serve file in chunks so big files work (rubric: multi-packet content)
        file_size = os.path.getsize(fs_path)
        hdr = build_header("HTTP/1.1 200 OK", file_size)
        client_sock.sendall(hdr)

        with open(fs_path, "rb") as f:
            while True:
                buf = f.read(BUF_SIZE)
                if not buf:
                    break
                client_sock.sendall(buf)

        print(f"[{client_addr}] 200 {path} ({file_size} bytes)")
    except socket.timeout:
        pass
    except Exception as e:
        # Don’t crash the server on one bad client
        print(f"[{client_addr}] Error: {e}")
    finally:
        try:
            client_sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        client_sock.close()

def run_server():
    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow quick restart
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to host/port (rubric: create and bind)
    server_socket.bind((HOST, PORT))

    # Listen (rubric: main process accepts connections)
    server_socket.listen(BACKLOG)
    print(f"MT server listening on http://{HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            # Create a Communicator thread per client (rubric: separate thread+socket)
            t = threading.Thread(
                target=handle_client, args=(client_socket, client_address), daemon=True
            )
            t.start()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_server()