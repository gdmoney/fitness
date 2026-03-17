#!/usr/bin/env python3
"""
Fitness Tracker - Local Web App
Run: python tracker.py
Then open http://localhost:8765 in your browser.
"""

import re
import json
from datetime import datetime
import http.server
import socketserver
import webbrowser
import threading
from pathlib import Path
from collections import defaultdict

PORT = 8765
README_PATH = Path(__file__).parent / "README.md"

LINE_RE    = re.compile(r'^(\d{4})\.\d{2}\.\d{2}\s+\*\*\*`([^`]*)`\*\*\*(.*)')
SECTION_RE = re.compile(r'^##\s+(\d{4})\s*$')
SETS_RE    = re.compile(r'Total number of sets:\s*(\d+)')
CARDIO_RE  = re.compile(r'\b(run|elliptical|elpt|swim|bike|cycle|jog)\b', re.IGNORECASE)


def parse_readme():
    yearly = defaultdict(lambda: {"resistance": 0, "resistance_only": 0, "cardio": 0, "missed": 0, "sets": None})
    section_year = None

    with open(README_PATH, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()

            sec = SECTION_RE.match(line)
            if sec:
                section_year = int(sec.group(1))
                continue

            m = LINE_RE.match(line)
            if m:
                year = int(m.group(1))
                if year < 2021:
                    continue
                if section_year is None:
                    section_year = year
                label   = m.group(2).strip().lower()
                content = m.group(3).strip().lower()
                if not label or label == "rest" or content == "**rest**":
                    yearly[year]["missed"] += 1
                elif label == "cardio":
                    yearly[year]["cardio"] += 1
                elif CARDIO_RE.search(content):
                    yearly[year]["resistance"] += 1
                else:
                    yearly[year]["resistance_only"] += 1
                continue

            s = SETS_RE.search(line)
            if s and section_year is not None and section_year >= 2021:
                if yearly[section_year]["sets"] is None:
                    yearly[section_year]["sets"] = 0
                yearly[section_year]["sets"] += int(s.group(1))

    return dict(sorted(yearly.items()))


def build_html(data):
    years            = list(data.keys())
    resistance       = [data[y]["resistance"]      for y in years]
    resistance_only  = [data[y]["resistance_only"] for y in years]
    cardio           = [data[y]["cardio"]           for y in years]
    missed           = [data[y]["missed"]           for y in years]
    sets             = [data[y]["sets"]             for y in years]


    sets_years = [y for y in years if data[y]["sets"] is not None]
    sets_vals  = [data[y]["sets"] for y in sets_years]

    current_year = datetime.now().year
    rows = ""
    for y in reversed(years):
        i = years.index(y)
        sets_cell = f'<td class="num sets">{sets[i]:,}</td>' if sets[i] is not None else '<td class="num dim">—</td>'
        row_class = ' class="current-year"' if y == current_year else ''
        rows += f"""
        <tr{row_class}>
          <td class="num">{y}</td>
          <td class="num">{resistance[i]}</td>
          <td class="num">{resistance_only[i]}</td>
          <td class="num">{cardio[i]}</td>
          <td class="num">{missed[i]}</td>

          {sets_cell}
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fitness Tracker</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 40px 24px;
    }}

    h1 {{
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.5px;
      color: #f8fafc;
      margin-bottom: 8px;
    }}

    .subtitle {{
      color: #64748b;
      font-size: 0.875rem;
      margin-bottom: 40px;
    }}

    .container {{
      max-width: 960px;
      margin: 0 auto;
    }}

    /* Summary cards */
    .cards {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 16px;
      margin-bottom: 40px;
    }}

    .card {{
      background: #1e2130;
      border: 1px solid #2d3348;
      border-radius: 12px;
      padding: 20px 24px;
    }}

    .card-label {{
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #64748b;
      margin-bottom: 8px;
    }}

    .card-value {{
      font-size: 2rem;
      font-weight: 700;
    }}

    .card-sub {{
      font-size: 0.75rem;
      color: #64748b;
      margin-top: 4px;
    }}

    .card.resistance      .card-value {{ color: #60a5fa; }}
    .card.resistance-only .card-value {{ color: #818cf8; }}
    .card.cardio          .card-value {{ color: #34d399; }}
    .card.missed          .card-value {{ color: #f87171; }}
    .card.sets            .card-value {{ color: #fb923c; }}

    /* Chart */
    .section {{
      background: #1e2130;
      border: 1px solid #2d3348;
      border-radius: 12px;
      padding: 28px;
      margin-bottom: 32px;
    }}

    .section-title {{
      font-size: 0.875rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #64748b;
      margin-bottom: 24px;
    }}

    .chart-wrap {{
      position: relative;
      height: 320px;
    }}

    /* Table */
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }}

    thead th {{
      text-align: left;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #64748b;
      padding: 0 12px 12px 12px;
      border-bottom: 1px solid #2d3348;
    }}

    thead th.num {{ text-align: right; }}

    tbody tr {{
      border-bottom: 1px solid #1a1f2e;
      transition: background 0.15s;
    }}

    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr:hover {{ background: #252a3a; }}

    td {{
      padding: 14px 12px;
      color: #cbd5e1;
    }}

    td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    tr.current-year td {{ background: #252a3a; }}


    .dot {{
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      margin-right: 8px;
      vertical-align: middle;
    }}

    .dot-r  {{ background: #60a5fa; }}
    .dot-ro {{ background: #818cf8; }}
    .dot-c  {{ background: #34d399; }}
    .dot-m  {{ background: #f87171; }}
    .dot-s  {{ background: #fb923c; }}

    td.sets {{ color: #fb923c; }}
    td.dim  {{ color: #334155; }}

    @media (max-width: 800px) {{
      .cards {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 480px) {{
      .cards {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Fitness Tracker</h1>
    <p class="subtitle">Yearly workout totals · {years[0]}–{years[-1]}</p>

    <div class="cards">
      <div class="card resistance">
        <div class="card-label">Resistance + Cardio</div>
        <div class="card-value">{sum(resistance):,}</div>
        <div class="card-sub">total workouts across all years</div>
      </div>
      <div class="card resistance-only">
        <div class="card-label">Resistance Only</div>
        <div class="card-value">{sum(resistance_only):,}</div>
        <div class="card-sub">total workouts across all years</div>
      </div>
      <div class="card cardio">
        <div class="card-label">Cardio Only</div>
        <div class="card-value">{sum(cardio):,}</div>
        <div class="card-sub">total workouts across all years</div>
      </div>
      <div class="card missed">
        <div class="card-label">Missed / Rest</div>
        <div class="card-value">{sum(missed):,}</div>
        <div class="card-sub">total workouts across all years</div>
      </div>
      <div class="card sets">
        <div class="card-label">Total Sets</div>
        <div class="card-value">{sum(s for s in sets if s is not None):,}</div>
        <div class="card-sub">total sets across all years</div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Days per Year</div>
      <div class="chart-wrap">
        <canvas id="chart"></canvas>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Sets per Year</div>
      <div class="chart-wrap">
        <canvas id="sets-chart"></canvas>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Yearly Breakdown</div>
      <table>
        <thead>
          <tr>
            <th>Year</th>
            <th class="num"><span class="dot dot-r"></span>Resistance + Cardio</th>
            <th class="num"><span class="dot dot-ro"></span>Resistance Only</th>
            <th class="num"><span class="dot dot-c"></span>Cardio Only</th>
            <th class="num"><span class="dot dot-m"></span>Missed / Rest</th>

            <th class="num"><span class="dot dot-s"></span>Total Sets</th>
          </tr>
        </thead>
        <tbody>{rows}
        </tbody>
      </table>
    </div>
  </div>

  <script>
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels: {json.dumps(years)},
        datasets: [
          {{
            label: 'Resistance + Cardio',
            data: {json.dumps(resistance)},
            backgroundColor: '#3b82f6',
            borderRadius: 4,
            borderSkipped: false,
          }},
          {{
            label: 'Resistance Only',
            data: {json.dumps(resistance_only)},
            backgroundColor: '#818cf8',
            borderRadius: 4,
            borderSkipped: false,
          }},
          {{
            label: 'Cardio Only',
            data: {json.dumps(cardio)},
            backgroundColor: '#10b981',
            borderRadius: 4,
            borderSkipped: false,
          }},
          {{
            label: 'Missed / Rest',
            data: {json.dumps(missed)},
            backgroundColor: '#ef4444',
            borderRadius: 4,
            borderSkipped: false,
          }},
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{
            position: 'top',
            labels: {{
              color: '#94a3b8',
              font: {{ size: 12 }},
              boxWidth: 12,
              boxHeight: 12,
              borderRadius: 3,
            }}
          }},
          tooltip: {{
            backgroundColor: '#1e2130',
            borderColor: '#2d3348',
            borderWidth: 1,
            titleColor: '#f8fafc',
            bodyColor: '#94a3b8',
            padding: 12,
          }}
        }},
        scales: {{
          x: {{
            stacked: true,
            grid: {{ color: '#1a1f2e' }},
            ticks: {{ color: '#64748b' }}
          }},
          y: {{
            stacked: true,
            max: 366,
            grid: {{ color: '#1a1f2e' }},
            ticks: {{ color: '#64748b' }}
          }}
        }}
      }}
    }});

    const setsCtx = document.getElementById('sets-chart').getContext('2d');
    new Chart(setsCtx, {{
      type: 'bar',
      data: {{
        labels: {json.dumps(sets_years)},
        datasets: [
          {{
            label: 'Total Sets',
            data: {json.dumps(sets_vals)},
            backgroundColor: '#fb923c',
            borderRadius: 4,
            borderSkipped: false,
          }},
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{
            position: 'top',
            labels: {{
              color: '#94a3b8',
              font: {{ size: 12 }},
              boxWidth: 12,
              boxHeight: 12,
              borderRadius: 3,
            }}
          }},
          tooltip: {{
            backgroundColor: '#1e2130',
            borderColor: '#2d3348',
            borderWidth: 1,
            titleColor: '#f8fafc',
            bodyColor: '#94a3b8',
            padding: 12,
            callbacks: {{
              label: (ctx) => ` ${{ctx.parsed.y.toLocaleString()}} sets`,
            }}
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: '#1a1f2e' }},
            ticks: {{ color: '#64748b' }}
          }},
          y: {{
            grid: {{ color: '#1a1f2e' }},
            ticks: {{
              color: '#64748b',
              callback: (v) => v.toLocaleString(),
            }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = parse_readme()
            html = build_html(data)
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        pass  # suppress server logs


def open_browser():
    import time
    time.sleep(0.5)
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    print(f"Fitness Tracker running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
