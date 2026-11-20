#!/usr/bin/env python
"""
按期刊名单从 OpenAlex 抓取已发表期刊论文，并合并进当天的论文池。

设计要点：
- query-first：只向 OpenAlex 请求名单内期刊、近 N 天发表的论文，几十条请求即可完成；
- OpenAlex 拿不到摘要（如 Elsevier 旗下的 The Lancet）时，用 PubMed 按 DOI 补摘要；
- 期刊论文常常晚于发表日才被收录，因此按「发表日回溯 lookback_days 天 + 已见 ID 去重」抓取，
  已见状态写在 archive/journal_seen.json；
- 结果追加到 archive/<token>/raw/arxiv_papers_<token>.json，下游召回/打分无需改动。

配置（config.yaml）：
journal_sources:
  enabled: true
  lookback_days: 30
  exclude_types: [editorial, paratext, erratum, letter, retraction]
  journals:
    - {name: The Lancet, issn: 0140-6736}
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List

import requests

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    from source_config import load_config_with_source_migration
except Exception:  # pragma: no cover
    from src.source_config import load_config_with_source_migration


ROOT_DIR = os.path.abspath(os.path.join(SRC_DIR, ".."))
CONFIG_FILE = os.path.join(ROOT_DIR, "config.yaml")
SEEN_FILE = os.path.join(ROOT_DIR, "archive", "journal_seen.json")
OPENALEX_WORKS = "https://api.openalex.org/works"
PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DATE_TOKEN_RE = re.compile(r"^\d{8}(-\d{8})?$")
DEFAULT_EXCLUDE_TYPES = ["editorial", "paratext", "erratum", "letter", "retraction"]
SEEN_KEEP_DAYS = 120
USER_AGENT = "daily-paper-reader-journal-fetcher"


def log(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {message}", flush=True)


def _norm(value: Any) -> str:
    return str(value or "").strip()


def load_journal_setting() -> Dict[str, Any]:
    try:
        config = load_config_with_source_migration(CONFIG_FILE, write_back=False) or {}
    except Exception as exc:
        log(f"[WARN] 读取 config.yaml 失败：{exc}")
        return {}
    setting = config.get("journal_sources") or {}
    return setting if isinstance(setting, dict) else {}


def resolve_run_token() -> str:
    token = _norm(os.getenv("DPR_RUN_DATE"))
    if DATE_TOKEN_RE.match(token):
        return token
    return datetime.now(timezone.utc).strftime("%Y%m%d")


# ---------------- 已见状态 ----------------

def load_seen() -> Dict[str, str]:
    if not os.path.exists(SEEN_FILE):
        return {}
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f) or {}
    except Exception:
        return {}
    ids = payload.get("ids") or {}
    return {str(k): str(v) for k, v in ids.items()} if isinstance(ids, dict) else {}


def save_seen(seen: Dict[str, str]) -> None:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=SEEN_KEEP_DAYS)).date().isoformat()
    kept = {k: v for k, v in seen.items() if v >= cutoff}
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"updated_at": datetime.now(timezone.utc).isoformat(), "ids": dict(sorted(kept.items()))},
            f,
            ensure_ascii=False,
            indent=1,
        )


# ---------------- OpenAlex ----------------

def _openalex_params(extra: Dict[str, Any]) -> Dict[str, Any]:
    params = dict(extra)
    api_key = _norm(os.getenv("OPENALEX_API_KEY"))
    if api_key:
        params["api_key"] = api_key
    return params


def _get_json(url: str, params: Dict[str, Any], *, retries: int = 4) -> Dict[str, Any]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=60, headers={"User-Agent": USER_AGENT})
            if resp.status_code in (429, 500, 502, 503, 504):
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            resp.raise_for_status()
            return resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"请求失败：{url} ({last_exc})")


def rebuild_abstract(inverted: Any) -> str:
    if not isinstance(inverted, dict) or not inverted:
        return ""
    positions: List[tuple[int, str]] = []
    for word, idxs in inverted.items():
        for idx in idxs or []:
            positions.append((int(idx), str(word)))
    positions.sort()
    return " ".join(word for _, word in positions).strip()


def _chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def fetch_openalex_works(issns: List[str], start_date: str, end_date: str) -> List[Dict[str, Any]]:
    works: List[Dict[str, Any]] = []
    select = ",".join(
        [
            "id", "doi", "title", "publication_date", "type", "authorships",
            "primary_location", "best_oa_location", "open_access", "abstract_inverted_index",
        ]
    )
    for group in _chunks(issns, 40):
        # 用页码翻页：无 API key 时 OpenAlex 不允许 cursor 翻页；页码翻页上限 1 万条，足够日常窗口
        page = 1
        while page <= 50:
            data = _get_json(
                OPENALEX_WORKS,
                _openalex_params(
                    {
                        "filter": (
                            f"primary_location.source.issn:{'|'.join(group)},"
                            f"from_publication_date:{start_date},to_publication_date:{end_date}"
                        ),
                        "select": select,
                        "per-page": 200,
                        "page": page,
                    }
                ),
            )
            results = data.get("results") or []
            works.extend(results)
            total = int((data.get("meta") or {}).get("count") or 0)
            if not results or page * 200 >= total:
                break
            page += 1
            time.sleep(0.2)
    return works


def normalize_work(work: Dict[str, Any]) -> Dict[str, Any] | None:
    openalex_id = _norm(work.get("id")).rsplit("/", 1)[-1].lower()
    title = re.sub(r"\s+", " ", _norm(work.get("title")))
    if not openalex_id or not title:
        return None
    doi = _norm(work.get("doi"))
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    venue = _norm(source.get("display_name"))
    best_oa = work.get("best_oa_location") or {}
    oa_pdf = _norm(best_oa.get("pdf_url"))
    landing = f"https://doi.org/{doi}" if doi else _norm(location.get("landing_page_url"))
    authors = [
        _norm((a.get("author") or {}).get("display_name"))
        for a in (work.get("authorships") or [])
        if _norm((a.get("author") or {}).get("display_name"))
    ]
    published = _norm(work.get("publication_date"))
    return {
        "id": f"journal-{openalex_id}",
        "source": "journal",
        "source_paper_id": openalex_id,
        "doi": doi,
        "venue": venue,
        "work_type": _norm(work.get("type")),
        "title": title,
        "abstract": rebuild_abstract(work.get("abstract_inverted_index")),
        "authors": authors,
        "primary_category": venue or None,
        "categories": [venue] if venue else [],
        "published": f"{published}T00:00:00+00:00" if published else None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "link": landing,
        "abs_url": landing,
        "pdf_url": oa_pdf,
        "is_oa": bool((work.get("open_access") or {}).get("is_oa")),
    }


# ---------------- PubMed 摘要补全 ----------------

def _pubmed_params(extra: Dict[str, Any]) -> Dict[str, Any]:
    params = dict(extra)
    api_key = _norm(os.getenv("NCBI_API_KEY"))
    if api_key:
        params["api_key"] = api_key
    params.setdefault("tool", USER_AGENT)
    return params


def fill_abstracts_from_pubmed(papers: List[Dict[str, Any]]) -> int:
    missing = {p["doi"].lower(): p for p in papers if not p.get("abstract") and p.get("doi")}
    if not missing:
        return 0
    filled = 0
    for group in _chunks(list(missing.keys()), 40):
        try:
            term = " OR ".join(f'"{doi}"[doi]' for doi in group)
            search = requests.post(
                PUBMED_ESEARCH,
                data=_pubmed_params({"db": "pubmed", "term": term, "retmode": "json", "retmax": 200}),
                timeout=60,
            )
            search.raise_for_status()
            pmids = ((search.json() or {}).get("esearchresult") or {}).get("idlist") or []
            time.sleep(0.4)
            if not pmids:
                continue
            fetch = requests.post(
                PUBMED_EFETCH,
                data=_pubmed_params({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}),
                timeout=60,
            )
            fetch.raise_for_status()
            root = ET.fromstring(fetch.content)
            for article in root.iter("PubmedArticle"):
                doi = ""
                for aid in article.iter("ArticleId"):
                    if aid.get("IdType") == "doi":
                        doi = _norm(aid.text).lower()
                        break
                paper = missing.get(doi)
                if not paper:
                    continue
                parts = []
                for node in article.iter("AbstractText"):
                    text = "".join(node.itertext()).strip()
                    label = _norm(node.get("Label"))
                    if text:
                        parts.append(f"{label}: {text}" if label else text)
                if parts:
                    paper["abstract"] = " ".join(parts)
                    filled += 1
            time.sleep(0.4)
        except Exception as exc:  # noqa: BLE001
            log(f"[WARN] PubMed 补摘要失败（跳过本批）：{exc}")
    return filled


# ---------------- 合并进论文池 ----------------

def merge_into_raw_pool(papers: List[Dict[str, Any]], run_token: str) -> str:
    raw_dir = os.path.join(ROOT_DIR, "archive", run_token, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    raw_path = os.path.join(raw_dir, f"arxiv_papers_{run_token}.json")
    existing: List[Dict[str, Any]] = []
    if os.path.exists(raw_path):
        try:
            with open(raw_path, "r", encoding="utf-8") as f:
                existing = json.load(f) or []
        except Exception:
            existing = []
    existing_ids = {_norm(p.get("id")) for p in existing if isinstance(p, dict)}
    existing_dois = {_norm(p.get("doi")).lower() for p in existing if isinstance(p, dict) and p.get("doi")}
    merged = list(existing)
    for paper in papers:
        if paper["id"] in existing_ids:
            continue
        if paper.get("doi") and paper["doi"].lower() in existing_dois:
            continue
        merged.append(paper)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    return raw_path


def fetch_journals(*, lookback_days: int | None = None, ignore_seen: bool = False) -> None:
    setting = load_journal_setting()
    if not setting.get("enabled"):
        log("[INFO] journal_sources 未启用，跳过期刊抓取。")
        return
    journals = setting.get("journals") or []
    issns = []
    for item in journals:
        issn = _norm(item.get("issn") if isinstance(item, dict) else item)
        if issn:
            issns.append(issn)
    if not issns:
        log("[WARN] journal_sources.journals 为空，跳过期刊抓取。")
        return

    days = int(lookback_days or setting.get("lookback_days") or 30)
    days = max(1, min(days, 365))
    exclude_types = {str(t).lower() for t in (setting.get("exclude_types") or DEFAULT_EXCLUDE_TYPES)}
    today = datetime.now(timezone.utc).date()
    start_date = (today - timedelta(days=days)).isoformat()
    end_date = today.isoformat()

    print("::group::Step 1b - fetch journals (OpenAlex)", flush=True)
    log(f"📚 [Journals] {len(issns)} 本期刊，发表日 {start_date} ~ {end_date}")
    try:
        raw_works = fetch_openalex_works(issns, start_date, end_date)
    except Exception as exc:  # noqa: BLE001
        # 期刊源失败不应拖垮整条流水线（arXiv 结果照常使用）
        log(f"[WARN] OpenAlex 抓取失败，本次不含期刊论文：{exc}")
        print("::endgroup::", flush=True)
        return

    seen = {} if ignore_seen else load_seen()
    papers: List[Dict[str, Any]] = []
    skipped_type = skipped_seen = 0
    for work in raw_works:
        paper = normalize_work(work)
        if not paper:
            continue
        if paper["work_type"].lower() in exclude_types:
            skipped_type += 1
            continue
        if paper["id"] in seen:
            skipped_seen += 1
            continue
        papers.append(paper)

    filled = fill_abstracts_from_pubmed(papers)
    no_abstract = sum(1 for p in papers if not p.get("abstract"))

    by_venue: Dict[str, int] = {}
    for p in papers:
        by_venue[p.get("venue") or "?"] = by_venue.get(p.get("venue") or "?", 0) + 1
    log(
        f"✅ [Journals] OpenAlex 返回 {len(raw_works)} 条；新论文 {len(papers)} 篇"
        f"（跳过已见 {skipped_seen}、非研究类型 {skipped_type}）；PubMed 补摘要 {filled} 篇，仍缺摘要 {no_abstract} 篇"
    )
    for venue, count in sorted(by_venue.items(), key=lambda kv: -kv[1]):
        log(f"    {count:>4}  {venue}")

    raw_path = merge_into_raw_pool(papers, resolve_run_token())
    log(f"💾 已合并进论文池：{raw_path}")

    stamp = today.isoformat()
    for p in papers:
        seen[p["id"]] = stamp
    save_seen(seen)
    print("::endgroup::", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="按期刊名单从 OpenAlex 抓取期刊论文并合并进论文池。")
    parser.add_argument("--days", type=int, default=None, help="发表日回溯天数（默认读 journal_sources.lookback_days）。")
    parser.add_argument("--ignore-seen", action="store_true", help="忽略已见状态。")
    args = parser.parse_args()
    fetch_journals(lookback_days=args.days, ignore_seen=bool(args.ignore_seen))
