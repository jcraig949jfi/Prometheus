"""C-013-T011 challenge cases against FREEZE_D1 (Pallas, Q3). CHALLENGE_SET.md s2 is the specification; expected.json
the answer key, both committed before this file first ran.

    <venv python> rso/reach/challenge/D1/cases_d1.py --case S1 [--case B3 ...] | --all

Rules enforced here: development lineages only (DEV_* < 0: knock-out indices below 3000, disjoint from the calibration,
test and toy-runner ranges); toy budgets; blind mode wherever a hit could otherwise be observed and is not needed;
nothing under rso/reach/ is written; one process (the caller keeps <= 2). Appends one JSON row per case to
results_d1.jsonl beside this file.
"""
import argparse
import json
import math
import pathlib
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rso.reach import analyze, arms, certify, descriptor, stats          # noqa: E402
from rso.reach._proto import org, ru, wm                               # noqa: E402

RESULTS = HERE / "results_d1.jsonl"
DS = (1, 3, 8)
ARMS6 = analyze.ARMS
DEV_B2 = -3000          # B2b lineages -3000..-2997 (knock-out indices 2000..2003)
DEV_B3 = -3100          # B3 lineage (knock-out index 1900)
DEV_P2 = -3200          # P2 lineage (knock-out index 1800)

# Fields each opcode READS, from wm_mini.run_phase (field 1 = a, 2 = b, 3 = c; registers are taken mod 8; SET reads
# field 2 mod 64; JMP reads field 3 mod 16). A row's FUNCTIONAL key is (op, the values of its read fields mod their
# modulus); two rows with equal functional keys execute identically in every state.
FUNC_FIELDS = {
    wm.NOP: (), wm.IN: ((1, 8),), wm.PH: ((1, 8),), wm.SET: ((1, 8), (2, 64)), wm.MOV: ((1, 8), (2, 8)),
    wm.ADD: ((1, 8), (2, 8), (3, 8)), wm.SUB: ((1, 8), (2, 8), (3, 8)), wm.SKZ: ((1, 8),), wm.SKNZ: ((1, 8),),
    wm.SKEQ: ((1, 8), (2, 8)), wm.SKLT: ((1, 8), (2, 8)), wm.STW: ((1, 8), (2, 8)), wm.STR: ((1, 8), (2, 8)),
    wm.FW: ((1, 8), (2, 8)), wm.FR: ((1, 8), (2, 8)), wm.OUT: ((1, 8),), wm.HALT: (), wm.JMP: ((3, 16),),
    wm.XOR: ((1, 8), (2, 8), (3, 8)),
}
FIELD_RANGE = {1: 8, 2: 64, 3: 16}       # the operator's draw ranges (reach.py:108-111 / arms._mutate_into)


def fkey(row):
    op = int(row[0]) % wm.NOPS
    return (op,) + tuple(int(row[f]) % m for f, m in FUNC_FIELDS[op])


def fpath(g, start, target):
    """Functional analogue of arms._path_restored: -1 if off a shortest path functionally; else knocked rows restored."""
    r = 0
    for i in range(g.shape[0]):
        kt, ks, kg = fkey(target[i]), fkey(start[i]), fkey(g[i])
        knocked = kt != ks
        if not knocked:
            if kg != kt:
                return -1
        elif kg == kt:
            r += 1
        elif kg != ks:
            return -1
    return r


def unused_fields(row):
    op = int(row[0]) % wm.NOPS
    used = {f for f, _ in FUNC_FIELDS[op]}
    return [f for f in (1, 2, 3) if f not in used]


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record(case, observed, verdict, prediction_note, t0, c0):
    row = dict(case=case, started_at_utc=t0, finished_at_utc=now(), cpu_s=round(time.process_time() - c0, 2),
               verdict=verdict, prediction_note=prediction_note, observed=observed)
    with open(RESULTS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: row[k] for k in ("case", "verdict", "cpu_s")}))
    return row


