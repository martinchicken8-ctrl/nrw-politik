import os

files = {
"index.html": """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>NRW Politik News</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>

<header>
<h1>NRW Politik News</h1>
<input id="search" placeholder="Suche..." />
<select id="sourceFilter">
<option value="">Alle Quellen</option>
</select>
</header>

<main id="app"></main>

<script src="app.js"></script>
</body>
</html>
""",

"app.js": """let data = [];

async function loadData() {
const res = await fetch("./data/data.json");
const json = await res.json();

data = json.items;
render(data);
populateFilters(data);
}

function render(items) {
const app = document.getElementById("app");
app.innerHTML = "";

items.forEach(item => {
const div = document.createElement("div");
div.className = "card";

div.innerHTML = `
<h3><a href="${item.link}" target="_blank">${item.title}</a></h3>
<p class="meta">${item.source} • ${item.published}</p>
<p>${item.summary || ""}</p>
`;

app.appendChild(div);
});
}

function populateFilters(items) {
const sources = [...new Set(items.map(i => i.source))];
const select = document.getElementById("sourceFilter");

sources.forEach(s => {
const opt = document.createElement("option");
opt.value = s;
opt.textContent = s;
select.appendChild(opt);
});
}

function applyFilters() {
const search = document.getElementById("search").value.toLowerCase();
const source = document.getElementById("sourceFilter").value;

const filtered = data.filter(item => {
const matchesSearch =
item.title.toLowerCase().includes(search) ||
item.summary.toLowerCase().includes(search);

const matchesSource = source === "" || item.source === source;

return matchesSearch && matchesSource;
});

render(filtered);
}

document.getElementById("search").addEventListener("input", applyFilters);
document.getElementById("sourceFilter").addEventListener("change", applyFilters);

loadData();
""",

"styles.css": """body {
font-family: system-ui;
margin: 0;
background: #f6f7f9;
}

header {
background: #1f2937;
color: white;
padding: 16px;
}

header input, header select {
margin-top: 10px;
padding: 8px;
margin-right: 10px;
}

.card {
background: white;
margin: 12px;
padding: 12px;
border-radius: 8px;
}
""",

"data/data.json": """{
"updated": "",
"items": []
}
""",

"scripts/fetch_rss.py": """import feedparser
import json
from datetime import datetime

FEEDS = [
{"name": "Landtag NRW", "url": "https://www.landtag.nrw.de/rss/rss.xml"},
{"name": "WDR Politik", "url": "https://www1.wdr.de/mediathek/video/politik/index.xml"}
]

def extract():
items = []
for feed in FEEDS:
parsed = feedparser.parse(feed["url"])
for e in parsed.entries:
items.append({
"source": feed["name"],
"title": e.get("title",""),
"link": e.get("link",""),
"published": e.get("published",""),
"summary": e.get("summary","")
})
return items

if __name__ == "__main__":
data = {
"updated": datetime.utcnow().isoformat(),
"items": extract()
}

os.makedirs("data", exist_ok=True)

with open("data/data.json","w",encoding="utf-8") as f:
json.dump(data,f,ensure_ascii=False,indent=2)

print("done")
""",

".github/workflows/update-data.yml": """name: Update NRW News

on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - run: pip install feedparser

      - run: python scripts/fetch_rss.py

      - run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add data/data.json
          git commit -m "update" || exit 0
          git push
""",

"README.md": """# NRW Politik News

Statische RSS News Aggregation für NRW Politik.

## Setup

1. GitHub Repo erstellen
2. Dateien pushen
3. GitHub Pages aktivieren
4. Action läuft automatisch täglich

## Daten

- Landtag NRW
- WDR Politik
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Projekt erstellt.")
