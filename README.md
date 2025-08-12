# **Corne + Nice!Nano + Nice!View — ZMK Config** ✨

- 🧠 Repo for a Corne (3x6 + 3 thumbs) running ZMK
- 🔌 MCUs: `nice_nano_v2` (split, left/right)
- 🖼️ Display: Nice!View OLED with a custom status/art widget

This repository contains the full user configuration for ZMK, including keymaps, build matrix, a custom Nice!View widget, and an automated workflow to convert and rotate artwork for the screen.

**Table of Contents**
- Overview
- Repo Structure
- Nice!View Artwork Workflow
- Image Conversion Details
- Local Testing
- Tips & Troubleshooting

**Overview**
- 🧩 Split layout: 3 rows × 6 columns + 3 thumb keys
- 🔋 Custom status screen: battery, connection, and rotating artwork
- ⚙️ Automated CI: image-to-C conversion and firmware builds

**Repo Structure**
- `config/`
  - `corne.keymap`: Keymap layers, combos, and behaviors
  - `corne.conf`: ZMK settings (enables custom status screen)
  - `west.yml`: ZMK upstream reference
- `boards/shields/nice_view_custom/widgets/`
  - `peripheral_status.c/.h`: Custom status widget (art + status)
  - `status.c/.h`, `bolt.c`, `util.c/.h`: Supporting widget code
  - `art.c`: Auto-generated C file containing the image data; do not edit
- `assets/`
  - Source images for Nice!View artwork (e.g., `me.png`, `palestine.webp`)
- `scripts/`
  - `niceview_lvgl_convert.py`: Python image → LVGL C array converter
- `.github/workflows/`
  - `update-images.yml`: Converts images and commits new `art.c` and declarations
  - `build.yml`: Builds firmware using ZMK’s reusable workflow
- `build.yaml`: Build matrix for left/right halves and shields
- `zephyr/module.yml`: Zephyr module descriptor

**Nice!View Artwork Workflow**
The CI automates converting images and wiring them into the widget.

1) ➕ Add images
   - Place PNG/JPG/WEBP/etc. into `assets/` and push your branch (or open a PR).
   - Tip: Keep filenames simple (letters, numbers, underscores). The filename becomes the C symbol (e.g., `logo.png` → `LV_IMG_DECLARE(logo)`).

2) 🤖 Conversion action runs (`.github/workflows/update-images.yml`)
   - Checks `assets/` for images.
   - Converts each image via `scripts/niceview_lvgl_convert.py` into `converted/*.c`.
   - Concatenates all converted files into `boards/shields/nice_view_custom/widgets/art.c`.
   - Updates `boards/shields/nice_view_custom/widgets/peripheral_status.c` to:
     - Declare each image (`LV_IMG_DECLARE(...)`).
     - Rotate displayed image automatically every 5 minutes.
   - Commits and pushes changes back to the repo.

3) 🏗️ Firmware build triggers (`.github/workflows/build.yml`)
   - The commit from step 2 modifies tracked source files (not ignored), which triggers the build workflow.
   - Uses `build.yaml` to build both halves:
     - Left: `nice_nano_v2` + `corne_left nice_view_adapter nice_view`
     - Right: `nice_nano_v2` + `corne_right nice_view_adapter nice_view_custom`
   - Download artifacts from the Actions page and flash them to your boards.

4) 🖼️ Result on-device
   - The status screen shows battery/connection and your art.
   - Multiple images rotate automatically every 5 minutes.

**Image Conversion Details**
- ⚙️ Pipeline (handled by `niceview_lvgl_convert.py`):
  - Resize to `--width 68` × `--height 140`.
  - Rotate 90° clockwise by default (final display ~140×68).
  - Convert to 1‑bit with Floyd–Steinberg dithering (can disable).
  - Always invert colors (white ↔ black) to match widget expectations.
  - Pack pixels and emit LVGL `LV_IMG_CF_INDEXED_1BIT` arrays.
- 🧾 Declarations & rotation
  - The workflow injects `LV_IMG_DECLARE(name);` lines and updates the widget to cycle through all images present.
  - Rotation interval lives in `peripheral_status.c` (5 minutes). Adjust by editing the workflow’s update step or the file directly.
- 🪪 Palette inversion
  - The emitted arrays include a conditional palette driven by `CONFIG_NICE_VIEW_WIDGET_INVERTED` if used by your build.

**Local Testing**
- Install deps: `pip install Pillow`
- Convert one image locally:
  - `python3 scripts/niceview_lvgl_convert.py assets/logo.png --outdir converted`
- Useful flags:
  - `--no-rotate` to keep original orientation
  - `--no-dither` to disable FS dithering
  - `--lsb-first` to change bit packing
  - `--width/--height` to tune the resize step

**Tips & Troubleshooting**
- 🔐 PAT for Actions push: The image update workflow uses `secrets.ACTIONS_PAT` to push commits. Create a classic PAT with `repo` scope, add it as a repo secret named `ACTIONS_PAT`.
- 🧹 Replace images: Remove old files from `assets/` to drop them from rotation, then push. The workflow will regenerate `art.c` and update the declarations.
- 📝 Naming: Stick to alphanumerics/underscores to ensure valid C identifiers.
- 🚫 Ignored paths: The build workflow ignores direct changes to `assets/` and `.github/`, but the converter’s commit touches `boards/...`, which triggers a build.
- 📐 Aspect & readability: High‑contrast artwork works best at ~140×68 final. If your image looks muddy, try manual preprocessing (levels/contrast) before adding to `assets/`.

—
Built with ❤️ on ZMK. If you want me to tweak the rotation interval, add a preview of the current keymap, or document flashing steps for your OS, just say the word.
