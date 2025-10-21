import ipaddress
import sys
from socket import *

''' 
	Send email using SMTP (starter code)

	Author: Tim Pierson, Dartmouth CS60, Fall 2025
        Based on code from Kurose and Ross
        Also input from ChatGPT

	run: python3 send_email.py <mailserver> <port>
         python3 send_email.py smtp.kiewet.dartmouth.edu 1025
         python3 send_email.py 10.28.55.168 1025

    Note: temporary email server simulator is at smtp.kiewet.dartmouth.edu on port 1025
'''   

RECV_BUFFER_SIZE = 1024

def check_server_address(host):
    """
    Check to see if host is an ip address (it might be something like smtp.keiwit.dartmouth.edu)
    If host is not an ip address, try to resolve into an ip address, exit program if unable to resolve to ip address

    host: an ip address or a hostname such as smtp.kiewet.dartmouth.edu
    
    return the ip address for the host 
    """
    #TODO: search on how to tell if a string is an ip address and the command to resolve a hostname to an ip address
    pass
    

def send_message(sock, msg, expected_reply_code=None):
    """
    Send a msg message to the server (with CRLF at end)  
    Listen for reply if expected_reply_code is not None
        Exit if expecting return code and did not get it in server's reply
    
    sock: socket with TCP connection to mail server
    msg: string to send to mail server
    expected_reply_code: integer code the server should reply with, use None if no reply expected

    return server's reply or None if not expecting reply
    """

    #convert expected_reply_code to string
    if expected_reply_code is not None:
        expected_reply_code = str(expected_reply_code)

    #add carriage return and line feed if needed
    if not msg.endswith('\r\n'):
        msg += '\r\n'
    
    #encode message and send to server
    #TODO: use utf-8 encoding, send message out socket 

    #read reply if expecting one
    reply = None
    if expected_reply_code is not None:
        #TODO: receive from server over socket, convert reply to string, look for code
        pass

    return reply

def get_email_message_details():
    '''
    Read sender, recipient, subject and body from keyboard
    
    return sender, recipient, subject, body
    '''
    #get email message to/from (assume one recipient)
    print("Enter email message parameters")
    sender = input("From: ").strip()
    recipient = input("To: ").strip()

    #get subject
    subject = input("Subject: ").strip()

    #get message body (note: body may be multiple lines!)
    print("Enter message body (end with a single '.' on a line):")
    body_lines = []
    while True:
        line = input()
        if line == ".":
            break
        body_lines.append(line)
    body = "\r\n".join(body_lines) #convert body to string with each line separated by carriage return/line feed

    return sender, recipient, subject, body



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <mailserver> <port>")
        exit()
    #get mailserver address and port from command line
    #note that the host migth not be an ip address, might be smtp.kiewit.dartmouth.edu, will have to resolve those to ip addresses
    host = check_server_address(sys.argv[1].strip())
    port = int(sys.argv[2].strip())


    #get message details
    sender, recipient, subject, body = get_email_message_details()
   
    try:
        # Open TCP socket to mail server
        print(f"Connecting to {host} on port {port}")
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))

        # Greeting from server
        print("Server:", sock.recv(RECV_BUFFER_SIZE).decode())

        # HELO
        #TODO: send HELO command to mail server

        # MAIL FROM
        #TODO: send FROM command to mail server

        # RCPT TO
        #TODO: send RCPT TO command to mail server

        # DATA
        #TODO: send DATA command to mail server

        # Send headers and body
        #TODO: send body of email to mail server

        # QUIT
        send_message(sock, "QUIT", 221) #send QUIT to mail server

    except Exception as e:
        print(f"An expected error occured: {e}")
    finally:
            sock.close()