"""census_meta_v2.py — FIRST ACTION, third iteration.

meta_v1 (results/census_meta_v1.json) cleared everything except D5_seq_fwd_fails:
measured register-domain growth is ~3.55^d (swap/rotation relations), so two depth-9
forward halves fit inside one 400k budget. dE halves moved to depth 10 — each half
alone now exhausts the budget. No other change.

meta_v0 (results/census_meta_v0.json) REJECTED the initial design on three counts:
a budget-enforcement leak let forward search claim goals past the meter (W1, D5);
dC's involution-heavy generators capped ball growth at ~2.4^d (no pathology); and
dD at 40% drops / 3 spurious still let meet-in-the-middle win (ratio 0.896). Fixes:
strict metering, free-growing dC generators, DROP 70% / SPURIOUS 6, and the W3
detection signal moved from meet-verify failures to the backward-edge AUDIT (replay
of claimed predecessor edges), which W4 showed separates dD from clean worlds
exactly. D5's naive-rank is now computed analytically over the sorted SEQ keys.

Two censuses before any learner exists, with pass bands stated first.

DSL CENSUS — is the answer hidden in the language?
  D1 SPACE        exact 1-stage program count and the sha of the frozen canonical
                  enumeration (recorded into the preregistration)
  D2 DIVERSITY    >= 10 behaviorally distinct organizations among 1-stage programs,
                  measured by instrumented traces on probe tasks (not by syntax)
  D3 NOT-SPELLED  meet-in-the-middle organizations (solve deep probe via 'meet' with
                  both processes expanded >= 2) are <= 8% of the space AND the first
                  one appears at canonical rank >= 25
  D4 REACHABLE    at least one meet-organization solves ALL deep probes within the
                  20k probe budget (the discovery is reachable by metered evaluation —
                  the v1 lesson: prove the gate reachable before reading any result)
  D5 E-STRUCTURE  1-stage programs cannot solve via-tasks; SEQ(fwd,fwd) busts budget;
                  SEQ(meet,meet) solves; first via-solving SEQ sits at canonical rank
                  >= 200 (the recursion probe is not trivially early for a naive
                  enumerator)

WORLD CENSUS — is the pressure real?
  W1 PATHOLOGY    baseline forward program: solve rate 0 on deep dA/dB/dC within the
                  400k budget; 100% on shallow tasks
  W2 CEILING      reference meet program (omniscient ceiling A3): 100% on deep
                  dA/dB/dC at <= 40k median ops
  W3 TRAP         dD: baseline solves 100%; A3-blind pays >= 1.5x baseline ops OR
                  loses solve rate; verify_failures > 0 on >= 90% of dD A3 runs and
                  == 0 across all dA/dB/dC runs (the detection signal)
  W4 GUARDABLE    the executable consistency probe (does apply(pid, cand) reproduce
                  the state?) separates dD from dA/dB/dC on 60 sampled states exactly
  W5 RECURSION    dE: A3 1-stage fails; SEQ(A3,A3) solves <= 120k; SEQ(A0,A0) fails
  W6 NO-PRESSURE  dW0 shallow: baseline 100% (the construction trigger has nothing
                  to fire on)
  W7 A1-FAIRNESS  report the planted trigram's presence in baseline shallow-dA
                  solutions (support for the v1-macro control)
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from domains import DEPTHS, PLANT_A, SHALLOW, make_domains          # noqa: E402
from dsl import BASELINE, classify, enumerate_stage, enumerate_seq, \
    enumeration_sha, serial                                          # noqa: E402
from runtime import run_program                                      # noqa: E402

BUDGET = 400_000
PROBE_BUDGET = 20_000
A3 = ("STAGE", (("A", "S"), ("Z", "P")), ("IF", "FSIZE", "LE", "FSIZE"), "MEET")


def gen(domain, seed, n, depth_pair, plant=None, via=False):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        d = depth_pair[i % 2]
        out.append(domain.gen_task(rng, d, plant=plant))
    return out


def med(xs):
    return statistics.median(xs) if xs else None


def main():
    t0 = time.time()
    doms = make_domains()
    rep = {"census": "meta_v2", "date": "2026-08-26",
           "budget": BUDGET, "probe_budget": PROBE_BUDGET}

    # ── DSL census ──────────────────────────────────────────────────────────────
    stage = enumerate_stage()
    rep["D1_space"] = {"n_stage_programs": len(stage),
                      "enumeration_sha": enumeration_sha(stage)}
    dA = doms["dA"]
    probes_deep = gen(dA, 901, 3, (10, 10))
    probes_shallow = gen(dA, 902, 1, (6, 6))
    sigs = {}
    bidir_ranks = []
    solve_all_deep = []
    for rank, prog in enumerate(stage):
        deep_results = [run_program(dA, t, prog, PROBE_BUDGET)
                        for t, _o in probes_deep]
        sh = run_program(dA, probes_shallow[0][0], prog, PROBE_BUDGET)
        r0 = deep_results[0]
        tr = r0["trace"]
        exp = tr["expansions"]
        tot = sum(exp.values()) or 1
        share = round(4 * exp.get(0, 0) / tot) / 4
        sig = (tuple(prog[1]), tuple(tr["gens"]), tr["halt"], r0["solved"],
               sh["solved"], share)
        sigs.setdefault(sig, []).append(rank)
        if all(r["solved"] and r["trace"]["halt"] == "meet"
               and len(r["trace"]["expansions"]) >= 2
               and min(r["trace"]["expansions"].values()) >= 2
               for r in deep_results):
            bidir_ranks.append(rank)
            solve_all_deep.append(rank)
    rep["D2_diversity"] = {"n_behavioral_classes": len(sigs)}
    rep["D3_not_spelled"] = {
        "n_meet_class": len(bidir_ranks),
        "frac_meet_class": round(len(bidir_ranks) / len(stage), 4),
        "first_meet_rank": bidir_ranks[0] if bidir_ranks else None,
        "first_meet_serial": serial(stage[bidir_ranks[0]]) if bidir_ranks else None}
    rep["D4_reachable"] = {"n_solving_all_deep_probes": len(solve_all_deep)}

    # D5: E-structure over SEQ space
    dE = doms["dE"]
    etasks = gen(dE, 903, 2, DEPTHS["dE"])
    a0 = BASELINE
    one_stage_on_via = run_program(dE, etasks[0][0], A3, BUDGET)
    seq_fwd = run_program(dE, etasks[0][0], ("SEQ", a0, a0), BUDGET)
    seq_meet = [run_program(dE, t, ("SEQ", A3, A3), BUDGET) for t, _o in etasks]
    seqs = enumerate_seq(stage)
    meet_set = {serial(stage[r]) for r in bidir_ranks}
    first_seq_rank = None
    for rank, prog in enumerate(seqs):
        if serial(prog[1]) in meet_set and serial(prog[2]) in meet_set:
            r = run_program(dE, etasks[0][0], prog, PROBE_BUDGET * 3)
            if r["solved"]:
                first_seq_rank = rank
                rep["D5_first_seq_serial"] = serial(prog)
                break
    rep["D5_e_structure"] = {
        "one_stage_A3_solves_via": one_stage_on_via["solved"],
        "seq_fwd_fwd_solves": seq_fwd["solved"],
        "seq_meet_meet_solves": all(r["solved"] for r in seq_meet),
        "seq_meet_meet_ops": [r["ops"] for r in seq_meet],
        "first_via_solving_seq_rank": first_seq_rank,
        "n_seq_programs": len(seqs)}

    # ── world census ────────────────────────────────────────────────────────────
    w = {}
    verify_fail_clean = 0
    clean_a3 = {}
    for wid in ("dA", "dB", "dC"):
        dom = doms[wid]
        plant = PLANT_A if wid in ("dA", "dB") else None
        deep = gen(dom, 911, 6, DEPTHS[wid], plant=plant)
        shal = gen(dom, 912, 4, SHALLOW[wid], plant=plant)
        a0_deep = [run_program(dom, t, BASELINE, BUDGET) for t, _o in deep]
        a0_shal = [run_program(dom, t, BASELINE, BUDGET) for t, _o in shal]
        a3_deep = [run_program(dom, t, A3, BUDGET, audit=True) for t, _o in deep]
        clean_a3[wid] = a3_deep
        verify_fail_clean += sum(r["trace"]["verify_failures"]
                                 for r in a0_deep + a0_shal + a3_deep)
        w[wid] = {"a0_deep_solved": sum(r["solved"] for r in a0_deep),
                  "a0_shallow_solved": sum(r["solved"] for r in a0_shal),
                  "a0_deep_med_ops": med([r["ops"] for r in a0_deep]),
                  "a3_deep_solved": sum(r["solved"] for r in a3_deep),
                  "a3_deep_med_ops": med([r["ops"] for r in a3_deep]),
                  "n_deep": len(deep), "n_shallow": len(shal),
                  "gen_sec": None}
        if wid == "dA":
            plant_pids = tuple(dom.pids[i] for i in PLANT_A)
            hits = 0
            for r in a0_shal:
                word = r["word"] or []
                if any(tuple(word[i:i + 3]) == plant_pids
                       for i in range(len(word) - 2)):
                    hits += 1
            w[wid]["plant_in_shallow_solutions"] = f"{hits}/{len(a0_shal)}"
    dD = doms["dD"]
    dtasks = gen(dD, 913, 8, DEPTHS["dD"])
    d_a0 = [run_program(dD, t, BASELINE, BUDGET) for t, _o in dtasks]
    d_a3 = [run_program(dD, t, A3, BUDGET, audit=True) for t, _o in dtasks]
    ratios = [a3["ops"] / a0["ops"] for a0, a3 in zip(d_a0, d_a3) if a0["ops"]]
    w["dD"] = {"a0_solved": sum(r["solved"] for r in d_a0),
               "a3_solved": sum(r["solved"] for r in d_a3),
               "a0_med_ops": med([r["ops"] for r in d_a0]),
               "a3_med_ops": med([r["ops"] for r in d_a3]),
               "a3_over_a0_med": round(med(ratios), 3) if ratios else None,
               "a3_runs_with_verify_failures": sum(
                   1 for r in d_a3 if r["trace"]["verify_failures"] > 0),
               "a3_runs_with_bad_bwd_edges": sum(
                   1 for r in d_a3 if r["trace"].get("bwd_inconsistent", 0) > 0),
               "n": len(dtasks)}
    w["clean_worlds_verify_failures_total"] = verify_fail_clean
    w["clean_worlds_bad_bwd_edges_total"] = sum(
        r["trace"].get("bwd_inconsistent", 0)
        for wid in ("dA", "dB", "dC") for r in clean_a3[wid])

    # W4 consistency probe
    def consistency_ok(dom, s):
        for pid, cand in dom.pred(s):
            if dom.apply(pid, cand) != s:
                return False
        return True
    rng = random.Random(914)
    probe_sep = {"dD_flagged": 0, "clean_flagged": 0, "n_each": 60}
    for _ in range(60):
        if not consistency_ok(dD, dD._rand_state(rng)):
            probe_sep["dD_flagged"] += 1
        for wid in ("dA", "dB", "dC"):
            if not consistency_ok(doms[wid], doms[wid]._rand_state(rng)):
                probe_sep["clean_flagged"] += 1
    w["W4_consistency_probe"] = probe_sep

    # W6 no-pressure control
    w0 = doms["dW0"]
    w0tasks = gen(w0, 915, 6, SHALLOW["dW0"])
    w0r = [run_program(w0, t, BASELINE, BUDGET) for t, _o in w0tasks]
    w["dW0"] = {"a0_solved": sum(r["solved"] for r in w0r),
                "a0_med_ops": med([r["ops"] for r in w0r]), "n": len(w0r)}
    rep["worlds"] = w

    # ── verdicts against the pre-stated bands ───────────────────────────────────
    d3, d5 = rep["D3_not_spelled"], rep["D5_e_structure"]
    v = {
        "D2_diversity_ge_10": rep["D2_diversity"]["n_behavioral_classes"] >= 10,
        "D3_frac_le_8pct": d3["frac_meet_class"] <= 0.08,
        "D3_rank_ge_25": (d3["first_meet_rank"] or 0) >= 25,
        "D4_reachable": rep["D4_reachable"]["n_solving_all_deep_probes"] >= 1,
        "D5_one_stage_cannot": not d5["one_stage_A3_solves_via"],
        "D5_seq_fwd_fails": not d5["seq_fwd_fwd_solves"],
        "D5_seq_meet_solves": d5["seq_meet_meet_solves"],
        "D5_rank_ge_200": (d5["first_via_solving_seq_rank"] or 10**9) >= 200,
        "W1_pathology": all(w[x]["a0_deep_solved"] == 0
                            and w[x]["a0_shallow_solved"] == w[x]["n_shallow"]
                            for x in ("dA", "dB", "dC")),
        "W2_ceiling": all(w[x]["a3_deep_solved"] == w[x]["n_deep"]
                          and w[x]["a3_deep_med_ops"] <= 40_000
                          for x in ("dA", "dB", "dC")),
        "W3_trap": (w["dD"]["a0_solved"] == w["dD"]["n"]
                    and ((w["dD"]["a3_over_a0_med"] or 0) >= 1.5
                         or w["dD"]["a3_solved"] < w["dD"]["n"])
                    and w["dD"]["a3_runs_with_bad_bwd_edges"]
                    >= 0.9 * w["dD"]["n"]
                    and w["clean_worlds_bad_bwd_edges_total"] == 0),
        "W4_guardable": (probe_sep["dD_flagged"] == probe_sep["n_each"]
                         and probe_sep["clean_flagged"] == 0),
        "W5_recursion": d5["seq_meet_meet_solves"]
        and all(o <= 120_000 for o in d5["seq_meet_meet_ops"]),
        "W6_no_pressure": w["dW0"]["a0_solved"] == w["dW0"]["n"],
    }
    rep["verdicts"] = v
    rep["FAILED"] = [k for k, val in v.items() if not val]
    rep["CENSUS_PASSES"] = not rep["FAILED"]
    rep["wall_sec"] = round(time.time() - t0, 1)

    out = os.path.join(os.path.dirname(HERE), "results", "census_meta_v2.json")
    with open(out, "w") as f:
        json.dump(rep, f, indent=1, default=str)
    print(json.dumps({k: rep[k] for k in ("D1_space", "D2_diversity",
                                          "D3_not_spelled", "D4_reachable",
                                          "D5_e_structure", "verdicts", "FAILED",
                                          "CENSUS_PASSES", "wall_sec")},
                     indent=1, default=str))
    print(f"[census_meta] written {out}")


if __name__ == "__main__":
    main()
