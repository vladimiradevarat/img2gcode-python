import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps, ImageDraw, ImageFont
import os
import ctypes
import json
from datetime import datetime

class Img2GcodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Img2Gcode - Ender 3 Laser Mod")
        
        self.conf_file = "laser2gcode.conf"
        
        # Variables with hardcoded defaults (used if no .conf exists)
        self.filepath = tk.StringVar()
        self.laser_min = tk.IntVar(value=0)
        self.laser_max = tk.IntVar(value=65)
        self.laser_off = tk.IntVar(value=0)
        self.white_level = tk.IntVar(value=253)
        
        self.travel_rate = tk.IntVar(value=6000)
        self.feed_rate = tk.IntVar(value=1600)
        self.overscan = tk.DoubleVar(value=3.0)
        
        # Image specific variables (not saved to config)
        self.size_y = tk.DoubleVar(value=40.0)
        self.res_x = tk.DoubleVar(value=0.1)
        self.scan_gap = tk.DoubleVar(value=0.1)
        self.rotation = tk.IntVar(value=180) 
        
        self.pause_cmd = tk.StringVar(value="M0 ; Pause for confirmation")
        self.process_mode = tk.StringVar(value="bw") 
        
        # Grid variables (not saved)
        self.grid_cols = tk.IntVar(value=1)
        self.grid_rows = tk.IntVar(value=1)
        self.grid_gap_x = tk.DoubleVar(value=5.0)
        self.grid_gap_y = tk.DoubleVar(value=5.0)
        
        self.return_origin = tk.BooleanVar(value=True)
        
        # Calibration variables (not saved)
        self.tune_min = tk.BooleanVar(value=False)
        self.tune_max = tk.BooleanVar(value=False)
        
        self.info_text = tk.StringVar(value="Info: No image selected")
        self.sd_drive = None 

        # Load config before building GUI
        self.load_config()

        # Event traces
        self.filepath.trace_add("write", self.update_info)
        self.size_y.trace_add("write", self.update_info)
        self.res_x.trace_add("write", self.update_info)
        self.scan_gap.trace_add("write", self.update_info)
        self.rotation.trace_add("write", self.update_info)
        self.grid_cols.trace_add("write", self.update_info)
        self.grid_rows.trace_add("write", self.update_info)
        self.grid_gap_x.trace_add("write", self.update_info)
        self.grid_gap_y.trace_add("write", self.update_info)

        self.build_gui()
        self.check_sd_loop()

    def load_config(self):
        """Loads basic settings from the config file if it exists"""
        if os.path.exists(self.conf_file):
            try:
                with open(self.conf_file, 'r') as f:
                    config = json.load(f)
                    
                if 'laser_min' in config: self.laser_min.set(config['laser_min'])
                if 'laser_max' in config: self.laser_max.set(config['laser_max'])
                if 'laser_off' in config: self.laser_off.set(config['laser_off'])
                if 'white_level' in config: self.white_level.set(config['white_level'])
                if 'travel_rate' in config: self.travel_rate.set(config['travel_rate'])
                if 'feed_rate' in config: self.feed_rate.set(config['feed_rate'])
                if 'overscan' in config: self.overscan.set(config['overscan'])
                if 'res_x' in config: self.res_x.set(config['res_x'])
                if 'scan_gap' in config: self.scan_gap.set(config['scan_gap'])
                if 'rotation' in config: self.rotation.set(config['rotation'])
                if 'pause_cmd' in config: self.pause_cmd.set(config['pause_cmd'])
                if 'process_mode' in config: self.process_mode.set(config['process_mode'])
                if 'return_origin' in config: self.return_origin.set(config['return_origin'])
            except Exception as e:
                print(f"Warning: Could not load {self.conf_file} correctly. Using defaults.")

    def save_config(self):
        """Saves current basic settings to the config file"""
        config = {
            'laser_min': self.laser_min.get(),
            'laser_max': self.laser_max.get(),
            'laser_off': self.laser_off.get(),
            'white_level': self.white_level.get(),
            'travel_rate': self.travel_rate.get(),
            'feed_rate': self.feed_rate.get(),
            'overscan': self.overscan.get(),
            'res_x': self.res_x.get(),
            'scan_gap': self.scan_gap.get(),
            'rotation': self.rotation.get(),
            'pause_cmd': self.pause_cmd.get(),
            'process_mode': self.process_mode.get(),
            'return_origin': self.return_origin.get()
        }
        try:
            with open(self.conf_file, 'w') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Success", f"Settings successfully saved to {self.conf_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config file:\n{str(e)}")

    def build_gui(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack()

        tk.Button(frame, text="Select Image", command=self.select_file).grid(row=0, column=0, pady=5)
        tk.Label(frame, textvariable=self.filepath, width=50, anchor="w", bg="white").grid(row=0, column=1, columnspan=3, padx=5)

        # Settings - Left
        tk.Label(frame, text="Laser Min [0-255]:").grid(row=1, column=0, sticky="e")
        tk.Entry(frame, textvariable=self.laser_min, width=10).grid(row=1, column=1, sticky="w")
        
        tk.Label(frame, text="Laser Max [0-255]:").grid(row=2, column=0, sticky="e")
        tk.Entry(frame, textvariable=self.laser_max, width=10).grid(row=2, column=1, sticky="w")

        tk.Label(frame, text="Laser 'Off' [0-255]:").grid(row=3, column=0, sticky="e")
        tk.Entry(frame, textvariable=self.laser_off, width=10).grid(row=3, column=1, sticky="w")
        
        tk.Label(frame, text="White Level (Cutoff):").grid(row=4, column=0, sticky="e")
        tk.Entry(frame, textvariable=self.white_level, width=10).grid(row=4, column=1, sticky="w")

        # Settings - Right
        tk.Label(frame, text="Travel Rate [mm/min]:").grid(row=1, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.travel_rate, width=10).grid(row=1, column=3, sticky="w")

        tk.Label(frame, text="Scan Rate [mm/min]:").grid(row=2, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.feed_rate, width=10).grid(row=2, column=3, sticky="w")

        tk.Label(frame, text="Overscan [mm]:").grid(row=3, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.overscan, width=10).grid(row=3, column=3, sticky="w")

        tk.Label(frame, text="Height (Y) [mm]:").grid(row=4, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.size_y, width=10).grid(row=4, column=3, sticky="w")

        tk.Label(frame, text="Resolution X [mm/px]:").grid(row=5, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.res_x, width=10).grid(row=5, column=3, sticky="w")

        tk.Label(frame, text="Scan Gap Y [mm/line]:").grid(row=6, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.scan_gap, width=10).grid(row=6, column=3, sticky="w")

        tk.Label(frame, text="Rotation [deg]:").grid(row=7, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.rotation, width=10).grid(row=7, column=3, sticky="w")

        tk.Label(frame, text="Pause Command:").grid(row=7, column=0, sticky="e", pady=10)
        tk.Entry(frame, textvariable=self.pause_cmd, width=20).grid(row=7, column=1, sticky="w")

        # Process Mode
        tk.Label(frame, text="Processing Mode:").grid(row=8, column=0, sticky="e", pady=5)
        modes_frame = tk.Frame(frame)
        modes_frame.grid(row=8, column=1, columnspan=3, sticky="w")
        tk.Radiobutton(modes_frame, text="Black & White (Text/Logo)", variable=self.process_mode, value="bw").pack(side="left")
        tk.Radiobutton(modes_frame, text="Grayscale (Photos)", variable=self.process_mode, value="gray").pack(side="left")

        # Grid Settings
        grid_frame = tk.LabelFrame(frame, text=" Grid / Array (Multiple Copies) ", font=("Arial", 9, "bold"), padx=10, pady=5)
        grid_frame.grid(row=9, column=0, columnspan=4, sticky="we", pady=5)
        
        tk.Label(grid_frame, text="Columns (X):").grid(row=0, column=0, sticky="e")
        tk.Entry(grid_frame, textvariable=self.grid_cols, width=6).grid(row=0, column=1, sticky="w", padx=(0,15))
        tk.Label(grid_frame, text="Rows (Y):").grid(row=0, column=2, sticky="e")
        tk.Entry(grid_frame, textvariable=self.grid_rows, width=6).grid(row=0, column=3, sticky="w", padx=(0,15))
        tk.Label(grid_frame, text="Gap X [mm]:").grid(row=0, column=4, sticky="e")
        tk.Entry(grid_frame, textvariable=self.grid_gap_x, width=6).grid(row=0, column=5, sticky="w", padx=(0,15))
        tk.Label(grid_frame, text="Gap Y [mm]:").grid(row=0, column=6, sticky="e")
        tk.Entry(grid_frame, textvariable=self.grid_gap_y, width=6).grid(row=0, column=7, sticky="w")

        # Calibration Frame
        cal_frame = tk.LabelFrame(frame, text=" Calibration Test (Advanced) ", fg="red", font=("Arial", 9, "bold"), padx=10, pady=5)
        cal_frame.grid(row=10, column=0, columnspan=4, sticky="we", pady=5)
        cal_checks = tk.Frame(cal_frame)
        cal_checks.pack(anchor="w")
        tk.Checkbutton(cal_checks, text="Tune Min (+0.5/line)", variable=self.tune_min).pack(side="left", padx=(0, 15))
        tk.Checkbutton(cal_checks, text="Tune Max (-0.5/line)", variable=self.tune_max).pack(side="left")

        # End Behavior and Save Config
        tk.Checkbutton(frame, text="Return to origin (0,0) when finished", variable=self.return_origin, font=("Arial", 9, "bold")).grid(row=11, column=0, columnspan=3, sticky="w", pady=5)
        tk.Button(frame, text="Save Config", command=self.save_config, font=("Arial", 8)).grid(row=11, column=3, sticky="e", padx=5)

        # Info Text
        tk.Label(frame, textvariable=self.info_text, fg="blue", font=("Arial", 9, "bold")).grid(row=12, column=0, columnspan=4, pady=5)

        # Buttons
        self.btn_generate = tk.Button(frame, text="Generate G-Code", command=self.save_manual, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.btn_generate.grid(row=13, column=0, columnspan=2, pady=5, sticky="we", padx=5)

        self.btn_sd = tk.Button(frame, text="Save to SD", command=self.save_to_sd, bg="#1971c2", fg="white", font=("Arial", 10, "bold"))

        tk.Button(frame, text="Preview", command=self.preview_image).grid(row=14, column=0, columnspan=2, pady=5, sticky="we", padx=5)
        tk.Button(frame, text="Preview White-Level", command=self.preview_whitelevel).grid(row=14, column=2, columnspan=2, pady=5, sticky="we", padx=5)

    def check_sd_loop(self):
        self.sd_drive = self.find_sd_card_windows()
        if self.sd_drive:
            self.btn_sd.grid(row=13, column=2, columnspan=2, pady=5, sticky="we", padx=5)
            self.btn_sd.config(text=f"Save directly to SD ({self.sd_drive})")
        else:
            self.btn_sd.grid_forget()
        
        self.root.after(1000, self.check_sd_loop)

    def select_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if filepath:
            self.filepath.set(filepath)

    def update_info(self, *args):
        if not self.filepath.get():
            self.info_text.set("Info: No image selected")
            return
        
        try:
            img = Image.open(self.filepath.get())
            rot = self.rotation.get()
            if rot != 0:
                img = img.rotate(rot, expand=True)
                
            w, h = img.size
            size_y = self.size_y.get()
            res_x = self.res_x.get()
            scan_gap = self.scan_gap.get()
            
            if size_y <= 0 or res_x <= 0 or scan_gap <= 0:
                self.info_text.set("Info: Invalid dimensions set.")
                return

            size_x = size_y * w / h
            pixels_x = int(round(size_x / res_x))
            pixels_y = int(round(size_y / scan_gap))
            
            cols = max(1, self.grid_cols.get())
            rows = max(1, self.grid_rows.get())
            gap_x = self.grid_gap_x.get()
            gap_y = self.grid_gap_y.get()
            
            tot_x = size_x * cols + gap_x * (cols - 1)
            tot_y = size_y * rows + gap_y * (rows - 1)
            
            self.info_text.set(f"Original: {w}x{h} px  |  Total Size: {tot_x:.2f}x{tot_y:.2f} mm  |  Grid: {cols}x{rows}")
        except Exception:
            self.info_text.set("Info: Enter valid numbers to calculate.")

    def process_image(self):
        if not self.filepath.get():
            messagebox.showerror("Error", "Please select an image!")
            return None, None, None, None, None

        img = Image.open(self.filepath.get()).convert('L')
        
        rot = self.rotation.get()
        if rot != 0:
            img = img.rotate(rot, expand=True)
        
        if self.process_mode.get() == "bw":
            wl = self.white_level.get()
            img = img.point(lambda p: 0 if p < wl else 255)

        img = ImageOps.mirror(img)
        
        w, h = img.size
        size_y = self.size_y.get()
        size_x = size_y * w / h
        
        pixels_x = int(round(size_x / self.res_x.get()))
        pixels_y = int(round(size_y / self.scan_gap.get()))
        
        img = img.resize((pixels_x, pixels_y), Image.Resampling.LANCZOS)
        
        if self.process_mode.get() == "bw":
            img = img.point(lambda p: 0 if p < 128 else 255)

        return img, size_x, size_y, pixels_x, pixels_y

    def generate_preview_canvas(self, show_whitelevel=False):
        img, size_x, size_y, px, py = self.process_image()
        if not img: return None

        if show_whitelevel:
            img = img.convert('RGB')
            pixels = img.load()
            wl = self.white_level.get() if self.process_mode.get() == "gray" else 128
            for y in range(py):
                for x in range(px):
                    if pixels[x, y][0] >= wl:
                        pixels[x, y] = (255, 0, 0)

        cols = max(1, self.grid_cols.get())
        rows = max(1, self.grid_rows.get())
        
        gap_x_px = int(round(self.grid_gap_x.get() / self.res_x.get()))
        gap_y_px = int(round(self.grid_gap_y.get() / self.scan_gap.get()))

        tot_px_x = (px * cols) + (gap_x_px * (cols - 1))
        tot_px_y = (py * rows) + (gap_y_px * (rows - 1))
        
        tot_mm_x = size_x * cols + self.grid_gap_x.get() * (cols - 1)
        tot_mm_y = size_y * rows + self.grid_gap_y.get() * (rows - 1)

        bg_color = (255, 255, 255) if show_whitelevel else 255
        mode = "RGB" if show_whitelevel else "L"
        base_canvas = Image.new(mode, (tot_px_x, tot_px_y), color=bg_color)

        for r in range(rows):
            for c in range(cols):
                off_x = c * (px + gap_x_px)
                off_y = r * (py + gap_y_px)
                base_canvas.paste(img, (off_x, off_y))

        # Margins and ruler
        margin = 40
        ruler_bg = (235, 235, 235) if show_whitelevel else 235
        text_color = (0, 0, 0) if show_whitelevel else 0
        
        ruler_canvas = Image.new(mode, (tot_px_x + margin, tot_px_y + margin), color=ruler_bg)
        ruler_canvas.paste(base_canvas, (margin, margin))
        
        draw = ImageDraw.Draw(ruler_canvas)
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font = ImageFont.load_default()
            
        draw.text((10, margin - 20), "0,0", fill=text_color, font=font)
        
        # X Axis
        for mm in range(0, int(tot_mm_x) + 2):
            px_pos = margin + int(mm / self.res_x.get())
            if mm % 10 == 0:
                draw.line([(px_pos, margin - 15), (px_pos, margin)], fill=text_color, width=2)
                draw.text((px_pos + 2, margin - 30), f"{mm}", fill=text_color, font=font)
            elif mm % 5 == 0:
                draw.line([(px_pos, margin - 10), (px_pos, margin)], fill=text_color, width=1)
            else:
                if (1 / self.res_x.get()) > 3:
                    draw.line([(px_pos, margin - 5), (px_pos, margin)], fill=text_color, width=1)
                
        # Y Axis
        for mm in range(0, int(tot_mm_y) + 2):
            py_pos = margin + int(mm / self.scan_gap.get())
            if mm % 10 == 0:
                draw.line([(margin - 15, py_pos), (margin, py_pos)], fill=text_color, width=2)
                draw.text((5, py_pos - 7), f"{mm}", fill=text_color, font=font)
            elif mm % 5 == 0:
                draw.line([(margin - 10, py_pos), (margin, py_pos)], fill=text_color, width=1)
            else:
                if (1 / self.scan_gap.get()) > 3:
                    draw.line([(margin - 5, py_pos), (margin, py_pos)], fill=text_color, width=1)

        return ruler_canvas

    def preview_image(self):
        canvas = self.generate_preview_canvas(show_whitelevel=False)
        if canvas: 
            canvas.show(title=f"Preview Grid - {self.process_mode.get()}")

    def preview_whitelevel(self):
        canvas = self.generate_preview_canvas(show_whitelevel=True)
        if canvas: 
            canvas.show(title="Preview Grid White-Level")

    def find_sd_card_windows(self):
        if os.name != 'nt':
            return None
        try:
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                if bitmask & 1:
                    drive = f"{letter}:\\"
                    if ctypes.windll.kernel32.GetDriveTypeW(drive) == 2:
                        try:
                            free_bytes = ctypes.c_ulonglong(0)
                            ctypes.windll.kernel32.GetDiskFreeSpaceExW(drive, None, None, ctypes.byref(free_bytes))
                            if free_bytes.value > 0:
                                return drive
                        except:
                            pass
                bitmask >>= 1
        except Exception:
            pass
        return None

    def get_auto_filename(self):
        original_filename = os.path.basename(self.filepath.get())
        base_name, _ = os.path.splitext(original_filename)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        return f"{base_name}_{timestamp}.gcode"

    def save_manual(self):
        if not self.filepath.get(): return
        path = filedialog.asksaveasfilename(
            initialfile=self.get_auto_filename(),
            defaultextension=".gcode", 
            filetypes=[("G-code Files", "*.gcode")]
        )
        if path:
            if self._write_file(path):
                messagebox.showinfo("Success", f"G-code file saved successfully to:\n{path}")

    def save_to_sd(self):
        if not self.sd_drive or not self.filepath.get(): return
        path = os.path.join(self.sd_drive, self.get_auto_filename())
        if self._write_file(path):
            messagebox.showinfo("Success", f"Saved directly to SD Card:\n{path}")

    def _write_file(self, save_path):
        img, size_x, size_y, pixels_x, pixels_y = self.process_image()
        if not img:
            return False

        cols = max(1, self.grid_cols.get())
        rows = max(1, self.grid_rows.get())
        gap_x = self.grid_gap_x.get()
        gap_y = self.grid_gap_y.get()

        tot_x = size_x * cols + gap_x * (cols - 1)
        tot_y = size_y * rows + gap_y * (rows - 1)

        try:
            pixels = img.load()
            with open(save_path, 'w', encoding='utf-8') as f:
                self.write_header(f, tot_x, tot_y, pixels_x, pixels_y, cols, rows)
                self.write_bounding_box(f, tot_x, tot_y)

                for row in range(rows):
                    for col in range(cols):
                        offset_x = col * (size_x + gap_x)
                        offset_y = row * (size_y + gap_y)
                        
                        if cols > 1 or rows > 1:
                            f.write(f"\n; --- START COPY [{row+1}, {col+1}] ---\n")
                        else:
                            f.write("\n; --- START ENGRAVING ---\n")
                            
                        self.write_image_data(f, img, pixels, size_x, size_y, pixels_x, pixels_y, offset_x, offset_y)

                f.write("; --- END OF PRINT --- \n")
                if self.return_origin.get():
                    f.write(f"G0 X0 Y0 F{self.travel_rate.get()} ; Back to origin\n")
                else:
                    f.write("; Staying at final position (Return to origin disabled)\n")

            return True
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during generation:\n{str(e)}")
            return False

    def write_header(self, f, tot_x, tot_y, px, py, cols, rows):
        f.write("; Generated with the Python Img2Gcode script\n")
        f.write(f"; Processing Mode: {self.process_mode.get()}\n")
        if cols > 1 or rows > 1:
            f.write(f"; Grid: {cols} columns x {rows} rows\n")
        f.write(f"; Total Size mm: X={tot_x:.2f}, Y={tot_y:.2f}\n")
        f.write(f"; Base Image Pixels: X={px}, Y={py}\n")
        f.write("G21 ; Set units to mm\n")
        f.write("G90 ; Absolute positioning\n")
        f.write("G92 X0 Y0 ; Set current point as origin (0,0)\n")
        f.write(f"M106 S{self.laser_off.get()} ; Turn off laser\n\n")

    def write_bounding_box(self, f, size_x, size_y):
        tr = self.travel_rate.get()
        f.write("; --- START BOUNDING BOX (Total Area) ---\n")
        f.write("M106 S1 ; Turn on laser at minimum power for bounding box\n") 
        f.write(f"G0 X{size_x:.4f} Y0 F{tr}\n")
        f.write(f"G0 X{size_x:.4f} Y{size_y:.4f} F{tr}\n")
        f.write(f"G0 X0 Y{size_y:.4f} F{tr}\n")
        f.write(f"G0 X0 Y0 F{tr}\n")
        f.write(f"M106 S{self.laser_off.get()} ; Turn off laser after bounding box\n")
        f.write("; --- END BOUNDING BOX ---\n\n")
        
        f.write("; --- PAUSE FOR VERIFICATION ---\n")
        f.write(f"{self.pause_cmd.get()}\n")

    def write_image_data(self, f, img, pixels, size_x, size_y, pixels_x, pixels_y, offset_x=0, offset_y=0):
        f.write(f"G1 F{self.feed_rate.get()}\n")
        
        prev_value = self.laser_off.get()
        
        def map_val(val, in_min, in_max, out_min, out_max):
            return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

        wl_threshold = self.white_level.get() if self.process_mode.get() == "gray" else 128
        
        current_min = float(self.laser_min.get())
        current_max = float(self.laser_max.get())

        for y in range(pixels_y):
            line_y = (y * self.scan_gap.get()) + offset_y
            
            first_x, last_x = -1, -1
            for x in range(pixels_x):
                if pixels[x, y] < wl_threshold:
                    if first_x == -1:
                        first_x = x
                    last_x = x
                    
            if first_x != -1:
                for x in range(first_x, last_x + 1):
                    pixel_x = (x * self.res_x.get()) + offset_x
                    
                    if x == first_x:
                        f.write(f"G0 X{pixel_x - self.overscan.get():.4f} Y{line_y:.4f} F{self.travel_rate.get()}\n")
                        f.write(f"G1 F{self.feed_rate.get()}\n")
                        f.write(f"G1 X{pixel_x:.4f} Y{line_y:.4f}\n")
                    else:
                        f.write(f"G1 X{pixel_x:.4f}\n")
                        
                    val_8bit = pixels[x, y]
                    laser_val = round(map_val(val_8bit, 255, 0, current_min, current_max), 1)
                    
                    if laser_val != prev_value:
                        f.write(f"M106 S{laser_val}\n")
                        prev_value = laser_val
                
                f.write(f"M106 S{self.laser_off.get()}\n\n")
                prev_value = self.laser_off.get()

            if self.tune_min.get():
                current_min += 0.5
            if self.tune_max.get():
                current_max -= 0.5

            if current_min >= current_max:
                f.write("; Calibration bounds met (Min >= Max). Stopping early for this copy.\n")
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = Img2GcodeApp(root)
    root.mainloop()
