#!/usr/bin/env python3
"""Render a dumbbell (before/after) chart for the guardrails benchmark."""
import os
from PIL import Image, ImageDraw, ImageFont

SS = 3  # supersample then downscale for crisp output

def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("no font found")

NOTO_R = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
NOTO_B = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
NOTO_M = ["/usr/share/fonts/truetype/noto/NotoSans-Medium.ttf"] + NOTO_B

f_title = font(NOTO_B, 31 * SS)
f_sub   = font(NOTO_R, 16 * SS)
f_cat   = font(NOTO_B, 16 * SS)
f_catn  = font(NOTO_R, 13 * SS)
f_val   = font(NOTO_B, 15 * SS)
f_vald  = font(NOTO_R, 14 * SS)
f_tick  = font(NOTO_R, 12 * SS)
f_leg   = font(NOTO_R, 14 * SS)
f_foot  = font(NOTO_R, 12 * SS)

# colors
CREAM   = (246, 243, 236)
CARD    = (255, 255, 255)
BORDER  = (227, 224, 218)
INK     = (28, 27, 25)
GREY    = (124, 121, 116)
GRID    = (236, 233, 228)
TICK    = (158, 155, 150)
DEFDOT  = (150, 148, 143)
HARD    = (238, 106, 77)
LINE    = (208, 205, 199)

# data: (label, n, default%, hardened%)
ROWS = [
    ("Overall coverage", 25, 68, 92),
    ("Catastrophic hard-block", 8, 25, 75),
    ("Secrets blocked", 7, 71, 100),
    ("Destructive gated", 6, 83, 100),
]

W, H = 1040 * SS, 560 * SS
img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)

def rrect(box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)

# card
m = 22 * SS
rrect([m, m, W - m, H - m], 16 * SS, fill=CARD, outline=BORDER, width=1 * SS)

def ctext(x, y, s, fnt, fill, anchor="la"):
    d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)

cx = W // 2
ctext(cx, 48 * SS, "Guardrail coverage — default vs hardened", f_title, INK, "ma")
ctext(cx, 88 * SS, "Permission rules gating a 25-op risk suite  (% of each category)", f_sub, GREY, "ma")

# horizontal legend, centered, between subtitle and plot
leg_y = 126 * SS
dot_w, dot_gap, pad_between = 14 * SS, 9 * SS, 42 * SS
items = [(DEFDOT, "Default (shipped)", GREY), (HARD, "Hardened (proposed)", INK)]
widths = [dot_w + dot_gap + d.textlength(t, font=f_leg) for _, t, _ in items]
total = sum(widths) + pad_between * (len(items) - 1)
lx = cx - total / 2
for (col, txt, tcol), wdt in zip(items, widths):
    d.ellipse([lx, leg_y, lx + dot_w, leg_y + dot_w], fill=col)
    d.text((lx + dot_w + dot_gap, leg_y + dot_w / 2), txt, font=f_leg, fill=tcol, anchor="lm")
    lx += wdt + pad_between

# plot geometry
pl = 300 * SS      # plot left (x=0%)
pr = 905 * SS      # plot right (x=100%)
pt = 175 * SS
pb = 452 * SS

def xof(pct):
    return pl + (pr - pl) * pct / 100.0

# vertical gridlines + ticks
for g in (0, 25, 50, 75, 100):
    gx = xof(g)
    d.line([gx, pt, gx, pb], fill=GRID, width=1 * SS)
    ctext(gx, pb + 12 * SS, f"{g}%", f_tick, TICK, "ma")

n = len(ROWS)
for i, (label, cnt, dv, hv) in enumerate(ROWS):
    y = pt + (pb - pt) * (i + 0.5) / n
    # category label (right-aligned, left of plot)
    ctext(pl - 26 * SS, y - 10 * SS, label, f_cat, INK, "ra")
    ctext(pl - 26 * SS, y + 9 * SS, f"n = {cnt}", f_catn, GREY, "ra")
    # connecting line
    d.line([xof(dv), y, xof(hv), y], fill=LINE, width=5 * SS)
    rdot = 9 * SS
    # default dot + value below
    d.ellipse([xof(dv) - rdot, y - rdot, xof(dv) + rdot, y + rdot], fill=DEFDOT)
    ctext(xof(dv), y + 16 * SS, f"{dv}%", f_vald, GREY, "ma")
    # hardened dot + value above
    d.ellipse([xof(hv) - rdot, y - rdot, xof(hv) + rdot, y + rdot], fill=HARD)
    ctext(xof(hv), y - 30 * SS, f"{hv}%", f_val, HARD, "ma")

# footnote
ctext(pl - 26 * SS, pb + 48 * SS,
      "Policy coverage of permission rules, not task success.  Reproducible: node bench/guardrails-bench.js",
      f_foot, TICK, "la")

# downscale
out = img.resize((W // SS, H // SS), Image.LANCZOS)
os.makedirs("/home/hahoang/harness-setup/assets", exist_ok=True)
out.save("/home/hahoang/harness-setup/assets/guardrails-chart.png")
print("saved assets/guardrails-chart.png", out.size)
