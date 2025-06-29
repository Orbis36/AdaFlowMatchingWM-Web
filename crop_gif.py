# #!/usr/bin/env python3
# """
# Batch‐crop all GIFs in a folder by fixed margins.

# Usage:
#     python crop_gifs_folder.py \
#         --input_dir /path/to/gifs \
#         --output_dir /path/to/cropped \
#         --left 50 --right 50 --top 0 --bottom 0
# """
import os
import argparse
from PIL import Image, ImageSequence

def crop_frame(frame, crop):
    left, right, top, bottom = crop
    w, h = frame.size
    return frame.crop((left, top, w - right, h - bottom))

def process_gif(path_in, path_out, crop):
    im = Image.open(path_in)
    frames = []
    durations = []
    for frame in ImageSequence.Iterator(im):
        f = frame.convert("RGB")  # ensure consistent mode
        cropped = crop_frame(f, crop)
        frames.append(cropped)
        durations.append(frame.info.get("duration", 100))

    # save
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    frames[0].save(
        path_out,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0
    )
    print(f"Cropped → {os.path.basename(path_out)}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input_dir",  required=True, help="Folder with original GIFs")
    p.add_argument("--output_dir", required=True, help="Folder to save cropped GIFs")
    p.add_argument("--left",   type=int, default=0, help="Pixels to crop from left")
    p.add_argument("--right",  type=int, default=0, help="Pixels to crop from right")
    p.add_argument("--top",    type=int, default=0, help="Pixels to crop from top")
    p.add_argument("--bottom", type=int, default=0, help="Pixels to crop from bottom")
    args = p.parse_args()

    crop = (args.left, args.right, args.top, args.bottom)
    os.makedirs(args.output_dir, exist_ok=True)

    for fname in os.listdir(args.input_dir):
        if not fname.lower().endswith(".gif"):
            continue
        in_path  = os.path.join(args.input_dir, fname)
        out_path = os.path.join(args.output_dir, fname)
        process_gif(in_path, out_path, crop)

if __name__ == "__main__":
    main()