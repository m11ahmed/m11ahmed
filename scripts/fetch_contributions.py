"""Scrape the public contribution calendar (no token needed)."""
import json, re, sys, datetime as dt
import requests
from bs4 import BeautifulSoup

USER = sys.argv[1] if len(sys.argv) > 1 else "m11ahmed"
html = requests.get(f"https://github.com/users/{USER}/contributions",
                    headers={"User-Agent": "Mozilla/5.0"}, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

counts = {}
for tip in soup.find_all("tool-tip"):
    m = re.match(r"\s*(No|\d+) contributions?", tip.get_text())
    if m:
        counts[tip.get("for")] = 0 if m.group(1) == "No" else int(m.group(1))

days = []
for td in soup.select("td.ContributionCalendar-day"):
    days.append({"date": td["data-date"], "level": int(td["data-level"]),
                 "count": counts.get(td.get("id"), 0)})
days.sort(key=lambda d: d["date"])

# stats
today = dt.date.today().isoformat()
past = [d for d in days if d["date"] <= today]
longest = cur = 0
for d in past:
    cur = cur + 1 if d["count"] else 0
    longest = max(longest, cur)
current = 0
for d in reversed(past):
    if d["count"]: current += 1
    elif d["date"] == today: continue
    else: break
best = max(past, key=lambda d: d["count"]) if past else None

out = {"user": USER, "total": sum(d["count"] for d in days), "days": days,
       "current_streak": current, "longest_streak": longest, "best_day": best}
json.dump(out, open("data/contributions.json", "w"), indent=1)
print(f"{USER}: {out['total']} contributions, {len(days)} days, longest streak {longest}")
