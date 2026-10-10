"""Exploration arms at matched compute: ordinary search and ONE-FACTOR archive arms (Nyx B1 factorisation), with the
random-archive control matched on cell count AND restore frequency.

Unified driver (every arm). The run is a sequence of BURSTS. A burst starts with a RESTORE (a parent is selected; for
TFS-1 programs this is a genotype copy, never an environment-state restore) and then makes L = `burst` mutation steps as
a neutral chain: child = mutate(current); the child is evaluated on ALL dev examples (1 search charge); the chain
moves to the child iff it is not all-FAIL and its credit (channel `credit`, default exact dev credit) >= the current
one. Restore frequency is therefore exactly ceil((charges - starts) / L) for every arm with the same L (A-CHAIN: a single
restore); the start programs are evaluated (and charged) once at the beginning of every arm.

Arms (factor changed relative to the row above it in brackets):
  A-ENUM        ordinary TFS-1 keyed enumeration (measure.hitting_cost), no archive
  A-FRESH       restart: every burst restores a generic START program; nothing is retained          [baseline]
  A-CHAIN       one neutral chain for the whole budget (no restore)                                  [no restarts]
  B1-RETAIN     retain every non-all-FAIL child whose credit >= its chain parent's (genome retention);
                restore uniformly over retained entries                                              [RETENTION]
  B2-DESCSEL    B1's admission; restore = choose a CELL with weight 1/sqrt(1 + times chosen), then an entry uniformly
                in that cell                                                                         [SELECTION]
  B3-CELLADMIT  admission = a child in a NEW cell is admitted even if worse; in an occupied cell it replaces the
                incumbent iff strictly better (one elite per cell); restore uniformly over entries   [ADMISSION]
  C3-RAND       B3 with the RAND:K genotype-hash cell function, K calibrated outcome-blind so that the realised cell
                count matches B3's; same L                                               [random-archive control]
  C2-RAND       B2 with RAND:K, K matched to B2's realised cell count                  [random-selection control]

Archive entries record: program (genotype text + term), descriptor cell, exact and partial dev credit, acquisition
cost (charge), lineage (anchor parent entry id; full trajectory via lineage()), the burst index and step at
acquisition, the RNG state (sha256 of random.getstate(), full state if store_rng=True), and descendant outcomes
(children, admitted children, best child credit, dev-consistent and qualified descendants).

Target-blindness: archive and chain decisions are functions of (genotype, dev outputs, dev targets, probe outputs)
only. The Certifier (test + witness + tribunal) is consulted ONLY for a dev-consistent child and its answer only
decides whether the run stops (and what is logged as a hit). With stop_on_hit=False the decision log is provably
independent of the certifier (tested by perturbing test outputs and the witness).
"""
import copy
import hashlib
import math
from collections import Counter
from typing import Dict, List, Optional, Sequence

from tfs1 import core as C
from tfs1.enum import Enumerator, canon_comm
from tfs1.mutate import Mutator, rng_for

from . import common as K
from . import descriptors as DS

SPECS = {
    "A-FRESH": {"admission": "none", "selection": "start", "descriptor": False},
    "A-CHAIN": {"admission": "none", "selection": "start", "descriptor": False, "single_burst": True},
    "B1-RETAIN": {"admission": "nondecreasing", "selection": "uniform", "descriptor": False},
    "B2-DESCSEL": {"admission": "nondecreasing", "selection": "cell_count", "descriptor": True},
    "B3-CELLADMIT": {"admission": "cell", "selection": "uniform", "descriptor": True},
    "C3-RAND": {"admission": "cell", "selection": "uniform", "descriptor": True, "random": True},
    "C2-RAND": {"admission": "nondecreasing", "selection": "cell_count", "descriptor": True, "random": True},
}
DEFAULT_BURST = 10


def skeleton(t, lib=None) -> str:
    """Mechanism skeleton = sorted multiset of base primitives of the fully expanded program."""
    e = lib.expand(t) if lib is not None else t
    cnt = Counter()

    def go(u):
        tag = u[0]
        if tag in C.PRIM_SIGS:
            cnt[tag] += 1
        for c in C.children(u):
            go(c)
    go(e)
    return ",".join("%s%d" % (k, v) for k, v in sorted(cnt.items()))


