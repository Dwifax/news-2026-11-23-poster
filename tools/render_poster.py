#!/usr/bin/env python
"""Renders entry.png: a 1024x1024 editorial news poster for Monday 23 Nov 2026.

Dev-only script (Pillow). Run: python tools/render_poster.py
Keep the day's copy in the DATA block below so it's easy to edit.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# DATA BLOCK -- edit the day's copy here
# ---------------------------------------------------------------------------
DOW = "MONDAY"
DATE = "23 NOVEMBER 2026"
EYEBROW = "WORLD NEWS IN ONE IMAGE"

LEAD_KICKER = "STRAIT OF HORMUZ"
LEAD_HEAD = ["THREE MORE SHIPS HIT"]
LEAD_SUB = "Tankers struck crossing the strait; attacks at their highest since February"

TILES = [
    ("CLIMATE", "COP31 talks collapse", "globe"),
    ("EUROPE", "General strikes sweep Italy and France", "strike"),
    ("LIBYA / UKRAINE", "Sea drone sinks Russian warship", "drone"),
    ("GAZA", "Aid vehicle struck; three killed", "aid"),
    ("UNITED STATES", "Masked ICE arrests at Seattle airport", "airport"),
    ("TECH", "Delta delays 1,300 flights; FBI breach", "screen"),
]

ALSO_TODAY = (
    "Moscow warns Estonia  •  Nvidia reinstates Huang  •  "
    "Democrats reach 259 House seats  •  Rikers Island to close by 2032"
)

FOOTER = "23 November 2026  ·  Sources: Democracy Now!, Reuters, Al Jazeera, PBS NewsHour"

# ---------------------------------------------------------------------------
# PALETTE / CANVAS
# ---------------------------------------------------------------------------
INK = (20, 17, 15)
PAPER = (243, 237, 222)
RED = (179, 39, 30)
BLUE = (70, 88, 106)
ORANGE = (226, 98, 42)
SMOKE = tuple(round(c * 0.55 + p * 0.45) for c, p in zip(INK, PAPER))

W = H = 1024
MARGIN = 40

FONT_DIR = "C:/Windows/Fonts/"


def font(name, size):
    try:
        return ImageFont.truetype(FONT_DIR + name, size)
    except OSError:
        return ImageFont.load_default()


def tint(color, amount):
    """Blend `color` toward PAPER by `amount` (0=color, 1=paper)."""
    return tuple(round(c * (1 - amount) + p * amount) for c, p in zip(color, PAPER))


def measure(draw, text, fnt):
    l, t, r, b = draw.textbbox((0, 0), text, font=fnt, anchor="lt")
    return r - l, b - t


def wrap_text(draw, text, fnt, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if measure(draw, trial, fnt)[0] <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(draw, text, font_name, max_width, start_size, min_size):
    size = start_size
    while size >= min_size:
        f = font(font_name, size)
        if measure(draw, text, f)[0] <= max_width:
            return f
        size -= 1
    return font(font_name, min_size)


def text_center(draw, cx, y, text, fnt, fill, anchor="mt"):
    draw.text((cx, y), text, font=fnt, fill=fill, anchor=anchor)


def text_right(draw, rx, y, text, fnt, fill, anchor="rt"):
    draw.text((rx, y), text, font=fnt, fill=fill, anchor=anchor)


def rounded_tag(draw, x, y, text, fnt, fg, bg):
    tw, th = measure(draw, text, fnt)
    pad_x, pad_y = 10, 5
    box = [x, y, x + tw + pad_x * 2, y + th + pad_y * 2 + 4]
    draw.rounded_rectangle(box, radius=4, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), text, font=fnt, fill=fg)
    return box[3] - box[1]


def dashed_arc(draw, points, color, width=3, dash=8, gap=6):
    """Draw a dashed line along a polyline given by `points`."""
    import math

    total = []
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        seg_len = math.hypot(x1 - x0, y1 - y0)
        steps = max(1, int(seg_len))
        for s in range(steps + 1):
            t = s / steps
            total.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    on = True
    count = 0
    seg_start = total[0] if total else None
    for i in range(1, len(total)):
        count += 1
        if count >= (dash if on else gap):
            if on:
                draw.line([seg_start, total[i]], fill=color, width=width)
            on = not on
            count = 0
            seg_start = total[i]
    if on and seg_start is not None and total:
        draw.line([seg_start, total[-1]], fill=color, width=width)


def quad_bezier(p0, p1, p2, n=28):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def simple_hull(draw, x, y, w, h, color):
    """A small tanker hull + bridge for tile-scale icons. Waterline at (x, y).
    Returns the (cx, cy) point on deck where a flame/hit should sit."""
    deck_h = h * 0.42
    hull = [
        (x, y),
        (x + w * 0.04, y - deck_h),
        (x + w * 0.78, y - deck_h),
        (x + w, y - deck_h * 0.32),
        (x + w * 0.97, y),
    ]
    draw.polygon(hull, fill=color)
    sup_w, sup_h = w * 0.17, h * 0.58
    sx = x + w * 0.14
    draw.rectangle([sx, y - deck_h - sup_h, sx + sup_w, y - deck_h + 1], fill=color)
    win = max(2, sup_w * 0.18)
    for i in range(2):
        wx = sx + sup_w * 0.22 + i * sup_w * 0.4
        wy = y - deck_h - sup_h * 0.62
        draw.rectangle([wx, wy, wx + win, wy + win], fill=PAPER)
    draw.line(
        [sx + sup_w * 0.5, y - deck_h - sup_h, sx + sup_w * 0.5, y - deck_h - sup_h - h * 0.2],
        fill=color, width=max(2, int(h * 0.045)),
    )
    draw.line([x + w * 0.36, y - deck_h, x + w * 0.74, y - deck_h], fill=color, width=max(2, int(h * 0.04)))
    return (x + w * 0.5, y - deck_h)


def rot_transform(origin, angle_deg):
    ox, oy = origin
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    return lambda px, py: (ox + px * ca - py * sa, oy + px * sa + py * ca)


def dome_points(x0, x1, base_y, height, n=8):
    """A smooth half-ellipse dome profile from (x0, base_y) to (x1, base_y)."""
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        rel = (x - cx) / rx if rx else 0
        y = base_y - height * math.sqrt(max(0.0, 1 - rel * rel))
        pts.append((x, y))
    return pts


def tanker_silhouette(draw, origin, angle_deg, w, h, color):
    """A long, low tanker: flat stern, raked bow, aft bridge with a funnel,
    two rounded deck-tank domes linked by a pipe line. `origin` is the
    stern-bottom point at the waterline (global coords); the hull extends
    toward +x (bow) and -y (up) before being rotated by `angle_deg` around
    `origin` to show a list. Returns (hit_point, deck_mid_point) in global
    coords: hit_point for a flame, deck_mid_point (clear of the bridge and
    the hit) for a clean marker anchor."""
    T = rot_transform(origin, angle_deg)

    def poly(pts_local, fill):
        draw.polygon([T(px, py) for px, py in pts_local], fill=fill)

    deck_h = h * 0.34

    # hull outline with two low rounded deck-tank domes built into the deck edge
    tank_h, gap = h * 0.1, w * 0.07
    tank_spans = [(w * 0.38, w * 0.54), (w * 0.61, w * 0.77)]
    tank_tops = []
    hull_pts = [(0, 0), (0, -deck_h), (tank_spans[0][0], -deck_h)]
    for x0, x1 in tank_spans:
        hull_pts += dome_points(x0, x1, -deck_h, tank_h, n=8)
        tank_tops.append(((x0 + x1) / 2, -deck_h - tank_h))
    hull_pts += [(w * 0.84, -deck_h), (w, -deck_h * 0.18), (w * 0.88, 0)]
    poly(hull_pts, color)

    # bridge / superstructure aft
    sup_x0, sup_x1, sup_h = w * 0.07, w * 0.26, h * 0.3
    poly([(sup_x0, -deck_h), (sup_x0, -deck_h - sup_h), (sup_x1, -deck_h - sup_h), (sup_x1, -deck_h)], color)
    # a single light window band near the top of the bridge
    band_h = sup_h * 0.16
    band_y = -deck_h - sup_h * 0.82
    poly(
        [(sup_x0 + w * 0.015, band_y), (sup_x0 + w * 0.015, band_y - band_h),
         (sup_x1 - w * 0.015, band_y - band_h), (sup_x1 - w * 0.015, band_y)],
        PAPER,
    )

    # funnel, aft edge of the bridge, taller than the bridge roof
    fun_w, fun_h = (sup_x1 - sup_x0) * 0.3, h * 0.3
    fun_x0 = sup_x1 - fun_w * 1.4
    poly(
        [(fun_x0, -deck_h - sup_h), (fun_x0, -deck_h - sup_h - fun_h),
         (fun_x0 + fun_w, -deck_h - sup_h - fun_h), (fun_x0 + fun_w, -deck_h - sup_h)],
        color,
    )

    # pipe line connecting the deck-tank domes
    draw.line([T(px, py) for px, py in tank_tops], fill=color, width=max(2, int(h * 0.03)))

    hit_local = (tank_tops[-1][0], tank_tops[-1][1] - tank_h * 0.3)
    deck_mid_local = ((sup_x1 + tank_spans[0][0]) / 2, -deck_h)
    return T(*hit_local), T(*deck_mid_local)


def smoke_plume(draw, cx, base_y, size, color):
    cx0, cy0 = cx, base_y
    for i in range(3):
        r = size * (0.55 + i * 0.24)
        cy0 -= size * 0.6
        cx0 += size * 0.3
        draw.ellipse([cx0 - r, cy0 - r, cx0 + r, cy0 + r], fill=color)


def flame(draw, cx, baseline, size, color):
    pts = [
        (cx, baseline - size * 1.3),
        (cx + size * 0.32, baseline - size * 0.8),
        (cx + size * 0.18, baseline - size * 0.55),
        (cx + size * 0.42, baseline - size * 0.2),
        (cx + size * 0.15, baseline),
        (cx - size * 0.15, baseline),
        (cx - size * 0.42, baseline - size * 0.2),
        (cx - size * 0.18, baseline - size * 0.55),
        (cx - size * 0.32, baseline - size * 0.8),
    ]
    draw.polygon(pts, fill=color)


def locator_pin(draw, cx, tip_y, size, color):
    top = tip_y - size
    draw.ellipse([cx - size * 0.5, top - size * 0.5, cx + size * 0.5, top + size * 0.5], fill=color)
    draw.polygon(
        [
            (cx - size * 0.32, top + size * 0.28),
            (cx + size * 0.32, top + size * 0.28),
            (cx, tip_y),
        ],
        fill=color,
    )
    draw.ellipse(
        [cx - size * 0.16, top - size * 0.16, cx + size * 0.16, top + size * 0.16],
        fill=PAPER,
    )


# ---------------------------------------------------------------------------
# PICTOGRAMS -- flat vector icons drawn inside a square box (x, y, s)
# ---------------------------------------------------------------------------

def icon_globe(draw, x, y, s):
    cx, cy = x + s / 2, y + s / 2
    r = s * 0.38
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=5)
    draw.ellipse([cx - r * 0.42, cy - r, cx + r * 0.42, cy + r], outline=BLUE, width=4)
    draw.line([cx - r, cy, cx + r, cy], fill=BLUE, width=4)
    draw.line([cx - r * 0.86, cy - r * 0.5, cx + r * 0.86, cy - r * 0.5], fill=BLUE, width=3)
    draw.line([cx - r * 0.86, cy + r * 0.5, cx + r * 0.86, cy + r * 0.5], fill=BLUE, width=3)
    d = r * 1.25
    draw.line([cx - d, cy - d, cx + d, cy + d], fill=RED, width=8)


def icon_strike(draw, x, y, s):
    base = y + s * 0.92
    figs = [0.22, 0.42, 0.62, 0.82]
    for i, fx in enumerate(figs):
        px = x + s * fx
        head_r = s * 0.07
        body_h = s * 0.26
        draw.ellipse(
            [px - head_r, base - body_h - head_r * 2, px + head_r, base - body_h],
            fill=INK,
        )
        draw.polygon(
            [
                (px - head_r * 1.3, base),
                (px + head_r * 1.3, base),
                (px + head_r * 0.9, base - body_h),
                (px - head_r * 0.9, base - body_h),
            ],
            fill=INK,
        )
        if i % 2 == 0:
            stick_top = base - body_h - head_r * 2 - s * 0.22
            draw.line([px, base - body_h, px, stick_top], fill=INK, width=3)
            placard_w, placard_h = s * 0.2, s * 0.13
            color = RED if i == 0 else ORANGE
            draw.rectangle(
                [px - placard_w / 2, stick_top - placard_h, px + placard_w / 2, stick_top],
                fill=color,
            )


def icon_drone(draw, x, y, s):
    base_y = y + s * 0.82
    simple_hull(draw, x + s * 0.08, base_y, s * 0.78, s * 0.42, BLUE)
    flame(draw, x + s * 0.55, base_y, s * 0.22, ORANGE)
    dx, dy = x + s * 0.72, y + s * 0.22
    draw.ellipse([dx - s * 0.07, dy - s * 0.07, dx + s * 0.07, dy + s * 0.07], fill=INK)
    arm = s * 0.16
    for ang in (1, -1):
        draw.line([dx - arm, dy - arm * ang, dx + arm, dy + arm * ang], fill=INK, width=3)
    dashed_arc(draw, [(dx, dy + s * 0.08), (x + s * 0.55, base_y - s * 0.3)], RED, width=3, dash=6, gap=5)


def icon_aid(draw, x, y, s):
    base = y + s * 0.78
    cargo_w, cargo_h = s * 0.5, s * 0.34
    cx0 = x + s * 0.1
    draw.rectangle([cx0, base - cargo_h, cx0 + cargo_w, base], fill=PAPER, outline=INK, width=4)
    cross_s = cargo_h * 0.5
    ccx, ccy = cx0 + cargo_w / 2, base - cargo_h / 2
    draw.rectangle([ccx - cross_s * 0.15, ccy - cross_s / 2, ccx + cross_s * 0.15, ccy + cross_s / 2], fill=RED)
    draw.rectangle([ccx - cross_s / 2, ccy - cross_s * 0.15, ccx + cross_s / 2, ccy + cross_s * 0.15], fill=RED)
    cab_w, cab_h = s * 0.22, cargo_h * 0.78
    cabx = cx0 + cargo_w
    draw.polygon(
        [
            (cabx, base),
            (cabx, base - cab_h),
            (cabx + cab_w * 0.6, base - cab_h),
            (cabx + cab_w, base - cab_h * 0.5),
            (cabx + cab_w, base),
        ],
        fill=INK,
    )
    for wx in (cx0 + cargo_w * 0.22, cabx + cab_w * 0.55):
        r = s * 0.06
        draw.ellipse([wx - r, base - r, wx + r, base + r], fill=INK)
        draw.ellipse([wx - r * 0.45, base - r * 0.45, wx + r * 0.45, base + r * 0.45], fill=PAPER)


def icon_airport(draw, x, y, s):
    # universal "airplane" glyph (top-down silhouette), nose up
    cx = x + s * 0.42
    draw.polygon(
        [(cx, y + s * 0.06), (cx - s * 0.05, y + s * 0.3), (cx + s * 0.05, y + s * 0.3)],
        fill=BLUE,
    )
    draw.rectangle([cx - s * 0.04, y + s * 0.28, cx + s * 0.04, y + s * 0.72], fill=BLUE)
    for sign in (-1, 1):
        draw.polygon(
            [
                (cx, y + s * 0.34),
                (cx + sign * s * 0.46, y + s * 0.6),
                (cx + sign * s * 0.3, y + s * 0.64),
                (cx, y + s * 0.46),
            ],
            fill=BLUE,
        )
        draw.polygon(
            [
                (cx, y + s * 0.68),
                (cx + sign * s * 0.2, y + s * 0.84),
                (cx + sign * s * 0.11, y + s * 0.86),
                (cx, y + s * 0.74),
            ],
            fill=BLUE,
        )
    # badge (shield) for law-enforcement arrest
    bx, by = x + s * 0.76, y + s * 0.8
    br = s * 0.18
    draw.polygon(
        [
            (bx - br, by - br),
            (bx + br, by - br),
            (bx + br, by + br * 0.25),
            (bx, by + br * 1.15),
            (bx - br, by + br * 0.25),
        ],
        fill=RED,
    )
    star_r = br * 0.4
    draw.regular_polygon((bx, by - br * 0.1, star_r), n_sides=5, fill=PAPER)


def icon_screen(draw, x, y, s):
    mx0, my0, mx1, my1 = x + s * 0.1, y + s * 0.14, x + s * 0.9, y + s * 0.68
    draw.rectangle([mx0, my0, mx1, my1], fill=INK)
    draw.rectangle([mx0 + 6, my0 + 6, mx1 - 6, my1 - 6], fill=BLUE)
    draw.polygon(
        [
            (x + s * 0.5 - s * 0.05, y + s * 0.68),
            (x + s * 0.5 + s * 0.05, y + s * 0.68),
            (x + s * 0.5 + s * 0.1, y + s * 0.82),
            (x + s * 0.5 - s * 0.1, y + s * 0.82),
        ],
        fill=INK,
    )
    draw.rectangle([x + s * 0.3, y + s * 0.82, x + s * 0.7, y + s * 0.87], fill=INK)
    crack = [
        (mx0 + s * 0.08, my0 + s * 0.06),
        (mx0 + s * 0.3, my0 + s * 0.26),
        (mx0 + s * 0.2, my0 + s * 0.32),
        (mx0 + s * 0.42, my0 + s * 0.46),
        (mx0 + s * 0.3, my0 + s * 0.5),
        (mx0 + s * 0.55, my0 + s * 0.52),
    ]
    draw.line(crack, fill=RED, width=4, joint="curve")


ICONS = {
    "globe": icon_globe,
    "strike": icon_strike,
    "drone": icon_drone,
    "aid": icon_aid,
    "airport": icon_airport,
    "screen": icon_screen,
}


# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------

def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    f_dow = font("arialbd.ttf", 24)
    f_eyebrow = font("arialbd.ttf", 16)
    f_date = fit_one_line(draw, DATE, "ariblk.ttf", W - 2 * MARGIN, 108, 60)
    f_kicker = font("arialbd.ttf", 22)
    f_head = font("georgiab.ttf", 46)
    f_sub = font("georgiai.ttf", 22)
    f_tag = font("arialbd.ttf", 13)
    f_label = font("arialbd.ttf", 19)
    f_footer = font("arial.ttf", 17)

    # ---- 1. date band ------------------------------------------------
    y = 26
    draw.text((MARGIN, y), DOW, font=f_dow, fill=RED, anchor="lt")
    text_right(draw, W - MARGIN, y + 4, EYEBROW, f_eyebrow, BLUE)
    y += 36
    draw.text((MARGIN, y), DATE, font=f_date, fill=INK, anchor="lt")
    dw, dh = measure(draw, DATE, f_date)
    y += dh + 24
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=3)
    y += 22

    # ---- 2. lead story -------------------------------------------------
    lead_top = y
    draw.text((MARGIN, y), LEAD_KICKER, font=f_kicker, fill=RED, anchor="lt")
    y += 32
    for line in LEAD_HEAD:
        draw.text((MARGIN, y), line, font=f_head, fill=INK, anchor="lt")
        y += 52
    sub_lines = wrap_text(draw, LEAD_SUB, f_sub, W - 2 * MARGIN)
    for line in sub_lines:
        draw.text((MARGIN, y), line, font=f_sub, fill=BLUE, anchor="lt")
        y += 28
    y += 14

    scene_top = y
    scene_bottom = lead_top + 380
    scene_h = scene_bottom - scene_top
    panel = [MARGIN, scene_top, W - MARGIN, scene_bottom]
    draw.rectangle(panel, fill=tint(BLUE, 0.82))

    sea_h = scene_h * 0.4
    sea_top = scene_bottom - sea_h
    draw.rectangle([panel[0], sea_top, panel[2], scene_bottom], fill=BLUE)
    for i in range(1, 5):
        wy = sea_top + sea_h * i / 5
        draw.line([(panel[0] + 20, wy), (panel[2] - 20, wy)], fill=tint(BLUE, 0.25), width=2)

    avail_w = panel[2] - panel[0]
    ship_w, ship_h = scene_h * 0.78, scene_h * 0.46
    origins = [
        (panel[0] + avail_w * 0.03, sea_top + sea_h * 0.2),
        (panel[0] + avail_w * 0.5 - ship_w * 0.5, sea_top + sea_h * 0.55),
        (panel[2] - avail_w * 0.01 - ship_w, sea_top + sea_h * 0.2),
    ]
    angles = [0, -13, 0]

    deck_mid = None
    for i, (origin, angle) in enumerate(zip(origins, angles)):
        (hit_x, hit_y), deck_mid_pt = tanker_silhouette(draw, origin, angle, ship_w, ship_h, INK)
        smoke_plume(draw, hit_x, hit_y - scene_h * 0.03, scene_h * 0.06, SMOKE)
        flame(draw, hit_x, hit_y, scene_h * 0.14, ORANGE)
        flame(draw, hit_x - ship_w * 0.05, hit_y + scene_h * 0.015, scene_h * 0.08, RED)
        if i != 1:
            corner_x = panel[0] + 6 if i == 0 else panel[2] - 6
            src = (corner_x, scene_top + 6)
            ctrl = ((src[0] + hit_x) / 2, scene_top + (hit_y - scene_top) * 0.2)
            dst = (hit_x, hit_y - scene_h * 0.22)
            dashed_arc(draw, quad_bezier(src, ctrl, dst), RED, width=4, dash=10, gap=8)
        else:
            deck_mid = deck_mid_pt

    locator_pin(draw, deck_mid[0], deck_mid[1] - scene_h * 0.08, scene_h * 0.12, RED)

    # ---- 3. six tiles ----------------------------------------------------
    tiles_top = scene_bottom + 20
    gap = 11
    cols, rows = 2, 3
    tile_w = (W - 2 * MARGIN - gap) / cols
    tile_h = 88
    icon_s = 72

    for idx, (cat, label, icon_key) in enumerate(TILES):
        col = idx % cols
        row = idx // cols
        tx = MARGIN + col * (tile_w + gap)
        ty = tiles_top + row * (tile_h + gap)

        draw.rounded_rectangle([tx, ty, tx + tile_w, ty + tile_h], radius=10, fill=tint(INK, 0.92))
        icon_x, icon_y = tx + 10, ty + (tile_h - icon_s) / 2
        draw.rounded_rectangle(
            [icon_x, icon_y, icon_x + icon_s, icon_y + icon_s], radius=8, fill=PAPER
        )
        ICONS[icon_key](draw, icon_x, icon_y, icon_s)

        text_x = icon_x + icon_s + 14
        text_w = tx + tile_w - text_x - 12
        tag_h = rounded_tag(draw, text_x, ty + 7, cat, f_tag, PAPER, RED)
        label_lines = wrap_text(draw, label, f_label, text_w)[:2]
        ly = ty + 7 + tag_h + 5
        for line in label_lines:
            draw.text((text_x, ly), line, font=f_label, fill=INK, anchor="lt")
            ly += 22

    tiles_bottom = tiles_top + rows * tile_h + (rows - 1) * gap

    # ---- 5. footer (fixed near bottom) -------------------------------------
    footer_y = H - 34
    text_center(draw, W / 2, footer_y, FOOTER, f_footer, BLUE)

    # ---- 4. also-today strip (fills the gap between tiles and footer) -----
    y = tiles_bottom + 18
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=tint(INK, 0.6), width=2)
    y += 10
    strip_max_width = W - 2 * MARGIN
    strip_bottom_limit = footer_y - 10
    strip_budget_h = strip_bottom_limit - y

    size = 28
    while size >= 22:
        f_strip = font("arialbd.ttf", size)
        lines = wrap_text(draw, ALSO_TODAY, f_strip, strip_max_width)
        if len(lines) <= 2:
            _, lh = measure(draw, "Hg", f_strip)
            line_step = lh + 6
            total_h = lh + (len(lines) - 1) * line_step
            if total_h <= strip_budget_h:
                break
        size -= 1

    for line in lines:
        text_center(draw, W / 2, y, line, f_strip, INK)
        y += line_step

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "entry.png")
    img.save(out_path, "PNG", optimize=True)
    print(f"wrote {out_path}  size={img.size}  tiles_bottom={tiles_bottom:.0f}  strip_y={y:.0f}")
    return out_path


if __name__ == "__main__":
    render()
