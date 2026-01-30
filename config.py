"""
Configuration file for Jewelry Tag Printer
Edit these values to match your setup

Tag Layout (Front):
  - Line 1: Price (e.g., 17600)
  - Line 2: D=carat (e.g., D=5.26)
  - Line 3: Item Number (e.g., MSD958009)
  
Tag Layout (Back):
  - Barcode (Code 128)
"""

# =============================================================================
# USB PRINTER SETTINGS (Default - using USB connection)
# =============================================================================
# Set to True to use USB connection (recommended for your setup)
DEFAULT_USE_USB = True

# Windows printer name - find this in Control Panel > Devices and Printers
# Common names for your printer:
#   "Datamax-O'Neil E-4205A Mark III"
#   "DatamaxONeil E4205A Mark III"  
#   "Datamax E-4205A"
# Run: Get-Printer | Select-Object Name  (in PowerShell to list printers)
USB_PRINTER_NAME = "Datamax-O'Neil E-4205A Mark III"

# USB Port (for reference - Windows handles this via printer name)
USB_PORT = "USB003"

# =============================================================================
# NETWORK PRINTER SETTINGS (Alternative - if using Ethernet)
# =============================================================================
PRINTER_IP = "192.168.1.100"  # Your printer IP (if using network)
PRINTER_PORT = 9100           # Standard raw printing port

# =============================================================================
# PRINTER SPECIFICATIONS
# =============================================================================
# Printer DPI (dots per inch)
# E-Class Mark III E-4205A = 203 DPI (standard)
# E-Class Mark III E-4305A = 300 DPI (optional high-res)
PRINTER_DPI = 203

# Label Dimensions (in millimeters)
LABEL_WIDTH_MM = 42
LABEL_HEIGHT_MM = 26
TAIL_WIDTH_MM = 68  # Total width including tail (barcode area)
TAIL_HEIGHT_MM = 11

# =============================================================================
# FILE SETTINGS
# =============================================================================
CSV_FILE = "print_history.csv"
BARCODE_PREVIEW_DIR = "barcodes"

# =============================================================================
# PRINT FORMAT SETTINGS
# =============================================================================
DEFAULT_USE_ZPL = False  # Set to True if printer prefers ZPL over DPL
DEFAULT_USE_EPL = False  # Set to True to use EPL format
