#!/usr/bin/env python3
"""
GNYC Youth Leader Portal — UI Mockup Generator
Generates high-quality mobile and desktop mockup PNGs using Pillow.
All screens rendered at 2x for Retina quality.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mockups")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Scale factor (2x for Retina)
# ---------------------------------------------------------------------------
S = 2  # scale factor

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
C = {
    "primary_dark":  "#1A3A5C",
    "primary":       "#245E8A",
    "primary_light": "#3B82C4",
    "primary_soft":  "#6AABDE",
    "accent":        "#E8940A",
    "accent_light":  "#F4B03E",
    "accent_soft":   "#FCD581",
    "bg":            "#F7F8FA",
    "surface":       "#EDF0F5",
    "border":        "#D1D8E3",
    "text2":         "#64748B",
    "text1":         "#1E293B",
    "success":       "#10B981",
    "warning":       "#F59E0B",
    "error":         "#EF4444",
    "info":          "#8B5CF6",
    "white":         "#FFFFFF",
}

# Lighter tints for backgrounds
C["success_bg"] = "#D1FAE5"
C["warning_bg"] = "#FEF3C7"
C["error_bg"]   = "#FEE2E2"
C["info_bg"]    = "#E0E7FF"
C["accent_bg"]  = "#FFF7E6"
C["primary_bg"] = "#E8F4FD"

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"

def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size * S, index=1 if bold else 0)

def font_light(size):
    return ImageFont.truetype(FONT_PATH, size * S, index=4)

# Pre-build commonly used sizes
F10 = font(10); F10B = font(10, True)
F11 = font(11); F11B = font(11, True)
F12 = font(12); F12B = font(12, True)
F13 = font(13); F13B = font(13, True)
F14 = font(14); F14B = font(14, True)
F15 = font(15); F15B = font(15, True)
F16 = font(16); F16B = font(16, True)
F17 = font(17); F17B = font(17, True)
F18 = font(18); F18B = font(18, True)
F20 = font(20); F20B = font(20, True)
F22 = font(22); F22B = font(22, True)
F24 = font(24); F24B = font(24, True)
F28 = font(28); F28B = font(28, True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def s(v):
    """Scale a value."""
    return int(v * S)

def new_canvas(w, h, bg=None):
    """Create a new RGBA canvas at 2x resolution."""
    img = Image.new("RGBA", (s(w), s(h)), bg or C["bg"])
    draw = ImageDraw.Draw(img)
    return img, draw

def rounded_rect(draw, xy, fill=None, outline=None, r=12, width=1):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = [s(v) for v in xy]
    r = s(r)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=s(width) if outline else 0)

def card_shadow(draw, xy, r=12):
    """Simulate a subtle card shadow by drawing a slightly offset darker rect."""
    x0, y0, x1, y1 = xy
    # Draw shadow layer
    rounded_rect(draw, (x0+1, y0+2, x1+1, y1+2), fill="#D8DCE4", r=r)
    # Draw card
    rounded_rect(draw, (x0, y0, x1, y1), fill=C["white"], r=r)

def draw_status_bar(draw, w=390):
    """Draw a minimal iOS-style status bar."""
    # Background already handled by top bar usually
    # Time
    draw.text((s(20), s(6)), "9:41", fill=C["white"], font=F13B)
    # Battery outline
    bx = s(w - 40)
    by = s(7)
    bw, bh = s(22), s(11)
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=s(2), outline=C["white"], width=s(1))
    draw.rounded_rectangle([bx+s(2), by+s(2), bx+bw-s(2), by+bh-s(2)], radius=s(1), fill=C["white"])
    # Battery nub
    draw.rectangle([bx+bw+s(1), by+s(3), bx+bw+s(3), by+bh-s(3)], fill=C["white"])
    # Signal dots
    for i in range(4):
        cx = s(w - 80 + i*7)
        draw.ellipse([cx, by+s(2), cx+s(5), by+s(7)], fill=C["white"])

def draw_top_bar(draw, w=390, title="GNYC Youth", show_bell=False):
    """Draw the app top bar (Primary Dark)."""
    h = 48
    rounded_rect(draw, (0, 0, w, h + 20), fill=C["primary_dark"], r=0)
    # Overlap status bar area
    draw.rectangle([0, 0, s(w), s(h+20)], fill=C["primary_dark"])
    draw_status_bar(draw, w)
    # Title
    draw.text((s(20), s(26)), title, fill=C["white"], font=F18B)
    if show_bell:
        # Simple bell icon (triangle + circle)
        bx = s(w - 45)
        by = s(30)
        draw.polygon([(bx, by+s(14)), (bx+s(7), by), (bx+s(14), by+s(14))], fill=C["accent"])
        draw.ellipse([bx+s(4), by+s(14), bx+s(10), by+s(18)], fill=C["accent"])
        # Notification dot
        draw.ellipse([bx+s(11), by-s(2), bx+s(17), by+s(4)], fill=C["error"])
    return h + 20

def draw_back_title_bar(draw, title, w=390, right_icon=None):
    """Draw a top bar with back arrow and title."""
    h = 48
    draw.rectangle([0, 0, s(w), s(h+20)], fill=C["primary_dark"])
    draw_status_bar(draw, w)
    # Back arrow
    ax, ay = s(16), s(34)
    draw.line([(ax+s(8), ay-s(5)), (ax, ay), (ax+s(8), ay+s(5))], fill=C["white"], width=s(2))
    # Title
    draw.text((s(40), s(26)), title, fill=C["white"], font=F18B)
    if right_icon == "filter":
        ix = s(w - 40)
        iy = s(30)
        for i in range(3):
            lw = s(16 - i*4)
            draw.line([(ix, iy+s(i*5)), (ix+lw, iy+s(i*5))], fill=C["white"], width=s(2))
    elif right_icon == "download":
        ix = s(w - 35)
        iy = s(28)
        draw.line([(ix+s(7), iy), (ix+s(7), iy+s(10))], fill=C["white"], width=s(2))
        draw.line([(ix+s(3), iy+s(7)), (ix+s(7), iy+s(11)), (ix+s(11), iy+s(7))], fill=C["white"], width=s(2))
        draw.line([(ix, iy+s(13)), (ix+s(14), iy+s(13))], fill=C["white"], width=s(2))
    return h + 20

def draw_bottom_nav(draw, w, y, items, active_idx=0):
    """Draw bottom navigation bar."""
    bar_h = 60
    # Bar bg
    draw.rectangle([0, s(y), s(w), s(y + bar_h)], fill=C["white"])
    draw.line([(0, s(y)), (s(w), s(y))], fill=C["border"], width=s(1))
    iw = w // len(items)
    for i, (label, icon_type) in enumerate(items):
        cx = iw * i + iw // 2
        cy = y + 14
        is_active = (i == active_idx)
        color = C["accent"] if is_active else C["text2"]
        # Simple icon shapes
        ix = s(cx - 8)
        iy = s(cy)
        if icon_type == "home":
            # House
            draw.polygon([(ix, iy+s(10)), (ix+s(8), iy), (ix+s(16), iy+s(10))], fill=color)
            draw.rectangle([ix+s(3), iy+s(10), ix+s(13), iy+s(16)], fill=color)
        elif icon_type == "people":
            # Two circles
            draw.ellipse([ix+s(4), iy, ix+s(12), iy+s(8)], fill=color)
            draw.ellipse([ix+s(1), iy+s(9), ix+s(15), iy+s(17)], fill=color)
        elif icon_type == "chart":
            # Bar chart
            draw.rectangle([ix+s(1), iy+s(8), ix+s(5), iy+s(16)], fill=color)
            draw.rectangle([ix+s(6), iy+s(4), ix+s(10), iy+s(16)], fill=color)
            draw.rectangle([ix+s(11), iy+s(0), ix+s(15), iy+s(16)], fill=color)
        elif icon_type == "chat":
            draw.rounded_rectangle([ix, iy, ix+s(16), iy+s(12)], radius=s(3), fill=color)
            draw.polygon([(ix+s(3), iy+s(12)), (ix+s(6), iy+s(16)), (ix+s(9), iy+s(12))], fill=color)
        elif icon_type == "forms":
            draw.rounded_rectangle([ix+s(2), iy, ix+s(14), iy+s(16)], radius=s(2), fill=color)
            draw.line([(ix+s(5), iy+s(5)), (ix+s(11), iy+s(5))], fill=C["white"], width=s(1))
            draw.line([(ix+s(5), iy+s(8)), (ix+s(11), iy+s(8))], fill=C["white"], width=s(1))
            draw.line([(ix+s(5), iy+s(11)), (ix+s(9), iy+s(11))], fill=C["white"], width=s(1))
        elif icon_type == "profile":
            draw.ellipse([ix+s(5), iy, ix+s(11), iy+s(6)], fill=color)
            draw.ellipse([ix+s(2), iy+s(8), ix+s(14), iy+s(17)], fill=color)
        # Label
        tw = draw.textlength(label, font=F10)
        draw.text((s(cx) - tw//2, s(y + 38)), label, fill=color, font=F10B if is_active else F10)

def draw_people_icon(draw, x, y, size, color):
    """Draw a simple people/group icon."""
    sz = s(size)
    x, y = s(x), s(y)
    # Person 1 (center)
    draw.ellipse([x+sz//3, y, x+sz*2//3, y+sz//3], fill=color)
    draw.rounded_rectangle([x+sz//4, y+sz//3, x+sz*3//4, y+sz*3//4], radius=sz//8, fill=color)
    # Person 2 (left, smaller)
    off = -sz//5
    draw.ellipse([x+sz//5+off, y+sz//8, x+sz//2+off-sz//10, y+sz//3+sz//8], fill=color)
    draw.rounded_rectangle([x+sz//6+off, y+sz//3+sz//8, x+sz//2+off, y+sz*3//4], radius=sz//10, fill=color)

def draw_checkmark(draw, cx, cy, size, color):
    """Draw a checkmark."""
    s2 = s(size)
    cx, cy = s(cx), s(cy)
    draw.line([(cx-s2//2, cy), (cx-s2//6, cy+s2//3), (cx+s2//2, cy-s2//3)], fill=color, width=max(2, s2//4))

def draw_x_mark(draw, cx, cy, size, color):
    """Draw an X mark."""
    s2 = s(size)
    cx, cy = s(cx), s(cy)
    draw.line([(cx-s2//3, cy-s2//3), (cx+s2//3, cy+s2//3)], fill=color, width=max(2, s2//4))
    draw.line([(cx+s2//3, cy-s2//3), (cx-s2//3, cy+s2//3)], fill=color, width=max(2, s2//4))

def draw_clock_icon(draw, cx, cy, size, color):
    """Draw a clock/pending icon."""
    s2 = s(size)
    cx, cy = s(cx), s(cy)
    draw.ellipse([cx-s2//2, cy-s2//2, cx+s2//2, cy+s2//2], outline=color, width=max(2, s2//6))
    draw.line([(cx, cy-s2//4), (cx, cy), (cx+s2//4, cy)], fill=color, width=max(2, s2//6))

def draw_status_circle(draw, cx, cy, r, status):
    """Draw a colored status circle with icon inside."""
    cx_s, cy_s, r_s = s(cx), s(cy), s(r)
    if status == "ok":
        draw.ellipse([cx_s-r_s, cy_s-r_s, cx_s+r_s, cy_s+r_s], fill=C["success"])
        # checkmark inside
        draw.line([(cx_s-r_s//2, cy_s), (cx_s-r_s//6, cy_s+r_s//3), (cx_s+r_s//2, cy_s-r_s//3)],
                  fill=C["white"], width=max(2, r_s//3))
    elif status == "pending":
        draw.ellipse([cx_s-r_s, cy_s-r_s, cx_s+r_s, cy_s+r_s], fill=C["warning"])
        # clock
        draw.line([(cx_s, cy_s-r_s//3), (cx_s, cy_s), (cx_s+r_s//3, cy_s)],
                  fill=C["white"], width=max(2, r_s//3))
    elif status == "missing":
        draw.ellipse([cx_s-r_s, cy_s-r_s, cx_s+r_s, cy_s+r_s], fill=C["error"])
        # x
        d = r_s // 3
        draw.line([(cx_s-d, cy_s-d), (cx_s+d, cy_s+d)], fill=C["white"], width=max(2, r_s//3))
        draw.line([(cx_s+d, cy_s-d), (cx_s-d, cy_s+d)], fill=C["white"], width=max(2, r_s//3))

def text_width(draw, text, f):
    return draw.textlength(text, font=f)


# ============================================================================
# Screen 1: Director Dashboard
# ============================================================================
def screen_01():
    W, H = 390, 844
    img, d = new_canvas(W, H)

    # Top bar
    bar_h = draw_top_bar(d, W, "GNYC Youth", show_bell=True)

    # Greeting area
    y = bar_h + 16
    d.text((s(20), s(y)), "Good morning, Pastor Rivera", fill=C["text1"], font=F20B)
    y += 30
    d.text((s(20), s(y)), "Brooklyn Spanish SDA \u00b7 Pathfinders", fill=C["text2"], font=F14)
    y += 36

    # --- 3 stat cards ---
    card_w = 110
    gap = 10
    start_x = 20
    card_h = 80

    # Card 1: Active Youth
    cx = start_x
    card_shadow(d, (cx, y, cx+card_w, y+card_h), r=10)
    draw_people_icon(d, cx+12, y+12, 22, C["primary"])
    d.text((s(cx+12), s(y+40)), "12", fill=C["text1"], font=F22B)
    d.text((s(cx+12), s(y+62)), "Active Youth", fill=C["text2"], font=F10)

    # Card 2: Forms Pending (amber bg)
    cx = start_x + card_w + gap
    card_shadow(d, (cx, y, cx+card_w, y+card_h), r=10)
    # Amber tint overlay
    rounded_rect(d, (cx, y, cx+card_w, y+card_h), fill=C["accent_bg"], r=10)
    # Form icon
    ix, iy = s(cx+12), s(y+12)
    d.rounded_rectangle([ix, iy, ix+s(18), iy+s(22)], radius=s(3), fill=C["accent"])
    d.line([(ix+s(4), iy+s(7)), (ix+s(14), iy+s(7))], fill=C["white"], width=s(1))
    d.line([(ix+s(4), iy+s(11)), (ix+s(14), iy+s(11))], fill=C["white"], width=s(1))
    d.line([(ix+s(4), iy+s(15)), (ix+s(10), iy+s(15))], fill=C["white"], width=s(1))
    d.text((s(cx+12), s(y+40)), "3", fill=C["text1"], font=F22B)
    d.text((s(cx+12), s(y+62)), "Forms Pending", fill=C["text2"], font=F10)

    # Card 3: Report Due
    cx = start_x + 2*(card_w + gap)
    card_shadow(d, (cx, y, cx+card_w, y+card_h), r=10)
    # Urgency indicator — red left accent
    d.rounded_rectangle([s(cx), s(y), s(cx+4), s(y+card_h)], radius=s(2), fill=C["error"])
    # Calendar icon
    ix, iy = s(cx+14), s(y+12)
    d.rounded_rectangle([ix, iy, ix+s(18), iy+s(20)], radius=s(3), outline=C["error"], width=s(2))
    d.rectangle([ix, iy, ix+s(18), iy+s(6)], fill=C["error"])
    d.text((ix+s(4), iy+s(8)), "5", fill=C["error"], font=F11B)
    d.text((s(cx+14), s(y+38)), "Report Due", fill=C["text1"], font=F11B)
    d.text((s(cx+14), s(y+52)), "Apr 5", fill=C["error"], font=F14B)
    d.text((s(cx+14), s(y+68)), "2 days left", fill=C["text2"], font=F10)

    y += card_h + 30

    # --- Quick Actions ---
    d.text((s(20), s(y)), "Quick Actions", fill=C["text1"], font=F17B)
    y += 30

    # Button 1: Submit Monthly Report (primary filled)
    btn_h = 54
    rounded_rect(d, (20, y, W-20, y+btn_h), fill=C["primary"], r=14)
    # Icon
    ix, iy = s(36), s(y + btn_h//2 - 8)
    d.rounded_rectangle([ix, iy, ix+s(14), iy+s(16)], radius=s(2), fill=C["white"])
    d.line([(ix+s(3), iy+s(5)), (ix+s(11), iy+s(5))], fill=C["primary"], width=s(1))
    d.line([(ix+s(3), iy+s(8)), (ix+s(11), iy+s(8))], fill=C["primary"], width=s(1))
    d.line([(ix+s(3), iy+s(11)), (ix+s(8), iy+s(11))], fill=C["primary"], width=s(1))
    d.text((s(60), s(y + btn_h//2 - 9)), "Submit Monthly Report", fill=C["white"], font=F16B)
    # Arrow
    ax = s(W - 42)
    ay = s(y + btn_h//2)
    d.line([(ax, ay-s(4)), (ax+s(6), ay), (ax, ay+s(4))], fill=C["white"], width=s(2))
    y += btn_h + 12

    # Button 2: View Roster
    rounded_rect(d, (20, y, W-20, y+btn_h), fill=C["white"], outline=C["primary"], r=14, width=1.5)
    draw_people_icon(d, 28, y + btn_h//2 - 11, 20, C["primary"])
    d.text((s(60), s(y + btn_h//2 - 9)), "View Roster", fill=C["primary"], font=F16B)
    ax = s(W - 42)
    ay = s(y + btn_h//2)
    d.line([(ax, ay-s(4)), (ax+s(6), ay), (ax, ay+s(4))], fill=C["primary"], width=s(2))
    y += btn_h + 12

    # Button 3: Contact Coordinator
    rounded_rect(d, (20, y, W-20, y+btn_h), fill=C["white"], outline=C["primary"], r=14, width=1.5)
    # Chat icon
    ix, iy = s(30), s(y + btn_h//2 - 8)
    d.rounded_rectangle([ix, iy, ix+s(18), iy+s(13)], radius=s(4), fill=C["primary"])
    d.polygon([(ix+s(3), iy+s(13)), (ix+s(6), iy+s(17)), (ix+s(9), iy+s(13))], fill=C["primary"])
    d.text((s(60), s(y + btn_h//2 - 9)), "Contact Coordinator", fill=C["primary"], font=F16B)
    ax = s(W - 42)
    ay = s(y + btn_h//2)
    d.line([(ax, ay-s(4)), (ax+s(6), ay), (ax, ay+s(4))], fill=C["primary"], width=s(2))

    # --- Bottom nav ---
    nav_items = [("Home", "home"), ("Roster", "people"), ("Reports", "chart"), ("Chat", "chat")]
    draw_bottom_nav(d, W, H - 60, nav_items, active_idx=0)

    img.save(os.path.join(OUT_DIR, "01-director-dashboard.png"), dpi=(144, 144))
    print("  01-director-dashboard.png")


# ============================================================================
# Screen 2: Monthly Report (Step 1)
# ============================================================================
def screen_02():
    W, H = 390, 844
    img, d = new_canvas(W, H)

    bar_h = draw_back_title_bar(d, "Monthly Report", W)

    y = bar_h + 8
    # Month label
    d.text((s(W//2 - 30), s(y)), "April 2026", fill=C["text2"], font=F14)
    y += 28

    # Progress dots
    steps = ["Membership", "Service", "Education", "Review"]
    dot_r = 8
    spacing = 80
    start_x = (W - spacing * (len(steps)-1)) // 2
    for i, label in enumerate(steps):
        cx = start_x + i * spacing
        cx_s, cy_s = s(cx), s(y + dot_r)
        r_s = s(dot_r)
        if i == 0:
            d.ellipse([cx_s-r_s, cy_s-r_s, cx_s+r_s, cy_s+r_s], fill=C["accent"])
            d.text((cx_s - s(2), cy_s - s(5)), "1", fill=C["white"], font=F10B)
        else:
            d.ellipse([cx_s-r_s, cy_s-r_s, cx_s+r_s, cy_s+r_s], fill=C["border"])
            d.text((cx_s - s(2), cy_s - s(5)), str(i+1), fill=C["text2"], font=F10)
        # Line between dots
        if i < len(steps)-1:
            d.line([(cx_s+r_s+s(4), cy_s), (s(start_x + (i+1)*spacing)-r_s-s(4), cy_s)],
                   fill=C["accent"] if i == 0 else C["border"], width=s(2))
        # Label below dot
        tw = text_width(d, label, F10)
        d.text((cx_s - tw//2, cy_s + r_s + s(6)), label, fill=C["text1"] if i == 0 else C["text2"], font=F10)

    y += 50

    # Section title
    draw_people_icon(d, 22, y+2, 18, C["primary"])
    d.text((s(46), s(y)), "Membership", fill=C["text1"], font=F20B)
    y += 38

    # Number stepper rows
    fields = [
        ("Registered Youth", "12"),
        ("Active Youth", "10"),
        ("New Members", "1"),
        ("Adventurer \u2192 Pathfinder", "0"),
    ]
    for label, val in fields:
        row_h = 60
        # Row card
        card_shadow(d, (20, y, W-20, y+row_h), r=10)
        # Label
        d.text((s(32), s(y + row_h//2 - 8)), label, fill=C["text2"], font=F14)
        # Stepper: [ - ] val [ + ]
        btn_s = 34
        stepper_x = W - 20 - 12 - btn_s - 10 - 30 - 10 - btn_s  # approximate
        sx = W - 20 - 12 - btn_s
        # Plus button
        rounded_rect(d, (sx, y + row_h//2 - btn_s//2, sx + btn_s, y + row_h//2 + btn_s//2),
                     fill=C["primary_bg"], r=8)
        d.text((s(sx + btn_s//2 - 4), s(y + row_h//2 - 9)), "+", fill=C["primary"], font=F18B)
        # Value
        vx = sx - 10 - 30
        d.text((s(vx + 8), s(y + row_h//2 - 10)), val, fill=C["text1"], font=F20B)
        # Minus button
        mx = vx - 10 - btn_s
        rounded_rect(d, (mx, y + row_h//2 - btn_s//2, mx + btn_s, y + row_h//2 + btn_s//2),
                     fill=C["surface"], r=8)
        d.text((s(mx + btn_s//2 - 5), s(y + row_h//2 - 10)), "\u2013", fill=C["text2"], font=F18B)

        y += row_h + 10

    y += 6

    # Info box
    info_h = 50
    rounded_rect(d, (20, y, W-20, y+info_h), fill=C["info_bg"], r=10)
    # Info icon (circle with i)
    icx, icy = s(38), s(y + info_h//2)
    d.ellipse([icx-s(8), icy-s(8), icx+s(8), icy+s(8)], fill=C["info"])
    d.text((icx-s(2), icy-s(6)), "i", fill=C["white"], font=F11B)
    d.text((s(54), s(y + 10)), "Pre-filled from March.", fill=C["info"], font=F12B)
    d.text((s(54), s(y + 27)), "Update only what changed.", fill=C["text2"], font=F12)

    y = H - 60 - 16 - 56  # above a hypothetical bottom area

    # Bottom button
    btn_y = H - 90
    rounded_rect(d, (20, btn_y, W-20, btn_y+54), fill=C["primary"], r=14)
    d.text((s(W//2 - 50), s(btn_y + 16)), "Next: Service \u2192", fill=C["white"], font=F17B)

    img.save(os.path.join(OUT_DIR, "02-monthly-report.png"), dpi=(144, 144))
    print("  02-monthly-report.png")


# ============================================================================
# Screen 3: Roster View
# ============================================================================
def screen_03():
    W, H = 390, 844
    img, d = new_canvas(W, H)

    bar_h = draw_back_title_bar(d, "Club Roster", W, right_icon="filter")
    y = bar_h + 12

    # Search bar
    search_h = 40
    rounded_rect(d, (20, y, W-20, y+search_h), fill=C["white"], outline=C["border"], r=20)
    # Search icon (circle + line)
    sx, sy = s(36), s(y + search_h//2 - 1)
    d.ellipse([sx-s(6), sy-s(6), sx+s(6), sy+s(6)], outline=C["text2"], width=s(1.5))
    d.line([(sx+s(4), sy+s(4)), (sx+s(9), sy+s(9))], fill=C["text2"], width=s(1.5))
    d.text((s(50), s(y + search_h//2 - 7)), "Search children...", fill=C["border"], font=F14)
    y += search_h + 14

    # Tab bar
    tabs = [("All (12)", True), ("Forms Pending (3)", False), ("New (1)", False)]
    tx = 20
    for label, active in tabs:
        tw = int(text_width(d, label, F12B if active else F12) / S) + 20
        if active:
            rounded_rect(d, (tx, y, tx+tw, y+32), fill=C["primary"], r=16)
            d.text((s(tx+10), s(y+8)), label, fill=C["white"], font=F12B)
        else:
            rounded_rect(d, (tx, y, tx+tw, y+32), fill=C["surface"], r=16)
            d.text((s(tx+10), s(y+8)), label, fill=C["text2"], font=F12)
        tx += tw + 8
    y += 44

    # Child cards
    children = [
        ("Sofia Martinez", 11, "All Forms Complete", "success"),
        ("David Reyes", 10, "Medical Form Missing", "error"),
        ("Ana Torres", 12, "Consent Pending", "warning"),
        ("Carlos Mendez", 9, "All Forms Complete", "success"),
    ]
    for name, age, status_text, status_type in children:
        card_h = 72
        card_shadow(d, (20, y, W-20, y+card_h), r=12)
        # Avatar circle
        ax_c = 46
        ay_c = y + card_h//2
        d.ellipse([s(ax_c-16), s(ay_c-16), s(ax_c+16), s(ay_c+16)], fill=C["primary_soft"])
        # Initials
        initials = name[0] + name.split()[-1][0]
        tw = text_width(d, initials, F12B)
        d.text((s(ax_c) - tw//2, s(ay_c - 7)), initials, fill=C["white"], font=F12B)
        # Name
        d.text((s(72), s(y + 16)), name, fill=C["text1"], font=F15B)
        # Age + Pathfinder
        d.text((s(72), s(y + 38)), f"Age {age} \u00b7 Pathfinder", fill=C["text2"], font=F12)
        # Status badge
        badge_colors = {
            "success": (C["success_bg"], C["success"]),
            "error": (C["error_bg"], C["error"]),
            "warning": (C["warning_bg"], C["warning"]),
        }
        bg_c, fg_c = badge_colors[status_type]
        btw = int(text_width(d, status_text, F10) / S) + 16
        bx = W - 20 - 14 - btw
        by = y + card_h//2 - 10
        rounded_rect(d, (bx, by, bx+btw, by+20), fill=bg_c, r=10)
        d.text((s(bx+8), s(by+4)), status_text, fill=fg_c, font=F10)
        # Chevron
        cx_chev = s(W - 30)
        cy_chev = s(y + card_h//2)
        d.line([(cx_chev, cy_chev-s(5)), (cx_chev+s(5), cy_chev), (cx_chev, cy_chev+s(5))],
               fill=C["border"], width=s(1.5))

        y += card_h + 10

    img.save(os.path.join(OUT_DIR, "03-roster-view.png"), dpi=(144, 144))
    print("  03-roster-view.png")


# ============================================================================
# Screen 4: Form Status Grid
# ============================================================================
def screen_04():
    W, H = 390, 844
    img, d = new_canvas(W, H)

    bar_h = draw_back_title_bar(d, "Form Status", W, right_icon="download")
    y = bar_h + 14

    # Summary bar
    summary_h = 60
    rounded_rect(d, (20, y, W-20, y+summary_h), fill=C["white"], r=12)
    d.text((s(32), s(y+10)), "8 of 12 children fully cleared", fill=C["text1"], font=F14B)
    # Progress bar
    pb_y = y + 36
    pb_w = W - 20 - 20 - 24
    rounded_rect(d, (32, pb_y, 32+pb_w, pb_y+10), fill=C["surface"], r=5)
    filled_w = int(pb_w * 0.67)
    rounded_rect(d, (32, pb_y, 32+filled_w, pb_y+10), fill=C["success"], r=5)
    # Percentage
    d.text((s(32 + pb_w + 8), s(pb_y - 2)), "67%", fill=C["success"], font=F12B)
    y += summary_h + 20

    # Grid header
    cols = [("Name", 110), ("Medical", 70), ("Photo", 70), ("Permission", 90)]
    cx = 20
    for label, cw in cols:
        d.text((s(cx + 6), s(y)), label, fill=C["text2"], font=F11B)
        cx += cw
    y += 24
    d.line([(s(20), s(y)), (s(W-20), s(y))], fill=C["border"], width=s(1))
    y += 4

    # Rows
    rows = [
        ("Sofia M.",    ["ok", "ok", "ok"]),
        ("David R.",    ["missing", "ok", "ok"]),
        ("Ana T.",      ["ok", "pending", "ok"]),
        ("Carlos M.",   ["ok", "ok", "ok"]),
        ("Maria S.",    ["ok", "ok", "pending"]),
        ("Luis G.",     ["missing", "missing", "missing"]),
    ]
    row_h = 48
    for i, (name, statuses) in enumerate(rows):
        ry = y + i * row_h
        # Alternating background
        if i % 2 == 1:
            rounded_rect(d, (20, ry, W-20, ry+row_h), fill=C["surface"], r=0)
        # Name
        d.text((s(26), s(ry + row_h//2 - 7)), name, fill=C["text1"], font=F13B)
        # Status circles
        col_offsets = [110, 180, 250]
        for j, st in enumerate(statuses):
            cx = 20 + col_offsets[j] + 20
            cy = ry + row_h//2
            draw_status_circle(d, cx, cy, 11, st)

        # Separator
        d.line([(s(20), s(ry+row_h)), (s(W-20), s(ry+row_h))], fill=C["border"], width=s(1))

    y += len(rows) * row_h + 10

    # Legend
    legend_y = y + 10
    items = [("Complete", "ok"), ("Pending", "pending"), ("Missing", "missing")]
    lx = 30
    for label, st in items:
        draw_status_circle(d, lx + 6, legend_y + 6, 6, st)
        d.text((s(lx + 16), s(legend_y)), label, fill=C["text2"], font=F11)
        lx += 100

    # Bottom button
    btn_y = H - 90
    rounded_rect(d, (20, btn_y, W-20, btn_y+54), fill=C["accent"], r=14)
    tw = text_width(d, "Send Reminder to Parents", F16B)
    d.text((s(W//2) - tw//2, s(btn_y + 16)), "Send Reminder to Parents", fill=C["white"], font=F16B)

    img.save(os.path.join(OUT_DIR, "04-form-status-grid.png"), dpi=(144, 144))
    print("  04-form-status-grid.png")


# ============================================================================
# Screen 5: Parent Portal
# ============================================================================
def screen_05():
    W, H = 390, 844
    img, d = new_canvas(W, H)

    bar_h = draw_top_bar(d, W, "GNYC Youth")
    y = bar_h + 16

    # Greeting
    d.text((s(20), s(y)), "Welcome, Maria Santos", fill=C["text1"], font=F20B)
    y += 36

    # Section heading
    d.text((s(20), s(y)), "My Children", fill=C["text1"], font=F17B)
    y += 32

    # Card 1: Sofia — complete (green left border)
    card_h = 76
    card_shadow(d, (20, y, W-20, y+card_h), r=12)
    # Green left border
    d.rounded_rectangle([s(20), s(y), s(26), s(y+card_h)], radius=s(4), fill=C["success"])
    # Avatar
    ax_c, ay_c = 48, y + card_h//2
    d.ellipse([s(ax_c-16), s(ay_c-16), s(ax_c+16), s(ay_c+16)], fill=C["primary_soft"])
    d.text((s(ax_c-8), s(ay_c-7)), "SM", fill=C["white"], font=F12B)
    # Name & details
    d.text((s(74), s(y+16)), "Sofia Martinez", fill=C["text1"], font=F16B)
    d.text((s(74), s(y+38)), "Age 11 \u00b7 Pathfinder", fill=C["text2"], font=F13)
    # Badge
    badge_text = "All forms complete \u2713"
    btw = int(text_width(d, badge_text, F10) / S) + 16
    bx = W - 20 - 12 - btw
    rounded_rect(d, (bx, y + card_h//2 - 10, bx+btw, y + card_h//2 + 10), fill=C["success_bg"], r=10)
    d.text((s(bx+8), s(y + card_h//2 - 6)), badge_text, fill=C["success"], font=F10)
    # Chevron
    d.line([(s(W-30), s(y+card_h//2-5)), (s(W-25), s(y+card_h//2)), (s(W-30), s(y+card_h//2+5))],
           fill=C["border"], width=s(1.5))
    y += card_h + 12

    # Card 2: Lucas — expanded (amber left border)
    # Main card
    card_h_main = 76
    expanded_h = 180
    total_h = card_h_main + expanded_h
    card_shadow(d, (20, y, W-20, y+total_h), r=12)
    # Amber left border
    d.rounded_rectangle([s(20), s(y), s(26), s(y+total_h)], radius=s(4), fill=C["warning"])
    # Avatar
    ax_c, ay_c = 48, y + card_h_main//2
    d.ellipse([s(ax_c-16), s(ay_c-16), s(ax_c+16), s(ay_c+16)], fill=C["accent_soft"])
    d.text((s(ax_c-9), s(ay_c-7)), "LM", fill=C["white"], font=F12B)
    # Name & details
    d.text((s(74), s(y+16)), "Lucas Martinez", fill=C["text1"], font=F16B)
    d.text((s(74), s(y+38)), "Age 8 \u00b7 Adventurer", fill=C["text2"], font=F13)
    # Badge
    badge_text = "1 form needed"
    btw = int(text_width(d, badge_text, F10) / S) + 16
    bx = W - 20 - 12 - btw
    rounded_rect(d, (bx, y + card_h_main//2 - 10, bx+btw, y + card_h_main//2 + 10),
                 fill=C["warning_bg"], r=10)
    d.text((s(bx+8), s(y + card_h_main//2 - 6)), badge_text, fill=C["warning"], font=F10)

    # Divider
    div_y = y + card_h_main
    d.line([(s(36), s(div_y)), (s(W-36), s(div_y))], fill=C["border"], width=s(1))

    # Expanded form rows
    forms = [
        ("Medical Authorization", "\u2713 Submitted Mar 15", "success", False),
        ("Photo Consent", "\u2713 Submitted Mar 15", "success", False),
        ("Permission Slip", "Action needed", "warning", True),
    ]
    fy = div_y + 14
    for form_name, status_text, status_type, has_action in forms:
        # Form name
        d.text((s(40), s(fy)), form_name, fill=C["text1"], font=F13B)
        # Status
        color = C["success"] if status_type == "success" else C["warning"]
        d.text((s(40), s(fy + 18)), status_text, fill=color, font=F12)
        if has_action:
            # "Fill Out Now" button
            btn_text = "Fill Out Now \u2192"
            btw = int(text_width(d, btn_text, F12B) / S) + 20
            bx = W - 20 - 12 - btw
            rounded_rect(d, (bx, fy + 4, bx+btw, fy+30), fill=C["accent"], r=8)
            d.text((s(bx+10), s(fy+10)), btn_text, fill=C["white"], font=F12B)
        fy += 48

    # Bottom nav
    nav_items = [("My Children", "people"), ("Forms", "forms"), ("Profile", "profile")]
    draw_bottom_nav(d, W, H - 60, nav_items, active_idx=0)

    img.save(os.path.join(OUT_DIR, "05-parent-portal.png"), dpi=(144, 144))
    print("  05-parent-portal.png")


# ============================================================================
# Screen 6: Coordinator Dashboard (Desktop)
# ============================================================================
def screen_06():
    W, H = 1280, 800
    img, d = new_canvas(W, H)

    # --- Left sidebar ---
    sidebar_w = 220
    d.rectangle([0, 0, s(sidebar_w), s(H)], fill=C["primary_dark"])
    # Logo area
    d.text((s(24), s(24)), "GNYC Youth", fill=C["white"], font=F20B)
    d.text((s(24), s(50)), "Ministries", fill=C["primary_soft"], font=F13)

    # Nav items
    nav = [
        ("Dashboard", True),
        ("Clubs", False),
        ("Reports", False),
        ("Directors", False),
        ("Settings", False),
    ]
    nav_icons = ["home", "people", "chart", "profile", "forms"]  # reuse icon types loosely
    ny = 100
    for i, (label, active) in enumerate(nav):
        if active:
            # Active indicator
            d.rectangle([0, s(ny), s(4), s(ny+40)], fill=C["accent"])
            d.rectangle([0, s(ny), s(sidebar_w), s(ny+40)], fill="#1F4568")
        # Icon placeholder (small square)
        icon_color = C["accent"] if active else C["primary_soft"]
        d.rounded_rectangle([s(24), s(ny+10), s(42), s(ny+28)], radius=s(3), fill=icon_color)
        # Label
        text_color = C["white"] if active else C["primary_soft"]
        d.text((s(52), s(ny+11)), label, fill=text_color, font=F14B if active else F14)
        ny += 44

    # --- Top bar ---
    content_x = sidebar_w
    top_h = 56
    d.rectangle([s(content_x), 0, s(W), s(top_h)], fill=C["white"])
    d.line([(s(content_x), s(top_h)), (s(W), s(top_h))], fill=C["border"], width=s(1))
    d.text((s(content_x + 24), s(16)), "Area Dashboard \u2014 Brooklyn", fill=C["text1"], font=F18B)
    d.text((s(W - 180), s(18)), "Coord. Jimenez", fill=C["text2"], font=F14)
    # Avatar circle
    d.ellipse([s(W-40), s(12), s(W-8), s(44)], fill=C["primary_soft"])
    d.text((s(W-31), s(18)), "CJ", fill=C["white"], font=F12B)

    # --- Main content ---
    cx = content_x + 24
    cy = top_h + 24
    content_w = W - content_x - 48

    # Stat cards row
    card_count = 4
    card_gap = 16
    card_w = (content_w - card_gap * (card_count - 1)) // card_count
    card_h = 90

    stats = [
        ("8", "Clubs", C["primary"], C["primary_bg"]),
        ("156", "Active Youth", C["primary"], C["primary_bg"]),
        ("6 of 8", "Reports In", C["warning"], C["warning_bg"]),
        ("94%", "Forms Complete", C["success"], C["success_bg"]),
    ]
    for i, (val, label, color, bg_color) in enumerate(stats):
        sx = cx + i * (card_w + card_gap)
        card_shadow(d, (sx, cy, sx+card_w, cy+card_h), r=10)
        # Colored top accent
        d.rounded_rectangle([s(sx), s(cy), s(sx+card_w), s(cy+4)], radius=s(2), fill=color)
        d.text((s(sx+16), s(cy+20)), val, fill=color, font=F28B)
        d.text((s(sx+16), s(cy+58)), label, fill=C["text2"], font=F13)

    cy += card_h + 28

    # Club Health Overview table
    d.text((s(cx), s(cy)), "Club Health Overview", fill=C["text1"], font=F18B)
    cy += 32

    # Table
    table_cols = [
        ("Club Name", 220),
        ("Director", 140),
        ("Youth", 60),
        ("Report Status", 130),
        ("Forms", 70),
        ("Health", 60),
    ]
    # Header
    hx = cx
    header_h = 36
    rounded_rect(d, (cx, cy, cx+content_w, cy+header_h), fill=C["surface"], r=6)
    for label, cw in table_cols:
        d.text((s(hx + 12), s(cy + 10)), label, fill=C["text2"], font=F12B)
        hx += cw
    cy += header_h + 2

    # Table rows
    table_rows = [
        ("Brooklyn Spanish SDA", "Pastor Rivera", "12", ("\u2713 Submitted", "success"), "100%", "success"),
        ("Flatbush Haitian SDA", "Dir. Jean", "24", ("\u2713 Submitted", "success"), "88%", "success"),
        ("Crown Heights SDA", "Dir. Williams", "18", ("\u25f7 Pending", "warning"), "72%", "warning"),
        ("Canarsie SDA", "Dir. Lopez", "15", ("\u2717 Overdue", "error"), "65%", "error"),
    ]
    row_h = 46
    for i, (club, director, youth, (report_text, report_status), forms_pct, health) in enumerate(table_rows):
        ry = cy + i * row_h
        bg = C["white"] if i % 2 == 0 else C["surface"]
        rounded_rect(d, (cx, ry, cx+content_w, ry+row_h), fill=bg, r=0)
        rx = cx
        # Club name
        d.text((s(rx+12), s(ry+14)), club, fill=C["text1"], font=F13B)
        rx += table_cols[0][1]
        # Director
        d.text((s(rx+12), s(ry+14)), director, fill=C["text2"], font=F13)
        rx += table_cols[1][1]
        # Youth count
        d.text((s(rx+12), s(ry+14)), youth, fill=C["text1"], font=F13)
        rx += table_cols[2][1]
        # Report status badge
        status_colors = {
            "success": (C["success_bg"], C["success"]),
            "warning": (C["warning_bg"], C["warning"]),
            "error": (C["error_bg"], C["error"]),
        }
        bg_c, fg_c = status_colors[report_status]
        btw = int(text_width(d, report_text, F11) / S) + 14
        rounded_rect(d, (rx+8, ry+12, rx+8+btw, ry+32), fill=bg_c, r=8)
        d.text((s(rx+15), s(ry+14)), report_text, fill=fg_c, font=F11)
        rx += table_cols[3][1]
        # Forms %
        d.text((s(rx+12), s(ry+14)), forms_pct, fill=C["text1"], font=F13B)
        rx += table_cols[4][1]
        # Health dot
        dot_color = status_colors[health][1]
        dot_cx = rx + 30
        dot_cy = ry + row_h//2
        d.ellipse([s(dot_cx-5), s(dot_cy-5), s(dot_cx+5), s(dot_cy+5)], fill=dot_color)

        # Row separator
        d.line([(s(cx), s(ry+row_h)), (s(cx+content_w), s(ry+row_h))], fill=C["border"], width=s(1))

    img.save(os.path.join(OUT_DIR, "06-coordinator-dashboard.png"), dpi=(144, 144))
    print("  06-coordinator-dashboard.png")


# ============================================================================
# Screen 7: AI Assistant Chat
# ============================================================================
def screen_07():
    W, H = 390, 844
    img, d = new_canvas(W, H)

    # Dimmed background (simulate underlying screen)
    d.rectangle([0, 0, s(W), s(H)], fill="#F0F1F3")
    # Some fake content behind
    d.rectangle([0, 0, s(W), s(68)], fill=C["primary_dark"])
    d.text((s(20), s(26)), "GNYC Youth", fill=C["white"], font=F18B)
    # Fake cards behind
    for fy in [90, 170, 250]:
        rounded_rect(d, (20, fy, W-20, fy+60), fill=C["white"], r=10)
    # Dim overlay
    overlay = Image.new("RGBA", (s(W), s(H)), (0, 0, 0, 100))
    img = Image.alpha_composite(img, overlay)
    d = ImageDraw.Draw(img)

    # Chat window — bottom 75% of screen
    chat_top = 190
    # Chat background with rounded top corners
    d.rounded_rectangle([0, s(chat_top), s(W), s(H)], radius=s(20), fill=C["white"])

    # Drag indicator
    d.rounded_rectangle([s(W//2 - 20), s(chat_top + 10), s(W//2 + 20), s(chat_top + 14)],
                        radius=s(2), fill=C["border"])

    # Chat header
    y = chat_top + 24
    # AI icon (sparkle)
    aix, aiy = s(24), s(y)
    d.ellipse([aix, aiy, aix+s(28), aiy+s(28)], fill=C["info"])
    d.text((aix+s(7), aiy+s(4)), "\u2727", fill=C["white"], font=F16B)
    # Title
    d.text((s(60), s(y + 2)), "GNYC Youth Assistant", fill=C["text1"], font=F16B)
    d.text((s(60), s(y + 20)), "AI-powered help", fill=C["text2"], font=F11)
    # Close button
    cx_btn = s(W - 40)
    cy_btn = s(y + 14)
    d.ellipse([cx_btn-s(12), cy_btn-s(12), cx_btn+s(12), cy_btn+s(12)], fill=C["surface"])
    d.text((cx_btn-s(5), cy_btn-s(7)), "\u00d7", fill=C["text2"], font=F16B)

    y += 40
    d.line([(s(16), s(y)), (s(W-16), s(y))], fill=C["border"], width=s(1))
    y += 16

    # All coordinates in logical (unscaled) space from here
    msg_x = 24
    msg_max_w = W - 70

    # Bot message 1
    bot_h = 50
    rounded_rect(d, (msg_x, y, msg_x+msg_max_w, y+bot_h), fill=C["surface"], r=12)
    d.text((s(msg_x+14), s(y+10)), "Hi! I'm the GNYC Youth Ministry", fill=C["text1"], font=F13)
    d.text((s(msg_x+14), s(y+28)), "assistant. How can I help you today?", fill=C["text1"], font=F13)
    y += bot_h + 14

    # User message — right-aligned
    user_text = "Which clubs haven't submitted"
    user_text2 = "reports this month?"
    user_h = 48
    ux = 100
    rounded_rect(d, (ux, y, W-20, y+user_h), fill=C["primary"], r=12)
    d.text((s(ux+14), s(y+8)), user_text, fill=C["white"], font=F13)
    d.text((s(ux+14), s(y+26)), user_text2, fill=C["white"], font=F13)
    y += user_h + 14

    # Bot response (multi-line)
    bot_lines = [
        ("Based on April's reports, 2 of 8 clubs", False),
        ("in your area haven't submitted yet:", False),
        ("", False),
        ("\u2022  Crown Heights SDA", True),
        ("   pending since Apr 1", False),
        ("\u2022  Canarsie SDA", True),
        ("   overdue (was due Apr 5)", False),
        ("", False),
        ("Would you like me to draft a reminder", False),
        ("message to their directors?", False),
    ]
    line_h = 17
    bot_block_h = len(bot_lines) * line_h + 20
    rounded_rect(d, (msg_x, y, msg_x+msg_max_w, y+bot_block_h), fill=C["surface"], r=12)
    for i, (line, bold) in enumerate(bot_lines):
        ly = y + 12 + i * line_h
        d.text((s(msg_x+14), s(ly)), line, fill=C["text1"], font=F12B if bold else F13)
    y += bot_block_h + 12

    # Action buttons
    btn1_text = "Yes, draft a message"
    btn2_text = "Show contact info"
    btn1_w = int(text_width(d, btn1_text, F12B) / S) + 24
    btn2_w = int(text_width(d, btn2_text, F12B) / S) + 24

    rounded_rect(d, (msg_x, y, msg_x+btn1_w, y+34), fill=C["white"], outline=C["primary"], r=10, width=1.5)
    d.text((s(msg_x+12), s(y+9)), btn1_text, fill=C["primary"], font=F12B)

    rounded_rect(d, (msg_x+btn1_w+8, y, msg_x+btn1_w+8+btn2_w, y+34),
                 fill=C["white"], outline=C["primary"], r=10, width=1.5)
    d.text((s(msg_x+btn1_w+8+12), s(y+9)), btn2_text, fill=C["primary"], font=F12B)

    # Input bar at bottom
    input_y = H - 50
    d.rectangle([0, s(input_y - 8), s(W), s(H)], fill=C["white"])
    d.line([(0, s(input_y - 8)), (s(W), s(input_y - 8))], fill=C["border"], width=s(1))
    rounded_rect(d, (16, input_y - 4, W - 60, input_y + 32), fill=C["surface"], outline=C["border"], r=18)
    d.text((s(28), s(input_y + 4)), "Ask anything...", fill=C["border"], font=F14)
    # Send button
    send_x = W - 48
    send_y = input_y
    d.ellipse([s(send_x), s(send_y), s(send_x+32), s(send_y+32)], fill=C["primary"])
    # Arrow in send
    ax = s(send_x + 16)
    ay = s(send_y + 16)
    d.polygon([(ax-s(5), ay+s(4)), (ax, ay-s(6)), (ax+s(5), ay+s(4))], fill=C["white"])

    img.save(os.path.join(OUT_DIR, "07-ai-assistant.png"), dpi=(144, 144))
    print("  07-ai-assistant.png")


# ============================================================================
# Main
# ============================================================================
if __name__ == "__main__":
    print("Generating GNYC Youth Leader Portal mockups...")
    screen_01()
    screen_02()
    screen_03()
    screen_04()
    screen_05()
    screen_06()
    screen_07()
    print(f"\nAll mockups saved to: {OUT_DIR}")
