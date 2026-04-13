#!/usr/bin/env python3
"""
MAP-Elites Archive: Quality-diversity grid for hypothesis survival.

Grid axes:
  X: Domain category (math_arithmetic, math_algebraic, math_topological,
     math_analytic, physics, chemistry, biology, meta, cross_domain)
  Y: Measurement type (correlation, distribution, topology, spectral,
     information, algebraic)

Each cell stores the best-surviving hypothesis for that niche.
"""
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from gene_schema import Hypothesis

# Domain categories
DOMAIN_CATEGORIES = {
    "elliptic_curves": "math_arithmetic",
    "modular_forms": "math_analytic",
    "number_fields": "math_algebraic",
    "genus2_curves": "math_arithmetic",
    "maass_forms": "math_analytic",
    "knots": "math_topological",
    "lattices": "math_algebraic",
    "isogenies": "math_arithmetic",
    "oeis": "math_combinatorial",
    "polytopes": "math_topological",
    "space_groups": "math_algebraic",
    "fungrim": "meta",
    "findstat": "math_combinatorial",
    "metamath": "meta",
    "mathlib": "meta",
    "mmlkg": "meta",
    "dirichlet_zeros": "math_analytic",
    "ec_zeros": "math_analytic",
    "materials": "physics",
    "superconductors": "physics",
    "chemistry_qm9": "chemistry",
    "metabolism": "biology",
    "finance_ff": "finance",
    "source_code_scipy": "meta",
}

# Feature -> measurement type mapping
MEASUREMENT_TYPES = {
    "correlation": ["conductor", "log_conductor", "rank", "torsion", "class_number",
                     "regulator", "discriminant", "log_discriminant", "determinant",
                     "crossing_number", "n_atoms", "tc", "homo_lumo_gap"],
    "spectral": ["first_zero", "zero_spacing_1_2", "zero_spacing_2_3", "zero_density_tail",
                  "spectral_parameter", "nn_spacing_ratio"],
    "information": ["ap_compression_lz", "ap_compression_st", "coefficient_entropy",
                     "coefficient_autocorrelation", "ap_kurtosis"],
    "topology": ["congruence_degree_mod2", "congruence_degree_mod3", "congruence_degree_mod5",
                  "isogeny_class_size", "graph_diameter", "graph_clustering"],
    "algebraic": ["ap_mod2_fingerprint", "ap_mod3_fingerprint", "ap_mod5_fingerprint",
                   "n_bad_primes", "omega_conductor"],
    "distribution": ["ap_mean_abs", "n_symbols", "module_depth", "proof_length",
                      "import_degree", "f_vector_sum", "kissing_number"],
}

MEASUREMENT_CATEGORIES = list(MEASUREMENT_TYPES.keys())
DOMAIN_CATEGORY_LIST = sorted(set(DOMAIN_CATEGORIES.values()))


def _get_domain_category(domain):
    return DOMAIN_CATEGORIES.get(domain, "unknown")


def _get_measurement_type(feature):
    for mtype, features in MEASUREMENT_TYPES.items():
        if feature in features:
            return mtype
    return "correlation"  # default


def _cell_key(hypothesis):
    """Compute the (domain_category, measurement_type) cell for a hypothesis."""
    # Use the PAIR category
    cat_a = _get_domain_category(hypothesis.domain_a)
    cat_b = _get_domain_category(hypothesis.domain_b)
    domain_key = f"{min(cat_a, cat_b)}_{max(cat_a, cat_b)}"

    # Use the primary feature's measurement type
    mtype = _get_measurement_type(hypothesis.feature_a)

    return (domain_key, mtype)


