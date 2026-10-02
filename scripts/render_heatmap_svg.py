"""Render data/contributions.json as an animated 53x7 heatmap SVG."""
import json, datetime as dt

D = json.load(open("data/contributions.json"))
PALETTE = ["#1c2230", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, FG, MUTED = "#0d1117", "#c9d1d9", "#8b949e"
CELL, GAP, PADX, TOP = 13, 3, 40, 62
STEP = CELL + GAP

days = D["days"]
first = dt.date.fromisoformat(days[0]["date"])
weeks = (len(days) + 6) // 7
W = PADX * 2 + weeks * STEP
H = TOP + 7 * STEP + 56

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
     f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
     "<style>"
     ".c{opacity:0;transform:translateY(-8px);animation:in .5s ease-out forwards}"
     "@keyframes in{to{opacity:1;transform:translateY(0)}}"
     "</style>",
     f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
     f'<text x="{PADX}" y="30" fill="{MUTED}" font-size="14">avi@github ~ $ ./contributions.sh</text>'
     .replace("avi@github", "m11ahmed@github")]

# month labels
last_m = None
for i, d in enumerate(days):
    date = dt.date.fromisoformat(d["date"])
    if i % 7 == 0 and date.month != last_m:
        last_m = date.month
        o.append(f'<text x="{PADX + (i//7)*STEP}" y="{TOP-10}" fill="{MUTED}" font-size="11">'
                 f'{date.strftime("%b")}</text>')

# cells: diagonal reveal (delay by col+row)
for i, d in enumerate(days):
    col, row = divmod(i, 7)
    delay = round((col + row * 2) * 0.018, 3)
    x, y = PADX + col * STEP, TOP + row * STEP
    o.append(f'<rect class="c" style="animation-delay:{delay}s" x="{x}" y="{y}" width="{CELL}" '
             f'height="{CELL}" rx="3" fill="{PALETTE[d["level"]]}"><title>{d["count"]} on {d["date"]}</title></rect>')

# legend + footer
ly = TOP + 7 * STEP + 18
o.append(f'<text x="{W-PADX-170}" y="{ly+10}" fill="{MUTED}" font-size="11">Less</text>')
for k in range(6):
    o.append(f'<rect x="{W-PADX-132+k*(CELL+3)}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[k]}"/>')
o.append(f'<text x="{W-PADX-132+6*(CELL+3)+4}" y="{ly+10}" fill="{MUTED}" font-size="11">More</text>')
o.append(f'<text x="{PADX}" y="{ly+10}" fill="{FG}" font-size="12">{D["total"]:,} contributions in the last year'
         f' · current streak {D["current_streak"]}d · longest {D["longest_streak"]}d</text>')
o.append("</svg>")
open("contrib-heatmap.svg", "w").write("\n".join(o))
print("wrote contrib-heatmap.svg", W, "x", H)
