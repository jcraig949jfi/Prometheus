"""The producer: which experiment to run next, decided mechanically.

WHAT IT MAY DO. Assemble cells from the frozen grammar, and only from it. Every cell it
emits is grammar.repair()ed and grammar.is_valid()ated, so the producer cannot widen the
space it was given - it can only choose where in that space to spend.

HOW IT CHOOSES. Three mechanisms, all arithmetic:

  COVERAGE    counts of every factor level, every pair of levels and every triple the
              campaign has already run. Uncovered combinations score higher. This is what
              stops the campaign from varying a numeric knob inside one familiar cell
              while structural combinations go untouched.
  INTEREST    an upper-confidence bound per factor level and per pair, updated from the
              scalar interest the scheduler computes from each finished run. Levels that
              have produced replication, crossings or novel architecture get sampled more;
              levels with few observations keep an optimism bonus so they are not written
              off after one noisy run.
  FLOOR       a fixed fraction of every batch is drawn uniformly at random from the
              grammar regardless of interest. The exploration floor holds for the whole
              campaign, so an early noisy winner cannot monopolise the budget.

THE DIRECTIVE'S PREFERENCE, MADE ARITHMETIC. Atlas axes are worth more when crossed with
endogenous reproduction and with the accessibility manipulations than when run alone, so
a cell carrying an Atlas axis gets a bonus only if it also carries an endogenous
reproduction physics or a non-default accessibility setting. That is a scoring rule, not
a new experiment semantics.

MATCHED CONTROLS ARE NOT OPTIONAL. propose() returns (cell, control_axis) pairs, and the
scheduler is what turns them into two jobs. A cell whose control partner does not exist
in the grammar is emitted with control_axis None and recorded that way, so a missing
control is always visible as a missing control.
"""
from __future__ import annotations

import itertools
import math
import random

import grammar as G

# factors whose interaction the campaign most wants covered
PRIORITY_PAIRS = [
    ("reproduction", "task_transform"), ("reproduction", "read_order"),
    ("reproduction", "structure"), ("reproduction", "representation"),
    ("reproduction", "pressure"), ("structure", "task_transform"),
    ("pressure", "read_order"), ("copy_primitive", "self_location"),
    ("mutation_locality", "representation"), ("environment", "reproduction"),
    ("atlas_axis", "reproduction"), ("seeding", "reproduction"),
    ("task_transform", "mutation_operator"), ("bridge", "read_order"),
]
PRIORITY_TRIPLES = [
    ("reproduction", "task_transform", "read_order"),
    ("reproduction", "structure", "task_transform"),
    ("reproduction", "copy_primitive", "self_location"),
    ("representation", "mutation_locality", "task_transform"),
    ("environment", "reproduction", "structure"),
]
CONTROL_PREFERENCE = ("reproduction", "pressure", "read_order", "structure",
                      "environment", "copy_primitive", "self_location", "mutation_locality")


