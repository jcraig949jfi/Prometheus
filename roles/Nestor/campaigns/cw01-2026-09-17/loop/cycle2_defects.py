"""Cycle-2 defects (append-only, idempotent). Run after the batch so no concurrent appends occur."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

LEDGER = HERE.parent / "DEFECTS.jsonl"
D = [
    {"id": "CW01-D073", "experiment_id": "cw01-arch4", "phase": "EXECUTE", "severity": "medium", "category": "instrument", "status": "OPEN",
     "defect_class": "A - vacuous cells in a deformation probe",
     "title": "P-D02: per-tag 'delays', 'interleave=random' and 'ask_timing=interleaved' knobs are INERT at K=1 - those grid cells scored identical episodes",
     "evidence": "episodes_for(W0 with delays=(1,2,3,4)) == episodes_for(W0) tick for tick; likewise delays=(0,1), interleave=random, ask_timing=interleaved (verified in-session, 16 episodes each). archaeon/wse/worlds.py consumes spec.delays only on the random-timing generator path (line 344), which W0's one-stream K=1 spec never takes; the global 'delay' (NOISE ticks between the last PUT and the asks, lines 220/280) is the only live timing knob for these specs. P-D02's 'stochastic delays are silent' cells (displacement .000-.002) are therefore vacuous, not a finding.",
     "proposed_fix": "P-D02's material content is narrowed to: the switch is an INSERTED NOISE TICK between PUT and ASK (deterministic delay 1 -> displacement .118; interleaved_d1 .07; NOISE words inside the same tick .009). Continuation: vary the CONTENT of the inserted tick (empty / NOISE / repeated PUT) and use K=2 worlds where per-tag delays are live. Recorded on T-ARCH4/W1; a new node T-X12 (the inserted-tick switch) is opened.",
     "found_by": "reconcile of P-D02 + episode comparison"},
    {"id": "CW01-D074", "experiment_id": "cw01-e06", "phase": "EXECUTE", "severity": "medium", "category": "code", "status": "OPEN",
     "defect_class": "B - latent crash in a frozen module, surfaced by descendants",
     "title": "world_e06.growth_advantage crashes on any call: len() applied to an int (never exercised in e06)",
     "evidence": "P-D11 and P-D13 crashed at world_e06.py:730 (`n = float(len(run['history'][0].get('n_' + label, 0) or 1))`) with TypeError; e06 closed at QUALIFY and never ran the ecology read-outs. The frozen module is not edited; both drivers compute the same formula locally.",
     "proposed_fix": "Not fixed in the frozen module (e06's committed state); any e06 descendant must use its own growth formula. Logged.",
     "found_by": "P-D11/P-D13 run 1 tracebacks"},
    {"id": "CW01-D075", "experiment_id": "cw01-arch4", "phase": "EXECUTE", "severity": "high", "category": "harness", "status": "FIXED",
     "defect_class": "B - execution blocker",
     "title": "P-D01 run 1: unbounded rejection sampler for random window placement hung two pool workers for 3.1 h and blocked the batch",
     "evidence": "Process census: six workers finished (140-240 s CPU), two at 11,264 s CPU each, main with 0 log lines for 3 h; the placement loop `while len(starts) < s` had no iteration bound and a non-modular spacing test, so some (n, k, s) cells were infeasible. Killed by explicit PID (main + 8 verified children); the batch runner continued with P-D03.",
     "proposed_fix": "Sampler bounded at 500 rejections with a recorded fallback to even placement; spacing measured on the ring. P-D01 rerun after the batch. Standing rule: every rejection loop in a driver carries an explicit bound.",
     "found_by": "batch stall census"},
]


def main():
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    with LEDGER.open("a", encoding="utf-8") as fh:
        for e in D:
            if e["id"] in existing:
                continue
            rec = {"id": e["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
            rec.update({k: v for k, v in e.items() if k != "id"})
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            added.append(e["id"])
    RS.require_ascii_safe(LEDGER)
    print("appended", added)


if __name__ == "__main__":
    main()