class Search:
    """One arm run. Deterministic given (task view, library, spec, descriptor, seed, budget, burst)."""

    def __init__(self, view: K.LearnerView, certifier: Optional[K.Certifier], E: Enumerator, arm: str,
                 seed, budget: int, burst: int = DEFAULT_BURST, descriptor: Optional[str] = None,
                 stop_on_hit: bool = True, watch: Optional[Dict[str, str]] = None, log_descriptor: Optional[str] = None,
                 store_rng: bool = False, keep_log: bool = False, max_fill: int = 3, max_size: int = 16,
                 starts: Optional[Sequence[str]] = None, credit: str = "exact"):
        self.view, self.cert, self.E, self.lib = view, certifier, E, E.lib
        self.arm, self.spec = arm, SPECS[arm]
        self.T = view.output_type
        self.seed, self.budget = seed, budget
        self.L = budget + 1 if self.spec.get("single_burst") else burst
        self.desc = DS.get(descriptor) if (self.spec["descriptor"] and descriptor) else None
        if self.spec["descriptor"] and self.desc is None:
            raise ValueError("arm %s needs a descriptor" % arm)
        self.logdesc = DS.get(log_descriptor) if log_descriptor else None
        self.stop_on_hit, self.watch, self.store_rng, self.keep_log = stop_on_hit, watch, store_rng, keep_log
        self.mut = Mutator(E, max_fill=max_fill, max_size=max_size)
        if credit not in K.CREDITS:
            raise ValueError("credit channel %r" % credit)
        self.credit = credit
        self.rng = rng_for(seed, view.family_id)                 # CRN: identical stream start in every arm
        self.n_dev = len(view.dev)
        # state
        self.charges = self.restores = self.rejected = self.verify_evals = 0
        self.units_dev = [0, 0]
        self.units_probe = [0, 0]
        self.probe_runs = 0
        self.entries: List[Dict] = []
        self.by_cell: Dict = {}
        self.cell_order: List = []
        self.chosen: Counter = Counter()
        self.genos = set()
        self.replacements = 0
        self.hits: List[Dict] = []
        self.false_hits: List[Dict] = []
        self.mechanisms: Dict[str, int] = {}
        self.genotypes_q: Dict[str, int] = {}
        self.cert_patterns: Dict[str, int] = {}
        self.first_visit: Dict[str, int] = {}
        self.logcells = set()
        self.loghash = hashlib.sha256()
        self.log: List = []
        self.cur = None
        self.anchor = None
        self.burst_left = 0
        self.burst_idx = -1
        self.done = False
        self.starts = []
        for s in (starts or K.STARTS[self.T]):
            t = C.parse(s)
            rec = self._evaluate(t)
            self.starts.append({"id": "S%d" % len(self.starts), "term": t, "text": rec["text"],
                                "score": rec["score"], "partial": rec["partial"], "cell": rec["cell"],
                                "key": rec["key"]})
            self._post_eval(t, rec, None)
        if self.spec["admission"] != "none":
            for s in self.starts:                                 # starts seed the archive
                self._admit_entry(s["term"], {"text": s["text"], "score": s["score"], "partial": s["partial"],
                                              "cell": s["cell"], "key": s["key"]}, None, force=True)

    # ------------------------------------------------------------ evaluation (1 charge)
    def _evaluate(self, t) -> Dict:
        fn = C.compile_term(t, self.lib, None, swap=self.lib is not None)
        C.U[0] = C.U[1] = 0
        outs = [C.run(fn, i) for i in self.view.dev_inputs]
        self.units_dev[0] += C.U[0]
        self.units_dev[1] += C.U[1]
        probes = None
        if (self.desc is not None and self.desc.needs_probes) or (self.logdesc is not None and
                                                                  self.logdesc.needs_probes):
            C.U[0] = C.U[1] = 0
            probes = [C.run(fn, i) for i in self.view.probes]
            self.units_probe[0] += C.U[0]
            self.units_probe[1] += C.U[1]
            self.probe_runs += len(self.view.probes)
        self.charges += 1
        text = C.to_str(t)
        rec = {"text": text, "outs": outs, "probes": probes, "score": K.exact_credit(outs, self.view.targets),
               "partial": round(K.partial_credit(outs, self.view.targets), 6),
               "allfail": all(v == C.FAIL for v in outs)}
        rec["key"] = rec["score"] if self.credit == "exact" else K.CREDITS[self.credit](outs, self.view.targets)
        rec["cell"] = self.desc.cell(text, outs, probes, self.view) if self.desc is not None else None
        return rec

    def _post_eval(self, t, rec, anchor_entry):
        """Certifier consult (only for dev-consistent programs) + reporting-only bookkeeping."""
        if rec["score"] > 0:
            pat = "".join("1" if C.same_value(v, o) else "0" for v, o in zip(rec["outs"], self.view.targets))
            self.cert_patterns.setdefault(pat, self.charges)
        if self.logdesc is not None:
            self.logcells.add(self.logdesc.cell(rec["text"], rec["outs"], rec["probes"], self.view))
        if self.watch is not None:
            ck = C.to_str(canon_comm(t))
            if ck in self.watch and ck not in self.first_visit:
                self.first_visit[ck] = self.charges
        if rec["score"] == self.n_dev and self.cert is not None:
            self.verify_evals += 1
            u = (C.U[0], C.U[1])
            q = self.cert.verify(t)
            C.U[0], C.U[1] = u
            if anchor_entry is not None:
                anchor_entry["dev_consistent_desc"] += 1
                anchor_entry["qualified_desc"] += int(q)
            row = {"charge": self.charges, "program": rec["text"]}
            if q:
                self.hits.append(row)
                sk = skeleton(t, self.lib)
                self.mechanisms.setdefault(sk, self.charges)
                self.genotypes_q.setdefault(C.to_str(canon_comm(t)), self.charges)
                if self.stop_on_hit:
                    self.done = True
            else:
                self.false_hits.append(row)

    # ------------------------------------------------------------ archive
    def _rng_record(self) -> Dict:
        st = self.rng.getstate()
        d = {"rng_sha256": hashlib.sha256(repr(st).encode()).hexdigest()[:16]}
        if self.store_rng:
            d["rng_state"] = st
        return d

    def _new_entry(self, t, rec, parent_id):
        e = {"id": "E%d" % len(self.entries), "term": t, "text": rec["text"], "cell": rec["cell"],
             "score": rec["score"], "partial": rec["partial"], "key": rec["key"], "acquired_charge": self.charges,
             "parent": parent_id,
             "burst": self.burst_idx, "step_in_burst": (self.L - self.burst_left) if self.burst_idx >= 0 else 0,
             "children": 0, "admitted_children": 0, "best_child_score": None, "dev_consistent_desc": 0,
             "qualified_desc": 0, "times_restored": 0, **self._rng_record()}
        self.entries.append(e)
        self.genos.add(rec["text"])
        return e

    def _admit_entry(self, t, rec, parent_id, force=False) -> Optional[Dict]:
        adm = self.spec["admission"]
        if adm == "none":
            return None
        if adm == "nondecreasing":
            if rec["text"] in self.genos:
                return None
            e = self._new_entry(t, rec, parent_id)
            c = rec["cell"]
            if c not in self.by_cell:
                self.by_cell[c] = []
                self.cell_order.append(c)
            self.by_cell[c].append(len(self.entries) - 1)
            return e
        # cell admission (one elite per cell)
        c = rec["cell"]
        if c not in self.by_cell:
            e = self._new_entry(t, rec, parent_id)
            self.by_cell[c] = len(self.entries) - 1
            self.cell_order.append(c)
            return e
        inc = self.entries[self.by_cell[c]]
        if rec["key"] > inc["key"] and rec["text"] not in self.genos:
            e = self._new_entry(t, rec, parent_id)
            self.by_cell[c] = len(self.entries) - 1
            self.replacements += 1
            return e
        return None

    def live_entries(self) -> List[int]:
        if self.spec["admission"] == "cell":
            return [self.by_cell[c] for c in self.cell_order]
        return list(range(len(self.entries)))

    def lineage(self, entry_id: str) -> List[str]:
        idx = {e["id"]: e for e in self.entries}
        out, cur = [], idx.get(entry_id)
        while cur is not None:
            out.append(cur["id"])
            cur = idx.get(cur["parent"]) if cur["parent"] else None
        return out[::-1]

    # ------------------------------------------------------------ restore
    def _restore(self):
        self.restores += 1
        self.burst_idx += 1
        self.burst_left = self.L
        sel = self.spec["selection"]
        if sel == "start":
            s = self.starts[self.rng.randrange(len(self.starts))]
            self.cur = (s["term"], s["key"])
            self.anchor = None
            return
        live = self.live_entries()
        if sel == "uniform":
            e = self.entries[live[self.rng.randrange(len(live))]]
        else:                                                     # cell_count
            cells = self.cell_order
            w = [1.0 / math.sqrt(1 + self.chosen[c]) for c in cells]
            c = self.rng.choices(cells, weights=w)[0]
            self.chosen[c] += 1
            members = self.by_cell[c]
            e = self.entries[members[self.rng.randrange(len(members))]]
        e["times_restored"] += 1
        self.cur = (e["term"], e["key"])
        self.anchor = e

    # ------------------------------------------------------------ step
    def step(self):
        if self.burst_left <= 0:
            self._restore()
        child = self.mut.mutate(self.cur[0], self.T, self.rng)
        if child is None:                      # not evaluated, not charged, does not consume a burst slot
            self.rejected += 1
            if self.rejected > 100 * (self.budget + 1):
                self.done = True
            return
        self.burst_left -= 1
        rec = self._evaluate(child)
        anchor = self.anchor
        if anchor is not None:
            anchor["children"] += 1
        self._post_eval(child, rec, anchor)
        admitted = None
        ok_move = (not rec["allfail"]) and rec["key"] >= self.cur[1]
        if not rec["allfail"]:
            if self.spec["admission"] == "nondecreasing":
                if ok_move:
                    admitted = self._admit_entry(child, rec, anchor["id"] if anchor else None)
            elif self.spec["admission"] == "cell":
                admitted = self._admit_entry(child, rec, anchor["id"] if anchor else None)
        if admitted is not None and anchor is not None:
            anchor["admitted_children"] += 1
        if anchor is not None:
            b = anchor["best_child_score"]
            anchor["best_child_score"] = rec["score"] if b is None else max(b, rec["score"])
        if ok_move:
            self.cur = (child, rec["key"])
            if admitted is not None:
                self.anchor = admitted
        line = "%d|%s|%d|%s|%s|%d" % (self.charges, rec["text"], rec["score"],
                                       admitted["id"] if admitted else "-", anchor["id"] if anchor else "-",
                                       self.restores)
        self.loghash.update(line.encode())
        if self.keep_log:
            self.log.append(line)
        if self.charges >= self.budget:
            self.done = True

    def run(self) -> Dict:
        while not self.done:
            self.step()
        return self.result()

    # ------------------------------------------------------------ snapshot (STATE restore of the search process)
    def snapshot(self) -> Dict:
        """Full SEARCH-PROCESS state (archive, chain position, counters, RNG state, log hash). One deepcopy call, so
        aliasing (the anchor entry IS an archive entry) is preserved."""
        keep = ("view", "cert", "E", "lib", "mut", "desc", "logdesc", "watch", "spec", "loghash", "rng")
        snap = copy.deepcopy({k: v for k, v in self.__dict__.items() if k not in keep})
        snap["_rng"] = self.rng.getstate()
        snap["_loghash"] = self.loghash.copy()
        return snap

    def restore_state(self, snap: Dict):
        body = copy.deepcopy({k: v for k, v in snap.items() if k not in ("_rng", "_loghash")})
        for k, v in body.items():
            setattr(self, k, v)
        self.rng.setstate(snap["_rng"])
        self.loghash = snap["_loghash"].copy()

    # ------------------------------------------------------------ result
    def realised_cells(self) -> Optional[int]:
        if self.spec["admission"] == "none":
            return None
        if self.spec["descriptor"]:
            return len(self.cell_order)
        return None

    def result(self) -> Dict:
        hit = self.hits[0] if self.hits else None
        return {
            "arm": self.arm, "seed": self.seed, "budget": self.budget, "burst_L": self.L, "credit": self.credit,
            "descriptor": self.desc.name if self.desc else None,
            "hit": hit is not None, "hit_charge": hit["charge"] if hit else None,
            "program": hit["program"] if hit else None, "censored": hit is None,
            "first_false_hits": self.false_hits[:5], "n_false_hits": len(self.false_hits),
            "decision_log_sha256": self.loghash.hexdigest(),
            "first_visit_route": dict(self.first_visit) if self.watch is not None else None,
            "mechanisms": {"qualified_skeletons": dict(self.mechanisms),
                           "qualified_genotypes": len(self.genotypes_q),
                           "cert_patterns_seen": len(self.cert_patterns),
                           "cert_patterns_first_charge": dict(sorted(self.cert_patterns.items())[:64])},
            "archive": {"entries": len(self.entries), "live_entries": len(self.live_entries()),
                        "realised_cells": self.realised_cells(), "replacements": self.replacements,
                        "logged_descriptor_cells_visited": len(self.logcells) if self.logdesc else None},
            "ledger": {
                "organism": {"program": hit["program"] if hit else None},
                "developmental": {"library_entries": len(self.lib) if self.lib else 0,
                                  "library_sha256": self.lib.sha256()[:16] if self.lib else None,
                                  "library_max_depth": self.lib.max_depth() if self.lib else 0},
                "search": {"charges": self.charges, "units_dev_expanded": self.units_dev[0],
                           "units_dev_promoted": self.units_dev[1], "probe_runs": self.probe_runs,
                           "units_probe_expanded": self.units_probe[0], "genotype_restores": self.restores,
                           "state_restores": 0, "rejected_mutations": self.rejected,
                           "archive_admissions": len(self.entries)},
                "certifier": {"verify_evals": self.verify_evals},
            },
        }


