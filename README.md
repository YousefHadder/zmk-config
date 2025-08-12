# **Corne + Nice!Nano + Nice!View — ZMK Config** ✨

A complete ZMK configuration for the Corne keyboard with Nice!Nano v2 controllers and custom Nice!View displays featuring rotating artwork.

## 🎯 **Quick Overview**

- **Keyboard**: Corne (3×6 + 3 thumb keys, split layout)
- **MCUs**: Nice!Nano v2 (wireless, split left/right halves)
- **Display**: Nice!View OLED with custom status screen and rotating artwork
- **Features**: Custom keymap, automated image conversion, wireless connectivity

## 📋 **Table of Contents**

1. [Getting Started](#getting-started)
2. [Using This Repository](#using-this-repository)
   - [Fork and Use](#fork-and-use)
   - [Direct Usage](#direct-usage)
3. [Repository Structure](#repository-structure)
4. [Nice!View Artwork System](#niceview-artwork-system)
5. [Configuration](#configuration)
   - [Keymap Customization](#keymap-customization)
   - [Display Settings](#display-settings)
6. [Building Firmware](#building-firmware)
7. [Image Conversion Details](#image-conversion-details)
8. [Local Development](#local-development)
9. [Contributing](#contributing)

##  **Getting Started**

### Quick Start

1. **Fork this repository** to your GitHub account
2. **Enable GitHub Actions** in your forked repository
3. **Add your images** to the `assets/` folder
4. **Push changes** - GitHub Actions will automatically build firmware
5. **Download firmware** from the Actions tab
6. **Flash to your keyboards** using the instructions below

---

##  **Using This Repository**

### Fork and Use

**This is the recommended approach for most users:**

1. **Fork this repository** to your GitHub account:
   - Click the "Fork" button on GitHub
   - This creates your own copy where you can make changes

2. **Configure GitHub Actions** (required for automated builds):
   - Go to your forked repo → Settings → Actions → General
   - Enable "Read and write permissions" for GITHUB_TOKEN
   - Create a PAT with scope `Contents: Read and write` (fine‑grained) for the forked repo
   - Add it as a repository secret named `ACTIONS_PAT`

3. **Customize your configuration**:
   - Edit `config/corne.keymap` for your preferred key layout
   - Add your images to `assets/` folder for custom Nice!View artwork
   - Modify `config/corne.conf` for display and other settings

4. **Build firmware**:
   - Push your changes to trigger GitHub Actions
   - Download firmware files from the Actions tab
   - Flash to your keyboards

### Direct Usage

**For advanced users who want to use this config as-is:**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/zmk-config.git
   cd zmk-config
   ```

2. **Build locally** (requires ZMK development environment):
   ```bash
   # Follow ZMK's local build instructions
   west build -p -b nice_nano_v2 -- -DSHIELD="corne_left nice_view_adapter nice_view"
   west build -p -b nice_nano_v2 -- -DSHIELD="corne_right nice_view_adapter nice_view_custom"
   ```

---

##  **Repository Structure**

```
zmk-config/
├── config/                          # ZMK configuration files
│   ├── corne.keymap                 # Keymap layers, combos, and behaviors
│   ├── corne.conf                   # ZMK settings (enables custom status screen)
│   └── west.yml                     # ZMK upstream reference
├── boards/shields/nice_view_custom/ # Custom Nice!View shield
│   ├── widgets/                     # Custom widget implementations
│   │   ├── peripheral_status.c/.h   # Main status widget (art + status)
│   │   ├── status.c/.h             # Status display components
│   │   ├── bolt.c                  # Bluetooth/power indicators
│   │   ├── util.c/.h               # Utility functions
│   │   └── art.c                   # ⚠️ Auto-generated image data (don't edit)
│   ├── nice_view_custom.overlay     # Device tree overlay
│   ├── nice_view_custom.conf        # Shield configuration
│   └── CMakeLists.txt              # Build configuration
├── assets/                          # 🖼️ Your custom images for Nice!View
│   ├── itachi.jpeg                 # Example artwork
│   ├── me.png                      # Example artwork
│   └── palestine.webp              # Example artwork
├── scripts/
│   └── niceview_lvgl_convert.py    # Image → LVGL C array converter
├── .github/workflows/               # GitHub Actions automation
│   ├── update-images.yml           # Converts images and updates art.c
│   └── build.yml                   # Builds firmware
├── build.yaml                      # Build matrix for left/right halves
└── zephyr/module.yml               # Zephyr module descriptor
```

---

##  **Nice!View Artwork System**

This repository features an **automated artwork system** that converts your images into display-ready formats and rotates them on your Nice!View screens.

### How It Works

**Step 1: Add Images** 📁
- Place PNG/JPG/WEBP files into the `assets/` folder
- Use simple filenames (letters, numbers, underscores only)
- Example: `logo.png` becomes `LV_IMG_DECLARE(logo)` in code

**Step 2: Automated Conversion** 🤖
- GitHub Actions detects new images in `assets/`
- Runs `scripts/niceview_lvgl_convert.py` to:
  - Resize images to 68×140 pixels
  - Rotate 90° clockwise for proper display orientation  
  - Convert to 1-bit black/white with Floyd-Steinberg dithering
  - Generate LVGL C arrays in `art.c`
- Updates widget code to include new images in rotation
- Commits changes back to your repository

**Step 3: Firmware Build** 🏗️
- Build workflow triggers automatically after image conversion
- Compiles firmware for both keyboard halves:
  - **Left**: `nice_nano_v2` + `corne_left` + `nice_view`
  - **Right**: `nice_nano_v2` + `corne_right` + `nice_view_custom`
- Firmware files available in GitHub Actions artifacts

**Step 4: On-Device Display** 🖼️
- Images rotate automatically every **5 minutes**
- Display shows: battery level, connection status, and your artwork
- Works seamlessly with ZMK's power management

---

##  **Configuration**

### Keymap Customization

Edit `config/corne.keymap` to customize your keyboard layout:

- **Layers**: Define different key layouts (base, symbols, numbers, etc.)
- **Combos**: Set key combinations for special functions
- **Mod-tap**: Configure keys that act as modifiers when held, regular keys when tapped
- **Macros**: Create custom key sequences

**Current Layout Features:**
- Home row modifiers (Alt, Shift, Ctrl, GUI)
- 3 layers: base typing, media/navigation, symbols/numbers
- Caps Lock combo (both thumb keys)
- Custom shortcuts for window management

### Display Settings

Modify `config/corne.conf` to control display behavior:

```conf
CONFIG_ZMK_DISPLAY=y                        # Enable OLED display
CONFIG_ZMK_DISPLAY_STATUS_SCREEN_CUSTOM=y   # Use custom status screen
```

**Optional Settings:**
```conf
# Enable RGB underglow (requires additional hardware)
CONFIG_ZMK_RGB_UNDERGLOW=y
CONFIG_WS2812_STRIP=y

# Adjust display timeout and brightness
CONFIG_ZMK_DISPLAY_WORK_QUEUE_DEDICATED=y
```

---

## **Building Firmware**

### Automatic Builds (Recommended)

1. **Push changes** to your forked repository
2. **GitHub Actions** automatically builds firmware
3. **Download** from Actions tab → latest workflow run → Artifacts
4. **Files generated:**
   - `corne_left-nice_nano_v2-zmk.uf2` (left half)
   - `corne_right-nice_nano_v2-zmk.uf2` (right half)

### Manual/Local Builds

**Prerequisites:**
- ZMK development environment set up
- West build tool installed

**Build commands:**
```bash
# Left half
west build -p -b nice_nano_v2 -- -DSHIELD="corne_left nice_view_adapter nice_view"

# Right half  
west build -p -b nice_nano_v2 -- -DSHIELD="corne_right nice_view_adapter nice_view_custom"
```

---

##  **Image Conversion Details**

### Automatic Conversion

The `niceview_lvgl_convert.py` script processes images with these steps:

1. **Resize** to 68×140 pixels (optimized for Nice!View)
2. **Rotate** 90° clockwise for proper display orientation
3. **Convert** to 1-bit black/white using Floyd-Steinberg dithering
4. **Invert** colors (white ↔ black) for display compatibility
5. **Generate** LVGL C arrays with `LV_IMG_CF_INDEXED_1BIT` format

### Manual Testing

**Install dependencies:**
```bash
pip install Pillow
```

**Convert single image:**
```bash
python3 scripts/niceview_lvgl_convert.py assets/logo.png --outdir converted
```

**Useful flags:**
- `--no-rotate`: Keep original orientation
- `--no-dither`: Disable Floyd-Steinberg dithering  
- `--lsb-first`: Change bit packing order
- `--width 68 --height 140`: Custom dimensions

### Image Guidelines

**Recommended specs:**
- **Format**: PNG, JPG, WEBP, GIF
- **Size**: Any size (auto-resized to 68×140)
- **Content**: High contrast works best
- **Filename**: Letters, numbers, underscores only

**Pro tips:**
- Black and white images convert best
- Avoid fine details (display is only 68×140 pixels)
- Test locally before committing

---

## **Local Development**

### Setting Up Local Environment

1. **Install ZMK dependencies:**
   ```bash
   # Follow ZMK's getting started guide
   pip3 install --user -U west
   west init -l config
   west update
   west zephyr-export
   ```

2. **Install image conversion tools:**
   ```bash
   pip install Pillow
   ```

3. **Test image conversion:**
   ```bash
   python3 scripts/niceview_lvgl_convert.py assets/test.png --outdir test_output
   ```

### Development Workflow

1. **Edit keymap** in `config/corne.keymap`
2. **Add images** to `assets/` folder
3. **Test conversion** locally (optional)
4. **Build firmware** using GitHub Actions or locally
5. **Flash and test** on hardware

---

### Getting Help

- **ZMK Documentation**: [zmk.dev](https://zmk.dev)
- **ZMK Discord**: [discord.gg/8cfMkQksSB](https://discord.gg/8cfMkQksSB)
- **Nice!Keyboards**: [nicekeyboards.com](https://nicekeyboards.com)

### Tips

- **High-contrast artwork** works best on the 1-bit display
- **Keep backups** of your working firmware files
- **Test one change at a time** when troubleshooting
- **Check Actions logs** for detailed error messages

---

##  **Contributing**

Feel free to:
- 🐛 **Report bugs** via GitHub Issues
- 💡 **Suggest improvements** for the artwork system
- 🔧 **Submit PRs** for widget enhancements
- 📚 **Improve documentation**


---

## **License**

This configuration is provided under the MIT License. See individual files for their respective licenses.

---

**Built with ❤️ on ZMK**

*Need help customizing the rotation interval, keymap layout, or adding new features? Open an issue and let's make this configuration even better!*
