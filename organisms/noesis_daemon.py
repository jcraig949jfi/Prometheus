"""
Noesis Daemon — Continuous tensor-based exploration engine.

Runs a tournament of search strategies competing to find the highest-quality
compositions of mathematical operations. Each cycle: strategies propose chains,
chains execute in subprocess isolation, results are scored on 7 dimensions,
MAP-Elites grid maintains diversity, islands enable parallel exploration.

Usage:
    python noesis_daemon.py --hours 30 --batch-size 100
    python noesis_daemon.py --resume
    python noesis_daemon.py --report
"""

import argparse
import gc
import hashlib
import json
import logging
import math
import multiprocessing as mp
import os
import random
import sys
import time
import traceback
import warnings
import zlib
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

warnings.filterwarnings("ignore")
np.seterr(all="ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ORGANISMS_DIR = Path(__file__).resolve().parent
ROOT = ORGANISMS_DIR.parent
DB_PATH = ORGANISMS_DIR / "noesis_state.duckdb"
CRACKS_PATH = ORGANISMS_DIR / "cracks_live.jsonl"
REPORT_PATH = ORGANISMS_DIR / "noesis_tournament_report.json"
SUMMARY_PATH = ORGANISMS_DIR / "noesis_tournament_summary.md"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ORGANISMS_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NOESIS] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("noesis")


# ============================================================
# Database
# ============================================================

def init_db():
    """Initialize DuckDB with all required tables."""
    import duckdb
    db = duckdb.connect(str(DB_PATH))

    db.execute("""
        CREATE TABLE IF NOT EXISTS compositions (
            chain_id TEXT PRIMARY KEY,
            chain_steps TEXT NOT NULL,
            strategy TEXT NOT NULL,
            island INTEGER DEFAULT 0,
            cycle INTEGER NOT NULL,
            executed BOOLEAN NOT NULL,
            quality DOUBLE DEFAULT 0.0,
            score_execution DOUBLE DEFAULT 0.0,
            score_novelty DOUBLE DEFAULT 0.0,
            score_structure DOUBLE DEFAULT 0.0,
            score_diversity DOUBLE DEFAULT 0.0,
            score_compression DOUBLE DEFAULT 0.0,
            score_cheapness DOUBLE DEFAULT 0.0,
            score_dead_end DOUBLE DEFAULT 0.0,
            output_hash TEXT,
            output_type TEXT,
            failure_mode TEXT,
            execution_time_us INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS velocity_log (
            cycle INTEGER NOT NULL,
            strategy TEXT NOT NULL,
            chains_tested INTEGER DEFAULT 0,
            chains_executed INTEGER DEFAULT 0,
            cracks INTEGER DEFAULT 0,
            mean_quality DOUBLE DEFAULT 0.0,
            max_quality DOUBLE DEFAULT 0.0,
            qd_score DOUBLE DEFAULT 0.0,
            wall_time_ms INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS tournament_log (
            cycle INTEGER NOT NULL,
            strategy TEXT NOT NULL,
            allocation DOUBLE DEFAULT 0.0,
            total_cracks INTEGER DEFAULT 0,
            cracks_per_cycle DOUBLE DEFAULT 0.0,
            mean_quality DOUBLE DEFAULT 0.0,
            strategy_dna TEXT,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS checkpoint (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT current_timestamp
        )
    """)

    return db


# ============================================================
# Organism Loading
# ============================================================

def load_all_organisms():
    """Load all organisms: hand-built + generated + OEIS."""
    organisms = {}

    # Hand-built
    try:
        from organisms import ALL_ORGANISMS
        for cls in ALL_ORGANISMS:
            org = cls()
            organisms[org.name] = org
    except ImportError:
        pass

    # Generated (auto-wrapped library functions)
    try:
        from organisms.generated import ALL_GENERATED
        for cls in ALL_GENERATED:
            org = cls()
            organisms[org.name] = org
    except ImportError:
        pass

    # OEIS sequences
    try:
        from organisms.oeis_sequences import OeisOrganism
        org = OeisOrganism()
        organisms[org.name] = org
    except ImportError:
        pass

    return organisms


# ============================================================
# Type Compatibility
# ============================================================

NUMERIC_TYPES = {"scalar", "integer", "real", "float", "number", "complex_value"}
ARRAY_TYPES = {"array", "vector", "timeseries", "sequence", "list",
               "probability_distribution", "population_vector",
               "observation_vector", "prime_list", "coordinate_list",
               "gap_sequence"}
MATRIX_TYPES = {"matrix", "adjacency_matrix", "distance_matrix", "joint_distribution"}


def types_compatible(out_type: str, in_type: str) -> bool:
    if out_type == in_type:
        return True
    if out_type in NUMERIC_TYPES and in_type in NUMERIC_TYPES:
        return True
    if out_type in ARRAY_TYPES and in_type in ARRAY_TYPES:
        return True
    if out_type in MATRIX_TYPES and in_type in MATRIX_TYPES:
        return True
    return False


def build_operation_index(organisms):
    """Build flat list of (organism_name, op_name, input_type, output_type)."""
    ops = []
    for org_name, org in organisms.items():
        for op_name, meta in org.operations.items():
            ops.append({
                "organism": org_name,
                "op_name": op_name,
                "input_type": meta.get("input_type", "any"),
                "output_type": meta.get("output_type", "any"),
            })
    return ops


def build_compatible_pairs(op_index):
    """Build list of all type-compatible (i, j) operation pairs across organisms."""
    pairs = []
    for i, a in enumerate(op_index):
        for j, b in enumerate(op_index):
            if a["organism"] == b["organism"]:
                continue
            if types_compatible(a["output_type"], b["input_type"]):
                pairs.append((i, j))
    return pairs


# ============================================================
# Subprocess Chain Execution
# ============================================================

# Test inputs for chain execution
TEST_INPUTS = {
    "scalar": [0.5, 2.0, 7.0, 13.0],
    "integer": [5, 7, 13, 42],
    "array": [
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
    ],
    "matrix": [
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[1, 2], [3, 4]],
    ],
}


_pool_organisms = None