class Producer:
    def __init__(self, seed=0, explore_floor=0.30, candidates=48):
        self.rng = random.Random(seed ^ 0x5A5A5A5)
        self.explore_floor = explore_floor
        self.candidates = candidates
        self.n_runs = 0
        self.level_n = {}          # (factor, level) -> count
        self.level_s = {}          # (factor, level) -> summed interest
        self.pair_n = {}           # (f1, l1, f2, l2) -> count
        self.pair_s = {}
        self.triple_n = {}
        self.emitted = {}          # cell_id -> times proposed

    # ------------------------------------------------------------------ feedback
    def observe(self, cell, interest):
        self.n_runs += 1
        for f, l in cell.items():
            k = (f, l)
            self.level_n[k] = self.level_n.get(k, 0) + 1
            self.level_s[k] = self.level_s.get(k, 0.0) + interest
        for f1, f2 in PRIORITY_PAIRS:
            k = (f1, cell[f1], f2, cell[f2])
            self.pair_n[k] = self.pair_n.get(k, 0) + 1
            self.pair_s[k] = self.pair_s.get(k, 0.0) + interest
        for f1, f2, f3 in PRIORITY_TRIPLES:
            k = (f1, cell[f1], f2, cell[f2], f3, cell[f3])
            self.triple_n[k] = self.triple_n.get(k, 0) + 1

    # ------------------------------------------------------------------ scoring
    def _ucb(self, n, s):
        if n == 0:
            return 1.0                                   # unseen: maximum optimism
        return s / n + 1.2 * math.sqrt(math.log(max(self.n_runs, 2)) / n)

    def score(self, cell, stage):
        d = G.derived(cell)
        cov = 0.0
        for f1, f2 in PRIORITY_PAIRS:
            n = self.pair_n.get((f1, cell[f1], f2, cell[f2]), 0)
            cov += 1.0 / (1.0 + n)
        for f1, f2, f3 in PRIORITY_TRIPLES:
            n = self.triple_n.get((f1, cell[f1], f2, cell[f2], f3, cell[f3]), 0)
            cov += 1.5 / (1.0 + n)
        cov /= (len(PRIORITY_PAIRS) + 1.5 * len(PRIORITY_TRIPLES))

        interest = 0.0
        for f, l in cell.items():
            interest += self._ucb(self.level_n.get((f, l), 0), self.level_s.get((f, l), 0.0))
        interest /= len(cell)
        for f1, f2 in PRIORITY_PAIRS:
            k = (f1, cell[f1], f2, cell[f2])
            interest += 0.15 * self._ucb(self.pair_n.get(k, 0), self.pair_s.get(k, 0.0))
        interest /= (1.0 + 0.15 * len(PRIORITY_PAIRS))

        # the directive's preferred collisions, as arithmetic
        bonus = 0.0
        if cell["atlas_axis"] != "NONE" and (d["endogenous"] or d["moat"] or
                                             d["constant_kind"] == "ATOMIC"):
            bonus += 0.25
        if d["endogenous"] and d["has_task"]:
            bonus += 0.10
        if d["endogenous"] and cell["structure"] in ("RESERVOIR", "NICHES_LOW_MIG",
                                                     "COMPETENCE_MIG", "NICHES_PERIODIC_MIG"):
            bonus += 0.10
        if d["spontaneity_test"]:
            bonus += 0.12
        if cell["atlas_axis"] != "NONE" and not (d["endogenous"] or d["has_task"]):
            bonus -= 0.15                    # an Atlas axis alone is a replication, not a crossing
        seen = self.emitted.get(G.cell_id(cell), 0)
        repeat = -0.30 * seen

        w_cov = {"EARLY": 0.62, "MIDDLE": 0.35, "LATE": 0.25}[stage]
        return w_cov * cov + (1 - w_cov) * interest + bonus + repeat

    # ------------------------------------------------------------------ proposal
    def _draw(self, fixed=None):
        for _ in range(8):
            c = G.sample_cell(self.rng, fixed=fixed)
            if c and G.is_valid(c):
                return c
        return None

    def propose(self, n, stage="EARLY", tier="S"):
        """n jobs as dicts {cell, control_axis, reason}."""
        out = []
        n_floor = max(1, int(round(self.explore_floor * n)))
        for i in range(n):
            floor = i < n_floor
            if floor:
                cell = self._draw()
                reason = "exploration_floor"
                score = None
            else:
                cands = [self._draw() for _ in range(self.candidates)]
                cands = [c for c in cands if c]
                if not cands:
                    continue
                scored = [(self.score(c, stage), c) for c in cands]
                scored.sort(key=lambda x: -x[0])
                score, cell = scored[0]
                reason = "coverage_and_interest"
            if cell is None:
                continue
            cell = dict(cell)
            self.emitted[G.cell_id(cell)] = self.emitted.get(G.cell_id(cell), 0) + 1
            out.append({"cell": cell, "control_axis": self._control_axis(cell),
                        "reason": reason, "score": None if score is None else round(score, 4),
                        "stage": stage})
        return out

    def _control_axis(self, cell):
        """The axis whose matched control this cell most needs, or None if the grammar
        offers no valid partner - recorded either way."""
        for ax in CONTROL_PREFERENCE:
            if G.control_partner(cell, ax) is not None:
                return ax
        return None

    def coverage_report(self):
        pairs_total = sum(len(G.FACTORS[a]) * len(G.FACTORS[b]) for a, b in PRIORITY_PAIRS)
        pairs_seen = len(self.pair_n)
        lv_total = sum(len(v) for v in G.FACTORS.values())
        return {"runs_observed": self.n_runs, "levels_seen": len(self.level_n), "levels_total": lv_total,
                "priority_pairs_seen": pairs_seen, "priority_pairs_total": pairs_total,
                "priority_pairs_share": round(pairs_seen / max(1, pairs_total), 4),
                "triples_seen": len(self.triple_n),
                "distinct_cells_emitted": len(self.emitted),
                "top_levels_by_interest": sorted(
                    [{"factor": f, "level": l, "n": self.level_n[(f, l)],
                      "mean_interest": round(self.level_s[(f, l)] / self.level_n[(f, l)], 4)}
                     for (f, l) in self.level_n if self.level_n[(f, l)] >= 3],
                    key=lambda d: -d["mean_interest"])[:20]}

    def uncovered_pairs(self, limit=40):
        out = []
        for a, b in PRIORITY_PAIRS:
            for la, lb in itertools.product(sorted(G.FACTORS[a]), sorted(G.FACTORS[b])):
                if (a, la, b, lb) not in self.pair_n:
                    out.append({"f1": a, "l1": la, "f2": b, "l2": lb})
                    if len(out) >= limit:
                        return out
        return out

    def state(self):
        return {"n_runs": self.n_runs,
                "level_n": {"%s|%s" % k: v for k, v in self.level_n.items()},
                "level_s": {"%s|%s" % k: round(v, 5) for k, v in self.level_s.items()},
                "pair_n": {"%s|%s|%s|%s" % k: v for k, v in self.pair_n.items()},
                "pair_s": {"%s|%s|%s|%s" % k: round(v, 5) for k, v in self.pair_s.items()},
                "triple_n": {"|".join(k): v for k, v in self.triple_n.items()},
                "emitted": dict(self.emitted)}

    def load(self, st):
        self.n_runs = st.get("n_runs", 0)
        self.level_n = {tuple(k.split("|")): v for k, v in st.get("level_n", {}).items()}
        self.level_s = {tuple(k.split("|")): v for k, v in st.get("level_s", {}).items()}
        self.pair_n = {tuple(k.split("|")): v for k, v in st.get("pair_n", {}).items()}
        self.pair_s = {tuple(k.split("|")): v for k, v in st.get("pair_s", {}).items()}
        self.triple_n = {tuple(k.split("|")): v for k, v in st.get("triple_n", {}).items()}
        self.emitted = dict(st.get("emitted", {}))
