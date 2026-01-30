#!/usr/bin/env python3
"""
Text Command Diagnostic
We know ONE label works - now find the right TEXT command
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def base_label(text_commands):
    """Wrap text commands in label start/end"""
    dpl = "\x02n\r\n"      # Clear buffer
    dpl += "\x02L\r\n"     # Start label
    dpl += "D11\r\n"       # Density
    dpl += text_commands
    dpl += "E\r\n"         # End
    return dpl.encode('ascii')

def test_text_1():
    """DPL scalable/smooth font"""
    print("\n" + "="*50)
    print("TEXT TEST 1: Scalable font ySnnnmmmhhhwwwDATA")
    print("="*50)
    # y=rotation, S=smooth, nnn=row, mmm=col, hhh=height, www=width
    text = "ySS000010010010010TEST1\r\n"
    print(f"Text command: {text}")
    return base_label(text)

def test_text_2():
    """DPL Internal bitmap font - format A"""
    print("\n" + "="*50)
    print("TEXT TEST 2: Bitmap font 1annnmmmhwfDATA")
    print("="*50)
    # 1=text, a=rotation(1-4), nnn=row, mmm=col, h=hmag, w=wmag, f=font
    text = "110010010110TEST2\r\n"
    print(f"Text command: {text}")
    return base_label(text)

def test_text_3():
    """DPL format with font ID"""
    print("\n" + "="*50)
    print("TEXT TEST 3: With font ID")
    print("="*50)
    text = "1100100101109TEST3\r\n"  # font 9
    print(f"Text command: {text}")
    return base_label(text)

def test_text_4():
    """DPL older format"""
    print("\n" + "="*50)
    print("TEXT TEST 4: Older DPL format")
    print("="*50)
    text = "1010010111TEST4\r\n"
    print(f"Text command: {text}")
    return base_label(text)

def test_text_5():
    """Alphanumeric field"""
    print("\n" + "="*50)
    print("TEXT TEST 5: Alpha field with quotes")
    print("="*50)
    text = 'A0101009011\"TEST5\"\r\n'
    print(f"Text command: {text}")
    return base_label(text)

def test_text_6():
    """Simple line format"""
    print("\n" + "="*50)
    print("TEXT TEST 6: Line format")
    print("="*50)
    text = "100100TEST6\r\n"
    print(f"Text command: {text}")
    return base_label(text)

def test_text_7():
    """DPL II format"""
    print("\n" + "="*50)
    print("TEXT TEST 7: DPL II with semicolons")
    print("="*50)
    text = "TEXT,10,10,0,0,1,1,TEST7\r\n"
    print(f"Text command: {text}")
    return base_label(text)

def test_text_8():
    """Direct coordinates"""
    print("\n" + "="*50)
    print("TEXT TEST 8: Simple X,Y format")
    print("="*50)
    # Try various simple formats
    text = "10,10,TEST8\r\n"
    print(f"Text command: {text}")
    return base_label(text)

def test_text_9():
    """Hex position format"""
    print("\n" + "="*50)
    print("TEXT TEST 9: Padded numbers")
    print("="*50)
    text = "1 010 010 1 1 0 TEST9\r\n"
    print(f"Text command: {text}")
    return base_label(text)

def test_text_10():
    """Font download reference format"""
    print("\n" + "="*50)
    print("TEXT TEST 10: Y command format")
    print("="*50)
    text = "y010010TEST10\r\n"
    print(f"Text command: {text}")
    return base_label(text)

def main():
    print("="*60)
    print("TEXT COMMAND DIAGNOSTIC")
    print("="*60)
    print("\nWe know ONE label prints. Now finding correct TEXT format.\n")
    
    tests = [
        test_text_1, test_text_2, test_text_3, test_text_4, test_text_5,
        test_text_6, test_text_7, test_text_8, test_text_9, test_text_10
    ]
    
    print("Tests 1-10 available. Enter number (1-10) or 'q' to quit.")
    print("Look for which test prints visible text!\n")
    
    while True:
        choice = input("Test number (1-10, or q): ").strip().lower()
        
        if choice == 'q':
            break
            
        try:
            num = int(choice)
            if 1 <= num <= 10:
                cmd = tests[num-1]()
                print(f"\nSending... ", end="")
                result = send_to_usb_printer(cmd)
                print("SENT" if result else "FAILED")
                
                print("\nDid text appear on the label? (y/n): ", end="")
                if input().strip().lower() == 'y':
                    print(f"\n✓ SUCCESS! Test {num} works!")
                    print("This is the correct text format for your printer.")
                    break
            else:
                print("Enter 1-10")
        except ValueError:
            print("Enter a number 1-10")

if __name__ == "__main__":
    main()
