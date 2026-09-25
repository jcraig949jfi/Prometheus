"""D-R7-9 (ANOM-1789415790378-0, still OPEN after D-R7-8 returned INDETERMINATE): D-R7-8 found that all 18
genome-eligible targets reproduced C7e's per-target (detected, switches) EXACTLY on a different record seed base, while
the 34 fit-eligible targets scored 180/238 against C7c's published 238/238. Two claims follow from one coincidence, so
both are tested here directly.

Q1 SEED STABILITY. Re-score the same 41 targets at two further fresh record bases (97000, 98000) and compare per-target
   (detected, switches) with D-R7-8's committed 96000 run. If detection is a deterministic property of the world's
   regime structure, every target matches at every base.
Q2 ELIGIBILITY CONDITIONING. Re-run C7c's OWN fit-eligibility procedure at a fresh eligibility base (99000; C7c used
   91000) over C7c's own world list, and compare the admitted set with C7c's committed 34. If C7c's 238/238 rests on
   eligibility being decided on the seeds that also make the learner look quiet, the admitted set moves.

Seed bases used before and avoided here: C7c 90000 (record) / 91000 (eligibility), C7e 94000 / 95000, D-R7-8 96000.

Zero new instrument: C7c/C7e's shared learner, probe and measures (brain/c7b_regime_plastic drive, score, trajectory;
brain/affine_plastic), C7c's eligibility rule (sensitivity >= SENS_MIN on a never-scored base, then the null-world fit
admitting a column iff surprises after first fit <= FIT_MAX_NULL_SURPRISES), and D-R7-8's partition file read from its
committed rows.

CONTROL CHOICE, fixed before running and stated because it differs from D-R7-8. D-R7-8's binding control was
"null_world_quiet on every target"; one target (world 497 j=2) read 62 and voided the run. That bound is NOT relaxed --
it is retired from the binding set for THIS question, because whether the null-world count is itself seed-dependent is
part of what Q1 measures. Reporting it while binding on it would be circular. The binding controls here are:
  determinism_repeat  one base (97000) is scored twice in the same job; every target must give identical
                      (detected, switches, null_surprises), else the comparison across bases is meaningless
  probe_affine CLEAN and probe_leak LEAK on every target at every base (C's own leak probes, unchanged)

Rule (fixed before any value is read). Let match(b) = #targets whose (detected, switches) at base b equal D-R7-8's
committed values, out of 41.
  Q1  SEED_INSENSITIVE  match(97000) == 41 and match(98000) == 41
      SEED_SENSITIVE    match(97000) <= 37 or match(98000) <= 37
      MIXED_SEED        otherwise
  Q2  Let A = C7c's committed fit-eligible set (34 targets), B = the set admitted at eligibility base 99000, and
      d = |A symmetric-difference B|.
      ELIGIBILITY_SEED_CONDITIONED  d >= 6
      ELIGIBILITY_STABLE            d <= 2
      MIXED_ELIGIBILITY             otherwise
  decision = "seed:<Q1>|eligibility:<Q2>"; INDETERMINATE if I1 or a binding control fails.
I1: 41 targets scored at each base; the 96000 comparison values load from D-R7-8's committed rows; C7c's world list and
its committed eligible set load from C7c's committed rows.
Reported, not judged: null_surprises per target per base (including world 497 j=2, whose 62 prompted this); which
targets move between eligibility sets; per-base rate_f and rate_g; detection by corrupt_rate.

    worker.submit("D", "primordial.cohorts.d.r7_9_c7_seed_stability:job", EXP, ROWS, 900, envelope={...})
"""
from __future__ import annotations

import hashlib
import json
import time

import numpy as np

from primordial.cohorts.d import r7_8_c7_eligibility_swap as S8

EXP = "D-R7-9-c7-seed-stability"
PREDICATE_ID = EXP
ANOMALY = "1789415790378-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
D_R7_8_ROWS = "primordial/ledger/rows/D/D-R7-8-c7-eligibility-swap.jsonl"
BASES = (97000, 98000)
REPEAT_BASE = 97000
ELIG_BASE = 99000
N_SEEDS = S8.N_SEEDS
MATCH_ALL, MATCH_LO = 41, 37
ELIG_MOVED, ELIG_STABLE = 6, 2
PRIOR_BASES = {"C7c_record": 90000, "C7c_eligibility": 91000, "C7e_record": 94000, "C7e_calibration": 95000,
               "D-R7-8_record": 96000}


def committed_r7_8(text: str) -> dict:
    """D-R7-8's per-target (detected, switches, partition) at base 96000."""
    out = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        x = json.loads(line)
        if x.get("kind") == "target":
            out[(int(x["gen_seed"]), int(x["j"]))] = {"detected": int(x["detected"]), "switches": int(x["switches"]),
                                                      "partition": x["partition"],
                                                      "null_surprises": int(x["null_surprises_after_first_fit"])}
    return out


