"""Move against-the-spread picks in picks.json to ESPN's current line until kickoff.

A pick like "DET -2.5" follows the market while its game hasn't started; once it kicks off
the stored line stops changing, so picks are graded on the last line seen before kickoff.
Straight-up picks ("DET") are left alone. Prints what changed; writes picks.json only if needed.
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PICKS = Path(__file__).resolve().parents[2] / "picks.json"
URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?seasontype=2&week={w}&dates={season}"
PICK_RE = re.compile(r"^\s*([A-Z]{2,3})(?:\s+(PK|[+-]?\d+(?:\.\d+)?))?\s*$", re.I)


def fmt(team, spread):
    if spread == 0:
        return f"{team} PK"
    s = f"{spread:+g}"
    return f"{team} {s}"


def line_for(team, game):
    """The current spread from `team`'s side, or None if ESPN has no line yet."""
    c = game["competitions"][0]
    side = {x["homeAway"]: x["team"]["abbreviation"] for x in c["competitors"]}
    odds = (c.get("odds") or [{}])[0]
    details = (odds.get("details") or "").strip()
    if details.upper() in ("EVEN", "PK", "PICK"):
        return 0.0
    m = re.match(r"^([A-Z]{2,3})\s+(-?\d+(?:\.\d+)?)$", details)
    if m:
        n = float(m.group(2))
        return n if m.group(1) == team else -n
    if isinstance(odds.get("spread"), (int, float)):  # home team's side
        return float(odds["spread"]) if team == side["home"] else -float(odds["spread"])
    return None


def dump(doc):
    # keep the hand-editable layout: one line per week
    weeks = doc["weeks"]
    rows = [f'    {json.dumps(k)}: {json.dumps(v)}' for k, v in weeks.items()]
    head = {k: v for k, v in doc.items() if k != "weeks"}
    out = "{\n" + "".join(f"  {json.dumps(k)}: {json.dumps(v)},\n" for k, v in head.items())
    out += '  "weeks": {\n' + ",\n".join(rows) + "\n  }\n}\n"
    return out


def main(path=PICKS):
    path = Path(path)
    doc = json.loads(path.read_text())
    season = doc.get("season", 2026)
    now = datetime.now(timezone.utc)
    changes = []
    for wk, picks in doc["weeks"].items():
        parsed = [PICK_RE.match(p) for p in picks]
        if not any(m and m.group(2) is not None for m in parsed):
            continue  # no against-the-spread picks this week
        with urllib.request.urlopen(URL.format(w=wk, season=season), timeout=30) as r:
            events = json.load(r)["events"]
        by_team = {}
        for e in events:
            for x in e["competitions"][0]["competitors"]:
                by_team[x["team"]["abbreviation"]] = e
        for i, m in enumerate(parsed):
            if not m or m.group(2) is None:
                continue
            team = m.group(1).upper()
            game = by_team.get(team)
            if not game:
                continue
            state = game["competitions"][0]["status"]["type"]["state"]
            kick = datetime.strptime(game["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
            if state != "pre" or now >= kick:
                continue  # line locked at kickoff
            new = line_for(team, game)
            if new is None:
                continue
            updated = fmt(team, new)
            if updated != picks[i].strip():
                changes.append(f"Week {wk}: {picks[i].strip()} -> {updated}")
                picks[i] = updated
    if changes:
        doc["linesUpdatedAt"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        path.write_text(dump(doc))
        print("\n".join(changes))
    else:
        print("No line changes")


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
