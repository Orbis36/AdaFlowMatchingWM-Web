#!/usr/bin/env python3
"""
Assemble a sequence of PNG frames into a GIF, with custom per-frame durations.

- The first frame and the 8th frame each have a duration of 0.5 seconds.
- All other frames have a duration of 1 second.

Usage:
    python frames_to_gif.py \
        --input_dir /path/to/frame_folder \
        --output_gif /path/to/output.gif \
        [--pattern "*.png"]
"""
import os
import argparse
from PIL import Image

def main():
    parser = argparse.ArgumentParser(description="Convert frames in a folder back into a GIF with custom durations.")
    parser.add_argument("--input_dir",  required=True, help="Directory containing frame images")
    parser.add_argument("--output_gif", required=True, help="Path to save the resulting GIF")
    parser.add_argument("--pattern",    default="*.png", help="Glob pattern to match frame files")
    args = parser.parse_args()

    # List and sort frame files
    from glob import glob
    pattern = os.path.join(args.input_dir, args.pattern)
    files = sorted(glob(pattern))
    if not files:
        print(f"No files matching {pattern}")
        return

    # Load images
    images = [Image.open(f).convert("RGBA") for f in files]

    # Build duration list in milliseconds
    durations = []
    for idx, _ in enumerate(images):
        # first (idx=0) and 8th (idx=7) frames: 0.5s = 500ms
        if idx == 0 or idx == 7:
            durations.append(800)
        else:
            durations.append(1200)

    # Save GIF
    os.makedirs(os.path.dirname(args.output_gif), exist_ok=True)
    images[0].save(
        args.output_gif,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0
    )
    print(f"✅ GIF assembled at {args.output_gif} with {len(images)} frames.")

if __name__ == '__main__':
    main()