def _pool_init():
    """Initialize organisms once per worker process."""
    global _pool_organisms
    import warnings
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    _pool_organisms = load_all_organisms()


def _execute_single_chain_pooled(args):
    """Execute a chain using pre-loaded organisms in the worker process."""
    pair_or_chain, timeout = args
    global _pool_organisms
    if _pool_organisms is None:
        _pool_init()

    # pair_or_chain is either (i, j) index pair or [(org, op), ...] chain
    if isinstance(pair_or_chain, tuple) and len(pair_or_chain) == 2 and isinstance(pair_or_chain[0], int):
        # It's an index pair — but we don't have op_index in the worker
        # Return a dummy result
        return {"chain": [], "executed": False, "successes": 0, "attempts": 0,
                "success_rate": 0, "outputs": [], "failure_mode": "warmup",
                "execution_time_us": 0}

    chain = pair_or_chain
    return _execute_chain_direct(chain, _pool_organisms, timeout=timeout)


def _execute_chain_direct(chain, organisms, timeout=2.0):
    """Execute a chain directly using pre-loaded organisms (for thread-based execution)."""
    successes = 0
    attempts = 0
    outputs = []
    failure_mode = None

    for input_type, inputs in TEST_INPUTS.items():
        for test_input in inputs:
            attempts += 1
            try:
                result = np.array(test_input) if isinstance(test_input, list) else test_input

                for org_name, op_name in chain:
                    if org_name not in organisms:
                        raise ValueError(f"Unknown organism: {org_name}")
                    org = organisms[org_name]
                    t0 = time.perf_counter()
                    result = org.execute(op_name, result)
                    if time.perf_counter() - t0 > timeout:
                        raise TimeoutError("timeout")

                    if result is None:
                        raise ValueError("None result")
                    if isinstance(result, (np.ndarray, np.generic)):
                        if np.any(np.isnan(result)):
                            raise ValueError("nan")
                        if np.any(np.isinf(result)):
                            raise ValueError("overflow")
                        if isinstance(result, np.ndarray) and result.size > 500_000:
                            raise ValueError("output_too_large")

                successes += 1
                if isinstance(result, np.ndarray):
                    h = hashlib.md5(result.tobytes()).hexdigest()[:12]
                    otype = f"ndarray_{result.shape}"
                elif isinstance(result, (int, float, np.integer, np.floating)):
                    h = hashlib.md5(str(float(result)).encode()).hexdigest()[:12]
                    otype = "scalar"
                else:
                    h = hashlib.md5(str(result)[:500].encode()).hexdigest()[:12]
                    otype = type(result).__name__
                outputs.append({"hash": h, "type": otype})

            except ValueError as e:
                msg = str(e).lower()
                if "nan" in msg:
                    failure_mode = failure_mode or "nan"
                elif "overflow" in msg or "inf" in msg:
                    failure_mode = failure_mode or "overflow"
                else:
                    failure_mode = failure_mode or "value_error"
            except TimeoutError:
                failure_mode = failure_mode or "timeout"
            except TypeError:
                failure_mode = failure_mode or "type_error"
            except Exception:
                failure_mode = failure_mode or "other_error"

    return {
        "chain": chain,
        "executed": successes > 0,
        "successes": successes,
        "attempts": max(attempts, 1),
        "success_rate": successes / max(attempts, 1),
        "outputs": outputs,
        "failure_mode": failure_mode if successes == 0 else None,
        "execution_time_us": 0,
    }


def _pair_to_chain_static(op_index, i, j):
    """Convert operation indices to chain tuples (module-level for multiprocessing)."""
    a = op_index[i]
    b = op_index[j]
    return [(a["organism"], a["op_name"]), (b["organism"], b["op_name"])]


def _execute_single_chain(args):
    """
    Execute a single chain in an isolated subprocess.
    Called by multiprocessing.Pool. Returns result dict.
    """
    chain, timeout = args
    # chain is list of (org_name, op_name) tuples

    import warnings
    warnings.filterwarnings("ignore")
    import numpy as np
    np.seterr(all="ignore")

    # Must re-load organisms in subprocess
    organisms = {}
    try:
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(ORGANISMS_DIR))
        organisms = load_all_organisms()
    except Exception as e:
        return {
            "chain": chain, "executed": False, "failure_mode": "import_error",
            "outputs": [], "execution_time_us": 0, "error": str(e)[:200]
        }

    successes = 0
    attempts = 0
    outputs = []
    failure_mode = None
    start_ns = time.perf_counter_ns()

    for input_type, inputs in TEST_INPUTS.items():
        for test_input in inputs:
            attempts += 1
            try:
                result = np.array(test_input) if isinstance(test_input, list) else test_input

                for org_name, op_name in chain:
                    if org_name not in organisms:
                        raise ValueError(f"Unknown organism: {org_name}")
                    org = organisms[org_name]
                    t0 = time.perf_counter()
                    result = org.execute(op_name, result)
                    if time.perf_counter() - t0 > timeout:
                        raise TimeoutError("timeout")

                    if result is None:
                        raise ValueError("None result")
                    if isinstance(result, (np.ndarray, np.generic)):
                        if np.any(np.isnan(result)):
                            raise ValueError("nan")
                        if np.any(np.isinf(result)):
                            raise ValueError("overflow")
                        if isinstance(result, np.ndarray) and result.size > 500_000:
                            raise ValueError("output_too_large")

                successes += 1
                # Hash output
                if isinstance(result, np.ndarray):
                    h = hashlib.md5(result.tobytes()).hexdigest()[:12]
                    otype = f"ndarray_{result.shape}"
                elif isinstance(result, (int, float, np.integer, np.floating)):
                    h = hashlib.md5(str(float(result)).encode()).hexdigest()[:12]
                    otype = "scalar"
                else:
                    h = hashlib.md5(str(result)[:500].encode()).hexdigest()[:12]
                    otype = type(result).__name__
                outputs.append({"hash": h, "type": otype})

            except ValueError as e:
                msg = str(e).lower()
                if "nan" in msg:
                    failure_mode = failure_mode or "nan"
                elif "overflow" in msg or "inf" in msg:
                    failure_mode = failure_mode or "overflow"
                elif "too_large" in msg:
                    failure_mode = failure_mode or "output_too_large"
                else:
                    failure_mode = failure_mode or "value_error"
            except TimeoutError:
                failure_mode = failure_mode or "timeout"
            except TypeError:
                failure_mode = failure_mode or "type_error"
            except Exception:
                failure_mode = failure_mode or "other_error"

    elapsed_us = (time.perf_counter_ns() - start_ns) // 1000

    return {
        "chain": chain,
        "executed": successes > 0,
        "successes": successes,
        "attempts": attempts,
        "success_rate": successes / max(attempts, 1),
        "outputs": outputs,
        "failure_mode": failure_mode if successes == 0 else None,
        "execution_time_us": elapsed_us,
    }


