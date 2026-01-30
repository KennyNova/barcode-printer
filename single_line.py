#!/usr/bin/env python3
"""
Single Line Printer - Since only one text command works per label
We'll combine info or test positioning
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def print_text(x, y, text):
    """Print single text using format 8 (the one that works)"""
    text_line = f'1211{x:04d}{y:03d}0100"{text}"'
    
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += text_line + "\r\n"
    dpl += "E\r\n"
    
    print(f"Command: {text_line}")
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("SINGLE LINE PRINTER")
    print("="*60)
    print("\nSince only 1 text line works, let's figure out:")
    print("1. The coordinate system")
    print("2. How to fit all info")
    
    while True:
        print("\n" + "-"*40)
        print("Options:")
        print("  1. Position test - print 'X' at coordinates")
        print("  2. Combined text - all info on one line")
        print("  3. Test negative coordinates")
        print("  4. Test large coordinates")
        print("  q. Quit")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == 'q':
            break
            
        elif choice == '1':
            try:
                print("\nX=0,Y=0 printed halfway. Let's map the label.")
                x = int(input("X position (-500 to 500): "))
                y = int(input("Y position (-100 to 100): "))
                cmd = print_text(x, y, "X")
                send_to_usb_printer(cmd)
                
                print("\nWhere did 'X' print?")
                print("  a) In the FRONT section (good!)")
                print("  b) In the BACK section")
                print("  c) In the LOOP (too far)")
                print("  d) Off the label / not visible")
                input("Result: ")
            except ValueError:
                print("Invalid input")
                
        elif choice == '2':
            try:
                print("\nWe'll combine all info into one line:")
                price = input("Price (e.g., 17600): ").strip() or "17600"
                carat = input("Carat (e.g., 5.26): ").strip() or "5.26"
                sku = input("SKU (e.g., MSD958009): ").strip() or "MSD958009"
                
                # Combined formats to try
                combined = f"{price} D={carat} {sku}"
                
                print(f"\nCombined text: {combined}")
                x = int(input("X position: "))
                y = int(input("Y position: "))
                
                cmd = print_text(x, y, combined)
                send_to_usb_printer(cmd)
                
                print("\nDid all info print on the label?")
            except ValueError:
                print("Invalid input")
                
        elif choice == '3':
            try:
                print("\nTrying negative X (might shift left):")
                x = int(input("Negative X (e.g., -100): "))
                y = int(input("Y: "))
                cmd = print_text(x, y, "NEG")
                send_to_usb_printer(cmd)
                print("\nWhere did it print?")
            except ValueError:
                print("Invalid input")
                
        elif choice == '4':
            try:
                print("\nTrying large X (might shift right):")
                x = int(input("Large X (e.g., 200, 300, 400): "))
                y = int(input("Y: "))
                cmd = print_text(x, y, "BIG")
                send_to_usb_printer(cmd)
                print("\nWhere did it print? (trying to find the front section)")
            except ValueError:
                print("Invalid input")

if __name__ == "__main__":
    main()
