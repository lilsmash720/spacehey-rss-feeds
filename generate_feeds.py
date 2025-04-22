import feedparser
from datetime import datetime

feeds = {
    "movies": "https://api.simkl.com/feeds/list/movies/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us",
    "tv": "https://api.simkl.com/feeds/list/tv/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
}

def generate_html(title, entries):
    html = f"<div><h3>{title}</h3><ul>"
    for entry in entries[:5]:  # limit to top 5
        html += f'<li><a href="{entry.link}" target="_blank">{entry.title}</a></li>'
    html += "</ul></div>"
    return html

for name, url in feeds.items():
    d = feedparser.parse(url)
    html = generate_html(f"Latest {name.title()} Watched", d.entries)
    with open(f"{name}.html", "w", encoding="utf-8") as f:
        f.write(html)