# ============================================================
# Quality Scoring
# ============================================================

class QualityScorer:
    """7-component quality scoring system."""

    def __init__(self, op_index, all_output_hashes=None):
        self.op_index = op_index
        self.seen_hashes = set(all_output_hashes or [])
        self.recent_organisms = []  # Last 200 chain organism sets
        self._output_type_downstream = self._build_downstream_map()
        self.execution_baseline = 0.0

    def _build_downstream_map(self):
        """For each output type, count how many operations accept it."""
        downstream = defaultdict(int)
        for op in self.op_index:
            downstream[op["input_type"]] += 1
        return downstream

    def score(self, result: Dict, chain: List[Tuple[str, str]]) -> Dict:
        """Score a chain execution result on 7 dimensions."""
        scores = {}

        # 1. Execution (binary)
        scores["execution"] = 1.0 if result["executed"] else 0.0

        # 2. Novelty (cosine distance from seen outputs)
        hashes = [o["hash"] for o in result.get("outputs", [])]
        new_hashes = [h for h in hashes if h not in self.seen_hashes]
        scores["novelty"] = len(new_hashes) / max(len(hashes), 1) if hashes else 0.0
        self.seen_hashes.update(hashes)

        # 3. Structure (output complexity)
        if result["executed"] and result.get("outputs"):
            output_types = [o["type"] for o in result["outputs"]]
            # Higher structure = array/matrix outputs vs scalar
            struct_score = 0.0
            for ot in output_types:
                if "ndarray" in ot:
                    struct_score += 0.8
                elif ot == "scalar":
                    struct_score += 0.3
                else:
                    struct_score += 0.5
            scores["structure"] = min(struct_score / max(len(output_types), 1), 1.0)
        else:
            scores["structure"] = 0.0

        # 4. Diversity (organism set novelty)
        chain_orgs = frozenset(org for org, _ in chain)
        recent_overlap = sum(1 for recent in self.recent_organisms[-200:]
                             if chain_orgs == recent)
        scores["diversity"] = max(0.0, 1.0 - recent_overlap / 5.0)
        self.recent_organisms.append(chain_orgs)

        # 5. Compression gain (entropy reduction)
        scores["compression"] = 0.0
        # Simplified: if we produced structured output from scalar input, that's negative compression
        # If we compressed array to scalar, that's positive
        if result["executed"] and result.get("outputs"):
            first_input_type = chain[0][0]  # approximate
            output_types = [o["type"] for o in result["outputs"]]
            scalar_out = sum(1 for ot in output_types if ot == "scalar")
            scores["compression"] = scalar_out / max(len(output_types), 1) * 0.5

        # 6. Cheapness penalty
        scores["cheapness"] = 0.0
        if result["executed"]:
            hashes = [o["hash"] for o in result.get("outputs", [])]
            if len(set(hashes)) == 1 and len(hashes) > 1:
                scores["cheapness"] = 0.5  # constant output regardless of input
            if result.get("execution_time_us", 0) < 100 and len(chain) >= 2:
                scores["cheapness"] = max(scores["cheapness"], 0.3)  # suspiciously fast

        # 7. Dead-end penalty
        scores["dead_end"] = 0.0
        if result["executed"] and result.get("outputs"):
            last_op = chain[-1]
            # Find the output type of the last operation
            for op in self.op_index:
                if op["organism"] == last_op[0] and op["op_name"] == last_op[1]:
                    out_type = op["output_type"]
                    if self._output_type_downstream.get(out_type, 0) == 0:
                        scores["dead_end"] = 1.0
                    break

        # Combined quality
        exec_weight = 0.10 if self.execution_baseline > 0.5 else 0.25
        remaining = 1.0 - exec_weight - 0.10  # 0.10 for penalties
        quality = (
            exec_weight * scores["execution"]
            + remaining * 0.31 * scores["novelty"]
            + remaining * 0.19 * scores["structure"]
            + remaining * 0.19 * scores["diversity"]
            + remaining * 0.19 * scores["compression"]
            - 0.05 * scores["cheapness"]
            - 0.05 * scores["dead_end"]
        )

        scores["quality"] = max(0.0, min(1.0, quality))
        return scores

    def update_baseline(self, exec_rate: float):
        """Update execution baseline for dynamic weight adjustment."""
        self.execution_baseline = 0.9 * self.execution_baseline + 0.1 * exec_rate


# ============================================================
# MAP-Elites Grid
# ============================================================

