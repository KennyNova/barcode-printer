#!/usr/bin/env python3
"""
Position Tool - Find the right X,Y coordinates
The text format works, we just need to find the right positions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def print_at_position(x, y, text="X"):
    """Print text at specific X,Y position"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    # Format: 121100XXXYYYHHWWFDATA
    # XXX = X position (3 digits)
    # YYY = Y position (3 digits, but we use 2 with leading 0)
    dpl += f"12110{x:04d}{y:03d}00100{text}\r\n"
    dpl += "E\r\n"
    return dpl.encode('ascii')

def print_grid():
    """Print a grid of markers to map out the label"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    
    # Print markers at different positions
    # This will help us see where things land on the label
    positions = [
        (0, 0, "A"),      # Origin
        (50, 0, "B"),     # X=50
        (100, 0, "C"),    # X=100
        (150, 0, "D"),    # X=150
        (200, 0, "E"),    # X=200
        (0, 20, "1"),     # Y=20
        (0, 40, "2"),     # Y=40
        (0, 60, "3"),     # Y=60
    ]
    
    for x, y, marker in positions:
        dpl += f"12110{x:04d}{y:03d}00100{marker}\r\n"
    
    dpl += "E\r\n"
    return dpl.encode('ascii')

def print_test_data(x_price, x_carat, x_item, y_all):
    """Print actual test data at specified positions"""
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    
    dpl += f"12110{x_price:04d}{y_all:03d}0010017600\r\n"
    dpl += f"12110{x_carat:04d}{y_all:03d}00100D=5.26\r\n"
    dpl += f"12110{x_item:04d}{y_all:03d}00100MSD958\r\n"
    
    dpl += "E\r\n"
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("POSITION FINDER TOOL")
    print("="*60)
    print("\nThis will help find the correct X,Y positions for your label.")
    print("The barbell label is narrow, so Y should be small (0-80).")
    print()
    
    while True:
        print("\nOptions:")
        print("  1. Print GRID (markers A,B,C,D,E at X positions; 1,2,3 at Y positions)")
        print("  2. Print single marker at custom X,Y")
        print("  3. Print Price/Carat/Item at custom X positions")
        print("  4. Quick test - all data at X=10,50,100 Y=10")
        print("  q. Quit")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == 'q':
            break
            
        elif choice == '1':
            print("\nPrinting grid of markers...")
            print("A=X0, B=X50, C=X100, D=X150, E=X200")
            print("1=Y20, 2=Y40, 3=Y60")
            cmd = print_grid()
            send_to_usb_printer(cmd)
            print("\nLook at the label - which markers are in the FRONT section?")
            print("(The front section is where product info should go)")
            
        elif choice == '2':
            try:
                x = int(input("X position (0-300): "))
                y = int(input("Y position (0-80): "))
                text = input("Text to print (default 'X'): ").strip() or "X"
                cmd = print_at_position(x, y, text)
                send_to_usb_printer(cmd)
                print(f"\nPrinted '{text}' at X={x}, Y={y}")
            except ValueError:
                print("Invalid number")
                
        elif choice == '3':
            try:
                print("\nEnter X positions for each field (they'll all be on same Y)")
                x_price = int(input("Price X position: "))
                x_carat = int(input("Carat X position: "))
                x_item = int(input("Item# X position: "))
                y = int(input("Y position for all (0-80): "))
                cmd = print_test_data(x_price, x_carat, x_item, y)
                send_to_usb_printer(cmd)
                print("\nPrinted: 17600, D=5.26, MSD958")
            except ValueError:
                print("Invalid number")
                
        elif choice == '4':
            print("\nPrinting quick test at X=10,50,100 Y=10...")
            cmd = print_test_data(10, 50, 100, 10)
            send_to_usb_printer(cmd)
            print("Printed: 17600 at X=10, D=5.26 at X=50, MSD958 at X=100")
            print("\nIs this in the FRONT section of the label?")

if __name__ == "__main__":
    main()
