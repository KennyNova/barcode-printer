#!/usr/bin/env python3
"""
Fix Barbell - Try positive C offset and longer text format
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def test_c_offset(c_value, text):
    """Try different C offset values"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"C{c_value}\r\n"
    dpl += f"121100000100100{text}\r\n"
    dpl += "E\r\n"
    print(f"C offset: {c_value}")
    return dpl.encode('ascii')

def test_reference_point(rx, ry, text):
    """Try R command for reference point"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"R{rx},{ry}\r\n"
    dpl += f"121100000100100{text}\r\n"
    dpl += "E\r\n"
    print(f"Reference point: R{rx},{ry}")
    return dpl.encode('ascii')

def test_longer_format(text):
    """Try different format params for longer text"""
    # Maybe 0100 limits length - try 0200 or different values
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    # Try different multiplier values
    dpl += f"121100000100200{text}\r\n"  # Changed 0100 to 0200
    dpl += "E\r\n"
    print(f"Format with 0200 params")
    return dpl.encode('ascii')

def test_wider_format(text):
    """Try 0300 for even wider"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"121100000100300{text}\r\n"  # 0300
    dpl += "E\r\n"
    print(f"Format with 0300 params")
    return dpl.encode('ascii')

def test_home_position(text):
    """Try setting home position"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "H0,0\r\n"  # Home position
    dpl += f"121100000100100{text}\r\n"
    dpl += "E\r\n"
    print(f"With home position H0,0")
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("FIX BARBELL POSITION AND TEXT LENGTH")
    print("="*60)
    
    while True:
        print("\n--- POSITION TESTS ---")
        print("  1. Try C+100 (positive offset, might move LEFT)")
        print("  2. Try C+200")
        print("  3. Try C+300")
        print("  4. Try Reference point R-200,0")
        print("  5. Try Home position H0,0")
        print("\n--- TEXT LENGTH TESTS ---")
        print("  6. Try 0200 format (for longer text)")
        print("  7. Try 0300 format")
        print("  8. Full test: C+200 with 0200 format")
        print("\n  q. Quit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == 'q':
            break
        elif choice == '1':
            send_to_usb_printer(test_c_offset("+100", "POS100"))
        elif choice == '2':
            send_to_usb_printer(test_c_offset("+200", "POS200"))
        elif choice == '3':
            send_to_usb_printer(test_c_offset("+300", "POS300"))
        elif choice == '4':
            send_to_usb_printer(test_reference_point(-200, 0, "REF"))
        elif choice == '5':
            send_to_usb_printer(test_home_position("HOME"))
        elif choice == '6':
            send_to_usb_printer(test_longer_format("ABCDEFGHIJ"))
            print("\nDid all 10 characters print? (ABCDEFGHIJ)")
        elif choice == '7':
            send_to_usb_printer(test_wider_format("1234567890ABCD"))
            print("\nDid all 14 characters print?")
        elif choice == '8':
            # Combined test
            dpl = "\x02L\r\n"
            dpl += "D11\r\n"
            dpl += "C+200\r\n"
            dpl += "121100000100200PRICE CARAT SKU123\r\n"
            dpl += "E\r\n"
            send_to_usb_printer(dpl.encode('ascii'))
            print("\nDid it print in a better position with full text?")
        
        print("\nWhere did it print? (front/back/loop)")
        input("Press Enter to continue...")

if __name__ == "__main__":
    main()
