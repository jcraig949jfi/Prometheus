"""D-R7-8 (ANOM-1789415790378-0): C7c detected 238/238 regime switches on FIT-eligible targets; C7e detected 73/130 on
GENOME-eligible targets. The anomaly expects the genome-derived set to be the cleaner one, so detection should not fall.

Reading both harnesses first changes the question. C7c (brain/c7c_fit_eligible.py) and C7e (brain/c7e_genome_eligible.py)
SHARE the learner, the probe, drive() and score() -- C7e's own docstring says "Learners, probe and per-target measures
are C7c/C7d's", and the per-target blocks are line-for-line the same. So "score C7e's learner on C7c's targets" is
vacuous: there is one learner. The two runs differ in TWO ways at once:
  (1) the eligibility criterion (fit on a never-scored seed set vs B's genome lookup), and
  (2) the RECORD SEEDS: C7c scores on 90000..90511, C7e on 94000..94511 -- disjoint. The anomaly's expectation
      silently assumes a common scoring seed set.

This experiment removes (2) so that (1) can be read. Zero new eligibility work: both eligible sets come from committed
rows (C7c's per-world `eligible_targets`, C7e's header `eligible` list), giving three partitions -- BOTH 11 targets,
FIT_ONLY 23, GENOME_ONLY 7 -- all scored on ONE record seed set that neither original used (96000.., n 512), so
neither criterion's targets get home advantage.

Measures: C7c/C7e's own per-target block, minus the digit-TT arm. digit_tt exists to ground C's H2 chance rate, not the
detection question here, and it costs ~95% of the wall (measured: 2.28 s of 2.39 s per target at n=512). Dropped, and
said so.

Rule (fixed before any detection value is read):
  rate(S) = sum(detected) / sum(switches) over the targets in S.
  rate_f = rate(BOTH + FIT_ONLY)      -- all 34 fit-eligible; C7c published 238/238 = 1.000
  rate_g = rate(BOTH + GENOME_ONLY)   -- all 18 genome-eligible; C7e published 73/130 = 0.562
  LEARNER_DOES_NOT_REPRODUCE  rate_f < 0.95   (the instrument fails on C7c's own targets: nothing else is readable)
  SELECTION                   rate_f >= 0.95 and rate_g <= 0.80  (the contrast survives a common seed set, so it is
                                                                  the eligibility criterion, not the seeds)
  SEEDS                       rate_f >= 0.95 and rate_g >= 0.95  (the contrast vanishes, so the published gap rode on
                                                                  the disjoint record seeds)
  MIXED                       otherwise
  INDETERMINATE if I1 or a binding control fails.
I1: all three partitions non-empty and of the committed sizes (11 / 23 / 7), every target scored, and every world's
switch count > 0.
Binding controls, all of C's own instrument: probe_affine CLEAN and probe_leak LEAK on EVERY target (the learner is not
leaking the regime flip through the probe offset), and the null-world learner (no_regime_flip) surprises <= 2 after its
first fit on every target.
Reported, not judged: per-partition detected/switches and rates; per-target detection; rate by corrupt_rate (rate 8
appears only among genome-only targets); support_in_regime; C7c's and C7e's published totals for reference.

    worker.submit("D", "primordial.cohorts.d.r7_8_c7_eligibility_swap:job", EXP, ROWS, 900, envelope={...})
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import time

import numpy as np

EXP = "D-R7-8-c7-eligibility-swap"
PREDICATE_ID = EXP
ANOMALY = "1789415790378-0"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
C7C_ROWS = "primordial/ledger/rows/C/C7c-fit-eligible-plasticity.jsonl"
C7E_ROWS = "primordial/ledger/rows/C/C7e-genome-eligible-plasticity.jsonl"
INTEGRATION = "origin/nestor/sidequest-graphworld-2026-09-14"
RECORD_SEED0, N_SEEDS = 96000, 512          # fresh: C7c used 90000/91000, C7e 94000/95000
SIZES = {"both": 11, "fit_only": 23, "genome_only": 7}
RATE_HI, RATE_LO = 0.95, 0.80
PUBLISHED = {"C7c": {"detected": 238, "switches": 238, "rate": 1.0, "record_seed0": 90000},
             "C7e": {"detected": 73, "switches": 130, "rate": 0.5615, "record_seed0": 94000}}


def source_text(path: str, root=ROOT, integration: str = INTEGRATION) -> tuple[str, str]:
    q = subprocess.run(["git", "-C", str(root), "show", f"{integration}:{path}"], capture_output=True, text=True,
                       encoding="utf-8")
    if q.returncode == 0 and q.stdout.strip():
        return q.stdout, integration
    return (root / path).read_text(encoding="utf-8"), "worktree"


def partitions(c7c_text: str, c7e_text: str) -> dict:
    """The two committed eligible sets -> {'both': [...], 'fit_only': [...], 'genome_only': [...]} of (gen_seed, j)."""
    c7c = [json.loads(l) for l in c7c_text.splitlines() if l.strip()]
    c7e = [json.loads(l) for l in c7e_text.splitlines() if l.strip()]
    fit = {(int(w["gen_seed"]), int(j)) for w in c7c if w.get("kind") == "world" for j in w.get("eligible_targets", [])}
    hdr = next(x for x in c7e if x.get("kind") == "header")
    gen = {(int(e["gen_seed"]), int(e["j"])) for e in hdr["eligible"]}
    rates = {(int(e["gen_seed"]), int(e["j"])): int(e["corrupt_rate"]) for e in hdr["eligible"]}
    return {"both": sorted(fit & gen), "fit_only": sorted(fit - gen), "genome_only": sorted(gen - fit),
            "corrupt_rate_from_c7e": rates}


def rate_of(rows: list[dict]) -> dict:
    det = sum(int(r["detected"]) for r in rows)
    sw = sum(int(r["switches"]) for r in rows)
    return {"detected": det, "switches": sw, "rate": round(det / sw, 4) if sw else None, "targets": len(rows)}


def decide(i1: bool, controls_ok: bool, rate_f, rate_g) -> str:
    if not (i1 and controls_ok) or rate_f is None or rate_g is None:
        return "INDETERMINATE"
    if rate_f < RATE_HI:
        return "LEARNER_DOES_NOT_REPRODUCE"
    if rate_g <= RATE_LO:
        return "SELECTION"
    if rate_g >= RATE_HI:
        return "SEEDS"
    return "MIXED"


def score_target(m, wid, gs: int, j: int, cache: dict) -> dict:
    """C7c/C7e's per-target block without the digit-TT arm."""
    from primordial.brain import affine_plastic as ap
    from primordial.brain.c7b_regime_plastic import drive, score, trajectory
    T, P, r = m.horizon, m.regime_period, m.corrupt_rate
    seeds = np.arange(RECORD_SEED0, RECORD_SEED0 + N_SEEDS, dtype=np.int64)
    if gs not in cache:
        cache[gs] = (trajectory(m, wid, "", seeds), trajectory(m, wid, "no_regime_flip", seeds))
    real, null = cache[gs]
    X, Y = real[:-1, :, :-1], real[1:, :, j]
    Xn, Yn = null[:-1, :, :-1], null[1:, :, j]
    mk_aff = lambda: ap.PlasticAffine(seed=gs * 101 + j)
    mk_leak = lambda: ap.LeakAffine(seed=gs * 101 + j)
    s_aff, u_aff, m_aff = drive(mk_aff, X, Y, T, P, 0)
    s_aff2, _, m_aff2 = drive(mk_aff, X, Y, T, P, P // 2)
    s_leak, _, m_leak = drive(mk_leak, X, Y, T, P, 0)
    s_leak2, _, m_leak2 = drive(mk_leak, X, Y, T, P, P // 2)
    s_null, u_null, _ = drive(mk_aff, Xn, Yn, T, P, 0)
    sc = score(s_aff, u_aff, T, P)
    return {"gen_seed": gs, "j": j, "corrupt_rate": r, "switches": int(sc["switches"]), "detected": int(sc["detected"]),
            "support_in_regime": sc.get("support_in_regime"),
            "surprises_outside_windows": int(sc.get("surprises_outside_windows", 0)),
            "null_surprises_after_first_fit": int(sum(s_null[1:])), "null_support": float(np.mean(u_null[1:])),
            "probe_affine": "CLEAN" if (s_aff, m_aff) == (s_aff2, m_aff2) else "LEAK",
            "probe_leak": "CLEAN" if (s_leak, m_leak) == (s_leak2, m_leak2) else "LEAK"}


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID, n_seeds: int = N_SEEDS):
    from primordial.soup.b1.common import make_world
    t0 = time.perf_counter()
    c7c_text, prov_c = source_text(C7C_ROWS)
    c7e_text, prov_e = source_text(C7E_ROWS)
    part = partitions(c7c_text, c7e_text)
    todo = [(name, gs, j) for name in ("both", "fit_only", "genome_only") for gs, j in part[name]]
    st = ctx.load_checkpoint() or {"next": 0, "rows": {}}
    cache = {}
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        name, gs, j = todo[st["next"]]
        m, wid = make_world(gs)
        row = score_target(m, wid, gs, j, cache)
        row["partition"] = name
        st["rows"][f"{name}|{gs}|{j}"] = row
        ctx.emit({"kind": "target", "exp": exp, "predicate_id": predicate_id, "status": status,
                  "ts": round(time.time(), 3), **row})
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    rows = list(st["rows"].values())
    by = {name: [r for r in rows if r["partition"] == name] for name in ("both", "fit_only", "genome_only")}
    per_part = {k: rate_of(v) for k, v in by.items()}
    fit_rows, gen_rows = by["both"] + by["fit_only"], by["both"] + by["genome_only"]
    f_stats, g_stats = rate_of(fit_rows), rate_of(gen_rows)
    i1 = {"partition_sizes": {k: len(v) for k, v in by.items()} == SIZES,
          "all_targets_scored": len(rows) == sum(SIZES.values()),
          "every_world_switches": all(r["switches"] > 0 for r in rows)}
    controls = {"probe_affine_clean": all(r["probe_affine"] == "CLEAN" for r in rows),
                "probe_leak_detects_leak": all(r["probe_leak"] == "LEAK" for r in rows),
                "null_world_quiet": all(r["null_surprises_after_first_fit"] <= 2 for r in rows)}
    ok = all(controls.values())
    decision = decide(all(i1.values()), ok, f_stats["rate"], g_stats["rate"])
    crate = part["corrupt_rate_from_c7e"]
    by_corrupt = {}
    for r in rows:
        by_corrupt.setdefault(str(r["corrupt_rate"]), []).append(r)
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "anomaly": ANOMALY, "status": status,
              "evidence_class": "OBSERVATION", "ts": round(time.time(), 3),
              "record_seed0": RECORD_SEED0, "n_seeds": n_seeds, "digit_tt": "not run (C's H2 chance arm, ~95% of wall)",
              "source_rows": {C7C_ROWS: prov_c, C7E_ROWS: prov_e},
              "source_sha256": {C7C_ROWS: hashlib.sha256(c7c_text.encode()).hexdigest()[:16],
                                C7E_ROWS: hashlib.sha256(c7e_text.encode()).hexdigest()[:16]},
              "partition_sizes": {k: len(v) for k, v in by.items()},
              "checks": {"I1": i1, "controls_ok": ok}, "controls": controls,
              "rate_fit_eligible": f_stats, "rate_genome_eligible": g_stats, "by_partition": per_part,
              "decision": decision,
              "reported_not_judged": {
                  "published": PUBLISHED,
                  "by_corrupt_rate": {k: rate_of(v) for k, v in sorted(by_corrupt.items())},
                  "corrupt_rate_of_genome_only": sorted({crate[(gs, j)] for gs, j in part["genome_only"] if (gs, j) in crate}),
                  "corrupt_rate_of_both": sorted({crate[(gs, j)] for gs, j in part["both"] if (gs, j) in crate}),
                  "per_target": sorted(((r["partition"], r["gen_seed"], r["j"], r["detected"], r["switches"]) for r in rows)),
                  "median_support_in_regime": float(np.median([r["support_in_regime"] for r in rows
                                                               if r["support_in_regime"] is not None])) if rows else None},
              "wall_s": round(time.perf_counter() - t0, 3)})
