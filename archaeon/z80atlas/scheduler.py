"""72-hour autonomous producer/consumer campaign scheduler (no HITL, no LLM, no post-result threshold changes).

    python -m archaeon.z80atlas.scheduler --start        # freeze grammar, start the 72 h clock (refuses if a campaign exists)
    python -m archaeon.z80atlas.scheduler --resume       # continue after a crash / restart (the supervisor calls this)
    python -m archaeon.z80atlas.scheduler --status       # print STATUS.json (<= 2 KB)
    python -m archaeon.z80atlas.scheduler --self-test    # one tiny run through the worker path

Stages by wall clock: EARLY (positive controls first, sparse coverage), MIDDLE (promotion-driven allocation with an
exploration floor), LATE (verification: fresh seeds, matched controls, physics/world/environment swaps, transplants).
Promotion = allocate more experiments. Scientific claims are post-campaign.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from proteus.foundry.prng import SplitMix64, seed_from                        # noqa: E402
from archaeon.z80atlas import grammar as GR, engine as E                       # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE / "campaign"
RUNS = ROOT / "runs"
STATE = ROOT / "CAMPAIGN_STATE.json"
RUNS_LOG = ROOT / "RUNS.jsonl"
ATLAS = ROOT / "ATLAS_INDEX.jsonl"
STATUS = ROOT / "STATUS.json"
DONE = ROOT / "CAMPAIGN_DONE.json"
LOG = ROOT / "scheduler.log"
F = GR.FROZEN


def now() -> float:
    return time.time()


def stamp(t=None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def log(msg: dict) -> None:
    msg["at"] = stamp()
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(msg, default=str) + "\n")


# ---------------------------------------------------------------- worker
def run_job(spec: dict, seed: int, run_dir: str) -> dict:
    """Executed in a worker process. Writes the observatory files; returns compact signals."""
    d = Path(run_dir); d.mkdir(parents=True, exist_ok=True)
    (d / "SPEC.json").write_text(json.dumps(spec, indent=0, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    t0 = time.time()
    try:
        out = E.run(spec, seed)
    except Exception as ex:                                                # noqa: BLE001
        rec = {"status": "ERROR", "error": repr(ex), "trace": traceback.format_exc()[-2000:], "wall_s": round(time.time() - t0, 1)}
        (d / "RECEIPT.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8", newline="\n")
        return {"status": "ERROR", "error": repr(ex)}
    sig = out["signals"]
    # genealogy of the first crossing (reconstructed from birth events)
    forensics = {}
    if sig["first_crossing"]:
        pmap = {e["c"]: e["p"] for e in out["events"] if e.get("k") == "birth"}
        tapes = {}
        for sn in out["snapshots"]:
            for o in sn["organisms"]: tapes.setdefault(o["id"], o["tape"])
        for task, fc in sig["first_crossing"].items():
            chain = []; x = fc["id"]
            while x and len(chain) < 200:
                chain.append({"id": x, "tape": tapes.get(x)}); x = pmap.get(x, 0)
            forensics[task] = {"first_crossing": fc, "ancestry": chain, "ancestry_depth": len(chain)}
    with gzip.open(d / "TELEMETRY.json.gz", "wt", encoding="utf-8") as f:
        json.dump({"telemetry": out["telemetry"], "events": out["events"], "env_changes": out["env_changes"]}, f)
    with gzip.open(d / "SNAPSHOTS.json.gz", "wt", encoding="utf-8") as f:
        json.dump({"snapshots": out["snapshots"], "final_population": out["final_population"]}, f)
    if out["dependents"]:
        (d / "DEPENDENTS.json").write_text(json.dumps(out["dependents"], indent=0) + "\n", encoding="utf-8", newline="\n")
    if out["exploits"]:
        (d / "EXPLOITS.json").write_text(json.dumps(out["exploits"], indent=1) + "\n", encoding="utf-8", newline="\n")
    if forensics:
        (d / "FORENSICS.json").write_text(json.dumps(forensics, indent=0) + "\n", encoding="utf-8", newline="\n")
    # DF-017: founder origin classes (one row per initial organism) + the run's provenance summary
    (d / "PROVENANCE.json").write_text(json.dumps({"schema": E.PROVENANCE_SCHEMA, "founders": out["founders"], "summary": sig["provenance"]}, indent=0) + "\n",
                                       encoding="utf-8", newline="\n")
    rec = {"status": "DONE", "spec_id": spec["spec_id"], "family": spec["family"], "seed": seed, "stage": spec["stage"], "scheduler_reason": spec["scheduler_reason"],
           "factor_vector": GR.factor_vector(spec), "signals": sig, "wall_s": round(time.time() - t0, 1), "finished_at": stamp(), "grammar": spec["grammar"],
           "final_population_n": len(out["final_population"]), "snapshots": len(out["snapshots"]), "events": len(out["events"])}
    (d / "RECEIPT.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8", newline="\n")
    return rec


# ---------------------------------------------------------------- signals -> flags -> family score (mechanical)
def flags_for(sig: dict, ctrl_sig: dict | None) -> dict:
    th = F["signal_thresholds"]; fl = {}
    if sig.get("spontaneous_replication"): fl["spontaneous_replication"] = 1
    if sig.get("moat_crossed"): fl["moat_crossed"] = 1
    if sig.get("compression"): fl["compression"] = 1
    if sig.get("new_arch_events", 0) >= th["new_arch_events"]: fl["new_arch_events"] = 1
    if sig.get("coexist_epochs", 0) >= th["coexist_epochs"]: fl["coexistence"] = 1
    if sig.get("max_lineage_age", 0) >= th["longevity"]: fl["longevity"] = 1
    if sig.get("env_births", 0) >= th["env_births"]: fl["env_lineage"] = 1
    if sig.get("migrations", 0) >= th["migrations"]: fl["transport"] = 1
    r = sig.get("ruler")
    if r and r.get("beneficial", 0) >= th["ruler_gain"]: fl["ruler_gain"] = 1
    if sig.get("exploits", 0): fl["exploit"] = 1
    if ctrl_sig:
        if sig.get("moat_crossed") and not ctrl_sig.get("moat_crossed"): fl["moat_advantage"] = 1
        if sig.get("final_pop_frac", 0) - ctrl_sig.get("final_pop_frac", 0) >= th["persistence_delta"]: fl["persistence_over_control"] = 1
    return fl


def score_flags(fl: dict) -> int:
    return sum(F["promotion_weights"].get(k, 0) for k in fl)


# ---------------------------------------------------------------- campaign
class Campaign:
    def __init__(self):
        self.state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else None
        self.runs = {}
        if RUNS_LOG.exists():
            for line in RUNS_LOG.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line); self.runs[r["run_id"]] = r
        self.rng = SplitMix64(seed_from("z80atlas.campaign", self.state["start_at"] if self.state else 0, len(self.runs)))
        self.queue = []                       # list of (spec, seed, kind)  kind in exploration|control|promotion|verification|positive_control
        self.recent_kinds = []
        self.futures = {}

    # ---- persistence
    def save(self):
        STATE.write_text(json.dumps(self.state, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")

    def record(self, r: dict):
        self.runs[r["run_id"]] = r
        with RUNS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(r, default=str) + "\n")

    def elapsed_h(self) -> float:
        return (now() - self.state["start_at"]) / 3600.0

    def stage(self) -> str:
        h = self.elapsed_h()
        return "early" if h < F["early_until_h"] else ("middle" if h < F["late_from_h"] else "late")

    # ---- coverage
    def coverage(self) -> dict:
        cov = {}
        for r in self.runs.values():
            for k, v in r["factor_vector"].items():
                cov["%s=%s" % (k, v)] = cov.get("%s=%s" % (k, v), 0) + 1
        return cov

    def pair_cost(self, spec: dict, pairs: dict) -> int:
        fv = GR.factor_vector(spec); ks = sorted(fv); c = 0
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                c += pairs.get("%s=%s|%s=%s" % (ks[i], fv[ks[i]], ks[j], fv[ks[j]]), 0)
        return c

    def pairs(self) -> dict:
        pairs = {}
        for r in self.runs.values():
            fv = r["factor_vector"]; ks = sorted(fv)
            for i in range(len(ks)):
                for j in range(i + 1, len(ks)):
                    key = "%s=%s|%s=%s" % (ks[i], fv[ks[i]], ks[j], fv[ks[j]]); pairs[key] = pairs.get(key, 0) + 1
        return pairs

    # ---- producers
    def push(self, spec: dict, kind: str, seed: int | None = None):
        if spec is None: return
        seed = seed if seed is not None else 1
        self.queue.append((spec, seed, kind))

    def explore(self, n: int, stage: str):
        cov = self.coverage(); pairs = self.pairs()
        for _ in range(n):
            cands = [GR.random_spec(self.rng, stage, cov, "exploration") for _ in range(4)]
            cands = [c for c in cands if c]
            if not cands: continue
            best = min(cands, key=lambda c: self.pair_cost(c, pairs))
            self.push(best, "exploration")
            for c in GR.matched_controls(best, stage): self.push(c, "control")
            for k, v in GR.factor_vector(best).items(): cov["%s=%s" % (k, v)] = cov.get("%s=%s" % (k, v), 0) + 1

    def family_table(self) -> dict:
        fams = {}
        for r in self.runs.values():
            if r["status"] != "DONE": continue
            f = fams.setdefault(r["family"], {"runs": [], "best": 0, "flags": {}, "specs": {}})
            f["runs"].append(r["run_id"]); f["specs"][r["spec_id"]] = r
        for fam, f in fams.items():
            for rid in f["runs"]:
                r = self.runs[rid]
                # the run's reproduction control = a DONE run in the family whose reason is matched_control:reproduction with the same task
                ctrl = None
                for r2 in f["specs"].values():
                    if r2["scheduler_reason"].startswith("matched_control:reproduction") and r2["spec_id"] != r["spec_id"] and r2["factor_vector"]["task"] == r["factor_vector"]["task"]:
                        ctrl = r2["signals"]
                fl = flags_for(r["signals"], ctrl); sc = score_flags(fl)
                r["flags"] = fl; r["flag_score"] = sc
                if sc > f["best"]: f["best"] = sc; f["flags"] = fl; f["best_run"] = rid
        return fams

    def promote(self, stage: str):
        fams = self.family_table(); st = self.state
        promoted = [(fam, f) for fam, f in fams.items() if f["best"] >= F["promote_min"] and not st["retired"].get(fam) and st["promotions"].get(fam, 0) < 4]
        promoted.sort(key=lambda x: -x[1]["best"])
        for fam, f in fams.items():
            if len(f["runs"]) >= F["retire_after_runs"] and f["best"] == 0 and not st["retired"].get(fam):
                st["retired"][fam] = {"at": stamp(), "reason": "no mechanical signal after %d runs" % len(f["runs"])}
        for fam, f in promoted[:6]:
            best = self.runs[f["best_run"]]; spec = json.loads((RUNS / best["run_dir"] / "SPEC.json").read_text(encoding="utf-8"))
            uncal = any(st["uncalibrated"].get(k) for k in (spec["representation"]["substrate"],))
            if uncal: continue
            st["promotions"][fam] = st["promotions"].get(fam, 0) + 1
            reason = "promotion:%s:%s" % (fam, "+".join(sorted(f["flags"])))
            fresh = json.loads(json.dumps(spec)); fresh["stage"] = stage; fresh["budget"] = dict(F["budgets"][stage]); fresh["scheduler_reason"] = reason + ":fresh_seed"
            self.push(fresh, "promotion", seed=best["seed"] + 1)
            m = GR.mutate_spec(spec, self.rng, stage, reason); self.push(m, "promotion")
            if m:
                for c in GR.matched_controls(m, stage): self.push(c, "control")
            others = [p for p in promoted if p[0] != fam]
            if others:
                o = self.runs[others[self.rng.randbelow(len(others))][1]["best_run"]]; ospec = json.loads((RUNS / o["run_dir"] / "SPEC.json").read_text(encoding="utf-8"))
                c = GR.combine_specs(spec, ospec, self.rng, stage, reason + ":combine"); self.push(c, "promotion")
                if c:
                    for cc in GR.matched_controls(c, stage): self.push(cc, "control")
            log({"promote": fam, "flags": f["flags"], "score": f["best"]})

    def verify(self):
        """LATE stage: for the top families, fresh seeds, matched controls, and interventions from the best run's final population."""
        st = self.state
        if st.get("verification_planned"): return
        fams = self.family_table(); top = sorted(fams.items(), key=lambda x: -x[1]["best"])[:F["verify_top"]]
        for fam, f in top:
            if f["best"] <= 0: continue
            best = self.runs[f["best_run"]]; d = RUNS / best["run_dir"]; spec = json.loads((d / "SPEC.json").read_text(encoding="utf-8"))
            with gzip.open(d / "SNAPSHOTS.json.gz", "rt", encoding="utf-8") as fh: fp = json.load(fh)["final_population"]
            tapes = [o["tape"] for o in fp][:F["N"]]
            base = json.loads(json.dumps(spec)); base["stage"] = "late"; base["budget"] = dict(F["budgets"]["late"]); base["parents"] = [spec["spec_id"]]
            for s in range(F["verify_seeds"]):
                fr = json.loads(json.dumps(base)); fr["scheduler_reason"] = "verify:%s:fresh_seed" % fam; self.push(fr, "verification", seed=100 + s)
            for c in GR.matched_controls(base, "late"):
                c["scheduler_reason"] = "verify:%s:%s" % (fam, c["scheduler_reason"]); self.push(c, "verification", seed=100)
            if tapes:
                def tp(reason, **chg):
                    t = json.loads(json.dumps(base)); t["transplant"] = {"from_run": best["run_id"], "tapes": tapes}
                    # DF-017: the campaign set init="random" here and the old predicate read that label. The engine now stamps these
                    # founders transplanted_lineage from the tapes themselves; the label is corrected so the spec no longer lies.
                    t["init"] = "transplanted_lineage"
                    for k, v in chg.items():
                        if k == "reproduction": t["reproduction"] = v; t["pressure"] = [p for p in t["pressure"] if p not in ("explicit_fitness", "recombination")] or ["implicit_survival"]
                        elif k == "topology": t["world"]["topology"] = v; t["world"]["migration"] = "none"; t["world"]["reservoir"] = False
                        elif k == "task": t["task"]["name"] = v
                    t["scheduler_reason"] = "verify:%s:%s" % (fam, reason); t["spec_id"] = GR.spec_id(t) + "-t"; t["family"] = fam
                    for name, ok in GR.CONSTRAINTS:
                        if not ok(t): return None
                    return t
                self.push(tp("transplant:same"), "verification", seed=100)
                self.push(tp("transplant:physics_swap", reproduction="EXTERNAL" if spec["reproduction"] != "EXTERNAL" else "ENDOGENOUS_COPY"), "verification", seed=100)
                self.push(tp("transplant:world_swap", topology="well_mixed" if spec["world"]["topology"] != "well_mixed" else "grid_vn"), "verification", seed=100)
                alt = {"CONST_atomic": "ECHO_forced", "ECHO_forced": "INC1", "INC1": "COND_multi"}.get(spec["task"]["name"], "COND_multi")
                self.push(tp("transplant:environment_swap", task=alt), "verification", seed=100)
        st["verification_planned"] = True; log({"verification_planned": len(self.queue)})

    # ---- consumer loop
    def launch(self, ex, spec, seed, kind):
        rid = "%s_s%d_%s" % (spec["spec_id"], seed, kind[:4]); rd = "%s/%s" % (spec["family"], rid)
        fut = ex.submit(run_job, spec, seed, str(RUNS / rd))
        self.futures[fut] = {"run_id": rid, "run_dir": rd, "spec_id": spec["spec_id"], "family": spec["family"], "seed": seed, "kind": kind, "stage": spec["stage"], "scheduler_reason": spec["scheduler_reason"], "factor_vector": GR.factor_vector(spec), "started_at": stamp()}
        self.recent_kinds = (self.recent_kinds + [kind])[-30:]
        self.state["launched"] = self.state.get("launched", 0) + 1

    def harvest(self, done):
        for fut in done:
            meta = self.futures.pop(fut)
            try:
                rec = fut.result()
            except Exception as ex:                                        # noqa: BLE001
                rec = {"status": "ERROR", "error": repr(ex)}
            r = dict(meta); r["status"] = rec.get("status"); r["signals"] = rec.get("signals", {}); r["wall_s"] = rec.get("wall_s"); r["error"] = rec.get("error"); r["finished_at"] = stamp()
            self.record(r)
            with ATLAS.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"run_id": r["run_id"], "family": r["family"], "spec_id": r["spec_id"], "seed": r["seed"], "stage": r["stage"], "kind": r["kind"], "reason": r["scheduler_reason"],
                                    "factors": r["factor_vector"], "signals": {k: v for k, v in r["signals"].items() if k not in ("first_crossing", "ruler")}, "run_dir": "runs/" + r["run_dir"], "status": r["status"]}) + "\n")
            if r["status"] == "ERROR": self.state["errors"] = self.state.get("errors", 0) + 1; log({"error": r["error"], "run": r["run_id"]})
            if r["kind"] == "positive_control" and r["status"] == "DONE":
                spec = json.loads((RUNS / r["run_dir"] / "SPEC.json").read_text(encoding="utf-8")); v = GR.control_verdict(spec, r["signals"])
                self.state["controls"][r["run_id"]] = {"verdict": v, "reason": spec["scheduler_reason"], "substrate": spec["representation"]["substrate"]}
                if v == "FAIL" and spec["scheduler_reason"].endswith("replicator_replicates"):
                    self.state["uncalibrated"][spec["representation"]["substrate"]] = r["run_id"]
                log({"positive_control": spec["scheduler_reason"], "substrate": spec["representation"]["substrate"], "verdict": v})
            # immediate preservation flag for the special high-value results
            fl = flags_for(r["signals"], None) if r["status"] == "DONE" else {}
            if fl.get("spontaneous_replication") or r["signals"].get("exploits"):
                self.state["high_value"].append({"run": r["run_id"], "flags": fl, "exploits": r["signals"].get("exploits", 0), "at": stamp()})

    def status(self) -> dict:
        fams = self.family_table() if self.runs else {}
        top = sorted(((fam, f["best"], sorted(f["flags"])) for fam, f in fams.items()), key=lambda x: -x[1])[:5]
        st = {"campaign": "z80atlas", "grammar": self.state["grammar"], "started": stamp(self.state["start_at"]), "elapsed_h": round(self.elapsed_h(), 2), "stage": self.stage(),
              "runs_done": sum(1 for r in self.runs.values() if r["status"] == "DONE"), "errors": self.state.get("errors", 0), "running": len(self.futures), "queued": len(self.queue),
              "families": len(fams), "retired": len(self.state["retired"]), "promotions": sum(self.state["promotions"].values()),
              "controls": {k: v["verdict"] for k, v in self.state["controls"].items()}, "uncalibrated": self.state["uncalibrated"],
              "high_value": len(self.state["high_value"]), "spontaneous": sum(1 for r in self.runs.values() if r.get("signals", {}).get("spontaneous_replication")),
              "moat_advantage": sum(1 for f in fams.values() if "moat_advantage" in f["flags"]), "top": top, "at": stamp()}
        return st

    def write_status(self):
        s = json.dumps(self.status(), indent=0, default=str)
        STATUS.write_text(s[:2000] + "\n", encoding="utf-8", newline="\n")

    def loop(self):
        st = self.state; workers = F["workers"]; last_status = 0; last_promote = 0
        with ProcessPoolExecutor(max_workers=workers) as ex:
            # positive controls first (only once)
            if not st.get("controls_launched"):
                for s in GR.positive_controls("early"): self.push(s, "positive_control")
                st["controls_launched"] = True
            while True:
                h = self.elapsed_h(); stage = self.stage()
                if h >= F["campaign_hours"]:
                    log({"stop": "campaign_hours reached", "running": len(self.futures)})
                    for fut in list(self.futures): fut.cancel()
                    done, _ = wait(list(self.futures), timeout=600)
                    self.harvest(done); break
                if stage == "late": self.verify()
                if stage != "early" and now() - last_promote > 300:
                    self.promote(stage); last_promote = now()
                # keep the pool full, honouring the exploration floor and the launch cutoff
                while len(self.futures) < workers and h < F["stop_launch_h"]:
                    if not self.queue:
                        if stage == "late" and st.get("verification_planned"): self.explore(2, "late")
                        else: self.explore(4, stage)
                        if not self.queue: break
                    kinds = self.recent_kinds[-20:]; expl = sum(1 for k in kinds if k in ("exploration", "control", "positive_control"))
                    idx = 0
                    if kinds and expl / len(kinds) < F["exploration_floor"]:
                        idx = next((i for i, q in enumerate(self.queue) if q[2] in ("exploration", "control")), None)
                        if idx is None: self.explore(1, stage); idx = len(self.queue) - 2 if len(self.queue) >= 2 else 0
                    spec, seed, kind = self.queue.pop(idx); self.launch(ex, spec, seed, kind)
                if not self.futures and h >= F["stop_launch_h"]:
                    break
                done, _ = wait(list(self.futures), timeout=30, return_when=FIRST_COMPLETED)
                self.harvest(done)
                if now() - last_status > 60:
                    self.write_status(); self.save(); last_status = now()
        self.finalize()

    def finalize(self):
        st = self.state; st["frozen_at"] = stamp(); self.save(); self.write_status()
        from archaeon.z80atlas.packet import build
        p = build(self)
        DONE.write_text(json.dumps({"done_at": stamp(), "runs": len(self.runs), "packet": str(p)}, indent=1) + "\n", encoding="utf-8", newline="\n")
        log({"finalized": True, "packet": str(p)})