def score_at(m, wid, gs: int, j: int, base: int, cache: dict) -> dict:
    """S8.score_target with the record base as a parameter (same learner, probes and measures)."""
    from primordial.brain import affine_plastic as ap
    from primordial.brain.c7b_regime_plastic import drive, score, trajectory
    T, P, r = m.horizon, m.regime_period, m.corrupt_rate
    key = (gs, base)
    if key not in cache:
        seeds = np.arange(base, base + N_SEEDS, dtype=np.int64)
        cache[key] = (trajectory(m, wid, "", seeds), trajectory(m, wid, "no_regime_flip", seeds))
    real, null = cache[key]
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
    return {"gen_seed": gs, "j": j, "base": base, "corrupt_rate": r, "switches": int(sc["switches"]),
            "detected": int(sc["detected"]), "null_surprises": int(sum(s_null[1:])),
            "probe_affine": "CLEAN" if (s_aff, m_aff) == (s_aff2, m_aff2) else "LEAK",
            "probe_leak": "CLEAN" if (s_leak, m_leak) == (s_leak2, m_leak2) else "LEAK"}


def fit_eligible_at(base: int, worlds, make_world) -> list[tuple[int, int]]:
    """C7c's own eligibility rule, evaluated at a fresh base: sensitivity >= SENS_MIN, then null-world fit <= bound."""
    from primordial.brain import affine_plastic as ap
    from primordial.brain.c7b_regime_plastic import SENS_MIN, drive, trajectory
    from primordial.brain.c7c_fit_eligible import FIT_MAX_NULL_SURPRISES
    seeds = np.arange(base, base + N_SEEDS, dtype=np.int64)
    out = []
    for gs in worlds:
        m, wid = make_world(gs)
        T, P = m.horizon, m.regime_period
        n_sw = len(range(P, T, P)) if P else 0
        if n_sw < 1 or T <= P + 1:
            continue
        real_e = trajectory(m, wid, "", seeds)
        null_e = trajectory(m, wid, "no_regime_flip", seeds)
        D = real_e.shape[2]
        sens = (real_e[P + 1:] != null_e[P + 1:]).mean(axis=(0, 1))
        for j in (k for k in range(D - 1) if sens[k] >= SENS_MIN):
            s_n, _, _ = drive(lambda: ap.PlasticAffine(seed=gs * 101 + j), null_e[:-1, :, :-1], null_e[1:, :, j], T, P, 0)
            if int(sum(s_n[1:])) <= FIT_MAX_NULL_SURPRISES:
                out.append((gs, j))
    return sorted(out)


def decide_seed(i1: bool, controls_ok: bool, matches: dict) -> str:
    if not (i1 and controls_ok) or sorted(matches) != sorted(BASES):
        return "INDETERMINATE"
    if all(matches[b] == MATCH_ALL for b in BASES):
        return "SEED_INSENSITIVE"
    if any(matches[b] <= MATCH_LO for b in BASES):
        return "SEED_SENSITIVE"
    return "MIXED_SEED"


