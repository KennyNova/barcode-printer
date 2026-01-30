#!/usr/bin/env python3
"""
Visual Label Preset Editor
See exactly what will print and adjust positions in real-time
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jewelry_tag_printer import (
    send_to_usb_printer, generate_item_barcode, 
    LABEL_PRESETS, USB_PRINTER_NAME
)


class LabelEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Label Preset Editor - Visual Preview")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Current preset
        self.current_preset = "barbell"
        
        # Sample data
        self.sample_data = {
            "price": "17600",
            "carat": "D=5.26",
            "item": "MSD958009"
        }
        
        # Position variables (in dots)
        self.price_x = tk.IntVar(value=10)
        self.price_y = tk.IntVar(value=5)
        self.carat_x = tk.IntVar(value=50)
        self.carat_y = tk.IntVar(value=5)
        self.item_x = tk.IntVar(value=90)
        self.item_y = tk.IntVar(value=5)
        
        # Label dimensions for barbell (in dots)
        self.label_width = 89      # 7/16" at 203 DPI
        self.label_length = 355    # 1.75" printable at 203 DPI
        self.first_half = 177      # First half boundary
        
        self.create_widgets()
        self.update_preview()
        
    def create_widgets(self):
        # Main container
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_frame = ttk.Frame(main_paned, width=350)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Preview and Commands
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        self.create_controls(left_frame)
        self.create_preview(right_frame)
        
    def create_controls(self, parent):
        # Preset selector
        preset_frame = ttk.LabelFrame(parent, text="Label Preset", padding=10)
        preset_frame.pack(fill=tk.X, pady=5)
        
        self.preset_var = tk.StringVar(value=self.current_preset)
        for preset_name in LABEL_PRESETS.keys():
            rb = ttk.Radiobutton(preset_frame, text=preset_name, 
                                 variable=self.preset_var, value=preset_name,
                                 command=self.on_preset_change)
            rb.pack(anchor=tk.W)
        
        # Sample data
        data_frame = ttk.LabelFrame(parent, text="Sample Data", padding=10)
        data_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(data_frame, text="Price:").grid(row=0, column=0, sticky="e")
        self.price_entry = ttk.Entry(data_frame, width=15)
        self.price_entry.insert(0, self.sample_data["price"])
        self.price_entry.grid(row=0, column=1, padx=5, pady=2)
        self.price_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        ttk.Label(data_frame, text="Carat:").grid(row=1, column=0, sticky="e")
        self.carat_entry = ttk.Entry(data_frame, width=15)
        self.carat_entry.insert(0, self.sample_data["carat"])
        self.carat_entry.grid(row=1, column=1, padx=5, pady=2)
        self.carat_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        ttk.Label(data_frame, text="Item#:").grid(row=2, column=0, sticky="e")
        self.item_entry = ttk.Entry(data_frame, width=15)
        self.item_entry.insert(0, self.sample_data["item"])
        self.item_entry.grid(row=2, column=1, padx=5, pady=2)
        self.item_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        # Position controls
        pos_frame = ttk.LabelFrame(parent, text="Text Positions (dots)", padding=10)
        pos_frame.pack(fill=tk.X, pady=5)
        
        # Price position
        ttk.Label(pos_frame, text="Price X:").grid(row=0, column=0, sticky="e")
        price_x_scale = ttk.Scale(pos_frame, from_=0, to=350, variable=self.price_x,
                                   command=lambda v: self.update_preview())
        price_x_scale.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(pos_frame, textvariable=self.price_x, width=4).grid(row=0, column=2)
        
        ttk.Label(pos_frame, text="Price Y:").grid(row=1, column=0, sticky="e")
        price_y_scale = ttk.Scale(pos_frame, from_=0, to=89, variable=self.price_y,
                                   command=lambda v: self.update_preview())
        price_y_scale.grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Label(pos_frame, textvariable=self.price_y, width=4).grid(row=1, column=2)
        
        # Carat position
        ttk.Label(pos_frame, text="Carat X:").grid(row=2, column=0, sticky="e")
        carat_x_scale = ttk.Scale(pos_frame, from_=0, to=350, variable=self.carat_x,
                                   command=lambda v: self.update_preview())
        carat_x_scale.grid(row=2, column=1, sticky="ew", padx=5)
        ttk.Label(pos_frame, textvariable=self.carat_x, width=4).grid(row=2, column=2)
        
        ttk.Label(pos_frame, text="Carat Y:").grid(row=3, column=0, sticky="e")
        carat_y_scale = ttk.Scale(pos_frame, from_=0, to=89, variable=self.carat_y,
                                   command=lambda v: self.update_preview())
        carat_y_scale.grid(row=3, column=1, sticky="ew", padx=5)
        ttk.Label(pos_frame, textvariable=self.carat_y, width=4).grid(row=3, column=2)
        
        # Item position
        ttk.Label(pos_frame, text="Item X:").grid(row=4, column=0, sticky="e")
        item_x_scale = ttk.Scale(pos_frame, from_=0, to=350, variable=self.item_x,
                                  command=lambda v: self.update_preview())
        item_x_scale.grid(row=4, column=1, sticky="ew", padx=5)
        ttk.Label(pos_frame, textvariable=self.item_x, width=4).grid(row=4, column=2)
        
        ttk.Label(pos_frame, text="Item Y:").grid(row=5, column=0, sticky="e")
        item_y_scale = ttk.Scale(pos_frame, from_=0, to=89, variable=self.item_y,
                                  command=lambda v: self.update_preview())
        item_y_scale.grid(row=5, column=1, sticky="ew", padx=5)
        ttk.Label(pos_frame, textvariable=self.item_y, width=4).grid(row=5, column=2)
        
        pos_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🖨️ Test Print", 
                   command=self.test_print).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 Copy DPL", 
                   command=self.copy_dpl).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Reset Positions", 
                   command=self.reset_positions).pack(side=tk.LEFT, padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(parent, text="Label Info", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="", justify=tk.LEFT)
        self.info_label.pack(anchor=tk.W)
        self.update_info()
        
    def create_preview(self, parent):
        # Preview canvas
        preview_frame = ttk.LabelFrame(parent, text="Label Preview (scaled)", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas for visual preview
        self.canvas = tk.Canvas(preview_frame, bg="white", highlightthickness=1,
                                highlightbackground="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.update_preview())
        
        # DPL commands display
        cmd_frame = ttk.LabelFrame(parent, text="Generated DPL Commands", padding=10)
        cmd_frame.pack(fill=tk.X, pady=5)
        
        self.cmd_text = tk.Text(cmd_frame, height=10, font=("Courier", 10))
        self.cmd_text.pack(fill=tk.X)
        
    def on_preset_change(self):
        self.current_preset = self.preset_var.get()
        self.update_info()
        self.update_preview()
        
    def update_info(self):
        preset = LABEL_PRESETS.get(self.current_preset, {})
        info = f"Preset: {preset.get('name', 'Unknown')}\n"
        info += f"Width: {preset.get('width_dots', '?')} dots\n"
        info += f"Height: {preset.get('height_dots', '?')} dots\n"
        if 'description' in preset:
            info += f"{preset['description']}"
        self.info_label.config(text=info)
        
    def update_preview(self):
        """Update the visual preview and DPL commands."""
        self.canvas.delete("all")
        
        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            return
        
        # For barbell: label is 89 dots wide x 355 dots long (printable)
        # Plus ~355 dots for the loop (shown grayed out)
        label_w = 89
        label_l = 355  # Printable
        loop_l = 355   # Loop (non-printable)
        total_l = label_l + loop_l
        
        # Calculate scale to fit canvas (with padding)
        padding = 40
        scale_x = (canvas_width - padding * 2) / total_l
        scale_y = (canvas_height - padding * 2) / label_w
        scale = min(scale_x, scale_y, 3)  # Cap at 3x
        
        # Draw label outline
        x_offset = padding
        y_offset = padding + 20
        
        # First half (printable - front)
        first_half_end = int(177 * scale)
        self.canvas.create_rectangle(
            x_offset, y_offset,
            x_offset + first_half_end, y_offset + int(label_w * scale),
            fill="#e8f5e9", outline="green", width=2
        )
        self.canvas.create_text(
            x_offset + first_half_end/2, y_offset - 10,
            text="FRONT (Product Info)", font=("Arial", 9), fill="green"
        )
        
        # Second half (printable - back/barcode)
        second_half_end = int(label_l * scale)
        self.canvas.create_rectangle(
            x_offset + first_half_end, y_offset,
            x_offset + second_half_end, y_offset + int(label_w * scale),
            fill="#e3f2fd", outline="blue", width=2
        )
        self.canvas.create_text(
            x_offset + first_half_end + (second_half_end - first_half_end)/2, y_offset - 10,
            text="BACK (Barcode)", font=("Arial", 9), fill="blue"
        )
        
        # Loop (non-printable)
        loop_end = int(total_l * scale)
        self.canvas.create_rectangle(
            x_offset + second_half_end, y_offset,
            x_offset + loop_end, y_offset + int(label_w * scale * 0.3),  # Narrower
            fill="#f5f5f5", outline="gray", width=1
        )
        self.canvas.create_text(
            x_offset + second_half_end + (loop_end - second_half_end)/2, 
            y_offset + int(label_w * scale * 0.15),
            text="LOOP (no print)", font=("Arial", 8), fill="gray"
        )
        
        # Draw fold line
        self.canvas.create_line(
            x_offset + first_half_end, y_offset,
            x_offset + first_half_end, y_offset + int(label_w * scale),
            fill="red", dash=(4, 4), width=2
        )
        
        # Draw text positions
        price_text = self.price_entry.get() or "PRICE"
        carat_text = self.carat_entry.get() or "D=0.00"
        item_text = self.item_entry.get() or "ITEM#"
        
        # Price
        px = x_offset + int(self.price_x.get() * scale)
        py = y_offset + int(self.price_y.get() * scale)
        self.canvas.create_text(px, py, text=price_text, anchor="nw", 
                                font=("Arial", 8), fill="black")
        self.canvas.create_oval(px-3, py-3, px+3, py+3, fill="red", outline="red")
        
        # Carat
        cx = x_offset + int(self.carat_x.get() * scale)
        cy = y_offset + int(self.carat_y.get() * scale)
        self.canvas.create_text(cx, cy, text=carat_text, anchor="nw",
                                font=("Arial", 8), fill="black")
        self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill="blue", outline="blue")
        
        # Item
        ix = x_offset + int(self.item_x.get() * scale)
        iy = y_offset + int(self.item_y.get() * scale)
        self.canvas.create_text(ix, iy, text=item_text, anchor="nw",
                                font=("Arial", 8), fill="black")
        self.canvas.create_oval(ix-3, ix-3, ix+3, iy+3, fill="green", outline="green")
        
        # Add scale indicator
        self.canvas.create_text(
            padding, canvas_height - 20,
            text=f"Scale: 1 dot = {scale:.2f} pixels | First half ends at X=177",
            anchor="w", font=("Arial", 9), fill="gray"
        )
        
        # Update DPL commands
        self.update_dpl_display()
        
    def generate_dpl(self):
        """Generate the DPL commands based on current settings."""
        price = self.price_entry.get() or "0"
        carat = self.carat_entry.get() or "D=0.00"
        item = self.item_entry.get() or "ITEM"
        
        px, py = self.price_x.get(), self.price_y.get()
        cx, cy = self.carat_x.get(), self.carat_y.get()
        ix, iy = self.item_x.get(), self.item_y.get()
        
        # Build DPL - using format that works
        dpl = []
        dpl.append("\\x02n")           # Clear buffer (shown as escape for display)
        dpl.append("\\x02L")           # Start label
        dpl.append("D11")              # Density
        
        # Text commands: 1 ROT 11 00 XXX YYY H W F DATA
        # ROT=2 (0 degrees), XXX=X position, YYY=Y position
        # Padding positions to 3 digits
        dpl.append(f"12110{px:03d}0{py:02d}00100{price}")
        dpl.append(f"12110{cx:03d}0{cy:02d}00100{carat}")
        dpl.append(f"12110{ix:03d}0{iy:02d}00100{item}")
        
        dpl.append("E")                # End and print
        
        return dpl
    
    def generate_raw_dpl(self):
        """Generate actual bytes to send to printer."""
        price = self.price_entry.get() or "0"
        carat = self.carat_entry.get() or "D=0.00"
        item = self.item_entry.get() or "ITEM"
        
        px, py = self.price_x.get(), self.price_y.get()
        cx, cy = self.carat_x.get(), self.carat_y.get()
        ix, iy = self.item_x.get(), self.item_y.get()
        
        dpl = "\x02n\r\n"
        dpl += "\x02L\r\n"
        dpl += "D11\r\n"
        dpl += f"12110{px:03d}0{py:02d}00100{price}\r\n"
        dpl += f"12110{cx:03d}0{cy:02d}00100{carat}\r\n"
        dpl += f"12110{ix:03d}0{iy:02d}00100{item}\r\n"
        dpl += "E\r\n"
        
        return dpl.encode('ascii')
        
    def update_dpl_display(self):
        """Update the DPL commands text display."""
        self.cmd_text.delete("1.0", tk.END)
        commands = self.generate_dpl()
        self.cmd_text.insert("1.0", "\n".join(commands))
        
    def test_print(self):
        """Send test print to printer."""
        try:
            command = self.generate_raw_dpl()
            
            # Show what we're sending
            print("Sending DPL:")
            print(command.decode('ascii'))
            
            success = send_to_usb_printer(command)
            
            if success:
                messagebox.showinfo("Print", "Test sent to printer!")
            else:
                messagebox.showerror("Error", "Failed to send to printer")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def copy_dpl(self):
        """Copy DPL commands to clipboard."""
        commands = "\n".join(self.generate_dpl())
        self.root.clipboard_clear()
        self.root.clipboard_append(commands)
        messagebox.showinfo("Copied", "DPL commands copied to clipboard!")
        
    def reset_positions(self):
        """Reset to default positions."""
        self.price_x.set(10)
        self.price_y.set(5)
        self.carat_x.set(50)
        self.carat_y.set(5)
        self.item_x.set(90)
        self.item_y.set(5)
        self.update_preview()


def main():
    root = tk.Tk()
    app = LabelEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
