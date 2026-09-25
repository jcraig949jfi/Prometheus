"""Batch E amendment (before any run): P-E07 was an ANALYSIS of P-E01's output plus P-D01's rows, not a
run of its own, and it consumed P-E01's parent slot in the first freeze attempt (the freeze was not
used; recorded as CW01-D080). It is superseded by P-E01, which absorbs the cross as an observable.
P-E09 is added: T-X13's recorded escape condition (an organism that can represent protection) is
posable in the Proteus substrate, where duplication exists as an operator."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

OUT = HERE / "PERTURBATIONS.jsonl"
LINES = [
    {"id": "P-E07", "amend": True, "superseded_by": "P-E01",
     "reason": "an analysis of P-E01 + P-D01 rows, not a run; absorbed into P-E01 as the 'tick sensitivity x damage loss x state-use' observable (D080)"},
    {"id": "P-E01", "amend": True,
     "delta_addendum": "OBSERVABLE (from P-E07): per-program tick sensitivity (self-displacement under one NOISE tick) against per-program damage loss from P-D01 rows.json and state-use descriptors (persist policy, tape writes, persistent words, tick budget); rank correlation with a permutation null, partial on length and set"},
    dict(id="P-E09", parent="T-X13", family="robustness_cross", axis="weather x representable_protection", type="serendipity-cross", serendipity=True, co_parents=["T-ARCH4/M1", "T-E07"],
         delta="WEATHER IN A SUBSTRATE THAT CAN REPRESENT PROTECTION: the P-E03 Nestor evolver (W2_K2 reward, N=96 from the walkers, 60 generations, tournament 3) with a third arm in which every birth suffers blind deletion of 2 instructions with probability .5 BEFORE evaluation (e07's damage family; a sham arm draws and applies nothing), 2 seeds; the P-D01 damage assay on the top-32 of the weather, sham and static arms and on their ancestors, paired by ancestor; state-use descriptors (persist policy share, tape writes, persistent words) and length by arm and generation. Does evolution under damage build robustness (duplication / redundancy: length and persistent words rise, loss falls) or select state AVOIDANCE as in e01 (persistent words fall, tape writes fall, loss unchanged or higher)?",
         unchanged="grammar, worlds, damage kinds, classification constants", attacks="T-X13's reversal (weather selects state avoidance) was found in a one-parameter organism; T-E07's stasis escape is an organism that can represent protection - the Proteus grammar has duplication and configurable persistence",
         nonredundant="T-X13 and T-ARCH4/M1 never met; the escape condition of a stasis is tested in another substrate rather than by rebuilding e01", cost_minutes=8,
         continuation=["damage probability dose", "damage kind (operand vs delete) during evolution", "persist policy frozen per arm"],
         scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                     regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2,
                     null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=2)),
]


def main():
    existing = set()
    for line in OUT.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            if d.get("amend") and d.get("superseded_by") and d["id"] == "P-E07":
                print("already amended"); return
            existing.add(d["id"])
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with OUT.open("a", encoding="utf-8") as fh:
        for d in LINES:
            if not d.get("amend") and d["id"] in existing:
                continue
            d = dict(d)
            d["recorded"] = ts
            if not d.get("amend"):
                d["batch"] = "E"
            fh.write(json.dumps(d, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(OUT)
    print("amended P-E07 -> P-E01; added P-E09")


if __name__ == "__main__":
    main()
