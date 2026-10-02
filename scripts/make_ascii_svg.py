"""Convert source-prepped.png into a self-typing monochrome ASCII SVG.
usage: python scripts/make_ascii_svg.py [image] [cols]"""
import sys, numpy as np
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
COLS = int(sys.argv[2]) if len(sys.argv) > 2 else 100
RAMP = " .`:-=+*cs#%@"          # bright (sparse) -> dark (dense)
FS, CW, LH = 7, 4.2, 8          # font size, char width, line height
COLOR, BG = "#c9d1d9", "#0d1117"

img = Image.open(SRC).convert("L")
w, h = img.size
rows = max(1, int(COLS * (h / w) * (CW / LH)))   # correct for char aspect
g = np.array(img.resize((COLS, rows), Image.LANCZOS)) / 255.0
g = np.clip((g - 0.08) / 0.84, 0, 1) ** 1.1      # a touch more contrast
idx = ((1 - g) * (len(RAMP) - 1)).round().astype(int)
lines = ["".join(RAMP[i] for i in r).rstrip() for r in idx]

PAD = 14
W, H = int(COLS * CW + PAD * 2), int(rows * LH + PAD * 2)
esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/><defs>']
for r, line in enumerate(lines):
    t0 = round(r * 0.07, 2)
    dur = max(0.2, round(len(line) * 0.008, 2))
    y = PAD + r * LH
    o.append(f'<clipPath id="k{r}"><rect x="{PAD}" y="{y-1}" width="0" height="{LH+1}">'
             f'<animate attributeName="width" from="0" to="{COLS*CW}" begin="{t0}s" dur="{dur}s" fill="freeze"/>'
             f'</rect></clipPath>')
o.append("</defs>")
for r, line in enumerate(lines):
    t0 = round(r * 0.07, 2)
    dur = max(0.2, round(len(line) * 0.008, 2))
    y = PAD + r * LH
    o.append(f'<g clip-path="url(#k{r})"><text x="{PAD}" y="{y+FS}" font-family="ui-monospace,Menlo,Consolas,monospace" '
             f'font-size="{FS}" fill="{COLOR}" xml:space="preserve" textLength="{len(line)*CW:.1f}" '
             f'lengthAdjust="spacing">{esc(line)}</text></g>')
    # block cursor riding the wipe edge, then vanishing
    o.append(f'<rect y="{y}" width="{CW}" height="{LH-1}" fill="{COLOR}" opacity="0" x="{PAD}">'
             f'<animate attributeName="x" from="{PAD}" to="{PAD+len(line)*CW:.1f}" begin="{t0}s" dur="{dur}s" fill="freeze"/>'
             f'<set attributeName="opacity" to="0.9" begin="{t0}s"/>'
             f'<set attributeName="opacity" to="0" begin="{t0+dur:.2f}s"/></rect>')
o.append("</svg>")
open("avi-ascii.svg", "w").write("\n".join(o))
print(f"wrote avi-ascii.svg ({COLS}x{rows} chars, {W}x{H}px)")
