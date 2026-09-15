"""D-R7-3 (ANOM-1789512027239-0, routed to D priority 1 by A 1789512067159-0): in E's O8 calibration the fused rollout
(soup.b6.fused.FusedRollout, the fast path under B-R5-1, the R16 screen and Clause B) disagreed with its numpy reference
(qd.e7_run.rollout) on 2 of 1280 random-donor graft runs: draw 24 run 2101|2192 (donor_tag 27024) and draw 31 run
2101|2255 (donor_tag 27031), both at granted 8 / numba 8 threads (E 1789512027239-0, 1789512256591-0).

Seen before this predicate: the two anomaly texts; from E's LOCAL O8 rows (nestor-r7-e working file; E's last commit on
that file is d22, so d24/d31 are not on origin) the two graft rows' donor_sha256, run ids and flags only; the code of
transfer_v2.run_seed, e7_run.rollout, fused._fused and genomes.Linear / linear_act_row. Nothing was rolled out.

Zero search. Per case, w13 linear (G7(13, "linear")), train seeds 9100..9227, donors
  raw = gb.pack(gb.init(PCG64([2101, donor_tag, run_seed, 13]), 16))        (transfer_v2 random donor, rng_family 2101)
  I1   sha256(raw) == E's donor_sha256 for both cases -- else INDETERMINATE.
  repro   E's comparison exactly: E7.rollout(gb, g, train)[0] vs FusedRollout(gb.spec, 16, train, 'linear').run(g)[0];
          fused 3x at the granted numba threads and 1x at 1 thread. Q = genomes whose fitness differs.
  locate  each q in Q alone (P = 1, 128 seeds, full logs both paths): per env the first tick where, in this order,
          obs, idx or acts differ (ticks below both done ticks), else done_tick, else final charge.
  brain   at an idx-first divergence: that obs row's numpy float32 logits (Linear.logits, einsum then + b), a float32
          emulation of linear_act_row (s = b, then + each feature in order), linear_act_row called directly, and the
          float64 ref_logits with genomes.clear_rows (rel 1e-6).
Label per case (first match):
  NOT_REPRODUCED    no fused/numpy fitness difference in any fused call
  NONDETERMINISTIC  the 3 fused calls at the granted threads do not all agree
  BATCH_ONLY        the P = 16 difference reproduces but every q alone agrees in all 128 envs
  OBS_FIRST         the earliest divergence (smallest tick over Q x envs) is an obs difference
  BRAIN_NEAR_TIE    it is an idx difference and the float64 ref is NOT a clear row at that obs row
  BRAIN_CLEAR       it is an idx difference on a clear row
  STEP_FIRST        otherwise (acts, done_tick or charge first)
decision = "d24:<label>|d31:<label>".
Controls (binding): clean_genome -- the first genome of the case with equal P = 16 fitness localizes to no divergence in
all 128 envs; planted_brain -- fused with brain_stride 2 (C's skip cheat) vs honest numpy on that genome localizes to an
idx-first divergence. Either failing -> INDETERMINATE.
Reported, not judged: per-q fitness both paths, envs diverging per q, thread-1 vs granted agreement, per-path argmax
agreement at the first brain row, float32 top-2 gaps.
evidence_class OBSERVATION: two loci from one family, not a 32/4/8 sample.

    worker.submit("D", "primordial.cohorts.d.r7_3_fused_vs_numpy_graft:job", EXP, ROWS, 600, envelope={...OBSERVATION...})
"""
from __future__ import annotations

import hashlib
import time

import numpy as np

EXP = "D-R7-3-fused-vs-numpy-graft"
PREDICATE_ID = EXP
ANOMALY = "1789512027239-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
RECIPIENT, N_TRAIN, TOP, FAMILY = 13, 128, 16, 2101
CASES = ({"draw": 24, "donor_tag": 27024, "run_seed": 2192,
          "donor_sha256": "e360648f44f9d934d600ae586e0b6f923b005e8ec2098c5515bcd6a2d4524fa2"},
         {"draw": 31, "donor_tag": 27031, "run_seed": 2255,
          "donor_sha256": "0ed376d22f6cdc1ddb3a8369ba6f9daf775933076e4cc262a11e96e8ff889a80"})
KINDS = ("obs", "idx", "acts")


def donors(case: dict):
    from primordial.qd import e7_run as E7
    gb = E7.G7(RECIPIENT, "linear")
    rng = np.random.Generator(np.random.PCG64([FAMILY, int(case["donor_tag"]), int(case["run_seed"]), RECIPIENT]))
    raw = gb.pack(gb.init(rng, TOP))
    return gb, raw


def one(g, q: int):
    (W, b), C = g
    return (W[q:q + 1].copy(), b[q:q + 1].copy()), C[q:q + 1].copy()


