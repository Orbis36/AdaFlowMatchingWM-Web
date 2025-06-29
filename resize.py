from pathlib import Path
from PIL import Image
import glob

def crop_image(src_path: str | Path,
               top_px: int = 0,
               bottom_px: int = 0,
               left_px: int = 0,
               right_px: int = 0) -> Path:
    """
    按指定像素数裁剪：上、下、左、右。
    保存为 “原名_cropped.扩展名”，返回保存后的路径。
    """
    src_path = Path(src_path)
    img = Image.open(src_path)
    w, h = img.size

    # 尺寸检查
    if w <= left_px + right_px or h <= top_px + bottom_px:
        raise ValueError(
            f"图片尺寸不足：{w}×{h}，"
            f"请求裁剪 (top={top_px}, bottom={bottom_px}, "
            f"left={left_px}, right={right_px})"
        )

    # Pillow crop 参数: (left, upper, right, lower)
    cropped = img.crop((
        left_px,
        top_px,
        w - right_px,
        h - bottom_px
    ))

    out_path = src_path.with_stem(src_path.stem + "_cropped")
    cropped.save(out_path)
    print(f"✅ 已保存: {out_path.resolve()}")
    return out_path


# 示例：上 50、下 80、左 120、右 120

for path in glob.glob("./images/dome_78/*.png"):
    crop_image(path, 380, 30, 70, 70)