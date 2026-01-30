#!/usr/bin/env python3
"""
Alternative Print Method (EPL)
Try this if DPL isn't working right
"""

from jewelry_tag_printer import send_to_usb_printer

def print_epl_test():
    # EPL2 Command
    # N = Clear buffer
    # q = Label width (dots)
    # Q = Label height, gap (dots)
    
    epl = []
    epl.append("N")              # Clear
    epl.append("q89")            # Width 89 dots (7/16")
    epl.append("Q710,24")        # Length 710 dots (3.5"), 24 dot gap
    
    # Text: A = ASCII text
    # p1, p2, rot, font, mul_h, mul_w, rev, "DATA"
    epl.append('A10,10,0,2,1,1,N,"TEST PRINT"')
    epl.append('A10,40,0,2,1,1,N,"PRICE 100"')
    
    epl.append("P1")             # Print 1 label
    
    command = "\n".join(epl).encode('ascii')
    
    print("Sending EPL test...")
    print(command.decode('ascii'))
    send_to_usb_printer(command)

if __name__ == "__main__":
    print_epl_test()
