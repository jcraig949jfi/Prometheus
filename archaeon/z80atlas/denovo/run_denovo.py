"""Pre-registered de-novo replication screen (directive 2026-09-23, Phase 4). Fixed allocation; no adaptivity.

    python -m archaeon.z80atlas.denovo.run_denovo --freeze        # writes PREREG.json once (refuses to overwrite)
    python -m archaeon.z80atlas.denovo.run_denovo --run           # verifies PREREG hashes, runs controls, then treatments
    python -m archaeon.z80atlas.denovo.run_denovo --report        # recomputes RESULTS.json from the run directories

Question: under candidate structural conditions, can a genuinely random population produce a self-sustaining endogenous
replicator with no seeded or transplanted genetic material? The preregistration (arms, seeds, budget, endpoint, control
criteria, outcome language, code hashes) is frozen by --freeze and committed BEFORE --run; --run refuses to start if any
hashed file changed. No transplants, no seeded replicators and no evolved tapes enter a treatment world; every treatment world's
founder census is checked after it runs and a single inserted founder stops the screen (INSTRUMENT_FAILURE).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.z80atlas import grammar as GR, tasks as T

HERE = Path(__file__).resolve().parent
ZROOT = HERE.parent
PREREG = HERE / "PREREG.json"
RUNS = HERE / "runs"
RESULTS = HERE / "RESULTS.json"
F = GR.FROZEN
HASHED = ["engine.py", "vm.py", "tasks.py", "grammar.py", "scheduler.py", "denovo/run_denovo.py"]

# ---- arms: world factors vary; everything else is held at the ONE configuration in which the campaign recorded a random-origin
# population that did not go extinct (84616cf8257b_s1_cont). Top-family modal levels are NOT used for the held factors: 27/30 of
# those families were seeded worlds, which carry no information about random-origin replication.
HELD = {"substrate": "vmcopy", "genome": 32, "layout": "shared", "reproduction": "ENDOGENOUS_COPY", "pressure": ["tape_cost"], "task": "ECHO_forced",
        "mutation": "local_byte", "resources": "limited", "env_dynamics": "env_mutate"}
ARMS = {                                                                   # 2x2 (migration x reservoir) inside niches + well-mixed comparison
    "A_niches_migration_reservoir": {"topology": "niches", "migration": "env_dependent", "reservoir": True},
    "B_niches_bare": {"topology": "niches", "migration": "none", "reservoir": False},
    "C_niches_migration_only": {"topology": "niches", "migration": "env_dependent", "reservoir": False},
    "D_niches_reservoir_only": {"topology": "niches", "migration": "none", "reservoir": True},
    "E_well_mixed": {"topology": "well_mixed", "migration": "none", "reservoir": False},
}
TREATMENT_SEEDS = list(range(1000, 1016))                                 # 16 independent seeds per arm, equal budget
POSCTRL_SEEDS = [2000, 2001]
NEGCTRL_SEED = 3000
STAGE = "late"                                                             # FROZEN budget: 150M VM steps / 4000 epochs / step_cap 256
CONTRASTS = [["B_niches_bare", "E_well_mixed", "topology alone"], ["A_niches_migration_reservoir", "B_niches_bare", "migration+reservoir"],
             ["C_niches_migration_only", "B_niches_bare", "migration"], ["D_niches_reservoir_only", "B_niches_bare", "reservoir"]]


def world(arm: dict) -> dict:
    return {"topology": arm["topology"], "migration": arm["migration"], "resources": HELD["resources"], "env_dynamics": HELD["env_dynamics"],
            "reservoir": arm["reservoir"], "niches": F["niches"]}


def make(arm_name: str, init: str, reason: str) -> dict:
    s = GR.make(world(ARMS[arm_name]), {"substrate": HELD["substrate"], "genome": HELD["genome"], "layout": HELD["layout"]}, HELD["reproduction"],
                list(HELD["pressure"]), HELD["task"], HELD["mutation"], init, stage=STAGE, reason=reason)
    if s is None:
        raise SystemExit("DESIGN_NOT_IDENTIFIABLE: grammar refuses arm %s" % arm_name)
    s["family"] = "denovo_" + arm_name
    return s


def negctrl(arm_name: str) -> dict:
    s = make(arm_name, "random", "denovo:provenance_negative_control")    # the exact campaign defect pattern: label random, tapes inserted
    hyb = T.pad(T.task_then_replicate(HELD["task"], HELD["substrate"] == "vmcopy"), HELD["genome"]).hex()
    s["transplant"] = {"from_run": "denovo:hand_written_hybrid_witness", "tapes": [hyb] * int(F["N"] * F["init_fill_pct"] / 100)}
    s["spec_id"] = GR.spec_id(s) + "-n"
    return s


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def code_hashes() -> dict:
    return {h: sha(ZROOT / h) for h in HASHED}


# ---------------------------------------------------------------------------------------------------------------- endpoint (frozen)
def endpoint(sig: dict, N: int) -> dict:
    """PRIMARY: DE_NOVO_REPLICATION iff (i) the world holds no seeded or transplanted founder, (ii) the repaired frozen predicate holds
    (>= spont_births endogenous births with random-only ancestry, final random-only population >= spont_pop_frac * N, mean fidelity of
    those births >= spont_fid), and (iii) the world is alive at the end of its budget after at least 2 * max_age epochs, so that every
    founder is dead and the surviving population exists only through endogenous reproduction.
    SECONDARY (reported, never an event for outcome language): SUSTAINED_LOW_FIDELITY_REPRODUCTION = (i) + (iii) + births and population
    thresholds met, fidelity below spont_fid."""
    p = sig["provenance"]
    clean_world = p["founders"]["seeded_replicator"] == 0 and p["founders"]["transplanted_lineage"] == 0 and not p["world_has_inserted_material"]
    alive = sig["extinct_epoch"] is None and sig["epochs"] >= 2 * F["max_age"]
    births_pop = p["births_endo_clean"] >= F["spont_births"] and p["final_pop_clean"] / N >= F["spont_pop_frac"]
    primary = bool(clean_world and alive and sig["spontaneous_replication"])
    secondary = bool(clean_world and alive and births_pop and not primary and p["fid_clean"] < F["spont_fid"])
    return {"clean_world": clean_world, "alive_after_founders": alive, "births_and_population": births_pop, "fid_clean": p["fid_clean"],
            "DE_NOVO_REPLICATION": primary, "SUSTAINED_LOW_FIDELITY_REPRODUCTION": secondary}


def posctrl_pass(sig: dict) -> dict:
    p = sig["provenance"]
    ok = p["founders"]["seeded_replicator"] > 0 and p["births_endo_inserted"] >= F["spont_births"] and p["fid_inserted"] >= F["spont_fid"] and sig["spontaneous_replication"] is False
    return {"PASS": bool(ok), "births_endo_inserted": p["births_endo_inserted"], "fid_inserted": p["fid_inserted"], "spontaneous_replication": sig["spontaneous_replication"]}


def negctrl_pass(sig: dict, n_tapes: int) -> dict:
    p = sig["provenance"]
    ok = p["founders"] == {"random": 0, "seeded_replicator": 0, "transplanted_lineage": n_tapes} and sig["spontaneous_replication"] is False
    return {"PASS": bool(ok), "founders": p["founders"], "spontaneous_replication": sig["spontaneous_replication"],
            "legacy_label_would_have_said": sig["spontaneous_replication_legacy_label"], "inserted_lineage_replication": sig["inserted_lineage_replication"]}


def clopper_pearson(k: int, n: int, alpha: float = 0.05):
    def cdf(x, p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))

    def solve(f, lo=0.0, hi=1.0):
        for _ in range(100):
            mid = (lo + hi) / 2
            if f(mid): lo = mid
            else: hi = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else solve(lambda p: 1 - cdf(k - 1, p) < alpha / 2)
    hi = 1.0 if k == n else solve(lambda p: cdf(k, p) > alpha / 2)
    return [round(lo, 4), round(hi, 4)]


OUTCOMES = {"REPRODUCIBLE_DE_NOVO_REPLICATION": "primary events in >= 2 independent seeds of the same arm",
            "RARE_DE_NOVO_EVENT": ">= 1 primary event, no arm with >= 2",
            "NO_DETECTABLE_DE_NOVO_REPLICATION": "0 primary events in all treatment runs; report exact 95% upper bounds per arm and pooled",
            "INSTRUMENT_FAILURE": "any control fails, any treatment world holds an inserted founder, any run errors, or a hash check fails",
            "DESIGN_NOT_IDENTIFIABLE": "the grammar refuses an arm (checked at --freeze)"}


# ---------------------------------------------------------------------------------------------------------------- freeze
def freeze(argv_date: str) -> int:
    if PREREG.exists():
        print("REFUSED: PREREG.json exists; a changed design needs a new preregistration file and run identity"); return 2
    specs = {a: make(a, "random", "denovo:treatment") for a in ARMS}
    for a, s in specs.items():
        assert s["init"] == "random" and "transplant" not in s, a
    pos = {a: make(a, "seeded_replicator", "denovo:positive_control") for a in ARMS}
    neg = {a: negctrl(a) for a in ARMS}
    grammar_ctrls = GR.positive_controls(STAGE)
    pr = {"schema": "archaeon.z80atlas.denovo.prereg.v1", "prereg_id": "DENOVO-01", "frozen_at_utc": argv_date, "grammar_digest": GR.digest(),
          "code_sha256_lf_normalised": code_hashes(), "question": __doc__.split("Question:")[1].split("The preregistration")[0].strip(),
          "held_factors": HELD, "held_factors_source": "84616cf8257b_s1_cont (the campaign's only random-origin endogenous world that did not go extinct)",
          "arms": {a: {"world": world(ARMS[a]), "spec_id": specs[a]["spec_id"], "spec": specs[a]} for a in ARMS},
          "arm_E_equals_candidate_world_class": specs["E_well_mixed"]["spec_id"] == "84616cf8257b",
          "treatment_seeds": TREATMENT_SEEDS, "budget": dict(F["budgets"][STAGE]), "N": F["N"],
          "allocation": "fixed; every (arm, seed) runs exactly once with the same budget; no promotion, scoring, transplant, seeding, warm start or manual intervention",
          "endpoint_primary": endpoint.__doc__, "thresholds": {k: F[k] for k in ("spont_births", "spont_pop_frac", "spont_fid", "max_age")},
          "controls": {"grammar_positive_controls": {"specs": [c["spec_id"] for c in grammar_ctrls], "seed": 1, "pass": "grammar.control_verdict == PASS for every one"},
                       "arm_positive_controls": {"seeds": POSCTRL_SEEDS, "spec_ids": {a: pos[a]["spec_id"] for a in ARMS},
                                                 "pass": "seeded founders present; >= spont_births endogenous births of inserted ancestry at mean fidelity >= spont_fid; repaired spontaneous predicate False"},
                       "arm_provenance_negative_controls": {"seed": NEGCTRL_SEED, "spec_ids": {a: neg[a]["spec_id"] for a in ARMS},
                                                            "pass": "every founder classified transplanted_lineage (hand-written hybrid witness, spec labelled init=random); repaired spontaneous predicate False"},
                       "order": "all controls run and pass BEFORE any treatment world starts; controls run in their own worlds (separate engine runs)"},
          "outcomes": OUTCOMES, "contrasts_if_events": CONTRASTS, "interval": "exact two-sided Clopper-Pearson 95%",
          "stop_conditions": ["provenance tests fail", "hash mismatch at --run", "any control fails", "any treatment world holds an inserted founder",
                              "any run errors", "a threshold or endpoint would need to change after results begin (-> new prereg + new run identity)"],
          "expected_power_note": ("Campaign base rate: 1 of 27,141 random-init endogenous runs without inserted material stayed alive (fidelity 0.482); "
                                  "median extinction epoch 61 because founders die at max_age=60 and nothing replicates. A 16-seed arm can only bound the "
                                  "per-world event rate from above (0/16 -> 95% upper 0.206); the screen is a targeted look at the candidate world class, "
                                  "not a powered rate estimate.")}
    PREREG.write_text(json.dumps(pr, indent=1, sort_keys=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"prereg": str(PREREG), "arms": {a: pr["arms"][a]["spec_id"] for a in ARMS}, "arm_E_equals_candidate": pr["arm_E_equals_candidate_world_class"]}))
    return 0


# ---------------------------------------------------------------------------------------------------------------- run
def _job(spec: dict, seed: int, rd: str) -> dict:
    from archaeon.z80atlas import scheduler as S
    return S.run_job(spec, seed, rd)


def _batch(ex, jobs):
    out = {}
    futs = {ex.submit(_job, s, seed, str(RUNS / rid)): (rid, s, seed) for rid, s, seed in jobs}
    for fu in as_completed(futs):
        rid, s, seed = futs[fu]; rec = fu.result(); out[rid] = rec
        print(json.dumps({"run": rid, "status": rec["status"], "wall_s": rec.get("wall_s")}), flush=True)
    return out


def run(workers: int) -> int:
    pr = json.loads(PREREG.read_text(encoding="utf-8"))
    now = code_hashes()
    if now != pr["code_sha256_lf_normalised"]:
        print("STOP: code changed after preregistration: %s" % sorted(k for k in now if now[k] != pr["code_sha256_lf_normalised"].get(k))); return 3
    if GR.digest() != pr["grammar_digest"]:
        print("STOP: grammar digest changed"); return 3
    specs = {a: pr["arms"][a]["spec"] for a in ARMS}
    for a, s in specs.items():
        if s["init"] != "random" or "transplant" in s or s["spec_id"] != GR.spec_id(s):
            print("STOP: treatment spec %s is not random-only or its id does not recompute" % a); return 3
    RUNS.mkdir(exist_ok=True)
    gctrl = GR.positive_controls(STAGE)
    ctrl_jobs = [("gctrl_%s_s1" % c["spec_id"], c, 1) for c in gctrl]
    ctrl_jobs += [("pos_%s_s%d" % (a, sd), make(a, "seeded_replicator", "denovo:positive_control"), sd) for a in ARMS for sd in POSCTRL_SEEDS]
    ctrl_jobs += [("neg_%s_s%d" % (a, NEGCTRL_SEED), negctrl(a), NEGCTRL_SEED) for a in ARMS]
    with ProcessPoolExecutor(workers) as ex:
        crec = _batch(ex, ctrl_jobs)
        verdicts = {}
        for rid, s, seed in ctrl_jobs:
            rec = crec[rid]
            if rec["status"] != "DONE":
                verdicts[rid] = {"PASS": False, "error": rec.get("error")}; continue
            if rid.startswith("gctrl_"): verdicts[rid] = {"PASS": GR.control_verdict(s, rec["signals"]) == "PASS", "reason": s["scheduler_reason"]}
            elif rid.startswith("pos_"): verdicts[rid] = posctrl_pass(rec["signals"])
            else: verdicts[rid] = negctrl_pass(rec["signals"], len(s["transplant"]["tapes"]))
        (HERE / "CONTROLS.json").write_text(json.dumps(verdicts, indent=1) + "\n", encoding="utf-8", newline="\n")
        if not all(v["PASS"] for v in verdicts.values()):
            print("STOP: INSTRUMENT_FAILURE -- control(s) failed: %s" % [k for k, v in verdicts.items() if not v["PASS"]]); return 4
        jobs = [("%s_s%d" % (a, sd), specs[a], sd) for a in ARMS for sd in TREATMENT_SEEDS]
        _batch(ex, jobs)
    return report()


def _lineage_history(rd: Path, lineage: int) -> list:
    with gzip.open(rd / "SNAPSHOTS.json.gz", "rt", encoding="utf-8") as f:
        sn = json.load(f)
    out = []
    for s in sn["snapshots"]:
        orgs = [o for o in s["organisms"] if o["lineage"] == lineage]
        if orgs:
            niches = {}
            for o in orgs: niches[o["niche"]] = niches.get(o["niche"], 0) + 1
            out.append({"epoch": s["epoch"], "reason": s["reason"], "n": len(orgs), "niches": niches, "best_score": max(o["score"] for o in orgs)})
    return out


def _trajectory(rd: Path, every: int = 25) -> list:
    with gzip.open(rd / "TELEMETRY.json.gz", "rt", encoding="utf-8") as f:
        tel = json.load(f)["telemetry"]
    return [[r["e"], r["pop"], r.get("pop_clean"), r["endo"], r["fid"], r["smax"]] for r in tel if r["e"] % every == 0 or r is tel[-1]]


def report() -> int:
    pr = json.loads(PREREG.read_text(encoding="utf-8"))
    controls = json.loads((HERE / "CONTROLS.json").read_text(encoding="utf-8")) if (HERE / "CONTROLS.json").exists() else {}
    rows, failures = [], []
    for a in ARMS:
        for sd in TREATMENT_SEEDS:
            rd = RUNS / ("%s_s%d" % (a, sd)); recp = rd / "RECEIPT.json"
            if not recp.exists():
                failures.append("missing " + rd.name); continue
            rec = json.loads(recp.read_text(encoding="utf-8"))
            if rec["status"] != "DONE":
                failures.append("error " + rd.name); continue
            sig = rec["signals"]; ep = endpoint(sig, pr["N"])
            if not ep["clean_world"]:
                failures.append("inserted founder in treatment " + rd.name)
            p = sig["provenance"]; row = {"arm": a, "seed": sd, "run_dir": "archaeon/z80atlas/denovo/runs/" + rd.name, **ep,
                                          "final_pop_frac": sig["final_pop_frac"], "extinct_epoch": sig["extinct_epoch"], "epochs": sig["epochs"],
                                          "births_endo_clean": p["births_endo_clean"], "births_endo_clean_hifi": p["births_endo_clean_hifi"], "founders": p["founders"],
                                          "best_ever": sig["best_ever"], "task_max_final": sig["task_max_final"], "moat_crossed": sig["moat_crossed"]}
            if ep["DE_NOVO_REPLICATION"] or ep["SUSTAINED_LOW_FIDELITY_REPRODUCTION"] or p["first_clean_hifi_replication"]:
                fr = p["first_clean_hifi_replication"] or p["first_clean_replication"]
                row["first_replicator"] = fr
                row["first_crossing_provenance"] = p["first_crossing"]
                row["trajectory_e_pop_popclean_endo_fid_smax"] = _trajectory(rd)
                if fr:
                    row["persistence_epochs_after_first_hifi"] = (sig["epochs"] - fr["epoch"]) if sig["extinct_epoch"] is None else (sig["extinct_epoch"] - fr["epoch"])
                    row["lineage_history"] = _lineage_history(rd, fr["lineage"])
            rows.append(row)
    per_arm = {}
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]; k = sum(r["DE_NOVO_REPLICATION"] for r in rs); k2 = sum(r["SUSTAINED_LOW_FIDELITY_REPRODUCTION"] for r in rs)
        per_arm[a] = {"n": len(rs), "primary_events": k, "primary_rate_ci95": clopper_pearson(k, len(rs)) if rs else None, "secondary_events": k2,
                      "secondary_rate_ci95": clopper_pearson(k2, len(rs)) if rs else None, "extinct": sum(r["extinct_epoch"] is not None for r in rs),
                      "any_clean_hifi_birth": sum(r["births_endo_clean_hifi"] > 0 for r in rs), "median_extinct_epoch": sorted(r["extinct_epoch"] for r in rs if r["extinct_epoch"] is not None)[len([r for r in rs if r["extinct_epoch"] is not None]) // 2] if any(r["extinct_epoch"] is not None for r in rs) else None}
    n = len(rows); k = sum(r["DE_NOVO_REPLICATION"] for r in rows)
    ctrl_ok = bool(controls) and all(v["PASS"] for v in controls.values())
    if failures or not ctrl_ok or n != len(ARMS) * len(TREATMENT_SEEDS):
        outcome = "INSTRUMENT_FAILURE"
    elif any(v["primary_events"] >= 2 for v in per_arm.values()):
        outcome = "REPRODUCIBLE_DE_NOVO_REPLICATION"
    elif k >= 1:
        outcome = "RARE_DE_NOVO_EVENT"
    else:
        outcome = "NO_DETECTABLE_DE_NOVO_REPLICATION"
    res = {"schema": "archaeon.z80atlas.denovo.results.v1", "prereg_id": pr["prereg_id"], "prereg_sha256": sha(PREREG), "outcome": outcome,
           "numerator_primary": k, "denominator": n, "pooled_primary_ci95": clopper_pearson(k, n) if n else None,
           "numerator_secondary": sum(r["SUSTAINED_LOW_FIDELITY_REPRODUCTION"] for r in rows), "controls_all_pass": ctrl_ok, "controls": controls,
           "failures": failures, "per_arm": per_arm, "runs": rows}
    RESULTS.write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"outcome": outcome, "primary": "%d/%d" % (k, n), "per_arm": {a: (v["primary_events"], v["n"], v["secondary_events"], v["extinct"]) for a, v in per_arm.items()}}))
    return 0 if outcome != "INSTRUMENT_FAILURE" else 4


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--freeze", metavar="UTC_STAMP"); ap.add_argument("--run", action="store_true"); ap.add_argument("--report", action="store_true")
    ap.add_argument("--workers", type=int, default=20)
    a = ap.parse_args(argv)
    if a.freeze: return freeze(a.freeze)
    if a.run: return run(a.workers)
    if a.report: return report()
    ap.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
