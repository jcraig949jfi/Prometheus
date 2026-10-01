"""Ingest the historical Nous / Hephaestus / Coeus record into Collider data files.

Read-only over the source artifacts: nothing under agents/ is modified. Every output
record keeps a pointer back to the exact artifact (path + line) it came from.

Outputs (collider/public/data/):
  concepts.json               the 95-concept Nous dictionary + Coeus forge effects
  hephaestus-collisions.json  one record per unique historical triple (Nous order kept)
  ingest-manifest.json        input sha256s, counts, script version

Run from the repository root or from collider/:  python collider/scripts/ingest_hephaestus.py
"""
from __future__ import annotations

import glob
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLLIDER = os.path.dirname(HERE)
REPO = os.path.dirname(COLLIDER)
OUT = os.path.join(COLLIDER, "public", "data")
SCRIPT_VERSION = "ingest-hephaestus/1"
LF = chr(10)

SRC_CONCEPTS = "agents/nous/src/concepts.py"
SRC_NOUS = "agents/nous/runs/*/responses.jsonl"
SRC_LEDGER = "agents/hephaestus/ledger.jsonl"
SRC_COEUS = "agents/coeus/graphs/concept_scores.json"
SRC_PRIORITY = "agents/nous/data/priority_triples.json"
FORGE_DIRS = ["forge"] + [f"forge_v{i}" for i in range(2, 10)]

GENERIC = {"algorithm", "algorithm:", "parsing", "structural parsing", "overview", "summary",
           "concept", "idea", "approach", "method", "scoring", "ratings", "novelty"}


def rel(p: str) -> str:
    return os.path.relpath(p, REPO).replace(os.sep, "/")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_concepts():
    spec = importlib.util.spec_from_file_location("nous_concepts", os.path.join(REPO, SRC_CONCEPTS))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.CONCEPTS