class MAPElitesGrid:
    """4x4x4 behavioral descriptor grid."""

    # Axes: chain_length(2-5), output_complexity(scalar/array/matrix/struct), organism_diversity
    SHAPE = (4, 4, 4)

    def __init__(self):
        self.grid = {}  # (i, j, k) -> {"chain": ..., "quality": ..., "chain_id": ...}

    def get_cell(self, chain, result, scores):
        """Map a chain+result to grid coordinates."""
        # Axis 0: chain length (2=0, 3=1, 4=2, 5+=3)
        length_idx = min(len(chain) - 2, 3)

        # Axis 1: output complexity
        if not result["executed"]:
            complexity_idx = 0
        else:
            output_types = [o["type"] for o in result.get("outputs", [])]
            has_matrix = any("ndarray" in ot and "," in ot for ot in output_types)
            has_array = any("ndarray" in ot for ot in output_types)
            has_struct = any(ot not in ("scalar",) and "ndarray" not in ot for ot in output_types)
            if has_matrix:
                complexity_idx = 3
            elif has_struct:
                complexity_idx = 2
            elif has_array:
                complexity_idx = 1
            else:
                complexity_idx = 0

        # Axis 2: organism diversity
        unique_orgs = len(set(org for org, _ in chain))
        diversity_idx = min(unique_orgs - 1, 3)

        return (length_idx, complexity_idx, diversity_idx)

    def try_insert(self, cell, chain, quality, chain_id):
        """Insert if cell is empty or new quality exceeds current occupant."""
        if cell not in self.grid or quality > self.grid[cell]["quality"]:
            self.grid[cell] = {
                "chain": chain,
                "quality": quality,
                "chain_id": chain_id,
            }
            return True
        return False

    def qd_score(self):
        """Sum of all filled cell qualities."""
        return sum(entry["quality"] for entry in self.grid.values())

    def cells_filled(self):
        return len(self.grid)

    def total_cells(self):
        return self.SHAPE[0] * self.SHAPE[1] * self.SHAPE[2]

    def to_dict(self):
        return {
            "cells_filled": self.cells_filled(),
            "total_cells": self.total_cells(),
            "qd_score": self.qd_score(),
            "grid": {str(k): v for k, v in self.grid.items()},
        }


# ============================================================
# Strategies
# ============================================================

class Strategy:
    """Base class for search strategies."""
    name = "base"

    def __init__(self, op_index, compat_pairs):
        self.op_index = op_index
        self.compat_pairs = compat_pairs
        self.total_cracks = 0
        self.total_tested = 0
        self.allocation = 1.0
        self.blacklist = set()  # Chain hashes to skip
        self._recent_proposals = []

    def propose(self, n: int) -> List[List[Tuple[str, str]]]:
        raise NotImplementedError

    def _pair_to_chain(self, i, j):
        a = self.op_index[i]
        b = self.op_index[j]
        return [(a["organism"], a["op_name"]), (b["organism"], b["op_name"])]

    def _chain_hash(self, chain):
        return hashlib.md5(str(chain).encode()).hexdigest()[:16]

    def _filter_blacklisted(self, chains):
        filtered = []
        for c in chains:
            h = self._chain_hash(c)
            if h not in self.blacklist:
                filtered.append(c)
        return filtered

    def _track_proposals(self, chains):
        """Track proposals for degenerate loop detection."""
        for c in chains:
            self._recent_proposals.append(self._chain_hash(c))
        # Keep last 500
        self._recent_proposals = self._recent_proposals[-500:]

    def proposal_uniqueness(self):
        """Fraction of unique proposals in recent history."""
        if not self._recent_proposals:
            return 1.0
        return len(set(self._recent_proposals[-100:])) / min(100, len(self._recent_proposals))

    def update(self, cracks, tested):
        self.total_cracks += cracks
        self.total_tested += tested

    def cracks_per_cycle(self):
        return self.total_cracks / max(self.total_tested / 100, 1)

    def to_dict(self):
        return {
            "name": self.name,
            "total_cracks": self.total_cracks,
            "total_tested": self.total_tested,
            "cracks_per_cycle": self.cracks_per_cycle(),
            "allocation": self.allocation,
            "proposal_uniqueness": self.proposal_uniqueness(),
        }


class RandomStrategy(Strategy):
    """Strategy 1: Uniform random over type-compatible pairs."""
    name = "random_baseline"

    def propose(self, n):
        if not self.compat_pairs:
            return []
        indices = [random.choice(self.compat_pairs) for _ in range(n)]
        chains = [self._pair_to_chain(i, j) for i, j in indices]
        chains = self._filter_blacklisted(chains)
        self._track_proposals(chains)
        return chains[:n]


class TensorTopKStrategy(Strategy):
    """Strategy 2: Top-K by operation tensor score."""
    name = "tensor_topk"

    def __init__(self, op_index, compat_pairs, pairwise_scores):
        super().__init__(op_index, compat_pairs)
        # Pre-sort pairs by score
        self.scored_pairs = sorted(
            compat_pairs,
            key=lambda p: pairwise_scores[p[0], p[1]],
            reverse=True,
        )
        self.scores = pairwise_scores
        self._pointer = 0

    def propose(self, n):
        chains = []
        for _ in range(n):
            if self._pointer >= len(self.scored_pairs):
                self._pointer = 0
            i, j = self.scored_pairs[self._pointer]
            chains.append(self._pair_to_chain(i, j))
            self._pointer += 1
        chains = self._filter_blacklisted(chains)
        self._track_proposals(chains)
        return chains[:n]


class FrontierStrategy(Strategy):
    """Strategy 3: Favor unexplored regions of the operation space."""
    name = "frontier_seeking"

    def __init__(self, op_index, compat_pairs, pairwise_scores):
        super().__init__(op_index, compat_pairs)
        self.scores = pairwise_scores
        self.visit_counts = defaultdict(int)

    def propose(self, n):
        # Score = tensor_score * (1 / (1 + visit_count))
        scored = []
        for i, j in self.compat_pairs:
            visits = self.visit_counts[(i, j)]
            curiosity = 1.0 / (1.0 + visits)
            score = self.scores[i, j] * curiosity
            scored.append((i, j, score))

        scored.sort(key=lambda x: -x[2])
        chains = []
        for i, j, _ in scored[:n * 2]:
            chain = self._pair_to_chain(i, j)
            if self._chain_hash(chain) not in self.blacklist:
                chains.append(chain)
                self.visit_counts[(i, j)] += 1
            if len(chains) >= n:
                break
        self._track_proposals(chains)
        return chains[:n]


class EpsilonGreedyStrategy(Strategy):
    """Strategy 5: 80% exploit (tensor top), 20% explore (random)."""
    name = "epsilon_greedy"

    def __init__(self, op_index, compat_pairs, pairwise_scores, epsilon=0.2):
        super().__init__(op_index, compat_pairs)
        self.scores = pairwise_scores
        self.epsilon = epsilon
        self.sorted_pairs = sorted(
            compat_pairs,
            key=lambda p: pairwise_scores[p[0], p[1]],
            reverse=True,
        )

    def propose(self, n):
        chains = []
        for _ in range(n):
            if random.random() < self.epsilon:
                i, j = random.choice(self.compat_pairs)
            else:
                idx = random.randint(0, min(len(self.sorted_pairs) - 1, n * 2))
                i, j = self.sorted_pairs[idx]
            chains.append(self._pair_to_chain(i, j))
        chains = self._filter_blacklisted(chains)
        self._track_proposals(chains)
        return chains[:n]


