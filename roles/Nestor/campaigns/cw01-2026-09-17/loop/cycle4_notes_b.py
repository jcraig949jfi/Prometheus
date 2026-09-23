"""Cycle-4 reconciler notes, part B: P-F08 (T-E03 mask gene) and P-F09 (T-X15 in e06 bodies) + defect D086."""
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
D086 = {"id": "CW01-D086", "experiment_id": "cw01-loop4", "phase": "EXECUTE", "severity": "medium", "category": "ruler", "status": "OPEN",
        "defect_class": "A - ill-conditioned ratio (D071 class)",
        "title": "P-F09's relative score loss (s0 - sd) / s0 explodes when the baseline score is tiny (duplicated TAPE bodies: mean 'loss' -2.66), and evolved bodies are not score-optimal so damage often IMPROVES raw score (TAPE fixed-k mean -.14): the ruler cannot support a length-vs-robustness read as designed",
        "evidence": "RESULT.json mean_loss TAPE|k2 -.138, pad|k2 +.126 (dilution of an improvement), duplicate|f -2.66; TAPE regression bands +-.25-.29 driven by outliers.",
        "proposed_fix": "Use absolute score change with a baseline floor, or MAE change; treat 'damage improves score' as the finding it is (see T-X16 note).", "found_by": "P-F09 result"}


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    if D086["id"] not in existing:
        rec = {"id": D086["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
        rec.update({k: v for k, v in D086.items() if k != "id"})
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-E03", "P-F08", "RECONCILER: the heritable MASK GENE makes the L0 coordinate attainable (drift moves the effective non-zero share by .34; the transient zeroing kick moved it .06). Under the tax at H the share falls (.54 -> .44, below p05) while MI excess (1.03 -> 1.02), routing precision (.55 -> .56), sparsity and score are inside their bands: reading SPARSITY_ONLY. The stasis scope [burden=L0 x mutation=clipped-gaussian-or-transient-zeroing] is ESCAPED (the coordinate moves) and the burden question is answered on this organism: representational burden pressure changes what is carried, not conditionality. T-E03 returns to ACTIVE with that answer on record.", True)
    L.append_evidence("T-X05", "P-F08", "cross: in e03, burden pressure on a heritable mask lowers the L0 share without touching capability structure (MI, precision) - the same shape as e08's 'burden fell at unchanged capability'.", True)
    L.append_evidence("T-X15", "P-F09", "RECONCILER (ruler ill-conditioned, D086; reading UNRESOLVED by rule): in evolved e06 bodies (575 TAPE, 558 TREE) blind deletion of 2 units IMPROVES raw score on average (TAPE relative loss -.14; TREE -.04), so 'damage robustness' has no fixed sign there. TREE: fixed-k and fraction-matched loss both fall with size (coef -.043 / -.050, below p05) and rise with depth (+.046 / +.047, above p95): in trees the coordinate that predicts damage sensitivity is DEPTH, with size protective under both damage doses - not the Proteus pattern (size protective at fixed k only). TAPE: no coefficient clears its (outlier-widened) band; NOP-pad halves whatever the effect is (dilution of an improvement, +.126). Portability: T-X15's fixed-count length effect is dilution in both substrates; the representation-specific coordinate in TREE is depth.", True)
    L.append_evidence("T-X16", "P-F09", "RECONCILER: evolved e06 bodies carry score-HARMFUL units (random deletion raises raw score, TAPE -.14 relative): part of damage's 'benefit' in P-E06 may be a DAMAGE_EFFECT proper (removal of deleterious structure under weak selection), distinct from the price. P-F04 (price 0) decides; this note records the candidate mechanism before its result is read.", True)
    L.append_evidence("T-E06", "P-F09", "cross: blind deletion improves raw score in evolved TAPE bodies on average; mutation-selection balance under sharing + price leaves deleterious instructions in place.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes B appended")


if __name__ == "__main__":
    main()
