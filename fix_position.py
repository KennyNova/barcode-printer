#!/usr/bin/env python3
"""
Fix Position - Try swapping X/Y and using reference point
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def test_swapped(x, y, text):
    """Try with X and Y swapped in the format"""
    # Original: 1211{x:04d}{y:03d}
    # Swapped:  1211{y:04d}{x:03d}
    text_line = f'1211{y:04d}{x:03d}0100"{text}"'
    
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += text_line + "\r\n"
    dpl += "E\r\n"
    
    print(f"Swapped format: {text_line}")
    return dpl.encode('ascii')

def test_reference_point(ref_x, ref_y, x, y, text):
    """Set a reference point before printing"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"R{ref_x:04d},{ref_y:04d}\r\n"  # Reference point command
    dpl += f'1211{x:04d}{y:03d}0100"{text}"\r\n'
    dpl += "E\r\n"
    
    print(f"Reference: R{ref_x},{ref_y}")
    return dpl.encode('ascii')

def test_row_col_format(row, col, text):
    """Maybe it's row,column not x,y"""
    text_line = f'1211{col:04d}{row:03d}0100"{text}"'
    
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += text_line + "\r\n"
    dpl += "E\r\n"
    
    print(f"Col,Row format: {text_line}")
    return dpl.encode('ascii')

def test_origin_command(orig_x, x, y, text):
    """Try setting origin with different command"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"O{orig_x:04d}\r\n"  # Origin offset
    dpl += f'1211{x:04d}{y:03d}0100"{text}"\r\n'
    dpl += "E\r\n"
    
    print(f"Origin offset: {orig_x}")
    return dpl.encode('ascii')

def test_column_offset(col_offset, y, text):
    """Try C command for column"""
    dpl = "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += f"C{col_offset:04d}\r\n"  # Column offset
    dpl += f'121100000{y:03d}0100"{text}"\r\n'
    dpl += "E\r\n"
    
    print(f"Column offset: {col_offset}")
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("FIX HORIZONTAL POSITION")
    print("="*60)
    print("\nY works but X doesn't. Let's find the right way to move horizontally.\n")
    
    while True:
        print("\nOptions:")
        print("  1. Swap X and Y (maybe they're reversed)")
        print("  2. Set reference point (R command)")
        print("  3. Try row,col instead of x,y")
        print("  4. Set origin offset (O command)")
        print("  5. Column offset (C command)")
        print("  6. Print combined text at working Y positions")
        print("  q. Quit")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == 'q':
            break
            
        elif choice == '1':
            print("\nSwapping X and Y in the command...")
            x = int(input("Value for horizontal (was Y): "))
            y = int(input("Value for vertical (was X): "))
            cmd = test_swapped(x, y, "SWAP")
            send_to_usb_printer(cmd)
            print("\nDid changing first value move it horizontally?")
            
        elif choice == '2':
            print("\nSetting reference point...")
            ref_x = int(input("Reference X (try -200, -300, -400): "))
            ref_y = int(input("Reference Y (try 0): "))
            x = int(input("Text X (try 0): "))
            y = int(input("Text Y (try 10): "))
            cmd = test_reference_point(ref_x, ref_y, x, y, "REF")
            send_to_usb_printer(cmd)
            print("\nDid it move toward the front section?")
            
        elif choice == '3':
            print("\nUsing column, row (common in label printers)...")
            col = int(input("Column (horizontal, try 0, 50, 100): "))
            row = int(input("Row (vertical, try 10): "))
            cmd = test_row_col_format(row, col, "COLROW")
            send_to_usb_printer(cmd)
            print("\nDid column value move it horizontally?")
            
        elif choice == '4':
            print("\nSetting origin offset...")
            orig = int(input("Origin X offset (try -200, -300): "))
            y = int(input("Y position: "))
            cmd = test_origin_command(orig, 0, y, "ORIG")
            send_to_usb_printer(cmd)
            print("\nDid it shift the print position?")
            
        elif choice == '5':
            print("\nColumn offset command...")
            col = int(input("Column offset (try -200, -300, -400): "))
            y = int(input("Y position: "))
            cmd = test_column_offset(col, y, "COL")
            send_to_usb_printer(cmd)
            print("\nDid it move horizontally?")
            
        elif choice == '6':
            print("\nSince only Y works, let's print stacked vertically...")
            print("We'll print on different Y values (vertical stacking)")
            
            y1 = int(input("Y for Price (try 5): "))
            y2 = int(input("Y for Carat (try 25): "))
            y3 = int(input("Y for SKU (try 45): "))
            
            price = input("Price (default 17600): ") or "17600"
            carat = input("Carat (default D=5.26): ") or "D=5.26"
            sku = input("SKU (default MSD958): ") or "MSD958"
            
            # Print three separate labels with different Y positions
            # to see where each would go
            for y, text in [(y1, price), (y2, carat), (y3, sku)]:
                print(f"\nPrinting '{text}' at Y={y}...")
                text_line = f'121100000{y:03d}0100"{text}"'
                dpl = "\x02L\r\n"
                dpl += "D11\r\n"
                dpl += text_line + "\r\n"
                dpl += "E\r\n"
                send_to_usb_printer(dpl.encode('ascii'))
                input("Press Enter for next...")

if __name__ == "__main__":
    main()