def clean(text: str) -> str:
    t = re.sub(r"```.*?```", " ", text, flags=re.S)
    t = re.sub(r"\\\((.*?)\\\)", r"\1", t)
    t = re.sub(r"\\\[(.*?)\\\]", r"\1", t, flags=re.S)
    t = t.replace("**", "").replace("`", "").replace("\\_", "_")
    t = re.sub(r"(?m)^\s*(#+|[-*]|\d+\.)\s+", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


MECH_NOUNS = ("scorer", "solver", "network", "engine", "framework", "system", "machine", "model",
              "architecture", "loop", "algorithm", "filter", "learner", "controller", "optimizer",
              "estimator", "graph", "calculus", "sampler", "inference", "detector", "evaluator", "planner")


def extract_title(text: str) -> str | None:
    """A named mechanism if the analysis gives one, else None (never invented).

    Accept a phrase only if it names a mechanism: it carries an acronym in parentheses
    (e.g. "... Solver (PACS)") or ends in a mechanism noun (Scorer, Network, Engine, ...).
    Section headers such as "Parsing layer" or "Cellular-automaton core" are rejected.
    """
    head = text[:1200]
    cands = []
    for m in re.finditer(r"\*\*(.+?)\*\*|(?<!\*)\*([^*\n]{6,90})\*(?!\*)", head):
        cands.append((m.group(1) or m.group(2) or "").strip())
    for m in re.finditer(r"\b((?:[A-Z][\w‑\-]+\s+){1,7}[A-Z][\w‑\-]+)\s*\(([A-Z]{2,8})\)", head):
        cands.append(f"{m.group(1)} ({m.group(2)})")
    for cand in cands:
        cand = re.sub(r"^Algorithm\s*[:\-–—]\s*", "", cand).strip().strip(":").strip()
        cand = cand.strip("\"'“” ").replace("” ", " ")
        if not (6 <= len(cand) <= 90):
            continue
        low = cand.lower()
        if low in GENERIC or len(re.findall(r"[A-Za-z]+", cand)) < 2:
            continue
        acr = re.search(r"\(([A-Z]{2,8})\)\s*$", cand)
        base = re.sub(r"\s*\([A-Z]{2,8}\)\s*$", "", low).rstrip()
        if acr or base.endswith(MECH_NOUNS):
            if re.match(r"^(\d+\.|step\b|parsing|scoring|ratings?\b|novelty\b)", low):
                continue
            return cand
    return None


def excerpt(text: str, limit: int = 300) -> str:
    t = clean(text)
    t = re.sub(r"^(Algorithm\s*[:\-–—]?\s*)", "", t)
    sents = re.split(r"(?<=[.!?])\s+", t)
    out = ""
    for s in sents:
        if len(out) + len(s) + 1 > limit:
            break
        out = (out + " " + s).strip()
    if not out:
        out = t[:limit].rsplit(" ", 1)[0] + "…"
    return out


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    inputs: dict[str, str] = {}

    concepts = load_concepts()
    inputs[SRC_CONCEPTS] = sha256_file(os.path.join(REPO, SRC_CONCEPTS))
    coeus = json.load(open(os.path.join(REPO, SRC_COEUS), encoding="utf-8"))
    inputs[SRC_COEUS] = sha256_file(os.path.join(REPO, SRC_COEUS))
    influence = coeus.get("concept_influence", {})
    by_name = {}
    out_concepts = []
    for c in concepts:
        rec = {
            "id": slug(c["name"]),
            "name": c["name"],
            "field": c["field"],
            "tags": [c.get("mechanism", "")],
            "sourceMetadata": {
                "mechanism": c.get("mechanism"),
                "shortDescription": c.get("short_description"),
                "coeusForgeEffect": (influence.get(c["name"]) or {}).get("forge_effect"),
                "artifact": SRC_CONCEPTS,
            },
        }
        by_name[c["name"]] = rec
        out_concepts.append(rec)

    # Hephaestus ledger: key is the sorted names joined by " + ".
    ledger: dict[str, list] = {}
    lp = os.path.join(REPO, SRC_LEDGER)
    inputs[SRC_LEDGER] = sha256_file(lp)
    for ln, line in enumerate(open(lp, encoding="utf-8"), start=1):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ledger.setdefault(e["key"], []).append({
            "status": e.get("status"), "reason": e.get("reason"),
            "accuracy": e.get("accuracy"), "calibration": e.get("calibration"),
            "timestamp": e.get("timestamp"), "line": ln,
        })

    # Forge library files: <a>_x_<b>_x_<c>.py (sorted, snake-case).
    tools: dict[str, list] = {}
    for d in FORGE_DIRS:
        for p in glob.glob(os.path.join(REPO, "agents", "hephaestus", d, "*_x_*_x_*.py")):
            tools.setdefault(os.path.basename(p)[:-3], []).append(rel(p))

    priority = json.load(open(os.path.join(REPO, SRC_PRIORITY), encoding="utf-8"))
    inputs[SRC_PRIORITY] = sha256_file(os.path.join(REPO, SRC_PRIORITY))
    priority_keys = {" + ".join(sorted(p["concepts"])): p.get("reason") for p in priority}

    records: dict[str, dict] = {}
    n_resp = 0
    for path in sorted(glob.glob(os.path.join(REPO, SRC_NOUS))):
        rp = rel(path)
        inputs[rp] = sha256_file(path)
        for ln, line in enumerate(open(path, encoding="utf-8"), start=1):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            n_resp += 1
            names = list(r.get("concept_names") or [])
            if len(names) != 3:
                continue
            key = " + ".join(sorted(names))
            score = r.get("score") or {}
            occ = {
                "artifact": rp, "line": ln, "model": r.get("model"), "timestamp": r.get("timestamp"),
                "composite": score.get("composite_score"), "novelty": score.get("novelty"),
                "unproductive": bool(score.get("is_unproductive")), "highPotential": bool(score.get("high_potential")),
                "ratings": score.get("ratings"),
            }
            rec = records.get(key)
            if rec is None:
                text = r.get("response_text") or ""
                h = hashlib.sha256(key.encode()).hexdigest()[:12]
                snake = "_x_".join(sorted(n.lower().replace(" ", "_").replace("-", "_") for n in names))
                hr = "---".join(n.replace(" ", "_") for n in names)
                hr_path = f"agents/hephaestus/humanreadable/{hr}.md"
                rec = {
                    "id": f"historical-{h}",
                    "concepts": [by_name[n]["id"] if n in by_name else slug(n) for n in names],
                    "conceptNames": names,
                    "fields": r.get("concept_fields"),
                    "source": "hephaestus",
                    "sourceArtifact": rp,
                    "sourceLine": ln,
                    "synthesis": {
                        "title": extract_title(text),
                        "excerpt": excerpt(text),
                        "kind": "historical-nous-analysis",
                    },
                    "historicalMetadata": {
                        "occurrences": [],
                        "forge": ledger.get(key, []),
                        "forgeTools": tools.get(snake, []),
                        "humanReadable": hr_path if os.path.exists(os.path.join(REPO, hr_path)) else None,
                        "priorityReason": priority_keys.get(key),
                    },
                }
                records[key] = rec
            rec["historicalMetadata"]["occurrences"].append(occ)

    out = []
    for rec in records.values():
        hm = rec["historicalMetadata"]
        comps = [o["composite"] for o in hm["occurrences"] if isinstance(o["composite"], (int, float))]
        hm["bestComposite"] = max(comps) if comps else None
        hm["forged"] = any(f.get("status") == "forged" for f in hm["forge"])
        out.append(rec)
    out.sort(key=lambda r: r["id"])

    with open(os.path.join(OUT, "concepts.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"source": SRC_CONCEPTS, "concepts": out_concepts}, f, ensure_ascii=False, indent=1)
    # Index (small, loaded at start) + 16 detail shards (loaded on demand) keep the phone
    # payload light. Nothing is dropped: every field lives in exactly one of the two.
    index = []
    shards: dict[str, dict] = {}
    for rec in out:
        hm = rec["historicalMetadata"]
        index.append({
            "id": rec["id"], "concepts": rec["concepts"], "conceptNames": rec["conceptNames"],
            "fields": rec["fields"], "source": "hephaestus",
            "sourceArtifact": rec["sourceArtifact"], "sourceLine": rec["sourceLine"],
            "title": rec["synthesis"]["title"], "bestComposite": hm["bestComposite"],
            "forged": hm["forged"],
            "unproductive": all(o["unproductive"] for o in hm["occurrences"]),
            "shard": rec["id"][len("historical-"):][0],
        })
        shards.setdefault(rec["id"][len("historical-"):][0], {})[rec["id"]] = {
            "synthesis": rec["synthesis"], "historicalMetadata": hm,
        }
    with open(os.path.join(OUT, "hephaestus-collisions.json"), "w", encoding="utf-8", newline=LF) as f:
        json.dump({"schema": "collider.historical.index.v1", "detailPath": "hephaestus/detail-<shard>.json",
                   "records": index}, f, ensure_ascii=False, separators=(",", ":"))
    os.makedirs(os.path.join(OUT, "hephaestus"), exist_ok=True)
    for k, v in shards.items():
        with open(os.path.join(OUT, "hephaestus", f"detail-{k}.json"), "w", encoding="utf-8", newline=LF) as f:
            json.dump({"schema": "collider.historical.detail.v1", "records": v}, f, ensure_ascii=False, separators=(",", ":"))
    manifest = {
        "script": SCRIPT_VERSION,
        "inputs_sha256_lf": inputs,
        "counts": {
            "concepts": len(out_concepts), "fields": len({c["field"] for c in out_concepts}),
            "nous_responses": n_resp, "unique_triples": len(out),
            "ledger_keys": len(ledger), "forged_triples": sum(1 for r in out if r["historicalMetadata"]["forged"]),
            "with_named_title": sum(1 for r in out if r["synthesis"]["title"]),
            "unproductive_triples": sum(1 for r in out if all(o["unproductive"] for o in r["historicalMetadata"]["occurrences"])),
        },
        "not_ingested": {
            "agents/hephaestus/humanreadable": "derived reports; linked per record, not copied",
            "agents/coeus/enrichments": "code-generation prompt blocks, not collisions",
            "forge/candidates": "tier-2 single-field forge (2026-04), not triples",
        },
    }
    with open(os.path.join(OUT, "ingest-manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1)
    print(json.dumps(manifest["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
