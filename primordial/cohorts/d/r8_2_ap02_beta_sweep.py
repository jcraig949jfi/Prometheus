"""D-R8-2 (PC 1789518268676-0; ANOM-1789517546515-0; SWARM_R8 s9): the BETA sweep on C-R7-AP-02's cell
codebook / nk_stub / byte_charge / falkordb_cypher / metered_stream. Two round-7 discriminators returned MIXED with no
mechanism: D-R7-6 (the charge is paid, median 3.65% of what the winner earns, winner smaller in 22/32) and D-R7-7 (it
costs <1% of train fitness and nothing on held-out). The question: at what byte charge does held-out parity BREAK, or
does parity survive a charge that demonstrably binds?

Seen before this predicate: C's module and committed rows (sha256 b13bd4fb...), D-R7-6 / D-R7-7 receipts and their
descriptive numbers at C's BETA only. No value at any other BETA exists.

HARNESS: C's module is IMPORTED AND CALLED UNCHANGED (primordial.cohorts.c.r7_ap02_codebook_nk_bytecharge_falkordb_metered:
run, oracles, score, beta_of, Landscapes). BETA is the ONLY thing that varies -- C's run() already takes it as a
parameter. Substrate: lane D's own Redis 8 + FalkorDB :6393 (same image and module version as C's :6392), graph
d_r8_2_beta, so nothing touches C's keys. Streams are C's: GA PCG64([family, rs, arm_i, 7201]), sampler
[family + 1, rs, arm_i, 7201], cell arm_i 0, control arm_i 1. The cell arm therefore runs the SAME streams at every BETA:
every comparison across BETA is paired within (family, run seed).

POINTS (fixed): BASE = C's BETA = floor(0.01 * RANDOM_MEAN) * 8 = 169144 (recomputed in-job by C's beta_of and required
to equal 169144). BETA = m * BASE, m in MULTS = (0, 1, 4, 16, 64). The control carries no charge and is BETA-independent:
it runs ONCE. 32 runs per point: families (4200, 2101, 3303, 5501) x run seeds 0..7 (runs_total 32, rng_family_count 4,
runs_per_family 8). C's GENS 50, batch 128, reader top1_train. 6 x 32 = 192 runs.
Why these points: m = 1 is C's cell (binding replication); m = 0 is the null arm (cell streams, no charge: selection is
identical to the control's, only the streams differ); 4 and 16 bracket the range; 64 puts one functional byte at
64% of the whole train NK sum, which is past any NK difference two genomes can plausibly have, i.e. effectively
bytes-first selection -- the saturated end of the axis. int32 selection fitness cannot overflow at 64x (>= -70M).

EXECUTION ORDER AND STOPPING RULE (fixed): control -> m1 -> [I1 check] -> m0 -> m4 -> m16 -> m64. No other point is
ever added in this job and no point is re-run; a finer bracket, if the curve suggests one, is a NEW preregistered
experiment (a PC), never an extension. EARLY STOP (summary INDETERMINATE, remaining points not run) if I1 fails after m1
or if any point's oracles are not clean. If the round clock ends the job, completed points are reported, the decision is
INDETERMINATE, and the unrun points get WHY_NOT_RUN.

PRIMARY RESPONSE VARIABLES, per point (all from C's own row fields):
  beta                        m * BASE
  held                        held_per_landscape_top1 (C's readout); median + IQR over 32 runs
  parity(m)                   C's own primary: median held(cell@m) >= median held(control) - 0.5 * IQR(control)
  genome bytes                top1 functional_bytes (C: 2 + ceil(code_len / 8); stored length is always 8)
  fraction of possible charge actually paid
                              avoidable_paid = (fb - FB_MIN) / (FB_MAX - FB_MIN), FB_MIN 3, FB_MAX 6: the share of the
                              charge the winner could have avoided that it still pays; also charge_share (D-R7-6's
                              beta * fb / earned train NK) and fb / FB_MAX
  train fitness               train_nk_per_landscape_top1 (raw NK) and train_fit_top1 (net of the charge)
  verdict                     parity(m) as PASS / FAIL (per point, C's rule, oracle-clean 32/4/8 only)

BINDING: bound(m) = median fb(m) <= median fb(m0) - 1 AND fb(m) < fb(m0) in >= 24 of the 32 paired streams.

SWEEP DECISION (fixed before any value):
  INDETERMINATE            I1 fails, any oracle fails, any point incomplete, OR the NULL ARM fails: parity(0) is False
                           (the rule's bar cannot tell two uncharged stream sets apart, so no break is readable)
  CHARGE_NEVER_BINDS       not bound(64): even bytes-first selection does not shrink the winner; the sweep cannot test
                           size against held-out on this cell
  PARITY_BREAKS            m* = the smallest m in (4, 16, 64) with parity False, and bound(m*): the charge reaches
                           held-out; beta_break = m* * BASE (bracketed below by the largest passing m under m*)
  PARITY_SURVIVES_BINDING  parity True at every m in (1, 4, 16, 64) and bound(64): the charge shrinks the winner and
                           held-out parity does not move -- program size carries no held-out cost in this cell
  MIXED                    otherwise (e.g. parity fails only where the charge does not bind)
  Non-monotone parity (a FAIL followed by a PASS at larger m) is REPORTED with the decision, never used to relabel it.

I1 (BINDING REPLICATION of C at m = 1): every one of the 64 runs (control, and cell at m1) reproduces C's committed row
exactly on top1_sha256, train_fit_top1 and held_per_landscape_top1; and the recomputed BETA equals 169144. D's harness on
D's substrate must BE C's experiment at C's point, or the curve does not speak to AP-02.
ORACLES: C's own, unchanged -- every run: top-16 recount exact and (first stream of each point) every offer exact; family
4200 run seed 0 of every point: world / k3 / brain / meter / charge (C's oracles()).

NOT CLAIMED: clause A; the anti-prior arm or any predictor statement; any statement about byte_charge on another cell.
The substrate is part of the cell and is kept; a numpy variant would answer a neighbouring question and is not run.

    worker job = primordial.cohorts.d.r8_2_ap02_beta_sweep:job
    dev (no rows) = python -m primordial.cohorts.d.r8_2_ap02_beta_sweep dev
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time

import numpy as np

from primordial.cohorts.c import r7_ap02_codebook_nk_bytecharge_falkordb_metered as CA

EXP = "D-R8-2-ap02-beta-sweep"
PREDICATE_ID = EXP
PC = "1789518268676-0"
ANOMALY = "1789517546515-0"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
SRC_ROWS = "primordial/ledger/rows/C/C-R7-AP-02-codebook-nk-bytecharge-falkordb-metered.jsonl"
SRC_SHA256 = "b13bd4fbbe9e7e1df105d4336814abd7ba1937d0367a653101975cdc74154ee9"
PORT, GRAPH = 6393, "d_r8_2_beta"
BASE_BETA = 169144
MULTS = (0, 1, 4, 16, 64)
ORDER = ("control", 1, 0, 4, 16, 64)
FAMILIES, RUNS_PER_FAMILY = CA.FAMILIES, CA.RUNS_PER_FAMILY
FB_MIN, FB_MAX = 3, 6
BIND_PAIRS = 24
ARM_I = {"cell": 0, "control": 1}


# ------------------------------------------------------------------ pure pieces (tested)

def key(point) -> str:
    return point if point == "control" else f"m{int(point)}"


def todo() -> list[tuple]:
    return [(p, f, rs) for p in ORDER for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]


def fb(row: dict) -> int:
    return int(row["top1_program"]["functional_bytes"])


def derived(row: dict, beta: int) -> dict:
    earned = float(row["train_nk_per_landscape_top1"]) * len(CA.TRAIN_SEEDS)
    b = fb(row)
    return {"functional_bytes": b, "avoidable_paid": (b - FB_MIN) / (FB_MAX - FB_MIN), "fb_over_max": b / FB_MAX,
            "charge_share": (beta * b / earned) if earned else float("nan"), "charge_paid": int(beta * b)}


def bound(rows_m: dict, rows_0: dict) -> dict:
    """rows_*: {(family, rs): row}. -> {"median_fb", "median_fb_m0", "smaller_pairs", "bound"}."""
    ks = sorted(set(rows_m) & set(rows_0))
    mm, m0 = float(np.median([fb(rows_m[k]) for k in ks])), float(np.median([fb(rows_0[k]) for k in ks]))
    smaller = int(sum(fb(rows_m[k]) < fb(rows_0[k]) for k in ks))
    return {"median_fb": mm, "median_fb_m0": m0, "smaller_pairs": smaller, "pairs": len(ks),
            "bound": bool(len(ks) == 32 and mm <= m0 - 1 and smaller >= BIND_PAIRS)}


def parity(rows_m: dict, rows_ctrl: dict) -> dict:
    return CA.score([float(v["held_per_landscape_top1"]) for v in rows_m.values()],
                    [float(v["held_per_landscape_top1"]) for v in rows_ctrl.values()])


def decide(i1_ok: bool, oracles_ok: bool, pts: dict) -> tuple[str, dict]:
    """pts: {"control": {(f, rs): row}, "m0": {...}, ...}."""
    complete = all(len(pts.get(key(p), {})) == 32 for p in ORDER)
    stats: dict = {"complete": complete}
    if not complete:
        return "INDETERMINATE", stats
    par = {m: parity(pts[key(m)], pts["control"]) for m in MULTS}
    bnd = {m: bound(pts[key(m)], pts["m0"]) for m in MULTS if m != 0}
    stats.update({"parity": {key(m): par[m]["parity"] for m in MULTS}, "bound": {key(m): bnd[m]["bound"] for m in bnd},
                  "score": {key(m): par[m] for m in MULTS}, "binding": {key(m): bnd[m] for m in bnd}})
    seq = [par[m]["parity"] for m in (1, 4, 16, 64)]
    stats["non_monotone"] = any((not a) and b for a, b in zip(seq, seq[1:]))
    if not (i1_ok and oracles_ok):
        return "INDETERMINATE", stats
    if not par[0]["parity"]:
        stats["null_arm"] = "FAILED"
        return "INDETERMINATE", stats
    if not bnd[64]["bound"]:
        return "CHARGE_NEVER_BINDS", stats
    fails = [m for m in (4, 16, 64) if not par[m]["parity"]]
    if fails:
        m = fails[0]
        if bnd[m]["bound"]:
            below = [x for x in (1, 4, 16) if x < m and par[x]["parity"]]
            stats.update({"m_break": m, "beta_break": m * BASE_BETA,
                          "beta_last_pass_below": (max(below) * BASE_BETA) if below else None})
            return "PARITY_BREAKS", stats
        return "MIXED", stats
    if all(seq):
        return "PARITY_SURVIVES_BINDING", stats
    return "MIXED", stats


def verdict_of(stats: dict, pk: str, clean: bool):
    """Per-point PASS/FAIL under C's rule; None for the control, an incomplete sweep, or unclean oracles / I1."""
    if pk == "control" or not clean or pk not in stats.get("parity", {}):
        return None
    return "PASS" if stats["parity"][pk] else "FAIL"