def first_divergence(a: dict, b: dict, dta: int, dtb: int):
    """a, b: one env's logs {obs [T,S,D], idx [T,S], acts [T,S,W]}; -> None or {tick, kind, slot}."""
    for t in range(min(int(dta), int(dtb))):
        for kind in KINDS:
            x, y = np.asarray(a[kind][t]), np.asarray(b[kind][t])
            if not np.array_equal(x, y):
                diff = (x != y).reshape(x.shape[0], -1).any(1)
                return {"tick": t, "kind": kind, "slot": int(np.nonzero(diff)[0][0])}
    if int(dta) != int(dtb):
        return {"tick": min(int(dta), int(dtb)), "kind": "done_tick", "slot": None}
    return None


def localize(gb, g1, train, brain_stride: int = 1) -> dict:
    """One genome alone over every train seed, both paths logged. -> per-env first divergences + fitness."""
    from primordial.qd import e7_run as E7
    from primordial.soup.b6.fused import FusedRollout
    k = len(train)
    _, _, w, L = E7.rollout(gb, g1, train, log=True)
    fu = FusedRollout(gb.spec, 1, train, family="linear")
    _, _, dt_f, logs, _ = fu.run(g1, brain_stride=brain_stride, record=list(range(k)))
    dt_n = L["live"].any(-1).sum(0)
    fit_n = np.clip(w.charge, 0, None).sum(1)
    fit_f = np.array([np.clip(logs["charge"][max(int(dt_f[e]) - 1, 0), e], 0, None).sum() for e in range(k)])
    envs = []
    for e in range(k):
        d = first_divergence({x: L[x][:, e] for x in KINDS}, {x: logs[x][:, e] for x in KINDS}, dt_n[e], dt_f[e])
        if d is None and int(fit_n[e]) != int(fit_f[e]):
            d = {"tick": int(dt_f[e]), "kind": "charge", "slot": None}
        if d is not None:
            d.update(env=e, seed=int(train[e]), fit_numpy=int(fit_n[e]), fit_fused=int(fit_f[e]))
            if d["kind"] == "idx":
                d["obs_row"] = [int(v) for v in L["obs"][d["tick"], e, d["slot"]]]
                d["idx_numpy"] = int(L["idx"][d["tick"], e, d["slot"]])
                d["idx_fused"] = int(logs["idx"][d["tick"], e, d["slot"]])
            envs.append(d)
    return {"envs_diverging": len(envs), "divergences": envs}


def brain_row(gb, g1, obs_row) -> dict:
    """Every path's decision on one obs row for one linear genome."""
    from primordial.brain import genomes as gm
    from primordial.brain.genomes import linear_act_row
    (W, b), _ = g1
    W32, b32 = np.ascontiguousarray(W[0], np.float32), np.ascontiguousarray(b[0], np.float32)
    D, A = W32.shape
    row = np.asarray(obs_row, np.int64)
    lg = np.asarray(gb.fam.logits((W32[None], b32[None]), row[None], np.zeros(1, np.int64))[0], np.float32)
    seq = np.empty(A, np.float32)
    for a in range(A):
        s = np.float32(b32[a])
        for f in range(D):
            s = np.float32(s + (np.float32(row[f]) / np.float32(65535.0) - np.float32(0.5)) * W32[f, a])
        seq[a] = s
    ref = gb.fam.ref_logits((W32, b32), row[None])[0]
    top2 = np.sort(ref)[-2:]
    gap32 = lambda v: float(np.sort(v)[-1] - np.sort(v)[-2])
    return {"argmax_numpy_f32": int(lg.argmax()), "argmax_seq_f32": int(seq.argmax()),
            "argmax_kernel_direct": int(linear_act_row(row, W32, b32, 1)), "argmax_ref_f64": int(ref.argmax()),
            "ref_clear": bool(gm.clear_rows(ref[None])[0]), "ref_top2_gap": float(top2[1] - top2[0]),
            "ref_scale": float(np.abs(ref).max()), "f32_top2_gap_numpy": gap32(lg), "f32_top2_gap_seq": gap32(seq),
            "numpy_vs_seq_bitwise_equal": bool(np.array_equal(lg.view(np.uint32), seq.view(np.uint32))),
            "logits_numpy_f32": [float(x) for x in lg], "logits_seq_f32": [float(x) for x in seq]}


