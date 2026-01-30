#!/usr/bin/env python3
"""
Force Printer Configuration
Sends raw system commands to force the printer into the correct mode
"""

from jewelry_tag_printer import send_to_usb_printer

def configure_printer():
    # Force system configuration
    # SOH = \x01
    
    cmds = []
    
    # Set to GAP sensing mode
    cmds.append("\x01KcG")       
    
    # Set Label Length to 3.5 inches (Total length)
    # The printer needs to know the FULL length including loop
    # 3.5" * 203 DPI = ~710 dots
    cmds.append("\x01Kc710")     
    
    # Set Label Width (0.44")
    cmds.append("\x01KW089")
    
    # Store settings
    cmds.append("\x01Ks")
    
    # Calibrate now
    cmds.append("\x02e")         # Autosense/Calibrate
    
    command = "\r\n".join(cmds).encode('ascii')
    
    print("Sending configuration commands...")
    success = send_to_usb_printer(command)
    
    if success:
        print("✓ Configuration sent!")
        print("  Printer should feed a few labels to calibrate.")
        print("  Wait 10 seconds, then try printing again.")

if __name__ == "__main__":
    configure_printer()
