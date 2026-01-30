#!/usr/bin/env python3
"""
Format Finder - Test exact DPL text format variations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def send_test(description, text_line):
    """Send a test with specific text line format"""
    print(f"\n{'='*50}")
    print(f"TEST: {description}")
    print(f"Text line: {text_line}")
    print('='*50)
    
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += text_line + "\r\n"
    dpl += "E\r\n"
    
    result = send_to_usb_printer(dpl.encode('ascii'))
    return result

def main():
    print("="*60)
    print("FORMAT FINDER")
    print("="*60)
    print("\nWe'll test variations to find the exact format.")
    print("Looking for one that prints 'TEST' cleanly.\n")
    
    # Different format variations - X=10, Y=10, text="TEST"
    formats = [
        ("Original that showed 00", "121100010010001001TEST"),
        ("With 100 only", "12110001001001001TEST"),  
        ("With just font", "121100010010100TEST"),
        ("Shorter params", "1211000100101TEST"),
        ("Even shorter", "12110001001TEST"),
        ("Minimal", "121100010010TEST"),
        ("With spaces", "12110 0010 010 1 TEST"),
        ("Quoted text", '121100010010100"TEST"'),
        ("Different rotation", "111100010010100TEST"),
        ("Rotation 0", "101100010010100TEST"),
        ("No rotation prefix", "11100010010100TEST"),
        ("Just position+text", "00100101TEST"),
        ("Simple format", "1,10,10,TEST"),
    ]
    
    for i, (desc, fmt) in enumerate(formats, 1):
        print(f"{i:2}. {desc}")
    
    print("\nEnter test number (1-13) or 'q' to quit")
    print("We want one that prints just 'TEST' with no extra characters.\n")
    
    while True:
        choice = input("Test #: ").strip()
        
        if choice.lower() == 'q':
            break
            
        try:
            num = int(choice)
            if 1 <= num <= len(formats):
                desc, fmt = formats[num-1]
                send_test(desc, fmt)
                
                print("\nWhat printed?")
                print("  a) Just 'TEST' perfectly ✓")
                print("  b) 'TEST' with extra characters before/after")
                print("  c) Nothing / blank label")
                print("  d) Error or multiple labels")
                ans = input("Result (a/b/c/d): ").strip().lower()
                
                if ans == 'a':
                    print(f"\n✓✓✓ PERFECT! Format #{num} works!")
                    print(f"Format: {fmt}")
                    print("\nNow we can use this format for all text!")
                    break
                elif ans == 'b':
                    extra = input("What extra characters? ")
                    print(f"Noted: printed extra '{extra}'")
        except ValueError:
            print("Enter a number 1-13")

if __name__ == "__main__":
    main()