class TemperatureAnnealStrategy(Strategy):
    """Strategy 6: Softmax selection with annealing temperature."""
    name = "temperature_anneal"

    def __init__(self, op_index, compat_pairs, pairwise_scores):
        super().__init__(op_index, compat_pairs)
        self.scores = pairwise_scores
        self.temperature = 2.0
        self.min_temp = 0.3
        self.anneal_rate = 0.995
        self.cycle_count = 0
        self.reset_every = 200

        # Precompute scores for compat pairs
        self.pair_scores = np.array([
            pairwise_scores[i, j] for i, j in compat_pairs
        ], dtype=np.float64)

    def propose(self, n):
        self.cycle_count += 1

        # Anneal
        self.temperature = max(self.min_temp, self.temperature * self.anneal_rate)

        # Reset periodically
        if self.cycle_count % self.reset_every == 0:
            self.temperature = 2.0

        # Softmax with temperature
        logits = self.pair_scores / max(self.temperature, 0.01)
        logits = logits - np.max(logits)  # numerical stability
        probs = np.exp(logits)
        probs = probs / probs.sum()

        indices = np.random.choice(len(self.compat_pairs), size=n, replace=True, p=probs)
        chains = [self._pair_to_chain(*self.compat_pairs[idx]) for idx in indices]
        chains = self._filter_blacklisted(chains)
        self._track_proposals(chains)
        return chains[:n]

    def to_dict(self):
        d = super().to_dict()
        d["temperature"] = self.temperature
        return d


class MutationStrategy(Strategy):
    """Strategy 19: Mutate successful chains by replacing one operation."""
    name = "mutation"

    def __init__(self, op_index, compat_pairs, pairwise_scores):
        super().__init__(op_index, compat_pairs)
        self.scores = pairwise_scores
        self.hall_of_fame = []  # Top chains seen

    def add_to_hof(self, chain, quality):
        self.hall_of_fame.append((chain, quality))
        self.hall_of_fame.sort(key=lambda x: -x[1])
        self.hall_of_fame = self.hall_of_fame[:50]

    def propose(self, n):
        if not self.hall_of_fame:
            # Fall back to random
            indices = [random.choice(self.compat_pairs) for _ in range(n)]
            chains = [self._pair_to_chain(i, j) for i, j in indices]
            self._track_proposals(chains)
            return chains[:n]

        chains = []
        for _ in range(n):
            parent, _ = random.choice(self.hall_of_fame[:20])
            # Pick a random position to mutate
            pos = random.randint(0, len(parent) - 1)
            mutant = list(parent)

            # Find a compatible replacement
            if pos == 0 and len(parent) > 1:
                # Must output type compatible with next step's input
                next_op = parent[1]
                next_input = None
                for op in self.op_index:
                    if op["organism"] == next_op[0] and op["op_name"] == next_op[1]:
                        next_input = op["input_type"]
                        break
                candidates = [op for op in self.op_index
                              if op["organism"] != next_op[0]
                              and next_input and types_compatible(op["output_type"], next_input)]
            elif pos == len(parent) - 1 and len(parent) > 1:
                prev_op = parent[-2]
                prev_output = None
                for op in self.op_index:
                    if op["organism"] == prev_op[0] and op["op_name"] == prev_op[1]:
                        prev_output = op["output_type"]
                        break
                candidates = [op for op in self.op_index
                              if op["organism"] != prev_op[0]
                              and prev_output and types_compatible(prev_output, op["input_type"])]
            else:
                candidates = list(self.op_index)

            if candidates:
                replacement = random.choice(candidates)
                mutant[pos] = (replacement["organism"], replacement["op_name"])
                chains.append(mutant)

        chains = self._filter_blacklisted(chains)
        self._track_proposals(chains)
        return chains[:n]


# ============================================================
# Tournament
# ============================================================

class Tournament:
    """Manages strategy allocation and adaptive rebalancing."""

    def __init__(self, strategies: List[Strategy]):
        self.strategies = {s.name: s for s in strategies}
        self.cycle = 0
        self.total_cracks = 0
        self._rebalance_every = 50

    def select_strategy(self) -> Strategy:
        """Select a strategy weighted by allocation."""
        names = list(self.strategies.keys())
        weights = [max(self.strategies[n].allocation, 0.05) for n in names]
        total = sum(weights)
        weights = [w / total for w in weights]
        chosen = random.choices(names, weights=weights, k=1)[0]
        return self.strategies[chosen]

    def update(self, strategy_name: str, cracks: int, tested: int):
        self.strategies[strategy_name].update(cracks, tested)
        self.total_cracks += cracks
        self.cycle += 1

        if self.cycle % self._rebalance_every == 0:
            self._rebalance()

    def _rebalance(self):
        """Adaptive allocation based on performance."""
        avg_cpc = np.mean([s.cracks_per_cycle() for s in self.strategies.values()])
        if avg_cpc == 0:
            return  # Nothing to rebalance yet

        for s in self.strategies.values():
            if s.name == "random_baseline":
                continue  # Sacred: never change random's allocation
            cpc = s.cracks_per_cycle()
            if cpc > 2 * avg_cpc:
                s.allocation = min(s.allocation * 1.5, 5.0)
            elif cpc < 0.5 * avg_cpc and s.total_tested > 300:
                s.allocation = max(s.allocation * 0.7, 0.1)

    def should_abort(self) -> bool:
        """Check abort conditions."""
        if self.cycle < 500:
            return False

        random_strat = self.strategies.get("random_baseline")
        if not random_strat:
            return False

        random_cpc = random_strat.cracks_per_cycle()
        any_beats_random = any(
            s.cracks_per_cycle() > random_cpc * 1.2
            for name, s in self.strategies.items()
            if name != "random_baseline" and s.total_tested > 100
        )

        if not any_beats_random and self.total_cracks == 0:
            return True

        return False

    def leaderboard(self) -> List[Dict]:
        entries = [s.to_dict() for s in self.strategies.values()]
        entries.sort(key=lambda x: -x["cracks_per_cycle"])
        return entries


