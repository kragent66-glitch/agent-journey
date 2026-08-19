#!/usr/bin/env python3
"""Generate day1.html (Nocturne article w/ TOC, byline, JSON-LD, prev/next) + feed.xml + index refresh."""
import re, html, datetime
import markdown

MD = '/home/ubuntu/aswp/linkedin/blog/day1_deep_dive.md'
OUT = '/home/ubuntu/agent-journey/day1.html'
FEED = '/home/ubuntu/agent-journey/feed.xml'
INDEX = '/home/ubuntu/agent-journey/index.html'
SITE = 'https://kragent66-glitch.github.io/agent-journey'

def slugify(t):
    t = re.sub(r'^\d+\.\s*', '', t).strip().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

md_text = open(MD).read()
words = len(md_text.split())
read_min = max(1, round(words / 200))

# strip the h1 title (template supplies it)
body_md = re.sub(r'^# .*\n+', '', md_text, count=1)
body = markdown.markdown(body_md, extensions=['fenced_code', 'tables', 'nl2br'])

# post-process: ids + TOC + table wrappers
toc = []
def h2_repl(m):
    txt = re.sub(r'<[^>]+>', '', m.group(1))
    sid = slugify(txt)
    toc.append((sid, txt))
    return f'<h2 id="{sid}">{m.group(1)}</h2>'
body = re.sub(r'<h2>(.*?)</h2>', h2_repl, body)
body = re.sub(r'<table>', '<div class="table-wrapper"><table>', body)
body = re.sub(r'</table>', '</table></div>', body)
# external links open new tab
body = re.sub(r'<a href="(http[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', body)

toc_html = '\n'.join(f'<li><a href="#{sid}">{txt}</a></li>' for sid, txt in toc)
toc_html = f'<nav class="toc" aria-label="On this page"><div class="toc-title">On this page</div><ol>{toc_html}</ol></nav>'

pub = '2026-05-30T06:13:00+05:30'
jsonld = f'''<script type="application/ld+json">{{
"@context":"https://schema.org",
"@type":"BlogPosting",
"headline":"Running an AI Agent on a Phone",
"description":"Day 1 of Agent Journey: no systemd, nohup as service manager, proot Ubuntu, and the migration plan. The engineering record behind the LinkedIn post.",
"datePublished":"2026-05-30",
"author":{{"@type":"Person","name":"Utkarsh Bhangale","url":"https://github.com/kragent66-glitch"}},
"publisher":{{"@type":"Organization","name":"Agent Journey","url":"{SITE}"}},
"mainEntityOfPage":"{SITE}/day1.html",
"wordCount":{words}
}}</script>'''

html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Day 1 Deep Dive - Running an AI Agent on a Phone</title>
<meta name="description" content="The engineering record of day 1: no systemd, nohup as service manager, proot, the search-backend war. {read_min} min read.">
<meta property="og:title" content="Day 1 - Running an AI Agent on a Phone (Termux, no systemd)">
<meta property="og:description" content="The engineering record of day 1: no systemd, nohup as service manager, proot, the search-backend war. {read_min} min read.">
<meta property="og:type" content="article">
<meta property="og:image" content="{SITE}/og-card.png">
<link rel="alternate" type="application/rss+xml" title="Agent Journey" href="{SITE}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
{jsonld}
</head>
<body>
<div id="progress"></div>
<div class="wrap">
  <header class="article-hero">
    <a class="back" href="index.html">All chapters</a>
    <span class="eyebrow" style="display:block;margin-top:34px;">Day 1 - May 30, 2026</span>
    <h1>Running an AI Agent on a <em>Phone</em></h1>
    <div class="byline">
      <span class="by-author">Utkarsh Bhangale</span>
      <span class="by-sep"></span>
      <span>May 30, 2026</span>
      <span class="by-sep"></span>
      <span>{read_min} min read</span>
      <span class="by-sep"></span>
      <span>{words:,} words</span>
    </div>
    <div class="chips">
      <span class="chip">Termux</span><span class="chip">no systemd</span><span class="chip">proot</span>
      <span class="chip">aarch64</span><span class="chip">build in public</span>
    </div>
  </header>
  <div class="article-grid">
    <article class="article">
    {body}
    <div class="end-actions">
      <button class="ghost-btn" id="copy-link">Copy link</button>
      <button class="ghost-btn" id="to-top">Back to top</button>
    </div>
    <nav class="nextprev" aria-label="Chapter navigation">
      <div class="np-block np-prev">
        <span class="np-label">Prev</span>
        <a href="index.html">All chapters</a>
      </div>
      <div class="np-block np-next">
        <span class="np-label">Next</span>
        <span class="np-soon">The free-model economy (coming soon)</span>
      </div>
    </nav>
    </article>
    <aside class="toc-wrap">{toc_html}</aside>
  </div>
  <footer>
    <div class="row">
      <span><a href="index.html">All chapters</a></span>
      <span><a href="feed.xml">RSS</a></span>
      <span>By <a href="https://github.com/kragent66-glitch">Utkarsh Bhangale</a></span>
      <span>All rights reserved</span>
    </div>
  </footer>
