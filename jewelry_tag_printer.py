#!/usr/bin/env python3
"""
Jewelry Tag Printer for Datamax O'Neil E-Class Mark III
Prints item details on front, barcode on back of jewelry tags (42mm x 26mm)
"""

import csv
import os
import socket
import sys
from datetime import datetime
from typing import Optional
import argparse

# Try to import barcode library for preview generation
try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_PREVIEW_AVAILABLE = True
except ImportError:
    BARCODE_PREVIEW_AVAILABLE = False

# Try to load configuration from config.py
try:
    from config import (
        PRINTER_IP, PRINTER_PORT, CSV_FILE, PRINTER_DPI,
        LABEL_WIDTH_MM, LABEL_HEIGHT_MM
    )
    DPI = PRINTER_DPI
except ImportError:
    # Default configuration if config.py not found
    PRINTER_IP = "192.168.1.100"  # Change to your printer's IP
    PRINTER_PORT = 9100           # Default raw printing port
    CSV_FILE = "print_history.csv"
    DPI = 203                     # E-Class Mark III standard DPI
    LABEL_WIDTH_MM = 42
    LABEL_HEIGHT_MM = 26

# Label dimensions in dots (203 DPI = 8 dots/mm)
DOTS_PER_MM = DPI / 25.4
LABEL_WIDTH_DOTS = int(LABEL_WIDTH_MM * DOTS_PER_MM)
LABEL_HEIGHT_DOTS = int(LABEL_HEIGHT_MM * DOTS_PER_MM)


def generate_item_barcode(item_number: str) -> str:
    """Generate Code 128 barcode data for the item number."""
    # Clean the item number for barcode use
    return item_number.replace(" ", "").upper()


def create_dpl_command(item_number: str, price: float, carat_weight: float, 
                        gold_karat: int) -> bytes:
    """
    Create DPL (Datamax Programming Language) command for the jewelry tag.
    
    Front side: Price, D=carat, Item number (rotated 90°)
    Back side: Barcode (printed on tail portion that folds over)
    """
    barcode_data = generate_item_barcode(item_number)
    
    # Format values for display (matching the tag image)
    price_str = f"{int(price)}" if price == int(price) else f"{price:.2f}"
    carat_str = f"D={carat_weight:.2f}"
    
    # DPL Command structure for Datamax E-Class
    dpl = []
    
    # Initialize label
    dpl.append("\x02L")           # STX + Start label format
    dpl.append("D11")             # Density
    dpl.append("H15")             # Heat setting  
    dpl.append(f"PW{LABEL_HEIGHT_DOTS}")  # Print width (swapped due to rotation)
    dpl.append(f"LL{LABEL_WIDTH_DOTS}")   # Label length
    
    # FRONT SIDE - Text rotated 90° (rotation 1 = 90° clockwise)
    # Format: 1YRRRXXXX YYYY fffFONTdata
    # Y=rotation(1=90°), R=reverse, X=column, Y=row, f=font magnification
    
    # Price - top line (largest)
    # Position from right edge, text reads bottom to top when tag hangs
    dpl.append(f"141100015005000{price_str}")
    
    # D=carat - middle line  
    dpl.append(f"131100095005000{carat_str}")
    
    # Item number - bottom line
    dpl.append(f"121100160005000{item_number}")
    
    # BACK SIDE - Barcode on the tail portion (folds behind)
    # This prints on the extended tail area that wraps around
    # Barcode rotated 90° to match orientation, positioned on tail
    dpl.append(f"1B1300250010030h040w02c{barcode_data}")
    
    # End and print
    dpl.append("E")
    
    return "\r\n".join(dpl).encode('ascii')


def create_zpl_command(item_number: str, price: float, carat_weight: float,
                       gold_karat: int) -> bytes:
    """
    Create ZPL command (if printer supports ZPL emulation).
    Front: Price, D=carat, Item number (rotated)
    Back: Barcode on tail
    """
    barcode_data = generate_item_barcode(item_number)
    
    price_str = f"{int(price)}" if price == int(price) else f"{price:.2f}"
    carat_str = f"D={carat_weight:.2f}"
    
    # ZPL with rotation (^FWR = rotate 90°)
    zpl = f"""^XA
^PW{LABEL_HEIGHT_DOTS}
^LL{LABEL_WIDTH_DOTS}
^FWR
^CF0,32
^FO20,30^FD{price_str}^FS
^CF0,28
^FO65,30^FD{carat_str}^FS
^CF0,24
^FO110,30^FD{item_number}^FS
^FWR
^BY2,2,40
^FO160,200^BC,40,N,N,N^FD{barcode_data}^FS
^XZ"""
    return zpl.strip().encode('ascii')


