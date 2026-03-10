<p align="center">
  <h1 align="center">Img2Gcode-Python ⚡</h1>
  <p align="center">
    <strong>Advanced Image to G-Code Generator for Ender 3 Laser Mod</strong>
    <br />
    <a href="#-features">Features</a>
    ·
    <a href="#-installation">Installation</a>
    ·
    <a href="#-usage">Usage</a>
    ·
    <a href="#-credits--acknowledgments">Credits</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/GUI-Tkinter-green.svg" alt="Tkinter">
  <img src="https://img.shields.io/badge/License-GPLv3-red.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
</p>

---

## 📖 Overview

**Img2Gcode-Python** is a standalone desktop application designed to convert raster images (`.jpg`, `.png`, `.bmp`) into highly optimized G-code for 3D printers equipped with laser engraver modules (specifically tailored for the Creality Ender 3). 

This tool eliminates the need for complex CAM software for simple engravings, offering a fast, offline, and user-friendly interface with advanced production features.

<img width="524" height="548" alt="image" src="https://github.com/user-attachments/assets/7e39ad2c-e840-4654-a3ae-0e37f4f6da00" />


## ✨ Features

This project massively expands upon traditional web-based converters by introducing native desktop features:

- **Grid / Matrix Array Generation:** Print multiple copies of the same image in a highly configurable grid (custom X/Y columns, rows, and gap spacing).
- **Smart SD Card Detection:** Automatically scans for removable drives with available space and reveals a one-click "Save to SD" button.
- **Real-Time Ruler Preview:** Visually inspect your final print layout with an accurate millimeter-scale ruler overlaid directly on the preview canvas.
- **Image Rotation:** Built-in 180° rotation (or custom angles) to match your machine's hardware origin point.
- **Bounding Box Tracing:** Traces the exact outer perimeter of your print area at minimum/zero power, ensuring perfect material alignment before the burn starts.
- **Calibration Suite:** Auto-tunes laser power line-by-line to find the optimal burn settings for new, untested materials.
- **Persistent Configuration:** Saves your machine's default travel rates, laser power limits, and modes to a local `laser2gcode.conf` file.

## 🚀 Installation

### Option 1: Running from Source
To run the script directly, ensure you have Python 3 installed on your system.

<ol>
  <li>
    <p>Clone the repository:</p>
    <pre><code class="language-bash">git clone https://github.com/YOUR_USERNAME/img2gcode-python.git
cd img2gcode-python</code></pre>
  </li>
  <li>
    <p>Install the required image processing library:</p>
    <pre><code class="language-bash">pip install Pillow</code></pre>
  </li>
  <li>
    <p>Run the application:</p>
    <pre><code class="language-bash">python main.py</code></pre>
  </li>
</ol>

💻 Usage
Load Image: Click Select Image and pick a supported raster graphic.

Configure Laser: Input your laser's Min, Max, and Off PWM values (typically 0-255).

Set Speeds: Define Travel Rate (non-burning moves) and Scan Rate (burning speed).

Define Size: Set the physical Height (Y) in millimeters. The X-axis is calculated automatically to maintain the aspect ratio.

Array Setup (Optional): If engraving multiple pieces, configure the Columns, Rows, and gaps in the Grid section.

Preview: Use the Preview or Preview White-Level buttons to verify the output and dimensions on the ruler canvas.

Export: Click Generate G-Code to save locally, or use the Save to SD button if a removable drive is detected.

Tip: Click the "💾 Save Config" button to lock in your machine's specific speeds and laser values for future sessions!

🤝 Credits & Acknowledgments
This application is a heavy modernization and standalone Python port of the original PHP-based web tool.

🏆 Original Concept & Core Logic: nebarnix

🔗 Original Web Tool: Img2gco

Massive thanks to nebarnix for the brilliant approach to G-code generation and the open-source spirit that made this Python port possible.

📄 License
This project is licensed under the GNU General Public License v3.0 (GPLv3).
See the LICENSE file for details. You are free to use, modify, and distribute this software, provided you keep it open-source and state the modifications.
