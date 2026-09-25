"""File the lane-B bounty receipt against C7d: its sole KILL target was the mislabelled charge channel.

Run only after the rows commit is on the integration branch; pass that SHA as --git.
usage: python -m primordial.soup.b7.receipt_bounty_c7d --git <pushed sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS = ROOT / "ledger" / "rows" / "B" / "B-bounty-C7d-charge-index.jsonl"
C7D = ROOT / "ledger" / "rows" / "C" / "C7d-chance-grounded-contrast.jsonl"
CLAIM = ("Bounty on C7d-chance-grounded-contrast: its only KILL target, gs 612 j2, is the charge bucket, mislabelled as "
         "a register feature because the C7 harness assumed the charge channel is the last observation column. "
         "Measured from observations (B NpEncounter, zero actions, slot 0, 256 envs, full horizon, charge bucket "
         "computed independently from charge). Predicted: (H1) exactly one column matches the charge bucket (>= 0.99 "
         "clean, within 0.05 of 1-1/corrupt_rate corrupted) and it is obs_perm.index(D-1) in 36/36 worlds; (H2) that "
         "column is not last in 29/36; (H3) in gs 612 it is column 2; (H4) every other column matches <= 0.02. Cheat "
         "control: 'charge = last column' must pass the same bar exactly where the measured column is last.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = [json.loads(x) for x in open(ROWS, encoding="utf-8")]
    n = len(rows)
    h1 = all(r["measured_equals_obs_perm"] for r in rows)
    not_last = sum(not r["charge_is_last"] for r in rows)
    h2 = not_last == 29 and n == 36
    g612 = next(r for r in rows if r["gen_seed"] == 612)
    h3 = g612["measured_charge_columns"] == [2]
    max_other = max(r["max_other_column_match"] for r in rows)
    h4 = max_other <= 0.02
    cheat_ok = all(r["cheat_last_column_passes_bar"] == r["charge_is_last"] for r in rows)
    cheat_pass_worlds = [r["gen_seed"] for r in rows if r["cheat_last_column_passes_bar"]]
    c7d_target = next((json.loads(l) for l in open(C7D, encoding="utf-8")
                       if json.loads(l).get("kind") == "target" and json.loads(l)["gen_seed"] == 612
                       and json.loads(l)["j"] == 2), None)
    status = "KILL" if (h1 and h2 and h3 and h4 and cheat_ok) else "INDETERMINATE"
    rec = {
        "lane": "B", "exp_id": "B-bounty-C7d-charge-index", "claim": CLAIM, "status": status,
        "refutes": "C7d-chance-grounded-contrast",
        "engineering": {"worlds": n, "envs_per_world": 256, "actions": "zero", "slot": 0},
        "science": {
            "hypothesis_scoring": {
                "h1_measured_charge_column_is_obs_perm_position": f"{'CONFIRMED' if h1 else 'WRONG'} "
                                                                  f"({sum(r['measured_equals_obs_perm'] for r in rows)}/{n})",
                "h2_charge_not_last": f"{'CONFIRMED' if h2 else 'WRONG'} ({not_last}/{n})",
                "h3_gs612_charge_column_is_2": f"{'CONFIRMED' if h3 else 'WRONG'} "
                                               f"(measured {g612['measured_charge_columns']}, "
                                               f"match {g612['match_rate_per_column']})",
                "h4_other_columns_le_0_02": f"{'CONFIRMED' if h4 else 'WRONG'} (max {max_other})",
            },
            "refuted_target": {"gen_seed": 612, "j": 2,
                               "c7d_row": ({"support": c7d_target["null_affine"]["support"],
                                            "detected": c7d_target["plastic_affine"]["detected"],
                                            "switches": c7d_target["plastic_affine"]["switches"]}
                                           if c7d_target else None),
                               "is": "the charge bucket min(15, charge//32), which no affine map of registers fits"},
            "acknowledged": ("lane C confirmed and fixed the harness (d1f73fc3c) and filed "
                             "C7-correction-charge-column-index crediting B; A removed C7d's auto-scored kill point "
                             "and invited this receipt"),
        },
        "controls": {
            "cheat": (f"harness assumption 'charge = last column' scored with the same bar passes in worlds "
                      f"{cheat_pass_worlds} and fails in the other {n - len(cheat_pass_worlds)}; it passes exactly "
                      f"where the measured charge column is last: {cheat_ok}"),
            "negative": f"register columns matching the charge bucket: max {max_other} over all worlds and columns",
        },
        "rows": "primordial/ledger/rows/B/B-bounty-C7d-charge-index.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "refutes", "science", "controls")}, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
