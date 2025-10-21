import socket
import os

HOST = "127.0.0.1" # localhost
PORT = 8080 

def run_server():
    # create tcp socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # bind socket to address/port
    server_socket.bind((HOST, PORT))
    
    # listen for incoming connections
    server_socket.listen(1)
    print(f"Server is listening on http://{HOST}:{PORT}")
    
    try:
        while True:
            # accept new connection
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            
            try:
                # read data from client socket and decode
                request = client_socket.recv(1024).decode('utf-8', errors='ignore')
                if not request:
                    continue
            
                # parse request to get the filename
                request_lines = request.split('\n')
                first_line = request_lines[0].strip()
                method, path, _ = first_line.split()
            
                if method == 'GET':
                    filename = path[1:]
                
                    if os.path.exists(filename):
                        # send ok response
                        response_header = 'HTTP/1.1 200 OK\r\n\r\n'
                    
                        with open(filename, 'rb') as file:
                            content = file.read()
                        
                        client_socket.sendall(response_header.encode('utf-8') + content)
                        print(f"Sent file: {filename}")
                    else:
                        # send 404 file not found
                        response_header = 'HTTP/1.1 404 Not Found\r\n\r\n'
                        response_body = '<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n'
                        client_socket.sendall((response_header + response_body).encode('utf-8'))
                        print(f"File not found: {filename}")
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                client_socket.close()
    except KeyboardInterrupt:
        print("\nShutting down the server")
    finally:
        server_socket.close()
if __name__ == "__main__":
    run_server()