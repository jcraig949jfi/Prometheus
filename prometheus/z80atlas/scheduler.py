"""The 72-hour autonomous producer/consumer campaign.

  PRODUCER  assembles experiment specs ONLY from the frozen grammar: sparse pairwise coverage (exploration), matched
            controls, one-factor mutations of promoted families, collision crosses, fresh-seed replicates, and -- in the
            late stage -- verification reruns, the full matched-control set, lineage transplants and environment swaps.
  CONSUMER  a process pool running runner.run_spec.
  STAGES    by wall-clock fraction of the fixed window: EARLY (< 30%): positive controls, then broad coverage with
            matched endogenous/exogenous pairs; MIDDLE (30-80%): allocation to families with mechanical triggers, an
            exploration FLOOR (>= 30% of each batch), retirement of silent families; LATE (>= 80%): no new families;
            rerun the strongest with fresh seeds and their critical controls, intervene (transplant, env swap), and
            attribute each surviving signal mechanically to world / organism / representation / reproductive
            mechanism / ecology / measurement artefact.
  Every allocation, promotion, retirement and verification is logged with its mechanical reason. State is
  checkpointed after every batch and resumable; the grammar and threshold hashes are re-checked on resume.
  At the wall-clock boundary: stop cleanly, freeze state, emit the packet."""
from __future__ import annotations

import datetime
import json
import multiprocessing as mp
import os
import pathlib
import random
import time
from typing import Dict, List, Optional

from prometheus.z80atlas import grammar as G
from prometheus.z80atlas import observatory as O
from prometheus.z80atlas import controls as C
from prometheus.z80atlas.runner import run_spec
from prometheus.z80atlas.world import ENDOGENOUS

