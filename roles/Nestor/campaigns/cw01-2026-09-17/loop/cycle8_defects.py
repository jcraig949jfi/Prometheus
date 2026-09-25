"""Cycle-8 defects: D089 (P-I02's in-sample regime-register predictor is vacuous) and D090 (P-J02 / P-J08's
first census baseline was measured on a different held-out slice than the mutants)."""
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
DEFECTS = [
    {"id": "CW01-D089", "experiment_id": "cw01-loop7", "phase": "READ", "severity": "medium", "category": "ruler", "status": "OPEN",
     "defect_class": "A - an in-sample lookup accuracy over near-unique values is vacuous",
     "title": "P-I02's regime_registers() scored each register by the IN-SAMPLE accuracy of a value -> regime lookup; a register holding 64 distinct values over 64 asks (a tag register) scores 1.0 trivially. Cycle 7's reading 'the organism reads the regime word into a register (predictor accuracy 1.0) but the register is causally inert' rested on it.",
     "evidence": "P-I02 rows: world A candidate register 13, accuracy 1.0, n_values 64 of 64 asks, typical values 18840 / 51331 (tags). P-J02 probes at the answering OUT: unread words 3 of 3 on 5/6 plateau genomes (2 on one), literal regime registers [], cross-set lookup registers [] - the answer is emitted BEFORE the ask tick is read; the regime word is read afterwards, in the same tick, and cannot reach the answer.",
     "proposed_fix": "Score regime registers by cross-set lookup (fit on one held-out set, test on another) and by literal equality, at the moment of the answering OUT (probe by rewriting the OUT's source register), as P-J02 does. The cycle-7 'causally inert' conclusion stands (register transplant changed 0 percent), its mechanism reading is corrected: the word is not read before the answer.", "found_by": "P-J02 probe_out vs P-I02 rows"},
    {"id": "CW01-D090", "experiment_id": "cw01-loop8", "phase": "EXECUTE", "severity": "medium", "category": "ruler", "status": "FIXED",
     "defect_class": "A - a screen baseline measured on a different sample than the screened items",
     "title": "P-J02 and P-J08's first runs classified mutants as beneficial when their 2-set (P-J02: 1-set) held-out reward exceeded the plateau's 4-SET mean + .05; on the screen slice the plateau itself scores higher (.625 on set 0), so 58 percent of neutral mutants read as beneficial (best .625 = the plateau's own set-0 score).",
     "evidence": "P-J02 run 1 (RESULT_prev1.json): grammar one-op beneficial .58, best .625, identical on xor1 and xor15; P-J08 run 1: B .587 vs v0.4 .577 'beneficial'. Rerun with the baseline on the same 2 sets and confirmation on all 4: beneficial 0.0 for both grammars.",
     "proposed_fix": "APPLIED before any reading was recorded as a result: the baseline is computed on the same slice as the screen; beneficial / hit calls are confirmed on all 4 held-out sets; both drivers rerun (first outputs archived as *_prev1). The first runs' evidence lines are superseded by the reruns.", "found_by": "reconciler read of P-J08 run 1 (best == plateau's own set score)"},
]


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    n = 0
    with LEDGER.open("a", encoding="utf-8") as fh:
        for d in DEFECTS:
            if d["id"] in existing:
                continue
            rec = {"id": d["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
            rec.update({k: v for k, v in d.items() if k != "id"})
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            n += 1
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-X21", "P-J02", "DEFECT D089: cycle 7's 'reads the regime word into a register' rested on an in-sample lookup over near-unique values (vacuous); P-J02's probes show the answer is emitted before the ask tick is read. The 'causally inert' conclusion stands; its mechanism is corrected.", True)
    L.append_evidence("T-R01", "P-J02", "DEFECT D090 (fixed pre-read): the first census baseline was on a different held-out slice than the mutants; rerun with the same-slice baseline and 4-set confirmation. The first runs' evidence lines (P-J02, P-J08 material True/False) are superseded by the reruns.", False)
    print("defects appended:", n, "ledger:", len(LEDGER.read_text(encoding='utf-8').splitlines()))


if __name__ == "__main__":
    main()
