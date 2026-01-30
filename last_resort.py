#!/usr/bin/env python3
"""
Last Resort - Try setting print area and other fundamental settings
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def test_print_width(pw, text):
    """Set print width explicitly"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"PW{pw}\r\n"  # Print width
    dpl += f"121100000100100{text}\r\n"
    dpl += "E\r\n"
    print(f"Print Width: PW{pw}")
    return dpl.encode('ascii')

def test_label_length(ll, text):
    """Set label length explicitly"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"LL{ll}\r\n"  # Label length
    dpl += f"121100000100100{text}\r\n"
    dpl += "E\r\n"
    print(f"Label Length: LL{ll}")
    return dpl.encode('ascii')

def test_origin_zero(text):
    """Try setting origin to 0"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "z0\r\n"  # Origin setting
    dpl += f"121100000100100{text}\r\n"
    dpl += "E\r\n"
    print("Origin z0")
    return dpl.encode('ascii')

def test_start_position(sp, text):
    """Try start print position"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"SP{sp}\r\n"  # Start position
    dpl += f"121100000100100{text}\r\n"
    dpl += "E\r\n"
    print(f"Start Position: SP{sp}")
    return dpl.encode('ascii')

def test_negative_x(x, text):
    """Try negative X in the text command itself"""
    # Maybe format allows negative
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"1211{x:05d}0100100{text}\r\n"  # 5 digit X with sign
    dpl += "E\r\n"
    print(f"Negative X: {x}")
    return dpl.encode('ascii')

def test_form_feed_position(ff, text):
    """Try form feed position"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"f{ff}\r\n"  # Form feed position
    dpl += f"121100000100100{text}\r\n"
    dpl += "E\r\n"
    print(f"Form feed position: f{ff}")
    return dpl.encode('ascii')

def test_simple_rotation(text):
    """Try different rotation"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    # Rotation 1 instead of 2
    dpl += f"111100000100100{text}\r\n"
    dpl += "E\r\n"
    print("Rotation 1 instead of 2")
    return dpl.encode('ascii')

def test_different_record_type(text):
    """Try record type 2 instead of 1"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"221100000100100{text}\r\n"
    dpl += "E\r\n"
    print("Record type 2")
    return dpl.encode('ascii')

def ask_printer_config():
    """Print current config from printer"""
    print("\n*** IMPORTANT ***")
    print("On your printer's LCD screen, please check:")
    print("1. MENU -> MEDIA SETTINGS -> PRINT WIDTH")
    print("2. MENU -> MEDIA SETTINGS -> LABEL LENGTH")  
    print("3. MENU -> MEDIA SETTINGS -> LEFT POSITION (or OFFSET)")
    print("\nWhat values do you see?")

def main():
    print("="*60)
    print("LAST RESORT TESTS")
    print("="*60)
    
    while True:
        print("\n--- OPTIONS ---")
        print("  1. Set Print Width (PW200)")
        print("  2. Set Print Width (PW400)")
        print("  3. Set Label Length (LL200)")
        print("  4. Try origin z0")
        print("  5. Try Start Position SP-200")
        print("  6. Try Start Position SP200")
        print("  7. Try negative X (-200)")
        print("  8. Try form feed f-200")
        print("  9. Try rotation 1")
        print("  10. Try record type 2")
        print("  11. Check printer settings (instructions)")
        print("  q. Quit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == 'q':
            break
        elif choice == '1':
            send_to_usb_printer(test_print_width(200, "PW200"))
        elif choice == '2':
            send_to_usb_printer(test_print_width(400, "PW400"))
        elif choice == '3':
            send_to_usb_printer(test_label_length(200, "LL200"))
        elif choice == '4':
            send_to_usb_printer(test_origin_zero("ZERO"))
        elif choice == '5':
            send_to_usb_printer(test_start_position(-200, "SPneg"))
        elif choice == '6':
            send_to_usb_printer(test_start_position(200, "SPpos"))
        elif choice == '7':
            send_to_usb_printer(test_negative_x(-200, "NEG"))
        elif choice == '8':
            send_to_usb_printer(test_form_feed_position(-200, "FFneg"))
        elif choice == '9':
            send_to_usb_printer(test_simple_rotation("ROT1"))
        elif choice == '10':
            send_to_usb_printer(test_different_record_type("TYPE2"))
        elif choice == '11':
            ask_printer_config()
        
        print("\nResult? (Enter to continue)")
        input()

if __name__ == "__main__":
    main()
