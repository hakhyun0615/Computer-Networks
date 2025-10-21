#!/usr/bin/env python3
"""
Helper script to get network configuration for your system.
Run this first to get the values needed for testing.
"""

import subprocess
import re


def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    except:
        return ""


def get_default_interface():
    """Get the default network interface"""
    try:
        # Try using ip route
        output = run_command("ip route | grep default")
        match = re.search(r'dev\s+(\S+)', output)
        if match:
            return match.group(1)
        
        # Fallback
        output = run_command("ip link show")
        for line in output.split('\n'):
            if 'state UP' in line:
                match = re.search(r'^\d+:\s+(\S+):', line)
                if match and match.group(1) != 'lo':
                    return match.group(1)
        
        return "ens160"  # Default guess
    except:
        return "ens160"


def get_ip_address(interface):
    """Get IP address for an interface"""
    try:
        output = run_command(f"ip addr show {interface}")
        match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', output)
        if match:
            return match.group(1)
        return "0.0.0.0"
    except:
        return "0.0.0.0"


def get_mac_address(interface):
    """Get MAC address for an interface"""
    try:
        output = run_command(f"ip link show {interface}")
        match = re.search(r'link/ether\s+([\da-f:]+)', output)
        if match:
            return match.group(1)
        return "00:00:00:00:00:00"
    except:
        return "00:00:00:00:00:00"


def get_gateway_ip():
    """Get gateway IP address"""
    try:
        output = run_command("ip route | grep default")
        match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', output)
        if match:
            return match.group(1)
        return None
    except:
        return None


def get_gateway_mac():
    """Get MAC address of default gateway using ARP"""
    try:
        gateway_ip = get_gateway_ip()
        if not gateway_ip:
            # Fallback: look for gateway in arp table
            output = run_command("arp -n")
            for line in output.split('\n'):
                if 'ether' in line.lower() or ':' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = None
                        for part in parts:
                            if ':' in part and len(part) == 17:
                                mac = part
                                break
                        if mac:
                            return mac
        else:
            # Ping gateway to ensure it's in ARP table
            run_command(f"ping -c 1 -W 1 {gateway_ip} > /dev/null 2>&1")
            output = run_command(f"arp -n {gateway_ip}")
            match = re.search(r'([\da-f:]{17})', output)
            if match:
                return match.group(1)
            
            # Try without specific IP
            output = run_command("arp -n")
            for line in output.split('\n'):
                if gateway_ip in line:
                    match = re.search(r'([\da-f:]{17})', line)
                    if match:
                        return match.group(1)
        
        return "00:00:00:00:00:00"
    except:
        return "00:00:00:00:00:00"


def main():
    print("="*60)
    print("Network Configuration Discovery")
    print("="*60)
    print()
    
    # Get default interface
    print("Detecting network interface...")
    interface = get_default_interface()
    print(f"✓ Default Interface: {interface}")
    
    # Get IP address
    print("\nGetting IP address...")
    my_ip = get_ip_address(interface)
    print(f"✓ IP Address: {my_ip}")
    
    # Get MAC address
    print("\nGetting MAC address...")
    my_mac = get_mac_address(interface)
    print(f"✓ MAC Address: {my_mac}")
    
    # Get gateway info
    print("\nGetting gateway information...")
    gateway_ip = get_gateway_ip()
    if gateway_ip:
        print(f"✓ Gateway IP: {gateway_ip}")
    
    print("\nAttempting to get gateway MAC address...")
    print("(This may take a moment...)")
    gateway_mac = get_gateway_mac()
    print(f"✓ Gateway MAC: {gateway_mac}")
    
    print("\n" + "="*60)
    print("Configuration Summary:")
    print("="*60)
    print(f"""
interface = "{interface}"
my_ip = "{my_ip}"
my_mac = "{my_mac}"
gateway_mac = "{gateway_mac}"
""")
    
    print("\n" + "="*60)
    print("Copy these values to test_all.py")
    print("="*60)
    
    print("\n" + "="*60)
    print("Additional Network Information:")
    print("="*60)
    
    print("\n--- IP Addresses ---")
    output = run_command("ip addr show")
    print(output)
    
    print("\n--- ARP Table ---")
    output = run_command("arp -n")
    print(output)
    
    print("\n--- Default Route ---")
    output = run_command("ip route | grep default")
    print(output)
    
    print("\n" + "="*60)
    print("IMPORTANT: Update test_all.py with these values!")
    print("="*60)


if __name__ == "__main__":
    main()
