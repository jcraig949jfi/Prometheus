"""Recover papers discarded for lacking an abstract, and re-test the holes that assumed they
were absent.

    python -m techne.cartography.backfill_titleonly --apply

THE DEFECT THIS REPAIRS. Cycles 000-020 rejected 45 sources with reason
`no_abstract_available` -- 57% of all rejections, and 33% the size of the kept corpus. Sampling
them showed they were not marginal: Fogel's "Evolutionary computation: toward a new philosophy
of machine intelligence", Eiben & Smith's "From evolutionary computation to the evolution of
things", "Lexicase Selection for Program Synthesis: A Diversity Analysis", "Relaxations of
Lexicase Parent Selection", Coello Coello's multi-objective text, Jin's fitness-approximation
survey.

WHY IT MATTERED MORE THAN IT LOOKED. Abstract availability in OpenAlex correlates with
publisher: books, edited volumes and older proceedings frequently carry none. So the filter was
not removing low-quality records, it was removing a VENUE TYPE -- and with it, disproportionately,
the foundational and survey literature. Every coverage hole computed over that archive was
therefore biased toward looking emptier than the field is, which attacks the campaign's central
product at its root.

WHAT RECOVERY DOES AND DOES NOT CHANGE. Recovered records join the QD archive so the cells they
occupy read as occupied. They carry `abstract_available=False` and NO claim predicate runs on
them -- a title cannot support CLAIM_PRESENT, let alone MECHANISM_ISOLATED. So this fixes
coverage without inflating the claim ledger by a single row.

Holes are then re-tested: any COVERAGE_HOLE_CANDIDATE whose cell is occupied by a recovered
paper is killed, with the killing paper recorded. Killing holes is the desirable direction --
these were never holes, and the archive had simply lost their occupants.
"""
from __future__ import annotations

import argparse
import hashlib
import json

from . import cycle as cyc
from . import domain, sources, store, taxonomy


def discarded_ids() -> list:
    """Sources rejected specifically for missing an abstract, still absent from the archive."""
    have = {g.get("source_id") for g in store.current("genomes").values()}
    out, seen = [], set()
    for r in store.read("rejected"):
        sid = r.get("source_id")
        if not sid or sid in have or sid in seen:
            continue
        if str(r.get("reason", "")).startswith("no_abstract_available"):
            seen.add(sid)
            out.append({"source_id": sid, "title": r.get("title")})
    return out


def recover(limit: int = 200) -> dict:
    """Re-fetch each discarded source and compile it as a title-only genome."""
    todo = discarded_ids()
    recovered = rejected = failed = 0
    titles = []
    for rec in todo[:limit]:
        try:
            work = sources.openalex_work(rec["source_id"])
            norm = sources.openalex_normalize(work)
            norm["_index"] = "openalex"
            # The domain gate still applies -- recovering a record is not a reason to lower
            # the bar on whether it belongs in a computational-search corpus.
            dstat, _dr = domain.classify(
                norm.get("concepts"),
                (norm.get("title") or "") + " " + (norm.get("abstract") or "")[:600],
                norm.get("venue"))
            if domain.is_rejected(dstat):
                rejected += 1
                continue
            genome, claims = cyc.compile_genome(norm, cycle=-1, request_url=work.get("_request_url"))
            genome.provenance["recovered_from"] = "no_abstract_available rejection"
            store.upsert("genomes", genome)
            # claims is empty for title-only records by construction; assert the invariant
            # rather than trusting it, because a claim built on a title would be exactly the
            # inflation this recovery is supposed to avoid.
            if not norm.get("abstract") and claims:
                raise AssertionError("title-only record produced claims: " + genome.research_genome_id)
            store.append_many("claims", claims)
            recovered += 1
            titles.append(norm.get("title"))
        except Exception as e:                                        # noqa: BLE001
            failed += 1
            continue
    return {"candidates": len(todo), "recovered": recovered,
            "rejected_by_domain_gate": rejected, "failed": failed,
            "sample": [t for t in titles[:8] if t]}


def retest_holes() -> dict:
    """Kill any candidate hole whose cell is now occupied."""
    occupied = {}
    for g in store.current("genomes").values():
        occupied.setdefault(taxonomy.cell_of(g), []).append(g)

    killed = []
    for h in store.current("holes").values():
        if h.get("status") != "COVERAGE_HOLE_CANDIDATE":
            continue
        cell = tuple(h["coordinates"]["cell"])
        occ = occupied.get(cell)
        if occ:
            h["status"] = "KILLED_BY_RETRIEVAL"
            h["killed_by"] = ("archive re-test after title-only recovery: cell is occupied by "
                              + str(len(occ)) + " genome(s) that had been discarded for "
                              "lacking an abstract")
            h["nearest_prior_work"] = [g["research_genome_id"] for g in occ[:5]]
            h["confidence_in_absence"] = "none_cell_is_occupied"
            store.upsert("holes", h)
            killed.append({"cell": list(cell),
                           "by": (occ[0].get("title") or "")[:70]})
    return {"holes_killed": len(killed), "detail": killed[:10]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=200)
    a = ap.parse_args()

    todo = discarded_ids()
    print("sources discarded for missing abstract, still absent: " + str(len(todo)))
    for r in todo[:8]:
        print("  - " + str(r.get("title") or "?")[:72].encode("ascii", "replace").decode())
    if not a.apply:
        print("\n(dry run; pass --apply)")
        return 0

    res = recover(a.limit)
    print("\nRECOVERY: " + json.dumps({k: v for k, v in res.items() if k != "sample"}))
    for t in res["sample"]:
        print("  recovered: " + str(t)[:72].encode("ascii", "replace").decode())
    rt = retest_holes()
    print("\nHOLE RE-TEST: " + str(rt["holes_killed"]) + " candidate hole(s) killed "
          "-- they were never holes; the archive had lost their occupants")
    for d in rt["detail"]:
        print("  " + str(d["cell"]))
        print("      occupied by: " + str(d["by"]).encode("ascii", "replace").decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
