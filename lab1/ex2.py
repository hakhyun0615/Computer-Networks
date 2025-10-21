#!/usr/bin/env python3
# CS60 Lab 1 - Exercise 2: Scapy Traceroute (ICMP-based)
# Author: <Your Name>
# Usage: sudo python3 ex2.py <host or IP> [options]
#
# Notes:
#  - Uses ICMP Echo with increasing TTL (do NOT use scapy's built-in traceroute).
#  - Prints per-hop lines similar to classic traceroute.
#  - Defaults: max 30 hops, 3 probes per hop, 2s timeout.
#
# Dartmouth note: If ICMP replies are blocked on campus, test off-campus (no VPN).

import argparse
import socket
import time

from scapy.all import ICMP, IP, Raw, conf, sr1


def resolve_target(target: str) -> str:
    try:
        return socket.gethostbyname(target)
    except socket.gaierror as e:
        raise SystemExit(f"traceroute: cannot resolve {target}: Unknown host ({e})")

def rdns(ip: str) -> str:
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except Exception:
        return ip

def main():
    parser = argparse.ArgumentParser(description="Scapy-based traceroute (ICMP)")
    parser.add_argument("target", help="hostname or IPv4 (e.g., 8.8.8.8 or google.com)")
    parser.add_argument("-m", "--max-hops", type=int, default=30, help="max TTL (default 30)")
    parser.add_argument("-q", "--queries", type=int, default=3, help="probes per hop (default 3)")
    parser.add_argument("-W", "--timeout", type=float, default=2.0, help="timeout seconds (default 2.0)")
    args = parser.parse_args()

    conf.verb = 0  # quiet
    dest_ip = resolve_target(args.target)
    print(f"traceroute to {args.target} ({dest_ip}), {args.max_hops} hops max, {args.queries} probes, {int(args.timeout*1000)}ms timeout")

    # Stable ICMP identifier
    ident = int(time.time()) & 0xFFFF
    reached = False

    for ttl in range(1, args.max_hops + 1):
        line_outputs = []
        hop_ip = None
        for q in range(args.queries):
            seq = ttl * 10 + q  # unique-ish per probe
            payload = bytes((i % 256 for i in range(32)))  # 32B payload is enough
            pkt = IP(dst=dest_ip, ttl=ttl) / ICMP(id=ident, seq=seq) / Raw(load=payload)

            t0 = time.time()
            reply = sr1(pkt, timeout=args.timeout)
            t1 = time.time()

            if reply is None:
                line_outputs.append("*")
                continue

            rtt_ms = (t1 - t0) * 1000.0
            hop_ip = reply[IP].src
            line_outputs.append(f"{rtt_ms:.3f} ms")

            # Destination reached when Echo Reply (type 0)
            if reply.haslayer(ICMP) and reply[ICMP].type == 0 and reply[IP].src == dest_ip:
                reached = True

        # Print hop line
        if hop_ip is None:
            # Unknown hop
            print(f"{ttl:>2}  " + "  ".join(line_outputs))
        else:
            host_display = rdns(hop_ip)
            print(f"{ttl:>2}  {host_display} ({hop_ip})  " + "  ".join(line_outputs))

        if reached:
            break

if __name__ == "__main__":
    main()