def create_epl_command(item_number: str, price: float, carat_weight: float,
                       gold_karat: int) -> bytes:
    """
    Create EPL2 command (alternative format supported by some Datamax printers).
    """
    barcode_data = generate_item_barcode(item_number)
    
    price_str = f"{int(price)}" if price == int(price) else f"{price:.2f}"
    carat_str = f"D={carat_weight:.2f}"
    
    epl = []
    epl.append("N")  # Clear buffer
    epl.append(f"q{LABEL_HEIGHT_DOTS}")  # Label width
    epl.append(f"Q{LABEL_WIDTH_DOTS},24")  # Label height, gap
    
    # Rotated text (R270 = text reads upward when label hangs)
    # A command: Ax,y,rotation,font,h_mult,v_mult,N/R,"data"
    epl.append(f'A30,180,1,4,1,2,N,"{price_str}"')      # Price
    epl.append(f'A70,180,1,3,1,1,N,"{carat_str}"')      # D=carat
    epl.append(f'A105,180,1,3,1,1,N,"{item_number}"')   # Item number
    
    # Barcode on back/tail area
    epl.append(f'B180,50,1,1,2,3,40,N,"{barcode_data}"')
    
    epl.append("P1")  # Print 1 label
    
    return "\r\n".join(epl).encode('ascii')


