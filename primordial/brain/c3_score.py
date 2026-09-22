"""Score the C3 record run against its pre-run hypothesis (bus 1789390041907-0).

usage: python -m primordial.brain.c3_score <record.jsonl>
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

ROWS = pathlib.Path(__file__).resolve().parents[1] / "ledger" / "rows" / "C"
EXP_ID = "C3-representation-ecology"
TENSOR = ("tt", "cp", "tucker")


def main(argv):
    src = pathlib.Path(argv[0])
    rows = [json.loads(line) for line in open(src, encoding="utf-8")]
    pts = [r for r in rows if r["kind"] == "point"]
    seeds = sorted({p["seed"] for p in pts})
    P = lambda s, t: [p for p in pts if p["seed"] == s and p["target"] == t and not p["bytes_mismatch"]]
    at = lambda ps, eps, fams=None: sorted([p for p in ps if p["rel_mse"] <= eps and (fams is None or p["family"] in fams)],
                                           key=lambda p: (p["bytes"], p["flops"]))
    rep = lambda p: None if p is None else {k: p[k] for k in ("rep", "bytes", "flops", "rel_mse")}
    first = lambda lst: lst[0] if lst else None

    h1 = []
    for s in seeds:
        ps = P(s, "tt_rank2")
        w, t, c, k = first(at(ps, 1e-4)), first(at(ps, 1e-4, ("tt",))), first(at(ps, 1e-4, ("cp",))), first(at(ps, 1e-4, ("tucker",)))
        h1.append({"seed": s, "winner": rep(w), "best_tt": rep(t), "best_cp": rep(c), "best_tucker": rep(k),
                   "held": bool(w and w["family"] == "tt" and w["bytes"] <= 1000
                                and (c is None or c["bytes"] >= 2 * w["bytes"])
                                and (k is None or k["bytes"] >= 2 * w["bytes"]))})
    h2 = []
    for s in seeds:
        ps = P(s, "separable_decay")
        w, t = first(at(ps, 1e-4)), first(at(ps, 1e-4, ("tt",)))
        h2.append({"seed": s, "winner": rep(w), "best_tt": rep(t),
                   "held": bool(w and w["family"] == "cp" and (t is None or t["bytes"] >= 2 * w["bytes"]))})
    h3 = []
    for s in seeds:
        ps = P(s, "program_in")
        w, ten = first(at(ps, 1e-4)), first(at(ps, 1e-4, TENSOR))
        h3.append({"seed": s, "winner": rep(w), "best_tensor": rep(ten),
                   "held": bool(w and w["family"] == "program" and w["bytes"] <= 64
                                and (ten is None or ten["bytes"] >= 500 * w["bytes"]))})
    h4 = []
    for s in seeds:
        ps = P(s, "program_out")
        prog = next(p for p in ps if p["family"] == "program")
        w, b8 = first(at(ps, 1e-4)), next(p for p in ps if p["rep"] == "bits8")
        h4.append({"seed": s, "program_rel": prog["rel_mse"], "winner": rep(w), "bits8": rep(b8),
                   "held": bool(prog["rel_mse"] >= 0.9 and w and w["family"] == "cp" and w["bytes"] < b8["bytes"])})
    h5 = []
    for s in seeds:
        ps = P(s, "noise")
        dense = next(p for p in ps if p["rep"] == "dense")["bytes"]
        w = first(at(ps, 1e-2))
        cheap_good = [p["rep"] for p in ps if p["family"] not in ("dense", "bits")
                      and p["rel_mse"] <= 0.5 and p["bytes"] < 0.5 * dense]
        h5.append({"seed": s, "winner_at_1e-2": rep(w), "structured_reps_rel_le_0.5_under_half_dense": cheap_good,
                   "held": bool(w and w["family"] == "bits" and not cheap_good)})
    cheat = [p for p in pts if p["family"] == "cheat_ref"]
    honest = [p for p in pts if p["family"] != "cheat_ref"]
    controls = {
        "cheat_flagged": f"{sum(p['bytes_mismatch'] for p in cheat)}/{len(cheat)}",
        "honest_flagged": [(p["seed"], p["target"], p["rep"]) for p in honest if p["bytes_mismatch"]],
        "dense_max_rel": max(p["rel_mse"] for p in pts if p["rep"] == "dense"),
        "program_in_program_rel": [next(p for p in P(s, "program_in") if p["family"] == "program")["rel_mse"] for s in seeds],
    }
    controls_ok = (all(p["bytes_mismatch"] for p in cheat) and not controls["honest_flagged"]
                   and controls["dense_max_rel"] <= 1e-12 and all(x <= 1e-12 for x in controls["program_in_program_rel"]))
    held = lambda h: all(x["held"] for x in h)
    status = ("KILL" if not (held(h1) and held(h3) and held(h5))
              else "PASS" if controls_ok else "FAIL")
    fronts = [r for r in rows if r["kind"] == "front"]
    out = {"exp_id": EXP_ID, "source": src.name, "git": rows[0]["git"], "seeds": seeds,
           "H1_tt_rank2": {"held": held(h1), "per_seed": h1}, "H2_separable_decay": {"held": held(h2), "per_seed": h2},
           "H3_program_in": {"held": held(h3), "per_seed": h3}, "H4_program_out": {"held": held(h4), "per_seed": h4},
           "H5_noise": {"held": held(h5), "per_seed": h5}, "controls": controls, "controls_ok": controls_ok,
           "status_by_posted_rule": status,
           "fronts": [{k: f[k] for k in ("seed", "target", "front_bytes_err", "cheapest_at_eps", "flagged")} for f in fronts]}
    ROWS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, ROWS / f"{EXP_ID}.jsonl")
    with open(ROWS / f"{EXP_ID}.summary.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items() if k != "fronts"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
