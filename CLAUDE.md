# Feras's Pick Sheet

Public NFL picks site for the 2026 season: https://feraskarablieh.github.io/nfl-picks/
Repo: github.com/feraskarablieh/nfl-picks (public, GitHub Pages serves `main` at `/`).

## Files

- `index.html` is the whole site (no build step). It fetches schedule and live scores from ESPN's public scoreboard API (`site.api.espn.com/.../nfl/scoreboard?seasontype=2&week=N&dates=2026`) in the browser and refreshes every 5 minutes. No server, no scheduled job.
- `picks.json` holds the picks: `weeks` maps week number (string) to a list of picks. Each team plays once a week, so the team identifies the game. `"DET"` is a straight-up pick (weeks 1–9). `"DET -2.5"` is against the spread, with the line from the picked team's side (`"NE +3"` for an underdog, `"DAL PK"` for a pick'em). Feras picks against the spread from Week 10 on. Record the current ESPN line when adding a pick. When Feras gives his own number, add ` fixed` (`"GB +3.5 fixed"`): a fixed custom line is never moved by the updater. A pick he says should follow the market has no `fixed`.
- `.github/workflows/update-lines.yml` runs `.github/scripts/update_lines.py` every 15 minutes on GitHub: each spread pick moves to ESPN's current line until its game kicks off, then stays locked. It commits `picks.json` as github-actions[bot], so always `git pull --rebase` before editing picks.
- `claude-artifact/`, `data/`, `refresh_scores.py` are an older claude.ai artifact version, gitignored and no longer updated. Ignore them.

## Updating picks ("Week 9: Bills, Chiefs, ...")

0. `git pull --rebase` (the line updater may have committed).
1. Map team names to ESPN abbreviations (WSH, LAR, LAC, JAX, LV, NE, NO, SF, TB, GB, KC, NYG, NYJ...).
2. Check that week's matchups on ESPN: every pick must play that week, no two picks in the same game, and say whether any game has already kicked off. Note the current line (`competitions[0].odds[0].details`, e.g. `DET -2.5`) for each pick.
3. Edit `picks.json`: set the week's list, as `"TEAM ±spread"` entries (merge with existing picks for that week unless told to replace) and bump `updatedAt` to the current UTC time.
4. Validate with `python3 -m json.tool picks.json`, commit, and push to `main`. Pages redeploys in about a minute. Confirm with `gh api repos/feraskarablieh/nfl-picks/pages/builds/latest`.
5. Reply with a table of pick, matchup, and kickoff in ET.

## Changing the site

Edit `index.html`, preview locally with `python3 -m http.server 8765` (picks.json needs http, not file://), then commit and push. End commit messages with the Co-Authored-By line the session asks for.