# ------------------------------------------------------------------------------------------------ S1
def _sim_fwer(rate, mults, cap_frac, sims, seed, cache):
    rng = random.Random(seed)
    cap = None if cap_frac is None else cap_frac * 24 * 18 * 1.0
    fw, Ns, underp = 0, Counter(), 0
    for _ in range(sims):
        counts = {(a, d): 0 for a in ARMS6 for d in DS}
        cost, N = 0.0, 0
        for j in range(24):
            m = rng.choice(mults)
            for d in DS:
                p = min(1.0, rate * m)
                for a in ARMS6:
                    if rng.random() < p:
                        counts[(a, d)] += 1
                        cost += rng.random() + 0.02          # hit at a uniform time, plus certification
                    else:
                        cost += 1.0                          # a miss runs the whole budget
            N = j + 1
            if cap is not None and cost >= cap:
                break
        Ns[N] += 1
        if N < analyze.MIN_ROUNDS:
            underp += 1
            continue
        raw = {}
        for name, a, b in analyze.CONTRASTS:
            strata = tuple((counts[(a, d)], N, counts[(b, d)], N) for d in DS)
            if strata not in cache:
                cache[strata] = stats.stratified_exact(list(strata))
            raw[name] = cache[strata]
        adj = stats.holm(raw)
        fw += any(v <= analyze.ALPHA for v in adj.values())
    return dict(fwer=fw / sims, sims=sims, rounds_distribution={str(k): v for k, v in sorted(Ns.items())},
                underpowered=underp, cap=cap, rate=rate, multipliers=list(mults))


def case_S1():
    t0, c0 = now(), time.process_time()
    cache = {}
    obs = {
        "rate_1_24_cap": _sim_fwer(1 / 24, (1.0,), 0.75, 1000, 101, cache),
        "rate_1_24_nocap": _sim_fwer(1 / 24, (1.0,), None, 1000, 102, cache),
        "rate_0_25_shared_starts_cap": _sim_fwer(0.25, (0.5, 1.0, 1.5), 0.75, 600, 103, cache),
        "rate_0_25_shared_starts_nocap": _sim_fwer(0.25, (0.5, 1.0, 1.5), None, 600, 104, cache),
    }
    ok = all(v["fwer"] <= 0.05 for v in obs.values())
    varies = len(obs["rate_0_25_shared_starts_cap"]["rounds_distribution"]) > 1
    obs["stop_varies_with_outcomes"] = varies
    return record("S1_SOUND_NULL_STOP", obs, "AS_EXPECTED" if ok else "NOT_AS_PREDICTED",
                  "fwer <= 0.05 everywhere; N varies under the cap", t0, c0)


# ------------------------------------------------------------------------------------------------ S2
def case_S2():
    t0, c0 = now(), time.process_time()
    p24 = stats.power([1 / 24] * 3, [1 / 24 + 0.20] * 3, 24, 5, sims=2000, seed=2)
    p12 = stats.power([1 / 24] * 3, [1 / 24 + 0.20] * 3, 12, 5, sims=2000, seed=2)
    obs = dict(power_N24_plus020=p24, quoted_N24=0.82, power_N12_plus020=p12, quoted_N12=0.33)
    ok = 0.78 <= p24 <= 0.86 and 0.29 <= p12 <= 0.37
    return record("S2_SOUND_POWER_RECHECK", obs, "AS_EXPECTED" if ok else "NOT_AS_PREDICTED",
                  "within +-0.04 of the quoted values", t0, c0)


# ------------------------------------------------------------------------------------------------ S3
def target_synonyms(n, seed):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        g = arms.TARGET.copy()
        i = rng.randrange(8)
        uf = unused_fields(g[i])
        f = uf[rng.randrange(len(uf))]
        g[i, f] = rng.randrange(FIELD_RANGE[f])
        if not np.array_equal(g, arms.TARGET) and not any(np.array_equal(g, h) for h in out):
            out.append(g)
    return out


def case_S3():
    t0, c0 = now(), time.process_time()
    tgt_trace = descriptor.trace_hash(arms.TARGET)
    rows = []
    for g in target_synonyms(24, 20261011):
        c = certify.certify(g)
        f, nfix, _ = arms.train_eval(g)
        rows.append(dict(status=c["status"], training=f, trace_equal=descriptor.trace_hash(g) == tgt_trace,
                         selection=c["selection_probe"], sealed=c["sealed_verdict"]))
    n_cert = sum(r["status"] == "CERTIFIED" for r in rows)
    ok = n_cert == 24 and all(r["trace_equal"] and r["training"] == 126 for r in rows) and \
        not any(r["status"] == "VOID" for r in rows)
    obs = dict(certified=n_cert, of=24, all_trace_equal=all(r["trace_equal"] for r in rows),
               all_training_126=all(r["training"] == 126 for r in rows), rows=rows)
    return record("S3_SOUND_CERT_SYNONYMS", obs, "AS_EXPECTED" if ok else "NOT_AS_PREDICTED",
                  "24/24 certified, trace equal, training 126, no VOID", t0, c0)


