"""Cycle-4 reconciler notes, part A: P-F01 and P-F11 (T-X15 / T-X17) + defects D084/D085. Run after every driver has exited."""
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
D = [
    {"id": "CW01-D084", "experiment_id": "cw01-loop4", "phase": "EXECUTE", "severity": "high", "category": "design", "status": "OPEN",
     "defect_class": "A - a preregistered prediction rested on a ruler property that does not hold",
     "title": "P-F01's 'fraction-matched' damage used ONE CONTIGUOUS window (k = .15 n at s=1); on a NOP-padded genome such a window lands in the padding half the time, so fraction-matched loss falls by dilution exactly as fixed-k loss does - the prediction table (DILUTION: fraction-matched unchanged) assumed scattered damage",
     "evidence": "pad (70 identity-preserving programs): delete k4 -.231, delete f.15 -.204, both below p05; loss orig .53 -> pad .33 under f.15. A dilution-neutral fraction-matched design deletes each instruction independently with probability f (scattered).",
     "proposed_fix": "The BROKEN flag raised by the rule is a defect of the prediction, not a finding against dilution. Re-pose with scattered fraction-matched damage in cycle 5; the pad result is recorded as consistent with DILUTION of a contiguous window.", "found_by": "P-F01 result"},
    {"id": "CW01-D085", "experiment_id": "cw01-loop4", "phase": "EXECUTE", "severity": "high", "category": "control", "status": "OPEN",
     "defect_class": "A - a manipulation that destroys function is not a coordinate manipulation",
     "title": "P-F01's persist=none arm collapses mean reward from .72 to .03 (below the viability floor 3/16) in 122/126 programs; its 'loss' (.99) is trivial, so the CARRIED_STATE reading from that arm is void",
     "evidence": "rows.json variants.persist_none.r0 mean .033 vs original .717; identity preserved in 4/126; persistent words 256 -> 0.",
     "proposed_fix": "Carried state cannot be removed without removing function in these programs; a dose (persist regs vs tape vs all on programs whose reward survives) or a census-only approach is the only honest route. Recorded; the census regression carries the evidence instead.", "found_by": "P-F01 result (baseline check)"},
]


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    with LEDGER.open("a", encoding="utf-8") as fh:
        for e in D:
            if e["id"] in existing:
                continue
            rec = {"id": e["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
            rec.update({k: v for k, v in e.items() if k != "id"})
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-X15", "P-F01", "RECONCILER (rule reading ['CARRIED_STATE','BROKEN'], corrected by D084/D085): (1) NOP-PAD, identity-preserving in 70/70 feasible programs, lowers loss under fixed-k (-.23) AND under the contiguous fraction-matched window (-.20): both are DILUTION of a contiguous damage window over a longer genome - the ruler's geometry, not a property of the program. (2) DUPLICATE changes behaviour in 30/70 and halves mean reward (.71 -> .41); among identity-preserving duplicates fixed-k loss falls (-.20, dilution) while fraction-matched loss does not (-.03): the copy is load-bearing when hit, so 'redundant executable structure' is NOT what duplication creates here. (3) persist=none destroys function (reward .72 -> .03): void as a manipulation (D085). (4) CENSUS along orig-rule walks (271 archived programs): under fixed k the depth effect is carried by log length (-.148, band +-.03) with persistent words inside its band (-.026); under fraction-matched, length carries nothing (-.011) and persistent words a small effect (-.032, band +-.027). Reading: the fixed-count length effect that named T-X15 is mostly DILUTION GEOMETRY; the residual coordinate is carried state, small, and not yet separable from function.", True,
                      state="ACTIVE", state_reason="the coordinate is re-posed: scattered fraction-matched damage (dilution-neutral) and a persist DOSE on programs whose reward survives; 'length = robustness' is retired as a mechanism claim")
    L.append_evidence("T-ARCH4/M1", "P-F01", "RECONCILER: P-D01's 'dose in units' and P-E05's 'growth lowers loss' are largely the geometry of a contiguous fixed-count window on a longer genome (dilution); the damage surface must be re-read with scattered fraction-matched damage before any robustness claim.", True)
    L.append_evidence("T-X17", "P-F11", "RECONCILER: temporal class after manipulation - identity-preserving NOP-pad preserves the class in 70/70 (length is not entangled with timing); duplication preserves it in 70 percent (30 percent when reward is lost); blind deletion that DESTROYS reward preserves the class in 41-42 percent (154 / 144 cases) while deletion that keeps reward preserves it in 95 percent: the class is partly structural (survives loss of function in two of five cases) and partly functional. persist=none sends 99 percent to immunity (ONE_NODE by the preregistered rule) - but P-F01 shows persist=none also destroys function (D085), so 'carried state is the timing coordinate' is entangled with 'carried state is the function'. T-X15 and T-X17 share their coordinate to the extent that both are the program's persistence, which is not yet separable from what the program computes.", True,
                      state="ACTIVE", state_reason="continuation: class along persist DOSE on programs that keep reward; class vs D-class of damaged children")
    L.append_evidence("T-X15", "P-F11", "cross: pad preserves timing class 100 percent, persist=none removes it 99 percent - consistent with carried state, subject to D085.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes A appended")


if __name__ == "__main__":
    main()