def decide_elig(i1: bool, controls_ok: bool, d: int) -> str:
    if not (i1 and controls_ok) or d is None:
        return "INDETERMINATE"
    if d >= ELIG_MOVED:
        return "ELIGIBILITY_SEED_CONDITIONED"
    if d <= ELIG_STABLE:
        return "ELIGIBILITY_STABLE"
    return "MIXED_ELIGIBILITY"


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID):
    from primordial.soup.b1.common import make_world
    from primordial.brain.c7c_fit_eligible import CLEAN, CORRUPTED
    t0 = time.perf_counter()
    r8_text, prov8 = S8.source_text(D_R7_8_ROWS)
    c7c_text, prov_c = S8.source_text(S8.C7C_ROWS)
    c7e_text, _ = S8.source_text(S8.C7E_ROWS)
    ref = committed_r7_8(r8_text)
    part = S8.partitions(c7c_text, c7e_text)
    targets = sorted(set(part["both"]) | set(part["fit_only"]) | set(part["genome_only"]))
    committed_fit = sorted(set(part["both"]) | set(part["fit_only"]))
    units = [("score", b, gs, j) for b in BASES for gs, j in targets] + \
            [("repeat", REPEAT_BASE, gs, j) for gs, j in targets] + [("elig", ELIG_BASE, 0, 0)]
    st = ctx.load_checkpoint() or {"next": 0, "rows": {}, "repeat": {}, "elig": None}
    cache = {}
    while st["next"] < len(units):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(units) - st["next"])
        kind, base, gs, j = units[st["next"]]
        if kind == "elig":
            st["elig"] = [list(t) for t in fit_eligible_at(ELIG_BASE, list(CLEAN) + list(CORRUPTED), make_world)]
        else:
            m, wid = make_world(gs)
            row = score_at(m, wid, gs, j, base, cache)
            if kind == "score":
                row["partition"] = ref.get((gs, j), {}).get("partition")
                row["matches_r7_8"] = (row["detected"], row["switches"]) == \
                                      (ref.get((gs, j), {}).get("detected"), ref.get((gs, j), {}).get("switches"))
                st["rows"][f"{base}|{gs}|{j}"] = row
                ctx.emit({"kind": "target", "exp": exp, "predicate_id": predicate_id, "status": status,
                          "ts": round(time.time(), 3), **row})
            else:
                st["repeat"][f"{gs}|{j}"] = {k: row[k] for k in ("detected", "switches", "null_surprises")}
        st["next"] += 1
        ctx.progress(st["next"], len(units) - st["next"])
    rows = list(st["rows"].values())
    matches = {b: sum(1 for r in rows if r["base"] == b and r["matches_r7_8"]) for b in BASES}
    first = {f"{r['gen_seed']}|{r['j']}": r for r in rows if r["base"] == REPEAT_BASE}
    det = {k: (v["detected"], v["switches"], v["null_surprises"]) for k, v in first.items()}
    rep = {k: (v["detected"], v["switches"], v["null_surprises"]) for k, v in st["repeat"].items()}
    controls = {"determinism_repeat": {"targets": len(rep), "identical": det == rep,
                                       "differing": sorted(k for k in det if det.get(k) != rep.get(k))},
                "probe_affine_clean": all(r["probe_affine"] == "CLEAN" for r in rows),
                "probe_leak_detects_leak": all(r["probe_leak"] == "LEAK" for r in rows)}
    ok = bool(controls["determinism_repeat"]["identical"] and controls["probe_affine_clean"]
              and controls["probe_leak_detects_leak"])
    elig_new = sorted(tuple(t) for t in (st["elig"] or []))
    d = len(set(committed_fit) ^ set(elig_new)) if elig_new is not None else None
    i1 = {"targets_41": len(targets) == 41, "scored_each_base": all(sum(1 for r in rows if r["base"] == b) == 41 for b in BASES),
          "reference_loaded": len(ref) == 41, "committed_fit_34": len(committed_fit) == 34}
    q1, q2 = decide_seed(all(i1.values()), ok, matches), decide_elig(all(i1.values()), ok, d)
    decision = "INDETERMINATE" if "INDETERMINATE" in (q1, q2) else f"seed:{q1}|eligibility:{q2}"
    by_base = {}
    for b in BASES:
        rb = [r for r in rows if r["base"] == b]
        by_base[str(b)] = {"detected": sum(r["detected"] for r in rb), "switches": sum(r["switches"] for r in rb),
                           "matches_r7_8": matches[b],
                           "null_surprises_over_2": sorted((r["gen_seed"], r["j"], r["null_surprises"])
                                                           for r in rb if r["null_surprises"] > 2)}
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "anomaly": ANOMALY, "status": status,
              "evidence_class": "OBSERVATION", "ts": round(time.time(), 3), "bases": list(BASES),
              "eligibility_base": ELIG_BASE, "n_seeds": N_SEEDS, "prior_bases": PRIOR_BASES,
              "source_provenance": {D_R7_8_ROWS: prov8, S8.C7C_ROWS: prov_c},
              "source_sha256": {D_R7_8_ROWS: hashlib.sha256(r8_text.encode()).hexdigest()[:16]},
              "checks": {"I1": i1, "controls_ok": ok}, "controls": controls,
              "matches_by_base": matches, "by_base": by_base,
              "eligibility": {"committed_fit_eligible": len(committed_fit), "fresh_base_eligible": len(elig_new),
                              "symmetric_difference": d,
                              "dropped": sorted(set(committed_fit) - set(elig_new)),
                              "added": sorted(set(elig_new) - set(committed_fit))},
              "q1_seed": q1, "q2_eligibility": q2, "decision": decision,
              "reported_not_judged": {
                  "world_497_j2": {b: next((r["null_surprises"] for r in rows if r["base"] == b
                                            and (r["gen_seed"], r["j"]) == (497, 2)), None) for b in BASES},
                  "r7_8_null_surprises_497_j2": ref.get((497, 2), {}).get("null_surprises"),
                  "mismatching_targets": sorted((r["base"], r["gen_seed"], r["j"], r["detected"], r["switches"])
                                                for r in rows if not r["matches_r7_8"])},
              "wall_s": round(time.perf_counter() - t0, 3)})
