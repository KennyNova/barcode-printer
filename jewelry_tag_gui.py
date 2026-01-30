#!/usr/bin/env python3
"""
Jewelry Tag Printer GUI
Simple graphical interface for printing jewelry tags
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import print_tag, generate_item_barcode, CSV_FILE, PRINTER_IP


class JewelryTagPrinterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jewelry Tag Printer")
        self.root.geometry("450x480")
        self.root.resizable(False, False)
        
        # Set style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Status.TLabel', font=('Helvetica', 10))
        style.configure('Preview.TLabel', font=('Courier', 11))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        title = ttk.Label(main_frame, text="🏷️ Jewelry Tag Printer", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Subtitle
        subtitle = ttk.Label(main_frame, text="Datamax O'Neil E-Class Mark III")
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Input fields
        row = 2
        
        # Item Number
        ttk.Label(main_frame, text="Item Number:").grid(row=row, column=0, sticky="e", pady=5)
        self.item_number_var = tk.StringVar()
        self.item_entry = ttk.Entry(main_frame, textvariable=self.item_number_var, width=25)
        self.item_entry.grid(row=row, column=1, sticky="w", pady=5, padx=(10, 0))
        row += 1
        
        # Price
        ttk.Label(main_frame, text="Price:").grid(row=row, column=0, sticky="e", pady=5)
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(main_frame, textvariable=self.price_var, width=25)
        self.price_entry.grid(row=row, column=1, sticky="w", pady=5, padx=(10, 0))
        row += 1
        
        # Carat Weight
        ttk.Label(main_frame, text="Carat Weight (D=):").grid(row=row, column=0, sticky="e", pady=5)
        self.carat_var = tk.StringVar()
        self.carat_entry = ttk.Entry(main_frame, textvariable=self.carat_var, width=25)
        self.carat_entry.grid(row=row, column=1, sticky="w", pady=5, padx=(10, 0))
        row += 1
        
        # Gold Karat
        ttk.Label(main_frame, text="Gold Karat:").grid(row=row, column=0, sticky="e", pady=5)
        self.karat_var = tk.StringVar()
        karat_combo = ttk.Combobox(main_frame, textvariable=self.karat_var, 
                                    values=['10', '14', '18', '22', '24'], width=22, state='readonly')
        karat_combo.grid(row=row, column=1, sticky="w", pady=5, padx=(10, 0))
        karat_combo.set('14')
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                            sticky='ew', pady=15)
        row += 1
        
        # Tag Preview (shows how it will look)
        preview_frame = ttk.LabelFrame(main_frame, text="Tag Preview (Front)", padding="10")
        preview_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.preview_label = ttk.Label(preview_frame, text="17600\nD=5.26\nMSD958009", 
                                        style='Preview.TLabel', justify='left')
        self.preview_label.grid(row=0, column=0, sticky="w")
        
        # Update preview on input change
        self.item_number_var.trace('w', self.update_preview)
        self.price_var.trace('w', self.update_preview)
        self.carat_var.trace('w', self.update_preview)
        
        row += 1
        
        # Printer Settings
        settings_frame = ttk.LabelFrame(main_frame, text="Printer Settings", padding="10")
        settings_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Printer IP
        ttk.Label(settings_frame, text="Printer IP:").grid(row=0, column=0, sticky="e", pady=2)
        self.printer_ip_var = tk.StringVar(value=PRINTER_IP)
        ip_entry = ttk.Entry(settings_frame, textvariable=self.printer_ip_var, width=20)
        ip_entry.grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))
        
        # Options
        self.dry_run_var = tk.BooleanVar(value=False)
        dry_run_check = ttk.Checkbutton(settings_frame, text="Dry Run (Preview Only)", 
                                        variable=self.dry_run_var)
        dry_run_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        self.use_zpl_var = tk.BooleanVar(value=False)
        zpl_check = ttk.Checkbutton(settings_frame, text="Use ZPL Format", 
                                    variable=self.use_zpl_var)
        zpl_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        
        row += 1
        
        # Barcode info
        self.barcode_label = ttk.Label(main_frame, text="Barcode (on back): ---", style='Status.TLabel')
        self.barcode_label.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Print Button
        print_btn = ttk.Button(btn_frame, text="🖨️ Print Tag", command=self.print_tag)
        print_btn.grid(row=0, column=0, padx=5)
        
        # Clear Button
        clear_btn = ttk.Button(btn_frame, text="🗑️ Clear", command=self.clear_fields)
        clear_btn.grid(row=0, column=1, padx=5)
        
        # View History Button
        history_btn = ttk.Button(btn_frame, text="📋 History", command=self.view_history)
        history_btn.grid(row=0, column=2, padx=5)
        
        row += 1
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                               relief="sunken", anchor="w")
        status_bar.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Focus on first entry
        self.item_entry.focus()
    
    def update_preview(self, *args):
        """Update the tag preview and barcode text."""
        item = self.item_number_var.get().strip() or "ITEM#"
        
        try:
            price = self.price_var.get().replace('$', '').replace(',', '')
            price_val = float(price) if price else 0
            price_str = f"{int(price_val)}" if price_val == int(price_val) else f"{price_val:.2f}"
        except ValueError:
            price_str = "0"
        
        try:
            carat = float(self.carat_var.get()) if self.carat_var.get() else 0
            carat_str = f"D={carat:.2f}"
        except ValueError:
            carat_str = "D=0.00"
        
        # Update preview (mimics actual tag layout)
        preview_text = f"{price_str}\n{carat_str}\n{item}"
        self.preview_label.config(text=preview_text)
        
        # Update barcode info
        if item and item != "ITEM#":
            barcode = generate_item_barcode(item)
            self.barcode_label.config(text=f"Barcode (on back): {barcode}")
        else:
            self.barcode_label.config(text="Barcode (on back): ---")
    
    def validate_inputs(self):
        """Validate all input fields."""
        errors = []
        
        if not self.item_number_var.get().strip():
            errors.append("Item Number is required")
        
        try:
            price = float(self.price_var.get().replace('$', '').replace(',', ''))
            if price < 0:
                errors.append("Price must be positive")
        except ValueError:
            errors.append("Invalid Price format")
        
        try:
            carat = float(self.carat_var.get())
            if carat < 0:
                errors.append("Carat weight must be positive")
        except ValueError:
            errors.append("Invalid Carat Weight format")
        
        if not self.karat_var.get():
            errors.append("Gold Karat is required")
        
        return errors
    
    def print_tag(self):
        """Print the jewelry tag."""
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        self.status_var.set("Printing...")
        self.root.update()
        
        try:
            success = print_tag(
                item_number=self.item_number_var.get().strip(),
                price=float(self.price_var.get().replace('$', '').replace(',', '')),
                carat_weight=float(self.carat_var.get()),
                gold_karat=int(self.karat_var.get()),
                printer_ip=self.printer_ip_var.get().strip(),
                use_zpl=self.use_zpl_var.get(),
                dry_run=self.dry_run_var.get()
            )
            
            if success:
                self.status_var.set("✓ Print successful!")
                if not self.dry_run_var.get():
                    messagebox.showinfo("Success", "Tag printed successfully!")
                else:
                    messagebox.showinfo("Dry Run", "Print command generated (not sent to printer)")
            else:
                self.status_var.set("✗ Print failed")
                messagebox.showerror("Error", "Failed to send to printer. Check connection.")
                
        except Exception as e:
            self.status_var.set("✗ Error")
            messagebox.showerror("Error", str(e))
    
    def clear_fields(self):
        """Clear all input fields."""
        self.item_number_var.set("")
        self.price_var.set("")
        self.carat_var.set("")
        self.karat_var.set("14")
        self.status_var.set("Ready")
        self.item_entry.focus()
    
    def view_history(self):
        """Open the CSV history file."""
        if os.path.exists(CSV_FILE):
            if sys.platform == "darwin":
                os.system(f"open '{CSV_FILE}'")
            elif sys.platform == "win32":
                os.startfile(CSV_FILE)
            else:
                os.system(f"xdg-open '{CSV_FILE}'")
        else:
            messagebox.showinfo("History", "No print history yet.")


def main():
    root = tk.Tk()
    app = JewelryTagPrinterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
