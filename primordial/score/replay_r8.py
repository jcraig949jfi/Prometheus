"""H R8 SCIENCE (prompts_r8/H.md items 1-2): independent replay and rule consistency on live r8 results.

The judge re-derives each verdict from the COMMITTED rows, never from the experimenter's summary, and compares.
Disagreement is reported as a DISPUTE and preserved; nothing here writes rows or edits another lane's record.

Rule consistency (item 2), per predicate:
  pinned       refs/pm/pred/<id> exists on origin and equals the code_sha cited in the bus post
  predates     the bus PREDICATE post ts < the earliest committed row ts
  evidence_n   the predicate's declared sample passes EVIDENCE_N_v1 (VERDICT) or it is OBSERVATION (no PASS/FAIL)
  balance      the committed run rows realise the declared sample: per arm, 4 families x run seeds 0..7, no
               duplicate (arm, family, run_seed) row (a checkpoint resume can duplicate), no missing one

C-R8-AP-01 replay is INDEPENDENT of C's harness where it can be: the world stream (splitmix64 + xorshift64) is
re-implemented here in pure Python integers from signal.py's definition, the brain is decoded from the stored
top1 bytes by the predicate TEXT (6 pair tables T_ij[4x4] over base-4 digits, s mod 256 >> 5; act = cb[heard] % 8),
and fitness is an explicit tick loop -- no histogram, no GraphBLAS, no import of C's module. Shared with C (stated,
not hidden): the predicate text itself, the seed lists, and the scramble permutation construction (argsort of
PCG64 uniforms), which the predicate does not define and which is therefore re-derived from C's code reading.

    python -m primordial.score.replay_r8 c-ap01 ROWS.jsonl [--ref origin/<branch>] [--out REPORT.json]
    python -m primordial.score.replay_r8 d-r8-1 ROWS.jsonl [--ref ...] [--out ...]
    python -m primordial.score.replay_r8 route-b primordial/ledger/qd/r8_route_b.json --no-bus [--out ...]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

import numpy as np

M64 = (1 << 64) - 1
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8


# ------------------------------------------------------------------ rows

def load_rows(path: str, ref: str | None = None) -> list[dict]:
    if ref:
        txt = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True).stdout
    else:
        txt = open(path, encoding="utf-8").read()
    return [json.loads(l) for l in txt.splitlines() if l.strip()]


def balance(runs: list[dict], arms) -> dict:
    out = {}
    for arm in arms:
        keys = [(r["family"], r["run_seed"]) for r in runs if r.get("arm") == arm]
        want = {(f, s) for f in FAMILIES for s in range(RUNS_PER_FAMILY)}
        dup = sorted({k for k in keys if keys.count(k) > 1})
        out[arm] = {"rows": len(keys), "missing": sorted(want - set(keys)), "extra": sorted(set(keys) - want),
                    "duplicates": dup, "balanced_32_4_8": set(keys) == want and not dup and len(keys) == 32}
    return out


# ------------------------------------------------------------------ independent world stream (pure Python ints)

def _splitmix(x: int) -> int:
    z = (x + 0x9E3779B97F4A7C15) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


def r_stream_py(seeds, T: int) -> np.ndarray:
    out = np.empty((T, len(seeds)), np.int64)
    for j, s in enumerate(seeds):
        st = _splitmix(int(s) & M64) or 1
        for t in range(T):
            st ^= (st << 13) & M64
            st ^= st >> 7
            st ^= (st << 17) & M64
            out[t, j] = (st >> 24) & 255
    return out


# ------------------------------------------------------------------ C-R8-AP-01

C_PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
C_T, C_RATE, C_TAG, C_P3_MIN = 64, 16, 8101, 17
C_TRAIN = list(range(128))
C_HELD = [10_000_000 + i for i in range(256)]
C_ARM_INDEX = {"cell": 0, "control": 1, "null": 2}


def c_encoder(g: bytes) -> list[int]:
    """sym[R] from the predicate text: s = sum_{i<j} T_ij[q_i, q_j] mod 256, sym = s >> 5, q0 = R >> 6 (MSD)."""
    tabs = [g[16 * k:16 * (k + 1)] for k in range(6)]
    sym = []
    for R in range(256):
        q = ((R >> 6) & 3, (R >> 4) & 3, (R >> 2) & 3, R & 3)
        s = sum(tabs[k][4 * q[i] + q[j]] for k, (i, j) in enumerate(C_PAIRS))
        sym.append((s % 256) >> 5)
    return sym


def c_tick_yield(g: bytes, Rs: np.ndarray, silent: bool, perm: np.ndarray | None = None) -> tuple[int, int]:
    sym = c_encoder(g)
    cb = [b % 8 for b in g[96:104]]
    right = 0
    T, E = Rs.shape
    for e in range(E):
        for t in range(T):
            R = int(Rs[t, e])
            h = 0 if silent else sym[R]
            if perm is not None:
                h = int(perm[e, h])
            right += cb[h] == (R >> 5)
    return right, T * E


def c_floor(Rs: np.ndarray) -> float:
    counts = np.bincount((Rs >> 5).ravel(), minlength=8)
    return float(counts.max() / Rs.size)


def c_perm(family: int, rs: int, arm: str, E: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64([C_TAG, family, rs, C_ARM_INDEX[arm], 99]))
    return np.argsort(rng.random((E, 8)), axis=1)


def c_score(held, lowers, control, floor) -> dict:
    q = np.percentile(held, [25, 50, 75])
    qc = np.percentile(control, [25, 50, 75])
    bar = float(qc[1] - 0.5 * (qc[2] - qc[0]))
    n_low = int(sum(lowers))
    return {"median": float(q[1]), "iqr": float(q[2] - q[0]), "control_median": float(qc[1]),
            "control_iqr": float(qc[2] - qc[0]), "bar": bar, "floor": floor, "P1_parity": bool(q[1] >= bar),
            "P2_above_floor": bool(q[1] > floor), "P3_scramble_lowers_runs": n_low,
            "P3_uses_channel": n_low >= C_P3_MIN, "n": len(held)}


def replay_c_ap01(rows: list[dict]) -> dict:
    Rh = r_stream_py(C_HELD, C_T)
    floor = c_floor(Rh)
    ref = next((r for r in rows if r.get("kind") == "reference"), {})
    runs = [r for r in rows if r.get("kind") == "run"]
    per_run, mism = [], []
    held = {"cell": [], "control": [], "null": []}
    lowers = {"cell": [], "null": []}
    oracle_ok = {"cell": True, "control": True, "null": True}
    for r in runs:
        arm, g = r["arm"], bytes.fromhex(r["top1_hex"])
        silent = arm == "null"
        right, n = c_tick_yield(g, Rh, silent)
        h = right / n
        rs_right, _ = c_tick_yield(g, Rh, silent, c_perm(r["family"], r["run_seed"], arm, len(C_HELD)))
        scr = rs_right / n
        d = {"arm": arm, "family": r["family"], "run_seed": r["run_seed"], "held_replay": h,
             "held_rows": r["held_yield_top1"], "scr_replay": scr, "scr_rows": r["held_scrambled_top1"],
             "lowers_replay": scr < h, "lowers_rows": r["scramble_lowers"]}
        if (h != r["held_yield_top1"] or scr != r["held_scrambled_top1"] or (scr < h) != r["scramble_lowers"]):
            mism.append(d)
        per_run.append(d)
        held[arm].append(h)
        if arm != "control":
            lowers[arm].append(scr < h)
        ok = r.get("recount_mismatched_top16") == 0 and r.get("offers_mismatched") == 0
        if "oracles" in r:
            ok = ok and bool(r["oracles"].get("ok"))
        oracle_ok[arm] = oracle_ok[arm] and ok
    out = {"predicate_id": "C-R8-AP-01", "floor_replay": floor, "floor_rows": ref.get("floor_held"),
           "floor_agrees": floor == ref.get("floor_held"), "runs_replayed": len(per_run),
           "value_mismatches": mism, "balance": balance(runs, ("control", "null", "cell")),
           "binding_precheck_rows": ref.get("binding_precheck")}
    nc = None
    if len(held["null"]) == 32 and len(held["control"]) == 32:
        sc = c_score(held["null"], lowers["null"], held["control"], floor)
        nc = {"null_predicate": "PASS" if (sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_channel"]
                                           and oracle_ok["null"] and oracle_ok["control"]) else "FAIL", **sc,
              # a silent arm's action is constant, so its held yield is at most the best constant action = FLOOR:
              # P2 (median > FLOOR, strict) is unreachable by construction, whatever the search does.
              "null_can_pass_by_construction": bool(max(held["null"]) > floor)}
    out["null_check_replay"] = nc
    rows_nc = next((r for r in rows if r.get("kind") == "null_check"), None)
    summ = next((r for r in rows if r.get("kind") == "summary"), None)
    out["null_check_rows"] = rows_nc and {k: rows_nc.get(k) for k in ("null_predicate", "median", "iqr",
                                                                     "P3_scramble_lowers_runs")}
    if len(held["cell"]):
        sc = c_score(held["cell"], lowers["cell"], held["control"], floor)
        full = all(out["balance"][a]["balanced_32_4_8"] for a in ("cell", "control"))
        ok_all = oracle_ok["cell"] and oracle_ok["control"]
        vac = sc["iqr"] == 0 and sc["control_iqr"] == 0 and sc["median"] == sc["control_median"]
        prim = "INDETERMINATE" if not (ok_all and full) else "VACUOUS" if vac else \
            ("PASS" if sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_channel"] else "FAIL")
        out["cell_replay"] = {**sc, "vacuous": vac, "oracle_clean": ok_all, "full": full, "primary": prim}
    if summ:
        out["summary_rows"] = {k: summ.get(k) for k in ("primary", "median", "iqr", "control_median", "control_iqr",
                                                        "bar", "floor", "P1_parity", "P2_above_floor",
                                                        "P3_scramble_lowers_runs", "vacuous", "oracle_clean",
                                                        "reasons")}
        if "cell_replay" in out:
            keys = ("primary", "median", "iqr", "control_median", "control_iqr", "bar", "P1_parity",
                    "P2_above_floor", "P3_scramble_lowers_runs", "vacuous")
            out["summary_disagreements"] = {k: {"rows": summ.get(k), "replay": out["cell_replay"][k]}
                                            for k in keys if summ.get(k) != out["cell_replay"][k]}
            out["verdict_agrees"] = summ.get("primary") == out["cell_replay"]["primary"] and not mism
        else:
            out["verdict_agrees"] = summ.get("primary") in ("INELIGIBLE", "PREDICATE_PASSES_PLANTED_NULL") and \
                (nc is None or (nc["null_predicate"] == "PASS") == (summ.get("primary") ==
                                                                   "PREDICATE_PASSES_PLANTED_NULL"))
    return out


def c_resolving_power(rows: list[dict], drops=(0.05, 0.10, 0.15, 0.20), draws=2000, seed=0) -> dict:
    """POST HOC, descriptive (not preregistered): can P1 fail for a degradation of the pressure's own size?
    A planted cell arm = a bootstrap draw of the CONTROL held values x (1 - d); P1 fail rate = share of draws whose
    median < the control draw's median - 0.5 IQR. Also: rank tests cell vs control, and the largest relative median
    drop P1 accepts on the observed control."""
    from scipy import stats
    runs = [r for r in rows if r.get("kind") == "run"]
    ref = next((r for r in rows if r.get("kind") == "reference"), {})
    c = np.array([r["held_yield_top1"] for r in runs if r["arm"] == "cell"])
    k = np.array([r["held_yield_top1"] for r in runs if r["arm"] == "control"])
    rng = np.random.default_rng(seed)
    fail = {}
    for d in drops:
        n = 0
        for _ in range(draws):
            kk, cc = rng.choice(k, len(k)), rng.choice(k, len(k)) * (1 - d)
            n += np.median(cc) < np.median(kk) - 0.5 * (np.percentile(kk, 75) - np.percentile(kk, 25))
        fail[str(d)] = n / draws
    bar = np.median(k) - 0.5 * (np.percentile(k, 75) - np.percentile(k, 25))
    return {"post_hoc": True, "pressure_direct_magnitude_train_flipped_tick_share": ref.get("train_flipped_tick_share"),
            "hand_code_yield_loss_under_pressure": 1 - (ref.get("hand_yield") or {}).get("train_corrupt", float("nan")),
            "median_cell_minus_control": float(np.median(c) - np.median(k)),
            "mannwhitney_p": float(stats.mannwhitneyu(c, k).pvalue), "ks_p": float(stats.ks_2samp(c, k).pvalue),
            "largest_relative_median_drop_P1_accepts": float(1 - bar / np.median(k)),
            "P1_fail_rate_for_planted_relative_drop": fail, "draws": draws, "seed": seed}


# ------------------------------------------------------------------ rule consistency (item 2)

def rule_consistency(predicate_id: str, rows: list[dict], r=None, repo=".") -> dict:
    """Pinned, predates, EVIDENCE_N_v1 on the declared sample, OBSERVATION carries no PASS/FAIL."""
    import re
    from primordial.bus import bus
    from primordial.ops.predicate_ref import cited_code_sha
    from primordial.score import evidence_n as EN
    r = r or bus.conn()
    pat = re.compile(rf"PREDICATE {re.escape(predicate_id)}(?![\w.-])")
    posts = sorted((float(f.get("ts") or 0), i, f.get("body") or "") for i, f in r.xrange(bus.SWARM)
                   if f.get("kind") == "claim" and pat.match(f.get("subject") or ""))
    out = {"predicate_id": predicate_id, "posts": len(posts)}
    if not posts:
        return {**out, "ok": False, "failures": ["PREDICATE_MISSING"]}
    ts, eid, body = posts[0]
    sha = cited_code_sha(body)
    ev = None
    for line in body.splitlines():
        if line.startswith("evidence="):
            try:
                ev = json.loads(line[len("evidence="):])
            except ValueError:
                ev = None
    pin = subprocess.run(["git", "-C", repo, "ls-remote", "origin", f"refs/pm/pred/{predicate_id}"],
                         capture_output=True, text=True).stdout.split()
    row_ts = [float(x["ts"]) for x in rows if isinstance(x.get("ts"), (int, float))]
    fails = []
    if not sha:
        fails.append("NO_CODE_SHA_CITED")
    if not pin or pin[0] != sha:
        fails.append(f"PIN_MISMATCH ref={pin[:1]} cited={sha}")
    if not row_ts:
        fails.append("RUN_START_UNKNOWN")
    elif ts >= min(row_ts):
        fails.append(f"PREDICATE_AFTER_RUN {ts} >= {min(row_ts)}")
    if ev is None:
        fails.append("NO_EVIDENCE_LINE")
    else:
        req = EN.requirement(ev.get("experiment_class"), ev.get("sample"), ev.get("evidence_class"))
        if req:
            fails.append(f"SAMPLE_RULE_MISMATCH {req.get('failures')}")
    ec = (ev or {}).get("evidence_class")
    words = sorted({str(x.get(k)) for x in rows if x.get("kind") == "summary"
                    for k in ("status", "primary", "decision", "verdict")} & set(EN.VERDICT_WORDS))
    if ec == "OBSERVATION" and words:
        fails.append(f"OBSERVATION_CARRIES_VERDICT {words}")
    wrong = sorted({x.get("predicate_id") for x in rows if x.get("predicate_id") not in (None, predicate_id)})
    if wrong:
        fails.append(f"ROWS_CITE_OTHER_PREDICATE {wrong}")
    return {**out, "event_id": eid, "predicate_ts": ts, "first_row_ts": min(row_ts) if row_ts else None,
            "code_sha": sha, "pin": pin[:1], "evidence": ev, "ok": not fails, "failures": fails}


# ------------------------------------------------------------------ D-R8-1 (re-derivation from rows only)

D_CELLS = (("linear", 0), ("tt_feat", 3), ("tt_feat", 2), ("tt_feat", 1), ("tt_digits", 3), ("tt_digits", 2),
           ("tt_digits", 1))
D_WORLDS = (4, 1, 3)


def d_oracles_ok(x: dict) -> bool:
    w, wl = x.get("world_oracle_honest") or {}, x.get("world_oracle_skip_lin") or {}
    b, bc = x.get("brain_oracle_honest") or {}, x.get("brain_oracle_cheat") or {}
    return bool(w.get("elites_failing") == 0 and wl.get("elites_failing", 0) >= 14
                and b.get("mismatched_rows") == 0 and bc.get("elites_mismatching", 0) >= 14)


def _d_key(k: str):
    fam, rest = k.split("@")
    rk, w = rest.split("|w")
    return fam, int(rk), int(w)


def replay_d_r8_1(rows: list[dict]) -> dict:
    """Re-derives I1, the binding controls and the PARITY decision from the committed run rows. The rows carry no
    elite bytes, so held64 values themselves cannot be re-scored: this replay checks the DECISION, not the values."""
    runs = [x for x in rows if x.get("kind") == "run"]
    keys = [(x["family"], int(x["rank"]), int(x["gen_seed"]), int(x["run_seed"])) for x in runs]
    want = {(f, rk, w, s) for f, rk in D_CELLS for w in D_WORLDS for s in range(8)}
    bal = {"rows": len(keys), "missing": len(want - set(keys)), "extra": sorted(set(keys) - want),
           "duplicates": sorted({k for k in keys if keys.count(k) > 1}), "complete_168": set(keys) == want}
    by = {}
    for x in runs:
        by.setdefault((x["family"], int(x["rank"]), int(x["gen_seed"])), []).append(float(x["held64_per_seed"]))
    med = {k: float(np.median(v)) for k, v in by.items()}
    i1w = {}
    for w in D_WORLDS:
        c = [med.get(("linear", 0, w)), med.get(("tt_feat", 3, w)), med.get(("tt_digits", 3, w))]
        i1w[str(w)] = bool(None not in c and c[0] > c[1] > c[2])
    i1_ok = sum(i1w.values()) >= 2
    orows = [x for x in runs if "world_oracle_honest" in x]
    bad = sorted({(x["family"], int(x["rank"]), int(x["gen_seed"])) for x in orows if not d_oracles_ok(x)})
    controls_ok = not bad and len(orows) == 21 and all(int(x["run_seed"]) == 0 for x in orows)
    rev = hold = 0
    per = {}
    for w in D_WORLDS:
        lin, m = med.get(("linear", 0, w)), med.get(("tt_feat", 1, w))
        if lin is None or m is None:
            per[str(w)] = None
            continue
        per[str(w)] = {"linear": lin, "tt_feat@1": m, "margin": m - lin}
        rev += m >= lin
        hold += lin > m
    complete = bal["complete_168"] and not bal["duplicates"]
    decision = "INDETERMINATE" if not (i1_ok and controls_ok and complete) else \
        "PARITY_REVERSES" if rev >= 2 else "PARITY_HOLDS" if hold >= 2 else "MIXED"
    out = {"predicate_id": "D-R8-1-byte-parity-rerank", "balance": bal, "i1_per_world": i1w, "i1_ok": i1_ok,
           "controls_ok": controls_ok, "oracle_rows": len(orows), "failing_oracle_cells": bad,
           "per_world": per, "worlds_matched_ge_linear": rev, "worlds_linear_ahead": hold,
           "decision_replay": decision, "values_rescored": False,
           "replay_power_limit": "rows store no elite bytes: held64/train values are taken as recorded",
           "median_grid": {f"{f}@{rk}|w{w}": v for (f, rk, w), v in sorted(med.items())}}
    summ = next((x for x in rows if x.get("kind") == "summary"), None)
    if summ:
        checks, st = summ.get("checks") or {}, summ.get("stats") or {}
        cmp = (("decision", summ.get("decision"), decision),
               ("i1_ok", (checks.get("I1") or {}).get("ranking_at_rank3"), i1_ok),
               ("controls_ok", checks.get("controls_ok"), controls_ok),
               ("worlds_matched_ge_linear", st.get("worlds_matched_ge_linear"), rev),
               ("worlds_linear_ahead", st.get("worlds_linear_ahead"), hold))
        out["decision_rows"] = summ.get("decision")
        out["summary_disagreements"] = {k: {"rows": a, "replay": b} for k, a, b in cmp if a != b}
        grid = (summ.get("reported_not_judged") or {}).get("grid_median_held64") or {}
        out["grid_disagreements"] = {k: {"rows": v.get("held64"), "replay": med.get(_d_key(k))}
                                     for k, v in grid.items() if v.get("held64") != med.get(_d_key(k))}
        out["verdict_agrees"] = (summ.get("decision") == decision and not out["summary_disagreements"]
                                 and not out["grid_disagreements"])
    return out


# ------------------------------------------------------------------ G Route B (SURVIVAL_IMPOSSIBLE bound)

def replay_route_b(doc: dict, rows_dir: str = "primordial/ledger/rows/G") -> dict:
    """Re-derives G's r8_route_b.json claim from the committed R16 rows, aimed at the claim itself:
    b = max over the run floor parts (read here, not via suite.floor_of_parts), gate from the suite row;
    min_x f(x) = b (four_policy) / max(b, gate) (gate_in); SURVIVAL_IMPOSSIBLE iff ci_lo <= min_x f for every variant.
    ci_lo is re-computed from held64_by_run under all 24 family orders x 4 bootstrap seeds (the pooled CI is known to
    be order-sensitive), so the verdict is judged against the WORST ci_lo, not the one recorded; no learner row for the
    cell may exist anywhere under rows_dir."""
    import ast
    import glob
    import itertools
    from primordial.metric.ci import median_ci
    allrows = []
    for f in sorted(glob.glob(f"{rows_dir}/*.jsonl")):
        for line in open(f, encoding="utf-8"):
            if line.strip():
                try:
                    allrows.append(json.loads(line))
                except ValueError:
                    pass
    out = {"cells": [], "disagreements": []}
    for c in doc["cells"]:
        key = (int(c["gen_seed"]), c["pressure"])
        fl = [x for x in allrows if x.get("kind") == "floor_suite_r16" and (int(x["gen_seed"]), x["pressure"]) == key]
        ba = [x for x in allrows if x.get("kind") == "baseline_r16" and (int(x["gen_seed"]), x["pressure"]) == key]
        lr = [x for x in allrows if x.get("kind") == "floor_invariant_r16" and
              (int(x.get("gen_seed", -1)), x.get("pressure")) == key]
        fl_vals = {json.dumps(x["floor_parts"], sort_keys=True) for x in fl}
        rec = {"world": c["world"], "pressure": c["pressure"], "suite_rows": len(fl), "suite_rows_distinct": len(fl_vals),
               "baseline_rows": len(ba), "learner_rows": len(lr)}
        if len(fl_vals) != 1 or len(ba) != 1:
            rec["status"] = "UNREPLAYABLE"
            out["cells"].append(rec)
            out["disagreements"].append(rec)
            continue
        parts = fl[0]["floor_parts"]
        b = max(v for v in parts.values() if v is not None)
        gate = float(fl[0]["gate_held64"])
        hb = ba[0]["held64_by_run"]
        hb = ast.literal_eval(hb) if isinstance(hb, str) else hb
        fams = sorted({int(k.split("|")[0]) for k in hb})
        per_fam = {f: sorted(int(k.split("|")[1]) for k in hb if int(k.split("|")[0]) == f) for f in fams}
        balanced = len(fams) == 4 and all(v == list(range(8)) for v in per_fam.values())
        los = []
        for order in itertools.permutations(fams):
            xs = [hb[f"{f}|{s}"] for f in order for s in range(8)]
            for seed in (20260914, 1, 2, 3):
                los.append(median_ci(xs, seed=seed)[0])
        canon = [hb[f"{f}|{s}"] for f in (4200, 2101, 3303, 5501) for s in range(8)]
        lo_canon = median_ci(canon)[0]
        min_f = {"four_policy": b, "gate_in": max(b, gate)}
        worst = max(los)
        imp = all(worst <= v for v in min_f.values())
        rec.update(b=b, gate=gate, ci_lo_recorded=float(ba[0]["ci95"][0]), ci_lo_canonical_replay=lo_canon,
                   ci_lo_min_over_orders_seeds=min(los), ci_lo_max_over_orders_seeds=worst, balanced_32_4_8=balanced,
                   min_over_learner_floor=min_f, smallest_margin_vs_worst_ci_lo=min(min_f.values()) - worst,
                   status="SURVIVAL_IMPOSSIBLE" if imp and balanced and not lr else
                   ("NOT_PENDING" if lr else "UNRESOLVED"))
        if (rec["status"] != c["status"] or lo_canon != rec["ci_lo_recorded"] or b != c["b_floor_bound"]
                or gate != c["gate_held64"]):
            out["disagreements"].append({k: rec[k] for k in ("world", "status", "b", "gate", "ci_lo_recorded",
                                                            "ci_lo_canonical_replay")} | {"g_status": c["status"]})
        out["cells"].append(rec)
    out["verdict_agrees"] = not out["disagreements"]
    return out


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["c-ap01", "d-r8-1", "route-b"])
    ap.add_argument("rows")
    ap.add_argument("--ref")
    ap.add_argument("--out")
    ap.add_argument("--no-bus", action="store_true")
    a = ap.parse_args(argv)
    if a.which == "route-b":
        doc = json.loads(subprocess.run(["git", "show", f"{a.ref}:{a.rows}"], capture_output=True, text=True,
                                        check=True).stdout) if a.ref else json.load(open(a.rows, encoding="utf-8"))
        rows, rep = [], replay_route_b(doc)
        rep["predicate_id"] = None
    else:
        rows = load_rows(a.rows, a.ref)
        rep = {"c-ap01": replay_c_ap01, "d-r8-1": replay_d_r8_1}[a.which](rows)
    if not a.no_bus and rep["predicate_id"]:
        rep["rule_consistency"] = rule_consistency(rep["predicate_id"], rows)
    rep["rows_path"], rep["rows_ref"], rep["rows_count"] = a.rows, a.ref, len(rows)
    txt = json.dumps(rep, indent=1, default=str)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt + "\n")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
