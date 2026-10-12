"""W08 DISCOVERY PILOT on the EXPOSED W9-H pilot seeds 0-2 (development data; never confirmatory).

Machinery: engine/w5p/harness.run (W5P donor, promotion ON, rule g11), unchanged. The donor reads only the role list
(name, role, body, init, final, Q2_size, p_PRISTINE -- exactly b02.plan_seed's keep-set). It never reads
W9H_TRUTH.json; truth is joined AFTER the run, in `score`.

Role rule W9H-R1 (arm-neutral, truth-free; the minimal change to A19 + T12 extras, see E5H_DESIGN_NOTES.md s2):
  pool = admitted families of the seed (W9-H admission includes the A19 window p_PRISTINE <= .75);
  seeded shuffle "APHRODITE/W9H/ROLES/<seed>"; OBSERVE 10, VALIDATE 12, TRANSFER = the rest.
  = A19 O10/V12 widths with the OBSERVE floor (0 < p_PRISTINE) DROPPED, because the floor pool is 1-4 families per
  seed (< the 4 + 6 required).

Arms (stage names):
  gen1_30k    pristine start, escrow 30k (the standard)                                      (a)
  cand_300k   pristine start, escrow 300k everywhere, CANDIDACY-ONLY probe: the selector is a stub that records the
              candidate set and returns INHERITED without walking (so no validation cost). The full g11 donor at
              300k is run only for seeds whose candidate set contains a true mechanism (cost control; declared).   (b)
  gen1_300k   full g11 donor at 300k (only if cand_300k found a true-mechanism candidate)                         (b)
  oracle_30k  KNOWN-POSITIVE gen-2 control: START = every TRUE level-1 mechanism of the seed as a schema entry
              (W5P promotes each to P_i in P1), then PRISTINE; escrow 30k; rule g11. Sensitivity control only.     (c)
  oracle_cand_300k / oracle_300k   the same known-positive start at escrow 300k: candidacy probe first, the full
              g11 donor only for seeds whose 300k candidate set holds a non-trivial depth-2 schema (cost control).
  oracle_tx   transfer walks (2 cells x cap 1M, the W9H-tx cells) of oracle_30k's SELECTED library on every admitted
              L2 family of the seed; PRISTINE on the same cells is reused from W9H_FOUNDRY (identical cells).
Usage: python w9h_pilot_discovery.py <stage> [workers]   stages: roles gen1_30k cand_300k gen1_300k oracle_30k
       oracle_tx score
"""
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
HERE = Path(__file__).resolve().parent
ENG = HERE.parents[1] / "engine"
sys.path.insert(0, str(ENG))
from w5p import harness as H  # noqa: E402  (imports b02 first: A18_TAG=T51, escrow 30k)
import b02  # noqa: E402

PILOT = HERE / "pilot"
OUT = HERE / "discovery"
SEEDS = [int(x) for x in os.environ.get("W9H_DISC_SEEDS", "0,1,2").split(",")]
N_OBS, N_VAL = 10, 12
ESC_STD, ESC_HI = 30_000, 300_000
CAP = 1_000_000
KEEP = ("name", "body", "init", "final", "Q2_size", "p_PRISTINE")


def log(m):
    print("[W9H-DISC %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def rdl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def rj(p):
    return json.loads(p.read_text(encoding="utf-8"))


def wj(p, o):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(o, indent=1, sort_keys=True, default=str), encoding="utf-8")


# ------------------------------------------------------------------ roles (truth is read ONLY to apply admission)
def stage_roles():
    sys.path.insert(0, str(HERE))
    import identity as I
    import w9h_admit as A
    rows = rdl(PILOT / "W9H_FOUNDRY.jsonl")
    adm = A.admit(rows, rj(PILOT / "W9H_TRUTH.json"))     # admission = world definition, fixed before any donor
    by = {r["name"]: r for r in rows}
    roles = {}
    for s in SEEDS:
        key = "W9H:%d" % s
        pool = sorted(n for n, a in adm.items() if a["seed"] == key and a["admitted"])
        floor = [n for n in pool if 0 < by[n].get("p_PRISTINE", 0) <= 0.75]
        rng = random.Random(I._seed("APHRODITE/W9H/ROLES/%d" % s))
        rng.shuffle(pool)
        fams = ([dict({k: by[n][k] for k in KEEP}, role="OBSERVE") for n in pool[:N_OBS]] +
                [dict({k: by[n][k] for k in KEEP}, role="VALIDATE") for n in pool[N_OBS:N_OBS + N_VAL]] +
                [dict({k: by[n][k] for k in KEEP}, role="TRANSFER") for n in pool[N_OBS + N_VAL:]])
        roles[key] = {"families": fams, "pool": len(pool), "a19_observe_floor_pool": len(floor),
                      "a19_fillable": len(floor) >= 4 + 6}
    wj(OUT / "ROLES.json", roles)
    log({k: (v["pool"], v["a19_observe_floor_pool"]) for k, v in roles.items()})


