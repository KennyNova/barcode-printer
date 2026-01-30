#!/usr/bin/env python3
"""
Safe test - no reset commands, just print tests
Uses the format that printed "00hi" before
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def test1():
    """Exact format that printed 00hi"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "121100010010001001TEST\r\n"
    dpl += "E\r\n"
    return dpl.encode('ascii')

def test2():
    """Same but with STX n first to clear just the buffer"""
    dpl = "\x02n\r\n"  # Clear input buffer only
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "121100010010001001TEST\r\n"
    dpl += "E\r\n"
    return dpl.encode('ascii')

def test3():
    """Try without D11 density"""
    dpl = "\x02L\r\n"
    dpl += "121100010010001001TEST\r\n"
    dpl += "E\r\n"
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("SAFE TEST - No reset commands")
    print("="*60)
    print("\nThese use the format that printed '00hi' before")
    print("\n1. Basic format")
    print("2. With buffer clear")
    print("3. Without D11")
    print("q. Quit")
    
    while True:
        choice = input("\nChoice: ").strip()
        
        if choice == 'q':
            break
        elif choice == '1':
            print("Sending test 1...")
            send_to_usb_printer(test1())
        elif choice == '2':
            print("Sending test 2...")
            send_to_usb_printer(test2())
        elif choice == '3':
            print("Sending test 3...")
            send_to_usb_printer(test3())
        
        result = input("What happened? ").strip()
        print(f"Noted: {result}")

if __name__ == "__main__":
    main()