def label(repro: dict, local: dict, brain: dict | None) -> str:
    if not repro["any_difference"]:
        return "NOT_REPRODUCED"
    if not repro["granted_repeats_agree"]:
        return "NONDETERMINISTIC"
    if not any(v["envs_diverging"] for v in local.values()):
        return "BATCH_ONLY"
    first = min((d for v in local.values() for d in v["divergences"]), key=lambda d: (d["tick"], d["env"]))
    if first["kind"] == "obs":
        return "OBS_FIRST"
    if first["kind"] == "idx":
        return "BRAIN_CLEAR" if brain is not None and brain["ref_clear"] else "BRAIN_NEAR_TIE"
    return "STEP_FIRST"


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID):
    """D-R7-3's rows were all rejected by the RowWriter (`status 'observation'` is not in fabric.rows.STATUSES); the
    evidentiary class lives in the row's `evidence_class` field, not in the writer's status. D-R7-3b re-runs the same
    deterministic zero-QD rule with status 'record' under its own predicate and rows file."""
    import numba
    from primordial.qd import e7_run as E7
    from primordial.soup.b6.fused import FusedRollout
    t0 = time.perf_counter()
    train = np.arange(9100, 9100 + N_TRAIN, dtype=np.int64)
    granted = int(numba.get_num_threads())
    labels, i1, ctl = {}, {}, {}
    for case in CASES:
        gb, raw = donors(case)
        g = gb.unpack(raw)
        sha = hashlib.sha256(np.ascontiguousarray(raw).tobytes()).hexdigest()
        i1[f"d{case['draw']}_donor_sha256"] = sha == case["donor_sha256"]
        np_fit = E7.rollout(gb, g, train)[0]
        fused = [FusedRollout(gb.spec, TOP, train, family="linear").run(g)[0] for _ in range(3)]
        numba.set_num_threads(1)
        fused1 = FusedRollout(gb.spec, TOP, train, family="linear").run(g)[0]
        numba.set_num_threads(granted)
        calls = fused + [fused1]
        Q = sorted({int(q) for f in calls for q in np.nonzero(np.asarray(f) != np.asarray(np_fit))[0]})
        repro = {"granted_threads": granted, "any_difference": bool(Q), "genomes_differing": Q,
                 "granted_repeats_agree": all(np.array_equal(fused[0], f) for f in fused[1:]),
                 "thread1_equals_granted": bool(np.array_equal(fused[0], fused1)),
                 "per_genome": {str(q): {"numpy": int(np_fit[q]), "fused_granted": int(fused[0][q]),
                                         "fused_thread1": int(fused1[q])} for q in Q}}
        local = {str(q): localize(gb, one(g, q), train) for q in Q}
        brain = None
        firsts = [d for v in local.values() for d in v["divergences"]]
        if firsts:
            first = min(firsts, key=lambda d: (d["tick"], d["env"]))
            q0 = next(int(q) for q, v in local.items() if first in v["divergences"])
            if first["kind"] == "idx":
                brain = dict(brain_row(gb, one(g, q0), first["obs_row"]), genome=q0, tick=first["tick"],
                             env=first["env"], slot=first["slot"], idx_numpy_log=first["idx_numpy"],
                             idx_fused_log=first["idx_fused"])
        clean_q = next((q for q in range(TOP) if int(np_fit[q]) == int(fused[0][q])), None)
        c_clean = localize(gb, one(g, clean_q), train) if clean_q is not None else None
        c_plant = localize(gb, one(g, clean_q if clean_q is not None else 0), train, brain_stride=2)
        plant_first = min(c_plant["divergences"], key=lambda d: (d["tick"], d["env"])) if c_plant["divergences"] else None
        ctl[f"d{case['draw']}"] = {
            "clean_genome": {"genome": clean_q, "envs_diverging": None if c_clean is None else c_clean["envs_diverging"],
                             "ok": c_clean is not None and c_clean["envs_diverging"] == 0},
            "planted_brain": {"first_kind": None if plant_first is None else plant_first["kind"],
                              "envs_diverging": c_plant["envs_diverging"],
                              "ok": plant_first is not None and plant_first["kind"] == "idx"}}
        lab = label(repro, local, brain)
        labels[f"d{case['draw']}"] = lab
        ctx.emit({"kind": "case", "exp": exp, "status": status, "ts": round(time.time(), 3), **case,
                  "rng_family": FAMILY, "recipient": f"w{RECIPIENT}", "train_seeds": N_TRAIN, "donor_sha256_rebuilt": sha,
                  "repro": repro, "localize": {q: {"envs_diverging": v["envs_diverging"],
                                                   "divergences": v["divergences"][:32]} for q, v in local.items()},
                  "brain_at_first_divergence": brain, "controls": ctl[f"d{case['draw']}"], "label": lab})
    ok = all(c["clean_genome"]["ok"] and c["planted_brain"]["ok"] for c in ctl.values())
    decision = "INDETERMINATE" if not (all(i1.values()) and ok) else "|".join(f"{k}:{v}" for k, v in labels.items())
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "anomaly": ANOMALY, "status": status,
              "evidence_class": "OBSERVATION", "ts": round(time.time(), 3), "qd_runs": 0,
              "runs_total": len(CASES), "rng_family_count": 1, "runs_per_family": len(CASES), "families": [FAMILY],
              "n_per_family": {str(FAMILY): len(CASES)}, "checks": {"I1": i1, "controls_ok": ok}, "controls": ctl,
              "labels": labels, "decision": decision, "wall_s": round(time.perf_counter() - t0, 3)})
