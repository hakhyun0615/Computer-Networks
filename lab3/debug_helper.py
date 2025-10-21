#!/usr/bin/env python3
"""
Debug helper for Lab 3
Checks common issues and provides solutions
"""

import os
import subprocess
import sys


def run_cmd(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def check_root():
    """Check if running as root"""
    print("[*] Checking root privileges...")
    if os.geteuid() != 0:
        print("    ❌ NOT running as root")
        print("    → Solution: Run with 'sudo python3 debug_helper.py'")
        return False
    else:
        print("    ✅ Running as root")
        return True


def check_python_version():
    """Check Python version"""
    print("\n[*] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"    ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"    ❌ Python {version.major}.{version.minor}.{version.micro}")
        print("    → Solution: Install Python 3.7 or higher")
        return False


def check_network_interface():
    """Check network interfaces"""
    print("\n[*] Checking network interfaces...")
    code, out, err = run_cmd("ip link show")
    
    interfaces = []
    for line in out.split('\n'):
        if ': ' in line and not line.startswith(' '):
            parts = line.split(': ')
            if len(parts) >= 2:
                iface = parts[1].split('@')[0]
                if iface != 'lo' and 'state UP' in line:
                    interfaces.append(iface)
    
    if interfaces:
        print(f"    ✅ Found active interfaces: {', '.join(interfaces)}")
        return True, interfaces[0]
    else:
        print("    ❌ No active network interfaces found")
        print("    → Solution: Check network connection")
        return False, None


def check_connectivity():
    """Check basic network connectivity"""
    print("\n[*] Checking network connectivity...")
    code, out, err = run_cmd("ping -c 1 -W 2 8.8.8.8")
    
    if code == 0:
        print("    ✅ Can reach 8.8.8.8")
        return True
    else:
        print("    ❌ Cannot reach 8.8.8.8")
        print("    → Solution: Check network connection and routing")
        return False


def check_arp_table():
    """Check ARP table for gateway"""
    print("\n[*] Checking ARP table...")
    code, out, err = run_cmd("arp -n")
    
    entries = len([l for l in out.split('\n') if ':' in l])
    if entries > 0:
        print(f"    ✅ Found {entries} ARP entries")
        print("\n    ARP Table:")
        for line in out.split('\n')[:6]:  # Show first 5 lines
            if line.strip():
                print(f"    {line}")
        return True
    else:
        print("    ⚠️  Empty ARP table")
        print("    → Trying to populate with ping...")
        run_cmd("ping -c 1 -W 1 $(ip route | grep default | awk '{print $3}')")
        code, out, err = run_cmd("arp -n")
        print(f"\n    {out}")
        return True


def check_firewall():
    """Check iptables rules"""
    print("\n[*] Checking firewall rules...")
    code, out, err = run_cmd("iptables -L OUTPUT -n")
    
    if 'RST' in out:
        print("    ⚠️  RST blocking rule found (expected during TCP tests)")
        print("    → This is normal during TCP testing")
        print("    → Run cleanup: sudo iptables -D OUTPUT -p tcp --tcp-flags RST RST -j DROP")
    else:
        print("    ✅ No RST blocking rules")
    
    return True


def check_files():
    """Check if all required files exist"""
    print("\n[*] Checking required files...")
    
    required_files = [
        'api.py',
        'test_all.py',
        'ping_example.py',
        'dns_example.py',
        'tcp_http_example.py',
        'layers/__init__.py',
        'layers/base.py',
        'layers/ether.py',
        'layers/ip.py',
        'layers/icmp.py',
        'layers/udp.py',
        'layers/tcp.py',
        'layers/dns.py',
        'utils/__init__.py',
        'utils/helpers.py',
    ]
    
    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)
    
    if missing:
        print(f"    ❌ Missing files:")
        for f in missing:
            print(f"       - {f}")
        return False
    else:
        print(f"    ✅ All {len(required_files)} required files present")
        return True


def test_import():
    """Test if modules can be imported"""
    print("\n[*] Testing module imports...")
    
    try:
        from layers import Ether, IP, ICMP, UDP, TCP, DNS
        print("    ✅ Successfully imported all layers")
        
        from api import send, sendp, sr, sniff
        print("    ✅ Successfully imported all API functions")
        
        from utils import checksum_ones_complement, ip_to_bytes, mac_to_bytes
        print("    ✅ Successfully imported all utility functions")
        
        return True
    except Exception as e:
        print(f"    ❌ Import error: {e}")
        return False


def suggest_config():
    """Suggest configuration values"""
    print("\n[*] Suggested configuration:")
    print("="*60)
    
    # Get interface
    code, out, err = run_cmd("ip route | grep default | awk '{print $5}'")
    interface = out.strip() or "ens160"
    print(f"interface = \"{interface}\"")
    
    # Get IP
    code, out, err = run_cmd(f"ip addr show {interface} | grep 'inet ' | awk '{{print $2}}' | cut -d/ -f1")
    my_ip = out.strip() or "0.0.0.0"
    print(f"my_ip = \"{my_ip}\"")
    
    # Get MAC
    code, out, err = run_cmd(f"ip link show {interface} | grep 'link/ether' | awk '{{print $2}}'")
    my_mac = out.strip() or "00:00:00:00:00:00"
    print(f"my_mac = \"{my_mac}\"")
    
    # Get gateway IP and MAC
    code, out, err = run_cmd("ip route | grep default | awk '{print $3}'")
    gateway_ip = out.strip()
    
    if gateway_ip:
        run_cmd(f"ping -c 1 -W 1 {gateway_ip} > /dev/null 2>&1")
        code, out, err = run_cmd(f"arp -n {gateway_ip} | grep {gateway_ip} | awk '{{print $3}}'")
        gateway_mac = out.strip()
        if not gateway_mac or ':' not in gateway_mac:
            code, out, err = run_cmd("arp -n | grep -v 'incomplete' | grep ':' | head -n 1 | awk '{print $3}'")
            gateway_mac = out.strip() or "00:00:00:00:00:00"
    else:
        gateway_mac = "00:00:00:00:00:00"
    
    print(f"gateway_mac = \"{gateway_mac}\"")
    print("="*60)
    print("\n    Copy these values to test_all.py")


def main():
    print("="*60)
    print("Lab 3: Packet Crafting - Debug Helper")
    print("="*60)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Run all checks
    checks = [
        ("Root privileges", check_root),
        ("Python version", check_python_version),
        ("Network interface", lambda: check_network_interface()[0]),
        ("Network connectivity", check_connectivity),
        ("Required files", check_files),
        ("Module imports", test_import),
    ]
    
    for name, check in checks:
        total_checks += 1
        try:
            if check():
                checks_passed += 1
        except Exception as e:
            print(f"    ❌ Error during {name} check: {e}")
    
    # Additional checks (non-critical)
    check_arp_table()
    check_firewall()
    suggest_config()
    
    # Summary
    print("\n" + "="*60)
    print(f"Summary: {checks_passed}/{total_checks} critical checks passed")
    print("="*60)
    
    if checks_passed == total_checks:
        print("\n✅ All checks passed! You're ready to run tests.")
        print("\nNext steps:")
        print("1. Update test_all.py with the configuration above")
        print("2. Start Wireshark")
        print("3. Run: sudo python3 test_all.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Run with: sudo python3 debug_helper.py")
        print("- Check network connection")
        print("- Install Python 3.7+")
        print("- Verify all files are present")


if __name__ == "__main__":
    main()