# ------------------------------------------------------------------------------------------------ B1
def synthetic_ledger(counts, rounds=24, default=1):
    rows = []
    for j in range(rounds):
        for d in DS:
            for a in ARMS6:
                disc = j < counts.get((a, d), default)
                rows.append(dict(round=j, arm=a, d=d, discovery=disc, hit=disc, evals=1000 if disc else -1,
                                 certificate=({"status": "CERTIFIED", "certified": True} if disc else None), cells=10,
                                 distinct_genomes=100, stones_retained_end=0, stones_evaluated=0, max_stone_restored=0))
    return rows


def case_B1():
    t0, c0 = now(), time.process_time()
    counts = {("X3", 1): 18, ("X3", 3): 0, ("X3", 8): 0, ("X2", 1): 1, ("X2", 3): 4, ("X2", 8): 4}
    res = analyze.analyze(synthetic_ledger(counts))
    c4 = res["contrasts"]["C4_new_cell_admission_of_worse"]
    per_d = {str(d): dict(X3=counts[("X3", d)], X2=counts[("X2", d)],
                          direction=("X3 > X2" if counts[("X3", d)] > counts[("X2", d)] else "X3 < X2"))
             for d in DS}
    keys = sorted(c4.keys())
    het_field = any(k for k in keys if "strat" in k or "interaction" in k or "heterogen" in k or "per_d" in k)
    separated = c4["verdict"].startswith("SEPARATES") and c4["p_holm"] <= analyze.ALPHA
    direction_pooled = c4["verdict"].endswith("X3 > X2")
    strata_against = sum(1 for d in DS if counts[("X3", d)] < counts[("X2", d)])
    obs = dict(status=res["status"], C4=c4, per_stratum=per_d, contrast_output_keys=keys,
               heterogeneity_field_present=het_field, strata_pointing_the_other_way=strata_against,
               all_contrasts={k: v["verdict"] for k, v in res["contrasts"].items()})
    survivor = separated and direction_pooled and not het_field and strata_against == 2
    return record("B1_BROKEN_HETEROGENEITY", obs, "SURVIVOR" if survivor else "NOT_AS_PREDICTED",
                  "C4 SEPARATES X3 > X2 while two strata point the other way; no heterogeneity field", t0, c0)


# ------------------------------------------------------------------------------------------------ B2a
def case_B2a():
    t0, c0 = now(), time.process_time()
    d = 3
    _, _, kidx = arms._reach_streams("chain_neutral", d, DEV_B2, "fresh")
    start = arms.knock_out(d, kidx)
    knocked = [i for i in range(8) if not np.array_equal(start[i], arms.TARGET[i])]
    kept = [i for i in range(8) if i not in knocked]
    i, j = knocked[0], kept[0]
    exact = start.copy()
    exact[i] = arms.TARGET[i]
    funk = exact.copy()
    f_i = unused_fields(arms.TARGET[i])[0]
    funk[i, f_i] = {1: 5, 2: 37, 3: 11}[f_i]
    drift = start.copy()
    f_j = unused_fields(arms.TARGET[j])[0]
    drift[j, f_j] = {1: 5, 2: 37, 3: 11}[f_j]
    obs = dict(
        lineage=DEV_B2, knockout_index=kidx, knocked_rows=knocked, restored_row=i, junk_field=f_i, drift_row=j,
        drift_field=f_j,
        exact_restore=dict(path_restored=int(arms._path_restored(exact, start, arms.TARGET)), fpath=fpath(exact, start, arms.TARGET)),
        functional_restore=dict(path_restored=int(arms._path_restored(funk, start, arms.TARGET)), fpath=fpath(funk, start, arms.TARGET),
                                trace_equal_to_exact=descriptor.trace_hash(funk) == descriptor.trace_hash(exact),
                                train_eval_equal_to_exact=arms.train_eval(funk) == arms.train_eval(exact)),
        unused_field_drift_of_start=dict(path_restored=int(arms._path_restored(drift, start, arms.TARGET)), fpath=fpath(drift, start, arms.TARGET),
                                         trace_equal_to_start=descriptor.trace_hash(drift) == descriptor.trace_hash(start),
                                         train_eval_equal_to_start=arms.train_eval(drift) == arms.train_eval(start)),
        start=start.tolist(), functional_intermediate=funk.tolist(), drifted_start=drift.tolist())
    fr, dr = obs["functional_restore"], obs["unused_field_drift_of_start"]
    survivor = fr["path_restored"] == -1 and dr["path_restored"] == -1 and fr["trace_equal_to_exact"] and \
        dr["trace_equal_to_start"] and fr["fpath"] == 1 and dr["fpath"] == 0 and obs["exact_restore"]["path_restored"] == 1
    return record("B2a_BROKEN_STONE_SYNONYM", obs, "SURVIVOR" if survivor else "NOT_AS_PREDICTED",
                  "exact predicate says off-path for a behaviourally identical intermediate and for an unused-field drift of the start", t0, c0)


