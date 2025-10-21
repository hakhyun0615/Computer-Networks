#!/bin/bash
# Quick Start Script for Lab 3
# Run this script to set up and test everything

echo "========================================="
echo "Lab 3: Packet Crafting - Quick Start"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Please run with sudo"
    echo "Usage: sudo bash quickstart.sh"
    exit 1
fi

echo "[1/4] Detecting network configuration..."
python3 get_network_info.py > network_config.txt 2>&1

echo ""
echo "[2/4] Network configuration saved to network_config.txt"
echo "Please review and update test_all.py with these values:"
echo ""
grep -A 4 "interface =" network_config.txt | head -n 5
echo ""

read -p "Have you updated test_all.py? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please update test_all.py first, then run:"
    echo "  sudo python3 test_all.py"
    exit 1
fi

echo ""
echo "[3/4] Starting Wireshark (in background)..."
echo "Make sure to start capturing on your network interface!"
wireshark &
sleep 3

echo ""
echo "[4/4] Running complete test suite..."
read -p "Press Enter when Wireshark is capturing..."

python3 test_all.py

echo ""
echo "========================================="
echo "Tests Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review Wireshark captures"
echo "2. Take screenshots of:"
echo "   - ICMP ping (send, sendp, sr)"
echo "   - DNS query/response"
echo "   - TCP handshake"
echo "   - HTTP GET/response"
echo "3. Create report PDF with screenshots"
echo "4. Zip lab3 folder for submission"
echo ""
