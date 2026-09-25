"""The scheduler: 72 hours of producer/consumer search, decided by arithmetic.

NO MODEL IN THIS LOOP. Everything below is counting, thresholds and an upper-confidence
bound. The only judgement calls were made before the campaign started, when the grammar
and these weights were frozen and hashed; after that the campaign cannot acquire a new
opinion, only new counts.

THREE STAGES ON ONE WALL CLOCK
  EARLY   broad coverage and calibration. The producer's coverage term dominates.
  MIDDLE  expansion: cells whose signals fired get more seeds and a bigger tier, while an
          exploration floor keeps a fixed share of the budget on combinations nobody has
          touched, so an early noisy winner cannot take the campaign over.
  LATE    expansion stops with time to spare. The strongest families are re-run on fresh
          seeds, against their matched controls, and against single-factor interventions
          that try to attribute the effect to a world, an organism, a representation, a
          reproductive mechanism, an ecology - or to the measurement.

PROMOTION MEANS COMPUTE, NOT TRUTH. A promoted family gets more experiments. Nothing in
this file decides that a mechanism is real; that is post-campaign adjudication, and the
packet is written so someone else can do it against the record.

SEEDED INSTRUMENTS CANNOT WIN. A run seeded with a hand-written replicator scores a
fraction of the replication signal and can never carry a spontaneous-origin flag. The
grammar already forbids the other half of that mistake by requiring random initial
populations in spontaneity tests.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import pathlib
import random
import time
import traceback

import anticheat
import assays
import grammar as G
import observatory as OB
import producer as PR
import world

STAGES = (("EARLY", 0.00), ("MIDDLE", 0.35), ("LATE", 0.78))
EARLY_S_CAP = 5000        # screening runs after which EARLY stops screening and deepens
EARLY_COV_TARGET = 0.55   # priority-pair coverage that also ends the screening phase
PROMOTE_T = 0.42          # interest at which a family earns more compute
VERIFY_T = 0.50           # interest at which a family becomes a late-verification candidate
RETIRE_T = 0.10           # interest below which a family stops being re-emitted
MAX_PROMO_SHARE = 0.45    # promotions may never exceed this share of submissions

SIGNALS = {
    "replicated": 0.30, "crossed": 0.30, "entropy_drop": 0.10, "compression": 0.10,
    "novel_genome": 0.10, "coexistence": 0.05, "transition": 0.05, "serendipity": 0.10,
    "persistence": 0.05, "invasion": 0.10,
}


def _worker(job):
    """Runs in a separate process. Returns a compact record; raises nothing."""
    t0 = time.time()
    try:
        r = world.run_cell(job["cell"], job["seed"], tier=job["tier"],
                           invaders=job.get("invaders", 0))
        s = r["summary"]
        a = assays.run_assays(job["cell"], s, r["series"], r["specimens"], job["seed"])
        ser = OB.serendipity(r["series"], s)
        return {"job": job, "ok": True, "summary": s, "series": r["series"],
                "specimens": r["specimens"], "lineage_tail": r["lineage_tail"],
                "assays": a, "serendipity": ser, "wall_s": round(time.time() - t0, 2)}
    except Exception as e:                                        # noqa: BLE001
        return {"job": job, "ok": False, "error": "%s: %s" % (type(e).__name__, e),
                "traceback": traceback.format_exc()[-1500:], "wall_s": round(time.time() - t0, 2)}


class Scheduler:
    def __init__(self, root, hours=72.0, workers=6, seed=1, batch=None, disk_budget_gb=60.0):
        self.root = pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.obs = OB.Observatory(self.root, disk_budget_gb=disk_budget_gb)
        self.prod = PR.Producer(seed=seed)
        self.rng = random.Random(seed ^ 0xBEEF)
        self.workers = workers
        self.batch = batch or max(workers * 2, 8)
        self.hours = hours
        self.t_start = time.time()
        self.deadline = self.t_start + hours * 3600
        self.grammar_hash = G.grammar_hash()

        self.submitted = 0
        self.completed = 0
        self.failed = 0
        self.promotions = 0
        self.n_by_stage = {"EARLY": 0, "MIDDLE": 0, "LATE": 0}
        self.families = {}          # family -> aggregate record
        self.retired = set()
        self.genome_archive = set()
        self.pending_jobs = []
        self.specials = 0
        self.est = {"S": 25.0, "M": 70.0, "L": 160.0}
        self.state_path = self.root / "STATE.json"
        self.specials_path = self.root / "SPECIALS.jsonl"
        self.errors_path = self.root / "ERRORS.jsonl"

    # ------------------------------------------------------------------ clock
    def elapsed_frac(self):
        return (time.time() - self.t_start) / (self.hours * 3600)

    def stage(self):
        f = self.elapsed_frac()
        s = "EARLY"
        for name, start in STAGES:
            if f >= start:
                s = name
        return s

    def time_left(self):
        return self.deadline - time.time()

    def tier_for(self, stage):
        """Compute per run, escalated when screening has done its job.

        Coverage saturates long before the clock does: a screening run takes seconds, so
        an unbounded EARLY stage would spend twenty-five hours producing tens of thousands
        of shallow runs and an index too large to be useful. Screening therefore ends on
        whichever comes first - a run cap or a coverage target - and the remaining early
        time is spent at depth. Both constants are preregistered.
        """
        base = {"EARLY": "S", "MIDDLE": "M", "LATE": "L"}[stage]
        if stage == "EARLY":
            cov = self.prod.coverage_report()["priority_pairs_share"]
            if self.completed >= EARLY_S_CAP or cov >= EARLY_COV_TARGET:
                return "M"
        return base

    # ------------------------------------------------------------------ jobs
    def _run_id(self, cell, seed, tier, attempt=0):
        return "%s-s%d-t%s-a%d" % (G.cell_id(cell), seed, tier, attempt)

    def make_job(self, cell, seed, tier, role="EXPERIMENT", reason="", stage=None,
                 control_of=None, control_axis=None, parent_run=None, invaders=0):
        cell = dict(cell)
        cell.pop("tier", None)     # tier is compute, not semantics: it must not shard families
        fam = G.cell_id(cell)
        attempt = 0
        rid = self._run_id(cell, seed, tier, attempt)
        while rid in self.families.get(fam, {}).get("runs", {}):
            attempt += 1
            rid = self._run_id(cell, seed, tier, attempt)
        return {"run_id": rid, "family": fam, "cell": cell, "derived": G.derived(cell),
                "seed": seed, "tier": tier, "role": role, "reason": reason,
                "stage": stage or self.stage(), "control_of": control_of,
                "control_axis": control_axis, "parent_run": parent_run, "invaders": invaders,
                "grammar_hash": self.grammar_hash}

    def fill_queue(self):
        """Top the queue up with the stage's work: proposals plus their matched controls."""
        stage = self.stage()
        tier = self.tier_for(stage)
        if stage == "LATE":
            self._queue_verification()
            return
        want = max(0, self.batch - len(self.pending_jobs))
        if want <= 0:
            return
        props = self.prod.propose(max(1, want // 2), stage=stage, tier=tier)
        for p in props:
            cell = p["cell"]
            if G.cell_id(cell) in self.retired:
                continue
            seed = self.rng.randrange(1, 10_000)
            job = self.make_job(cell, seed, tier, reason=p["reason"], stage=stage,
                                control_axis=p["control_axis"])
            self.pending_jobs.append(job)
            ax = p["control_axis"]
            partner = G.control_partner(cell, ax) if ax else None
            if partner is not None:
                self.pending_jobs.append(self.make_job(
                    partner, seed, tier, role="CONTROL",
                    reason="matched control on %s for %s" % (ax, job["run_id"]),
                    stage=stage, control_of=job["run_id"], control_axis=ax))

    def _queue_verification(self):
        """LATE: challenge the strongest families instead of expanding."""
        if self.pending_jobs:
            return
        cands = [f for f, rec in self.families.items()
                 if rec["best_interest"] >= VERIFY_T and not rec["voided"]
                 and rec.get("verified", 0) < 1]
        cands.sort(key=lambda f: -self.families[f]["best_interest"])
        if not cands:
            # nothing met the bar: keep the exploration floor running rather than idling,
            # because an empty late stage would waste the budget that is left
            props = self.prod.propose(max(2, self.batch // 2), stage="LATE", tier="M")
            for p in props:
                self.pending_jobs.append(self.make_job(
                    p["cell"], self.rng.randrange(1, 10_000), "M",
                    reason="late floor: no family met the verification bar", stage="LATE",
                    control_axis=p["control_axis"]))
            return
        fam = cands[0]
        rec = self.families[fam]
        rec["verified"] = rec.get("verified", 0) + 1
        cell = rec["cell"]
        base_reason = "late verification of %s (best interest %.3f)" % (fam, rec["best_interest"])
        for k in range(2):                                    # fresh seeds
            self.pending_jobs.append(self.make_job(
                cell, self.rng.randrange(10_000, 99_999), "L", role="VERIFY",
                reason=base_reason + " : fresh seed", stage="LATE", parent_run=rec["best_run"]))
        ax = rec.get("control_axis") or "reproduction"
        partner = G.control_partner(cell, ax)
        if partner is not None:
            self.pending_jobs.append(self.make_job(
                partner, self.rng.randrange(10_000, 99_999), "L", role="CONTROL",
                reason=base_reason + " : matched control on " + ax, stage="LATE",
                control_of=rec["best_run"], control_axis=ax))
        # single-factor interventions: attribute the effect to a level of the system
        for ax2 in ("read_order", "task_transform", "copy_primitive", "self_location",
                    "structure", "environment", "representation", "mutation_locality"):
            alt = G.control_partner(cell, ax2)
            if alt is None:
                if ax2 == "representation":
                    alt = dict(cell)
                    alt["representation"] = "Z8_SLOTTED" if cell["representation"] != "Z8_SLOTTED" else "Z8_64"
                    alt = G.repair(alt)
                if alt is None:
                    continue
            self.pending_jobs.append(self.make_job(
                alt, self.rng.randrange(10_000, 99_999), "L", role="INTERVENTION",
                reason=base_reason + " : intervention on " + ax2, stage="LATE",
                control_of=rec["best_run"], control_axis=ax2))

    # ------------------------------------------------------------------ signals
    def signals(self, job, summary, serendipity_fired, assay):
        d = job["derived"]
        seeded = d["seeded_instrument"]
        sig = {}
        sig["replicated"] = (1.0 if summary.get("replicated") else 0.0) * (0.25 if seeded else 1.0)
        sig["crossed"] = 1.0 if summary.get("crossed") else 0.0
        ed = summary.get("entropy_drop")
        sig["entropy_drop"] = min(1.0, max(0.0, (ed or 0.0) / 2.0))
        span = summary.get("span_mean_final")
        L = world.REP_LEN[job["cell"]["representation"]]
        sig["compression"] = min(1.0, max(0.0, (L - span) / L)) if span else 0.0
        novel = 0
        for sp in (summary.get("first_replicator"), summary.get("first_cross")):
            if sp and sp.get("genome") and sp["genome"][:32] not in self.genome_archive:
                novel = 1
        sig["novel_genome"] = float(novel)
        occ = summary.get("niche_occupancy") or []
        sig["coexistence"] = 1.0 if (len(occ) > 1 and min(occ) > 0
                                     and min(occ) / max(max(occ), 1) > 0.2) else 0.0
        tr = (assay or {}).get("transitions") or {}
        sig["transition"] = 1.0 if any((v.get("share_of_range") or 0) > 0.5 for v in tr.values()) else 0.0
        sig["serendipity"] = min(1.0, len(serendipity_fired) / 4.0)
        sig["persistence"] = 1.0 if (summary.get("pop_final", 0) > 0 and not summary.get("extinct")) else 0.0
        inv = summary.get("invader_share_final")
        sig["invasion"] = float(inv) if inv else 0.0
        if summary.get("voided"):
            for k in sig:
                sig[k] = 0.0
        interest = sum(SIGNALS[k] * v for k, v in sig.items())
        return sig, round(min(1.0, interest), 4)

    def special_flags(self, job, summary, rec):
        """The directive's preserve-immediately list. Each needs a comparison, so each is
        computed against this family's own matched control or against a sibling cell that
        differs in exactly one factor."""
        out = []
        cell, d = job["cell"], job["derived"]
        ctrl = rec.get("control_summary")
        if summary.get("crossed") and d["endogenous"] and ctrl is not None \
                and not ctrl.get("crossed") and rec.get("control_axis") == "reproduction":
            out.append({"flag": "REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION",
                        "evidence": {"endogenous_held": summary.get("held_max"),
                                     "external_held": ctrl.get("held_max")}})
        if summary.get("crossed") and d["constant_kind"] == "INCREMENTAL" \
                and rec.get("sibling_atomic") is not None and not rec["sibling_atomic"].get("crossed"):
            out.append({"flag": "REACHED_ONLY_IN_INCREMENTAL_REPRESENTATION",
                        "evidence": {"incremental_held": summary.get("held_max"),
                                     "atomic_held": rec["sibling_atomic"].get("held_max")}})
        if summary.get("crossed") and cell["structure"] == "RESERVOIR" and d["moat"]:
            out.append({"flag": "RESERVOIR_CROSSED_A_MOAT",
                        "evidence": {"held": summary.get("held_max"),
                                     "niche_occupancy": summary.get("niche_occupancy")}})
        if summary.get("replicated") and not d["seeded_instrument"] and d["spontaneity_test"]:
            out.append({"flag": "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES",
                        "evidence": summary.get("first_replicator")})
        if summary.get("replicated") and summary.get("crossed") and cell["pressure"] in (
                "TASK_GATED_INTERACTION", "RESOURCE_GATED", "MINIMAL_CRITERION"):
            sp = summary.get("span_mean_final")
            if sp and sp < world.REP_LEN[cell["representation"]] * 0.75:
                out.append({"flag": "REPRODUCTIVE_ARCHITECTURE_CHANGED_UNDER_TASK_DEMAND",
                            "evidence": {"span_mean_final": sp, "pressure": cell["pressure"]}})
        return out

    # ------------------------------------------------------------------ completion
    def on_complete(self, res):
        job = res["job"]
        fam = job["family"]
        rec = self.families.setdefault(fam, {
            "family": fam, "cell": job["cell"], "derived": job["derived"], "runs": {},
            "best_interest": 0.0, "best_run": None, "voided": False, "n_runs": 0,
            "control_axis": job.get("control_axis"), "control_summary": None,
            "sibling_atomic": None, "crossed_any": False, "replicated_any": False})
        if not res["ok"]:
            self.failed += 1
            with self.errors_path.open("a", encoding="ascii") as fh:
                fh.write(json.dumps({"run_id": job["run_id"], "cell": job["cell"],
                                     "error": res["error"], "traceback": res.get("traceback"),
                                     "ts": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
            rec["runs"][job["run_id"]] = {"ok": False}
            return
        s = res["summary"]
        sig, interest = self.signals(job, s, res["serendipity"], res["assays"])
        self.est[job["tier"]] = 0.8 * self.est[job["tier"]] + 0.2 * res["wall_s"]

        if job["role"] == "CONTROL" and job["control_of"]:
            for r2 in self.families.values():
                if job["control_of"] in r2["runs"]:
                    r2["control_summary"] = s
                    break
        specials = self.special_flags(job, s, rec)
        for sp in specials:
            self.specials += 1
            with self.specials_path.open("a", encoding="ascii") as fh:
                fh.write(json.dumps({"run_id": job["run_id"], "family": fam, "cell": job["cell"],
                                     "flag": sp["flag"], "evidence": sp["evidence"],
                                     "seeded_instrument": job["derived"]["seeded_instrument"],
                                     "ts": time.strftime("%Y-%m-%d %H:%M:%S")}, default=str) + "\n")

        paths = self.obs.write_run(job["run_id"], fam,
                                   {"job": job, "grammar_hash": self.grammar_hash,
                                    "tier_params": G.TIERS[job["tier"]]},
                                   {"summary": s, "assays": res["assays"],
                                    "serendipity": res["serendipity"], "signals": sig,
                                    "interest": interest, "specials": specials,
                                    "wall_s": res["wall_s"]},
                                   res["series"], res["lineage_tail"], res["specimens"])
        self.obs.append_index({
            "run_id": job["run_id"], "family": fam, "cell": job["cell"], "derived": job["derived"],
            "seed": job["seed"], "tier": job["tier"], "role": job["role"],
            "control_of": job["control_of"], "control_axis": job["control_axis"],
            "parent_run": job["parent_run"], "reason": job["reason"], "stage": job["stage"],
            "signals": sig, "interest": interest, "flags": s.get("flags", []),
            "voided": s.get("voided", False), "specials": [x["flag"] for x in specials],
            "serendipity": [x["trigger"] for x in res["serendipity"]],
            "assay_axis": (res["assays"] or {}).get("axis"),
            "summary": {k: s.get(k) for k in (
                "pop_final", "extinct", "births_endogenous", "births_external", "deaths",
                "comp_max", "held_max", "crossed", "replicated", "replication_rate",
                "entropy_drop", "dom_share_final", "uniq_final", "len_mean_final",
                "fid_mean_final", "span_mean_final", "invader_share_final",
                "reads_at_answer_of_best", "niche_occupancy", "epochs_run", "ops")},
            "paths": paths, "wall_s": res["wall_s"],
            "ts": time.strftime("%Y-%m-%d %H:%M:%S")})

        for sp in res["specimens"][:2]:
            if sp["hash"] not in self.genome_archive:
                self.genome_archive.add(sp["hash"])
                if res["serendipity"] or s.get("crossed") or s.get("replicated"):
                    self.obs.append_specimen({"run_id": job["run_id"], "family": fam,
                                              "cell": job["cell"], "specimen": sp,
                                              "triggers": [x["trigger"] for x in res["serendipity"]],
                                              "seeded_instrument": job["derived"]["seeded_instrument"]})

        rec["n_runs"] += 1
        rec["runs"][job["run_id"]] = {"ok": True, "interest": interest, "role": job["role"]}
        rec["crossed_any"] = rec["crossed_any"] or bool(s.get("crossed"))
        rec["replicated_any"] = rec["replicated_any"] or bool(s.get("replicated"))
        if s.get("voided"):
            rec["voided"] = True
        if interest > rec["best_interest"]:
            rec["best_interest"], rec["best_run"] = interest, job["run_id"]
        self.prod.observe(job["cell"], interest)
        self.completed += 1
        self.n_by_stage[job["stage"]] = self.n_by_stage.get(job["stage"], 0) + 1

        if job["role"] == "EXPERIMENT":
            self._maybe_promote(job, rec, interest)
        if rec["n_runs"] >= 3 and rec["best_interest"] < RETIRE_T:
            self.retired.add(fam)

    def _maybe_promote(self, job, rec, interest):
        stage = self.stage()
        if stage == "LATE" or interest < PROMOTE_T:
            return
        if self.promotions > MAX_PROMO_SHARE * max(1, self.submitted):
            return                                    # the exploration floor outranks a winner
        nxt = {"S": "M", "M": "L", "L": None}[job["tier"]]
        if nxt is None:
            return
        self.promotions += 1
        reason = ("promoted from %s: interest %.3f >= %.2f (more compute, not a claim)"
                  % (job["run_id"], interest, PROMOTE_T))
        self.pending_jobs.append(self.make_job(
            job["cell"], self.rng.randrange(1, 10_000), nxt, reason=reason,
            stage=stage, parent_run=job["run_id"], control_axis=job["control_axis"]))
        # the atomic sibling: the accessibility comparison the campaign exists to make
        if job["derived"]["constant_kind"] == "INCREMENTAL":
            sib = G.control_partner(job["cell"], "task_transform")
            if sib is not None:
                self.pending_jobs.append(self.make_job(
                    sib, job["seed"], nxt, role="CONTROL",
                    reason=reason + " : atomic-constant sibling", stage=stage,
                    control_of=job["run_id"], control_axis="task_transform"))

    # ------------------------------------------------------------------ persistence
    def save_state(self):
        st = {"t_start": self.t_start, "hours": self.hours, "grammar_hash": self.grammar_hash,
              "submitted": self.submitted, "completed": self.completed, "failed": self.failed,
              "promotions": self.promotions, "specials": self.specials,
              "n_by_stage": self.n_by_stage, "retired": sorted(self.retired),
              "est": self.est, "producer": self.prod.state(),
              "families": {f: {k: v for k, v in rec.items() if k not in ("runs",)}
                           for f, rec in self.families.items()},
              "family_run_counts": {f: len(rec["runs"]) for f, rec in self.families.items()},
              "observatory": self.obs.stats(),
              "elapsed_h": round((time.time() - self.t_start) / 3600, 3),
              "stage": self.stage(), "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=1, ensure_ascii=True, default=str), encoding="ascii")
        tmp.replace(self.state_path)

    def load_state(self):
        if not self.state_path.exists():
            return False
        st = json.loads(self.state_path.read_text(encoding="ascii"))
        if st.get("grammar_hash") != self.grammar_hash:
            raise SystemExit("REFUSE: resume with a different grammar hash (%s != %s)"
                             % (st.get("grammar_hash"), self.grammar_hash))
        self.t_start = st["t_start"]
        self.deadline = self.t_start + self.hours * 3600
        self.submitted, self.completed = st["submitted"], st["completed"]
        self.failed, self.promotions = st["failed"], st["promotions"]
        self.specials = st.get("specials", 0)
        self.n_by_stage = st.get("n_by_stage", self.n_by_stage)
        self.retired = set(st.get("retired", []))
        self.est = st.get("est", self.est)
        self.prod.load(st.get("producer", {}))
        for f, rec in st.get("families", {}).items():
            rec["runs"] = {}
            self.families[f] = rec
        return True

    # ------------------------------------------------------------------ the loop
    def run(self, heartbeat=None):
        print("CAMPAIGN start: %.1f h, %d workers, grammar %s"
              % (self.hours, self.workers, self.grammar_hash[:12]), flush=True)
        last_save = 0.0
        with cf.ProcessPoolExecutor(max_workers=self.workers) as ex:
            futures = {}
            while True:
                left = self.time_left()
                stage = self.stage()
                if left <= 0:
                    break
                # only submit what can plausibly finish
                if left > self.est[self.tier_for(stage)] * 1.15:
                    self.fill_queue()
                    while self.pending_jobs and len(futures) < self.workers * 2:
                        job = self.pending_jobs.pop(0)
                        futures[ex.submit(_worker, job)] = job
                        self.submitted += 1
                if not futures:
                    if left <= self.est[self.tier_for(stage)] * 1.15:
                        break
                    time.sleep(1.0)
                    continue
                done, _ = cf.wait(list(futures), timeout=20, return_when=cf.FIRST_COMPLETED)
                for fut in done:
                    job = futures.pop(fut)
                    try:
                        res = fut.result()
                    except Exception as e:                        # noqa: BLE001
                        res = {"job": job, "ok": False, "error": "future: %s" % e,
                               "traceback": "", "wall_s": 0.0}
                    self.on_complete(res)
                if time.time() - last_save > 30:
                    self.save_state()
                    last_save = time.time()
                    if heartbeat:
                        heartbeat(self)
            # clean stop: let what is running finish, then freeze
            print("CAMPAIGN wall clock reached; draining %d running" % len(futures), flush=True)
            for fut in cf.as_completed(list(futures), timeout=max(60, self.est["L"] * 2)):
                job = futures.pop(fut)
                try:
                    self.on_complete(fut.result())
                except Exception as e:                            # noqa: BLE001
                    self.on_complete({"job": job, "ok": False, "error": str(e), "wall_s": 0.0})
        self.save_state()
        print("CAMPAIGN done: %d completed, %d failed, %d specials"
              % (self.completed, self.failed, self.specials), flush=True)
        return self.summary()

    def summary(self):
        fams = sorted(self.families.values(), key=lambda r: -r["best_interest"])
        return {"grammar_hash": self.grammar_hash, "hours": self.hours,
                "elapsed_h": round((time.time() - self.t_start) / 3600, 3),
                "submitted": self.submitted, "completed": self.completed, "failed": self.failed,
                "promotions": self.promotions, "specials": self.specials,
                "families": len(self.families), "retired": len(self.retired),
                "by_stage": self.n_by_stage,
                "crossed_families": sum(1 for r in fams if r["crossed_any"]),
                "replicated_families": sum(1 for r in fams if r["replicated_any"]),
                "voided_families": sum(1 for r in fams if r["voided"]),
                "coverage": self.prod.coverage_report(),
                "observatory": self.obs.stats(),
                "top_families": [{"family": r["family"], "interest": r["best_interest"],
                                  "crossed": r["crossed_any"], "replicated": r["replicated_any"],
                                  "cell": r["cell"]} for r in fams[:25]]}
