"""Remediation: re-classify already-compiled genomes against the domain gate.

    python -m techne.cartography.remediate --apply

WHY A SEPARATE PASS. The store is append-only, so contaminated records cannot be deleted and
should not be: the fact that 22.7% of the first corpus was off-domain is itself a finding about
this campaign's retrieval, and erasing it would erase the evidence for a defect the final
report has to disclose. Remediation therefore RE-WRITES each affected genome with its
domain_status set, leaving the original write in the file as history.

WHAT IT FIXES, CONCRETELY. Cycles 000-012 admitted papers that share vocabulary with
computational search but nothing else -- coevolution in paleoanthropology, astronomy,
hydrology, virology and entomology; lexical density in linguistics. One of them, a
paleoanthropology paper on human hands and feet, had already been written into the CONFOUND
ledger as a CONFIRMED confounded causal claim. That is the campaign's priority lane being
populated by a homonym, and it is exactly the kind of number that would have looked like a
finding in a four-hour report.

Confounds whose genome is rejected are re-written with adjudication=REFUTED and a reason, not
deleted -- so the ledger records that the rule fired, on what, and why it was withdrawn.
"""
from __future__ import annotations

import argparse
import json

from . import domain, store


def _blob(g: dict) -> str:
    parts = [g.get("title") or ""]
    for s in g.get("evidence_spans") or []:
        if s.get("scope") == "abstract":
            parts.append((s.get("text") or "")[:800])
    return " ".join(parts)


def backfill_concepts(limit: int = 400) -> dict:
    """Fetch OpenAlex concept labels for genomes compiled before the field existed.

    The domain gate is only as good as its input, and the first 97 genomes were written before
    `concepts` was captured -- so the gate was silently falling back to the SAME lexical
    instrument that caused the contamination. Backfilling is what makes the remediation real
    rather than cosmetic.
    """
    from . import sources
    genomes = store.current("genomes")
    todo = [g for g in genomes.values() if not g.get("concepts") and g.get("source_id")]
    filled = failed = 0
    for g in todo[:limit]:
        try:
            work = sources.openalex_work(g["source_id"])
            norm = sources.openalex_normalize(work)
            g["concepts"] = norm.get("concepts") or []
            g["_concepts_backfilled"] = True
            store.upsert("genomes", g)
            filled += 1
        except Exception as e:                                        # noqa: BLE001
            failed += 1
            continue
    return {"candidates": len(todo), "filled": filled, "failed": failed}


def audit() -> dict:
    """Classify every genome currently in the store. Read-only."""
    rows = []
    for g in store.current("genomes").values():
        status, reason = domain.classify(g.get("concepts"), _blob(g), g.get("venue"))
        rows.append({"research_genome_id": g["research_genome_id"],
                     "title": (g.get("title") or "")[:100],
                     "year": g.get("year"),
                     "had_concepts": bool(g.get("concepts")),
                     "status": status, "reason": reason})
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {"rows": rows, "counts": counts, "total": len(rows)}


def apply() -> dict:
    """Re-write genomes with domain_status, and withdraw confounds resting on rejected ones."""
    genomes = store.current("genomes")
    rejected_ids = set()
    updated = 0
    for g in genomes.values():
        status, reason = domain.classify(g.get("concepts"), _blob(g), g.get("venue"))
        if g.get("domain_status") == status:
            continue
        g["domain_status"] = status
        g["domain_reason"] = reason
        g["_remediated"] = True
        store.upsert("genomes", g)
        updated += 1
        if domain.is_rejected(status):
            rejected_ids.add(g["research_genome_id"])
            store.append("rejected", {"source_id": g.get("source_id"),
                                      "reason": "off_domain_remediation:" + reason,
                                      "title": g.get("title"), "cycle": None})

    withdrawn = []
    for c in store.current("confounds").values():
        if c.get("research_genome_id") in rejected_ids and c.get("adjudication") != "REFUTED":
            c["adjudication"] = "REFUTED"
            c["adjudicated_by"] = (str(c.get("adjudicated_by")) + " -> WITHDRAWN_OFF_DOMAIN")
            c["withdrawal_reason"] = ("the genome this confound rests on failed the domain "
                                      "gate: it is not a computational-search paper. The P4 "
                                      "rule fired correctly on the text; the text was not in "
                                      "scope. Kept as a REFUTED row so the ledger records "
                                      "that this happened.")
            store.upsert("confounds", c)
            withdrawn.append(c["confound_id"])

    return {"genomes_updated": updated, "genomes_rejected": len(rejected_ids),
            "confounds_withdrawn": withdrawn}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the reclassification")
    ap.add_argument("--backfill", action="store_true",
                    help="fetch missing OpenAlex concepts first (required for a real gate)")
    a = ap.parse_args()
    if a.backfill:
        bf = backfill_concepts()
        print("concept backfill: " + json.dumps(bf))
    rep = audit()
    print("genomes audited: " + str(rep["total"]))
    for k, v in sorted(rep["counts"].items(), key=lambda kv: -kv[1]):
        pct = 100.0 * v / max(1, rep["total"])
        print("  {:22s} {:4d}  ({:.1f}%)".format(k, v, pct))
    off = [r for r in rep["rows"] if r["status"] == "OFF_DOMAIN_REJECTED"]
    if off:
        print("\nOFF-DOMAIN (would be rejected):")
        for r in off[:20]:
            # Titles carry non-Latin-1 characters (en-dashes, accents) and this console is
            # cp1252; print ASCII-safe rather than crashing a diagnostic on a hyphen.
            safe = r["title"][:84].encode("ascii", "replace").decode("ascii")
            print("  - " + safe + "  [" + str(r["year"]) + "]")
    if a.apply:
        res = apply()
        print("\nAPPLIED: " + json.dumps(res, indent=2))
    else:
        print("\n(dry run; pass --apply to write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
