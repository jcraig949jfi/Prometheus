"""Score the C6 record rows against the posted rule (bus 1789393441422-0).

The harness's in-run summary row selected 'core' cells by first letter ("abc") and so also
counted the cheat_stride2 cells as core, mis-scoring a clean run as KILL. This scorer names the
core conditions exactly. The cell rows themselves are unaffected.

usage: python -m primordial.brain.c6_score <record.jsonl>
"""
from __future__ import annotations

import json
import pathlib
import sys

ROWS = pathlib.Path(__file__).resolve().parents[1] / "ledger" / "rows" / "C"
EXP_ID = "C6-audit-b6-fused-exactness"
CORE = ("a_elites_train", "b_elites_heldout", "c_p1", "c_p7", "c_mutated")


def main(argv):
    src = pathlib.Path(argv[0])
    rows = [json.loads(line) for line in open(src, encoding="utf-8")]
    cells = [r for r in rows if r["kind"] == "cell"]
    core = [c for c in cells if c["condition"] in CORE]
    core_exact = len(core) == 25 and all(c["genomes_exact"] == c["P"] for c in core)
    oracle = [c for c in cells if c["condition"] == "b_elites_heldout"]
    oracle_ok = all(c["brain_oracle_mismatches"] == 0 and c["brain_oracle_clear_rows"] > 0 for c in oracle)
    cheat = [c for c in cells if c["condition"] == "cheat_stride2"]
    cheat_ok = len(cheat) == 5 and all(c["P"] - c["genomes_exact"] >= 14 for c in cheat)
    status = "PASS" if core_exact and oracle_ok and cheat_ok else ("KILL" if not core_exact else "INDETERMINATE")
    out = {"exp_id": EXP_ID, "source": src.name, "git": rows[0]["git"],
           "core_cells_exact": f"{sum(c['genomes_exact'] == c['P'] for c in core)}/{len(core)}",
           "core_genomes_exact": f"{sum(c['genomes_exact'] for c in core)}/{sum(c['P'] for c in core)}",
           "brain_oracle": {f"w{c['gen_seed']}": [c["brain_oracle_clear_rows"], c["brain_oracle_mismatches"]] for c in oracle},
           "cheat_mismatching_genomes": {f"w{c['gen_seed']}": c["P"] - c["genomes_exact"] for c in cheat},
           "report_only_d": {f"{c['condition']}_w{c['gen_seed']}": f"{c['genomes_exact']}/{c['P']}"
                             for c in cells if c["condition"].startswith("d_")},
           "core_exact": core_exact, "oracle_ok": oracle_ok, "cheat_ok": cheat_ok,
           "status_by_posted_rule": status,
           "harness_summary_row_status": next(r for r in rows if r["kind"] == "summary")["status_by_posted_rule"],
           "harness_summary_row_defect": "core filter c['condition'][0] in 'abc' included cheat_stride2; fixed in c6_audit_b6.py"}
    ROWS.mkdir(parents=True, exist_ok=True)
    with open(ROWS / f"{EXP_ID}.summary.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