def c_reference(text: str) -> dict:
    """C's committed runs of its completed job -> {(arm, family, rs): row}."""
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    return {(x["arm"], int(x["family"]), int(x["run_seed"])): x for x in rows
            if x.get("kind") == "run" and x.get("arm") in ARM_I and int(x.get("genome_bytes", 0)) == CA.GLEN}


def i1_check(pts: dict, ref: dict, beta: int) -> dict:
    fields = ("top1_sha256", "train_fit_top1", "held_per_landscape_top1")
    bad = []
    for arm, pk in (("control", "control"), ("cell", "m1")):
        for (f, rs), row in pts.get(pk, {}).items():
            c = ref.get((arm, f, rs))
            if c is None or any(row[x] != c[x] for x in fields):
                bad.append([arm, f, rs])
    n = len(pts.get("control", {})) + len(pts.get("m1", {}))
    return {"runs_compared": n, "mismatched": bad, "beta_recomputed": beta,
            "ok": bool(n == 64 and not bad and beta == BASE_BETA)}


# ------------------------------------------------------------------ job

def _pts(st) -> dict:
    return {p: {tuple(int(x) for x in k.split("|")): v for k, v in d.items()} for p, d in st["pts"].items()}


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID, gens: int = CA.GENS,
        port: int = PORT, order=ORDER, families=FAMILIES, runs_per_family: int = RUNS_PER_FAMILY):
    import redis
    from falkordb import FalkorDB
    t0 = time.perf_counter()
    r = redis.Redis(host="127.0.0.1", port=port)
    graph = FalkorDB(host="127.0.0.1", port=port, socket_timeout=300).select_graph(GRAPH)
    train, held = CA.Landscapes(CA.TRAIN_SEEDS), CA.Landscapes(CA.HELD_SEEDS)
    work = [(p, f, rs) for p in order for f in families for rs in range(runs_per_family)]
    st = ctx.load_checkpoint() or {"next": 0, "pts": {}, "oracles": {}, "clean": True, "i1": None, "stopped": None,
                                   "beta": None}
    if st["beta"] is None:
        st["beta"] = CA.beta_of(train)
        text = (ROOT / SRC_ROWS).read_text(encoding="utf-8")
        ctx.emit({"kind": "reference", "exp": exp, "predicate_id": predicate_id, "pc": PC, "anomaly": ANOMALY,
                  "base_beta_recomputed": st["beta"], "base_beta_frozen": BASE_BETA, "mults": list(MULTS),
                  "order": [key(p) for p in order], "gens": gens, "batch": CA.BATCH, "port": port, "graph": GRAPH,
                  "c_rows": SRC_ROWS, "c_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                  "c_rows_sha256_frozen": SRC_SHA256, "status": "control", "ts": round(time.time(), 3)})
    while st["next"] < len(work) and st["stopped"] is None:
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(work) - st["next"])
        p, fam, rs = work[st["next"]]
        arm = "control" if p == "control" else "cell"
        beta = 0 if p == "control" else int(p) * BASE_BETA
        pk = key(p)
        first = fam == families[0] and rs == 0
        c0, w0 = time.process_time(), time.perf_counter()
        info, top = CA.run(r, graph, fam, rs, ARM_I[arm], arm, gens, train, held, beta, track=first)
        ok = info["recount_mismatched_top16"] == 0 and info["offers_mismatched"] == 0
        row = {"kind": "run", "exp": exp, "point": pk, "mult": None if p == "control" else int(p), "arm": arm,
               "cell": CA.CELL if arm == "cell" else CA.CELL_CTRL, "family": int(fam), "run_seed": int(rs),
               "beta": beta, "gens": gens, "genome_bytes": CA.GLEN, "reader": "top1_train", **info,
               **derived(info, beta)}
        if first:
            o = CA.oracles(graph, top, train, arm, beta)
            row["oracles"] = o
            st["oracles"][pk] = o
            ok = ok and o["ok"]
        row["run_ok"] = bool(ok)
        st["clean"] = bool(st["clean"] and ok)
        row.update({"cpu_s": round(time.process_time() - c0, 3), "wall_s": round(time.perf_counter() - w0, 3),
                    "status": status if arm == "cell" else "control", "ts": round(time.time(), 3)})
        st["pts"].setdefault(pk, {})[f"{fam}|{rs}"] = row
        ctx.emit(row)
        st["next"] += 1
        ctx.progress(st["next"], len(work) - st["next"])
        done_point = rs == runs_per_family - 1 and fam == families[-1]
        if done_point and not st["clean"]:
            st["stopped"] = f"ORACLE_NOT_CLEAN_AT_{pk}"
        if done_point and pk == "m1" and st["stopped"] is None:
            st["i1"] = i1_check(_pts(st), c_reference((ROOT / SRC_ROWS).read_text(encoding="utf-8")), st["beta"])
            if not st["i1"]["ok"]:
                st["stopped"] = "I1_REPLICATION_FAILED"
    pts = _pts(st)
    i1 = st["i1"] or {"ok": False, "reason": "not reached"}
    decision, stats = decide(i1["ok"], st["clean"], pts)
    per_point = {}
    for pk, d in pts.items():
        rows = list(d.values())
        med = lambda k: float(np.median([float(x[k]) for x in rows]))
        per_point[pk] = {"n": len(rows), "per_family": {str(f): sum(x["family"] == f for x in rows) for f in families},
                         "beta": rows[0]["beta"], "median_held": med("held_per_landscape_top1"),
                         "median_functional_bytes": med("functional_bytes"),
                         "median_avoidable_paid": med("avoidable_paid"), "median_charge_share": med("charge_share"),
                         "median_fb_over_max": med("fb_over_max"),
                         "median_train_nk_per_landscape": med("train_nk_per_landscape_top1"),
                         "median_train_fit_net": med("train_fit_top1"),
                         "functional_bytes_hist": {str(b): sum(x["functional_bytes"] == b for x in rows)
                                                   for b in range(FB_MIN, FB_MAX + 1)},
                         "median_code_len": float(np.median([x["top1_program"]["code_len"] for x in rows])),
                         "median_digits_read": float(np.median([x["top1_program"]["d"] for x in rows])),
                         "median_delivered_share": med("held_delivered_share_top1"),
                         "verdict": verdict_of(stats, pk, st["clean"] and i1["ok"])}
    unrun = [key(p) for p in order if len(pts.get(key(p), {})) < len(families) * runs_per_family]
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "pc": PC, "anomaly": ANOMALY,
              "status": status, "evidence_class": "VERDICT", "ts": round(time.time(), 3),
              "runs_total": 32, "rng_family_count": len(families), "runs_per_family": runs_per_family,
              "families": list(families), "n_per_family": {str(f): runs_per_family for f in families},
              "runs_total_all_points": sum(len(d) for d in pts.values()), "base_beta": BASE_BETA, "mults": list(MULTS),
              "checks": {"I1": i1, "oracles_clean": st["clean"], "oracles": st["oracles"]},
              "stopped": st["stopped"], "points_not_run": unrun, "decision": decision, "stats": stats,
              "per_point": per_point, "wall_s": round(time.perf_counter() - t0, 3)})


