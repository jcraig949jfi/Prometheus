"""Cycle-3 reconciler notes, part A (P-E01, P-E02, P-E05, P-D14, P-D06, P-A05, P-E08) + defect D081.
Run after every driver has exited."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402

LEDGER = HERE.parent / "DEFECTS.jsonl"
D081 = {"id": "CW01-D081", "experiment_id": "cw01-loop3", "phase": "EXECUTE", "severity": "low", "category": "instrument", "status": "OPEN",
        "defect_class": "C - uninformative sub-assay",
        "title": "P-E01 walker trace defined 'onset' as the first step whose self-displacement crosses .10 from below; base sensitivity was already 1.0 for every w0_solver parent, so no onset and no revert test could occur (0/60)",
        "evidence": "walkers.base_sens_mean 1.0, final_sens_mean 1.0, n_onset 0. The program-level map and the cross observable are unaffected.",
        "proposed_fix": "A descendant should trace LOSS of sensitivity along the walk (or use P-D02's walker-vs-program ruler) - not re-run here.", "found_by": "P-E01 result"}


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    if D081["id"] not in existing:
        rec = {"id": D081["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
        rec.update({k: v for k, v in D081.items() if k != "id"})
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-X12", "P-E01", "RECONCILER: the switch is an INPUT-LESS TICK, not content and not delay: mean self-displacement under one EMPTY tick .40 (parents) / .70 (C4-08 tops) is as large as under a NOISE tick (.48 / .75), 2-4 ticks add nothing (saturation at one tick), NOISE words INSIDE the PUT tick move little (.13 / 0), and a REPEATED-PUT tick moves almost nothing (.10 / .00). Position matters less than presence (a tick before the first PUT .57 / .25). Forcing persist='none' makes every program tick-insensitive (0.0) while changing its behaviour (.82-.94): the coordinate is CARRIED STATE advanced by a tick that delivers no input. 94-100 percent of programs are not immune; the P-D02 'delay switch' sat on a substrate property. Cross: tick sensitivity correlates NEGATIVELY with damage loss (rho -.43, partial on length and set -.29, both clear the permutation band) and positively with persistent state words (+.39); loss correlates with persistent words (-.51) and length (-.76). Walker sub-assay uninformative (D081).", True,
                      detail={"note": "see RESULT.json shares_by_set, signflips, cross"}, state="ACTIVE", state_reason="a substrate-level temporal-semantics coordinate (input-less tick x carried state) with a lineage phenotype; continuation: idle-tick dose during evolution, persist policy as a factor, tick budget")
    L.append_evidence("T-ARCH4/M1", "P-E01", "cross from T-X12: programs that carry more state are both more tick-sensitive and more damage-robust; length is the strongest single correlate of damage loss (rho -.76); the two anomalies share a coordinate (carried state / length), see P-E05.", True)
    L.append_evidence("T-X12", "P-E02", "RECONCILER: per-tag timing is NOT a coordinate; the temporal response is a LINEAGE PHENOTYPE. W0-evolved parents: an idle tick before an ask displaces that ask only (1.0 own, .004 other; between the PUTs 0.0) - ask-time bound, no cross-tag effect. C4-08 W2-evolved tops: an idle tick BETWEEN the PUTs displaces both answers (.748 = the one-stream value) while an idle tick before either ask displaces NOTHING (0.0) - input-schedule bound. Shelf parents intermediate (.1-.3, both tags). Upstream harness check passed (0.0). Two temporal response classes now exist: ask-time-bound and input-schedule-bound.", True,
                      state="ACTIVE", state_reason="continuation: idle tick between the PUTs of the same tag (D=2), K=3, evolve under idle ticks and read which class selection builds")
    L.append_evidence("T-ARCH4/S1", "P-E05", "RECONCILER (stasis escape): depth 64 is connected in every cell (94/94 walks reach 64). Exaptation rises only modestly with depth (orig|frozen .032 -> .053; no_growth|delheavy .074 -> .106; bands overlap). The material result is A x C: under the ORIGINAL rule length grows (+5.7 at 64) and damage loss FALLS (.60 -> .50, below p05); under NO_GROWTH length shrinks (-8.6 / -12.2) and loss RISES (.67 -> .76 / .72 -> .84, above p95); at depth 64 no_growth products lose +.27 more than orig products. The acceptance filter's length accumulation is the damage-robustness mechanism.", True,
                      state="ACTIVE", state_reason="the recorded escape held: depth is informative under a different rule; S1 leaves stasis")
    L.append_evidence("T-ARCH4/M1", "P-E05", "RECONCILER: deformations A and C are COUPLED through length: neutral length accumulation (junk under trap-NOP) lowers loss at fixed k. Open: dilution (fixed k over more instructions) vs redundancy; a fraction-matched damage dose (k proportional to n) separates them. Promoted to node T-X15 (length as the shared coordinate of damage robustness, tick sensitivity and growth).", True)
    L.append_evidence("T-ARCH4/W1", "P-D14", "RECONCILER: the neutral archive holds almost no exaptation under either selection rule (train-selected 0/47, held-out-selected 1/47; 41/47 choose the same variant); e08's train-vs-held-out surface does not transfer to C4's depth-16 archive because there is nothing to select among. Not material; consistent with P-C08.", False)
    L.append_evidence("T-X04", "P-D06", "RECONCILER: no separatrix at phi .5: final TREE frequency is NOT monotone in the founding frequency (3-5 sign changes per series; finals mostly 0 or 1); bistable-by-rule in 1/4. Founder control at phi .5 is not a threshold in f0 - the outcome is decided by early dynamics, not by the seed. Observatory note: multi-stability without a separatrix.", False)
    L.append_evidence("T-X03", "P-A05", "RECONCILER: neither pre-run predictor clears its permutation band on 48 fresh worlds (coverage overlap .40 accuracy vs p95 .60; conjunctive concentration .60 = p95, not above; base rate .46). Composability is not predicted by these two capability-pool statistics; the split rule was fixed on 4 worlds. Not material.", False)
    L.append_evidence("T-E03", "P-E08", "RECONCILER: INSTRUMENT_UNATTAINABLE by the preregistered check - the zeroing kick (p=.05) moves the non-zero share by .06 under 30 drift generations (plain .001), below the .10 threshold, because the clipped Gaussian re-inflates a zeroed weight at the next birth. The L0 coordinate needs an operator whose zeros PERSIST (a sparsity mask gene). The stasis scope stands; its escape is now more precisely stated.", False,
                      state="TEMPORAL_STASIS[burden=L0-threshold on continuous weights x mutation=clipped-gaussian-or-transient-zeroing]", state_reason="escape: an operator whose zeros persist across births (mask gene) or a magnitude burden")
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes A appended")


if __name__ == "__main__":
    main()
