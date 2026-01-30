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
        LABEL_WIDTH_MM, LABEL_HEIGHT_MM, DEFAULT_USE_USB,
        USB_PRINTER_NAME
    )
    DPI = PRINTER_DPI
except ImportError:
    # Default configuration if config.py not found
    PRINTER_IP = "192.168.1.100"
    PRINTER_PORT = 9100
    CSV_FILE = "print_history.csv"
    DPI = 203
    LABEL_WIDTH_MM = 42
    LABEL_HEIGHT_MM = 26
    DEFAULT_USE_USB = True
    USB_PRINTER_NAME = "Datamax-O'Neil E-4205A Mark III"

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
    Datamax O'Neil E-4205A Mark III
    
    Tag: 42mm x 26mm (336 x 208 dots at 203 DPI)
    Front side: Price, D=carat, Item number (rotated 90° for hanging tag)
    Back side: Barcode on tail
    """
    barcode_data = generate_item_barcode(item_number)
    
    # Format values for display (matching the tag image)
    price_str = f"{int(price)}" if price == int(price) else f"{price:.2f}"
    carat_str = f"D={carat_weight:.2f}"
    
    # Build DPL command
    dpl = []
    
    # Initialize and configure
    dpl.append("\x02n")                  # Clear image buffer
    dpl.append("\x02L")                  # Start label format
    dpl.append("D11")                    # Darkness (0-30, 11 is good)
    dpl.append("S1")                     # Speed (1=slow, better for small labels)
    dpl.append("H10")                    # Heat setting
    dpl.append("R0000")                  # Reference point 0,0
    dpl.append("ZT")                     # Thermal transfer (ZB for direct thermal)
    dpl.append("JF")                     # Top of form backup
    dpl.append("f100")                   # Form stop position  
    dpl.append(f"PW{LABEL_WIDTH_DOTS}")  # Print width: 336 dots (42mm)
    dpl.append(f"LE{LABEL_HEIGHT_DOTS}") # Label length: 208 dots (26mm)
    
    # Text with 90° rotation (rotation code 1)
    # Format: 1 R 11 00 XXX YYY 0 HH W FONT DATA
    # R=rotation (1=90°CW), XXX=row, YYY=col, HH=height mult, W=width mult
    
    # Price - top (when hanging), large
    dpl.append(f"111100002001500211{price_str}")
    
    # D=carat - middle
    dpl.append(f"111100007001500211{carat_str}")
    
    # Item number - bottom  
    dpl.append(f"111100012001500211{item_number}")
    
    # Barcode on tail area - Code 128
    # Format: 1 B rotation col row narrow:wide height readable type DATA
    # e = Code 128 Auto
    dpl.append(f"1e1016000200102040100{barcode_data}")
    
    # Print 1 label and end
    dpl.append("Q0001")
    dpl.append("E")
    
    return "\r\n".join(dpl).encode('ascii')


def create_test_label() -> bytes:
    """Create a simple test label to verify printer communication."""
    # For jewelry tag: 42mm wide x 26mm tall (at 203 DPI: 336 x 208 dots)
    # Using gap sensing between labels
    dpl = []
    dpl.append("\x02n")                  # Clear buffer
    dpl.append("\x02O")                  # Reset to default settings
    dpl.append("\x02L")                  # Start label format
    dpl.append("H08")                    # Heat setting (0-20, 8 is moderate)
    dpl.append("D11")                    # Darkness/density
    dpl.append("S1")                     # Slow speed for small labels
    dpl.append("R0000")                  # Reference point at 0,0
    dpl.append("ZT")                     # Thermal transfer mode (or ZB for direct thermal)
    dpl.append("JF")                     # Top of form backup
    dpl.append("f100")                   # Form stop position (label gap sensing)
    dpl.append("PW336")                  # Print width 42mm = 336 dots
    dpl.append("LE208")                  # Label end/length 26mm = 208 dots
    # Simple text - format: 1X1100xxxyyy0ttfDATA
    # X=rotation(2=0°), xxx=col, yyy=row, t=size multiplier, f=font
    dpl.append("121100005003000TEST")    # "TEST" at position 50,30
    dpl.append("121100005008000PRINT")   # "PRINT" below
    dpl.append("Q0001")                  # Quantity = 1
    dpl.append("E")                      # End and print ONE label
    
    return "\r\n".join(dpl).encode('ascii')


def create_zpl_command(item_number: str, price: float, carat_weight: float,
                       gold_karat: int) -> bytes:
    """
    Create ZPL command (if printer is in ZPL emulation mode).
    Front: Price, D=carat, Item number (rotated)
    Back: Barcode on tail
    """
    barcode_data = generate_item_barcode(item_number)
    
    price_str = f"{int(price)}" if price == int(price) else f"{price:.2f}"
    carat_str = f"D={carat_weight:.2f}"
    
    # ZPL II format - simpler and more compatible
    zpl = f"""^XA
