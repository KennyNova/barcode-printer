#!/usr/bin/env python3
"""
Position Tool v2 - Fixed format based on testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def print_single(x, y, text):
    """Print single text - format that worked"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    # Try simpler format without the extra parameters
    dpl += f"12110{x:04d}{y:03d}{text}\r\n"
    dpl += "E\r\n"
    print(f"Command: 12110{x:04d}{y:03d}{text}")
    return dpl.encode('ascii')

def print_multi_v1(items):
    """Try multiple texts in one label - all commands before E"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    for x, y, text in items:
        dpl += f"12110{x:04d}{y:03d}{text}\r\n"
    dpl += "E\r\n"
    return dpl.encode('ascii')

def print_multi_v2(items):
    """Try with record numbers"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    for i, (x, y, text) in enumerate(items):
        dpl += f"{i+1}2110{x:04d}{y:03d}{text}\r\n"
    dpl += "E\r\n"
    return dpl.encode('ascii')

def print_multi_v3(items):
    """Try semicolon separated on one line"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    parts = []
    for x, y, text in items:
        parts.append(f"12110{x:04d}{y:03d}{text}")
    dpl += ";".join(parts) + "\r\n"
    dpl += "E\r\n"
    return dpl.encode('ascii')

def print_multi_v4(items):
    """Try without rotation/format prefix"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    for x, y, text in items:
        dpl += f"1{x:03d}{y:03d}{text}\r\n"
    dpl += "E\r\n"
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("POSITION TOOL v2 - Fixed Format")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  1. Print single text at X,Y")
        print("  2. Print 3 items (multi-text v1 - standard)")
        print("  3. Print 3 items (multi-text v2 - numbered)")
        print("  4. Print 3 items (multi-text v3 - semicolon)")
        print("  5. Print 3 items (multi-text v4 - short format)")
        print("  q. Quit")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == 'q':
            break
            
        elif choice == '1':
            try:
                x = int(input("X position (0-300): "))
                y = int(input("Y position (0-80): "))
                text = input("Text: ").strip()
                cmd = print_single(x, y, text)
                result = send_to_usb_printer(cmd)
                print("Sent!" if result else "Failed")
                
                ok = input("Did it print correctly without extra characters? (y/n): ")
                if ok.lower() == 'y':
                    print("✓ Single text format works!")
            except ValueError:
                print("Invalid input")
                
        elif choice in ['2', '3', '4', '5']:
            print("\nEnter positions for 3 items:")
            try:
                x1 = int(input("Item 1 (Price) X: "))
                x2 = int(input("Item 2 (Carat) X: "))
                x3 = int(input("Item 3 (SKU) X: "))
                y = int(input("Y position for all: "))
                
                items = [
                    (x1, y, "17600"),
                    (x2, y, "D=5.26"),
                    (x3, y, "MSD958"),
                ]
                
                if choice == '2':
                    cmd = print_multi_v1(items)
                    print("Using multi v1 (standard)")
                elif choice == '3':
                    cmd = print_multi_v2(items)
                    print("Using multi v2 (numbered)")
                elif choice == '4':
                    cmd = print_multi_v3(items)
                    print("Using multi v3 (semicolon)")
                else:
                    cmd = print_multi_v4(items)
                    print("Using multi v4 (short)")
                
                result = send_to_usb_printer(cmd)
                print("Sent!" if result else "Failed")
                
                print("\nWhat happened?")
                print("  a) ONE label with ALL 3 texts ✓")
                print("  b) ONE label with SOME texts")
                print("  c) MULTIPLE labels")
                print("  d) Nothing printed")
                ans = input("Answer (a/b/c/d): ").strip().lower()
                
                if ans == 'a':
                    print(f"\n✓✓✓ SUCCESS! Option {choice} works for multiple texts!")
                elif ans == 'b':
                    print("Partial success - some texts worked")
                elif ans == 'c':
                    print("Multiple labels - this format triggers new labels")
                    
            except ValueError:
                print("Invalid input")

if __name__ == "__main__":
    main()
