#!/usr/bin/env python3
"""
Test using exact format from old label software
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def test_full_sequence():
    """Full sequence exactly like old software"""
    # $02 = STX character = \x02
    dpl = "\x02M3000\r\n"      # Metric mode 3000
    dpl += "\x02KcLW1BB\r\n"   # Configuration
    dpl += "\x0200215\r\n"     # Setting
    dpl += "\x02L\r\n"         # Start label
    dpl += "D11\r\n"           # Density
    dpl += "PE\r\n"            # Present enable
    dpl += "SE\r\n"            # Sensor enable
    dpl += "H17\r\n"           # Heat setting
    dpl += "1911001008001 20TEST1\r\n"
    dpl += "1911001007001 20TEST2\r\n"
    dpl += "1911001006001 20TEST3\r\n"
    dpl += "Q0001\r\n"         # Quantity
    dpl += "E\r\n"             # End
    
    print("Full sequence like old software:")
    print(dpl)
    return dpl.encode('ascii')

def test_minimal_19():
    """Just the 19 format without extra setup"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "1911001008001 20TEST\r\n"
    dpl += "E\r\n"
    
    print("Minimal with 19 format")
    return dpl.encode('ascii')

def test_19_with_quotes():
    """19 format with quoted text"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += '1911001008001 20"TEST"\r\n'
    dpl += "E\r\n"
    
    print("19 format with quotes")
    return dpl.encode('ascii')

def test_19_smaller_row():
    """Try smaller row numbers"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "191100010001 20TEST\r\n"  # Row 10 instead of 1008
    dpl += "E\r\n"
    
    print("19 format with row 10")
    return dpl.encode('ascii')

def test_19_without_space():
    """Maybe space isn't needed"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "191100100800120TEST\r\n"  # No space before 20
    dpl += "E\r\n"
    
    print("19 format without space")
    return dpl.encode('ascii')

def test_format_12_that_worked():
    """Go back to format 12 that DID print text before"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += '12110000010100"TEST"\r\n'  # Format 8 from earlier that worked
    dpl += "E\r\n"
    
    print("Format 12 with quotes (worked before)")
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("TEST OLD SOFTWARE FORMAT")
    print("="*60)
    
    tests = [
        ("1. Full sequence from old software", test_full_sequence),
        ("2. Minimal 19 format", test_minimal_19),
        ("3. 19 format with quotes", test_19_with_quotes),
        ("4. 19 format smaller row", test_19_smaller_row),
        ("5. 19 format no space", test_19_without_space),
        ("6. Format 12 (worked before)", test_format_12_that_worked),
    ]
    
    for name, _ in tests:
        print(f"  {name}")
    
    while True:
        choice = input("\nChoice (1-6, q=quit): ").strip()
        
        if choice == 'q':
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(tests):
                name, func = tests[idx]
                cmd = func()
                result = send_to_usb_printer(cmd)
                print(f"\nSent: {'OK' if result else 'FAILED'}")
                print("Did it print text? (y/n)")
                ans = input().strip().lower()
                if ans == 'y':
                    print(f"✓ {name} WORKS!")
        except ValueError:
            pass

if __name__ == "__main__":
    main()
