#!/usr/bin/env python3
"""Render an animated terminal GIF for harness-kit (real installer output)."""
import os
from PIL import Image, ImageDraw, ImageFont

SS = 2                      # supersample, downscaled later for crisp text
FS = 26 * SS
LH = 34 * SS
PAD_X = 26 * SS
TITLE_H = 46 * SS
PAD_TOP = 16 * SS
PAD_BOT = 14 * SS
VIS = 18                    # visible rows (terminal scrolls)
COLS = 55

FR = "/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf"
FB = "/usr/share/fonts/truetype/firacode/FiraCode-Bold.ttf"
FONT_R = ImageFont.truetype(FR, FS)
FONT_B = ImageFont.truetype(FB, FS)
CW = FONT_R.getlength("M")

# --- glyph fallback if a char is missing from the font ---
def _supported(path):
    try:
        from fontTools.ttLib import TTFont
        tt = TTFont(path)
        cmap = set()
        for t in tt["cmap"].tables:
            cmap |= set(t.cmap.keys())
        return cmap
    except Exception:
        return None
_CMAP = _supported(FR)
FALLBACK = {"❯": ">", "→": "->", "—": "-", "·": "-"}
def fix(s):
    if _CMAP is None:
        return s
    return "".join(c if ord(c) in _CMAP else FALLBACK.get(c, "?") for c in s)

# --- colors ---
BG       = (13, 17, 23)
TITLE_BG = (22, 27, 34)
BORDER   = (33, 38, 45)
DEFAULT  = (201, 209, 217)
GREEN    = (63, 185, 80)
CYAN     = (88, 166, 255)
DIM      = (110, 118, 129)
PROMPT   = (86, 211, 100)
WHITE    = (235, 240, 245)
PATH     = (139, 148, 158)
TL = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]

W = int(PAD_X * 2 + CW * COLS)
H = int(TITLE_H + PAD_TOP + VIS * LH + PAD_BOT)

CMD = "npx @htechcs/harness-kit --all"
PROMPT_PATH = "~/my-app"

# raw installer output, styled by kind
GUIDES = ["tutorial.md", "tutorial.en.md", "kit-README.md", "agents-README.md",
          "mcp-audit.md", "guardrails-README.md", "long-running-README.md", "TASK.md",
          "evals-README.md", "observability.md", "spec-README.md", "FEATURE.md"]
OUTPUT = [
    ("install", "harness-kit → installing into: ~/my-app"),
    ("blank", ""),
    ("header", "Level 1 — Foundation (CLAUDE.md)"),
    ("added", "~/.claude/skills/init-harness"),
    ("header", "Level 2 — Clean context"),
    ("added", ".claude/agents/repo-explorer.md"),
    ("header", "Level 3 — Guardrails"),
    ("added", ".claude/settings.json"),
    ("header", "Level 4 — Long-running"),
    ("added", "setup.sh"),
    ("added", "new-worktree.sh"),
    ("header", "Level 5 — Evals & Observability"),
    ("added", "evals/cases/example-task.md"),
    ("guide", "Guidance docs → docs/harness/"),
] + [("added", "docs/harness/" + g) for g in GUIDES] + [
    ("blank", ""),
    ("done", "Done. 5 levels installed — full guides in docs/harness/."),
]

def cmd_segments(typed):
    return [(PROMPT_PATH + " ", PROMPT, True), ("» ", CYAN, True), (typed, WHITE, False)]

def out_segments(kind, text):
    if kind == "blank":
        return []
    if kind == "install":
        return [(text, DIM, False)]
    if kind in ("header", "guide"):
        return [(text, CYAN, True)]
    if kind == "done":
        return [(text, GREEN, True)]
    if kind == "added":
        return [("  added   ", GREEN, False), (text, PATH, False)]
    return [(text, DEFAULT, False)]

def draw_line(d, x, y, segs):
    for text, color, bold in segs:
        text = fix(text)
        d.text((x, y), text, font=(FONT_B if bold else FONT_R), fill=color)
        x += CW * len(text)
    return x

def render(lines, cursor=False):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # title bar
    d.rectangle([0, 0, W, TITLE_H], fill=TITLE_BG)
    d.line([0, TITLE_H, W, TITLE_H], fill=BORDER, width=SS)
    r = 7 * SS
    cy = TITLE_H // 2
    for i, col in enumerate(TL):
        cx = PAD_X + i * (r * 2 + 8 * SS) + r
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    title = fix("my-app — zsh")
    tw = FONT_R.getlength(title)
    d.text(((W - tw) / 2, cy - FS / 2 - 2 * SS), title, font=FONT_R, fill=DIM)
    # body (last VIS lines)
    vis = lines[-VIS:]
    y = TITLE_H + PAD_TOP
    last_x = PAD_X
    for ln in vis:
        last_x = draw_line(d, PAD_X, y, ln)
        y += LH
    if cursor:
        cy0 = TITLE_H + PAD_TOP + (len(vis) - 1) * LH
        d.rectangle([last_x + 2 * SS, cy0, last_x + 2 * SS + CW, cy0 + FS], fill=DEFAULT)
    return img

# ---- build frame sequence ----
frames = []
def add(img, n=1):
    for _ in range(n):
        frames.append(img)

# 0: prompt with blinking cursor
base = [cmd_segments("")]
add(render(base, cursor=True), 3)
add(render(base, cursor=False), 2)

# 1: type the command, ~2 chars/frame
step = 2
for i in range(step, len(CMD) + step, step):
    add(render([cmd_segments(CMD[:i])], cursor=True), 1)
# full command, blink before enter
add(render([cmd_segments(CMD)], cursor=True), 3)
add(render([cmd_segments(CMD)], cursor=False), 2)

# 2: stream output line by line
buf = [cmd_segments(CMD)]
for kind, text in OUTPUT:
    buf.append(out_segments(kind, text))
    add(render(buf), 1)

# 3: hold final frame
add(render(buf), 36)

# ---- write PNG frames ----
FRDIR = "/tmp/hk-demo/frames"
os.makedirs(FRDIR, exist_ok=True)
for f in os.listdir(FRDIR):
    os.remove(os.path.join(FRDIR, f))
for i, fr in enumerate(frames):
    fr.save(os.path.join(FRDIR, "f%04d.png" % i))
print("frames:", len(frames), "size:", W, "x", H, "-> downscaled", W // SS, "x", H // SS)
