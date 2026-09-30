"""Fill the nyx_handoff block of the upstream-body records that shipped with it EMPTY (TECHNE-129).

Harmonia #1064 (2026-09-30, ruling b055767b2): poet-original-2019's nyx_handoff had all five
fields "", which is why Nyx's reader (nyx/atlas/migrate_v1.py grade_from_record) returned
provenance grade UNKNOWN for a record that is pinned to an upstream commit. Measured the same day:
49 of 169 records had an empty block -- every record written since batch 14 (no finalize step was
ever run for batches 14, 15, 16 or the rollout fossils), plus verilog-generic-fifo (batch 04).

This script fills TEN of them: the nine upstream bodies of batches 14-16 and verilog-generic-fifo.
It does NOT touch the 39 asal-rollout-* records: their designed handoff is CAPSULE.json, and a
filled where_it_came_from would make Nyx's string mapping read ORIGINAL_ARTIFACT for frames that
were regenerated inside Prometheus -- a provenance-grade question that is not mine to settle by
writing a string (filed in the backlog row).

Rules:
  - only nyx_handoff is written. observability, classifications, pins and hashes are untouched
    (batch04_finalize.fill also sets observability from run state; nothing here was run, so no
    observability claim is made).
  - NEVER overwrites: a record with any non-empty handoff field is reported KEPT and left alone.
  - no drive letter and no host path: the body is named as <vault>/<id> with the re-fetch command.
  - the five fields are context, never a decomposition (record.py): where the machine is, where it
    came from, how to run it, how we know it runs, what humans used it for.

    python -m techne.fossils.batches.finalize_handoff_20260930 [--write]
"""
from __future__ import annotations

import argparse

from .. import record as R
from .. import vault

IDS = ("asal-sakana-2024", "dcd-facebookresearch-2022", "lenia-chan-2019", "poet-enhanced-2020",
       "poet-original-2019", "terralingua-2026", "terralingua-data-abundant-exp-1",
       "tierra-6.02-ray-1998", "verilog-generic-fifo", "voyager-minedojo-2023")

FIELDS = ("here_is_the_machine", "where_it_came_from", "how_to_run_it", "how_we_know_it_runs",
          "what_humans_used_it_for")


def is_empty(rec: dict) -> bool:
    h = rec.get("nyx_handoff") or {}
    return not any(str(h.get(k, "")).strip() for k in FIELDS)


def handoff_of(rec: dict) -> dict:
    """The five context strings, derived from the record alone (no vault access, no host path)."""
    sid = rec["specimen_id"]
    arts = (rec.get("source_origin") or {}).get("artifacts") or []
    a0 = arts[0] if arts else {}
    ident = rec.get("source_identity") or {}
    if a0.get("kind") == "git":
        origin = a0.get("url", "")
        pin = "commit " + str(a0.get("commit_resolved") or a0.get("commit") or "UNPINNED")
    else:
        origin = ident.get("dataset") or ident.get("archive") or a0.get("url", "")
        pin = "%d file(s), sha256 each in UPSTREAM_HASHES.txt" % len(arts)
    lic = (rec.get("license") or {}).get("spdx", "")
    where = "%s ; %s ; %s ; licence %s" % (origin, rec.get("source_type", ""), pin, lic)
    tree = (rec.get("hashes") or {}).get("tree_sha256", "")
    rc = rec.get("run_classification", "NOT_ATTEMPTED")
    tc = rec.get("test_classification", "NOT_ATTEMPTED")
    if str(rc).startswith("RUNNABLE"):
        good = [x for x in rec.get("receipts", []) if x.get("ok")]
        ref = good[-1]["receipt"] if good else (rec["receipts"][-1]["receipt"] if rec.get("receipts") else "")
        how_run = "recipe.json; python -m techne.fossils.harvest run %s" % sid
        how_know = "%s / %s ; receipt %s" % (rc, tc, ref)
    else:
        host = (rec.get("runtime") or {}).get("host_class", "")
        how_run = "not executed from this record (%s); upstream entry: %s%s" % (
            rc, (rec.get("example") or {}).get("command", "see the record's entry_points"),
            (" ; host class: " + host) if host else "")
        how_know = ("we do not: no run receipt. The body is pinned (tree_sha256 %s, UPSTREAM_HASHES.txt) "
                    "and verifies by hash; that is preservation, not execution" % tree[:16])
    return {
        "here_is_the_machine": "vault body <vault>/%s (host-local; `python -m techne.fossils.harvest rematerialize %s` "
                               "on a host without it) ; tracked techne/fossils/specimens/%s" % (sid, sid, sid),
        "where_it_came_from": where,
        "how_to_run_it": how_run,
        "how_we_know_it_runs": how_know,
        "what_humans_used_it_for": (rec.get("human_capability_summary") or {}).get("built_to", "")
                                   or rec.get("known_human_problem_solved", ""),
    }


def fill(sid: str, write: bool) -> str:
    rec = R.load(sid)
    if not is_empty(rec):
        return "KEPT"
    rec["nyx_handoff"] = handoff_of(rec)
    probs = R.validate(rec)
    if probs:
        return "INVALID: " + "; ".join(probs)
    if write:
        R.save(rec)
        return "FILLED"
    return "WOULD_FILL"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    for sid in IDS:
        if not (vault.specimen_dir(sid) / "record.json").exists():
            print("%-34s NO_RECORD" % sid)
            continue
        print("%-34s %s" % (sid, fill(sid, a.write)))


if __name__ == "__main__":
    main()