class Archive:
    """MAP-Elites archive for hypothesis quality-diversity."""

    def __init__(self):
        self.grid = {}  # (domain_key, measurement_type) -> Hypothesis
        self.history = []  # all hypotheses ever tested
        self.generation = 0

    def update(self, hypothesis, result):
        """Try to place a hypothesis in the grid based on its result."""
        hypothesis.survival_depth = result.get("survival_depth", 0)
        hypothesis.kill_test = result.get("kill_test", "")
        hypothesis.fitness = result.get("z_score", 0)

        self.history.append({
            "id": hypothesis.id,
            "cell": _cell_key(hypothesis),
            "depth": hypothesis.survival_depth,
            "z": result.get("z_score", 0),
            "kill": hypothesis.kill_test,
            "gen": hypothesis.generation,
        })

        cell = _cell_key(hypothesis)

        # Only place if it survived at least 1 test
        if hypothesis.survival_depth < 1:
            return False

        # Place if cell is empty or this is better
        if cell not in self.grid or hypothesis.survival_depth > self.grid[cell].survival_depth:
            self.grid[cell] = hypothesis
            return True
        elif (hypothesis.survival_depth == self.grid[cell].survival_depth
              and abs(hypothesis.fitness) > abs(self.grid[cell].fitness)):
            self.grid[cell] = hypothesis
            return True

        return False

    def select_parents(self, n=2, rng=None):
        """Select parents for crossover from the archive."""
        if rng is None:
            rng = np.random.default_rng()

        if len(self.grid) < 2:
            return []

        cells = list(self.grid.values())
        if len(cells) < n:
            return cells

        # Tournament selection: pick 3, return best 2
        tournament = rng.choice(len(cells), min(3, len(cells)), replace=False)
        candidates = sorted([cells[i] for i in tournament],
                           key=lambda h: h.survival_depth, reverse=True)
        return candidates[:n]

    def get_void_cells(self):
        """Return cells that have never been filled."""
        all_cells = set()
        for dc in DOMAIN_CATEGORY_LIST:
            for mc in MEASUREMENT_CATEGORIES:
                all_cells.add((dc, mc))
        # Also add cross-category pairs
        for i, dc1 in enumerate(DOMAIN_CATEGORY_LIST):
            for dc2 in DOMAIN_CATEGORY_LIST[i:]:
                for mc in MEASUREMENT_CATEGORIES:
                    all_cells.add((f"{dc1}_{dc2}", mc))

        filled = set(self.grid.keys())
        return all_cells - filled

    def summary(self):
        """Print archive state."""
        n_cells = len(self.grid)
        n_tested = len(self.history)
        n_survived = sum(1 for h in self.history if h["depth"] > 0)
        max_depth = max((h["depth"] for h in self.history), default=0)

        depths = defaultdict(int)
        for h in self.history:
            depths[h["depth"]] += 1

        kill_modes = defaultdict(int)
        for h in self.history:
            if h["kill"]:
                kill_modes[h["kill"]] += 1

        return {
            "cells_filled": n_cells,
            "total_tested": n_tested,
            "total_survived_f1": n_survived,
            "max_depth": max_depth,
            "depth_distribution": dict(depths),
            "top_kill_modes": dict(sorted(kill_modes.items(), key=lambda x: -x[1])[:10]),
            "generation": self.generation,
        }

    def save(self, path):
        """Save archive to JSON."""
        data = {
            "grid": {str(k): v.to_json() for k, v in self.grid.items()},
            "history_count": len(self.history),
            "summary": self.summary(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path):
        """Load archive from JSON."""
        with open(path) as f:
            data = json.load(f)
        for key_str, hyp_json in data.get("grid", {}).items():
            hyp = Hypothesis.from_json(hyp_json)
            key = eval(key_str)  # convert string tuple back
            self.grid[key] = hyp


if __name__ == "__main__":
    from gene_schema import random_hypothesis

    print("Archive Test")
    print("=" * 60)

    archive = Archive()

    # Simulate 100 hypotheses
    import random
    _rng = random.Random(42)
    for gen in range(5):
        for i in range(20):
            h = random_hypothesis(gen, _rng)
            # Simulate result
            result = {
                "survival_depth": _rng.choice([0, 0, 0, 0, 1, 1, 2, 3]),
                "z_score": _rng.gauss(0, 2),
                "kill_test": _rng.choice(["F1_permutation_null", "F3_effect_size", "F24_permutation", ""]),
            }
            archive.update(h, result)
        archive.generation = gen

    summary = archive.summary()
    print(f"  Cells filled: {summary['cells_filled']}")
    print(f"  Total tested: {summary['total_tested']}")
    print(f"  Survived F1: {summary['total_survived_f1']}")
    print(f"  Max depth: {summary['max_depth']}")
    print(f"  Depth distribution: {summary['depth_distribution']}")
    print(f"  Top kill modes: {summary['top_kill_modes']}")
    print(f"  Void cells: {len(archive.get_void_cells())}")

    # Save/load test
    archive.save(Path(__file__).parent / "test_archive.json")
    print(f"\n  Saved to test_archive.json")
