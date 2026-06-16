#!/usr/bin/env python3
"""Render a slopegraph (before/after, % on the vertical axis) for the benchmark."""
import os
from PIL import Image, ImageDraw, ImageFont

SS = 3

def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("no font")

R = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
B = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
f_title = font(B, 31 * SS)
f_sub   = font(R, 16 * SS)
f_hdr   = font(B, 16 * SS)
f_name  = font(B, 15 * SS)
f_val   = font(B, 15 * SS)
f_anchor = font(R, 12 * SS)
f_foot  = font(R, 12 * SS)

CREAM = (246, 243, 236); CARD = (255, 255, 255); BORDER = (227, 224, 218)
INK = (28, 27, 25); GREY = (124, 121, 116); TICK = (158, 155, 150)
RAIL = (224, 221, 215)

# (label, n, default%, hardened%, color, hero)
ROWS = [
    ("Overall coverage", 25, 68, 92, (238, 106, 77), True),
    ("Catastrophic hard-block", 8, 25, 75, (199, 73, 91), False),
    ("Secrets blocked", 7, 71, 100, (47, 158, 143), False),
    ("Destructive gated", 6, 83, 100, (91, 108, 158), False),
]

W, H = 920 * SS, 600 * SS
img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)
d.rounded_rectangle([22 * SS, 22 * SS, W - 22 * SS, H - 22 * SS], radius=16 * SS, fill=CARD, outline=BORDER, width=1 * SS)
cx = W // 2
d.text((cx, 48 * SS), "Guardrail coverage — default vs hardened", font=f_title, fill=INK, anchor="ma")
d.text((cx, 88 * SS), "Permission rules gating a 25-op risk suite  (% of each category)", font=f_sub, fill=GREY, anchor="ma")

x_l, x_r = 360 * SS, 620 * SS
pt, pb = 168 * SS, 512 * SS   # y for 100% .. 0%

def y_of(pct):
    return pb - (pb - pt) * pct / 100.0

# column rails + headers + 0/100 anchors
for x in (x_l, x_r):
    d.line([x, pt, x, pb], fill=RAIL, width=1 * SS)
d.text((x_l, 130 * SS), "Default", font=f_hdr, fill=GREY, anchor="ma")
d.text((x_r, 130 * SS), "Hardened (proposed)", font=f_hdr, fill=INK, anchor="ma")
for pct in (0, 100):
    d.text((x_l - 300 * SS, y_of(pct)), f"{pct}%", font=f_anchor, fill=TICK, anchor="lm")

def declutter(targets, gap):
    order = sorted(range(len(targets)), key=lambda i: targets[i])
    ys = [0] * len(targets); prev = -1e9
    for i in order:
        y = max(targets[i], prev + gap); ys[i] = y; prev = y
    return ys

gap = 27 * SS
left_y = declutter([y_of(r[2]) for r in ROWS], gap)
right_y = declutter([y_of(r[3]) for r in ROWS], gap)

for i, (name, cnt, dv, hv, col, hero) in enumerate(ROWS):
    yl, yr = y_of(dv), y_of(hv)
    lw = 7 * SS if hero else 4 * SS
    rdot = 9 * SS if hero else 7 * SS
    d.line([x_l, yl, x_r, yr], fill=col, width=lw)
    d.ellipse([x_l - rdot, yl - rdot, x_l + rdot, yl + rdot], fill=col)
    d.ellipse([x_r - rdot, yr - rdot, x_r + rdot, yr + rdot], fill=col)
    # left label (name + value), de-cluttered y with leader
    ly = left_y[i]
    if abs(ly - yl) > 3 * SS:
        d.line([x_l - 16 * SS, yl, x_l - 30 * SS, ly], fill=col, width=1 * SS)
    val = f"{dv}%"; vw = d.textlength(val, font=f_val)
    d.text((x_l - 34 * SS, ly), val, font=f_val, fill=col, anchor="rm")
    d.text((x_l - 34 * SS - vw - 12 * SS, ly), name, font=f_name, fill=col, anchor="rm")
    # right label (value), de-cluttered y with leader
    ry = right_y[i]
    if abs(ry - yr) > 3 * SS:
        d.line([x_r + 16 * SS, yr, x_r + 30 * SS, ry], fill=col, width=1 * SS)
    d.text((x_r + 34 * SS, ry), f"{hv}%", font=f_val, fill=col, anchor="lm")

d.text((x_l - 300 * SS, pb + 44 * SS),
       "Policy coverage of permission rules, not task success.  Reproducible: node bench/guardrails-bench.js",
       font=f_foot, fill=TICK, anchor="la")

out = img.resize((W // SS, H // SS), Image.LANCZOS)
out.save("/home/hahoang/harness-setup/assets/guardrails-slope.png")
print("saved assets/guardrails-slope.png", out.size)