# ------------------------------------------------------------------------------------------------ B2b
def instrumented_lineage(arm, d, lineage, budget):
    seed, s, kidx = arms._reach_streams(arm, d, lineage, "fresh")
    start = arms.knock_out(d, kidx)
    nfix = arms.train_eval(arms.TARGET)[1]
    st = dict(i=-1, exact_stones=0, func_stones=0, last_exact_onpath=-1, last_func_onpath=-1, max_exact=0, max_func=0,
              evaluations=0)

    def propose(p, i):
        st["i"] = i
        return arms.mutate(p, seed, s, d, i)

    def evaluate(p):
        p = np.asarray(p)
        re_, rf = int(arms._path_restored(p, start, arms.TARGET)), fpath(p, start, arms.TARGET)
        st["evaluations"] += 1
        if re_ >= 0:
            st["last_exact_onpath"] = st["i"]
            st["max_exact"] = max(st["max_exact"], re_)
            if 1 <= re_ <= d - 1:
                st["exact_stones"] += 1
        if rf >= 0:
            st["last_func_onpath"] = st["i"]
            st["max_func"] = max(st["max_func"], rf)
            if 1 <= rf <= d - 1:
                st["func_stones"] += 1
        f, _, k = arms.train_eval(p)
        return f, k

    def rng_u(i):
        return float(arms._uniform(seed, s, d, i))

    r = arms.run_ladder(arm, start, evaluate, propose, budget, nfix, rng_u, sort_key=lambda c: c, ident=arms.genome_hash)
    archive = r.pop("archive")
    ret_exact = sum(1 for g in archive if 1 <= int(arms._path_restored(np.asarray(g), start, arms.TARGET)) <= d - 1)
    ret_func = sum(1 for g in archive if 1 <= fpath(np.asarray(g), start, arms.TARGET) <= d - 1)
    onpath_end_exact = sum(1 for g in archive if int(arms._path_restored(np.asarray(g), start, arms.TARGET)) >= 0)
    onpath_end_func = sum(1 for g in archive if fpath(np.asarray(g), start, arms.TARGET) >= 0)
    return dict(arm=arm, d=d, lineage=lineage, knockout_index=kidx, budget=budget, hit=r["evals"] >= 0, evals=r["evals"],
                accepted=r["accepted"], cells=r["cells"], start_fit=int(arms.train_eval(start)[0]),
                production_stones_evaluated=st["exact_stones"], functional_stones_evaluated=st["func_stones"],
                last_proposal_exact_onpath=st["last_exact_onpath"], last_proposal_functional_onpath=st["last_func_onpath"],
                max_exact_restored=st["max_exact"], max_functional_restored=st["max_func"],
                production_stones_retained_end=ret_exact, functional_stones_retained_end=ret_func,
                archive_size=len(archive), archive_onpath_exact=onpath_end_exact, archive_onpath_functional=onpath_end_func)