# ------------------------------------------------------------------ dev (no rows)

def dev(gens: int = 3, port: int = PORT) -> None:
    """No rows. Timing per generation on D's substrate at m64 (the most negative fitness), the BETA recomputation, and
    C's oracles on random + planted genomes at every BETA. No held-out value is computed."""
    import redis
    from falkordb import FalkorDB
    graph = FalkorDB(host="127.0.0.1", port=port, socket_timeout=300).select_graph(GRAPH + "_dev")
    redis.Redis(host="127.0.0.1", port=port).ping()
    train = CA.Landscapes(CA.TRAIN_SEEDS)
    beta = CA.beta_of(train)
    rng = np.random.Generator(np.random.PCG64(77))
    out = {"beta_recomputed": beta, "beta_frozen": BASE_BETA,
           "oracles_ok": {key(m): CA.oracles(graph, CA.init(rng, CA.TOP), train, "cell", m * BASE_BETA)["ok"]
                          for m in MULTS}}
    B = CA.init(rng, CA.BATCH)
    CA.brain_bits(B, train)
    t = time.perf_counter()
    lo = 0
    for _ in range(gens):
        B = CA.mutate(rng, B)
        bits, _ = CA.brain_bits(B, train)
        nk = CA.cypher_fit(graph, bits, train)
        lo = min(lo, int(CA.selection_fit(nk, B, "cell", 64 * BASE_BETA).min()))
    wall = (time.perf_counter() - t) / gens
    out["wall_per_gen_s"] = round(wall, 4)
    out["projected_runs_192_wall_s"] = round(192 * CA.GENS * wall, 1)
    out["min_selection_fit_m64"] = lo
    out["int32_safe"] = lo > -(2 ** 31)
    try:
        graph.delete()
    except Exception:
        pass
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        dev()
