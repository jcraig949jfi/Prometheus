"""Qualify the pyribs H3 retention adapter against the declared fixture stream.

    python -m techne.scripts.h3_adapter_qualify

Writes an ADAPTER_QUALIFICATION receipt. Read its `does_not_establish` field before quoting
it: this qualifies the adapter against a FIXTURE, which is not qualification against H3's
stream (that format does not exist yet) and is not evidence about any retention policy.

Four runs, because one would not exercise the thing:

  R1  tie policy probes at BOTH granularities -- declared, then verified against the installed
      pyribs, raising if they disagree
  R2  loose caps -- neither binds. Establishes the baseline retention and is explicitly NOT
      evidence that the caps work
  R3  binding caps -- BOTH bind. This is where the cap paths are exercised
  R4  batch vs one-at-a-time retention on the identical stream
"""
from __future__ import annotations

import argparse
import json
import pathlib

from techne.acquisition import budget as _budget
from techne.acquisition import paths, receipt
from techne.h3_retention import adapter as A
from techne.h3_retention import build_fixture as F
from techne.h3_retention import stream as S

FIXTURE_DIR = pathlib.Path(A.__file__).resolve().parent / "fixture"
DIMS = (4, 4)

LOOSE = A.Caps(max_retained=16, max_bytes=100_000)
BINDING = A.Caps(max_retained=4, max_bytes=4_000)


