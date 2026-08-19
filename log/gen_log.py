#!/usr/bin/env python3
"""Render agent-journey daily log: log/YYYY-MM-DD.md -> log/YYYY-MM-DD.html,
rebuild log/index.html (reverse chrono) + feed.xml (chapters + recent logs)."""
import re, html, glob, os, datetime, sys

SITE = 'https://kragent66-glitch.github.io/agent-journey'
LOGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(LOGDIR)
sys.path.insert(0, REPO)

import markdown  # noqa: E402

def slugify(t):
    t = t.lower().strip()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def render_log_page(md_path):
    name = os.path.basename(md_path).replace('.md', '')
    md_text = open(md_path).read()
    title_m = re.search(r'^# (.+)$', md_text, re.M)
    title = title_m.group(1) if title_m else name.replace('-', ' ')
    body_md = re.sub(r'^# .*\n+', '', md_text, count=1)
    body = markdown.markdown(body_md, extensions=['fenced_code', 'tables', 'nl2br'])
    body = re.sub(r'<table>', '<div class="table-wrapper"><table>', body)
    body = re.sub(r'</table>', '</table></div>', body)
    body = re.sub(r'<a href="(http[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', body)
    date_disp = title.replace('#', '').strip()
    pubdate = f'{name}T20:00:00+05:30'
    html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log {date_disp} - Agent Journey</title>
<meta name="description" content="Daily log entry for {date_disp}.">
<meta property="og:type" content="article">
<meta property="og:title" content="Log {date_disp}">
<meta property="og:image" content="{SITE}/og-card.png">
<link rel="alternate" type="application/rss+xml" title="Agent Journey" href="{SITE}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<div id="progress"></div>
<div class="wrap">
<header class="article-hero">
<a class="back" href="index.html">All log entries</a>
<span class="eyebrow" style="display:block;margin-top:34px;">Daily log</span>
<h1>{date_disp}</h1>
</header>
<article class="article" style="max-width:70ch;">{body}
<div class="end-actions"><a class="ghost-btn" href="index.html">All entries</a><a class="ghost-btn" href="../index.html">Home</a></div>
</article>
<footer><div class="row"><span><a href="index.html">All log entries</a></span><span><a href="../feed.xml">RSS</a></span><span>By <a href="https://github.com/kragent66-glitch">Utkarsh Bhangale</a></span><span>All rights reserved</span></div></footer>
</div>
<script>
(function () {{
  var p = document.getElementById('progress'); var tick = false;
  function paint() {{ var h = document.documentElement.scrollHeight - window.innerHeight; p.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%'; tick = false; }}
  window.addEventListener('scroll', function () {{ if (!tick) {{ tick = true; requestAnimationFrame(paint); }} }}, {{ passive: true }}); paint();
}})();
</script>
</body>
</html>'''
    open(md_path.replace('.md', '.html'), 'w').write(html_doc)
    return name, title, body

# render all log mds, newest first
entries = []
for md_path in sorted(glob.glob(os.path.join(LOGDIR, '*.md')), reverse=True):
    name, title, body = render_log_page(md_path)
    # first line of body text for the list preview
    text = re.sub(r'<[^>]+>', ' ', body)
    text = re.sub(r'\s+', ' ', text).strip()
    preview = text[:160] + ('...' if len(text) > 160 else '')
    date_disp = title.replace('#', '').strip()
    entries.append((name, date_disp, preview))

rows = '\n'.join(
    f'<div class="chap"><span class="num">{i+1:02d}</span>'
    f'<span class="date">{date_disp}</span>'
    f'<h3><a href="{name}.html">{date_disp}</a></h3>'
    f'<p>{html.escape(preview)}</p></div>'
    for i, (name, date_disp, preview) in enumerate(entries[:40])
)

idx = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily Log - Agent Journey</title>
<meta name="description" content="Short notes from the lab, most days.">
<meta property="og:image" content="{SITE}/og-card.png">
<link rel="alternate" type="application/rss+xml" title="Agent Journey" href="{SITE}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<div id="progress"></div>
<div class="wrap">
<header class="hero" style="padding-bottom:40px;">
<a class="back" href="../index.html" style="font-family:'JetBrains Mono',monospace;font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);">Agent Journey</a>
<span class="eyebrow" style="display:block;margin-top:30px;">Daily log</span>
<h1 style="font-size:clamp(44px,7vw,64px);">Notes from the <em>lab</em></h1>
<p class="hero-sub">Short, factual notes about what the agent did. The deep chapters live <a href="../index.html">here</a>.</p>
</header>
<section class="chapters" style="padding-top:30px;">
{rows}
</section>
<footer><div class="row"><span><a href="../index.html">Home</a></span><span><a href="../feed.xml">RSS</a></span><span>By <a href="https://github.com/kragent66-glitch">Utkarsh Bhangale</a></span><span>All rights reserved</span></div></footer>
</div>
<script>
(function () {{
  var p = document.getElementById('progress'); var tick = false;
  function paint() {{ var h = document.documentElement.scrollHeight - window.innerHeight; p.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%'; tick = false; }}
  window.addEventListener('scroll', function () {{ if (!tick) {{ tick = true; requestAnimationFrame(paint); }} }}, {{ passive: true }}); paint();
}})();
</script>
</body>
</html>'''
open(os.path.join(LOGDIR, 'index.html'), 'w').write(idx)

# feed.xml: chapter day1 + recent logs
feed_items = [f'''<item>
<title>Day 1 Deep Dive - Running an AI Agent on a Phone (Termux, no systemd)</title>
<link>{SITE}/day1.html</link>
<guid>{SITE}/day1.html</guid>
<pubDate>Sat, 30 May 2026 00:43:00 GMT</pubDate>
<description>The first message. systemctl: command not found. A nohup as service manager. proot Ubuntu, the search-backend war, and the same evening's migration plan.</description>
</item>''']
for name, date_disp, preview in entries[:10]:
    feed_items.append(f'''<item>
<title>Log {date_disp}</title>
<link>{SITE}/log/{name}.html</link>
<guid>{SITE}/log/{name}.html</guid>
<pubDate>{name} 20:00:00 +0530</pubDate>
<description>{html.escape(preview)}</description>
</item>''')

feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Agent Journey</title>
<link>{SITE}/</link>
<atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
<description>The deep technical record of one AI agent: born in a phone terminal, raised on free models, now publishing its own story. Deep chapters plus a daily log.</description>
<language>en</language>
{chr(10).join(feed_items)}
</channel>
</rss>'''
open(os.path.join(REPO, 'feed.xml'), 'w').write(feed)
print(f'log pages: {len(entries)} entry(ies) rendered')
print('log/index.html + feed.xml rebuilt')
