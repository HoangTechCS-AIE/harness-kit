#!/usr/bin/env python3
"""Render a slopegraph (before/after) with explicit axes for the benchmark."""
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
f_axis  = font(B, 15 * SS)   # axis titles / column labels
f_name  = font(B, 15 * SS)
f_val   = font(B, 15 * SS)
f_tick  = font(R, 13 * SS)
f_foot  = font(R, 12 * SS)

CREAM = (246, 243, 236); CARD = (255, 255, 255); BORDER = (227, 224, 218)
INK = (28, 27, 25); GREY = (110, 107, 102); TICK = (150, 147, 142)
GRID = (237, 234, 229); AXIS = (188, 184, 178); RAIL = (223, 220, 214)

# (label, n, default%, hardened%, color, hero)
ROWS = [
    ("Overall coverage", 25, 68, 92, (238, 106, 77), True),
    ("Catastrophic hard-block", 8, 25, 75, (199, 73, 91), False),
    ("Secrets blocked", 7, 71, 100, (47, 158, 143), False),
    ("Destructive gated", 6, 83, 100, (91, 108, 158), False),
]

W, H = 1000 * SS, 620 * SS
img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)
d.rounded_rectangle([22 * SS, 22 * SS, W - 22 * SS, H - 22 * SS], radius=16 * SS, fill=CARD, outline=BORDER, width=1 * SS)
cx = W // 2
d.text((cx, 46 * SS), "Guardrail coverage — default vs hardened", font=f_title, fill=INK, anchor="ma")
d.text((cx, 86 * SS), "Permission rules gating a 25-op risk suite", font=f_sub, fill=GREY, anchor="ma")

pt, pb = 152 * SS, 492 * SS
spine_x = 112 * SS
x_l, x_r = 500 * SS, 760 * SS

def y_of(pct):
    return pb - (pb - pt) * pct / 100.0

# --- Y axis: gridlines, ticks, spine, title ---
for pct in (0, 25, 50, 75, 100):
    gy = y_of(pct)
    strong = pct in (0, 100)
    d.line([spine_x, gy, x_r + 12 * SS, gy], fill=(AXIS if strong else GRID), width=1 * SS)
    d.line([spine_x - 6 * SS, gy, spine_x, gy], fill=AXIS, width=1 * SS)  # tick mark
    d.text((spine_x - 12 * SS, gy), f"{pct}%", font=f_tick, fill=TICK, anchor="rm")
d.line([spine_x, pt, spine_x, pb], fill=AXIS, width=1 * SS)  # vertical spine

def vtext(x, ymid, s, fnt, fill):
    w = int(d.textlength(s, font=fnt)) + 6 * SS
    asc, desc = fnt.getmetrics()
    h = asc + desc + 6 * SS
    tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((3 * SS, 3 * SS), s, font=fnt, fill=fill)
    tmp = tmp.rotate(90, expand=True)
    img.paste(tmp, (int(x), int(ymid - tmp.height / 2)), tmp)

vtext(44 * SS, (pt + pb) / 2, "Coverage (%)", f_axis, GREY)

# --- X axis: baseline already drawn at 0%; rails + bottom labels + ticks ---
for x in (x_l, x_r):
    d.line([x, pt, x, pb], fill=RAIL, width=1 * SS)
    d.line([x, pb, x, pb + 7 * SS], fill=AXIS, width=1 * SS)  # tick
d.text((x_l, pb + 16 * SS), "Default", font=f_axis, fill=GREY, anchor="ma")
d.text((x_r, pb + 16 * SS), "Hardened (proposed)", font=f_axis, fill=INK, anchor="ma")

# --- slopes with direct labels (de-cluttered) ---
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
    ly = left_y[i]
    if abs(ly - yl) > 3 * SS:
        d.line([x_l - 16 * SS, yl, x_l - 30 * SS, ly], fill=col, width=1 * SS)
    val = f"{dv}%"; vw = d.textlength(val, font=f_val)
    d.text((x_l - 34 * SS, ly), val, font=f_val, fill=col, anchor="rm")
    d.text((x_l - 34 * SS - vw - 12 * SS, ly), name, font=f_name, fill=col, anchor="rm")
    ry = right_y[i]
    if abs(ry - yr) > 3 * SS:
        d.line([x_r + 16 * SS, yr, x_r + 30 * SS, ry], fill=col, width=1 * SS)
    d.text((x_r + 34 * SS, ry), f"{hv}%", font=f_val, fill=col, anchor="lm")

d.text((spine_x - 30 * SS, pb + 58 * SS),
       "Policy coverage of permission rules, not task success.  Reproducible: node bench/guardrails-bench.js",
       font=f_foot, fill=TICK, anchor="la")

out = img.resize((W // SS, H // SS), Image.LANCZOS)
out.save("/home/hahoang/harness-setup/assets/guardrails-slope.png")
print("saved assets/guardrails-slope.png", out.size)