def run_arm(task: Dict, lib, arm: str, seed, budget: int, descriptor: Optional[str] = None, burst: int = DEFAULT_BURST,
            stop_on_hit: bool = True, witness: Optional[str] = None, watch=None, E: Optional[Enumerator] = None,
            log_descriptor: Optional[str] = None, final_eval: bool = True, **kw) -> Dict:
    view = K.LearnerView(task)
    cert = K.Certifier(task, lib, witness)
    E = E or Enumerator(lib)
    s = Search(view, cert, E, arm, seed, budget, burst, descriptor, stop_on_hit, watch, log_descriptor, **kw)
    r = s.run()
    if final_eval and r["program"]:
        fe = K.final_evaluation(r["program"], task, lib, witness)
        r["final_evaluation"] = fe
        r["archive_assisted_discovery"] = True
        r["autonomous_competence"] = fe["autonomous_pass"]
    else:
        r["archive_assisted_discovery"] = r["hit"]
        r["autonomous_competence"] = None if not r["hit"] else False
    r["ledger"]["certifier"]["final_eval_runs"] = 1 if r.get("final_evaluation") else 0
    return r


def calibrate_random_k(task: Dict, lib, ref_arm: str, descriptor: str, budget: int, seeds: Sequence,
                       burst: int = DEFAULT_BURST, E: Optional[Enumerator] = None) -> Dict:
    """OUTCOME-BLIND calibration of the random control's bucket count K: run the reference descriptor arm with
    stop_on_hit=False on CALIBRATION seeds (disjoint from evaluation seeds) and read only its realised cell count;
    then check the random arm's realised cells at that K and adjust once by the observed ratio."""
    E = E or Enumerator(lib)
    view = K.LearnerView(task)
    ref = []
    for sd in seeds:
        s = Search(view, None, E, ref_arm, sd, budget, burst, descriptor, stop_on_hit=False)
        s.run()
        ref.append(s.realised_cells())
    target = sum(ref) / len(ref)
    rand_arm = {"B3-CELLADMIT": "C3-RAND", "B2-DESCSEL": "C2-RAND"}[ref_arm]
    k = max(1, round(target))
    hist = []
    for _it in range(3):
        got = []
        for sd in seeds:
            s = Search(view, None, E, rand_arm, sd, budget, burst, "RAND:%d" % k, stop_on_hit=False)
            s.run()
            got.append(s.realised_cells())
        mean = sum(got) / len(got)
        hist.append({"K": k, "realised_mean": mean})
        if abs(mean - target) <= 0.05 * target or mean == 0:
            break
        k = max(1, round(k * target / mean))
    return {"ref_arm": ref_arm, "descriptor": descriptor, "calibration_seeds": list(seeds), "budget": budget,
            "ref_realised_cells": ref, "target_mean": target, "iterations": hist, "K": hist[-1]["K"],
            "matched_within_5pct": abs(hist[-1]["realised_mean"] - target) <= 0.05 * target,
            "outcome_blind": "stop_on_hit=False and no certifier: only cell counts are read"}
