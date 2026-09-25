"""ARCH4 tranche: reconciler notes (append-only), scoped stasis decisions, and one defect."""
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
DEFECT = {"id": "CW01-D072", "experiment_id": "cw01-arch4", "phase": "CLOSE_SCIENCE", "severity": "low", "category": "instrument",
          "status": "OPEN", "defect_class": "C - accounting gap; logged and continued",
          "title": "P-C03/P-C16: insulation-event count per accepted step was dropped by the frozen walk's step schema",
          "evidence": "The trap-to-NOP proposal hook attached 'trapped_words' to the operator record, but archaeon.campaign4.c4_05.walk stores only operator/args/proposals/reward/ref_broken/has_refs/descriptor/digest per step, so RESULT.json reports trapped_words_per_walker 0.0 in both arms. The arm effects (acceptance .602 -> .673, length delta .30 -> 1.80, exaptation .043 -> .032) are measured independently of that counter and stand.",
          "proposed_fix": "A descendant that needs the insulation count must count trapped words by re-decoding each accepted step's digest-verified child (regenerable from seeds), or wrap the walk. Not repaired here.",
          "found_by": "P-C03 RESULT.json"}


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    if DEFECT["id"] not in existing:
        rec = {"id": DEFECT["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
        rec.update({k: v for k, v in DEFECT.items() if k != "id"})
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-ARCH4/R1", "P-C13", "RECONCILER: the degenerate swamp has no gradient under ANY decode rule (modulo / trap-NOP / trap-HALT): D7 = D6 = 0 over 839 children per rule, "
                      "max reward on any environment .125 < floor .1875, walkers stay silent; the swamp is a property of the programs, not the decode.", False,
                      state="TEMPORAL_STASIS[starting_population=degenerate-gen0 x representation=trap-decode]",
                      state_reason="three decode rules strike the same surface; the next informative perturbation needs a different starting population (e.g. injected in-table generators as in C5-04)")
    L.append_evidence("T-ARCH4/M1", "P-C04", "RECONCILER: at radius 4, BLOCK edits (one window of 4 instructions) lose less than DISTRIBUTED edits (loss .569 vs .630; displacement .545 vs .620); "
                      "sequential-viable filtering leaves loss .048 by construction. Locality is an axis of the damage geometry that C4-02's radius curve did not measure.", True,
                      state="ACTIVE", state_reason="locality matters; next: window sizes 1/2/8 and locality under trap decode")
    L.append_evidence("T-ARCH4/D1", "P-C15", "RECONCILER: BLIND scattered deletion of k instructions is more destructive than CONTIGUOUS deletion of the same k at every fraction "
                      "(parents: .564/.761/.878 vs .463/.652/.795 at f .1/.2/.3; walkers slightly more robust than parents at every cell). Damage spread over more sites hurts more than a "
                      "contiguous hole of equal size - consistent with P-C04 and with C4-04's near-zero reference effect for contiguous deletion.", True,
                      state="ACTIVE", state_reason="a locality law is emerging across two perturbations; next: dose-response in number of sites at fixed k")
    L.append_evidence("T-ARCH4/R1", "P-C03", "RECONCILER: under trap-to-NOP the walk accepts MORE (.673 vs .602), grows SIX times more length (+1.80 vs +.30 instructions at depth 16), "
                      "exapts LESS (.032 vs .043) and is slightly less structurally diverse (1.24 vs 1.35): insulation makes the neutral band wider and emptier. D072: the insulation count was lost.", True)
    L.append_evidence("T-ARCH4/M1", "P-C16", "RECONCILER: length-balanced proposal weights do NOT stop growth under trap-to-NOP (+2.35 vs +1.80 instructions); they restore exaptation to the modulo level (.043). "
                      "Growth is driven by the ACCEPTANCE filter (NOP-trapped insertions are neutral and accepted, deletions of live code are rejected), not by the proposal mix - 'neutrality + length' is one phenomenon here.", True,
                      state="ACTIVE", state_reason="a mechanism for length growth is now stated and testable: next, a walk that rejects length-increasing neutral steps")
    L.append_evidence("T-ARCH4/W1", "P-C14", "RECONCILER: silent W0 drift becomes loud at ANY delay (.118/.109/.127/.108 at d1..d4, flat) and only faintly under noise (.018): the walkers' drift lives in "
                      "timing-sensitive behaviour that W0's immediate asks never exercise; delay is a switch, not a dose.", True,
                      state="ACTIVE", state_reason="a named phenotype now: timing-sensitive silent drift; next: which instructions carry it (ablation of accepted steps by ref_broken)")
    print("appended D072 + 6 reconciler notes with scoped stasis")


if __name__ == "__main__":
    main()
