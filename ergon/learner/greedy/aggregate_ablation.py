"""Aggregate leave-one-source-out ablation evals into a comparison table.

Reads runs/ablation/abl_eval_*.json and reports, per condition, overall
accuracy on the fixed gold set, the true/false balance, parse-fail, and the
per-source accuracy slice, plus the delta vs the full-corpus baseline. The
per-source slice is the load-bearing read: dropping a source should hurt the
gold slice that source taught (or reveal that another source transfers).
"""
from __future__ import annotations

import json
from pathlib import Path

RUNS = Path("F:/Prometheus/ergon/learner/greedy/runs/ablation")


def load(cond: str):
    p = RUNS / f"abl_eval_{cond}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def main():
    files = sorted(RUNS.glob("abl_eval_*.json"))
    conds = [f.stem.replace("abl_eval_", "") for f in files]
    # full first
    conds = (["full"] if "full" in conds else []) + [c for c in conds if c != "full"]

    full = load("full")
    full_acc = full["trained"]["accuracy"] if full else None
    base = full.get("base") if full else None

    print("\n=== SOURCE ABLATION (fixed gold_eval_v1, 1200 items, 600T/600F) ===")
    if base:
        print(f"base model: acc={base['accuracy']}  parse_fail={base['parse_fail_rate']}  "
              f"T={base['acc_on_true']} F={base['acc_on_false']}")
    print()
    lines = []
    rows_out = []
    for c in conds:
        d = load(c)
        if not d:
            continue
        t = d["trained"]
        bysrc = t["acc_by_source"]
        delta = round(t["accuracy"] - full_acc, 4) if full_acc is not None else None
        line = (f"{c:20s} acc={t['accuracy']:.4f}  d_vs_full={('%+.4f'%delta) if delta is not None else 'n/a':>8}  "
                f"T={t['acc_on_true']:.3f} F={t['acc_on_false']:.3f}  pf={t['parse_fail_rate']:.3f}  | "
                f"thes={bysrc.get('theseus','-')!s:>6} poll={bysrc.get('pollux','-')!s:>6} heph={bysrc.get('hephaestus','-')!s:>6}")
        print(line)
        lines.append(line)
        rows_out.append({"condition": c, "acc": t["accuracy"], "delta_vs_full": delta,
                         "acc_on_true": t["acc_on_true"], "acc_on_false": t["acc_on_false"],
                         "parse_fail": t["parse_fail_rate"], "by_source": bysrc})

    out = RUNS / "ablation_summary.json"
    out.write_text(json.dumps({"base": base, "full_acc": full_acc, "conditions": rows_out}, indent=2))
    print(f"\n[agg] wrote {out}")


if __name__ == "__main__":
    main()
