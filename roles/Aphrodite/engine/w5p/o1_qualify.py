"""O1 qualification on the EXPOSED W9-H pilot seeds 0-2 (protocol frozen in O1_REPAIR.md s0 before any run).

Reuses the ecology lead's runner (science/b03_ecology/w9h_pilot_discovery.py): roles W9H-R1 (discovery/ROLES.json),
oracle_start, escrow setter, transfer job. The only difference from its stages is the donor option o1=True (and the
meter ON, so both ledgers are billed). Donors never read W9H_TRUTH.json except oracle_start's START content (the
known-positive control's definition, as in the eco pilot); truth is joined in `score` only.

Usage (from anywhere):  python o1_qualify.py <stage> [workers]
  stages: oracle_300k | oracle_30k | gen1_30k | tx | score
"""
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
ECO = HERE.parents[1] / "science" / "b03_ecology"
sys.path.insert(0, str(ECO))
sys.path.insert(0, str(HERE.parent))
import w9h_pilot_discovery as D  # noqa: E402  (imports w5p.harness -> b02 first)
from w5p import harness as H  # noqa: E402

OUT = HERE / "o1_runs"
SEEDS = [0, 1, 2]
BARE = re.compile(r"P_[0-9a-f]{12}\(\{H\}\)")


def log(m):
    print("[O1 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def run_donor(a):
    stage, seed, fams, start, esc = a
    D._set_escrow(esc)
    t0, c0 = time.time(), time.process_time()
    r = H.run(("O1-%s" % stage, "g11", "O10", seed, fams, {}, start, {"promote": True, "meter": True, "o1": True}))
    import a17
    assert a17.ESCROW == esc, (a17.ESCROW, esc)
    r.update({"stage": stage, "escrow": esc, "cpu_s": round(time.process_time() - c0, 1),
              "wall_s": round(time.time() - t0, 1)})
    return r


def stage_donors(stage, workers=2):
    roles = D.rj(D.OUT / "ROLES.json")
    outp = OUT / ("%s.jsonl" % stage)
    OUT.mkdir(parents=True, exist_ok=True)
    done = {r["seed"] for r in D.rdl(outp)}
    jobs = []
    for s in SEEDS:
        if s in done:
            continue
        fams = roles["W9H:%d" % s]["families"]
        if stage == "gen1_30k":
            jobs.append((stage, s, fams, None, D.ESC_STD))
        else:
            truth = D.rj(D.PILOT / "W9H_TRUTH.json")["W9H:%d" % s]       # START content only (known-positive control)
            H.init_worker()
            jobs.append((stage, s, fams, D.oracle_start(truth), D.ESC_HI if stage == "oracle_300k" else D.ESC_STD))
    if not jobs:
        return
    with open(outp, "a", encoding="utf-8") as fh, ProcessPoolExecutor(min(workers, len(jobs)),
                                                                     initializer=H.init_worker) as ex:
        for r in ex.map(run_donor, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            o = r["w5p"].get("o1", {})
            log("%s seed %d sel=%s schema=%s derived=%d (w/P %d) obs=%d (O1 hits %s) classes=%d depth_sel=%s cpu=%ss"
                % (stage, r["seed"], r["selected"], r["selected_schema"], r["n_derived"],
                   r["w5p"]["n_derived_with_promoted"], r["n_observed"], o.get("n_hits"), r["classes"],
                   r["w5p"]["dag_depth_selected"], r["cpu_s"]))


# ------------------------------------------------------------------ scoring helpers (truth joined here only)
def _nkey(s):
    import identity as I
    return I.term_str(I.normalise(I.parse(s.replace("{H}", "HOLEVAR_W9H"))))


def _registry(r):
    from w5p import promote as W
    return W.load_records(r["w5p"]["promoted_in"])


def true_match(r, schema, truth):
    """S2: equal up to W5 canonicalisation to a TRUE composition (normalised expansion, or equal W5P instantiation
    set of P_b-schema[{H} := P_a({H})] under the run's registry). Returns matching composition ids."""
    from w5p import promote as W
    if not schema or not W.has_promoted(schema):
        return []
    reg = _registry(r)
    exp = W.expand(schema, reg)
    pid = {}
    for m in truth["mechanisms"]:
        for p in reg.values():
            if _nkey(p.schema) == _nkey(m["schema"]) and not p.deps:
                pid[m["id"]] = p.id
    inst = None
    out = []
    for c in truth["compositions"]:
        if _nkey(exp) == _nkey(c["schema"]):
            out.append(c["id"])
            continue
        if c["inner"] in pid and c["outer"] in pid:
            if inst is None:
                inst = set(W.instantiate(schema, reg))
            ref = reg[pid[c["outer"]]].schema.replace("{H}", "%s({H})" % pid[c["inner"]])
            if inst and inst == set(W.instantiate(ref, reg)):
                out.append(c["id"])
    return out


def stage_score():
    H.init_worker()
    import a18
    a18.use_world("W5")
    truths = D.rj(D.PILOT / "W9H_TRUTH.json")
    res = {}
    for stage in ("oracle_300k", "oracle_30k", "gen1_30k"):
        st = {}
        for r in D.rdl(OUT / ("%s.jsonl" % stage)):
            key = "W9H:%d" % r["seed"]
            tr = truths[key]
            sel = r["selected_schema"]
            dp = r["w5p"]["derived_with_promoted"]
            cand_match = {s: true_match(r, s, tr) for s in dp}
            s1 = bool(sel and r["w5p"]["dag_depth_selected"] >= 2 and not BARE.fullmatch(sel))
            s2 = true_match(r, sel, tr) if sel else []
            o1 = r["w5p"].get("o1", {})
            fam_lv = tr["families"]
            st[key] = {"selected": r["selected"], "selected_schema": sel,
                       "selected_expansion": r["w5p"]["selected_schema_expansion"],
                       "S1_nontrivial_depth2_selected": s1, "S2_selected_true_compositions": s2,
                       "n_observed": r["n_observed"], "classes": r["classes"], "n_derived": r["n_derived"],
                       "n_derived_with_promoted": len(dp), "derived_with_promoted": dp,
                       "candidate_true_compositions": {s: m for s, m in cand_match.items() if m},
                       "nontrivial_depth2_candidates": [s for s in dp if not BARE.fullmatch(s)],
                       "o1_entry_bodies": o1.get("entry_bodies"), "o1_charges": o1.get("charges"),
                       "o1_hits": o1.get("n_hits"),
                       "o1_hit_levels": [fam_lv.get(h["family"], {}).get("level") for h in o1.get("hits", [])],
                       "o1_hit_srcs": [fam_lv.get(h["family"], {}).get("src") for h in o1.get("hits", [])],
                       "selection_table": r.get("selection_table"), "meta_charges": r["meta_charges"],
                       "cost": r["w5p"]["cost"]["total"] if r["w5p"].get("cost") else None,
                       "cpu_s": r["cpu_s"], "wall_s": r["wall_s"]}
        res[stage] = st
    # gen-1 no-op check against the eco pilot's recorded gen1_30k rows
    keys = ("selected", "selected_schema", "selected_entries", "n_observed", "n_derived", "classes", "meta_charges")
    ref = {r["seed"]: r for r in D.rdl(D.OUT / "gen1_30k.jsonl")}
    mine = {r["seed"]: r for r in D.rdl(OUT / "gen1_30k.jsonl")}
    res["gen1_noop_vs_eco_gen1_30k"] = {s: {k: mine[s].get(k) == ref[s].get(k) for k in keys if k in ref[s]}
                                        for s in mine if s in ref}
    tx = D.rdl(OUT / "tx.jsonl")
    if tx:
        rows = {r["name"]: r for r in D.rdl(D.PILOT / "W9H_FOUNDRY.jsonl")}
        o = {}
        for s in SEEDS:
            rr = [x for x in tx if x["seed"] == s]
            if not rr:
                continue
            pr = {x["name"]: sum(not w["censored"] for w in rows[x["name"]]["PRISTINE_TX"]) for x in rr}
            sel = {x["name"]: sum(not w["censored"] for w in x["walks"]) for x in rr}
            ext = {x["name"]: any((not w["censored"]) and w["EXTEND"] for w in x["walks"]) for x in rr}
            o["W9H:%d" % s] = {"L2_families": len(rr), "reached_selected": sum(v > 0 for v in sel.values()),
                               "reached_pristine": sum(v > 0 for v in pr.values()),
                               "reached_selected_not_pristine": sum(sel[n] > 0 and pr[n] == 0 for n in sel),
                               "S3_EXTEND_selected_not_pristine": sum(ext[n] and pr[n] == 0 for n in sel),
                               "fp_B1": sum(1 for x in rr for w in x["walks"] if not w["censored"]
                                            and not w.get("equal_B1")),
                               "cpu_s": round(sum(x["cpu_s"] for x in rr), 1)}
        res["tx"] = o
    passes = {}
    for key, v in res.get("oracle_300k", {}).items():
        s3 = res.get("tx", {}).get(key, {}).get("S3_EXTEND_selected_not_pristine", 0) >= 1
        passes[key] = {"S1": v["S1_nontrivial_depth2_selected"], "S2": bool(v["S2_selected_true_compositions"]),
                       "S3": s3, "candidacy_true_composition": bool(v["candidate_true_compositions"]),
                       "PASS": v["S1_nontrivial_depth2_selected"] and bool(v["S2_selected_true_compositions"]) and s3}
    res["criterion_300k"] = passes
    cpu = {st: round(sum(r["cpu_s"] for r in D.rdl(OUT / ("%s.jsonl" % st))), 1)
           for st in ("oracle_300k", "oracle_30k", "gen1_30k")}
    cpu["tx"] = round(sum(x["cpu_s"] for x in tx), 1)
    res["cpu_s"] = cpu
    D.wj(OUT / "O1_SCORE.json", res)
    print(json.dumps({k: res[k] for k in ("criterion_300k", "cpu_s", "gen1_noop_vs_eco_gen1_30k")}, indent=1))
    return res


def stage_tx(workers=2):
    """S3 transfer walks for seeds passing S1+S2 at 300k (declared cost control), with the eco runner's _tx_job."""
    import w9h_admit as A
    sc = D.rj(OUT / "O1_SCORE.json")
    ok = [int(k.split(":")[1]) for k, v in sc["criterion_300k"].items() if v["S1"] and v["S2"]]
    rows = D.rdl(D.PILOT / "W9H_FOUNDRY.jsonl")
    adm = A.admit(rows, D.rj(D.PILOT / "W9H_TRUTH.json"))
    by = {r["name"]: r for r in rows}
    don = {r["seed"]: r for r in D.rdl(OUT / "oracle_300k.jsonl")}
    outp = OUT / "tx.jsonl"
    done = {(r["seed"], r["name"]) for r in D.rdl(outp)}
    jobs = [(s, don[s]["selected_entries"], by[n]) for s in ok
            for n, a in sorted(adm.items()) if a["seed"] == "W9H:%d" % s and a["admitted"] and a["level"] == "L2"
            and (s, n) not in done]
    log("tx seeds %s jobs %d" % (ok, len(jobs)))
    if not jobs:
        return
    with open(outp, "a", encoding="utf-8") as fh, ProcessPoolExecutor(workers, initializer=A.init_worker) as ex:
        for r in ex.map(D._tx_job, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


def _diag(a):
    """Diagnostic re-run (post-outcome, NOT part of the criterion): identical donor call to run_donor, but returns the
    full selection table (harness.run, frozen for E5-N, drops it)."""
    stage, seed, fams, start, esc = a
    D._set_escrow(esc)
    H.init_worker()
    import a17
    import a18_c1
    from w5p import donor as DN
    a17.R_VAL = a18_c1.R_VAL_C1
    c0 = time.process_time()
    fl = [dict(f, qualified_dev_size=f["Q2_size"]) for f in fams]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}
    args = ("LIN%d" % seed, "P", seed, fl, specs, {}, True, start)
    r = DN.donor_w5p("g10", args, exclude=("MEMORISE",), promote=True, meter=False, o1=True)
    return {"seed": seed, "selected": r["selected"], "selected_schema": r["selected_schema"],
            "selection_table": r["selection_table"], "derived_with_promoted": r["w5p"]["derived_with_promoted"],
            "cpu_s": round(time.process_time() - c0, 1)}


def stage_diag(seed):
    truth = D.rj(D.PILOT / "W9H_TRUTH.json")["W9H:%d" % seed]
    H.init_worker()
    fams = D.rj(D.OUT / "ROLES.json")["W9H:%d" % seed]["families"]
    with ProcessPoolExecutor(1, initializer=H.init_worker) as ex:
        r = list(ex.map(_diag, [("diag", seed, fams, D.oracle_start(truth), D.ESC_HI)]))[0]
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "diag_selection_300k.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
    log("diag seed %d sel=%s cpu=%s" % (seed, r["selected_schema"], r["cpu_s"]))


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    if st in ("oracle_300k", "oracle_30k", "gen1_30k"):
        stage_donors(st, w)
    elif st == "tx":
        stage_tx(w)
    elif st == "score":
        stage_score()
    elif st == "diag":
        stage_diag(w)
