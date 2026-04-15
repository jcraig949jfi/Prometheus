#!/usr/bin/env python3
"""
Shadow Archive — The negative space map.

Every failure is data. The shadow archive accumulates kill patterns across
the hypothesis space, tracking:

  - Which (domain, feature, coupling) regions have been explored
  - How deep each region got before dying
  - What killed it (dominant kill mode)
  - How many times we've tested it (confidence)
  - Z-scores at death (gradient information)

The shadow tensor is indexed by:
  (domain_a, domain_b, feature_a, feature_b, coupling) -> FailureProfile

This tells the explorer:
  - Confirmed dead zones (tested 50x, always F1) -> stop wasting time
  - Gradient zones (dies at depth 10-12, varies by coupling) -> promising
  - Unexplored zones (never tested) -> go here
  - Kill-mode clusters (everything in this region dies at F24) -> structural insight
"""
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict


@dataclass
class FailureProfile:
    """Accumulated failure statistics for one hypothesis-space cell."""
    n_tested: int = 0
    n_survived: int = 0           # made it past all tests
    best_depth: int = 0
    worst_depth: int = 999
    total_depth: int = 0          # for computing mean
    best_z: float = 0.0
    depths: list = field(default_factory=list)     # last N depths for variance
    kill_counts: dict = field(default_factory=dict)  # kill_test -> count
    z_scores: list = field(default_factory=list)     # last N z-scores

    MAX_HISTORY = 50  # keep last N for variance computation

    @property
    def mean_depth(self):
        return self.total_depth / self.n_tested if self.n_tested > 0 else 0

    @property
    def depth_variance(self):
        if len(self.depths) < 2:
            return 0.0
        return float(np.var(self.depths))

    @property
    def survival_rate(self):
        return self.n_survived / self.n_tested if self.n_tested > 0 else 0

    @property
    def dominant_kill(self):
        if not self.kill_counts:
            return ""
        return max(self.kill_counts, key=self.kill_counts.get)

    @property
    def confidence(self):
        """How confident are we in this cell's verdict?
        0.0 = never tested, 1.0 = tested 50+ times with consistent results.
        """
        if self.n_tested == 0:
            return 0.0
        # Base confidence from sample size (saturates around 50)
        n_conf = min(self.n_tested / 50.0, 1.0)
        # Penalize high variance (inconsistent results = less confident)
        var_penalty = 1.0 / (1.0 + self.depth_variance)
        return n_conf * var_penalty

    @property
    def gradient_score(self):
        """How promising is this region for further exploration?
        High score = high depth variance + high best_depth + low test count.
        The boundary between dead and alive is where discoveries happen.
        """
        if self.n_tested == 0:
            return 0.0
        # Reward: high best depth (got close to surviving)
        depth_reward = self.best_depth / 16.0  # normalize to ~1.0
        # Reward: high depth variance (inconsistent = boundary region)
        var_reward = min(self.depth_variance / 10.0, 1.0)
        # Reward: low confidence (under-explored)
        explore_reward = 1.0 - self.confidence
        # Penalty: fully confirmed dead (tested 50x, always depth 0)
        if self.n_tested >= 20 and self.best_depth <= 1:
            return 0.0
        return depth_reward * 0.5 + var_reward * 0.3 + explore_reward * 0.2

    def to_dict(self):
        return {
            "n_tested": self.n_tested,
            "n_survived": self.n_survived,
            "best_depth": self.best_depth,
            "mean_depth": round(self.mean_depth, 2),
            "depth_variance": round(self.depth_variance, 2),
            "survival_rate": round(self.survival_rate, 4),
            "best_z": round(self.best_z, 2),
            "dominant_kill": self.dominant_kill,
            "confidence": round(self.confidence, 3),
            "gradient_score": round(self.gradient_score, 3),
            "kill_counts": self.kill_counts,
        }


