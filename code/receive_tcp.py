import socket

''' 
    Receive TCP packets using Python (single client only)

	Author: Tim Pierson, Dartmouth CS60, Fall 2025
            Assisted by Microsoft Copilot
	
	run: python3 receive_tcp.py
	
	send data from netcat in another terminal or computer (replace IP address)
	nc -t 127.0.0.1 9090
	then type messages
'''

#define host ip and port
HOST = '0.0.0.0' #any localhost interface
PORT = 9090

#create TCP socket listening on ip address and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))


#listen for connections
server_socket.listen()
print(f"Server listening on {HOST}:{PORT}...")
try:
    client_socket, addr = server_socket.accept() #accept returns a new socket to the client and the clients ip/port
    print(f"Connected by {addr}")
    local_ip, local_port = client_socket.getsockname()
    print(f"Using IP {local_ip} and port {local_port} for this client")

    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Received: {data.decode()}") #decode converts bytes to string
        client_socket.sendall(b"Message received: " + data) #sendall sends all chunks (send only sends one chunk!)
finally:
    client_socket.close()
    server_socket.close()