"""Creative image preparation (Pillow)."""

from __future__ import annotations

from pathlib import Path

from .builder import resolve_asset


def prepare_image(source: str | Path, crop: str | None = "square", crop_focus: str = "center") -> tuple[bytes, str]:
    """Load an image, optionally center/side-crop it to a square, and export JPEG.

    Returns (jpeg_bytes, filename). Requires Pillow.
    """
    from PIL import Image

    source_path = resolve_asset(str(source))
    if not source_path.is_file():
        raise FileNotFoundError(f"image not found: {source_path}")

    with Image.open(source_path) as image:
        image = image.convert("RGB")
        if crop == "square":
            width, height = image.size
            side = min(width, height)
            if crop_focus == "left":
                left = 0
            elif crop_focus == "right":
                left = width - side
            else:
                left = (width - side) // 2
            top = (height - side) // 2
            image = image.crop((left, top, left + side, top + side))
        max_side = 1600
        if max(image.size) > max_side:
            image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        from io import BytesIO

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=88, optimize=True, progressive=True)
        data = buffer.getvalue()
    filename = f"{source_path.stem}.jpg"
    return data, filename