def send_to_printer(command: bytes, printer_ip: str = PRINTER_IP, 
                    printer_port: int = PRINTER_PORT) -> bool:
    """Send print command to the Datamax printer via TCP/IP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((printer_ip, printer_port))
            sock.sendall(command)
            print(f"✓ Print command sent to {printer_ip}:{printer_port}")
            return True
    except socket.timeout:
        print(f"✗ Connection timeout to printer at {printer_ip}:{printer_port}")
        return False
    except ConnectionRefusedError:
        print(f"✗ Connection refused by printer at {printer_ip}:{printer_port}")
        return False
    except Exception as e:
        print(f"✗ Failed to send to printer: {e}")
        return False


def send_to_usb_printer(command: bytes, printer_name: Optional[str] = None) -> bool:
    """
    Send print command to USB-connected printer.
    Works on Windows with the printer shared name.
    """
    if sys.platform == "win32":
        try:
            import win32print
            if printer_name is None:
                printer_name = win32print.GetDefaultPrinter()
            
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Jewelry Tag", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, command)
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            print(f"✓ Print command sent to USB printer: {printer_name}")
            return True
        except ImportError:
            print("✗ win32print not available. Install pywin32: pip install pywin32")
            return False
        except Exception as e:
            print(f"✗ Failed to send to USB printer: {e}")
            return False
    else:
        # On macOS/Linux, try using lpr command
        try:
            import subprocess
            process = subprocess.Popen(
                ['lpr', '-l'],  # -l for raw mode
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(input=command)
            if process.returncode == 0:
                print("✓ Print command sent via lpr")
                return True
            else:
                print(f"✗ lpr failed: {stderr.decode()}")
                return False
        except FileNotFoundError:
            print("✗ lpr command not found")
            return False
        except Exception as e:
            print(f"✗ Failed to send via lpr: {e}")
            return False


def save_to_csv(item_number: str, price: float, carat_weight: float,
                gold_karat: int, success: bool, csv_path: str = CSV_FILE):
    """Save print record to CSV file."""
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if new file
        if not file_exists:
            writer.writerow([
                'Timestamp', 'Item Number', 'Price', 'Carat Weight', 
                'Gold Karat', 'Barcode Data', 'Print Status'
            ])
        
        barcode_data = generate_item_barcode(item_number)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'SUCCESS' if success else 'FAILED'
        
        writer.writerow([
            timestamp, item_number, f"{price:.2f}", f"{carat_weight:.2f}",
            gold_karat, barcode_data, status
        ])
    
    print(f"✓ Record saved to {csv_path}")


def generate_barcode_preview(item_number: str, output_dir: str = "barcodes"):
    """Generate a barcode image preview (optional)."""
    if not BARCODE_PREVIEW_AVAILABLE:
        print("ℹ Barcode preview not available. Install: pip install python-barcode[images]")
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    barcode_data = generate_item_barcode(item_number)
    
    # Generate Code 128 barcode
    code128 = barcode.get_barcode_class('code128')
    barcode_instance = code128(barcode_data, writer=ImageWriter())
    
    filename = os.path.join(output_dir, f"barcode_{barcode_data}")
    saved_path = barcode_instance.save(filename)
    print(f"✓ Barcode preview saved: {saved_path}")
    return saved_path


def print_tag(item_number: str, price: float, carat_weight: float,
              gold_karat: int,
              printer_ip: Optional[str] = None,
              use_usb: bool = False,
              use_zpl: bool = False,
              use_epl: bool = False,
              dry_run: bool = False) -> bool:
    """
    Main function to print a jewelry tag.
    
    Args:
        item_number: Unique item identifier (e.g., MSD958009)
        price: Selling price (e.g., 17600)
        carat_weight: Diamond carat weight (e.g., 5.26)
        gold_karat: Gold karat (e.g., 14, 18, 24)
        printer_ip: Printer IP address (optional, uses default)
        use_usb: Use USB connection instead of network
        use_zpl: Use ZPL commands instead of DPL
        use_epl: Use EPL commands instead of DPL
        dry_run: Don't actually print, just generate commands
    
    Returns:
        True if print was successful
    """
    print("\n" + "="*50)
    print("JEWELRY TAG PRINT JOB")
    print("="*50)
    print(f"Item Number:  {item_number}")
    print(f"Price:        {int(price) if price == int(price) else price}")
    print(f"Carat Weight: D={carat_weight:.2f}")
    print(f"Gold Karat:   {gold_karat}K")
    print(f"Barcode:      {generate_item_barcode(item_number)}")
    print("="*50)
    
    # Generate print command
    if use_zpl:
        command = create_zpl_command(item_number, price, carat_weight, gold_karat)
        print("Using ZPL format")
    elif use_epl:
        command = create_epl_command(item_number, price, carat_weight, gold_karat)
        print("Using EPL format")
    else:
        command = create_dpl_command(item_number, price, carat_weight, gold_karat)
        print("Using DPL format")
    
    if dry_run:
        print("\n[DRY RUN] Print command generated:")
        print(command.decode('ascii'))
        success = True
    elif use_usb:
        success = send_to_usb_printer(command)
    else:
        ip = printer_ip or PRINTER_IP
        success = send_to_printer(command, ip)
    
    # Save to CSV
    save_to_csv(item_number, price, carat_weight, gold_karat, success)
    
    # Generate barcode preview image
    generate_barcode_preview(item_number)
    
    return success


def interactive_mode():
    """Run in interactive mode, prompting for each field."""
    print("\n" + "="*50)
    print("  JEWELRY TAG PRINTER - Interactive Mode")
    print("  Datamax O'Neil E-Class Mark III")
    print("="*50 + "\n")
    
    while True:
        try:
            item_number = input("Item Number (or 'quit' to exit): ").strip()
            if item_number.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            
            if not item_number:
                print("✗ Item number is required\n")
                continue
            
            price = float(input("Price: ").replace('$', '').replace(',', ''))
            carat_weight = float(input("Carat Weight (D=): "))
            gold_karat = int(input("Gold Karat (14/18/24): "))
            
            # Confirm before printing
            print("\nReady to print. Send to printer? [Y/n]: ", end="")
            confirm = input().strip().lower()
            
            if confirm in ('', 'y', 'yes'):
                print_tag(item_number, price, carat_weight, gold_karat)
            else:
                print("Print cancelled.")
            
            print("\n" + "-"*50 + "\n")
            
        except ValueError as e:
            print(f"✗ Invalid input: {e}\n")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Jewelry Tag Printer for Datamax O\'Neil E-Class Mark III',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i                                    # Interactive mode
  %(prog)s -n "MSD958009" -p 17600 -c 5.26 -k 14
  %(prog)s -n "RING001" -p 1299 -c 1.0 -k 18 --dry-run
  %(prog)s -n "NECK002" -p 899 -c 0.75 -k 14 --ip 192.168.1.50
        """
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('-n', '--item-number', type=str,
                        help='Item number/SKU')
    parser.add_argument('-p', '--price', type=float,
                        help='Selling price')
    parser.add_argument('-c', '--carat', type=float,
                        help='Carat weight')
    parser.add_argument('-k', '--karat', type=int, choices=[10, 14, 18, 22, 24],
                        help='Gold karat (10, 14, 18, 22, or 24)')
    parser.add_argument('--ip', type=str, default=PRINTER_IP,
                        help=f'Printer IP address (default: {PRINTER_IP})')
    parser.add_argument('--usb', action='store_true',
                        help='Use USB connection instead of network')
    parser.add_argument('--zpl', action='store_true',
                        help='Use ZPL format instead of DPL')
    parser.add_argument('--epl', action='store_true',
                        help='Use EPL format instead of DPL')
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate commands without sending to printer')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif all([args.item_number, args.price is not None, args.carat is not None,
              args.karat is not None]):
        print_tag(
            item_number=args.item_number,
            price=args.price,
            carat_weight=args.carat,
            gold_karat=args.karat,
            printer_ip=args.ip,
            use_usb=args.usb,
            use_zpl=args.zpl,
            use_epl=args.epl,
            dry_run=args.dry_run
        )
    else:
        parser.print_help()
        print("\n✗ Error: Either use -i for interactive mode or provide all required arguments:")
        print("  -n (item number), -p (price), -c (carat), -k (karat)")


if __name__ == "__main__":
    main()
