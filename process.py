#!/usr/bin/env python3
"""
Batch‐process GIFs in a folder by inserting two title frames:
 - Insert a "Condition" frame at the very start
 - Insert a "Forecasting" frame immediately after half of the original frames

Usage:
    python batch_insert_title_frames.py \
      --input_dir /path/to/gifs \
      --output_dir /path/to/modified \
      --font /path/to/font.ttf \
      --font-size 32 \
      --text-color "#000000" \
      --bg-color "#FFFFFF"
"""

import os
import argparse
from PIL import Image, ImageSequence, ImageDraw, ImageFont

def create_title_frame(size, text, font, text_color, bg_color):
    """
    Create a single image of given size with centered text.
    """
    img = Image.new("RGB", size, color=bg_color)
    draw = ImageDraw.Draw(img)
    # calculate text size
    try:
        tw, th = font.getsize(text)
    except AttributeError:
        bbox = draw.textbbox((0,0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x = (size[0] - tw) // 2
    y = (size[1] - th) // 2
    draw.text((x, y), text, font=font, fill=text_color)
    return img

def process_gif(in_path, out_path, font, text_color, bg_color):
    im = Image.open(in_path)
    frames = []
    durations = []

    # extract original frames and durations
    for frame in ImageSequence.Iterator(im):
        durations.append(frame.info.get("duration", 100))
        frames.append(frame.convert("RGB"))

    n = len(frames)
    half_index = n // 2

    # frame size from first frame
    size = frames[0].size

    # create title frames
    cond_frame = create_title_frame(size, "Condition", font, text_color, bg_color)
    fore_frame = create_title_frame(size, "Forecasting", font, text_color, bg_color)

    # build new frame list
    new_frames = []
    new_durations = []

    # insert Condition at start
    new_frames.append(frames[0])
    new_durations.append(500)  # 1s display

    # then original frames up to half
    for i in range(half_index):
        new_frames.append(frames[i])
        new_durations.append(1000)

    # insert Forecasting
    new_frames.append(frames[half_index-1])
    new_durations.append(500)

    # then remaining frames
    for i in range(half_index, n):
        new_frames.append(frames[i])
        new_durations.append(1000)

    # save
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    new_frames[0].save(
        out_path,
        save_all=True,
        append_images=new_frames[1:],
        duration=new_durations,
        loop=0
    )
    print(f"Processed: {os.path.basename(in_path)} → {os.path.basename(out_path)}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input_dir",  required=True, help="Folder of source GIFs")
    p.add_argument("--output_dir", required=True, help="Folder for modified GIFs")
    p.add_argument("--font",      required=True, help="Path to .ttf font file")
    p.add_argument("--font-size", type=int, default=200, help="Font size for titles")
    p.add_argument("--color", default="#000000", help="Title text color")
    p.add_argument("--outline-color",   default="#FFFFFF", help="Background color for title frames")
    args = p.parse_args()

    # load font
    font = ImageFont.truetype(args.font, args.font_size)

    os.makedirs(args.output_dir, exist_ok=True)
    for fname in sorted(os.listdir(args.input_dir)):
        if not fname.lower().endswith(".gif"):
            continue
        in_path  = os.path.join(args.input_dir, fname)
        out_path = os.path.join(args.output_dir, fname)
        process_gif(in_path, out_path, font, args.color, args.outline_color)

if __name__ == "__main__":
    main()

