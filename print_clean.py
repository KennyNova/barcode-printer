#!/usr/bin/env python3
"""
Clean Printer - Clear buffer and print properly
Uses formats 3 and 8 that worked
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def clear_printer():
    """Send commands to clear any pending jobs"""
    print("Clearing printer buffer...")
    # Cancel any pending job
    clear = "\x18"  # CAN - cancel
    clear += "\x02n\r\n"  # Clear image buffer
    send_to_usb_printer(clear.encode('ascii'))
    time.sleep(1)
    print("Buffer cleared.")

def print_format_3(x, y, text):
    """Format 3: 12110001001001001{text}"""
    # Pad x to 4 digits, y to 3 digits
    text_line = f"1211{x:04d}{y:03d}1001001{text}"
    
    dpl = "\x02L\r\n"  # Start label (no clear)
    dpl += "D11\r\n"
    dpl += text_line + "\r\n"
    dpl += "E\r\n"
    
    print(f"Sending: {text_line}")
    return dpl.encode('ascii')

def print_format_8(x, y, text):
    """Format 8: 121100010010100"{text}" (quoted)"""
    text_line = f'1211{x:04d}{y:03d}0100"{text}"'
    
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += text_line + "\r\n"
    dpl += "E\r\n"
    
    print(f"Sending: {text_line}")
    return dpl.encode('ascii')

def print_multi_format_8(items):
    """Multiple texts using format 8 (quoted)"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    
    for x, y, text in items:
        text_line = f'1211{x:04d}{y:03d}0100"{text}"'
        dpl += text_line + "\r\n"
        print(f"  {text_line}")
    
    dpl += "E\r\n"
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("CLEAN PRINTER TEST")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  0. Clear printer buffer (do this first!)")
        print("  1. Print single text (format 3)")
        print("  2. Print single text (format 8 - quoted)")
        print("  3. Print all 3 items (Price, Carat, SKU)")
        print("  q. Quit")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == 'q':
            break
            
        elif choice == '0':
            clear_printer()
            
        elif choice == '1':
            try:
                x = int(input("X position: "))
                y = int(input("Y position: "))
                text = input("Text: ").strip()
                cmd = print_format_3(x, y, text)
                send_to_usb_printer(cmd)
                print("\nDid it print ONE label with correct text? (y/n)")
            except ValueError:
                print("Invalid input")
                
        elif choice == '2':
            try:
                x = int(input("X position: "))
                y = int(input("Y position: "))
                text = input("Text: ").strip()
                cmd = print_format_8(x, y, text)
                send_to_usb_printer(cmd)
                print("\nDid it print ONE label with correct text? (y/n)")
            except ValueError:
                print("Invalid input")
                
        elif choice == '3':
            try:
                print("\nEnter X positions (items will be stacked vertically):")
                x1 = int(input("Price X: "))
                x2 = int(input("Carat X: "))  
                x3 = int(input("SKU X: "))
                y = int(input("Y position for all: "))
                
                items = [
                    (x1, y, "17600"),
                    (x2, y, "D=5.26"),
                    (x3, y, "MSD958"),
                ]
                
                print("\nSending all 3 items:")
                cmd = print_multi_format_8(items)
                send_to_usb_printer(cmd)
                
                print("\nResult:")
                print("  a) ONE label with all 3 texts ✓")
                print("  b) Multiple labels")
                print("  c) Missing some text")
                ans = input("What happened? (a/b/c): ")
                
                if ans.lower() == 'a':
                    print("\n✓✓✓ SUCCESS! We found the working format!")
                    
            except ValueError:
                print("Invalid input")

if __name__ == "__main__":
    main()
