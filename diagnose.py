#!/usr/bin/env python3
"""
Printer Diagnostic Tool
Tests different DPL command formats to find what works
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def test_format_1():
    """Original format"""
    print("\n" + "="*50)
    print("TEST 1: Original DPL format")
    print("="*50)
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "121100010005001001\r\n"  # Just print "1"
    dpl += "E\r\n"
    print(f"Sending:\n{repr(dpl)}")
    return dpl.encode('ascii')

def test_format_2():
    """Simpler text command"""
    print("\n" + "="*50)
    print("TEST 2: Simpler text format")
    print("="*50)
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "1X1100010005001002\r\n"  # Try with X
    dpl += "E\r\n"
    print(f"Sending:\n{repr(dpl)}")
    return dpl.encode('ascii')

def test_format_3():
    """EPL-style ASCII text command"""
    print("\n" + "="*50)
    print("TEST 3: EPL-style text")
    print("="*50)
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += 'A10,10,0,1,1,1,N,"3"\r\n'  # EPL text command
    dpl += "E\r\n"
    print(f"Sending:\n{repr(dpl)}")
    return dpl.encode('ascii')

def test_format_4():
    """DPL with quoted text"""
    print("\n" + "="*50)
    print("TEST 4: DPL with quoted text")
    print("="*50)
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += '1211000100050"4"\r\n'  # Quoted text
    dpl += "E\r\n"
    print(f"Sending:\n{repr(dpl)}")
    return dpl.encode('ascii')

def test_format_5():
    """Minimal - just clear and feed"""
    print("\n" + "="*50)
    print("TEST 5: Just feed one label (no text)")
    print("="*50)
    dpl = "\x02n\r\n"
    dpl += "\x02L\r\n"
    dpl += "E\r\n"
    print(f"Sending:\n{repr(dpl)}")
    return dpl.encode('ascii')

def test_format_6():
    """Try SOH format for label"""
    print("\n" + "="*50)
    print("TEST 6: SOH format")
    print("="*50)
    dpl = "\x01#\r\n"  # SOH # = reset
    dpl += "\x02L\r\n"
    dpl += "D11\r\n"
    dpl += "191100010010101016\r\n"  # Format 9
    dpl += "E\r\n"
    print(f"Sending:\n{repr(dpl)}")
    return dpl.encode('ascii')

def main():
    print("="*60)
    print("DATAMAX PRINTER DIAGNOSTIC")
    print("="*60)
    print("\nThis will test different DPL command formats.")
    print("Press PAUSE on printer between tests if needed.\n")
    
    tests = [
        ("Format 1 - Original DPL", test_format_1),
        ("Format 2 - With X marker", test_format_2),
        ("Format 3 - EPL style", test_format_3),
        ("Format 4 - Quoted text", test_format_4),
        ("Format 5 - Just feed (no text)", test_format_5),
        ("Format 6 - SOH format", test_format_6),
    ]
    
    print("Which test to run?")
    for i, (name, _) in enumerate(tests, 1):
        print(f"  {i}. {name}")
    print("  0. Run ALL tests (with pauses)")
    print("  q. Quit")
    
    while True:
        choice = input("\nEnter choice (1-6, 0, or q): ").strip().lower()
        
        if choice == 'q':
            print("Goodbye!")
            break
        
        if choice == '0':
            # Run all tests
            for name, test_func in tests:
                cmd = test_func()
                print(f"\nSend this test? (y/n): ", end="")
                if input().strip().lower() == 'y':
                    result = send_to_usb_printer(cmd)
                    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
                    print("\nCheck the printer. Press Enter when ready for next test...")
                    input()
        elif choice in '123456':
            idx = int(choice) - 1
            name, test_func = tests[idx]
            cmd = test_func()
            print(f"\nSend to printer? (y/n): ", end="")
            if input().strip().lower() == 'y':
                result = send_to_usb_printer(cmd)
                print(f"Result: {'SUCCESS' if result else 'FAILED'}")
                print("\nWhat happened?")
                print("  a) Printed ONE label with text")
                print("  b) Printed ONE label, NO text")
                print("  c) Printed MULTIPLE labels")
                print("  d) Nothing happened")
                feedback = input("Enter a/b/c/d: ").strip().lower()
                
                if feedback == 'a':
                    print(f"\n✓ SUCCESS! Format '{name}' works!")
                    print("Use this format for your labels.")
                elif feedback == 'b':
                    print("Label count OK, but text command needs adjustment.")
                elif feedback == 'c':
                    print("Multiple labels = label length/gap detection issue.")
                elif feedback == 'd':
                    print("Command may not have been received.")
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
