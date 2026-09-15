"""H-R4-3 (round 4 P0, builder H): an INDEPENDENT replay of G's world screen from committed rows.

Aimed at the claim (the verdicts in primordial/ledger/qd/worlds_r4.json), not at G's code: nothing from
primordial.metric.{screen, worlds, suite, baseline, invariant, screen_run} is imported, and no number is
read from the file or from G's aggregate rows. Numbers come from the lowest committed rows:

  floor parts   suite_cheap rows (G-R4-3-stage1): floors.abstain_held64, floors.best_fixed_held64, and the
                median of floors.random_action_held64_by_policy_seed; gate = gate.gate_held64
  learner       run rows without `family`, grouped by the cell's OWN (gen_seed, pressure) (train8 in
                G-R4-3-stage1; train128 in G-R4-3-stage2 / G-R4-3-stage2-learner): median over >= 8 run
                seeds (SWARM_R4 s2 G-R4-1). A train8 learner never enters a train128 floor.
  baseline      run rows with family linear (G-R4-3-stage2): held64_per_seed per run seed, the median, and
                primordial.metric.ci.median_ci over the values in run-seed order (M3: 10,000 resamples,
                PCG64 20260914; G 1789433928197-0); bytes = genome_bytes (one value per cell)

Rules (SWARM_R4 s2/s3/s7, operator message 13, conductor 1789433714703-0, 1789433825087-0, 1789440120713-0):
  F      the four-policy floor = max of the parts run; a lower BOUND when the learner was not run
  f(v)   four_policy: F        gate_in: max(F, gate)
  lo     the baseline's ci95[0]
  SURVIVED iff lo > f(v). HOLD variants: HELD iff gate > F and not SURVIVED. Else CULLED, with cull_reason
  BASELINE iff gate > F, else WEAK_WORLD. A cell with no baseline rows: CULLED NOT_REACHED (stage 1 only).
  Bound F: the verdicts are exact iff lo <= F and gate <= F (checked by re-judging at a larger floor).
  Otherwise the cell is PENDING:
    lo > F    survivable: the file may not be written with it (A 1789440120713-0), so it is a mismatch
    lo <= F   non-survivable: no variant can SURVIVE (lo <= F <= true floor <= f(v)). HOLD variants
              PENDING; CULL variants CULLED with cull_reason PENDING.
  Stop: stage 2 order is (gate - F) descending, then gen_seed, then pressure (train8 first). Per variant,
  after MAX_SURVIVORS SURVIVED cells every later cell is CULLED NOT_REACHED. PENDING never counts.

    python -m primordial.score.screen_replay [--worlds PATH] [--write]     rc 0 iff 0 mismatches, 0 row defects
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess

import numpy as np

from primordial.metric.ci import median_ci
from primordial.score.round2 import ROOT

ROWS = ROOT / "primordial" / "ledger" / "rows" / "G"
STAGE1 = ROWS / "G-R4-3-stage1.jsonl"
STAGE2 = ROWS / "G-R4-3-stage2.jsonl"
LEARNER = ROWS / "G-R4-3-stage2-learner.jsonl"
WORLDS_R4 = ROOT / "primordial" / "ledger" / "qd" / "worlds_r4.json"
OUT = ROOT / "primordial" / "ledger" / "rows" / "H" / "H-R4-3-screen-replay.jsonl"
VARIANTS = ("four_policy|CULL", "four_policy|HOLD", "gate_in|CULL", "gate_in|HOLD")
ACTIVE = ("gate_in", "HOLD")                  # operator message 13; the replay does not take it from the file
MAX_SURVIVORS = 8                             # SWARM_R4 s2 G-R4-3
MIN_RUNS = 8
PRESSURES = ("train8_held64", "train128_held64")
PARTS = ("abstain", "best_constant", "uniform_random_median", "input_invariant_learner")
TOL = 1e-9


def jsonl(path) -> list[dict]:
    p = pathlib.Path(path)
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def _per_run_seed(runs: list[dict], what: str, defects: list[str]) -> list[float] | None:
    by: dict[int, float] = {}
    for r in runs:
        rs, v = int(r["run_seed"]), float(r["held64_per_seed"])
        if rs in by and by[rs] != v:
            defects.append(f"{what}: run seed {rs} has two values {by[rs]} and {v}")
        by[rs] = v
    if not all(r.get("budget_ok") for r in runs):
        defects.append(f"{what}: a run is not at its budget")
    if len(by) < MIN_RUNS:
        defects.append(f"{what}: {len(by)} run seeds < {MIN_RUNS}")
        return None
    return [by[k] for k in sorted(by)]


def measure(stage1=STAGE1, stage2=STAGE2, learner=LEARNER) -> tuple[dict, list[str]]:
    """{(gen_seed, pressure): numbers} from the lowest committed rows, plus the row defects found."""
    s1, s2, sl = jsonl(stage1), jsonl(stage2), jsonl(learner)
    defects: list[str] = []
    cheap: dict[tuple, dict] = {}
    for r in s1:
        if r.get("kind") != "suite_cheap":
            continue
        k = (int(r["gen_seed"]), r["pressure"])
        if k in cheap and (cheap[k]["floors"], cheap[k]["gate"]) != (r["floors"], r["gate"]):
            defects.append(f"w{k[0]} {k[1]}: two suite_cheap rows disagree")
        cheap[k] = r
    learn: dict[tuple, list] = {}
    base: dict[tuple, list] = {}
    for r in s1 + s2 + sl:
        if r.get("kind") == "run":
            k = (int(r["gen_seed"]), r["pressure"])
            (base if r.get("family") == "linear" else learn).setdefault(k, []).append(r)
    out = {}
    for k in sorted(cheap):
        r, what = cheap[k], f"w{k[0]} {k[1]}"
        fl = r["floors"]
        parts = {"abstain": float(fl["abstain_held64"]), "best_constant": float(fl["best_fixed_held64"]),
                 "uniform_random_median": float(np.median(fl["random_action_held64_by_policy_seed"])),
                 "input_invariant_learner": None}
        gate = float(r["gate"]["gate_held64"])
        for p in PARTS[:3]:
            if abs(parts[p] - float(r["parts"][p])) > TOL:
                defects.append(f"{what}: suite_cheap parts.{p} {r['parts'][p]} != floors value {parts[p]}")
        if abs(gate - float(r["gate_held64"])) > TOL:
            defects.append(f"{what}: suite_cheap gate_held64 {r['gate_held64']} != gate.gate_held64 {gate}")
        if k in learn:
            lv = _per_run_seed(learn[k], f"{what} learner", defects)
            if lv is not None:
                parts["input_invariant_learner"] = float(np.median(lv))
        b = None
        if k in base:
            bv = _per_run_seed(base[k], f"{what} baseline", defects)
            nbytes = {int(x["genome_bytes"]) for x in base[k]}
            if len(nbytes) != 1:
                defects.append(f"{what} baseline: genome_bytes differ across run seeds {sorted(nbytes)}")
            if bv is not None:
                lo, hi = median_ci(bv)
                b = {"median": float(np.median(bv)), "ci95": [lo, hi], "bytes": min(nbytes), "n_runs": len(bv)}
        out[k] = {"world": f"w{k[0]}", "gen_seed": k[0], "pressure": k[1], "parts": parts, "gate": gate, "baseline": b}
    for k in sorted(set(learn) | set(base)):
        if k not in cheap:
            defects.append(f"w{k[0]} {k[1]}: run rows with no suite_cheap row")
    return out, defects


def judge(F: float, gate: float, lo: float, variant: str) -> dict:
    q1, q2 = variant.split("|")
    f = F if q1 == "four_policy" else max(F, gate)
    if lo > f:
        return {"verdict": "SURVIVED", "cull_reason": None, "floor": f}
    if q2 == "HOLD" and gate > F:
        return {"verdict": "HELD", "cull_reason": None, "floor": f}
    return {"verdict": "CULLED", "cull_reason": "BASELINE" if gate > F else "WEAK_WORLD", "floor": f}


def replay_cell(m: dict, defects: list[str]) -> dict:
    F = max(v for v in m["parts"].values() if v is not None)
    gate = m["gate"]
    bound = m["parts"]["input_invariant_learner"] is None
    floors = {v: (F if v.startswith("four_policy") else max(F, gate)) for v in VARIANTS}
    rec = {"world": m["world"], "gen_seed": m["gen_seed"], "pressure": m["pressure"], "floor_parts": m["parts"],
           "floor": F, "floor_is_bound": bound, "gate_held64": gate, "baseline": m["baseline"], "pending": None}
    if m["baseline"] is None:
        rec.update(stage=1, verdicts={v: {"verdict": "CULLED", "cull_reason": "NOT_REACHED", "floor": floors[v]}
                                      for v in VARIANTS})
        return rec
    rec["stage"] = 2
    lo = m["baseline"]["ci95"][0]
    if bound and (lo > F or gate > F):
        if lo > F:
            rec["pending"] = "survivable"
            rec["verdicts"] = {v: {"verdict": "PENDING", "cull_reason": None, "floor": floors[v]} for v in VARIANTS}
        else:
            rec["pending"] = "non_survivable"
            rec["non_survivable_exact"] = {"ci95_lo": lo, "bound": F, "holds": lo <= F}
            rec["verdicts"] = {v: ({"verdict": "PENDING", "cull_reason": None, "floor": floors[v]} if v.endswith("HOLD")
                                   else {"verdict": "CULLED", "cull_reason": "PENDING", "floor": floors[v]})
                               for v in VARIANTS}
        return rec
    rec["verdicts"] = {v: judge(F, gate, lo, v) for v in VARIANTS}
    if bound:                                  # exact from the bound: a larger true floor judges the same
        higher = max(F, lo, gate) + 1.0
        for v in VARIANTS:
            a, b = rec["verdicts"][v], judge(higher, gate, lo, v)
            if (a["verdict"], a["cull_reason"]) != (b["verdict"], b["cull_reason"]):
                defects.append(f"{m['world']} {m['pressure']} {v}: a verdict from the bound is not exact")
    return rec


def order_key(rec: dict) -> tuple:
    return (-(rec["gate_held64"] - rec["floor"]), rec["gen_seed"], PRESSURES.index(rec["pressure"]))


def apply_stop(recs: list[dict], max_survivors: int = MAX_SURVIVORS) -> list[dict]:
    count = dict.fromkeys(VARIANTS, 0)
    for r in sorted(recs, key=order_key):
        for v in VARIANTS:
            if count[v] >= max_survivors:
                r["verdicts"][v] = {"verdict": "CULLED", "cull_reason": "NOT_REACHED", "floor": r["verdicts"][v]["floor"]}
            elif r["verdicts"][v]["verdict"] == "SURVIVED":
                count[v] += 1
    return sorted(recs, key=order_key)


def replay(stage1=STAGE1, stage2=STAGE2, learner=LEARNER, max_survivors=MAX_SURVIVORS) -> tuple[list[dict], list[str]]:
    m, defects = measure(stage1, stage2, learner)
    return apply_stop([replay_cell(x, defects) for x in m.values()], max_survivors), defects


def _eq(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= TOL


def compare(doc: dict, recs: list[dict], active=ACTIVE, max_survivors=MAX_SURVIVORS) -> list[dict]:
    """Every field of every cell, under all four variants: file vs replay."""
    mm: list[dict] = []

    def miss(k, field, file_v, replay_v):
        mm.append({"world": k[0] if k else None, "pressure": k[1] if k else None, "field": field,
                   "file": file_v, "replay": replay_v})

    if (doc.get("q1_floor_policy"), doc.get("q2_policy")) != tuple(active):
        miss(None, "active variant", [doc.get("q1_floor_policy"), doc.get("q2_policy")], list(active))
    if doc.get("max_survivors") != max_survivors:
        miss(None, "max_survivors", doc.get("max_survivors"), max_survivors)
    cells = doc.get("cells", [])
    fc = {(c["world"], c["pressure"]): c for c in cells}
    if len(fc) != len(cells):
        miss(None, "duplicate cells", len(cells), len(fc))
    rc = {(r["world"], r["pressure"]): r for r in recs}
    for k in sorted(set(fc) ^ set(rc)):
        miss(k, "cell present", k in fc, k in rc)
    ak = "|".join(active)
    for k in sorted(set(fc) & set(rc)):
        c, r = fc[k], rc[k]
        for p in PARTS:
            if not _eq((c.get("floor_parts") or {}).get(p), r["floor_parts"][p]):
                miss(k, f"floor_parts.{p}", (c.get("floor_parts") or {}).get(p), r["floor_parts"][p])
        for f in ("floor", "gate_held64"):
            if not _eq(c.get(f), r[f]):
                miss(k, f, c.get(f), r[f])
        for f in ("floor_is_bound", "stage"):
            if c.get(f) != r[f]:
                miss(k, f, c.get(f), r[f])
        if (c.get("pending") or None) != r["pending"]:
            miss(k, "pending", c.get("pending"), r["pending"])
        if r["pending"] == "survivable":
            miss(k, "survivable PENDING in a written file", c.get("verdict"), "the file may not be written")
        cb, rb = c.get("baseline"), r["baseline"]
        if (cb is None) != (rb is None):
            miss(k, "baseline present", cb is not None, rb is not None)
        elif rb is not None:
            for f in ("median", "bytes", "n_runs"):
                if not _eq(cb.get(f), rb[f]):
                    miss(k, f"baseline.{f}", cb.get(f), rb[f])
            for i in (0, 1):
                fv = (cb.get("ci95") or [None, None])[i]
                if not _eq(fv, rb["ci95"][i]):
                    miss(k, f"baseline.ci95[{i}]", fv, rb["ci95"][i])
        for v in VARIANTS:
            cv, rv = (c.get("verdicts") or {}).get(v) or {}, r["verdicts"][v]
            for f in ("verdict", "cull_reason"):
                if cv.get(f) != rv[f]:
                    miss(k, f"verdicts.{v}.{f}", cv.get(f), rv[f])
            if not _eq(cv.get("floor"), rv["floor"]):
                miss(k, f"verdicts.{v}.floor", cv.get("floor"), rv["floor"])
        if (c.get("verdict"), c.get("cull_reason")) != (r["verdicts"][ak]["verdict"], r["verdicts"][ak]["cull_reason"]):
            miss(k, "active verdict", [c.get("verdict"), c.get("cull_reason")],
                 [r["verdicts"][ak]["verdict"], r["verdicts"][ak]["cull_reason"]])
    return mm


def summary(recs: list[dict], active=ACTIVE) -> dict:
    ak = "|".join(active)
    tally: dict[str, int] = {}
    for r in recs:
        tally[r["verdicts"][ak]["verdict"]] = tally.get(r["verdicts"][ak]["verdict"], 0) + 1
    pick = lambda st: [[r["world"], r["pressure"]] for r in recs if r["verdicts"][ak]["verdict"] == st]
    return {"cells": len(recs), "stage2_cells": sum(r["stage"] == 2 for r in recs), "active": ak, "verdicts": tally,
            "survived": pick("SURVIVED"), "held": pick("HELD"),
            "pending_non_survivable": [{"world": r["world"], "pressure": r["pressure"], **r["non_survivable_exact"],
                                        "gate_held64": r["gate_held64"]}
                                       for r in recs if r["pending"] == "non_survivable"],
            "pending_survivable": [[r["world"], r["pressure"]] for r in recs if r["pending"] == "survivable"],
            "not_reached": {v: sum(r["verdicts"][v]["cull_reason"] == "NOT_REACHED" for r in recs) for v in VARIANTS}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default=str(WORLDS_R4))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    doc = json.loads(pathlib.Path(a.worlds).read_text(encoding="utf-8"))
    recs, defects = replay()
    mm = compare(doc, recs)
    s = summary(recs)
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    result = {"kind": "screen_replay", "exp_id": "H-R4-3-screen-replay", "status": "record",
              "verdict": "PASS" if not mm and not defects else "FAIL", "replayed_at": head, "file_commit": doc.get("commit"),
              "rows": [p.relative_to(ROOT).as_posix() for p in (STAGE1, STAGE2, LEARNER)],
              "mismatches": len(mm), "row_defects": len(defects), "summary": s,
              "mismatch_detail": mm[:50], "defect_detail": defects[:50]}
    print(json.dumps({k: v for k, v in result.items() if k not in ("mismatch_detail", "defect_detail")}, indent=1))
    for x in mm[:20]:
        print("MISMATCH", x)
    for x in defects[:20]:
        print("DEFECT", x)
    if a.write:
        from primordial.fabric.rows import RowWriter
        with RowWriter(OUT, "H-R4-3-screen-replay", commit_every_s=10**9) as w:
            w.write(result)
        print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
