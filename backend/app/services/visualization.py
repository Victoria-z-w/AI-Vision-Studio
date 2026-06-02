from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
    "#F8C471", "#82E0AA", "#F1948A", "#AED6F1", "#D7BDE2",
    "#A3E4D7", "#FAD7A0", "#A9CCE3", "#D5F5E3", "#FADBD8",
]


def _get_font(size: int = 16) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()


def draw_yolo_boxes(
    image_path: str | Path, detections: list[dict], line_width: int = 3
) -> Image.Image:
    """Draw detection bounding boxes and labels on the image."""
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = _get_font(14)

    for i, det in enumerate(detections):
        color = COLORS[i % len(COLORS)]
        b = det["bbox"]
        box = [b["x1"], b["y1"], b["x2"], b["y2"]]

        # Draw rectangle
        for offset in range(line_width):
            draw.rectangle(
                [box[0] - offset, box[1] - offset, box[2] + offset, box[3] + offset],
                outline=color,
            )

        # Draw label
        label = f"{det['class_name']} {det['confidence']:.2f}"
        bbox = draw.textbbox((box[0], box[1] - 18), label, font=font)
        draw.rectangle(bbox, fill=color)
        draw.text((box[0], box[1] - 18), label, fill="#FFFFFF", font=font)

    return img


def draw_ocr_boxes(
    image_path: str | Path, regions: list[dict], line_width: int = 2
) -> Image.Image:
    """Draw OCR text region bounding boxes on the image."""
    img = Image.open(image_path).convert("RGB")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    draw = ImageDraw.Draw(img)
    font = _get_font(12)

    for i, region in enumerate(regions):
        color = COLORS[i % len(COLORS)]
        bbox = region["bbox"]
        pts = [tuple(pt) for pt in bbox]

        # Semi-transparent fill
        overlay_draw.polygon(pts, fill=(*_hex_to_rgb(color), 40))

        # Draw outline on main image
        for j in range(len(pts)):
            draw.line([pts[j], pts[(j + 1) % len(pts)]], fill=color, width=line_width)

        # Draw text label
        if region["text"]:
            text = region["text"][:20]
            x, y = pts[0]
            tb = draw.textbbox((x, y - 16), text, font=font)
            draw.rectangle(tb, fill=color)
            draw.text((x, y - 16), text, fill="#FFFFFF", font=font)

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
