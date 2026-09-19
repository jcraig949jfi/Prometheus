"""Source adapter: the ecosystem catalogue (roles/Atlas/catalog/ECOSYSTEMS.jsonl,
read from the working tree of this worktree -- it is Atlas's own committed file).

One line per ecosystem (schema: roles/Atlas/catalog/SCHEMA.md). Loads
atlas.ecosystem, atlas.ecosystem_reference and RELATED_TO edges between
ecosystems. External records are surveyor output: every link keeps the
surveyor's url_status (VERIFIED / SEARCH_RESULT / UNVERIFIED); Atlas does not
upgrade it.
"""
from __future__ import annotations

import json
from pathlib import Path

from atlas import db
from atlas.harvest import common as C

VERSION = "catalog/1"
CATALOG = Path(__file__).resolve().parents[2] / "roles" / "Atlas" / "catalog" / "ECOSYSTEMS.jsonl"


def _ref_uri(r):
    if r.get("url"):
        return r["url"].strip()
    if r.get("doi"):
        return "doi:" + r["doi"].strip()
    if r.get("arxiv"):
        return "arxiv:" + str(r["arxiv"]).strip()
    return None


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _list(v):
    if v is None:
        return []
    return [str(x) for x in (v if isinstance(v, list) else [v])]


def run(args) -> dict:
    lines = [json.loads(x) for x in CATALOG.read_text(encoding="utf-8").splitlines() if x.strip()]
    b = C.Batch("catalog", VERSION, "Atlas")
    eco, refs, edges = [], [], []
    for r in lines:
        w, o, p, a = r.get("world") or {}, r.get("organism") or {}, r.get("pressure") or {}, r.get("architecture") or {}
        links = (r.get("papers") or []) + (r.get("code") or []) + (r.get("other_links") or [])
        ver = sum(1 for x in links if x.get("url_status") == "VERIFIED")
        eco.append({"ecosystem_id": r["id"], "origin": r.get("origin", "external"), "name": r.get("name") or r["id"],
                    "aliases": _list(r.get("aliases")), "cluster": r.get("cluster"), "year_first": _int(r.get("year_first")),
                    "people": _list(r.get("people")), "institution": r.get("institution"),
                    "motivation": _list(r.get("motivation")), "world_kind": w.get("kind"), "world_notes": w.get("notes"),
                    "organism_repr": o.get("representation"), "organism_development": o.get("development"),
                    "organism_notes": o.get("notes"), "pressure_kinds": _list(p.get("kind")), "pressure_notes": p.get("notes"),
                    "search": r.get("search"), "environment_generation": r.get("environment_generation"),
                    "language": a.get("language"), "accelerator": a.get("accelerator"), "scale_note": a.get("scale_note"),
                    "key_claims": _list(r.get("key_claims")), "oee_evidence": r.get("open_endedness_evidence"),
                    "runnable_today": r.get("runnable_today"), "status": r.get("status"),
                    "prometheus_analogue": r.get("prometheus_analogue"), "internal_coverage": r.get("internal_coverage"),
                    "verification": "{}/{} links VERIFIED".format(ver, len(links)), "notes": r.get("notes"), "record": r})
        for kind, group in (("paper", r.get("papers") or []), ("code", r.get("code") or []),
                            ("other", r.get("other_links") or [])):
            for x in group:
                uri = _ref_uri(x)
                if not uri:
                    continue
                refs.append({"ref_uri": uri, "ecosystem_id": r["id"], "kind": x.get("kind", kind),
                             "title": x.get("title"), "year": _int(x.get("year")), "venue": x.get("venue"),
                             "doi": x.get("doi"), "arxiv": str(x["arxiv"]) if x.get("arxiv") else None,
                             "license": x.get("license"), "language": x.get("language"),
                             "last_activity_year": _int(x.get("last_activity_year")), "official": x.get("official"),
                             "url_status": x.get("url_status")})
        for rel in _list(r.get("relatives")):
            if rel != r["id"]:
                b.edge(("ecosystem", r["id"]), ("ecosystem", rel), "RELATED_TO", "SCIENTIFIC", basis="DECLARED",
                       confidence="MEDIUM", detail="catalogue relatives field")
    with db.harvest("catalog", VERSION, source_ref=str(CATALOG.relative_to(CATALOG.parents[3]))) as h:
        with h.conn.cursor() as cur:
            C._normalise_cols(eco)
            h.count("ecosystem", db.upsert(cur, "atlas.ecosystem", eco, ["ecosystem_id"], h.id,
                                           replace=("record", "verification", "key_claims", "aliases", "motivation",
                                                    "pressure_kinds", "people")))
            known = {e["ecosystem_id"] for e in eco}
            refs = [x for x in refs if x["ecosystem_id"] in known]
            C._normalise_cols(refs)
            h.count("reference", db.upsert(cur, "atlas.ecosystem_reference", refs, ["ref_uri", "ecosystem_id"], h.id,
                                           replace=("url_status",)))
        return b.flush(h)
