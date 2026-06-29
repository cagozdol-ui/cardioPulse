#!/usr/bin/env python3
"""
CardioPulse - generate_html.py
================================
data/latest.json dosyasını okuyup docs/index.html olarak statik bir
sayfa üretir (GitHub Pages /docs klasöründen yayın yapacak şekilde).
"""
import json
import os
from datetime import datetime

TYPE_LABELS_TR = {
    "Practice Guideline": "Kılavuz",
    "Guideline": "Kılavuz",
    "Randomized Controlled Trial": "RKÇ",
    "Meta-Analysis": "Meta-Analiz",
    "Systematic Review": "Sistematik Derleme",
    "Review": "Derleme",
    "Multicenter Study": "Çok Merkezli",
    "Observational Study": "Gözlemsel",
    "Comparative Study": "Karşılaştırmalı",
    "Clinical Trial": "Klinik Çalışma",
    "Editorial": "Editöryal",
}

MAX_SCORE = 90  # skor çubuğunu normalize etmek için yaklaşık tavan


def tr_type_label(primary_type):
    return TYPE_LABELS_TR.get(primary_type, "Orijinal Araştırma")


def tier_badge(tier):
    return {"tier1": "TIER 1", "tier2": "TIER 2", "diger": ""}.get(tier, "")


def fmt_date(iso_date):
    if not iso_date:
        return "tarih belirsiz"
    try:
        d = datetime.fromisoformat(iso_date)
        aylar = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
        return f"{d.day} {aylar[d.month - 1]} {d.year}"
    except ValueError:
        return iso_date


def render_article(a):
    pct = min(100, round(100 * a["score"] / MAX_SCORE))
    type_label = tr_type_label(a.get("primary_type"))
    tier = a.get("tier", "diger")
    badge = tier_badge(tier)
    badge_html = f'<span class="tag tag-{tier}">{badge}</span>' if badge else ""
    author = a.get("first_author") or "—"

    return f"""
    <article class="entry entry-{tier}">
      <div class="entry-main">
        <div class="entry-tags">
          {badge_html}
          <span class="tag tag-type">{type_label}</span>
        </div>
        <h3 class="entry-title">
          <a href="{a['url']}" target="_blank" rel="noopener">{a['title']}</a>
        </h3>
        <div class="entry-meta">{author} et al. &middot; <em>{a['journal']}</em> &middot; {fmt_date(a['pub_date'])}</div>
      </div>
      <div class="entry-score">
        <div class="score-num">{a['score']}</div>
        <div class="score-label">SKOR</div>
        <div class="score-strip"><div class="score-strip-fill" style="width:{pct}%"></div></div>
      </div>
    </article>"""


def render_category(key, cat, active):
    articles_html = "\n".join(render_article(a) for a in cat["articles"])
    active_class = " active" if active else ""
    return f"""
    <section class="panel{active_class}" id="panel-{key}">
      <div class="panel-stats">
        <div class="stat"><span class="stat-num">{cat['total_count']}</span><span class="stat-label">MAKALE</span></div>
        <div class="stat"><span class="stat-num">{cat['tier1_count']}</span><span class="stat-label">TIER 1 MAKALE</span></div>
      </div>
      <div class="entries">{articles_html if articles_html else '<p class="empty">Bu pencerede eşleşen makale bulunamadı.</p>'}</div>
    </section>"""


