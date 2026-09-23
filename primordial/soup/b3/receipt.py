"""File the B3 receipt from committed census rows. Run AFTER rebase so `git` is final.

usage: python -m primordial.soup.b3.receipt --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B"
CLAIM = ("B3 op census from execution: (1) wforge Encounter.step (+ its xorshift stream) traced at bytecode "
         "level over 60 worlds executes <=8 distinct arithmetic operators and mod+mul+add are >=60% of executed "
         "arithmetic ops; (2) in the B2 graphblas form, numpy<->GraphBLAS conversion takes >50% of wall time at "
         "<=8192 entities and SuiteSparse kernel execution <30%.")

# in-place bytecode variants are the same semantic operator
SEMANTIC = {"NB_INPLACE_ADD": "add", "NB_ADD": "add", "NB_INPLACE_SUBTRACT": "sub", "NB_SUBTRACT": "sub",
            "NB_MULTIPLY": "mul", "NB_INPLACE_MULTIPLY": "mul", "NB_REMAINDER": "mod", "NB_INPLACE_REMAINDER": "mod",
            "NB_FLOOR_DIVIDE": "floordiv", "NB_INPLACE_FLOOR_DIVIDE": "floordiv", "NB_AND": "and",
            "NB_INPLACE_AND": "and", "NB_XOR": "xor", "NB_INPLACE_XOR": "xor", "NB_OR": "or", "NB_INPLACE_OR": "or",
            "NB_LSHIFT": "lshift", "NB_INPLACE_LSHIFT": "lshift", "NB_RSHIFT": "rshift", "NB_INPLACE_RSHIFT": "rshift"}


def _jsonl(name):
    return [json.loads(x) for x in open(ROWS / name, encoding="utf-8")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    cal = _jsonl("B3-census-calibration.jsonl")
    cal_pos = [r for r in cal if r["part"] == "calibration"]
    cal_cheat = next(r for r in cal if r["part"] == "calibration_cheat")
    rep = _jsonl("B3-census-repeatability.jsonl")
    repeat_ok = bool(rep) and all(r["equal"] for r in rep)
    cold_first = min(cal_pos, key=lambda r: r["order"])
    # the cold-first run is a DETECTOR for the known cold-start loss, not a gate: the census
    # is collected after a warm-up, so the gate is every WARM calibration + cheat + repeat
    warm = [r for r in cal_pos if r["order"] != cold_first["order"]]
    calib_ok = (all(r["exact"] and not r["scope_leak"] for r in warm)
                and cal_cheat["counted_mul"] == cal_cheat["expected_mul"]
                and cal_cheat["counted_mod"] == cal_cheat["expected_mod"]
                and repeat_ok)
    b1 = _jsonl("B3-census-b1.jsonl")
    b2g = _jsonl("B3-census-b2gb.jsonl")
    b2r = _jsonl("B3-census-b2ref.jsonl")

    raw = Counter()
    for r in b1:
        raw.update({k.split(":", 1)[1]: v for k, v in r["ops"].items() if k.startswith("BINARY_OP:")})
    sem = Counter()
    for k, v in raw.items():
        sem[SEMANTIC.get(k, k)] += v
    total = sum(sem.values())
    mma = (sem["mod"] + sem["mul"] + sem["add"]) / total
    xs_only = {k: sem[k] for k in ("and", "xor", "lshift", "rshift")}

    shares = {str(r["entities"]): {**{g: round(v, 3) for g, v in r["wall_share"].items()},
                                   "unaccounted": round(r["unaccounted_share"], 3)} for r in b2g}
    small = [r for r in b2g if r["entities"] <= 8192]
    conv_max = max(r["wall_share"].get("convert", 0) for r in small)
    # the claim is "kernel < 30% at <= 8192 entities": it must hold at EVERY such size
    kern_max = max(r["wall_share"].get("kernel", 0) for r in small)
    ref_ops = Counter()
    for r in b2r:
        ref_ops.update({k.split(":", 1)[1] if ":" in k else k: v for k, v in r["ops"].items()})

    p1_ops = len(sem) <= 8
    p1_share = mma >= 0.60
    p2_conv = conv_max > 0.50
    p2_kern = kern_max < 0.30
    rec = {
        "lane": "B", "exp_id": "B3-op-census", "claim": CLAIM,
        # an uncalibrated instrument cannot kill or pass anything
        "status": ("INDETERMINATE" if not calib_ok else
                   "PASS" if all((p1_ops, p1_share, p2_conv, p2_kern)) else "KILL"),
        "engineering": {"b2gb_wall_share_by_entities": shares, "b1_worlds": len(b1), "b2ref_specs": len(b2r)},
        "science": {
            "b1_semantic_operator_counts": dict(sem.most_common()),
            "b1_distinct_semantic_operators": len(sem),
            "b1_mod_mul_add_share": round(mma, 4),
            "b1_ops_from_python_uint64_emulation": xs_only,
            "b2ref_executed_ops": dict(ref_ops.most_common(12)),
            "instrument_finding": (f"Python 3.12 sys.settrace opcode tracing: the first traced call in a fresh "
                                   f"process counted {cold_first['counted_mul']}/{cold_first['expected_mul']} "
                                   "executed multiplies; the identical call afterwards counted all of them. An "
                                   "earlier census without warm-up lost ~23% of world 0's ops. The mechanism "
                                   "inside CPython is not established"),
            "hypothesis_scoring": {
                "b1_at_most_8_operators": ("CONFIRMED" if p1_ops else
                                           f"WRONG: {len(sem)} semantic operators; and/xor/shifts are the xorshift "
                                           "stream plus Python's `& MASK64` uint64 emulation"),
                "b1_mod_mul_add_ge_60pct": f"{'CONFIRMED' if p1_share else 'WRONG'} ({mma:.1%})",
                "b2gb_convert_gt_50pct": f"{'CONFIRMED' if p2_conv else 'WRONG'} (max {conv_max:.1%} at <=8192 entities)",
                "b2gb_kernel_lt_30pct": f"{'CONFIRMED' if p2_kern else 'WRONG'} (max {kern_max:.1%} at <=8192 entities)",
            },
        },
        "controls": {
            "cheat": ("scope cheat RUN: an out-of-scope helper doing 50 mul + 50 mod is counted 0 when untraced "
                      f"(leaks: {sum(r['scope_leak'] for r in cal_pos)}/{len(cal_pos)}) and exactly when traced "
                      f"(mul {cal_cheat['counted_mul']}/{cal_cheat['expected_mul']}, "
                      f"mod {cal_cheat['counted_mod']}/{cal_cheat['expected_mod']})"),
            "positive": ("known op budgets counted exactly after warm-up: "
                         f"{sum(r['exact'] for r in warm)}/{len(warm)}; cold first run in a fresh process "
                         f"counted {cold_first['counted_mul']}/{cold_first['expected_mul']} multiplies"),
            "repeatability": (f"census over the same worlds twice in-process after a discarded warm-up: "
                              f"{sum(r['equal'] for r in rep)}/{len(rep)} worlds identical. A first attempt "
                              "without warm-up under-counted the first traced world by ~23% in every category"),
            "timing_control": "outermost-call-only timing, so nested GraphBLAS calls are not double counted; "
                              "group shares sum with 'unaccounted' to 1",
        },
        "rows": "primordial/ledger/rows/B/B3-census-*.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science")}, indent=1))
    print(json.dumps(shares))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
