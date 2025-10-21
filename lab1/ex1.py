import argparse
import signal
import socket
import time
from statistics import mean

from scapy.all import ICMP, IP, Raw, conf, sr1

sent = 0
received = 0
rtts = []
start_time = None
running = True

def sigint_handler(signum, frame):
    global running
    running = False

def resolve_target(target: str) -> str:
    # Use gethostbyname (as in lecture) to resolve names -> IPv4
    try:
        return socket.gethostbyname(target)
    except socket.gaierror as e:
        raise SystemExit(f"ping: cannot resolve {target}: Unknown host ({e})")

def human_stats(host, ip):
    loss = 0 if sent == 0 else (sent - received) * 100.0 / sent
    duration = time.time() - start_time if start_time else 0.0
    print(f"\n--- {host} ping statistics ---")
    print(f"{sent} packets transmitted, {received} packets received, {loss:.1f}% packet loss")
    if rtts:
        import statistics
        std_dev = statistics.stdev(rtts) if len(rtts) > 1 else 0.0
        print(f"round-trip min/avg/max/stddev = {min(rtts):.3f}/{mean(rtts):.3f}/{max(rtts):.3f}/{std_dev:.3f} ms")

def main():
    global sent, received, rtts, start_time

    parser = argparse.ArgumentParser(description="Scapy-based ping")
    parser.add_argument("target", help="hostname or IPv4 address (e.g., 8.8.8.8 or google.com)")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="seconds between pings (default 1.0)")
    parser.add_argument("-W", "--timeout", type=float, default=2.0, help="per-packet timeout in seconds (default 2.0)")
    parser.add_argument("-c", "--count", type=int, default=0, help="number of packets to send (default: unlimited until Ctrl-C)")
    args = parser.parse_args()

    # Resolve (or validate) target
    ip = resolve_target(args.target)

    # Prepare output header like system ping
    payload_size = 56  # bytes, typical /bin/ping data size
    print(f"PING {args.target} ({ip}): {payload_size} data bytes")

    # Prepare payload and identifiers
    payload = bytes((i % 256 for i in range(payload_size)))
    ident = int(time.time()) & 0xFFFF  # stable identifier across pings
    seq = 0

    signal.signal(signal.SIGINT, sigint_handler)
    conf.verb = 0  # be quiet

    start_time = time.time()
    while True:
        if args.count and sent >= args.count:
            break
        seq += 1
        sent += 1

        pkt = IP(dst=ip)/ICMP(id=ident, seq=seq)/Raw(load=payload)

        t0 = time.time()
        reply = sr1(pkt, timeout=args.timeout)
        t1 = time.time()

        if reply is None:
            print(f"Request timeout for icmp_seq {seq}")
        else:
            # Compute RTT in ms
            rtt_ms = (t1 - t0) * 1000.0
            rtts.append(rtt_ms)
            received += 1

            # Bytes reported by system ping include ICMP payload + 8 ICMP header bytes
            bytes_from = len(reply[Raw].load) + 8 if Raw in reply else 64
            ttl = reply[IP].ttl
            print(f"{bytes_from} bytes from {ip}: icmp_seq={seq} ttl={ttl} time={rtt_ms:.3f} ms")

        # pacing
        # Sleep so that total period is ~args.interval (accounting for time spent waiting)
        elapsed = time.time() - t0
        to_sleep = max(0.0, args.interval - elapsed)
        time.sleep(to_sleep)

        if not running:
            break

    human_stats(args.target, ip)

if __name__ == "__main__":
    main()