# ============================================================
# The Daemon
# ============================================================

def run_daemon(max_hours: float = 30.0, batch_size: int = 100,
               crack_threshold: float = 0.5, resume: bool = False):
    """Main exploration loop."""
    start_time = time.monotonic()
    deadline = start_time + max_hours * 3600

    log.info("=" * 70)
    log.info("  NOESIS DAEMON — Continuous Tensor Exploration")
    log.info("=" * 70)

    # Initialize DB
    db = init_db()

    # Resume check
    cycle_start = 0
    if resume:
        try:
            row = db.execute("SELECT value FROM checkpoint WHERE key='last_cycle'").fetchone()
            if row:
                cycle_start = int(row[0])
                log.info(f"  Resuming from cycle {cycle_start}")
        except Exception:
            pass

    # Load organisms
    log.info("  Loading organisms...")
    organisms = load_all_organisms()
    total_ops = sum(len(org.operations) for org in organisms.values())
    log.info(f"  {len(organisms)} organisms, {total_ops} operations")

    # Build operation index
    op_index = build_operation_index(organisms)
    compat_pairs = build_compatible_pairs(op_index)
    log.info(f"  {len(op_index)} operations indexed, {len(compat_pairs)} compatible pairs")

    # Build pairwise scores for tensor-guided strategies
    # We build this directly from op_index rather than using OperationTensor
    # because OperationTensor has its own organism loading which may differ.
    log.info("  Computing pairwise operation scores...")
    n_ops = len(op_index)
    from organisms.concept_tensor import CONCEPT_FEATURES

    # Map organisms to concept features
    org_to_concept = {
        "information_theory": "Information Theory", "topology": "Topology",
        "chaos_theory": "Chaos Theory", "bayesian_inference": "Bayesian Inference",
        "game_theory": "Nash Equilibrium", "immune_systems": "Immune Systems",
        "network_science": "Network Science", "signal_processing": "Matched Filtering",
        "statistical_mechanics": "Statistical Mechanics", "dynamical_systems": "Dynamical Systems",
        "prime_theory": "Prime Number Theory",
        "algebraic_number_theory": "Prime Number Theory",
        "analytic_number_theory": "Prime Number Theory",
        "geometric_number_theory": "Fractal Geometry",
        "probabilistic_number_theory": "Prime Number Theory",
        "combinatorial_number_theory": "Prime Number Theory",
        "computational_number_theory": "Prime Number Theory",
        "number_geometry_bridge": "Topology",
        "numpy": "Tensor Decomposition", "scipy_linalg": "Tensor Decomposition",
        "scipy_signal": "Wavelet Transforms", "scipy_stats": "Bayesian Inference",
        "scipy_special": "Fourier Transforms", "math": "Information Theory",
        "cmath": "Information Theory", "statistics": "Bayesian Inference",
        "oeis": "Prime Number Theory",
    }

    # Build concept feature vectors for each operation
    op_concept_feats = np.zeros((n_ops, 30), dtype=np.float32)
    for i, op in enumerate(op_index):
        concept = org_to_concept.get(op["organism"])
        if concept and concept in CONCEPT_FEATURES:
            op_concept_feats[i] = np.array(CONCEPT_FEATURES[concept], dtype=np.float32)

    # Compute pairwise scores for compatible pairs only
    pairwise_scores = np.zeros((n_ops, n_ops), dtype=np.float32)
    for i, j in compat_pairs:
        if op_index[i]["organism"] == op_index[j]["organism"]:
            continue
        fi, fj = op_concept_feats[i], op_concept_feats[j]
        comp = float(np.mean(np.abs(fi - fj)))
        res = float(np.mean(fi * fj))
        interface = np.outer(fi, fj)
        diag_e = np.sum(np.diag(interface) ** 2)
        total_e = np.sum(interface ** 2)
        nov = 1.0 - diag_e / total_e if total_e > 0 else 0.0
        # Exact type match bonus
        type_bonus = 1.2 if op_index[i]["output_type"] == op_index[j]["input_type"] else 1.0
        pairwise_scores[i, j] = (0.4 * nov + 0.35 * comp + 0.25 * res) * type_bonus

    n_scored = int(np.sum(pairwise_scores > 0))
    log.info(f"  Pairwise scores: {n_scored} non-zero pairs across {n_ops} operations")

    # Initialize strategies (core 6)
    strategies = [
        RandomStrategy(op_index, compat_pairs),
        TensorTopKStrategy(op_index, compat_pairs, pairwise_scores),
        FrontierStrategy(op_index, compat_pairs, pairwise_scores),
        EpsilonGreedyStrategy(op_index, compat_pairs, pairwise_scores),
        TemperatureAnnealStrategy(op_index, compat_pairs, pairwise_scores),
        MutationStrategy(op_index, compat_pairs, pairwise_scores),
    ]
    tournament = Tournament(strategies)
    log.info(f"  {len(strategies)} strategies initialized")

    # Initialize MAP-Elites
    grid = MAPElitesGrid()

    # Initialize quality scorer
    existing_hashes = set()
    try:
        rows = db.execute("SELECT output_hash FROM compositions WHERE output_hash IS NOT NULL").fetchall()
        existing_hashes = {r[0] for r in rows}
    except Exception:
        pass
    scorer = QualityScorer(op_index, existing_hashes)

    # Process pool with persistent workers (import organisms once per worker)
    n_workers = min(mp.cpu_count(), 4)
    # Workers import organisms in _pool_init and keep them alive
    pool = mp.Pool(processes=n_workers, initializer=_pool_init,
                   maxtasksperchild=20)
    _organisms_cache = organisms  # Keep for main-process fallback

    log.info(f"  Process pool: {n_workers} persistent workers (import once)")
    log.info(f"  Deadline: {max_hours:.1f} hours")

    # Warm up all workers by sending one dummy task to each
    log.info("  Warming up workers...")
    try:
        dummy_chains = [chains[0:1] if chains else [] for chains in
                        [[(_pair_to_chain_static(op_index, *compat_pairs[0]))] * n_workers]]
        warmup = pool.map(_execute_single_chain_pooled, [(compat_pairs[0], 3.0)] * n_workers)
        log.info(f"  {n_workers} workers ready")
    except Exception as e:
        log.info(f"  Warm-up issue: {e}")

    log.info("=" * 70)
    log.info("")

    cycle = cycle_start
    total_chains_tested = 0

    try:
        while time.monotonic() < deadline:
            cycle += 1
            cycle_t0 = time.monotonic()

            # Select strategy
            strategy = tournament.select_strategy()

            # Propose chains
            chains = strategy.propose(batch_size)
            if not chains:
                continue

            # Execute chains with individual per-chain timeouts
            # On first timeout, kill pool and restart (hung worker = dead slot)
            results = []
            pool_killed = False
            futures = []
            for c in chains:
                f = pool.apply_async(_execute_single_chain_pooled, [(c, 1.0)])
                futures.append((c, f))

            for c, f in futures:
                if pool_killed:
                    results.append({
                        "chain": c, "executed": False, "successes": 0,
                        "attempts": 1, "success_rate": 0,
                        "outputs": [], "failure_mode": "pool_killed",
                        "execution_time_us": 0,
                    })
                    continue
                try:
                    result = f.get(timeout=3.0)  # 3s hard limit per chain
                    results.append(result)
                except mp.TimeoutError:
                    # Hung worker — kill the entire pool and restart
                    results.append({
                        "chain": c, "executed": False, "successes": 0,
                        "attempts": 1, "success_rate": 0,
                        "outputs": [], "failure_mode": "timeout",
                        "execution_time_us": 0,
                    })
                    try:
                        pool.terminate()
                        pool.join()
                    except Exception:
                        pass
                    pool = mp.Pool(processes=n_workers, initializer=_pool_init,
                                   maxtasksperchild=20)
                    pool_killed = True
                except Exception:
                    results.append({
                        "chain": c, "executed": False, "successes": 0,
                        "attempts": 1, "success_rate": 0,
                        "outputs": [], "failure_mode": "other_error",
                        "execution_time_us": 0,
                    })

            # Score results
            cycle_cracks = 0
            cycle_executed = 0

            for chain, result in zip(chains, results):
                scores = scorer.score(result, chain)
                quality = scores["quality"]
                chain_id = hashlib.md5(str(chain).encode()).hexdigest()[:16]

                if result["executed"]:
                    cycle_executed += 1

                if quality >= crack_threshold:
                    cycle_cracks += 1
                    # Live crack logging
                    crack_entry = {
                        "cycle": cycle,
                        "strategy": strategy.name,
                        "chain": [f"{org}.{op}" for org, op in chain],
                        "quality": quality,
                        "scores": scores,
                        "timestamp": datetime.now().isoformat(),
                    }
                    with open(CRACKS_PATH, "a") as f:
                        f.write(json.dumps(crack_entry, default=str) + "\n")

                # MAP-Elites
                cell = grid.get_cell(chain, result, scores)
                grid.try_insert(cell, chain, quality, chain_id)

                # Update mutation strategy hall of fame
                if quality > 0.3:
                    for s in tournament.strategies.values():
                        if isinstance(s, MutationStrategy):
                            s.add_to_hof(chain, quality)

                # Record to DuckDB
                chain_steps = json.dumps(chain)
                output_hash = result["outputs"][0]["hash"] if result.get("outputs") else None

                try:
                    db.execute("""
                        INSERT OR REPLACE INTO compositions
                        (chain_id, chain_steps, strategy, cycle, executed,
                         quality, score_execution, score_novelty, score_structure,
                         score_diversity, score_compression, score_cheapness,
                         score_dead_end, output_hash, failure_mode, execution_time_us)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        chain_id, chain_steps, strategy.name, cycle,
                        result["executed"], quality,
                        scores["execution"], scores["novelty"], scores["structure"],
                        scores["diversity"], scores["compression"],
                        scores["cheapness"], scores["dead_end"],
                        output_hash, result.get("failure_mode"),
                        result.get("execution_time_us", 0),
                    ])
                except Exception:
                    pass

            # Update strategy performance
            tournament.update(strategy.name, cycle_cracks, len(chains))
            total_chains_tested += len(chains)

            # Update scorer baseline
            exec_rate = cycle_executed / max(len(chains), 1)
            scorer.update_baseline(exec_rate)

            # Degenerate loop detection
            if strategy.proposal_uniqueness() < 0.5:
                strategy.blacklist.clear()  # Reset blacklist
                log.info(f"  [{cycle}] {strategy.name} degenerate — clearing blacklist")

            # Log velocity
            cycle_time_ms = int((time.monotonic() - cycle_t0) * 1000)
            try:
                db.execute("""
                    INSERT INTO velocity_log
                    (cycle, strategy, chains_tested, chains_executed, cracks,
                     mean_quality, qd_score, wall_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    cycle, strategy.name, len(chains), cycle_executed,
                    cycle_cracks, quality, grid.qd_score(), cycle_time_ms,
                ])
            except Exception:
                pass

            # Checkpoint every 10 cycles
            if cycle % 10 == 0:
                try:
                    db.execute("""
                        INSERT OR REPLACE INTO checkpoint (key, value, updated_at)
                        VALUES ('last_cycle', ?, current_timestamp)
                    """, [str(cycle)])
                except Exception:
                    pass

            # Status line every 25 cycles
            if cycle % 25 == 0:
                elapsed_h = (time.monotonic() - start_time) / 3600
                remaining_h = max_hours - elapsed_h
                lb = tournament.leaderboard()
                best = lb[0] if lb else {"name": "none", "cracks_per_cycle": 0}
                random_cpc = tournament.strategies.get("random_baseline",
                    type("", (), {"cracks_per_cycle": lambda: 0})()).cracks_per_cycle()
                log.info(
                    f"  [Cycle {cycle}] Best: {best['name']} ({best['cracks_per_cycle']:.3f} cpc) | "
                    f"QD: {grid.cells_filled()}/{grid.total_cells()} | "
                    f"Cracks: {tournament.total_cracks} | "
                    f"Random: {random_cpc:.3f} cpc | "
                    f"Chains: {total_chains_tested} | "
                    f"Time: {elapsed_h:.1f}h/{remaining_h:.1f}h remain"
                )

            # Memory check every 50 cycles
            if cycle % 50 == 0:
                try:
                    import psutil
                    mem = psutil.virtual_memory()
                    if mem.percent > 80:
                        gc.collect()
                        log.warning(f"  Memory at {mem.percent}% — GC triggered")
                    if mem.percent > 90:
                        log.warning(f"  Memory at {mem.percent}% — aggressive GC")
                        gc.collect()
                except ImportError:
                    pass

            # Abort check
            if tournament.should_abort():
                log.info(f"  ABORT: No strategy beats random after {cycle} cycles")
                break

    except KeyboardInterrupt:
        log.info("  Interrupted by user (Ctrl+C)")

    finally:
        # Cleanup pool
        try:
            pool.terminate()
            pool.join()
        except Exception:
            pass

        # Final checkpoint
        try:
            db.execute("""
                INSERT OR REPLACE INTO checkpoint (key, value, updated_at)
                VALUES ('last_cycle', ?, current_timestamp)
            """, [str(cycle)])
        except Exception:
            pass

        elapsed_h = (time.monotonic() - start_time) / 3600

        # Generate report
        report = generate_report(db, tournament, grid, elapsed_h, cycle, total_chains_tested)
        with open(REPORT_PATH, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Generate summary
        summary = generate_summary(report)
        with open(SUMMARY_PATH, "w") as f:
            f.write(summary)

        log.info("")
        log.info("=" * 70)
        log.info(f"  RUN COMPLETE: {cycle} cycles, {total_chains_tested} chains, "
                 f"{tournament.total_cracks} cracks, {elapsed_h:.1f}h")
        log.info(f"  QD Score: {grid.qd_score():.3f} ({grid.cells_filled()}/{grid.total_cells()} cells)")
        log.info(f"  Report: {REPORT_PATH}")
        log.info(f"  Summary: {SUMMARY_PATH}")
        log.info(f"  Cracks log: {CRACKS_PATH}")
        log.info("=" * 70)

        db.close()


# ============================================================
# Reporting
# ============================================================

def generate_report(db, tournament, grid, elapsed_h, total_cycles, total_chains):
    """Generate the final tournament report."""
    report = {
        "run_metadata": {
            "start_time": datetime.now().isoformat(),
            "total_cycles": total_cycles,
            "total_chains_tested": total_chains,
            "total_cracks": tournament.total_cracks,
            "elapsed_hours": round(elapsed_h, 2),
        },
        "strategy_leaderboard": tournament.leaderboard(),
        "map_elites": grid.to_dict(),
    }

    # Top 50 compositions
    try:
        rows = db.execute("""
            SELECT chain_id, chain_steps, strategy, quality, score_execution,
                   score_novelty, score_structure, output_hash
            FROM compositions
            ORDER BY quality DESC
            LIMIT 50
        """).fetchall()
        report["top_50_compositions"] = [
            {
                "chain_id": r[0], "chain": json.loads(r[1]), "strategy": r[2],
                "quality": r[3], "execution": r[4], "novelty": r[5],
                "structure": r[6], "output_hash": r[7],
            }
            for r in rows
        ]
    except Exception:
        report["top_50_compositions"] = []

    # Failure geometry
    try:
        rows = db.execute("""
            SELECT failure_mode, COUNT(*) as cnt
            FROM compositions
            WHERE failure_mode IS NOT NULL
            GROUP BY failure_mode
            ORDER BY cnt DESC
        """).fetchall()
        report["failure_geometry"] = {r[0]: r[1] for r in rows}
    except Exception:
        report["failure_geometry"] = {}

    return report


def generate_summary(report):
    """Generate human-readable summary."""
    lines = ["# Noesis Tournament Summary\n"]
    meta = report["run_metadata"]
    lines.append(f"**Cycles:** {meta['total_cycles']}")
    lines.append(f"**Chains tested:** {meta['total_chains_tested']}")
    lines.append(f"**Cracks found:** {meta['total_cracks']}")
    lines.append(f"**Runtime:** {meta['elapsed_hours']:.1f} hours\n")

    lines.append("## Strategy Leaderboard\n")
    lines.append("| Strategy | Cracks/Cycle | Total Cracks | Allocation |")
    lines.append("|----------|-------------|--------------|------------|")
    for s in report["strategy_leaderboard"]:
        lines.append(f"| {s['name']} | {s['cracks_per_cycle']:.4f} | {s['total_cracks']} | {s['allocation']:.2f} |")

    me = report.get("map_elites", {})
    lines.append(f"\n## MAP-Elites\n")
    lines.append(f"- Cells filled: {me.get('cells_filled', 0)}/{me.get('total_cells', 64)}")
    lines.append(f"- QD Score: {me.get('qd_score', 0):.3f}")

    fg = report.get("failure_geometry", {})
    if fg:
        lines.append("\n## Failure Geometry\n")
        for mode, count in fg.items():
            lines.append(f"- {mode}: {count}")

    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Noesis Daemon — Continuous Exploration")
    parser.add_argument("--hours", type=float, default=30.0, help="Maximum runtime in hours")
    parser.add_argument("--batch-size", type=int, default=100, help="Chains per cycle")
    parser.add_argument("--threshold", type=float, default=0.5, help="Quality threshold for cracks")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--report", action="store_true", help="Print latest report and exit")
    args = parser.parse_args()

    if args.report:
        if REPORT_PATH.exists():
            with open(REPORT_PATH) as f:
                report = json.load(f)
            print(json.dumps(report, indent=2, default=str))
        else:
            print("No report found. Run the daemon first.")
        return

    run_daemon(
        max_hours=args.hours,
        batch_size=args.batch_size,
        crack_threshold=args.threshold,
        resume=args.resume,
    )


if __name__ == "__main__":
    mp.freeze_support()  # Required for Windows
    main()
