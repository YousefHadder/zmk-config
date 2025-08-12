#!/usr/bin/env python3
"""
niceview_lvgl_convert.py

Convert images to fixed size 1-bit indexed LVGL C arrays.
Pipeline:
  - Resize to width x height (defaults 140x60)
  - (Optional) Rotate 90° clockwise (default: rotate)
  - Convert to 1-bit (Floyd–Steinberg dither by default)
  - ALWAYS invert colors (white <-> black) after conversion
  - Pack pixels (8 px / byte), MSB-first by default
  - Emit a .c file whose name matches the source image stem
  - LVGL descriptor uses LV_IMG_CF_INDEXED_1BIT and includes a 2‑entry conditional palette

Usage examples:
  python3 niceview_lvgl_convert.py img.jpg
  python3 niceview_lvgl_convert.py img1.jpg img2.png --outdir out
  python3 niceview_lvgl_convert.py art.png --lsb-first
  python3 niceview_lvgl_convert.py logo.png --no-dither --no-rotate

Notes:
  - Colors are always inverted now (previous --invert flag removed).
  - If you need non-inverted output, reintroduce a flag or flip the logic in to_1bpp().
"""

import argparse
from pathlib import Path
from PIL import Image

def to_1bpp(img, dither=True, invert=True):
    """Convert a PIL image to 1-bit; always invert=True in this script."""
    if dither:
        bw = img.convert("1")  # 1-bit with FS dither
    else:
        # Threshold
        bw = img.convert("L").point(lambda p: 255 if p >= 128 else 0, mode="1")
    if invert:
        bw = bw.point(lambda p: 255 - p, mode="1")
    return bw

def pack_bits_1bpp(img_1bit, lsb_first=False):
    """
    Pack a mode '1' image into bytes (8 pixels per byte).
    MSB-first (bit 7 is leftmost pixel) by default; LSB-first if requested.
    """
    if img_1bit.mode != "1":
        raise ValueError("pack_bits_1bpp expects a mode '1' image")
    w, h = img_1bit.size
    pix = img_1bit.load()
    out = bytearray()
    for y in range(h):
        bit_acc = 0
        bit_count = 0
        for x in range(w):
            bit = 1 if pix[x, y] == 255 else 0
            if lsb_first:
                bit_acc |= (bit & 1) << bit_count
            else:
                bit_acc = (bit_acc << 1) | (bit & 1)
            bit_count += 1
            if bit_count == 8:
                out.append(bit_acc & 0xFF)
                bit_acc = 0
                bit_count = 0
        if bit_count:
            if not lsb_first:
                bit_acc <<= (8 - bit_count)
            out.append(bit_acc & 0xFF)
    return bytes(out)

def make_macro_name(s: str) -> str:
    """Make a valid macro name (uppercase, only A-Z, 0-9, _) from a string."""
    return "".join(ch.upper() if ch.isalnum() else "_" for ch in s)

def emit_indexed1bit_lvgl_c_file(filename_stem, width, height, image_bytes, bytes_per_line=12):
    macro_name = make_macro_name(filename_stem)
    array_name = f"{filename_stem}_map"
    img_var_name = filename_stem

    # Conditional palette (index 0 / index 1) – unchanged from previous requirement.
    palette_block = """\
#if CONFIG_NICE_VIEW_WIDGET_INVERTED
    0xff, 0xff, 0xff, 0xff, /*Color of index 0*/
    0x00, 0x00, 0x00, 0xff, /*Color of index 1*/
#else
    0x00, 0x00, 0x00, 0xff, /*Color of index 0*/
    0xff, 0xff, 0xff, 0xff, /*Color of index 1*/
#endif
"""

    hexes = [f"0x{b:02X}" for b in image_bytes]
    lines = [", ".join(hexes[i:i+bytes_per_line]) for i in range(0, len(hexes), bytes_per_line)]
    image_array_literal = ",\n    ".join(lines)
    array_block = f"{palette_block}\n{image_array_literal}"

    c_content = f"""\
#ifndef LV_ATTRIBUTE_IMG_{macro_name}
#define LV_ATTRIBUTE_IMG_{macro_name}
#endif

const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST LV_ATTRIBUTE_IMG_{macro_name} uint8_t
    {array_name}[] = {{
    {array_block}
}};

const lv_img_dsc_t {img_var_name} = {{
    .header.cf = LV_IMG_CF_INDEXED_1BIT,
    .header.always_zero = 0,
    .header.reserved = 0,
    .header.w = {width},
    .header.h = {height},
    .data_size = sizeof({array_name}),
    .data = {array_name},
}};
"""
    return c_content

def process_image(path: Path, args):
    filename_stem = path.stem

    with Image.open(path) as im:
        im = im.convert("L")
        im = im.resize((args.width, args.height), Image.LANCZOS)

        if not args.no_rotate:
            im = im.transpose(Image.ROTATE_270)

        # Always invert now
        bw = to_1bpp(im, dither=not args.no_dither, invert=True)
        packed = pack_bits_1bpp(bw, lsb_first=args.lsb_first)

        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        out_c = outdir / f"{filename_stem}.c"

        final_w, final_h = (args.height, args.width) if not args.no_rotate else (args.width, args.height)

        c_file_contents = emit_indexed1bit_lvgl_c_file(filename_stem, final_w, final_h, packed, bytes_per_line=args.bytes_per_line)

        with open(out_c, "w", encoding="utf-8") as f:
            f.write(c_file_contents)

        return out_c, len(packed)

def main():
    p = argparse.ArgumentParser(description="Convert images to 1bpp indexed LVGL arrays (always inverted).")
    p.add_argument("inputs", nargs="+", help="Input image files (png/jpg/gif/bmp/...)")
    p.add_argument("--outdir", default="out", help="Output directory (default: out)")
    p.add_argument("--width", type=int, default=68, help="Resize target width (default: 140)")
    p.add_argument("--height", type=int, default=140, help="Resize target height (default: 60)")
    p.add_argument("--no-dither", action="store_true", help="Disable Floyd–Steinberg dithering (use threshold)")
    p.add_argument("--lsb-first", action="store_true", help="Pack bits with LSB-first (bit 0 is leftmost pixel)")
    p.add_argument("--no-rotate", action="store_true", help="Do NOT rotate 90° clockwise")
    p.add_argument("--bytes-per-line", type=int, default=12, help="C array formatting: bytes per line")
    args = p.parse_args()

    total_bytes = 0
    outputs = []
    for inp in args.inputs:
        path = Path(inp)
        if not path.exists():
            print(f"[WARN] Skipping missing file: {path}")
            continue
        out_path, nbytes = process_image(path, args)
        total_bytes += nbytes
        outputs.append(out_path)

    print(f"Done. Wrote {len(outputs)} file(s), total {total_bytes} bytes of packed 1bpp (inverted) data.")
    for o in outputs:
        print(f" - {o}")

if __name__ == "__main__":
    main()