def start() -> int:
    if STATE.exists():
        print("campaign exists; use --resume"); return 2
    ROOT.mkdir(parents=True, exist_ok=True); RUNS.mkdir(exist_ok=True)
    g = {"digest": GR.digest(), "AXES": GR.AXES, "FROZEN": F, "constraints": [c[0] for c in GR.CONSTRAINTS], "blocked": GR.BLOCKED, "atlas_axes": GR.ATLAS_AXES, "frozen_at": stamp()}
    (ROOT / "GRAMMAR_FROZEN.json").write_text(json.dumps(g, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    st = {"start_at": now(), "started": stamp(), "grammar": GR.digest(), "controls": {}, "uncalibrated": {}, "retired": {}, "promotions": {}, "high_value": [], "errors": 0}
    STATE.write_text(json.dumps(st, indent=1) + "\n", encoding="utf-8", newline="\n")
    log({"start": True, "grammar": GR.digest(), "workers": F["workers"]})
    return resume()


def resume() -> int:
    if DONE.exists():
        print("campaign done"); return 0
    c = Campaign()
    if c.state is None:
        print("no campaign; use --start"); return 2
    if c.state["grammar"] != GR.digest():
        log({"halt": "GRAMMAR_CHANGED", "frozen": c.state["grammar"], "now": GR.digest()}); print("GRAMMAR CHANGED: refusing to run"); return 3
    log({"resume": True, "runs": len(c.runs), "elapsed_h": round(c.elapsed_h(), 2)})
    if c.elapsed_h() >= F["campaign_hours"]:
        c.finalize(); return 0
    c.loop(); return 0


def self_test() -> int:
    import tempfile
    s = GR.positive_controls("early")[0]; s["budget"] = {"vm_steps": 500000, "step_cap": 256, "max_epochs": 30}
    with tempfile.TemporaryDirectory() as td:
        r = run_job(s, 1, td)
        print(json.dumps({"status": r["status"], "births_endo": r["signals"]["births_endo"], "flags": flags_for(r["signals"], None), "files": sorted(os.listdir(td))}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--start", action="store_true"); ap.add_argument("--resume", action="store_true"); ap.add_argument("--status", action="store_true"); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test: return self_test()
    if a.start: return start()
    if a.resume: return resume()
    if a.status:
        print(STATUS.read_text(encoding="utf-8") if STATUS.exists() else "{}"); return 0
    ap.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
