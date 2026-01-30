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
# LABEL PRESETS
# =============================================================================
# Preset 1: Standard jewelry tag (42mm x 26mm body, 68mm with tail)
# Preset 2: Narrow barbell tag (7/16" x 3.5" overall, 7/16" x 1.75" printable)

LABEL_PRESETS = {
    "standard": {
        "name": "Standard RFID Tag (68x26mm)",
        "description": "Jewelry tag: 42mm body + 26mm tail, 26mm tall",
        # Total label dimensions (as it feeds through printer)
        "total_width_mm": 68,       # Full width with tail
        "body_width_mm": 42,        # Main body width
        "height_mm": 26,            # Label height
        "tail_width_mm": 26,        # Tail portion (68-42)
        "tail_height_mm": 11,       # Tail is narrower (11mm)
        # Dots at 203 DPI (8 dots per mm)
        "width_dots": 544,          # 68mm total width
        "height_dots": 208,         # 26mm height
        "body_width_dots": 336,     # 42mm body
        "printable_width_dots": 336, # Print on 42mm body
        "printable_height_dots": 208,
    },
    "barbell": {
        "name": "Barbell Tag (7/16\" x 3.5\")",
        "description": "Folding tag: front(0.875\") + back(0.875\") + loop(1.75\")",
        "width_inches": 0.4375,     # 7/16" = 11mm
        "total_length_inches": 3.5, # 3.5" total
        "printable_length_inches": 1.75,  # 1.75" printable (both halves)
        "front_length_inches": 0.875,     # First half - product info
        "back_length_inches": 0.875,      # Second half - barcode (folds behind)
        "loop_length_inches": 1.75,       # Thin loop - NO printing
        "width_dots": 89,           # 7/16" at 203 DPI
        "height_dots": 355,         # 1.75" printable at 203 DPI
        "front_dots": 177,          # First half for product info
        "back_dots": 178,           # Second half for barcode
        "loop_dots": 355,           # Loop - don't print here
    }
}

# Default preset to use
DEFAULT_PRESET = "standard"

# =============================================================================
# USB PRINTER SETTINGS (Default - using USB connection)
# =============================================================================
DEFAULT_USE_USB = True

# Windows printer name - find this in Control Panel > Devices and Printers
USB_PRINTER_NAME = "Datamax-O'Neil E-4205A Mark III"

# USB Port (for reference)
USB_PORT = "USB003"

# =============================================================================
# NETWORK PRINTER SETTINGS (Alternative - if using Ethernet)
# =============================================================================
PRINTER_IP = "192.168.1.100"
PRINTER_PORT = 9100

# =============================================================================
# PRINTER SPECIFICATIONS
# =============================================================================
PRINTER_DPI = 203  # E-4205A = 203 DPI

# =============================================================================
# FILE SETTINGS
# =============================================================================
CSV_FILE = "print_history.csv"
BARCODE_PREVIEW_DIR = "barcodes"

# =============================================================================
# PRINT FORMAT SETTINGS
# =============================================================================
DEFAULT_USE_ZPL = False
DEFAULT_USE_EPL = False