STAGE_EARLY_END = 0.30
STAGE_MIDDLE_END = 0.80
EXPLORATION_FLOOR = 0.30
RETIRE_AFTER_RUNS = 3
TOP_K_LATE = 16


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Campaign:
    def __init__(self, workdir: str, hours: float, workers: int, ticks: int = 200, cells: int = 144, seed: int = 0, resume: bool = False):
        self.wd = pathlib.Path(workdir); self.wd.mkdir(parents=True, exist_ok=True)
        self.runs_dir = self.wd / "runs"; self.runs_dir.mkdir(exist_ok=True)
        self.state_path = self.wd / "state.json"
        self.workers = max(1, workers)
        if resume and self.state_path.exists():
            self.s = json.loads(self.state_path.read_text(encoding="utf-8"))
            assert self.s["grammar_hash"] == G.grammar_hash(), "grammar changed since the campaign was frozen: refusing to resume"
            assert self.s["thresholds_hash"] == O.thresholds_hash(), "trigger thresholds changed since the campaign was frozen: refusing to resume"
            self._decide("resume", None, "resumed at %s with %d runs done" % (_utc(), self.s.get("n_runs", 0)))
        else:
            self.s = {"grammar_hash": G.grammar_hash(), "thresholds_hash": O.thresholds_hash(), "start_utc": _utc(), "start_ts": time.time(),
                      "hours": hours, "ticks": ticks, "cells": cells, "seed": seed, "runs": [], "families": {}, "covered_pairs": [],
                      "positive_controls": None, "specimen_archive": [], "decisions": [], "flags": [], "attribution": {},
                      "counters": {"exploration": 0, "promoted": 0, "control": 0, "verification": 0, "intervention": 0, "positive_control": 0},
                      "next_run_no": 1, "stage_log": [], "run_wall_ema": None, "stopped": None,
                      "unavailable": G.UNAVAILABLE}
            self._decide("start", None, "campaign frozen: grammar %s thresholds %s hours %s" % (self.s["grammar_hash"][:12], self.s["thresholds_hash"][:12], hours))
        self.rng = random.Random(self.s["seed"] * 1000003 + self.s["next_run_no"])
        self.covered = {tuple(p) for p in self.s["covered_pairs"]}
        # run records live in memory + append-only runs.jsonl (state.json stays small at any campaign size)
        self.runs: List[Dict] = []
        self.by_family: Dict[str, List[Dict]] = {}
        self.runs_path = self.wd / "runs.jsonl"
        if resume and self.runs_path.exists():
            for line in self.runs_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._index(json.loads(line))
        self.s.pop("runs", None)
        self._batches = 0

    # ---- clock ---------------------------------------------------------------------------------------------------------
    def elapsed_frac(self) -> float:
        return (time.time() - self.s["start_ts"]) / (self.s["hours"] * 3600.0)

    def remaining_s(self) -> float:
        return self.s["hours"] * 3600.0 - (time.time() - self.s["start_ts"])

    def stage(self) -> str:
        f = self.elapsed_frac()
        return "early" if f < STAGE_EARLY_END else ("middle" if f < STAGE_MIDDLE_END else "late")

    # ---- bookkeeping ---------------------------------------------------------------------------------------------------
    def _decide(self, kind: str, family: Optional[str], reason: str, **extra) -> None:
        self.s.setdefault("decisions", []).append(dict({"utc": _utc(), "kind": kind, "family": family, "reason": reason}, **extra))

    def _new_id(self) -> str:
        n = self.s["next_run_no"]; self.s["next_run_no"] = n + 1
        return "r%06d" % n

    def _family(self, vec: Dict[str, str], kind: str, parents: Optional[List[str]] = None) -> str:
        fid = G.vec_id(vec)
        fam = self.s["families"].get(fid)
        if fam is None:
            self.s["families"][fid] = {"vec": vec, "kind": kind, "runs": [], "scores": [], "allocated": 0, "retired": False,
                                       "promoted": False, "parents": parents or [], "created_utc": _utc()}
            self.covered |= G.pairs_of(vec)
        return fid

    def _spec(self, vec: Dict[str, str], kind: str, reason: str, parents: Optional[List[str]] = None, seed: Optional[int] = None,
              init_tapes: Optional[List[str]] = None, stage: Optional[str] = None) -> Dict:
        fid = self._family(vec, kind, parents)
        rid = self._new_id()
        sd = seed if seed is not None else (self.s["seed"] * 7919 + int(rid[1:]))
        self.s["families"][fid]["allocated"] += 1
        self.s["counters"][kind] = self.s["counters"].get(kind, 0) + 1
        return {"id": rid, "family": fid, "vec": vec, "seed": sd, "ticks": self.s["ticks"], "cells": self.s["cells"], "workdir": str(self.runs_dir),
                "parents": parents or [], "reason": reason, "stage": stage or self.stage(), "kind": kind, "init_tapes": init_tapes or []}

    def _index(self, rec: Dict) -> None:
        self.runs.append(rec); self.by_family.setdefault(rec["family"], []).append(rec)

    def checkpoint(self) -> None:
        self.s["covered_pairs"] = sorted(list(p) for p in self.covered)
        self.s["n_runs"] = len(self.runs)
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.s, sort_keys=True, default=str), encoding="utf-8", newline="\n")
        os.replace(tmp, self.state_path)

    # ---- ingest --------------------------------------------------------------------------------------------------------
    def ingest(self, res: Dict, kind: str) -> None:
        vec = res["vec"]; fid = res["family"]; summ = res["summary"]
        ctrl = self._control_summary(vec)
        archive = [bytes.fromhex(h) for h in self.s["specimen_archive"][-200:]]
        trg = O.triggers(summ, vec, self.s["ticks"], ctrl, archive)
        score = O.trigger_score(trg)
        rec = {"id": res["id"], "family": fid, "vec": vec, "seed": res["seed"], "stage": res["stage"], "kind": kind, "reason": res["reason"],
               "parents": res["parents"], "triggers": trg, "score": score, "dir": res["dir"], "wall_s": summ.get("wall_s"),
               "summary": {k: summ.get(k) for k in ("final_alive", "alive_fraction", "extinct", "external_births", "endogenous_births", "replication_rate_tail",
                                                     "mean_fidelity_tail", "hifi_replication_rate_tail", "repro_span_tail", "solvers_tail", "best_score_tail",
                                                     "lineages_final", "arch_clusters_final", "cross_niche_transport", "coexistence_ticks", "n_exploits",
                                                     "exploit_kinds", "seed_lineage_share", "geometry", "config_sha256")},
               "first_crossing_tick": (summ.get("first_crossing") or {}).get("tick"),
               "first_replication": {k: (summ.get("first_replication") or {}).get(k) for k in ("tick", "seeded", "fidelity", "span", "mechanism")} if summ.get("first_replication") else None,
               "geometry": summ.get("geometry")}
        self._index(rec)
        with self.runs_path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
        fam = self.s["families"][fid]; fam["runs"].append(res["id"]); fam["scores"].append(score)
        top = (summ.get("top") or [{}])[0].get("tape")
        if top and trg.get("novelty_distance"):
            self.s["specimen_archive"].append(top)
        w = summ.get("wall_s") or 1.0
        self.s["run_wall_ema"] = w if self.s["run_wall_ema"] is None else 0.8 * self.s["run_wall_ema"] + 0.2 * w
        fired = [k for k in O.PROMOTING if trg.get(k)]
        if score >= 2 and not fam["promoted"] and kind not in ("positive_control",):
            fam["promoted"] = True
            self._decide("promote", fid, "run %s fired %d mechanical triggers: %s" % (res["id"], score, ",".join(fired)))
        if len(fam["runs"]) >= RETIRE_AFTER_RUNS and max(fam["scores"]) <= 1 and not fam["retired"]:
            fam["retired"] = True
            self._decide("retire", fid, "%d runs, best trigger score %d: silent family" % (len(fam["runs"]), max(fam["scores"])))
        if trg.get("exploit_recorded"):
            self._decide("exploit", fid, "run %s recorded exploits %s (specimens frozen in exploits.json)" % (res["id"], summ.get("exploit_kinds")))

    def _control_summary(self, vec: Dict[str, str]) -> Optional[Dict]:
        cv = dict(vec, reproduction="EXTERNAL", recombination=vec["recombination"])
        cv = G.repair(cv, protect=("reproduction",))
        fid = G.vec_id(cv)
        fam = self.s["families"].get(fid)
        if not fam or not fam["runs"]:
            return None
        rs = self.by_family.get(fid) or []
        if not rs:
            return None
        return {"alive_fraction": sum(r["summary"]["alive_fraction"] for r in rs) / len(rs)}

    # ---- producer ----------------------------------------------------------------------------------------------------------
    def produce(self, n: int) -> List[Dict]:
        st = self.stage()
        if self.s["positive_controls"] is None:
            return self._positive_control_specs()
        if st == "early":
            return self._explore_batch(n, with_pairs=True)
        if st == "middle":
            return self._middle_batch(n)
        return self._late_batch(n)

    def _positive_control_specs(self) -> List[Dict]:
        specs = []
        for c in C.CONTROL_VECS:
            specs.append(self._spec(c["vec"], "positive_control", "positive control: " + c["name"], stage="early"))
        return specs

    def _explore_batch(self, n: int, with_pairs: bool) -> List[Dict]:
        specs = []
        k = max(1, n // 2) if with_pairs else n
        # half of exploration insists on RANDOM init + endogenous physics (spontaneous-emergence treatments)
        vecs = G.sample_sparse(self.rng, k // 2, self.covered, fixed={"init": "RANDOM"})
        vecs += G.sample_sparse(self.rng, k - len(vecs), self.covered)
        for v in vecs:
            specs.append(self._spec(v, "exploration", "sparse pairwise coverage (+%d new pairs)" % len(G.pairs_of(v) - self.covered)))
            if with_pairs:
                mc = G.matched_controls(v)
                key = "endogenous_vs_exogenous" if v["reproduction"] in ENDOGENOUS else "exogenous_vs_endogenous"
                if key in mc:
                    specs.append(self._spec(mc[key], "control", "matched %s pair of %s" % (key, G.vec_id(v)), parents=[G.vec_id(v)], seed=specs[-1]["seed"]))
        return specs

    def _promoted_families(self) -> List[str]:
        out = []
        for fid, fam in self.s["families"].items():
            if fam["promoted"] and not fam["retired"] and fam["kind"] not in ("positive_control",):
                out.append(fid)
        return out

    def _weight(self, fid: str) -> float:
        fam = self.s["families"][fid]
        mean = sum(fam["scores"]) / max(1, len(fam["scores"]))
        uncertainty = 1.0 / (1 + len(fam["runs"]))          # fewer runs -> more to learn
        return 0.2 + mean + 2.0 * uncertainty

    def _middle_batch(self, n: int) -> List[Dict]:
        n_explore = max(1, int(round(EXPLORATION_FLOOR * n)))
        specs = self._explore_batch(n_explore, with_pairs=False)
        prom = self._promoted_families()
        if not prom:
            return specs + self._explore_batch(n - len(specs), with_pairs=True)
        weights = [self._weight(f) for f in prom]
        while len(specs) < n:
            fid = self.rng.choices(prom, weights=weights)[0]; fam = self.s["families"][fid]; v = fam["vec"]
            move = self.rng.choices(("replicate", "mutate", "cross", "control"), weights=(0.3, 0.35, 0.25, 0.10))[0]
            if move == "replicate":
                specs.append(self._spec(v, "promoted", "fresh-seed replicate of promoted family (weight %.2f)" % self._weight(fid), parents=[fid]))
            elif move == "mutate":
                nb = G.neighbours(v, self.rng, 1)
                if nb:
                    changed = [a for a in G.AXES if nb[0][a] != v[a]]
                    specs.append(self._spec(nb[0], "promoted", "one-factor mutation of promoted family on %s" % changed, parents=[fid]))
            elif move == "cross":
                name, tmpl = self.rng.choice(G.COLLISIONS)
                cv = G.cross(v, tmpl)
                if cv and G.vec_id(cv) != fid:
                    specs.append(self._spec(cv, "promoted", "collision cross '%s' onto promoted family" % name, parents=[fid]))
            else:
                mc = G.matched_controls(v)
                missing = [(k, cv) for k, cv in mc.items() if G.vec_id(cv) not in self.s["families"]]
                if missing:
                    k, cv = self.rng.choice(missing)
                    specs.append(self._spec(cv, "control", "matched control %s for promoted family" % k, parents=[fid]))
        return specs[:n]

    def _late_batch(self, n: int) -> List[Dict]:
        """Verification in TIERS: the strongest families get fresh seeds, their full matched-control set and
        interventions; when a tier is verified the next tier (by mean trigger score) is planned, until the clock."""
        plan = self.s.setdefault("late_plan", [])
        if all(p["done"] for p in plan):
            planned = {p["fid"] for p in plan}
            ranked = sorted((f for f in self._promoted_families() if f not in planned and len(self.s["families"][f]["runs"]) >= 1),
                            key=lambda f: -sum(self.s["families"][f]["scores"]) / max(1, len(self.s["families"][f]["scores"])))
            tier = []
            for fid in ranked[:TOP_K_LATE]:
                fam = self.s["families"][fid]; v = fam["vec"]
                best_run = max(self.by_family.get(fid) or [], key=lambda r: r["score"], default=None)
                tier.append({"fid": fid, "vec": v, "best_run": best_run["id"] if best_run else None, "done": False})
            if not tier:
                return []
            plan.extend(tier)
            self._decide("late_stage", None, "verification tier %d planned for %d families: %s" % (len(plan) // TOP_K_LATE, len(tier), [p["fid"] for p in tier]))
        specs = []
        for p in plan:
            if p["done"] or len(specs) >= n:
                continue
            fid = p["fid"]; v = p["vec"]
            for k in range(2):
                specs.append(self._spec(v, "verification", "late verification: fresh seed %d/2" % (k + 1), parents=[fid], seed=self.s["seed"] * 104729 + int(fid[:6], 16) + k))
            for name, cv in G.matched_controls(v).items():
                specs.append(self._spec(cv, "verification", "late verification: matched control %s" % name, parents=[fid], seed=specs[0]["seed"]))
            tapes = self._top_tapes(p["best_run"])
            if tapes:
                ext = G.repair(dict(v, reproduction="EXTERNAL"), protect=("reproduction",))
                if G.is_valid(ext):
                    specs.append(self._spec(ext, "intervention", "lineage transplant of %s's top tapes into its EXTERNAL control world" % p["best_run"],
                                            parents=[fid], init_tapes=tapes))
                nxt = {"ECHO": "INC", "INC": "COND_ONE", "COND_ONE": "COND_MULTI", "CONST": "ECHO", "COND_MULTI": "SUM2", "SUM2": "COND_MULTI"}[v["task"]]
                sw = G.repair(dict(v, task=nxt, env_dynamics="FIXED"), protect=("task",))
                if G.is_valid(sw):
                    specs.append(self._spec(sw, "intervention", "environment swap: %s's lineage continued under task %s" % (p["best_run"], nxt),
                                            parents=[fid], init_tapes=tapes))
            p["done"] = True
        return specs

    def _top_tapes(self, run_id: Optional[str]) -> List[str]:
        if not run_id:
            return []
        try:
            summ = json.loads((self.runs_dir / run_id / "summary.json").read_text(encoding="utf-8"))
            return [t["tape"] for t in summ.get("top", [])[:4]]
        except Exception:
            return []

    # ---- loop ------------------------------------------------------------------------------------------------------------------
    def run(self, batch_mult: int = 2, quiet: bool = False) -> None:
        pool = mp.Pool(self.workers)
        try:
            while True:
                rem = self.remaining_s()
                est = (self.s["run_wall_ema"] or 5.0) * batch_mult * 1.5
                if rem <= est:
                    self._decide("stop", None, "wall-clock boundary: %.0fs remain, a batch needs ~%.0fs" % (rem, est)); break
                st = self.stage()
                if not self.s["stage_log"] or self.s["stage_log"][-1]["stage"] != st:
                    self.s["stage_log"].append({"stage": st, "utc": _utc(), "runs_done": len(self.runs)})
                specs = self.produce(self.workers * batch_mult)
                if not specs:
                    self._decide("stop", None, "producer has nothing left to schedule in stage %s" % st); break
                kinds = {sp["id"]: sp["kind"] for sp in specs}
                for res in pool.imap_unordered(run_spec, specs):
                    self.ingest(res, kinds[res["id"]])
                    if not quiet:
                        r = self.runs[-1]
                        print(json.dumps({"run": r["id"], "stage": r["stage"], "kind": r["kind"], "score": r["score"], "fam": r["family"][:8],
                                          "repro": r["vec"]["reproduction"], "task": r["vec"]["task"], "alive": r["summary"]["alive_fraction"],
                                          "fid": r["summary"]["mean_fidelity_tail"], "solv": r["summary"]["solvers_tail"], "wall": r["wall_s"]}), flush=True)
                if self.s["positive_controls"] is None:
                    self._grade_positive_controls()
                    if not self.s["positive_controls"]["all_passed"]:
                        self._decide("halt", None, "a positive control FAILED: %s" % [c["name"] for c in self.s["positive_controls"]["results"] if not c["passed"]])
                        break
                self._batches += 1
                if self._batches % 25 == 0:
                    self.s["flags"] = self._flags()
                self.checkpoint()
        finally:
            pool.close(); pool.join()
        self.finalize()

    def _grade_positive_controls(self) -> None:
        results = [C.vm_executes()]
        for c in C.CONTROL_VECS:
            fid = G.vec_id(c["vec"])
            rs = [r for r in self.by_family.get(fid) or [] if r["kind"] == "positive_control"]
            ok = False; detail = None
            for r in rs:
                summ = json.loads((self.runs_dir / r["id"] / "summary.json").read_text(encoding="utf-8"))
                ok = bool(c["predicate"](summ)); detail = {k: summ.get(k) for k in ("alive_fraction", "mean_fidelity_tail", "replication_rate_tail", "solvers_tail", "seed_lineage_share")}
                detail["first_crossing"] = summ.get("first_crossing") is not None
            results.append({"name": c["name"], "passed": ok, "detail": detail, "family": fid})
        self.s["positive_controls"] = {"results": results, "all_passed": all(r["passed"] for r in results), "utc": _utc()}
        self._decide("positive_controls", None, "graded: " + ", ".join("%s=%s" % (r["name"], "PASS" if r["passed"] else "FAIL") for r in results))

    def _flags(self) -> List[Dict]:
        vec_of = {f: fam["vec"] for f, fam in self.s["families"].items()}
        return O.high_value_flags(self.by_family, vec_of)

    # ---- attribution / packet ------------------------------------------------------------------------------------------------------
    def _attribution(self) -> Dict:
        out = {}
        axis_prop = {"reproduction": "reproductive_mechanism", "world": "population_ecological", "spatial": "population_ecological",
                     "representation": "representation", "layout": "representation", "mutation": "representation", "mutation_rate": "representation",
                     "task": "world", "scoring": "world", "read_gate": "world", "env_dynamics": "world", "pressure": "population_ecological",
                     "init": "organism", "recombination": "reproductive_mechanism"}
        for p in self.s.get("late_plan", []):
            fid = p["fid"]; v = p["vec"]
            rs = self.by_family.get(fid) or []
            if not rs:
                continue
            sig = [k for k in O.PROMOTING if sum(1 for r in rs if r["triggers"].get(k)) >= max(1, len(rs) // 2)]
            fresh = [r for r in rs if r["kind"] == "verification"]
            reproduced = [k for k in sig if fresh and sum(1 for r in fresh if r["triggers"].get(k)) >= max(1, len(fresh) // 2)]
            rows = {}
            for k in sig:
                verdict = {}
                for name, cv in G.matched_controls(v).items():
                    cf = G.vec_id(cv); crs = self.by_family.get(cf) or []
                    if not crs:
                        continue
                    persists = sum(1 for r in crs if r["triggers"].get(k)) >= max(1, len(crs) // 2)
                    axis = [a for a in G.AXES if cv[a] != v[a]]
                    verdict[name] = {"persists_in_control": persists, "axis": axis, "property_if_removed": axis_prop.get(axis[0], "?") if axis else "?"}
                removed_by = [n for n, d in verdict.items() if not d["persists_in_control"]]
                trans = [r for r in self.runs if r["kind"] == "intervention" and fid in r["parents"] and "transplant" in (r["reason"] or "")]
                carried = any(r["triggers"].get(k) for r in trans)
                if k not in reproduced:
                    attributed = "measurement_artefact_or_seed_dependent"
                elif not removed_by:
                    attributed = "robust_to_all_matched_controls"
                else:
                    attributed = sorted({verdict[n]["property_if_removed"] for n in removed_by})
                rows[k] = {"reproduced_with_fresh_seeds": k in reproduced, "controls": verdict, "removed_by": removed_by,
                           "carried_by_transplant": carried, "attributed": attributed}
            out[fid] = {"vec": v, "signals": sig, "rows": rows}
        return out

    def _map(self) -> Dict:
        """The operational success criterion: per axis level, which structural choices generate replication, change
        accessibility, produce transitions, transfer, keep diversity, alter evolvability, or reliably fail."""
        m: Dict[str, Dict[str, Dict[str, float]]] = {}
        for a in G.AXES:
            m[a] = {}
            for lvl in G.FACTORS[a]:
                rs = [r for r in self.runs if r["vec"][a] == lvl and r["kind"] != "positive_control"]
                if not rs:
                    continue
                n = len(rs)
                m[a][lvl] = {"runs": n,
                             "replication": round(sum(1 for r in rs if r["triggers"].get("replication")) / n, 3),
                             "spontaneous": round(sum(1 for r in rs if r["triggers"].get("spontaneous_replication")) / n, 3),
                             "accessibility_gain": round(sum(1 for r in rs if ((r["geometry"] or {}).get("beneficial_density_gain") or 0) > 0.05) / n, 3),
                             "transition_escape": round(sum(1 for r in rs if r["triggers"].get("escape")) / n, 3),
                             "moat_crossing": round(sum(1 for r in rs if r["triggers"].get("moat_crossing")) / n, 3),
                             "diversity_coexistence": round(sum(1 for r in rs if r["triggers"].get("coexistence")) / n, 3),
                             "transport": round(sum(1 for r in rs if r["triggers"].get("cross_niche_transport")) / n, 3),
                             "reliable_failure_extinct": round(sum(1 for r in rs if r["summary"].get("extinct")) / n, 3)}
        return m

    def finalize(self) -> None:
        self.s["stopped"] = _utc()
        self.s["flags"] = self._flags()
        self.s["attribution"] = self._attribution()
        self.s["map"] = self._map()
        self.checkpoint()
        O.write_jsonl(self.wd / "families.jsonl", [dict(id=f, **fam) for f, fam in self.s["families"].items()])
        O.write_jsonl(self.wd / "decisions.jsonl", self.s["decisions"])
        O.write_json(self.wd / "flags.json", self.s["flags"])
        O.write_json(self.wd / "attribution.json", self.s["attribution"])
        O.write_json(self.wd / "map.json", self.s["map"])
        (self.wd / "CAMPAIGN_PACKET.md").write_text(self.packet(), encoding="utf-8", newline="\n")

    def packet(self) -> str:
        s = self.s; runs = self.runs; fams = s["families"]
        L = []
        L.append("# Z80 x ATLAS COMBINATORIAL CAMPAIGN -- packet (Bellerophon / BEE harness)\n")
        L.append("start %s  stop %s  window %.2f h  workers %d  ticks/run %d  cells %d" % (s["start_utc"], s["stopped"], s["hours"], self.workers, s["ticks"], s["cells"]))
        L.append("grammar sha256 %s   thresholds sha256 %s   seed %d" % (s["grammar_hash"], s["thresholds_hash"], s["seed"]))
        L.append("runs %d   families %d   promoted %d   retired %d   specimen archive %d" % (
            len(runs), len(fams), sum(1 for f in fams.values() if f["promoted"]), sum(1 for f in fams.values() if f["retired"]), len(s["specimen_archive"])))
        L.append("runs by kind: " + ", ".join("%s=%d" % (k, v) for k, v in sorted(s["counters"].items())))
        L.append("stages: " + "; ".join("%s at %s (%d runs done)" % (x["stage"], x["utc"], x["runs_done"]) for x in s["stage_log"]))
        L.append("pairs covered %d" % len(self.covered))
        L.append("\n## Positive controls")
        pc = s.get("positive_controls") or {}
        for r in pc.get("results", []):
            L.append("  %-32s %s  %s" % (r["name"], "PASS" if r["passed"] else "FAIL", json.dumps(r.get("detail") or r.get("checks"), sort_keys=True)))
        L.append("  all_passed = %s" % pc.get("all_passed"))
        L.append("\n## Unavailable levels (declared, never substituted)")
        for k, v in s["unavailable"].items():
            L.append("  %s: %s" % (k, v))
        L.append("\n## High-value flags")
        for f in s["flags"] or []:
            L.append("  " + json.dumps(f, sort_keys=True))
        if not s["flags"]:
            L.append("  none")
        L.append("\n## Strongest families (mean trigger score; promoting triggers fired in >= half the runs)")
        ranked = sorted(((sum(f["scores"]) / max(1, len(f["scores"])), fid) for fid, f in fams.items() if f["runs"] and f["kind"] != "positive_control"), reverse=True)[:15]
        for mean, fid in ranked:
            f = fams[fid]; rs = self.by_family.get(fid) or []
            sig = [k for k in O.PROMOTING if sum(1 for r in rs if r["triggers"].get(k)) >= max(1, len(rs) // 2)]
            v = f["vec"]
            L.append("  %s  mean %.2f  runs %d  %s/%s/%s/%s/%s/%s  %s" % (fid, mean, len(rs), v["reproduction"], v["world"], v["spatial"], v["task"], v["scoring"], v["read_gate"], ",".join(sig)))
        L.append("\n## Attribution (late verification; mechanical)")
        for fid, a in (s["attribution"] or {}).items():
            L.append("  family %s signals %s" % (fid, a["signals"]))
            for k, row in a["rows"].items():
                L.append("    %-28s fresh=%s removed_by=%s transplant_carried=%s -> %s" % (k, row["reproduced_with_fresh_seeds"], row["removed_by"], row["carried_by_transplant"], row["attributed"]))
        L.append("\n## Map: trigger rates by factor level (runs; replication / spontaneous / accessibility gain / escape / moat / coexistence / transport / extinct)")
        for a, lv in (s["map"] or {}).items():
            for lvl, d in lv.items():
                L.append("  %-14s %-22s n=%-4d %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f" % (a, lvl, d["runs"], d["replication"], d["spontaneous"], d["accessibility_gain"],
                                                                                          d["transition_escape"], d["moat_crossing"], d["diversity_coexistence"], d["transport"], d["reliable_failure_extinct"]))
        L.append("\n## Exploits recorded")
        ex = [d for d in s["decisions"] if d["kind"] == "exploit"]
        L.append("  %d runs recorded exploits (specimens frozen in their exploits.json)" % len(ex))
        L.append("\n## Decisions (last 40)")
        for d in s["decisions"][-40:]:
            L.append("  %s %-18s %s %s" % (d["utc"], d["kind"], (d.get("family") or "-")[:16], d["reason"]))
        L.append("\nFiles: state.json, runs.jsonl, families.jsonl, decisions.jsonl, flags.json, attribution.json, map.json, runs/<id>/{config,summary,geometry,specimens,exploits}.json + ticks/events/snapshots.jsonl")
        L.append("Scientific interpretation is left to the subsequent review. Promotion here meant 'allocate more experiments', never 'claim accepted'.")
        return "\n".join(L) + "\n"