</div>
<script>
(function () {{
  var p = document.getElementById('progress');
  var ticking = false;
  function paint() {{
    var h = document.documentElement.scrollHeight - window.innerHeight;
    p.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
    ticking = false;
  }}
  window.addEventListener('scroll', function () {{ if (!ticking) {{ ticking = true; requestAnimationFrame(paint); }} }}, {{ passive: true }});
  paint();

  // copy buttons on code blocks
  document.querySelectorAll('pre').forEach(function (pre) {{
    var btn = document.createElement('button');
    btn.className = 'copy-code'; btn.textContent = 'Copy';
    pre.appendChild(btn);
    btn.addEventListener('click', function () {{
      var t = pre.querySelector('code').innerText;
      navigator.clipboard.writeText(t).then(function () {{
        btn.textContent = 'Copied';
        setTimeout(function () {{ btn.textContent = 'Copy'; }}, 1600);
      }});
    }});
  }});

  // TOC scrollspy
  var links = document.querySelectorAll('.toc a');
  if (links.length) {{
    var heads = Array.prototype.map.call(links, function (a) {{ return document.getElementById(a.getAttribute('href').slice(1)); }});
    var spy = new IntersectionObserver(function (entries) {{
      entries.forEach(function (e) {{
        if (e.isIntersecting) {{
          links.forEach(function (l) {{ l.classList.remove('active'); }});
          var hit = document.querySelector('.toc a[href="#' + e.target.id + '"]');
          if (hit) hit.classList.add('active');
        }}
      }});
    }}, {{ rootMargin: '-15% 0px -70% 0px' }});
    heads.forEach(function (h) {{ if (h) spy.observe(h); }});
  }}

  // end actions
  document.getElementById('copy-link').addEventListener('click', function () {{
    navigator.clipboard.writeText(location.href).then(function () {{
      var b = document.getElementById('copy-link'); b.textContent = 'Copied';
      setTimeout(function () {{ b.textContent = 'Copy link'; }}, 1600);
    }});
  }});
  document.getElementById('to-top').addEventListener('click', function () {{
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }});
}})();
</script>
</body>
</html>'''

open(OUT, 'w').write(html_doc)
print('day1.html:', len(html_doc), 'bytes,', len(toc), 'TOC entries,', read_min, 'min read')

# feed.xml (live posts only)
desc = html.escape("The deep technical record of one AI agent: born in a phone terminal, raised on free models, now publishing its own story.")
feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Agent Journey</title>
<link>{SITE}/</link>
<atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
<description>{desc}</description>
<language>en</language>
<item>
<title>Day 1 Deep Dive - Running an AI Agent on a Phone (Termux, no systemd)</title>
<link>{SITE}/day1.html</link>
<guid>{SITE}/day1.html</guid>
<pubDate>Sat, 30 May 2026 00:43:00 GMT</pubDate>
<description>{html.escape("The first message. systemctl: command not found. A nohup as service manager. proot Ubuntu, the search-backend war, Spotify OAuth from a phone browser, and the same evening's migration plan. " + str(words) + " words, " + str(read_min) + " min read.")}</description>
</item>
</channel>
</rss>'''
open(FEED, 'w').write(feed)
print('feed.xml written')

# index refresh: read-time chips + tags + RSS footer link
idx = open(INDEX).read()
idx = idx.replace(
    '<p>The first message. <code>systemctl: command not found</code>. A <code>nohup</code> as service manager. proot Ubuntu, the Docker dead-end, the search-backend war, Spotify OAuth from a phone browser, and the same evening\'s migration plan.</p>',
    '<p>The first message. <code>systemctl: command not found</code>. A <code>nohup</code> as service manager. proot Ubuntu, the Docker dead-end, the search-backend war, Spotify OAuth from a phone browser, and the same evening\'s migration plan.</p>\n      <div class="chap-meta"><span>{read_min} min read</span><span>Termux</span><span>no systemd</span><span>build in public</span></div>')
idx = idx.replace(
    '<span>Written with the agent this journey is about</span>',
    '<span><a href="feed.xml">RSS</a></span><span>Written with the agent this journey is about</span>')
open(INDEX, 'w').write(idx)
print('index.html refreshed')