^PW{LABEL_WIDTH_DOTS}
^LL{LABEL_HEIGHT_DOTS}
^LH0,0
^FWB
^CF0,30
^FO20,20^FD{price_str}^FS
^CF0,25
^FO60,20^FD{carat_str}^FS
^CF0,22
^FO100,20^FD{item_number}^FS
^FWB
^BY2
^FO150,180^BCB,40,N,N,N^FD{barcode_data}^FS
^XZ
"""
    return zpl.encode('ascii')


def create_zpl_test_label() -> bytes:
    """Create a simple ZPL test label."""
    return b"""^XA
^PW336
^LL208
^CF0,30
^FO50,50^FDTEST^FS
^CF0,25
^FO50,90^FDPRINT^FS
^XZ
"""


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
    Works on Windows with the printer name from Control Panel.
    
    For Datamax O'Neil E-4205A Mark III on USB003.
    """
    if printer_name is None:
        printer_name = USB_PRINTER_NAME
    
    if sys.platform == "win32":
        # Try Method 1: win32print (standard Windows printing)
        try:
            import win32print
            
            # List available printers for debugging
            printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            
            # Try to find the printer (case-insensitive partial match)
            matched_printer = None
            for p in printers:
                if "datamax" in p.lower() or "e-4205" in p.lower() or "e4205" in p.lower():
                    matched_printer = p
                    break
            
            if matched_printer:
                printer_name = matched_printer
                print(f"Found printer: {printer_name}")
            elif printer_name not in printers:
                print(f"⚠ Warning: '{printer_name}' not found in printer list")
                print(f"  Available printers: {printers}")
                print(f"  Trying anyway...")
            
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                # Get printer port for direct access attempt
                printer_info = win32print.GetPrinter(hPrinter, 2)
                port_name = printer_info.get('pPortName', 'Unknown')
                print(f"Printer port: {port_name}")
                
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Jewelry Tag", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    bytes_written = win32print.WritePrinter(hPrinter, command)
                    win32print.EndPagePrinter(hPrinter)
                    print(f"✓ Sent {bytes_written} bytes to {printer_name}")
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            return True
            
        except ImportError:
            print("✗ win32print not available. Install pywin32:")
            print("  pip install pywin32")
            return False
        except Exception as e:
            print(f"✗ Failed via win32print: {e}")
            print("  Trying alternative method...")
            
            # Try Method 2: Direct file write to printer share
            try:
                # Try writing directly to the printer share
                printer_path = f"\\\\localhost\\{printer_name}"
                with open(printer_path, 'wb') as f:
                    f.write(command)
                print(f"✓ Sent via direct file write to {printer_path}")
                return True
            except Exception as e2:
                print(f"✗ Direct write also failed: {e2}")
                
            # List printers for help
            try:
                import win32print
                printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                print(f"  Available printers: {printers}")
            except:
                pass
            return False
    else:
        # On macOS/Linux, try using lpr command with printer name
        try:
            import subprocess
            cmd = ['lpr', '-l']
            if printer_name:
                cmd = ['lpr', '-P', printer_name, '-l']
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(input=command)
            if process.returncode == 0:
                print(f"✓ Print command sent via lpr to {printer_name or 'default printer'}")
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
              printer_name: Optional[str] = None,
              use_usb: bool = None,  # None = use default from config
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
        printer_ip: Printer IP address (if using network)
        printer_name: USB printer name (if using USB)
        use_usb: Use USB connection (default: True from config)
        use_zpl: Use ZPL commands instead of DPL
        use_epl: Use EPL commands instead of DPL
        dry_run: Don't actually print, just generate commands
    
    Returns:
        True if print was successful
    """
    # Default to USB if not specified
    if use_usb is None:
        use_usb = DEFAULT_USE_USB
    
    print("\n" + "="*50)
    print("JEWELRY TAG PRINT JOB")
    print("="*50)
    print(f"Item Number:  {item_number}")
    print(f"Price:        {int(price) if price == int(price) else price}")
    print(f"Carat Weight: D={carat_weight:.2f}")
    print(f"Gold Karat:   {gold_karat}K")
    print(f"Barcode:      {generate_item_barcode(item_number)}")
    print(f"Connection:   {'USB' if use_usb else 'Network'}")
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
        success = send_to_usb_printer(command, printer_name)
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


def list_printers():
    """List available printers on the system."""
    if sys.platform == "win32":
        try:
            import win32print
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            print("\nAvailable Printers:")
            print("-" * 40)
            for flags, desc, name, comment in printers:
                marker = " <-- Datamax" if "datamax" in name.lower() else ""
                print(f"  {name}{marker}")
            print("-" * 40)
            return [p[2] for p in printers]
        except ImportError:
            print("✗ Install pywin32 to list printers: pip install pywin32")
            return []
    else:
        print("Printer listing only available on Windows")
        return []


def create_calibrate_command() -> bytes:
    """
    Create command to calibrate the printer for the current media.
    Run this first if labels aren't being detected properly.
    """
    dpl = []
    dpl.append("\x02n")          # Clear buffer
    dpl.append("\x02O")          # Reset to defaults
    dpl.append("\x02e")          # Autosense - calibrate for current media
    return "\r\n".join(dpl).encode('ascii')


def print_test_label(use_zpl: bool = False, printer_name: Optional[str] = None, 
                     dry_run: bool = False, calibrate: bool = False) -> bool:
    """
    Print a test label to verify printer communication.
    Try this if regular prints aren't working.
    """
    print("\n" + "="*50)
    print("TEST PRINT")
    print("="*50)
    
    if calibrate:
        print("Running media calibration first...")
        cal_cmd = create_calibrate_command()
        print(f"Calibration command: {cal_cmd.decode('ascii')}")
        if not dry_run:
            send_to_usb_printer(cal_cmd, printer_name)
            print("Waiting for calibration...")
            import time
            time.sleep(3)
    
    if use_zpl:
        print("Format: ZPL")
        command = create_zpl_test_label()
    else:
        print("Format: DPL")
        command = create_test_label()
    
    print(f"Command preview:\n{command.decode('ascii')}")
    print("="*50)
    
    if dry_run:
        print("[DRY RUN] Command not sent to printer")
        return True
    
    success = send_to_usb_printer(command, printer_name)
    
    if success:
        print("✓ Test command sent! Check if label printed.")
        print("\nIf still feeding continuously:")
        print("  1. Press PAUSE on printer")
        print("  2. Run: python jewelry_tag_printer.py --calibrate")
        print("  3. Try test again")
    else:
        print("✗ Failed to send test command")
    
    return success


def calibrate_printer(printer_name: Optional[str] = None) -> bool:
    """Run media calibration on the printer."""
    print("\n" + "="*50)
    print("MEDIA CALIBRATION")
    print("="*50)
    print("This will calibrate the printer for your label size.")
    print("Make sure labels are loaded correctly.")
    print("="*50)
    
    command = create_calibrate_command()
    success = send_to_usb_printer(command, printer_name)
    
    if success:
        print("✓ Calibration command sent!")
        print("  The printer should feed a few labels to detect the gap.")
        print("  Wait for it to finish, then try printing.")
    
    return success


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Jewelry Tag Printer for Datamax O\'Neil E-4205A Mark III (USB)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Printer: Datamax O'Neil E-4205A Mark III on USB003
Default connection: USB (configured in config.py)

Examples:
  %(prog)s -i                                    # Interactive mode
  %(prog)s -n "MSD958009" -p 17600 -c 5.26 -k 14 # Print via USB (default)
  %(prog)s -n "RING001" -p 1299 -c 1.0 -k 18 --dry-run
  %(prog)s --list-printers                       # Show available printers
  %(prog)s -n "TEST" -p 100 -c 1.0 -k 14 --network --ip 192.168.1.50
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
    parser.add_argument('--printer', type=str, default=USB_PRINTER_NAME,
                        help=f'USB printer name (default: {USB_PRINTER_NAME})')
    parser.add_argument('--network', action='store_true',
                        help='Use network connection instead of USB')
    parser.add_argument('--ip', type=str, default=PRINTER_IP,
                        help=f'Printer IP address for network mode (default: {PRINTER_IP})')
    parser.add_argument('--zpl', action='store_true',
                        help='Use ZPL format instead of DPL')
    parser.add_argument('--epl', action='store_true',
                        help='Use EPL format instead of DPL')
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate commands without sending to printer')
    parser.add_argument('--list-printers', action='store_true',
                        help='List available printers and exit')
    parser.add_argument('--test', action='store_true',
                        help='Print a test label to verify printer communication')
    parser.add_argument('--calibrate', action='store_true',
                        help='Calibrate printer for current label media (run if labels feed continuously)')
    
    args = parser.parse_args()
    
    if args.list_printers:
        list_printers()
        return
    
    if args.calibrate:
        calibrate_printer(printer_name=args.printer)
        return
    
    if args.test:
        print_test_label(
            use_zpl=args.zpl,
            printer_name=args.printer,
            dry_run=args.dry_run
        )
        return
    
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
            printer_name=args.printer,
            use_usb=not args.network,  # USB is default, --network overrides
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
