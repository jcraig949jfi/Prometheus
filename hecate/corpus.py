"""Normalise the historical Hephaestus/Nous triplicates (read-only).

Sources (never modified):
  agents/nous/src/concepts.py            concept dictionary (95)
  agents/nous/runs/<run>/responses.jsonl Nous analyses of sampled triples
  agents/hephaestus/ledger.jsonl         Hephaestus forge outcomes
  agents/hephaestus/humanreadable/*.md   derived per-triple reports (pointer only)

Output: hecate/corpus/historical_triplicates.jsonl, one row per unique
unordered triple, sorted by id, plus hecate/corpus/CORPUS_RECEIPT.json.

Per the charter preface, a historical row keeps source "hephaestus",
sourceArtifact (the original path + line) and historicalId (the ledger key
if the triple was forged or scrapped, else the Nous run:line). The Nous
upstream is kept as its own list so the derivation is reconstructable.

    python -m hecate.corpus            # rebuild
"""

from __future__ import annotations

import collections
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "hecate", "corpus")
LEDGER = "agents/hephaestus/ledger.jsonl"
NOUS_GLOB = "agents/nous/runs/*/responses.jsonl"
HUMAN_DIR = "agents/hephaestus/humanreadable"


def triple_key(names) -> str:
    """The ledger's own key form: sorted names joined by ' + '."""
    return " + ".join(sorted(names))


def triple_id(names) -> str:
    return "HT-" + hashlib.sha256(triple_key(names).encode("utf-8")).hexdigest()[:10]


def load_concepts():
    sys.path.insert(0, os.path.join(ROOT, "agents", "nous", "src"))
    try:
        from concepts import CONCEPTS  # type: ignore
    finally:
        sys.path.pop(0)
    return {c["name"]: c for c in CONCEPTS}


def _rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def build():
    concepts = load_concepts()
    rows = {}

    def row_for(names):
        k = triple_key(names)
        if k not in rows:
            rows[k] = {"nous": [], "ledger": []}
        return rows[k]

    n_nous = 0
    for path in sorted(glob.glob(os.path.join(ROOT, NOUS_GLOB))):
        run = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                r = json.loads(line)
                n_nous += 1
                sc = r.get("score") or {}
                row_for(r["concept_names"])["nous"].append({
                    "artifact": _rel(path), "run": run, "line": line_no,
                    "model": r.get("model"),
                    "order": r["concept_names"],
                    "composite_score": sc.get("composite_score"),
                    "novelty": sc.get("novelty"),
                    "is_unproductive": sc.get("is_unproductive"),
                    "high_potential": sc.get("high_potential"),
                })

    n_ledger = 0
    with open(os.path.join(ROOT, LEDGER), encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            n_ledger += 1
            row_for(r["concept_names"])["ledger"].append({
                "artifact": LEDGER, "line": line_no, "key": r.get("key"),
                "status": r.get("status"), "reason": r.get("reason"),
                "accuracy": r.get("accuracy"), "timestamp": r.get("timestamp"),
            })

    human = {}
    for p in glob.glob(os.path.join(ROOT, HUMAN_DIR, "*.md")):
        names = os.path.basename(p)[:-3].split("---")
        if len(names) == 3:
            human[triple_key(n.replace("_", " ") for n in names)] = _rel(p)

    out = []
    unknown_concepts = collections.Counter()
    for k, r in rows.items():
        names = k.split(" + ")
        for n in names:
            if n not in concepts:
                unknown_concepts[n] += 1
        if r["ledger"]:
            first = r["ledger"][0]
            hist_id = first["key"] or k
            src_art = f"{first['artifact']}#L{first['line']}"
        else:
            first = r["nous"][0]
            hist_id = f"nous:{first['run']}:{first['line']}"
            src_art = f"{first['artifact']}#L{first['line']}"
        comps = [n["composite_score"] for n in r["nous"] if n["composite_score"] is not None]
        statuses = [x["status"] for x in r["ledger"]]
        out.append({
            "id": triple_id(names),
            "key": k,
            "concepts": [
                {"name": n,
                 "field": concepts.get(n, {}).get("field"),
                 "mechanism": concepts.get(n, {}).get("mechanism"),
                 "short_description": concepts.get(n, {}).get("short_description")}
                for n in names
            ],
            "provenance": {
                "source": "hephaestus",
                "sourceArtifact": src_art,
                "historicalId": hist_id,
                "upstream_nous": [f"{x['artifact']}#L{x['line']}" for x in r["nous"]],
                "ledger_lines": [x["line"] for x in r["ledger"]],
                "humanreadable": human.get(k),
            },
            "history": {
                "nous_n": len(r["nous"]),
                "nous_composite_max": max(comps) if comps else None,
                "nous_high_potential": any(x["high_potential"] for x in r["nous"]),
                "nous_unproductive_any": any(x["is_unproductive"] for x in r["nous"]),
                "nous_models": sorted({x["model"] for x in r["nous"] if x["model"]}),
                "ledger_n": len(r["ledger"]),
                "forged": "forged" in statuses,
                "ledger_reasons": sorted({(x["reason"] or "").split(" (")[0] for x in r["ledger"]}),
            },
        })
    out.sort(key=lambda x: x["id"])
    ids = [x["id"] for x in out]
    assert len(ids) == len(set(ids)), "triple_id collision"

    os.makedirs(OUT_DIR, exist_ok=True)
    body = "".join(json.dumps(x, sort_keys=True) + "\n" for x in out)
    with open(os.path.join(OUT_DIR, "historical_triplicates.jsonl"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    receipt = {
        "nous_responses": n_nous,
        "ledger_rows": n_ledger,
        "dictionary_concepts": len(concepts),
        "unique_triples_union": len(out),
        "unique_triples_nous": sum(1 for x in out if x["history"]["nous_n"]),
        "unique_triples_ledger": sum(1 for x in out if x["history"]["ledger_n"]),
        "unique_triples_both": sum(1 for x in out if x["history"]["nous_n"] and x["history"]["ledger_n"]),
        "forged_triples": sum(1 for x in out if x["history"]["forged"]),
        "humanreadable_joined": sum(1 for x in out if x["provenance"]["humanreadable"]),
        "concepts_not_in_dictionary": dict(unknown_concepts),
        "sha256_jsonl_lf": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }
    with open(os.path.join(OUT_DIR, "CORPUS_RECEIPT.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return out, receipt


def load(path=None):
    path = path or os.path.join(OUT_DIR, "historical_triplicates.jsonl")
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


if __name__ == "__main__":
    _, rc = build()
    print(json.dumps(rc, indent=2, sort_keys=True))