def case_B2b():
    t0, c0 = now(), time.process_time()
    rows = []
    for arm in ("chain_neutral", "X3"):
        for lin in range(DEV_B2, DEV_B2 + 4):
            rows.append(instrumented_lineage(arm, 3, lin, 20_000))
            print(json.dumps(rows[-1]), flush=True)
    zero_prod = sum(1 for r in rows if r["production_stones_evaluated"] == 0)
    chain = [r for r in rows if r["arm"] == "chain_neutral"]
    short_life = sum(1 for r in chain if r["last_proposal_exact_onpath"] <= 50)
    func_small = all(r["functional_stones_evaluated"] <= 5 for r in rows)
    x3 = [r for r in rows if r["arm"] == "X3"]
    x3_none = all(r["production_stones_retained_end"] == 0 and r["functional_stones_retained_end"] == 0 for r in x3)
    obs = dict(rows=rows, lineages_with_zero_production_stones=zero_prod, chain_exact_lifetime_le_50=short_life,
               functional_le_5_everywhere=func_small, x3_retains_no_stone_either_predicate=x3_none,
               any_hit_observed=any(r["hit"] for r in rows))
    survivor = zero_prod >= 7 and x3_none
    return record("B2b_BROKEN_STONES_DRIFT", obs, "SURVIVOR" if survivor else "NOT_AS_PREDICTED",
                  ">= 7/8 lineages with zero production stones and X3 retains none: the s7 premise is vacuous", t0, c0)


