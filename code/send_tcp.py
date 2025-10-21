import socket

''' 
    Send TCP packets using Python 

	Author: Tim Pierson, Dartmouth CS60, Fall 2025
            Assisted by Microsoft Copilot
	
	run: python3 send_tcp.py
'''

#define server's ip and port
HOST = '127.0.0.1'
PORT = 9090

#create TCP socket to connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    message = "Hello, Server!"
    client_socket.sendall(message.encode()) #encode converts to bytes
    data = client_socket.recv(1024) #get server's response
    print(f"Received from server: {data.decode()}")
finally:
    client_socket.close()