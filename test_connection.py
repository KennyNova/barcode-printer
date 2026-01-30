#!/usr/bin/env python3
"""
Printer Connection Diagnostic
Finds the right printer and tests connection
"""

import sys
import win32print

def list_and_test_printers():
    print("Scanning printers...")
    printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
    
    datamax_printers = []
    
    for p in printers:
        print(f"Found: {p}")
        if "datamax" in p.lower() or "e-4205" in p.lower():
            datamax_printers.append(p)
            
    print("\n" + "="*40)
    
    if not datamax_printers:
        print("✗ No Datamax printers found!")
        print("Please verify the printer is installed in Windows 'Devices and Printers'")
        return
        
    for p_name in datamax_printers:
        print(f"Testing connection to: {p_name}")
        try:
            hPrinter = win32print.OpenPrinter(p_name)
            try:
                # Try to send a simple feed command
                # DPL Feed: <STX>f
                cmd = b"\x02f\r\n" 
                
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Connection Test", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    bytes_written = win32print.WritePrinter(hPrinter, cmd)
                    win32print.EndPagePrinter(hPrinter)
                    print(f"  ✓ Sent {bytes_written} bytes successfully")
                    print("  --> DID THE PRINTER FEED A LABEL? (Yes/No)")
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            
    print("\n" + "="*40)
    print("If the printer fed a label, use that EXACT printer name in config.py")

if __name__ == "__main__":
    list_and_test_printers()
