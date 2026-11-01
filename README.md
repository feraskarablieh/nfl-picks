# Feras's Pick Sheet

Straight-up NFL picks for the 2026 season: this week's games with my picks, week-by-week history, and pick performance.

Live at **https://feraskarablieh.github.io/nfl-picks/**

## How it works

- `index.html` is the whole site. It loads the schedule and live scores straight from ESPN's public scoreboard API in the visitor's browser and refreshes every 5 minutes while the page is open.
- `picks.json` holds my picks: for each week, the abbreviations of the teams I picked to win.

```json
"weeks": {
  "9": ["BUF", "KC", "DET", "PHI"]
}
```

Each team plays at most once a week, so the team alone identifies the game. Abbreviations are ESPN's (`WSH`, `LAR`, `LAC`, `JAX`, ...). Update `updatedAt` when changing picks, then commit and push. GitHub Pages redeploys in about a minute.

## Run locally

```bash
python3 -m http.server 8765
```

Then open http://localhost:8765.