# ------------------------------------------------------------------------------------------------ B3
def case_B3():
    t0, c0 = now(), time.process_time()
    b = 40_000
    out = {}
    for d in (3, 8):
        full = arms.run_reach_lineage("X3", d, DEV_B3, budget=b, impl="nb", blind=True)
        assert full["evals"] == -1
        B = int(full["cells"])
        traj = {}
        for k in (b // 8, b // 4, b // 2, b):
            x3 = arms.run_reach_lineage("X3", d, DEV_B3, budget=k, impl="nb", blind=True)
            x3g = arms.run_reach_lineage("X3G", d, DEV_B3, budget=k, impl="nb", blind=True, geno_buckets=B)
            assert x3["evals"] == -1 and x3g["evals"] == -1
            traj[str(k)] = dict(X3_cells=x3["cells"], X3G_cells=x3g["cells"], ratio=round(x3g["cells"] / max(1, x3["cells"]), 3),
                                X3_accepted=x3["accepted"], X3G_accepted=x3g["accepted"],
                                X3_new_cells=x3["new_cells_admitted"], X3G_new_cells=x3g["new_cells_admitted"],
                                X3_distinct=x3["distinct_genomes"], X3G_distinct=x3g["distinct_genomes"],
                                X3G_fill_fraction=round(x3g["cells"] / B, 3), X3_fraction_of_final=round(x3["cells"] / B, 3))
            print(d, k, json.dumps(traj[str(k)]), flush=True)
        x1 = arms.run_reach_lineage("X1", d, DEV_B3, budget=b, impl="nb", blind=True)
        x2 = arms.run_reach_lineage("X2", d, DEV_B3, budget=b, impl="nb", blind=True)
        out[str(d)] = dict(B_matched_at_toy_budget=B, trajectory=traj, X1_cells_at_b=x1["cells"], X2_cells_at_b=x2["cells"],
                           X2_over_X3_at_b=round(x2["cells"] / B, 4))
    q = {d: out[d]["trajectory"][str(b // 4)] for d in ("3", "8")}
    ratio_ok = all(q[d]["ratio"] >= 2.0 for d in q)
    fill_ok = all(q[d]["X3G_fill_fraction"] >= 0.85 and q[d]["X3_fraction_of_final"] <= 0.40 for d in q)
    x2_ok = all(out[d]["X2_over_X3_at_b"] <= 0.05 for d in out)
    obs = dict(budget=b, lineage=DEV_B3, by_d=out, ratio_ge_2_at_quarter=ratio_ok, fill_prediction=fill_ok, x2_le_5pct=x2_ok)
    return record("B3_BROKEN_C5_SIZE_TRAJECTORY", obs, "SURVIVOR" if ratio_ok else "NOT_AS_PREDICTED",
                  "X3G/X3 cells >= 2 at b/4 for d=3 and d=8", t0, c0)


# ------------------------------------------------------------------------------------------------ P1
def family(seed=20261011):
    rng = random.Random(seed)
    fam = {"builder_min": arms.TARGET, "holder": org.holder(certify.P.K), "constant": org.constant(), "lookup": org.lookup(),
           "empty": np.zeros((8, 4), dtype=np.int64)}
    for m in range(4, 9):
        fam["builder(%d)" % m] = org.builder(m)
    for k in range(24):
        fam["random_%02d" % k] = np.array([[rng.randrange(wm.NOPS), rng.randrange(8), rng.randrange(64), rng.randrange(16)]
                                           for _ in range(8)], dtype=np.int64)
    return fam


def case_P1():
    t0, c0 = now(), time.process_time()
    rows = {}
    for name, prog in family().items():
        c = certify.certify(prog)
        rows[name] = dict(selection_ok=c["selection_ok"], selection=c["selection_probe"], sealed=c["sealed_verdict"],
                          sealed_probe=c["sealed_probe"], status=c["status"])
    sel_pass_sealed_not_pass = [n for n, r in rows.items() if r["selection_ok"] and r["sealed"] != ru.PASS]
    impostors_fail_selection = all(not rows[n]["selection_ok"] for n in ("holder", "constant", "lookup", "empty"))
    sealed_rejects_alone = [n for n, r in rows.items() if r["selection_ok"] and r["status"] == "NOT_CERTIFIED"]
    bands = dict(select_lives=[certify.SELECT0, certify.SELECT0 + certify.N_SELECT - 1],
                 rulers_SELECT_LIVES=[ru.SELECT_LIVES.start, ru.SELECT_LIVES.stop - 1],
                 rulers_TRAIN_LIVES=[ru.TRAIN_LIVES.start, ru.TRAIN_LIVES.stop - 1],
                 select_inside_a_declared_band=(certify.SELECT0 in ru.SELECT_LIVES or certify.SELECT0 in ru.TRAIN_LIVES))
    obs = dict(rows=rows, selection_ok_but_sealed_not_pass=sel_pass_sealed_not_pass, impostors_fail_selection=impostors_fail_selection,
               rejected_by_sealed_alone=sealed_rejects_alone, builder6=rows["builder(6)"], builder7=rows["builder(7)"], bands=bands)
    return record("P1_PROBE_GATE_REDUNDANCY", obs, "RECORDED", "sealed gate never decides alone in this family", t0, c0)


# ------------------------------------------------------------------------------------------------ P2
def case_P2():
    t0, c0 = now(), time.process_time()
    from rso.reach import run_d1
    row = run_d1._worker(("X3", 3, DEV_P2, 500, None, False))
    keys = sorted(row.keys())
    anc = [k for k in keys if any(w in k for w in ("ancest", "parent", "lineage_trace", "route", "history", "visited"))]
    obs = dict(keys=keys, ancestry_like_keys=anc, hit=row["hit"], note="lineage key is the lineage index, not a trace")
    return record("P2_PROBE_LEDGER_ANCESTRY", obs, "RECORDED", "no ancestry field", t0, c0)


# ------------------------------------------------------------------------------------------------ P3
def case_P3():
    t0, c0 = now(), time.process_time()
    rows = {}
    for i in range(8):
        row = arms.TARGET[i]
        used = FUNC_FIELDS[int(row[0])]
        p_func = 1 / 8 / wm.NOPS                      # position, then opcode
        for f, m in used:                             # each read field must agree mod its modulus (m divides the range)
            p_func /= m
        p_exact = 1 / 8 / wm.NOPS / 8 / 64 / 16       # all four fields exactly (unused fields of the target are 0)
        rows["row %d %s" % (i, wm.OPNAMES[int(row[0])])] = dict(p_exact_per_proposal=p_exact, p_functional_per_proposal=p_func,
                                                               exact_over_functional=round(p_exact / p_func, 6),
                                                               expected_proposals_functional=round(1 / p_func),
                                                               expected_proposals_exact=round(1 / p_exact))
    return record("P3_PROBE_RESTORE_ODDS", rows, "RECORDED", "exact/functional 1/1024, 1/512, 1/16", t0, c0)


CASES = {"S1": case_S1, "S2": case_S2, "S3": case_S3, "B1": case_B1, "B2a": case_B2a, "B2b": case_B2b, "B3": case_B3,
         "P1": case_P1, "P2": case_P2, "P3": case_P3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    names = list(CASES) if a.all else a.case
    if not names:
        ap.error("--case or --all")
    for n in names:
        CASES[n]()


if __name__ == "__main__":
    main()
