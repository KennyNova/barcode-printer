#!/usr/bin/env python3
"""
Reset printer and test basic printing
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def reset_printer():
    """Send reset commands"""
    print("Sending reset...")
    # Various reset commands
    reset = "\x02n\r\n"    # Clear buffer
    reset += "\x02O\r\n"   # Reset to defaults
    send_to_usb_printer(reset.encode('ascii'))
    time.sleep(2)
    print("Reset sent. Wait for printer to be ready...")

def simple_test():
    """Absolute simplest test"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "A\r\n"  # Just the letter A
    dpl += "E\r\n"
    print("Sending just 'A'")
    return dpl.encode('ascii')

def test_original_working():
    """The format that printed '00hi' before - it DID print"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "121100010010001001TEST\r\n"  # Original format
    dpl += "E\r\n"
    print("Original format that printed (with 00 prefix)")
    return dpl.encode('ascii')

def test_quoted():
    """Quoted text format"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += '121100010010100"QUOTED"\r\n'
    dpl += "E\r\n"
    print("Quoted format")
    return dpl.encode('ascii')

def test_set_label_size():
    """Try setting label size in DPL"""
    dpl = "\x02n\r\n"      # Clear
    dpl += "\x02M0500\r\n" # Metric mode
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "PW089\r\n"     # Print width 89 dots (7/16")
    dpl += "LL355\r\n"     # Label length 355 dots (1.75")
    dpl += '121100010010100"SIZE"\r\n'
    dpl += "E\r\n"
    print("With explicit label size commands")
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("RESET AND TEST")
    print("="*60)
    
    print("\nOptions:")
    print("  0. Reset printer to defaults")
    print("  1. Simplest test (just 'A')")
    print("  2. Original format (printed with 00 prefix before)")
    print("  3. Quoted format")
    print("  4. With explicit label size")
    print("  q. Quit")
    
    while True:
        choice = input("\nChoice: ").strip()
        
        if choice == 'q':
            break
        elif choice == '0':
            reset_printer()
        elif choice == '1':
            send_to_usb_printer(simple_test())
        elif choice == '2':
            send_to_usb_printer(test_original_working())
        elif choice == '3':
            send_to_usb_printer(test_quoted())
        elif choice == '4':
            send_to_usb_printer(test_set_label_size())
        
        print("\nDid text print? (y/n)")
        input()

if __name__ == "__main__":
    main()
