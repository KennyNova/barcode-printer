#!/usr/bin/env python3
"""
ZPL Mode Diagnostic
Maybe the printer is in ZPL emulation mode
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import send_to_usb_printer

def test_zpl_1():
    """Basic ZPL"""
    print("\n" + "="*50)
    print("ZPL TEST 1: Basic ZPL II")
    print("="*50)
    zpl = """^XA
^FO10,10^A0N,20,20^FDZPL1^FS
^XZ
"""
    print(f"Sending:\n{zpl}")
    return zpl.encode('ascii')

def test_zpl_2():
    """ZPL with different font"""
    print("\n" + "="*50)
    print("ZPL TEST 2: Different font")
    print("="*50)
    zpl = """^XA
^CF0,30
^FO10,10^FDZPL2^FS
^XZ
"""
    print(f"Sending:\n{zpl}")
    return zpl.encode('ascii')

def test_zpl_3():
    """ZPL minimal"""
    print("\n" + "="*50)
    print("ZPL TEST 3: Minimal")
    print("="*50)
    zpl = "^XA^FO10,10^FDZPL3^FS^XZ"
    print(f"Sending:\n{zpl}")
    return zpl.encode('ascii')

def test_epl_1():
    """EPL format"""
    print("\n" + "="*50)
    print("EPL TEST 1: Basic EPL")
    print("="*50)
    epl = """N
A10,10,0,1,1,1,N,"EPL1"
P1
"""
    print(f"Sending:\n{epl}")
    return epl.encode('ascii')

def test_epl_2():
    """EPL format 2"""
    print("\n" + "="*50)
    print("EPL TEST 2: EPL with setup")
    print("="*50)
    epl = """
N
q89
A10,10,0,1,1,1,N,"EPL2"
P1
"""
    print(f"Sending:\n{epl}")
    return epl.encode('ascii')

def test_raw_ascii():
    """Just raw ASCII text"""
    print("\n" + "="*50)
    print("RAW TEST: Just plain ASCII")
    print("="*50)
    text = "HELLO\r\n"
    print(f"Sending: {repr(text)}")
    return text.encode('ascii')

def test_dpl_alternate():
    """DPL alternate mode"""
    print("\n" + "="*50)
    print("DPL ALT: Alternate DPL structure")
    print("="*50)
    dpl = "\x02L\r\n"
    dpl += "H10\r\n"      # Heat
    dpl += "D11\r\n"      # Density  
    dpl += "S3\r\n"       # Speed
    dpl += "R10,10\r\n"   # Reference point
    dpl += "A1\r\n"       # Font A
    dpl += "DPLALT\r\n"   # Text data
    dpl += "E\r\n"
    print(f"Sending:\n{dpl}")
    return dpl.encode('ascii')

def test_fingerprint():
    """Fingerprint/Direct Protocol"""
    print("\n" + "="*50)
    print("FINGERPRINT: Direct Protocol")
    print("="*50)
    fp = 'PRPOS 10,10\r\n'
    fp += 'PRTXT "FINGER"\r\n'
    fp += 'PRINTFEED\r\n'
    print(f"Sending:\n{fp}")
    return fp.encode('ascii')

def main():
    print("="*60)
    print("ALTERNATE LANGUAGE DIAGNOSTIC")
    print("="*60)
    print("\nTrying ZPL, EPL, and other formats...\n")
    
    tests = [
        ("ZPL Basic", test_zpl_1),
        ("ZPL Font", test_zpl_2),
        ("ZPL Minimal", test_zpl_3),
        ("EPL Basic", test_epl_1),
        ("EPL Setup", test_epl_2),
        ("Raw ASCII", test_raw_ascii),
        ("DPL Alternate", test_dpl_alternate),
        ("Fingerprint", test_fingerprint),
    ]
    
    print("Available tests:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"  {i}. {name}")
    print("\nEnter test number, or 'q' to quit")
    
    while True:
        choice = input("\nTest (1-8, or q): ").strip().lower()
        
        if choice == 'q':
            break
            
        try:
            num = int(choice)
            if 1 <= num <= len(tests):
                name, func = tests[num-1]
                cmd = func()
                print(f"\nSending to printer... ", end="")
                result = send_to_usb_printer(cmd)
                print("SENT" if result else "FAILED")
                
                ans = input("\nDid text appear? (y/n): ").strip().lower()
                if ans == 'y':
                    print(f"\n✓✓✓ SUCCESS! '{name}' format works! ✓✓✓")
                    print(f"Your printer uses {name} format, not DPL!")
                    break
        except ValueError:
            pass

if __name__ == "__main__":
    main()
