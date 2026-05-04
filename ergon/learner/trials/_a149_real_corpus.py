"""ergon.learner.trials._a149_real_corpus — real a149_obstruction corpus loader.

Per Iter 28 / Task #92. Loads the actual A149* (and broader OEIS lattice-walk)
corpus from cartography/convergence/data/asymptotic_deviations.jsonl + the
kill verdicts from battery_sweep_v2.jsonl, and produces a list of
CorpusEntry-shaped objects that Ergon's predicate-discovery pipeline can
consume.

Frontier verdict on Iter 28: run Ergon against the REAL corpus, not synthetic.
Goal: see if Ergon generates a predicate explaining a cluster of "Shadow
Catalog" entries that human pattern-mining missed.

Corpus shape: ~1,457 records (all parseable lattice-walk step sets from
asymptotic_deviations). kill_verdict=True iff ANY battery-sweep test fired
(partial or unanimous). Baseline kill rate ~6.7% — comparable to synthetic
OBSTRUCTION's 8%.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


REPO = Path(__file__).parents[3]
ASYMPTOTIC = REPO / "cartography" / "convergence" / "data" / "asymptotic_deviations.jsonl"
BATTERY_SWEEP = REPO / "cartography" / "convergence" / "data" / "battery_sweep_v2.jsonl"

STEP_SET_RE = re.compile(r"\{([^}]+)\}")
STEP_RE = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")

# Charon's unanimous battery
UNANIMOUS_BATTERY = {
    "F1_permutation_null",
    "F6_base_rate",
    "F9_simpler_explanation",
    "F11_cross_validation",
}


@dataclass(frozen=True)
class A149CorpusEntry:
    """A real A149* / lattice-walk record with structural features.

    Mirrors the synthetic CorpusEntry shape (features() + kill_verdict)
    so the existing predicate-discovery pipeline can consume it
    unchanged.
    """
    seq_id: str
    n_steps: int
    neg_x: int
    pos_x: int
    neg_y: int
    pos_y: int
    neg_z: int
    pos_z: int
    has_diag_neg: bool
    has_diag_pos: bool
    n_axis_aligned: int
    kill_verdict: bool          # True if ANY battery test fired
    n_kill_tests_fired: int     # how many of the 4+ tests fired
    is_unanimous_kill: bool     # all UNANIMOUS_BATTERY tests fired
    delta_pct: float            # asymptotic deviation magnitude

    def features(self) -> Dict[str, Any]:
        return {
            "n_steps": self.n_steps,
            "neg_x": self.neg_x,
            "pos_x": self.pos_x,
            "neg_y": self.neg_y,
            "pos_y": self.pos_y,
            "neg_z": self.neg_z,
            "pos_z": self.pos_z,
            "has_diag_neg": self.has_diag_neg,
            "has_diag_pos": self.has_diag_pos,
            "n_axis_aligned": self.n_axis_aligned,
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _parse_step_set(name: str) -> Optional[List[tuple]]:
    m = STEP_SET_RE.search(name)
    if not m:
        return None
    body = m.group(1)
    steps = STEP_RE.findall(body)
    if not steps:
        return None
    return [tuple(int(x) for x in s) for s in steps]


def _features_from_steps(steps: List[tuple]) -> Dict[str, Any]:
    n = len(steps)
    nx = sum(1 for s in steps if s[0] < 0)
    ny = sum(1 for s in steps if s[1] < 0)
    nz = sum(1 for s in steps if s[2] < 0)
    px = sum(1 for s in steps if s[0] > 0)
    py = sum(1 for s in steps if s[1] > 0)
    pz = sum(1 for s in steps if s[2] > 0)
    has_diag_neg = any(s == (-1, -1, -1) for s in steps)
    has_diag_pos = any(s == (1, 1, 1) for s in steps)
    n_axis_aligned = sum(1 for s in steps if sum(abs(c) for c in s) == 1)
    return {
        "n_steps": n, "neg_x": nx, "neg_y": ny, "neg_z": nz,
        "pos_x": px, "pos_y": py, "pos_z": pz,
        "has_diag_neg": has_diag_neg, "has_diag_pos": has_diag_pos,
        "n_axis_aligned": n_axis_aligned,
    }


def load_a149_real_corpus(
    a149_only: bool = False, include_no_kill: bool = True
) -> List[A149CorpusEntry]:
    """Load the real A149*+ corpus from cartography data files.

    a149_only=True restricts to A149xxx sequences (~500 records).
    a149_only=False (default) includes all parseable lattice-walks (~1,457).
    include_no_kill=False filters to records with at least one kill test fired.
    """
    if not ASYMPTOTIC.exists():
        raise FileNotFoundError(f"Missing: {ASYMPTOTIC}")
    if not BATTERY_SWEEP.exists():
        raise FileNotFoundError(f"Missing: {BATTERY_SWEEP}")

    all_records = []
    with ASYMPTOTIC.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    all_records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    kills: Dict[str, Set[str]] = defaultdict(set)
    with BATTERY_SWEEP.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    sid = r.get("seq_id")
                    if sid:
                        kills[sid].update(r.get("kill_tests", []) or [])
                except json.JSONDecodeError:
                    continue

    out: List[A149CorpusEntry] = []
    for r in all_records:
        sid = r.get("seq_id", "")
        if a149_only and not sid.startswith("A149"):
            continue
        steps = _parse_step_set(r.get("name", ""))
        if not steps:
            continue
        feats = _features_from_steps(steps)
        kill_set = kills.get(sid, set())
        n_kill = len(kill_set)
        if not include_no_kill and n_kill == 0:
            continue
        out.append(A149CorpusEntry(
            seq_id=sid,
            n_steps=feats["n_steps"],
            neg_x=feats["neg_x"], pos_x=feats["pos_x"],
            neg_y=feats["neg_y"], pos_y=feats["pos_y"],
            neg_z=feats["neg_z"], pos_z=feats["pos_z"],
            has_diag_neg=feats["has_diag_neg"],
            has_diag_pos=feats["has_diag_pos"],
            n_axis_aligned=feats["n_axis_aligned"],
            kill_verdict=(n_kill > 0),
            n_kill_tests_fired=n_kill,
            is_unanimous_kill=UNANIMOUS_BATTERY.issubset(kill_set),
            delta_pct=float(r.get("delta_pct", 0.0)),
        ))
    return out


def corpus_summary(corpus: List[A149CorpusEntry]) -> Dict[str, Any]:
    n = len(corpus)
    n_kill = sum(1 for e in corpus if e.kill_verdict)
    n_unanimous = sum(1 for e in corpus if e.is_unanimous_kill)
    n_partial = sum(1 for e in corpus if e.kill_verdict and not e.is_unanimous_kill)
    n_a149 = sum(1 for e in corpus if e.seq_id.startswith("A149"))
    n_steps_dist: Dict[int, int] = defaultdict(int)
    for e in corpus:
        n_steps_dist[e.n_steps] += 1
    return {
        "n_total": n,
        "n_kill_any": n_kill,
        "n_unanimous_kill": n_unanimous,
        "n_partial_kill": n_partial,
        "n_no_kill": n - n_kill,
        "baseline_kill_rate": n_kill / n if n else 0.0,
        "n_a149_records": n_a149,
        "n_steps_distribution": dict(n_steps_dist),
    }


__all__ = [
    "A149CorpusEntry",
    "load_a149_real_corpus",
    "corpus_summary",
    "UNANIMOUS_BATTERY",
]