class ShadowArchive:
    """The negative space map. Accumulates failure patterns across hypothesis space."""

    def __init__(self):
        # Primary index: (domain_a, domain_b) -> (feature_a, feature_b, coupling) -> FailureProfile
        self._cells = defaultdict(lambda: defaultdict(FailureProfile))
        # Marginal indices for fast lookup
        self._by_domain_pair = defaultdict(FailureProfile)
        self._by_feature = defaultdict(FailureProfile)
        self._by_kill = defaultdict(list)  # kill_test -> list of cell keys

    def _cell_key(self, hypothesis):
        """Canonical cell key: sorted domain pair + feature pair + coupling."""
        da, db = hypothesis.domain_a, hypothesis.domain_b
        fa, fb = hypothesis.feature_a, hypothesis.feature_b
        coupling = hypothesis.coupling
        return (da, db), (fa, fb, coupling)

    def record(self, hypothesis, result):
        """Record a hypothesis result (survived or killed) in the shadow archive."""
        (da, db), (fa, fb, coupling) = self._cell_key(hypothesis)
        depth = result.get("survival_depth", 0)
        z = result.get("z_score", 0.0)
        kill = result.get("kill_test", "")
        survived = result.get("status") == "survived"

        # Update primary cell
        cell = self._cells[(da, db)][(fa, fb, coupling)]
        cell.n_tested += 1
        if survived:
            cell.n_survived += 1
        cell.total_depth += depth
        cell.best_depth = max(cell.best_depth, depth)
        cell.worst_depth = min(cell.worst_depth, depth)
        if abs(z) > abs(cell.best_z):
            cell.best_z = z
        cell.depths.append(depth)
        if len(cell.depths) > FailureProfile.MAX_HISTORY:
            cell.depths.pop(0)
        cell.z_scores.append(z)
        if len(cell.z_scores) > FailureProfile.MAX_HISTORY:
            cell.z_scores.pop(0)
        if kill:
            cell.kill_counts[kill] = cell.kill_counts.get(kill, 0) + 1

        # Update domain pair marginal
        dp = self._by_domain_pair[(da, db)]
        dp.n_tested += 1
        if survived:
            dp.n_survived += 1
        dp.total_depth += depth
        dp.best_depth = max(dp.best_depth, depth)
        if abs(z) > abs(dp.best_z):
            dp.best_z = z
        if kill:
            dp.kill_counts[kill] = dp.kill_counts.get(kill, 0) + 1

        # Update feature marginal
        for feat in [fa, fb]:
            fp = self._by_feature[feat]
            fp.n_tested += 1
            if survived:
                fp.n_survived += 1
            fp.total_depth += depth
            fp.best_depth = max(fp.best_depth, depth)
            if kill:
                fp.kill_counts[kill] = fp.kill_counts.get(kill, 0) + 1

        # Track kill locations
        if kill:
            self._by_kill[kill].append(((da, db), (fa, fb, coupling)))

    def get_cell(self, domain_a, domain_b, feature_a, feature_b, coupling):
        """Get failure profile for a specific hypothesis-space cell."""
        return self._cells[(domain_a, domain_b)][(feature_a, feature_b, coupling)]

    def get_domain_pair(self, domain_a, domain_b):
        """Get aggregate failure profile for a domain pair."""
        return self._by_domain_pair[(domain_a, domain_b)]

    def get_dead_zones(self, min_tests=10, max_depth=1):
        """Return cells that are confirmed dead (tested enough, never got past depth 1)."""
        dead = []
        for (da, db), features in self._cells.items():
            for (fa, fb, coupling), cell in features.items():
                if cell.n_tested >= min_tests and cell.best_depth <= max_depth:
                    dead.append(((da, db, fa, fb, coupling), cell))
        dead.sort(key=lambda x: -x[1].n_tested)
        return dead

    def get_gradient_zones(self, min_score=0.3):
        """Return cells with high gradient scores (promising boundaries)."""
        gradients = []
        for (da, db), features in self._cells.items():
            for (fa, fb, coupling), cell in features.items():
                score = cell.gradient_score
                if score >= min_score:
                    gradients.append(((da, db, fa, fb, coupling), cell, score))
        gradients.sort(key=lambda x: -x[2])
        return gradients

    def get_unexplored(self, all_domains, all_features, all_couplings, max_tests=0):
        """Return (domain_pair, feature_pair) combos never or rarely tested."""
        explored = set()
        for (da, db), features in self._cells.items():
            for (fa, fb, coupling), cell in features.items():
                if cell.n_tested > max_tests:
                    explored.add((da, db, fa, fb, coupling))
        # This would be huge — just return the count
        return len(explored)

    def kill_heatmap(self):
        """Return kill mode counts by domain pair."""
        heatmap = {}
        for (da, db), profile in self._by_domain_pair.items():
            heatmap[f"{da} x {db}"] = {
                "tested": profile.n_tested,
                "best_depth": profile.best_depth,
                "mean_depth": round(profile.mean_depth, 1),
                "dominant_kill": profile.dominant_kill,
                "kills": profile.kill_counts,
            }
        return dict(sorted(heatmap.items(), key=lambda x: -x[1]["tested"]))

    def feature_heatmap(self):
        """Return kill mode counts by feature."""
        heatmap = {}
        for feat, profile in self._by_feature.items():
            if profile.n_tested > 0:
                heatmap[feat] = {
                    "tested": profile.n_tested,
                    "best_depth": profile.best_depth,
                    "mean_depth": round(profile.mean_depth, 1),
                    "dominant_kill": profile.dominant_kill,
                }
        return dict(sorted(heatmap.items(), key=lambda x: -x[1]["tested"]))

    def summary(self):
        """Summary statistics for the shadow archive."""
        total_cells = sum(len(features) for features in self._cells.values())
        total_tested = sum(
            cell.n_tested
            for features in self._cells.values()
            for cell in features.values()
        )
        dead_zones = self.get_dead_zones()
        gradient_zones = self.get_gradient_zones()

        return {
            "unique_cells_explored": total_cells,
            "total_tests_recorded": total_tested,
            "domain_pairs_explored": len(self._by_domain_pair),
            "features_explored": len(self._by_feature),
            "unique_kill_modes": len(self._by_kill),
            "confirmed_dead_zones": len(dead_zones),
            "gradient_zones": len(gradient_zones),
            "top_gradient_zones": [
                {"cell": key, "score": round(score, 3), "best_depth": cell.best_depth,
                 "n_tested": cell.n_tested, "depth_var": round(cell.depth_variance, 2)}
                for key, cell, score in gradient_zones[:5]
            ],
        }

    def save(self, path):
        """Save shadow archive to JSON."""
        data = {
            "summary": self.summary(),
            "domain_pair_heatmap": self.kill_heatmap(),
            "feature_heatmap": self.feature_heatmap(),
            "cells": {},
        }
        for (da, db), features in self._cells.items():
            pair_key = f"{da}|{db}"
            data["cells"][pair_key] = {}
            for (fa, fb, coupling), cell in features.items():
                feat_key = f"{fa}|{fb}|{coupling}"
                data["cells"][pair_key][feat_key] = cell.to_dict()

        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load(cls, path):
        """Load shadow archive from JSON."""
        sa = cls()
        with open(path) as f:
            data = json.load(f)
        for pair_key, features in data.get("cells", {}).items():
            da, db = pair_key.split("|", 1)
            for feat_key, cell_data in features.items():
                fa, fb, coupling = feat_key.split("|", 2)
                cell = sa._cells[(da, db)][(fa, fb, coupling)]
                cell.n_tested = cell_data["n_tested"]
                cell.n_survived = cell_data["n_survived"]
                cell.best_depth = cell_data["best_depth"]
                cell.total_depth = int(cell_data["mean_depth"] * cell_data["n_tested"])
                cell.best_z = cell_data["best_z"]
                cell.kill_counts = cell_data.get("kill_counts", {})
        return sa


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "forge/v3"))
    from gene_schema import Hypothesis

    sa = ShadowArchive()

    # Simulate some failures
    for i in range(30):
        h = Hypothesis(id=f"test_{i}", domain_a="elliptic_curves", domain_b="knots",
                       feature_a="conductor", feature_b="determinant", coupling="spearman")
        sa.record(h, {"survival_depth": 0, "z_score": 0.3, "kill_test": "F1_permutation_null"})

    for i in range(10):
        h = Hypothesis(id=f"test_deep_{i}", domain_a="elliptic_curves", domain_b="number_fields",
                       feature_a="rank", feature_b="class_number", coupling="spearman")
        depth = 8 + (i % 5)
        sa.record(h, {"survival_depth": depth, "z_score": 3.0 + i, "kill_test": "F24_variance_decomposition",
                       "status": "survived" if depth >= 12 else "killed"})

    print("Shadow Archive Summary:")
    summary = sa.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nDead zones:")
    for key, cell in sa.get_dead_zones()[:3]:
        print(f"  {key}: tested={cell.n_tested}, best_depth={cell.best_depth}, kill={cell.dominant_kill}")

    print("\nGradient zones:")
    for key, cell, score in sa.get_gradient_zones()[:3]:
        print(f"  {key}: score={score:.3f}, best_depth={cell.best_depth}, var={cell.depth_variance:.1f}")

    print("\nDomain pair heatmap:")
    for pair, stats in sa.kill_heatmap().items():
        print(f"  {pair}: {stats}")

    # Save/load test
    sa.save(Path(__file__).parent / "test_shadow.json")
    sa2 = ShadowArchive.load(Path(__file__).parent / "test_shadow.json")
    print(f"\nReload check: {sa2.summary()['unique_cells_explored']} cells")