def render_html(data):
    cats = data["categories"]
    keys = list(cats.keys())
    tabs_html = "\n".join(
        f'<button class="tab{" active" if i == 0 else ""}" data-target="panel-{k}">{cats[k]["label"]}</button>'
        for i, k in enumerate(keys)
    )
    panels_html = "\n".join(
        render_category(k, cats[k], active=(i == 0)) for i, k in enumerate(keys)
    )
    generated = datetime.fromisoformat(data["generated_at"]).strftime("%d.%m.%Y %H:%M")

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CardioPulse — Kardiyoloji Makale Radarı</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --paper: #EEF0EA;
    --card: #FAFBF7;
    --ink: #1A1D1B;
    --ink-soft: #5B5F58;
    --arterial: #9A2B2B;
    --arterial-soft: #C97A7A;
    --venous: #2F5D62;
    --line: #D2D5C9;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: 'Inter', sans-serif;
  }}
  .wrap {{ max-width: 880px; margin: 0 auto; padding: 28px 20px 80px; }}

  .masthead {{
    border-bottom: 3px solid var(--ink);
    padding-bottom: 18px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .masthead h1 {{
    font-family: 'Source Serif 4', serif;
    font-weight: 700;
    font-size: 2.1rem;
    margin: 0;
    letter-spacing: -0.01em;
  }}
  .masthead h1 span {{ color: var(--arterial); }}
  .masthead .meta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--ink-soft);
    text-align: right;
  }}
  .tagline {{
    font-family: 'Source Serif 4', serif;
    font-style: italic;
    color: var(--ink-soft);
    font-size: 1rem;
    margin: 10px 0 22px;
  }}

  .tabs {{
    display: flex;
    gap: 2px;
    margin-bottom: 22px;
    border-bottom: 1px solid var(--line);
  }}
  .tab {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    background: none;
    border: none;
    padding: 10px 16px;
    cursor: pointer;
    color: var(--ink-soft);
    border-bottom: 3px solid transparent;
    transition: color 0.15s, border-color 0.15s;
  }}
  .tab:hover {{ color: var(--ink); }}
  .tab.active {{
    color: var(--ink);
    border-bottom-color: var(--arterial);
    font-weight: 600;
  }}

  .panel {{ display: none; }}
  .panel.active {{ display: block; }}

  .panel-stats {{
    display: flex;
    gap: 28px;
    margin-bottom: 24px;
  }}
  .stat-num {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    display: block;
    color: var(--arterial);
  }}
  .stat-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: var(--ink-soft);
    letter-spacing: 0.05em;
  }}

  .entries {{ display: flex; flex-direction: column; gap: 14px; }}

  .entry {{
    background: var(--card);
    border-left: 4px solid var(--line);
    border-radius: 2px;
    padding: 16px 18px;
    display: flex;
    justify-content: space-between;
    gap: 18px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  }}
  .entry-tier1 {{ border-left-color: var(--arterial); }}
  .entry-tier2 {{ border-left-color: var(--venous); }}

  .entry-main {{ flex: 1; min-width: 0; }}
  .entry-tags {{ display: flex; gap: 6px; margin-bottom: 8px; }}
  .tag {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.04em;
    padding: 2px 7px;
    border-radius: 2px;
    background: var(--line);
    color: var(--ink-soft);
  }}
  .tag-tier1 {{ background: var(--arterial); color: #fff; }}
  .tag-tier2 {{ background: var(--venous); color: #fff; }}

  .entry-title {{
    font-family: 'Source Serif 4', serif;
    font-size: 1.08rem;
    font-weight: 600;
    line-height: 1.35;
    margin: 0 0 6px;
  }}
  .entry-title a {{ color: var(--ink); text-decoration: none; }}
  .entry-title a:hover {{ color: var(--arterial); text-decoration: underline; }}

  .entry-meta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    color: var(--ink-soft);
  }}
  .entry-meta em {{ font-style: italic; }}

  .entry-score {{
    flex-shrink: 0;
    width: 76px;
    text-align: center;
    border-left: 1px solid var(--line);
    padding-left: 14px;
  }}
  .score-num {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--ink);
    line-height: 1;
  }}
  .score-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: var(--ink-soft);
    letter-spacing: 0.06em;
    margin-bottom: 8px;
  }}
  .score-strip {{
    height: 3px;
    background: var(--line);
    border-radius: 2px;
    overflow: hidden;
  }}
  .score-strip-fill {{ height: 100%; background: var(--arterial); }}

  .empty {{ color: var(--ink-soft); font-style: italic; }}

  .footer {{
    margin-top: 50px;
    padding-top: 16px;
    border-top: 1px solid var(--line);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--ink-soft);
  }}

  @media (max-width: 560px) {{
    .masthead {{ flex-direction: column; align-items: flex-start; }}
    .masthead .meta {{ text-align: left; }}
    .entry {{ flex-direction: column; }}
    .entry-score {{ width: auto; border-left: none; border-top: 1px solid var(--line); padding: 10px 0 0; text-align: left; }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <div class="masthead">
    <h1>Cardio<span>Pulse</span></h1>
    <div class="meta">GÜNCELLENDİ<br>{generated}</div>
  </div>
  <p class="tagline">Son {data['window_days']} günde yayınlanan kardiyoloji literatüründen öne çıkanlar.</p>

  <div class="tabs">{tabs_html}</div>
  {panels_html}

  <div class="footer">
    Dergi kalitesi, makale tipi ve güncellik baz alınarak otomatik skorlanmıştır · Veri kaynağı: PubMed/NCBI
  </div>
</div>

<script>
  document.querySelectorAll('.tab').forEach(tab => {{
    tab.addEventListener('click', () => {{
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(tab.dataset.target).classList.add('active');
    }});
  }});
</script>
</body>
</html>"""


def main():
    with open(os.path.join("data", "latest.json"), encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs("docs", exist_ok=True)
    out_path = os.path.join("docs", "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(render_html(data))

    print(f"Sayfa üretildi -> {out_path}")


if __name__ == "__main__":
    main()
