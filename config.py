"""
Configuration file for Jewelry Tag Printer
Edit these values to match your setup
"""

# Printer Network Settings
PRINTER_IP = "192.168.1.100"  # Your Datamax O'Neil printer IP address
PRINTER_PORT = 9100           # Standard raw printing port (usually 9100)

# Printer DPI (dots per inch)
# E-Class Mark III standard is 203 DPI
# If you have the 300 DPI version, change this to 300
PRINTER_DPI = 203

# Label Dimensions (in millimeters)
# Based on your jewelry tag specifications
LABEL_WIDTH_MM = 42
LABEL_HEIGHT_MM = 26
TAIL_WIDTH_MM = 68  # Total width including tail
TAIL_HEIGHT_MM = 11

# CSV History File
CSV_FILE = "print_history.csv"

# Barcode Preview Directory
BARCODE_PREVIEW_DIR = "barcodes"

# Default Print Settings
DEFAULT_USE_ZPL = False  # Set to True if your printer prefers ZPL over DPL
DEFAULT_USE_USB = False  # Set to True if using USB connection
