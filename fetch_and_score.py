#!/usr/bin/env python3
"""
CardioPulse - fetch_and_score.py
=================================
PubMed E-utilities üzerinden tanımlı dergi listelerinden son N günde
yayınlanan makaleleri çeker, skorlar ve data/latest.json dosyasına yazar.

Kullanım:
    python fetch_and_score.py

Gereksinim:
    pip install requests

Bu script GitHub Actions üzerinde günlük olarak çalıştırılmak üzere
tasarlanmıştır (bkz. .github/workflows/daily-update.yml), ancak yerelde
de manuel çalıştırılabilir.
"""
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta

import requests

import config

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def build_journal_term(journals):
    parts = [f'"{j}"[ta]' for j in journals]
    return "(" + " OR ".join(parts) + ")"


def esearch(term, mindate, maxdate, retmax=400):
    """PubMed araması yapar, PMID listesi döner."""
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": retmax,
        "datetype": "pdat",
        "mindate": mindate,
        "maxdate": maxdate,
    }
    if config.NCBI_API_KEY:
        params["api_key"] = config.NCBI_API_KEY
    if config.NCBI_EMAIL and "example.com" not in config.NCBI_EMAIL:
        params["email"] = config.NCBI_EMAIL

    resp = requests.get(f"{EUTILS_BASE}/esearch.fcgi", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


def efetch(pmids):
    """Verilen PMID'ler için tam künye bilgisini (XML) çeker."""
    if not pmids:
        return []

    articles = []
    chunk_size = 200
    for i in range(0, len(pmids), chunk_size):
        chunk = pmids[i : i + chunk_size]
        params = {
            "db": "pubmed",
            "id": ",".join(chunk),
            "rettype": "abstract",
            "retmode": "xml",
        }
        if config.NCBI_API_KEY:
            params["api_key"] = config.NCBI_API_KEY

        resp = requests.get(f"{EUTILS_BASE}/efetch.fcgi", params=params, timeout=60)
        resp.raise_for_status()
        articles.extend(parse_efetch_xml(resp.text))

        # Rate limit: API key yoksa 3/sn, varsa 10/sn sınırına uy
        time.sleep(0.4 if config.NCBI_API_KEY else 1.0)

    return articles


def parse_efetch_xml(xml_text):
    root = ET.fromstring(xml_text)
    out = []
    for article in root.findall(".//PubmedArticle"):
        try:
            pmid = article.findtext(".//PMID", default="")
            title = article.findtext(".//ArticleTitle", default="").strip()
            journal = article.findtext(".//Journal/Title", default="").strip()

            # Yayın tarihi (PubDate alanı çok değişken biçimde gelebilir)
            pub_date_el = article.find(".//Journal/JournalIssue/PubDate")
            pub_date = parse_pub_date(pub_date_el)

            # Makale tipleri
            pub_types = [
                pt.text for pt in article.findall(".//PublicationTypeList/PublicationType")
                if pt.text
            ]

            # İlk yazar
            first_author_el = article.find(".//AuthorList/Author")
            first_author = ""
            if first_author_el is not None:
                last = first_author_el.findtext("LastName", default="")
                fore = first_author_el.findtext("ForeName", default="")
                first_author = f"{last} {fore[:1]}".strip()

            # DOI
            doi = ""
            for eloc in article.findall(".//ELocationID"):
                if eloc.get("EIdType") == "doi":
                    doi = eloc.text or ""

            out.append(
                {
                    "pmid": pmid,
                    "title": title,
                    "journal": journal,
                    "pub_date": pub_date.isoformat() if pub_date else None,
                    "pub_types": pub_types,
                    "first_author": first_author,
                    "doi": doi,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                }
            )
        except Exception as e:  # noqa: BLE001 - tek makale parse hatası tüm batch'i durdurmasın
            print(f"[uyarı] makale parse edilemedi (PMID={pmid}): {e}", file=sys.stderr)
            continue
    return out


def parse_pub_date(pub_date_el):
    if pub_date_el is None:
        return None
    year = pub_date_el.findtext("Year")
    month = pub_date_el.findtext("Month") or "Jan"
    day = pub_date_el.findtext("Day") or "1"
    if not year:
        return None

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }
    try:
        m = month_map.get(month, int(month) if str(month).isdigit() else 1)
        d = int(day) if str(day).isdigit() else 1
        return date(int(year), m, d)
    except ValueError:
        try:
            return date(int(year), 1, 1)
        except ValueError:
            return None


def score_article(article, tier1_journals, tier2_journals, today):
    score = 0
    is_tier1 = article["journal"] in tier1_journals
    is_tier2 = article["journal"] in tier2_journals

    if is_tier1:
        score += config.JOURNAL_WEIGHT_TIER1
    elif is_tier2:
        score += config.JOURNAL_WEIGHT_TIER2

    # En yüksek ağırlıklı makale tipini al
    type_score = config.DEFAULT_ARTICLE_TYPE_WEIGHT
    matched_type = None
    for pt in article["pub_types"]:
        w = config.ARTICLE_TYPE_WEIGHTS.get(pt, 0)
        if w > type_score or matched_type is None:
            if w > 0:
                type_score = w
                matched_type = pt
    score += type_score

    # Güncellik
    if article["pub_date"]:
        pub_date = date.fromisoformat(article["pub_date"])
        days_old = (today - pub_date).days
        days_old = max(0, days_old)
        recency = max(
            0,
            round(
                config.RECENCY_MAX_WEIGHT
                * (config.RECENCY_WINDOW_DAYS - days_old)
                / config.RECENCY_WINDOW_DAYS
            ),
        )
        score += recency

    article["score"] = score
    article["tier"] = "tier1" if is_tier1 else ("tier2" if is_tier2 else "diger")
    article["primary_type"] = matched_type or (article["pub_types"][0] if article["pub_types"] else "Orijinal Araştırma")
    return article


def run_category(key, cat_config, mindate, maxdate, today):
    print(f"[{key}] taranıyor: {cat_config['label']}")
    all_journals = cat_config["tier1"] + cat_config["tier2"]
    term = build_journal_term(all_journals)

    pmids = esearch(term, mindate, maxdate)
    print(f"[{key}] {len(pmids)} makale bulundu, künye çekiliyor...")

    articles = efetch(pmids)
    scored = [
        score_article(a, cat_config["tier1"], cat_config["tier2"], today)
        for a in articles
    ]
    scored.sort(key=lambda a: a["score"], reverse=True)

    tier1_count = sum(1 for a in scored if a["tier"] == "tier1")
    return {
        "label": cat_config["label"],
        "articles": scored,
        "total_count": len(scored),
        "tier1_count": tier1_count,
    }


def main():
    today = date.today()
    mindate_dt = today - timedelta(days=config.LOOKBACK_DAYS)
    mindate = mindate_dt.strftime("%Y/%m/%d")
    maxdate = today.strftime("%Y/%m/%d")

    result = {
        "generated_at": datetime.now().isoformat(),
        "window_days": config.LOOKBACK_DAYS,
        "categories": {},
    }

    for key, cat_config in config.CATEGORIES.items():
        result["categories"][key] = run_category(key, cat_config, mindate, maxdate, today)

    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "latest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nTamamlandı -> {out_path}")
    for key, cat in result["categories"].items():
        print(f"  {cat['label']}: {cat['total_count']} makale ({cat['tier1_count']} Tier-1)")


if __name__ == "__main__":
    main()