# ------------------------------------------------------------------ donor jobs
_CANDS = {}


def stub_select(cands, start, cells):
    """Candidacy-only probe: record candidate schemas, select INHERITED, walk nothing."""
    _CANDS["c"] = {k: {"schema": v[0].get("schema"), "schemas": v[0].get("schemas"),
                       "schema_expansion": v[0].get("schema_expansion"), "n_bodies": len(v[0].get("bodies", []))}
                   for k, v in cands.items() if k not in ("INHERITED", "MEMORISE")}
    return "INHERITED", {}, 0


def _set_escrow(esc):
    b02.T.ESC = esc                      # t51_natural.init_worker sets a17/fair.ESCROW from this module global


def run_donor(a):
    stage, seed, fams, start, esc, probe = a
    _set_escrow(esc)
    t0, c0 = time.time(), time.process_time()
    opts = {"promote": True, "meter": False}
    if probe:
        opts["select"] = stub_select
    r = H.run(("W9H-%s" % stage, "g11", "O10", seed, fams, {}, start, opts))
    import a17
    assert a17.ESCROW == esc, (a17.ESCROW, esc)
    r.update({"stage": stage, "escrow": esc, "cpu_s": round(time.process_time() - c0, 1),
              "wall_s": round(time.time() - t0, 1), "candidates": _CANDS.pop("c", None) if probe else None})
    return r


def oracle_start(truth):
    import a17
    import fair as FR
    return [a17.schema_entry("oracle_%s" % m["id"], m["schema"]) for m in truth["mechanisms"]] + FR.pristine().entries


