"""
Dashboard Generator - seen_jobs.csv (+ new_jobs_latest_run.csv) se ek
self-contained static HTML dashboard banata hai. Koi backend/server nahi
chahiye - GitHub Pages (docs/ folder) se seedha serve ho jayega.
"""
import csv
import json
import os
from datetime import datetime


def _read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def generate_dashboard(seen_csv_path: str, new_csv_path: str, output_path: str):
    all_jobs = _read_csv(seen_csv_path)
    new_jobs = _read_csv(new_csv_path)
    new_links = {j["link"] for j in new_jobs if j.get("link")}

    # Newest first
    all_jobs.sort(key=lambda j: j.get("first_seen", ""), reverse=True)

    for j in all_jobs:
        j["is_new"] = j.get("link") in new_links

    platforms = sorted({j.get("platform", "N/A") for j in all_jobs})

    html = _render_html(all_jobs, platforms, len(new_jobs))

    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def _render_html(jobs, platforms, new_count):
    jobs_json = json.dumps(jobs, ensure_ascii=False)
    platforms_json = json.dumps(platforms)
    last_updated = datetime.now().strftime("%d %b %Y, %I:%M %p")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Job Alert Dashboard</title>
<style>
  :root {{
    --bg: #0f1117;
    --card: #171a23;
    --border: #262a37;
    --text: #e8e9ec;
    --muted: #8b8fa3;
    --accent: #5b8cff;
    --new: #34d399;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 24px;
  }}
  .header {{
    max-width: 1100px;
    margin: 0 auto 20px auto;
  }}
  h1 {{ font-size: 24px; margin: 0 0 4px 0; }}
  .sub {{ color: var(--muted); font-size: 14px; }}
  .controls {{
    max-width: 1100px;
    margin: 0 auto 16px auto;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }}
  input[type=text] {{
    flex: 1;
    min-width: 200px;
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--card);
    color: var(--text);
    font-size: 14px;
  }}
  select {{
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--card);
    color: var(--text);
    font-size: 14px;
  }}
  .stats {{
    max-width: 1100px;
    margin: 0 auto 16px auto;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }}
  .stat {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 13px;
    color: var(--muted);
  }}
  .stat b {{ color: var(--text); font-size: 16px; display: block; }}
  .grid {{
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    gap: 10px;
  }}
  .job {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }}
  .job-title {{ font-size: 15px; font-weight: 600; }}
  .job-meta {{ color: var(--muted); font-size: 13px; margin-top: 3px; }}
  .badge {{
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 20px;
    background: rgba(91,140,255,0.15);
    color: var(--accent);
    white-space: nowrap;
  }}
  .badge.new {{
    background: rgba(52,211,153,0.15);
    color: var(--new);
  }}
  .apply-btn {{
    padding: 8px 16px;
    border-radius: 8px;
    background: var(--accent);
    color: white;
    text-decoration: none;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
  }}
  .empty {{ text-align: center; color: var(--muted); padding: 40px; }}
</style>
</head>
<body>

<div class="header">
  <h1>📋 Job Alert Dashboard</h1>
  <div class="sub">Last updated: {last_updated} &middot; Tracking LinkedIn, Naukri, Indeed &amp; Wellfound</div>
</div>

<div class="stats">
  <div class="stat"><b id="totalCount">0</b>Total jobs tracked</div>
  <div class="stat"><b>{new_count}</b>New jobs this run</div>
</div>

<div class="controls">
  <input type="text" id="searchBox" placeholder="Search by title or company...">
  <select id="platformFilter">
    <option value="all">All Platforms</option>
  </select>
  <select id="newFilter">
    <option value="all">All Jobs</option>
    <option value="new">New Only</option>
  </select>
</div>

<div class="grid" id="jobGrid"></div>
<div class="empty" id="emptyMsg" style="display:none;">Koi job match nahi hua filters se.</div>

<script>
  const jobs = {jobs_json};
  const platforms = {platforms_json};

  const grid = document.getElementById('jobGrid');
  const searchBox = document.getElementById('searchBox');
  const platformFilter = document.getElementById('platformFilter');
  const newFilter = document.getElementById('newFilter');
  const emptyMsg = document.getElementById('emptyMsg');
  const totalCount = document.getElementById('totalCount');

  totalCount.textContent = jobs.length;

  platforms.forEach(p => {{
    const opt = document.createElement('option');
    opt.value = p;
    opt.textContent = p;
    platformFilter.appendChild(opt);
  }});

  function render() {{
    const q = searchBox.value.toLowerCase();
    const platform = platformFilter.value;
    const newOnly = newFilter.value === 'new';

    const filtered = jobs.filter(j => {{
      const matchesQ = !q || (j.title || '').toLowerCase().includes(q) || (j.company || '').toLowerCase().includes(q);
      const matchesPlatform = platform === 'all' || j.platform === platform;
      const matchesNew = !newOnly || j.is_new;
      return matchesQ && matchesPlatform && matchesNew;
    }});

    grid.innerHTML = '';
    emptyMsg.style.display = filtered.length === 0 ? 'block' : 'none';

    filtered.forEach(j => {{
      const div = document.createElement('div');
      div.className = 'job';
      div.innerHTML = `
        <div>
          <div class="job-title">${{j.title}} ${{j.is_new === 'True' || j.is_new === true ? '<span class="badge new">NEW</span>' : ''}}</div>
          <div class="job-meta">${{j.company}} &middot; ${{j.location}} &middot; <span class="badge">${{j.platform}}</span></div>
        </div>
        <a class="apply-btn" href="${{j.link}}" target="_blank" rel="noopener">View / Apply</a>
      `;
      grid.appendChild(div);
    }});
  }}

  searchBox.addEventListener('input', render);
  platformFilter.addEventListener('change', render);
  newFilter.addEventListener('change', render);

  render();
</script>

</body>
</html>
"""