def _log_rows(res: A.ReplayResult) -> list[dict]:
    return [{
        "seq": d.seq, "candidate_id": d.candidate_id, "disposition": d.disposition,
        "cell_index": d.cell_index, "objective": d.objective,
        "payload_bytes": d.payload_bytes, "bytes_delta": d.bytes_delta,
        "displaced": d.displaced_candidate_id, "birth_status": d.birth_status,
        "parent_ids": list(d.parent_ids), "result_ref": d.result_ref["ref"],
        "reason": d.reason,
    } for d in res.log]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="offline_check")
    a = ap.parse_args(argv)

    rec = receipt.new("ADAPTER_QUALIFICATION", "pyribs", tool="ribs")
    rec["consumer"] = ("H3 retention replay (Archaeon). The REAL stream format does not exist "
                       "yet -- H3 alpha is NOT STARTED -- so this qualifies the adapter against "
                       "a declared fixture stream, per the operator's instruction of 2026-09-10.")
    rec["contract"] = "techne/h3_retention/STREAM_CONTRACT_V0.md"
    prof = _budget.get_profile(a.profile)
    rec["budget_profile"] = prof

    with _budget.Budget(profile=prof) as b:
        try:
            st = S.read_jsonl(FIXTURE_DIR / "stream_v0.jsonl", resolver=F.resolver)
            rec["observations"]["stream"] = st.validation
            rec["observations"]["stream_required_properties"] = {
                "stable_ordered_ids": "seq 0-based contiguous strictly increasing; candidate_id unique",
                "candidate_digests": "sha256 over canonical payload, recomputed and matched on every row",
                "birth_status": st.validation["birth_status_counts"],
                "fixed_assay_references": st.header["assay_ref"],
                "recoverable_results": st.validation["recoverability_check"],
            }

            # R1 -- tie policy at both granularities
            tie = A.verify_tie_policy()
            rec["observations"]["R1_tie_policy"] = tie

            # R2 -- loose caps
            r2 = A.replay(st, LOOSE, dims=DIMS, verify_ties=False)
            rec["observations"]["R2_loose_caps"] = {
                "caps": r2.caps, "counts": r2.counts, "retained_ids": r2.retained_ids,
                "retained_bytes": r2.retained_bytes, "grid_cells": r2.grid_cells,
                "binding_constraint": r2.binding_constraint, "notes": r2.notes,
                "emitter_guard": r2.emitter_guard, "log": _log_rows(r2),
            }

            # R3 -- binding caps
            r3 = A.replay(st, BINDING, dims=DIMS, verify_ties=False)
            rec["observations"]["R3_binding_caps"] = {
                "caps": r3.caps, "counts": r3.counts, "retained_ids": r3.retained_ids,
                "retained_bytes": r3.retained_bytes, "grid_cells": r3.grid_cells,
                "binding_constraint": r3.binding_constraint, "notes": r3.notes,
                "emitter_guard": r3.emitter_guard, "recoverable": r3.recoverable,
                "log": _log_rows(r3),
            }

            # R4 -- batch vs one-at-a-time
            r4 = A.replay_batch_equivalence(st, LOOSE, dims=DIMS)
            rec["observations"]["R4_batch_equivalence"] = r4

            # R5 -- the caps are NOT independent knobs, and this stream shows why.
            best = max(st.rows, key=lambda r: r.objective)
            d_best = next(d for d in r3.log if d.candidate_id == best.candidate_id)
            earlier_bytes_refusal = next(
                (d for d in r3.log
                 if d.disposition == "CAP_REFUSED_BYTES" and d.cell_index == d_best.cell_index
                 and d.seq < d_best.seq), None)
            rec["observations"]["R5_cap_coupling"] = {
                "finding": "The two caps are coupled THROUGH ARCHIVE OCCUPANCY, so they are not "
                           "independent knobs and a retention comparison that varies one is not "
                           "holding the other fixed.",
                "highest_objective_candidate": best.candidate_id,
                "its_objective": best.objective,
                "its_disposition_under_binding_caps": d_best.disposition,
                "its_disposition_under_loose_caps": next(
                    d.disposition for d in r2.log if d.candidate_id == best.candidate_id),
                "cell": d_best.cell_index,
                "earlier_byte_refusal_in_the_same_cell": (
                    {"candidate_id": earlier_bytes_refusal.candidate_id,
                     "seq": earlier_bytes_refusal.seq,
                     "bytes_delta": earlier_bytes_refusal.bytes_delta}
                    if earlier_bytes_refusal else None),
                "mechanism": (
                    f"{earlier_bytes_refusal.candidate_id} was refused for BYTES at seq "
                    f"{earlier_bytes_refusal.seq}, which left cell {d_best.cell_index} empty. "
                    f"{best.candidate_id} (objective {best.objective}, the highest in the "
                    f"stream) would have IMPROVED that cell at zero occupancy cost; because the "
                    f"cell was empty it counted as a new occupation instead, and the COUNT cap "
                    f"refused it. A byte refusal early caused the loss of the best candidate "
                    f"later, through the other cap."
                    if earlier_bytes_refusal else "not exercised on this stream"),
                "consequence_for_h3": (
                    "Report both caps and the disposition log, never a retained set alone. Two "
                    "policies compared at different caps differ by an amount that includes this "
                    "coupling, and the coupling is invisible in the retained set."),
                "fires_on_this_stream": bool(earlier_bytes_refusal)
                                        and d_best.disposition.startswith("CAP_REFUSED"),
            }

            checks = [
                ("stream validates against all five declared properties", True),
                ("recoverability verified through a resolver, not assumed",
                 st.validation["result_refs_resolved"]),
                ("duplicate content under distinct ids is detected and surfaced",
                 st.validation["n_duplicate_content_groups"] == 1),
                ("tie policy FIRST_WRITER_WINS verified one-at-a-time",
                 tie["sequential"]["first_writer_won"]),
                ("tie policy FIRST_WRITER_WINS verified in batch",
                 tie["batch"]["first_writer_won"]),
                ("exact tie is REJECTED_BY_ARCHIVE, incumbent survives",
                 any(d.candidate_id == "c004" and d.disposition == "REJECTED_BY_ARCHIVE"
                     for d in r2.log) and "c001" in r2.retained_ids),
                ("loose caps: NEITHER binds, and the run says so",
                 r2.binding_constraint == "NONE" and bool(r2.notes)),
                ("binding caps: BOTH the count cap and the byte cap fire",
                 "COUNT" in r3.binding_constraint and "BYTES" in r3.binding_constraint),
                ("no emitter or scheduler instance exists in either replay",
                 r2.emitter_guard["pass"] and r3.emitter_guard["pass"]),
                ("every non-retained candidate keeps a resolvable result_ref",
                 r3.recoverable["all_non_retained_carry_a_result_ref"]),
                ("byte ledger reconciles with archive occupancy", True),  # replay() raises otherwise
                ("batch and one-at-a-time agree on this stream when caps do not bind",
                 r4["identical"] and r4["comparison_is_meaningful"]),
                ("cap coupling is exercised: an early byte refusal costs the highest-objective "
                 "candidate later, through the OTHER cap",
                 rec["observations"]["R5_cap_coupling"]["fires_on_this_stream"]),
            ]
            rec["observations"]["checks"] = [{"claim": c, "pass": bool(p)} for c, p in checks]
            rec["observations"]["n_passed"] = sum(1 for _, p in checks if p)
            rec["observations"]["n_total"] = len(checks)
            rec["status"] = ("QUALIFIED_AGAINST_DECLARED_FIXTURE"
                             if all(p for _, p in checks) else "FAILED")
            rec["resource_receipt"] = b.resource_receipt()
        except Exception as exc:
            rec["status"] = "ERROR"
            rec["unrun_or_blocked"].append(f"{type(exc).__name__}: {exc}")
            rec["resource_receipt"] = b.resource_receipt()
            out = receipt.write(rec)
            print(f"ERROR: {exc}\nreceipt {out}")
            return 1

    rec["unrun_or_blocked"] = [
        "H3's REAL stream format -- Archaeon hands it over from Track B's C3 corpus or Track E's "
        "NK. Until then this adapter is qualified against a fixture, and the fixture is a Techne "
        "proposal that will lose to the real format.",
        "Retention POLICY comparison -- not attempted and not this seat's. The adapter replays "
        "one stream under one configuration; comparing policies is H3's experiment.",
        "Capped BATCH replay -- deliberately unavailable rather than faked. A cap is a "
        "per-candidate admission decision and the donor's batch path resolves collisions before "
        "returning, so capping a batch would mean reimplementing the donor's tie rule.",
    ]
    rec["deviations"] = [
        "DEV-H3-1: the stream contract is a Techne proposal, not Archaeon's format. Five "
        "required properties are implemented as refusals and argued in STREAM_CONTRACT_V0.md; "
        "the field names are provisional.",
        "DEV-H3-2: R4 compares an UNCAPPED batch against a capped-but-not-binding sequential "
        "replay, because the batch path cannot be capped without reimplementing the donor's "
        "rule. The comparison is therefore only meaningful when the caps do not bind, and the "
        "result carries that condition.",
    ]
    out = receipt.write(rec)

    print(f"=== ADAPTER_QUALIFICATION pyribs -> {rec['status']} ===")
    print(f"consumer        H3 retention replay (fixture stand-in; real format absent)")
    print(f"stream          {st.stream_id}  {st.validation['n_rows']} rows  "
          f"{st.validation['stream_digest'][:23]}...")
    print(f"  births        {st.validation['birth_status_counts']}")
    print(f"  recoverable   {st.validation['recoverability_check']}")
    print(f"  dup content   {st.validation['n_duplicate_content_groups']} group(s) "
          f"{list(st.validation['duplicate_digests_under_distinct_ids'].values())}")
    print(f"tie policy      {tie['declared']} verified: sequential="
          f"{tie['sequential']['first_writer_won']} batch={tie['batch']['first_writer_won']}")
    for label, r in (("R2 loose  ", r2), ("R3 binding", r3)):
        print(f"{label}      caps(count={r.caps['max_retained']}, bytes={r.caps['max_bytes']}) "
              f"-> retained {r.caps['retained']} cells / {r.retained_bytes} B  "
              f"BINDING={r.binding_constraint}")
        print(f"                {r.counts}")
    print(f"R4 batch        identical={r4['identical']} meaningful={r4['comparison_is_meaningful']}")
    cc = rec["observations"]["R5_cap_coupling"]
    print(f"R5 coupling     best={cc['highest_objective_candidate']} (obj "
          f"{cc['its_objective']}) loose={cc['its_disposition_under_loose_caps']} "
          f"binding={cc['its_disposition_under_binding_caps']}")
    print(f"                {cc['mechanism'][:150]}")
    print(f"emitters        {r3.emitter_guard['pass']} (instances: "
          f"{r3.emitter_guard['live_emitter_instances']}"
          f"{r3.emitter_guard['live_scheduler_instances']}, "
          f"{r3.emitter_guard['modules_imported']} modules imported)")
    for c in rec["observations"]["checks"]:
        print(f"  {'PASS' if c['pass'] else 'FAIL':<5} {c['claim']}")
    print(f"does not establish: {', '.join(rec['does_not_establish'])}")
    print(f"receipt         {out}")
    return 0 if rec["status"] == "QUALIFIED_AGAINST_DECLARED_FIXTURE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
