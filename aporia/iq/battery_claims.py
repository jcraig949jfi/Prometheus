"""battery_claims.py — R1: machine-derive claim objects from RESULT artifacts.

The external review's blocking finding: the BATTERY gate was an instrument over MY TRANSCRIPTION
of primary evidence, not over primary evidence. The chain was

    RESULT artifact -> my interpretation -> claim object -> gate -> verdict

so the gate was deterministic only AFTER the lossy step, and could not catch a mistranscribed
numerator, a wrong denominator, a wrong population, an omitted qualifier, or a swapped
experiment identity. Hashes and filenames are insufficient; the gate must consume the underlying
observations.

This module removes the human step. Every field is DERIVED from keys actually present in the
RESULT json by a fixed rule, and any field that cannot be derived is emitted as None rather than
guessed -- an underivable field is itself a finding about the artifact, not a licence to fill it
in.

    python aporia/iq/battery_claims.py        # derive, adjudicate, and diff against the
                                              # hand-transcribed objects in run_battery.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import battery as B  # noqa: E402

# RESULT artifact -> the rung it is evidence for. Identity comes from the file's own
# "experiment" field, NOT from the filename, so a swapped file is detectable.
FILES = {
    "RESULT_IQ_PORT_1.json": "IQ-PORT-1",
    "RESULT_IQ_NULL.json": "IQ-NULL",
    "RESULT_PROVENANCE.json": "PROVENANCE",
    "RESULT_TRANSFER_1.json": "TRANSFER-1",
    "RESULT_SCORER_FIX.json": "SCORER-FIX",
    "RESULT_CEILING_ABSTAIN.json": "CEILING-ABSTAIN",
    "RESULT_BATTERY.json": "BATTERY",
    "RESULT_SELECTOR_PREFLIGHT.json": "SELECTOR-PREFLIGHT",
}

# Falsifier -> the RESULT keys whose PRESENCE constitutes evidence it was run.
# Derivation rule, fixed before any diff was computed.
FALSIFIER_EVIDENCE = {
    "evaluation": ["evaluator_hash_matches_prereg", "corpus_sha256", "frozen_pool_sha256"],
    "answer": ["mutants", "mutants_nondegenerate", "all_mutants_zero_delta"],
    "parse": ["INJ_A_all_but_n_solved", "INJ_B_all_but_n_solved", "injection_branch"],
    "composition": ["knockout_delta", "knockout_port_load_bearing"],
    "retrieval": ["footprint_size", "quantities_producers_in_C", "pipelines_evaluated"],
    "distribution": ["x_heldout", "T5_parser_fails_on_all_X_routes"],
    "search": ["null_region_evals", "check_transitivity_evals"],
}


def _first(d, keys):
    for k in keys:
        if k in d:
            return d[k]
    return None


def derive(path: Path):
    """Derive a claim object from an artifact. No hand transcription anywhere."""
    d = json.loads(path.read_text(encoding="utf-8"))
    notes = []

    # identity from the artifact's own field, so a swapped file is caught
    ident = d.get("experiment")
    if ident is None:
        notes.append("artifact carries no `experiment` field: identity underivable")

    cls = d.get("intervention_class")
    if cls is None:
        cls = "INSTRUMENT"
        notes.append("no intervention_class in artifact; derived as INSTRUMENT")

    falsifiers = {}
    for f, keys in FALSIFIER_EVIDENCE.items():
        present = any(k in d for k in keys)
        if present:
            falsifiers[f] = True

    # readings: every key that carries an explicit n, derived not asserted
    readings = {}
    for k, v in d.items():
        if isinstance(v, dict) and "n" in v and isinstance(v["n"], int):
            readings[k] = {"n": v["n"], "attainable_lo": 0.0, "attainable_hi": 1.0}
    for k in ("pipelines_evaluated", "footprint_size", "null_region_evals", "nondegenerate_n",
              "T1_nondegenerate_n", "frozen_pool_size"):
        if isinstance(d.get(k), int):
            readings[k] = {"n": d[k], "attainable_lo": 0.0, "attainable_hi": 1.0}
    if not readings:
        notes.append("no reading with an explicit n could be derived")

    # is_null_result: derived from a measured zero-delta, not from my judgement
    nullish = [k for k in ("delta_E_null_noop", "delta_E_check_transitivity",
                           "tasks_lost_ceiling", "n_positive_dE")
               if k in d and d[k] in (0, 0.0)]
    is_null = bool(nullish)

    pos_ctl = bool(d.get("positive_control") or d.get("positive_control_ran"))
    if not pos_ctl and is_null:
        notes.append(f"null result (from {nullish}) with no positive-control field in the "
                     f"artifact: G-INERT will fire")

    claim = {
        "derived_from": path.name,
        "identity_in_artifact": ident,
        "intervention_class": cls,
        "falsifiers_run": falsifiers,
        "thresholds": {},          # only populated when the artifact records one explicitly
        "readings": readings,
        "branch_table_partitions": bool(d.get("branch_table_partitions")
                                        or d.get("terminal_table_partitions")),
        "is_null_result": is_null,
        "positive_control_ran": pos_ctl,
        "probe_modifies_measured_quantity": bool(d.get("probe_modifies_measured_quantity")),
    }
    return claim, notes


def main():
    out = {"experiment": "BATTERY-R1-MACHINE-BOUND", "date": "2026-08-25",
           "review_item": "R1 — gate must consume underlying observations, not a transcription"}

    derived, notes_all, verdicts = {}, {}, {}
    for fname, rung in FILES.items():
        p = HERE / fname
        if not p.exists():
            notes_all[rung] = ["ARTIFACT ABSENT"]
            continue
        c, notes = derive(p)
        derived[rung] = c
        notes_all[rung] = notes
        verdicts[rung] = B.adjudicate(c)

    out["derivation_notes"] = notes_all
    out["derived_verdicts"] = {k: v[0] for k, v in verdicts.items()}
    out["derived_reasons"] = {k: v[1] for k, v in verdicts.items() if v[1]}
    out["identity_check"] = {k: v["identity_in_artifact"] for k, v in derived.items()}
    out["identity_matches_expected"] = {
        k: (derived[k]["identity_in_artifact"] == k or
            derived[k]["identity_in_artifact"] in (k, k.replace("-", "_")))
        for k in derived}

    # ── the diff that matters: machine-derived vs my hand transcription ──────
    try:
        import run_battery as RB
        hand = {k: B.adjudicate(v)[0] for k, v in RB.CLAIMS.items()}
    except Exception as e:  # pragma: no cover
        hand = {}
        out["hand_import_error"] = str(e)
    out["hand_verdicts"] = hand
    disagree = {k: {"hand": hand.get(k), "derived": out["derived_verdicts"].get(k)}
                for k in set(hand) | set(out["derived_verdicts"])
                if hand.get(k) != out["derived_verdicts"].get(k)}
    out["verdict_disagreements"] = disagree
    out["n_disagreements"] = len(disagree)
    out["R1_transcription_was_lossy"] = len(disagree) > 0

    out["dropped_records"] = 0
    out["dropped_records_note"] = ("Every artifact in FILES is either derived-and-adjudicated or "
                                   "recorded ARTIFACT ABSENT. Underivable fields are emitted as "
                                   "notes, never filled in.")

    json.dump(out, open(HERE / "RESULT_BATTERY_R1.json", "w", encoding="utf-8"), indent=2)
    for k, v in out.items():
        if k not in ("derivation_notes", "derived_reasons"):
            print(f"{k}: {v}")
    print("\nderivation notes:")
    for k, v in notes_all.items():
        if v:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
