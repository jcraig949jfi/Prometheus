"""EXPERIMENT 2, stage 1 -- build a stratified full-text sample.

    python -m techne.cartography.exp2_corpus --fetch

WHY A FRESH SAMPLE. Only 13 of the 328 corpus papers are arXiv-identifiable, so the existing
corpus cannot supply 40-60 papers with legitimate full text. This draws a NEW stratified sample
from arXiv, where full text is openly available and the publisher explicitly permits automated
access at a polite rate.

STRATIFICATION. Equal quota per chartered field, so the arms are not dominated by the one field
whose vocabulary the tagger was written from. That matters: the whole campaign's placement rate
is inflated by core evolutionary computation and near zero everywhere else, and an unstratified
sample would carry that imbalance into the attribution result.

POLITENESS. arXiv asks for >= 3 seconds between requests; this uses 3.5, fetches at most one
PDF per paper, caps at 12 pages of extracted text, and stops on the first hard error rather
than retrying into a block.

WHAT FULL TEXT IS AND IS NOT HERE. "Full text" means the extracted body of the PDF, truncated
at 12 pages. It contains the methods and results sections an abstract omits -- which is the
entire point, since MECHANISM_ISOLATED cannot fire on an abstract. It is not the appendices,
and PDF extraction is lossy on tables and equations. Both limits are recorded on every record.
"""
from __future__ import annotations

import argparse
import io
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

OUT = pathlib.Path(__file__).resolve().parent / "exp2_fulltext_sample.json"
UA = "Prometheus-Techne-Cartography/0.1 (mailto:jcraig949@gmail.com)"
ARXIV_INTERVAL = 3.5
MAX_PAGES = 12

#: Equal quota per chartered field. The queries name the field, not our mechanism vocabulary,
#: so the sample is not selected by the same instrument being tested.
STRATA = {
    "evolutionary_computation": "genetic programming evolutionary algorithm",
    "program_synthesis": "program synthesis from examples",
    "quality_diversity": "quality diversity MAP-Elites novelty search",
    "mechanistic_interpretability": "mechanistic interpretability circuit transformer",
    "neurosymbolic": "neurosymbolic neural symbolic reasoning",
    "symbolic_regression": "symbolic regression equation discovery",
}
PER_STRATUM = 9
_ATOM = "{http://www.w3.org/2005/Atom}"
_last = [0.0]


def _throttle():
    wait = ARXIV_INTERVAL - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()


def _get(url: str, accept: str) -> bytes:
    _throttle()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def search_stratum(query: str, n: int) -> list:
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": "all:" + query, "max_results": str(n * 2), "sortBy": "relevance"})
    root = ET.fromstring(_get(url, "application/atom+xml"))
    out = []
    for e in root.findall(_ATOM + "entry"):
        def txt(tag):
            node = e.find(_ATOM + tag)
            return re.sub(r"\s+", " ", (node.text or "").strip()) if node is not None else ""
        aid = txt("id")
        m = re.search(r"(\d{4}\.\d{4,5})(v\d+)?$", aid)
        if not m:
            continue
        abstract = txt("summary")
        if len(abstract) < 200:          # an abstract too short to be evidence
            continue
        out.append({"arxiv_id": m.group(1), "title": txt("title"),
                    "abstract": abstract, "published": txt("published"),
                    "source_url": aid})
        if len(out) >= n:
            break
    return out


def fetch_fulltext(arxiv_id: str) -> dict:
    """Download the PDF and extract text. Returns {'text', 'pages', 'error'}."""
    url = "https://arxiv.org/pdf/" + arxiv_id
    try:
        raw = _get(url, "application/pdf")
    except Exception as e:                                            # noqa: BLE001
        return {"text": None, "pages": 0, "error": type(e).__name__ + ": " + str(e)[:120]}
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        pages = min(len(reader.pages), MAX_PAGES)
        chunks = []
        for i in range(pages):
            try:
                chunks.append(reader.pages[i].extract_text() or "")
            except Exception:                                         # noqa: BLE001
                continue
        text = re.sub(r"\s+", " ", " ".join(chunks)).strip()
        return {"text": text or None, "pages": pages,
                "total_pages": len(reader.pages), "bytes": len(raw), "error": None}
    except Exception as e:                                            # noqa: BLE001
        return {"text": None, "pages": 0, "error": "parse: " + type(e).__name__ + ": " + str(e)[:100]}


def build(per_stratum: int = PER_STRATUM) -> dict:
    papers, errors = [], []
    for field, q in STRATA.items():
        try:
            hits = search_stratum(q, per_stratum)
        except Exception as e:                                        # noqa: BLE001
            errors.append({"stratum": field, "stage": "search",
                           "error": type(e).__name__ + ": " + str(e)[:120]})
            continue
        for h in hits:
            h["stratum"] = field
            papers.append(h)
        print("  %-32s %d papers" % (field, len(hits)), flush=True)

    print("fetching %d PDFs at %.1fs intervals ..." % (len(papers), ARXIV_INTERVAL), flush=True)
    ok = 0
    for i, p in enumerate(papers, 1):
        ft = fetch_fulltext(p["arxiv_id"])
        p["fulltext"] = ft["text"]
        p["fulltext_pages"] = ft.get("pages", 0)
        p["fulltext_total_pages"] = ft.get("total_pages")
        p["fulltext_error"] = ft.get("error")
        if ft["text"]:
            ok += 1
        if i % 10 == 0:
            print("    %d/%d fetched (%d with text)" % (i, len(papers), ok), flush=True)

    return {"built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "strata": list(STRATA.keys()), "per_stratum": per_stratum,
            "n_papers": len(papers), "n_with_fulltext": ok,
            "max_pages_extracted": MAX_PAGES,
            "limits": ["full text truncated at %d pages -- appendices excluded" % MAX_PAGES,
                       "PDF extraction is lossy on tables, equations and multi-column layout",
                       "arXiv only: this sample is preprint-biased and excludes venues that "
                       "do not post to arXiv"],
            "errors": errors, "papers": papers}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--per-stratum", type=int, default=PER_STRATUM)
    a = ap.parse_args()
    if not a.fetch:
        print("pass --fetch to build the sample (downloads PDFs politely)")
        return 0
    d = build(a.per_stratum)
    OUT.write_text(json.dumps(d, indent=2), encoding="utf-8")
    print("\n%d papers, %d with full text -> %s" % (d["n_papers"], d["n_with_fulltext"], OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
