"""B-R2-8: re-adjudicate skip-odd-INELIGIBLE cells with E's powered brain cheats (E-T3, 33038855e).

  python -m primordial.cohorts.b.b8_readjudicate

Predicate posted on the bus before running (B-R2-8): on the SAME committed rs0 top-16 genomes
(top_hex) and HELD8, honest 0 mismatched clear rows, shift_action 16/16, ablate_top elites_caught
>= 14/16 with input_invariant elites counted as not caught. A cell that meets the rule becomes
eligible and is checked with qd_ledger check on its already-recorded 8-seed median/IQR; no rerun.
The a2 w3 train8 cell (skip-odd 14/16, PASS) is scored too and downgraded if ablate_top < 14/16.
"""
from __future__ import annotations

import json

import numpy as np

from primordial.cohorts.b.b1_qlinear import QLin, ROOT
from primordial.cohorts.e.oracles import brain_oracle_cheats
from primordial.fabric.rows import RowWriter
from primordial.ops import qd_ledger as QL
from primordial.qd import e7_run as E7

EXP = "B-R2-8-readjudicate-powered-brain-cheats"
ROWS = ROOT / "primordial" / "ledger" / "rows" / "B" / f"{EXP}.jsonl"
# (source exp, world, bits, acts, pressure, prior verdict)
CELLS = [("B-R2-4-int2-linear-nibble-w4-train128", 4, 2, 8, "train128", "INELIGIBLE"),
         ("B-R2-6-int3-a2-linear-nibble-w4-train8", 4, 3, 2, "train8", "INELIGIBLE"),
         ("B-R2-6-int3-a2-linear-nibble-w3-train128", 3, 3, 2, "train128", "INELIGIBLE"),
         ("B-R2-6-int3-a2-linear-nibble-w3-train8", 3, 3, 2, "train8", "PASS")]


def main() -> None:
    ledger = QL.load()
    with RowWriter(ROWS, EXP, commit_every_s=10**9) as rw:
        for src, w, bits, acts, pr, before in CELLS:
            q = QLin(w, bits, acts)
            rows = [json.loads(l) for l in open(ROOT / "primordial" / "ledger" / "rows" / "B" / f"{src}.jsonl",
                                                encoding="utf-8") if l.strip()]
            rec = [r for r in rows if r.get("status") == "record" and r.get("tag") == "full"]
            rs0 = [r for r in rec if r["run_seed"] == 0][-1]
            held = [r["held64_per_seed"] for r in sorted(rec, key=lambda r: r["run_seed"])][-8:]
            raw = np.frombuffer(b"".join(bytes.fromhex(h) for h in rs0["top_hex"]), np.uint8).reshape(-1, q.glen)
            top = q.decode(q.unpack(raw))
            c = brain_oracle_cheats(q.g7, top, E7.HELD8)
            P = c["elites"]
            ablate_caught = c["ablate_top"]["elites_caught"]      # invariant elites never enter ablate_top
            ok = (c["honest"]["mismatched_rows"] == 0 and c["shift_action"]["elites_caught"] == P
                  and ablate_caught >= 14 and rs0["world_oracle_skip_lin"]["elites_failing"] >= 14
                  and rs0["world_oracle_honest"]["elites_failing"] == 0
                  and rs0["fused_vs_numpy_elites_differing"] == 0)
            med = float(np.median(held))
            iqr = float(np.percentile(held, 75) - np.percentile(held, 25))
            verdict = QL.check(ledger, f"w{w}", f"{pr}_held64", med, iqr, q.glen, len(held), ok)
            row = {"status": "control", "source_exp": src, "world": f"w{w}", "pressure": f"{pr}_held64",
                   "bits": bits, "acts": acts, "genome_bytes": q.glen, "held64_median": med, "held64_iqr": iqr,
                   "n_runs": len(held), "verdict_before": before, "powered_cheats": c, "oracle_clean_powered": ok,
                   "verdict_after": verdict}
            print(json.dumps({k: v for k, v in row.items() if k != "powered_cheats"}
                             | {"ablate_caught": ablate_caught, "invariant": c["input_invariant_elites"],
                                "shift": c["shift_action"]["elites_caught"], "skip_odd": c["skip_odd"]["elites_caught"],
                                "honest_mm": c["honest"]["mismatched_rows"]}), flush=True)
            rw.write(row)


if __name__ == "__main__":
    main()