def stage_donors(stage, workers=2):
    roles = rj(OUT / "ROLES.json")
    outp = OUT / ("%s.jsonl" % stage)
    done = {r["seed"] for r in rdl(outp)}
    jobs = []
    for s in SEEDS:
        if s in done:
            continue
        fams = roles["W9H:%d" % s]["families"]
        if stage == "gen1_30k":
            jobs.append((stage, s, fams, None, ESC_STD, False))
        elif stage == "cand_300k":
            jobs.append((stage, s, fams, None, ESC_HI, True))
        elif stage == "gen1_300k":
            cand = {r["seed"]: r for r in rdl(OUT / "cand_300k.jsonl")}
            sc = rj(OUT / "SCORE.json") if (OUT / "SCORE.json").exists() else {}
            if sc.get("cand_300k", {}).get("W9H:%d" % s, {}).get("true_mechanism_candidates"):
                jobs.append((stage, s, fams, None, ESC_HI, False))
            else:
                log("gen1_300k seed %d skipped: no true-mechanism candidate at 300k (cand_300k)" % s)
        elif stage in ("oracle_30k", "oracle_cand_300k", "oracle_300k"):
            if stage == "oracle_300k":
                sc = rj(OUT / "SCORE.json").get("oracle_cand_300k", {}).get("W9H:%d" % s, {})
                if not sc.get("nontrivial_depth2_candidates"):
                    log("oracle_300k seed %d skipped: no non-trivial depth-2 candidate at 300k" % s)
                    continue
            truth = rj(PILOT / "W9H_TRUTH.json")["W9H:%d" % s]      # START content only (known-positive control)
            H.init_worker()
            jobs.append((stage, s, fams, oracle_start(truth), ESC_STD if stage == "oracle_30k" else ESC_HI,
                         stage == "oracle_cand_300k"))
    if not jobs:
        return
    with open(outp, "a", encoding="utf-8") as fh, ProcessPoolExecutor(min(workers, len(jobs)),
                                                                     initializer=H.init_worker) as ex:
        for r in ex.map(run_donor, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("%s seed %d sel=%s schema=%s derived=%d (w/P %d) obs=%d classes=%d depth_sel=%s cpu=%ss" % (
                stage, r["seed"], r["selected"], r["selected_schema"], r["n_derived"],
                r["w5p"]["n_derived_with_promoted"], r["n_observed"], r["classes"], r["w5p"]["dag_depth_selected"],
                r["cpu_s"]))


# ------------------------------------------------------------------ oracle transfer walks
def _tx_job(a):
    sys.path.insert(0, str(HERE))
    import w9h_admit as A
    A.init_worker()
    import a18
    a18.use_world("W5")
    import fair as FR
    seed, entries, row = a
    c0 = time.process_time()
    name = row["name"]
    prov = A.a17.Prov({name: (row["body"], row["final"], row["init"])})
    A.a17.M.use_provider(prov)
    _dev, tx = A.cells_for(prov, name, row["Q2_size"])
    w = [A.walk_cell(FR.KLib(entries), c, CAP, prov, name) for c in tx]
    g5 = set(A.a17.g5_bodies())
    for x in w:
        x["EXTEND"] = bool(x["program"]) and x["program"][2] not in g5
    return {"seed": seed, "name": name, "walks": w, "cpu_s": round(time.process_time() - c0, 1)}


def stage_oracle_tx(workers=2):
    sys.path.insert(0, str(HERE))
    import w9h_admit as A
    rows = rdl(PILOT / "W9H_FOUNDRY.jsonl")
    truths = rj(PILOT / "W9H_TRUTH.json")
    adm = A.admit(rows, truths)
    by = {r["name"]: r for r in rows}
    don = {r["seed"]: r for r in rdl(OUT / "oracle_30k.jsonl")}
    outp = OUT / "oracle_tx.jsonl"
    done = {(r["seed"], r["name"]) for r in rdl(outp)}
    jobs = [(s, don[s]["selected_entries"], by[n]) for s in SEEDS if s in don
            for n, a in sorted(adm.items()) if a["seed"] == "W9H:%d" % s and a["admitted"] and a["level"] == "L2"
            and (s, n) not in done]
    log("oracle_tx jobs %d" % len(jobs))
    with open(outp, "a", encoding="utf-8") as fh, ProcessPoolExecutor(workers, initializer=A.init_worker) as ex:
        for r in ex.map(_tx_job, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


# ------------------------------------------------------------------ scoring (truth joined here, after the runs)
def stage_score():
    sys.path.insert(0, str(HERE))
    import w9h_admit as A
    from a18 import T3D, I
    A.init_worker()
    truths = rj(PILOT / "W9H_TRUTH.json")
    rows = {r["name"]: r for r in rdl(PILOT / "W9H_FOUNDRY.jsonl")}
    mech_inst = {k: {m["id"]: set(T3D.instantiate(m["schema"])) for m in t["mechanisms"]} for k, t in truths.items()}

    def nkey(s):
        return I.term_str(I.normalise(I.parse(s.replace("{H}", "HOLEVAR_W9H"))))

    def match(key, schema):
        """Equal up to W5 canonicalisation: identical normalised structure OR identical W5 instantiation set."""
        if not schema:
            return []
        out = []
        si = set(T3D.instantiate(schema)) if "P_" not in schema else None
        for m in truths[key]["mechanisms"]:
            if nkey(m["schema"]) == nkey(schema) or (si and si == mech_inst[key][m["id"]]):
                out.append(m["id"])
        return out

    def best_overlap(key, schema):
        if not schema or "P_" in schema:
            return None
        si = set(T3D.instantiate(schema))
        return max((round(len(si & v) / max(1, len(si | v)), 3), k) for k, v in mech_inst[key].items())

    score = {}
    for stage in ("gen1_30k", "cand_300k", "gen1_300k", "oracle_30k", "oracle_cand_300k", "oracle_300k"):
        st = {}
        for r in rdl(OUT / ("%s.jsonl" % stage)):
            key = "W9H:%d" % r["seed"]
            fams = {f["name"]: f for f in rj(OUT / "ROLES.json")[key]["families"]}
            lv = {n: truths[key]["families"][n]["level"] for n in fams}
            obs = sorted(r.get("observed_families", [])) if "observed_families" in r else None
            sel = r["selected_schema"]
            exp = r["w5p"]["selected_schema_expansion"]
            rec = {"selected": r["selected"], "selected_schema": sel, "selected_expansion": exp,
                   "selected_matches_true_mechanism": match(key, exp or sel),
                   "selected_best_jaccard": best_overlap(key, exp or sel),
                   "n_observed": r["n_observed"], "classes": r["classes"], "n_derived": r["n_derived"],
                   "n_derived_with_promoted": r["w5p"]["n_derived_with_promoted"],
                   "derived_with_promoted": r["w5p"]["derived_with_promoted"],
                   "dag_depth_selected": r["w5p"]["dag_depth_selected"],
                   "selected_uses_promoted": r["w5p"]["selected_uses_promoted"],
                   "meta_charges": r["meta_charges"], "cpu_s": r["cpu_s"], "escrow": r["escrow"],
                   "observe_levels": {x: sum(1 for n, f in fams.items() if f["role"] == "OBSERVE" and lv[n] == x)
                                      for x in ("L0", "L1", "L2")},
                   "selection_table": r.get("selection_table")}
            if r.get("candidates"):
                rec["candidates"] = {k: {"schema": v["schema"], "match": match(key, v["schema_expansion"] or v["schema"])
                                         if v["schema"] else [], "jaccard": best_overlap(key, v["schema"])}
                                     for k, v in r["candidates"].items()}
                rec["true_mechanism_candidates"] = sorted({m for v in rec["candidates"].values() for m in v["match"]})
            else:
                tab = r.get("selection_table") or {}
                rec["candidates_in_table"] = sorted(tab)
            if stage.startswith("oracle"):
                pmap = {p["id"]: p["schema"] for p in r["w5p"]["promoted_in"]}
                rec["promoted_in_map"] = pmap
                if r.get("candidates"):
                    nt = [v["schema"] for v in r["candidates"].values()
                          if v["schema"] and "P_" in v["schema"]
                          and not __import__("re").fullmatch(r"P_[0-9a-f]{12}\(\{H\}\)", v["schema"])]
                    rec["nontrivial_depth2_candidates"] = nt
                ins = set(r["w5p"]["promoted_in_ids"])
                rec["promoted_in"] = len(ins)
                rec["nontrivial_depth2_selected"] = bool(r["w5p"]["dag_depth_selected"] >= 2 and sel and
                                                         not __import__("re").fullmatch(r"P_[0-9a-f]{12}\(\{H\}\)", sel))
            st[key] = rec
        score[stage] = st
    tx = rdl(OUT / "oracle_tx.jsonl")
    if tx:
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
                               "EXTEND_selected_not_pristine": sum(ext[n] and pr[n] == 0 for n in sel),
                               "cells_selected": sum(sel.values()), "cells_pristine": sum(pr.values()),
                               "fp_B1": sum(1 for x in rr for w in x["walks"] if not w["censored"] and not w.get("equal_B1")),
                               "cpu_s": round(sum(x["cpu_s"] for x in rr), 1)}
        score["oracle_tx"] = o
    cpu = {st: round(sum(r["cpu_s"] for r in rdl(OUT / ("%s.jsonl" % st))), 1)
           for st in ("gen1_30k", "cand_300k", "gen1_300k", "oracle_30k", "oracle_cand_300k", "oracle_300k")}
    cpu["oracle_tx"] = round(sum(x["cpu_s"] for x in tx), 1)
    score["cpu_s"] = cpu
    wj(OUT / "SCORE.json", score)
    print(json.dumps(score, indent=1, sort_keys=True, default=str)[:12000])


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    if st == "roles":
        stage_roles()
    elif st in ("gen1_30k", "cand_300k", "gen1_300k", "oracle_30k", "oracle_cand_300k", "oracle_300k"):
        stage_donors(st, w)
    elif st == "oracle_tx":
        stage_oracle_tx(w)
    elif st == "score":
        stage_score()
