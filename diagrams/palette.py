from PIL import Image, ImageDraw, ImageFont
import os

WIDTH = 1800
ROW_H = 200
SWATCH_W = 260
PADDING = 30
LABEL_H = 40

# --- Current palette ---
current = [
    ("#1e4974", "Navy", "Primary"),
    ("#163b62", "Dark Navy", "Depth"),
    ("#2563ae", "Cobalt", "Action"),
    ("#fea941", "Gold", "Accent"),
]

# --- Modernized palette ---
# Shifted blues: lighter, more vibrant, with more depth range
# Gold: warmer, richer amber that feels premium
# Added: soft surfaces, semantic colors, and a warm neutral
modern_primary = [
    ("#1a3a5c", "Deep Ocean", "Primary Dark"),
    ("#245e8a", "Atlantic Blue", "Primary"),
    ("#3b82c4", "Sky Cobalt", "Primary Light"),
    ("#6aabde", "Morning Mist", "Primary Soft"),
]

modern_accent = [
    ("#e8940a", "Amber Gold", "Accent"),
    ("#f4b03e", "Sunlight", "Accent Light"),
    ("#fcd581", "Golden Glow", "Accent Soft"),
]

modern_neutral = [
    ("#f7f8fa", "Cloud", "Background"),
    ("#edf0f5", "Frost", "Surface"),
    ("#d1d8e3", "Silver", "Border"),
    ("#64748b", "Slate", "Text Secondary"),
    ("#1e293b", "Midnight", "Text Primary"),
]

modern_semantic = [
    ("#10b981", "Emerald", "Success"),
    ("#f59e0b", "Amber", "Warning"),
    ("#ef4444", "Coral", "Error / Missing"),
    ("#8b5cf6", "Violet", "Info / Badge"),
]

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def luminance(rgb):
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])

def draw_palette_row(draw, y, title, colors, font_title, font_label, font_small):
    draw.text((PADDING, y), title, fill="#1e293b", font=font_title)
    y += 50
    x = PADDING
    for hex_color, name, role in colors:
        rgb = hex_to_rgb(hex_color)
        text_color = "#ffffff" if luminance(rgb) < 140 else "#1e293b"
        # Rounded rectangle
        draw.rounded_rectangle([x, y, x + SWATCH_W, y + 120], radius=12, fill=hex_color)
        draw.text((x + 15, y + 15), name, fill=text_color, font=font_label)
        draw.text((x + 15, y + 45), hex_color.upper(), fill=text_color, font=font_small)
        draw.text((x + 15, y + 70), role, fill=text_color, font=font_small)
        x += SWATCH_W + 20
    return y + 140

# Try to find a good font
font_paths = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFPro.ttf",
    "/System/Library/Fonts/SFNS.ttf",
]
font_path = None
for fp in font_paths:
    if os.path.exists(fp):
        font_path = fp
        break

if font_path:
    font_title = ImageFont.truetype(font_path, 28)
    font_label = ImageFont.truetype(font_path, 20)
    font_small = ImageFont.truetype(font_path, 16)
    font_header = ImageFont.truetype(font_path, 36)
else:
    font_title = ImageFont.load_default()
    font_label = font_title
    font_small = font_title
    font_header = font_title

# Calculate height
total_h = 60 + 200 + 200 + 200 + 200 + 200 + 100  # header + 5 sections + footer
img = Image.new('RGB', (WIDTH, total_h), '#ffffff')
draw = ImageDraw.Draw(img)

# Header
draw.text((PADDING, 20), "GNYC Youth — Color Palette Evolution", fill="#1e293b", font=font_header)

y = 80

# Current
draw.text((PADDING, y), "CURRENT PALETTE (Legacy)", fill="#94a3b8", font=font_title)
y += 50
x = PADDING
for hex_color, name, role in current:
    rgb = hex_to_rgb(hex_color)
    text_color = "#ffffff" if luminance(rgb) < 140 else "#1e293b"
    draw.rounded_rectangle([x, y, x + SWATCH_W, y + 120], radius=12, fill=hex_color)
    draw.text((x + 15, y + 15), name, fill=text_color, font=font_label)
    draw.text((x + 15, y + 45), hex_color.upper(), fill=text_color, font=font_small)
    draw.text((x + 15, y + 70), role, fill=text_color, font=font_small)
    x += SWATCH_W + 20
y += 160

# Divider
draw.line([(PADDING, y), (WIDTH - PADDING, y)], fill="#e2e8f0", width=2)
y += 20
draw.text((PADDING, y), "▼  MODERNIZED PALETTE", fill="#3b82c4", font=font_title)
y += 50

# Modern Primary
y = draw_palette_row(draw, y, "PRIMARY — Blues (Depth & Trust)", modern_primary, font_title, font_label, font_small)
y += 20

# Modern Accent
y = draw_palette_row(draw, y, "ACCENT — Golds (Energy & Warmth)", modern_accent, font_title, font_label, font_small)
y += 20

# Modern Neutral
y = draw_palette_row(draw, y, "NEUTRALS — Surfaces & Text", modern_neutral, font_title, font_label, font_small)
y += 20

# Modern Semantic
y = draw_palette_row(draw, y, "SEMANTIC — Status & Feedback", modern_semantic, font_title, font_label, font_small)

# Crop to actual content
img = img.crop((0, 0, WIDTH, y + 40))
img.save("/Users/Darwin/GNYC/gnycyouth/diagrams/color-palette.png", quality=95)
print(f"Saved: {img.size}")
