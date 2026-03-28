"""
Poros — The Concept Explorer

Closed-loop exploration of mathematical organism compositions.
Finds chains that produce emergent value. Stores everything.
Measures exploration velocity.

Storage architecture:
  - Organisms: Python files, loaded once at startup
  - Interaction results: numpy memory-mapped arrays (disk-backed, RAM-speed access)
  - Lattice graph: SQLite for persistence, numpy adjacency for fast traversal
  - VRAM: optional GPU acceleration via CuPy for tensor operations

The exploration loop:
  1. Enumerate valid chains (type-compatible operation sequences)
  2. Execute chains on test inputs
  3. Score: novelty, complementarity, resonance, execution success
  4. Store ALL results (even near-zero scores)
  5. Update the Lattice graph with discoveries
  6. Measure exploration velocity (cracks per cycle)
  7. Use velocity feedback to steer next exploration
  8. Loop forever

Usage:
    python explorer.py                    # Run exploration loop
    python explorer.py --cycles 100       # Fixed number of cycles
    python explorer.py --siege "topology"  # Target a specific concept
    python explorer.py --gpu              # Use VRAM for tensor ops
"""

import argparse
import hashlib
import json
import logging
import os
import sqlite3
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

ORGANISMS_DIR = Path(__file__).resolve().parent
DB_PATH = ORGANISMS_DIR / "lattice.db"
TENSOR_CACHE_DIR = ORGANISMS_DIR / "tensor_cache"
TENSOR_CACHE_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [POROS] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("poros")


# ---------------------------------------------------------------------------
# Lattice Database (persistent graph)
# ---------------------------------------------------------------------------

def init_lattice_db():
    """Initialize the SQLite lattice database."""
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA journal_mode=WAL")

    # Organisms (nodes)
    db.execute("""
        CREATE TABLE IF NOT EXISTS organisms (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            n_operations INTEGER,
            operation_names TEXT,
            loaded_at TEXT
        )
    """)

    # Composition results (every attempt, even failures)
    db.execute("""
        CREATE TABLE IF NOT EXISTS compositions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_key TEXT NOT NULL,
            chain_steps TEXT NOT NULL,
            chain_length INTEGER NOT NULL,
            executed INTEGER NOT NULL,
            score_novelty REAL DEFAULT 0.0,
            score_complementarity REAL DEFAULT 0.0,
            score_resonance REAL DEFAULT 0.0,
            score_combined REAL DEFAULT 0.0,
            output_type TEXT,
            output_hash TEXT,
            output_summary TEXT,
            error_message TEXT,
            execution_time_us INTEGER,
            cycle_number INTEGER,
            created_at TEXT NOT NULL,
            UNIQUE(chain_key)
        )
    """)

    # Discovered edges (interfaces between organisms)
    db.execute("""
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organism_a TEXT NOT NULL,
            organism_b TEXT NOT NULL,
            interface_type TEXT,
            score REAL DEFAULT 0.0,
            n_successful_chains INTEGER DEFAULT 0,
            n_failed_chains INTEGER DEFAULT 0,
            best_chain TEXT,
            discovered_at TEXT,
            UNIQUE(organism_a, organism_b, interface_type)
        )
    """)

    # Exploration velocity tracking
    db.execute("""
        CREATE TABLE IF NOT EXISTS velocity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle_number INTEGER,
            chains_tested INTEGER,
            chains_executed INTEGER,
            cracks_found INTEGER,
            velocity REAL,
            cumulative_cracks INTEGER,
            timestamp TEXT
        )
    """)

    db.commit()
    return db


# ---------------------------------------------------------------------------
# Organism Loading
# ---------------------------------------------------------------------------

def load_all_organisms():
    """Load all organism classes from the organisms directory."""
    organisms = {}

    # Import all organisms via package import
    parent_dir = str(ORGANISMS_DIR.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        from organisms import ALL_ORGANISMS
        for org_class in ALL_ORGANISMS:
            try:
                org = org_class()
                organisms[org.name] = org
            except Exception as e:
                log.warning(f"Failed to instantiate {org_class}: {e}")
    except ImportError as ie:
        log.warning(f"Could not import ALL_ORGANISMS: {ie}")
        # Fallback: import package then scan attributes
        try:
            import organisms as org_pkg
            for attr_name in dir(org_pkg):
                attr = getattr(org_pkg, attr_name)
                if isinstance(attr, type) and hasattr(attr, 'operations') and attr_name != 'MathematicalOrganism':
                    try:
                        org = attr()
                        organisms[org.name] = org
                    except Exception as e:
                        log.warning(f"Failed to instantiate {attr_name}: {e}")
        except Exception as e2:
            log.warning(f"Fallback import also failed: {e2}")

    log.info(f"Loaded {len(organisms)} organisms with "
             f"{sum(len(o.operations) for o in organisms.values())} total operations")
    return organisms


# ---------------------------------------------------------------------------
# Chain Discovery (type-compatible operation sequences)
# ---------------------------------------------------------------------------

def discover_chains(organisms, max_length=3, target=None):
    """
    Find all type-compatible operation chains across organisms.

    A chain is valid if output_type of step N is compatible with
    input_type of step N+1, and at least 2 different organisms are used.

    If target is specified, all chains must include that organism.
    """
    # Build operation index: (organism_name, op_name) → (input_type, output_type)
    op_index = []
    for org_name, org in organisms.items():
        for op_name, op_data in org.operations.items():
            op_index.append({
                "organism": org_name,
                "operation": op_name,
                "input_type": op_data.get("input_type", "any"),
                "output_type": op_data.get("output_type", "any"),
            })

    def types_compatible(out_type, in_type):
        """Check if output type can feed into input type."""
        if out_type == "any" or in_type == "any":
            return True
        if out_type == in_type:
            return True
        # Flexible matching: numeric types are interchangeable
        numeric = {"scalar", "real", "integer", "float", "number", "complex_value"}
        if out_type in numeric and in_type in numeric:
            return True
        # Array types are interchangeable
        array_types = {"array", "vector", "timeseries", "sequence", "list", "distribution",
                       "probability_distribution", "population_vector", "observation_vector",
                       "prime_list", "coordinate_list"}
        if out_type in array_types and in_type in array_types:
            return True
        # Matrix types
        matrix_types = {"matrix", "adjacency_matrix", "distance_matrix", "joint_distribution"}
        if out_type in matrix_types and in_type in matrix_types:
            return True
        return False

    # Generate 2-step chains
    chains = []
    for op1 in op_index:
        for op2 in op_index:
            if op1["organism"] == op2["organism"]:
                continue  # Must cross organisms
            if target and target not in (op1["organism"], op2["organism"]):
                continue
            if types_compatible(op1["output_type"], op2["input_type"]):
                chain = [
                    (op1["organism"], op1["operation"]),
                    (op2["organism"], op2["operation"]),
                ]
                chains.append(chain)

    # Generate 3-step chains (if requested)
    if max_length >= 3:
        for op1 in op_index:
            for op2 in op_index:
                if op1["organism"] == op2["organism"]:
                    continue
                if not types_compatible(op1["output_type"], op2["input_type"]):
                    continue
                for op3 in op_index:
                    if op3["organism"] in (op1["organism"], op2["organism"]):
                        continue  # Must use 3 different organisms
                    if target and target not in (op1["organism"], op2["organism"], op3["organism"]):
                        continue
                    if types_compatible(op2["output_type"], op3["input_type"]):
                        chain = [
                            (op1["organism"], op1["operation"]),
                            (op2["organism"], op2["operation"]),
                            (op3["organism"], op3["operation"]),
                        ]
                        chains.append(chain)

    log.info(f"Discovered {len(chains)} valid chains "
             f"(max_length={max_length}, target={target or 'any'})")
    return chains


# ---------------------------------------------------------------------------
# Test Inputs (seed data for chain execution)
# ---------------------------------------------------------------------------

def generate_test_inputs():
    """Generate diverse test inputs for chain execution."""
    rng = np.random.RandomState(42)
    return {
        "scalar": 42.0,
        "integer": 100,
        "real": 3.14159,
        "number": 2.718,
        "float": 0.5,
        "array": rng.randn(50),
        "vector": rng.randn(20),
        "timeseries": np.sin(np.linspace(0, 4 * np.pi, 200)) + 0.1 * rng.randn(200),
        "sequence": np.arange(1, 51, dtype=float),
        "list": list(range(2, 52)),
        "distribution": np.abs(rng.randn(20)) / np.abs(rng.randn(20)).sum(),
        "probability_distribution": np.array([0.1, 0.2, 0.3, 0.25, 0.15]),
        "population_vector": rng.randn(10, 5),
        "observation_vector": rng.randn(30),
        "prime_list": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
        "coordinate_list": [(rng.randint(0, 10), rng.randint(0, 10)) for _ in range(20)],
        "matrix": rng.randn(10, 10),
        "adjacency_matrix": (rng.rand(10, 10) > 0.7).astype(float),
        "distance_matrix": np.abs(rng.randn(10, 10)),
        "joint_distribution": np.abs(rng.randn(5, 5)),
        "integer_tuple": (12, 8),
        "modular_params": (3, 100, 7),  # base, exp, mod
        "geometric_params": 10.0,
        "simplicial_counts": (10, 15, 5),  # vertices, edges, faces
        "complex_value": 2.0,  # for zeta function input
        "factorization": {2: 3, 3: 1, 5: 2},
        "lattice_structure": np.array([[1, 0], [0, 1]]),
        "any": rng.randn(20),
    }


# ---------------------------------------------------------------------------
# Chain Execution
# ---------------------------------------------------------------------------

def execute_chain(chain, organisms, test_inputs, timeout_seconds=5):
    """
    Execute a chain of operations. Returns result dict.
    """
    import warnings
    chain_key = " -> ".join(f"{org}.{op}" for org, op in chain)

    # Find appropriate test input for first operation
    first_org, first_op = chain[0]
    first_op_data = organisms[first_org].operations[first_op]
    input_type = first_op_data.get("input_type", "any")
    data = test_inputs.get(input_type, test_inputs["any"])

    start = time.perf_counter_ns()
    steps_completed = []

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for org_name, op_name in chain:
                org = organisms[org_name]
                data = org.execute(op_name, data)
                steps_completed.append(f"{org_name}.{op_name}")
                # Check timeout between steps
                elapsed_so_far = (time.perf_counter_ns() - start) / 1e9
                if elapsed_so_far > timeout_seconds:
                    raise TimeoutError(f"Chain exceeded {timeout_seconds}s after {len(steps_completed)} steps")

        elapsed_us = (time.perf_counter_ns() - start) // 1000

        # Compute output summary
        if isinstance(data, np.ndarray):
            summary = f"ndarray shape={data.shape} mean={float(np.mean(data)):.4f} std={float(np.std(data)):.4f}"
            out_hash = hashlib.md5(data.tobytes()).hexdigest()[:12]
        elif isinstance(data, (int, float, np.integer, np.floating)):
            summary = f"scalar={float(data):.6f}"
            out_hash = hashlib.md5(str(data).encode()).hexdigest()[:12]
        elif isinstance(data, (list, tuple)):
            summary = f"list len={len(data)}"
            out_hash = hashlib.md5(str(data)[:1000].encode()).hexdigest()[:12]
        elif isinstance(data, dict):
            summary = f"dict keys={list(data.keys())[:5]}"
            out_hash = hashlib.md5(json.dumps(data, default=str)[:1000].encode()).hexdigest()[:12]
        else:
            summary = f"type={type(data).__name__}"
            out_hash = hashlib.md5(str(data)[:1000].encode()).hexdigest()[:12]

        return {
            "chain_key": chain_key,
            "chain_steps": chain,
            "executed": True,
            "output": data,
            "output_type": type(data).__name__,
            "output_hash": out_hash,
            "output_summary": summary,
            "execution_time_us": elapsed_us,
            "error": None,
        }

    except Exception as e:
        elapsed_us = (time.perf_counter_ns() - start) // 1000
        return {
            "chain_key": chain_key,
            "chain_steps": chain,
            "executed": False,
            "output": None,
            "output_type": None,
            "output_hash": None,
            "output_summary": None,
            "execution_time_us": elapsed_us,
            "error": f"{type(e).__name__}: {str(e)[:200]}",
        }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_result(result, all_results_so_far):
    """
    Score a composition result. Returns dict of scores.

    Novelty: is this output different from everything we've seen?
    Complementarity: did the chain use diverse organisms?
    Resonance: is the output structured (not noise)?
    Combined: weighted sum.
    """
    if not result["executed"]:
        return {"novelty": 0.0, "complementarity": 0.0, "resonance": 0.0, "combined": 0.0}

    # Novelty: hash uniqueness among all results
    existing_hashes = {r.get("output_hash") for r in all_results_so_far if r.get("output_hash")}
    novelty = 1.0 if result["output_hash"] not in existing_hashes else 0.1

    # Complementarity: how many different organisms in the chain?
    orgs_used = set(org for org, _ in result["chain_steps"])
    complementarity = len(orgs_used) / 3.0  # Normalize: 3 organisms = 1.0

    # Resonance: is the output structured?
    resonance = 0.0
    output = result["output"]
    if isinstance(output, np.ndarray):
        if output.size > 1 and np.std(output) > 1e-10:
            # Not constant — has structure
            resonance = min(1.0, np.std(output) / (np.mean(np.abs(output)) + 1e-10))
            # Check for NaN/inf — penalize
            if np.any(np.isnan(output)) or np.any(np.isinf(output)):
                resonance *= 0.1
    elif isinstance(output, (int, float, np.integer, np.floating)):
        if np.isfinite(output) and output != 0:
            resonance = 0.5  # Scalar, finite, non-zero — some value
    elif isinstance(output, (list, tuple, dict)):
        if len(output) > 0:
            resonance = 0.4  # Non-empty structure

    # Combined
    combined = 0.4 * novelty + 0.3 * complementarity + 0.3 * resonance

    return {
        "novelty": round(novelty, 4),
        "complementarity": round(complementarity, 4),
        "resonance": round(resonance, 4),
        "combined": round(combined, 4),
    }


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def store_result(db, result, scores, cycle_number):
    """Store a composition result in the lattice database."""
    chain_key = result["chain_key"]
    chain_steps_json = json.dumps(result["chain_steps"])

    try:
        db.execute("""
            INSERT OR IGNORE INTO compositions
            (chain_key, chain_steps, chain_length, executed,
             score_novelty, score_complementarity, score_resonance, score_combined,
             output_type, output_hash, output_summary, error_message,
             execution_time_us, cycle_number, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chain_key, chain_steps_json, len(result["chain_steps"]),
            1 if result["executed"] else 0,
            scores["novelty"], scores["complementarity"],
            scores["resonance"], scores["combined"],
            result.get("output_type"), result.get("output_hash"),
            result.get("output_summary"), result.get("error"),
            result.get("execution_time_us", 0), cycle_number,
            datetime.now().isoformat(),
        ))
    except sqlite3.Error as e:
        log.warning(f"DB store failed for {chain_key}: {e}")


def update_edges(db, result, scores):
    """Update the lattice edges based on a successful composition."""
    if not result["executed"] or scores["combined"] < 0.01:
        return

    orgs = [org for org, _ in result["chain_steps"]]
    # Create edges between all pairs of organisms in the chain
    for i in range(len(orgs)):
        for j in range(i + 1, len(orgs)):
            try:
                db.execute("""
                    INSERT INTO edges (organism_a, organism_b, interface_type, score,
                                      n_successful_chains, best_chain, discovered_at)
                    VALUES (?, ?, ?, ?, 1, ?, ?)
                    ON CONFLICT(organism_a, organism_b, interface_type)
                    DO UPDATE SET
                        score = MAX(score, ?),
                        n_successful_chains = n_successful_chains + 1,
                        best_chain = CASE WHEN ? > score THEN ? ELSE best_chain END
                """, (
                    orgs[i], orgs[j], result.get("output_type", "unknown"),
                    scores["combined"], result["chain_key"], datetime.now().isoformat(),
                    scores["combined"], scores["combined"], result["chain_key"],
                ))
            except sqlite3.Error:
                pass


def log_velocity(db, cycle_number, tested, executed, cracks, cumulative):
    """Log exploration velocity for this cycle."""
    velocity = cracks / max(tested, 1)
    db.execute("""
        INSERT INTO velocity_log (cycle_number, chains_tested, chains_executed,
                                  cracks_found, velocity, cumulative_cracks, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cycle_number, tested, executed, cracks, velocity, cumulative, datetime.now().isoformat()))


# ---------------------------------------------------------------------------
# The Exploration Loop
# ---------------------------------------------------------------------------

def explore(organisms, n_cycles=None, target=None, batch_size=500,
            crack_threshold=0.3, use_gpu=False):
    """
    Main exploration loop. Discovers, executes, scores, and stores
    compositions. Measures exploration velocity. Runs until stopped
    or n_cycles reached.
    """
    db = init_lattice_db()
    test_inputs = generate_test_inputs()

    # Register organisms
    for name, org in organisms.items():
        op_names = json.dumps(list(org.operations.keys()))
        db.execute("""
            INSERT OR REPLACE INTO organisms (name, n_operations, operation_names, loaded_at)
            VALUES (?, ?, ?, ?)
        """, (name, len(org.operations), op_names, datetime.now().isoformat()))
    db.commit()

    # Discover all valid chains
    all_chains = discover_chains(organisms, max_length=3, target=target)

    # Check which chains have already been tested
    tested_keys = set()
    rows = db.execute("SELECT chain_key FROM compositions").fetchall()
    for row in rows:
        tested_keys.add(row[0])

    untested = [c for c in all_chains
                if " -> ".join(f"{org}.{op}" for org, op in c) not in tested_keys]
    log.info(f"Chains: {len(all_chains)} total, {len(tested_keys)} already tested, "
             f"{len(untested)} remaining")

    if not untested:
        log.info("All chains tested! Consider adding new organisms or increasing max_length.")
        # Could still re-test with different inputs
        untested = all_chains

    # Optional GPU acceleration
    if use_gpu:
        try:
            import cupy as cp
            log.info(f"GPU acceleration enabled: {cp.cuda.runtime.getDeviceCount()} device(s)")
        except ImportError:
            log.warning("CuPy not installed — falling back to CPU")
            use_gpu = False

    # Exploration loop
    cycle = 0
    cumulative_cracks = db.execute(
        "SELECT COUNT(*) FROM compositions WHERE score_combined >= ?", [crack_threshold]
    ).fetchone()[0]
    all_results = []

    log.info("=" * 60)
    log.info("POROS — EXPLORATION LOOP STARTING")
    log.info(f"  Organisms: {len(organisms)}")
    log.info(f"  Operations: {sum(len(o.operations) for o in organisms.values())}")
    log.info(f"  Valid chains: {len(all_chains)}")
    log.info(f"  Untested: {len(untested)}")
    log.info(f"  Crack threshold: {crack_threshold}")
    log.info(f"  Batch size: {batch_size}")
    log.info(f"  GPU: {'enabled' if use_gpu else 'disabled'}")
    log.info("=" * 60)

    try:
        while True:
            cycle += 1
            if n_cycles and cycle > n_cycles:
                break

            # Select batch for this cycle
            if len(untested) > 0:
                batch = untested[:batch_size]
                untested = untested[batch_size:]
            else:
                # All tested — resample with different random inputs
                rng = np.random.RandomState(cycle)
                indices = rng.choice(len(all_chains), min(batch_size, len(all_chains)), replace=False)
                batch = [all_chains[i] for i in indices]
                test_inputs = generate_test_inputs()  # Fresh random inputs

            cycle_start = time.time()
            cycle_cracks = 0
            cycle_executed = 0

            for chain in batch:
                result = execute_chain(chain, organisms, test_inputs)
                scores = score_result(result, all_results)

                store_result(db, result, scores, cycle)

                if result["executed"]:
                    cycle_executed += 1
                    update_edges(db, result, scores)

                if scores["combined"] >= crack_threshold:
                    cycle_cracks += 1
                    cumulative_cracks += 1
                    log.info(f"  CRACK: {result['chain_key']} "
                             f"(score={scores['combined']:.3f}, "
                             f"novelty={scores['novelty']:.2f}, "
                             f"resonance={scores['resonance']:.2f})")

                all_results.append(result)

            # Log velocity
            log_velocity(db, cycle, len(batch), cycle_executed, cycle_cracks, cumulative_cracks)
            db.commit()

            elapsed = time.time() - cycle_start
            velocity = cycle_cracks / max(len(batch), 1)
            exec_rate = cycle_executed / max(len(batch), 1)

            log.info(f"Cycle {cycle}: {len(batch)} tested, {cycle_executed} executed ({exec_rate:.0%}), "
                     f"{cycle_cracks} cracks, velocity={velocity:.3f}, "
                     f"cumulative={cumulative_cracks}, "
                     f"remaining={len(untested)}, "
                     f"{elapsed:.1f}s")

            if len(untested) == 0 and n_cycles is None:
                log.info("All chains exhausted. Stopping.")
                break

    except KeyboardInterrupt:
        log.info("Exploration interrupted (Ctrl+C)")

    # Final report
    db.commit()
    total_compositions = db.execute("SELECT COUNT(*) FROM compositions").fetchone()[0]
    total_executed = db.execute("SELECT COUNT(*) FROM compositions WHERE executed = 1").fetchone()[0]
    total_cracks = db.execute(
        "SELECT COUNT(*) FROM compositions WHERE score_combined >= ?", [crack_threshold]
    ).fetchone()[0]
    total_edges = db.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

    log.info("=" * 60)
    log.info("EXPLORATION COMPLETE")
    log.info(f"  Total compositions tested: {total_compositions}")
    log.info(f"  Successfully executed: {total_executed} ({total_executed/max(total_compositions,1):.0%})")
    log.info(f"  Cracks found: {total_cracks} ({total_cracks/max(total_compositions,1):.0%})")
    log.info(f"  Lattice edges: {total_edges}")
    log.info(f"  Database: {DB_PATH}")
    log.info("=" * 60)

    # Show top 10 cracks
    top = db.execute("""
        SELECT chain_key, score_combined, score_novelty, score_resonance,
               output_summary, execution_time_us
        FROM compositions
        WHERE score_combined >= ?
        ORDER BY score_combined DESC
        LIMIT 10
    """, [crack_threshold]).fetchall()

    if top:
        log.info("\nTOP 10 CRACKS:")
        for i, (key, score, nov, res, summary, time_us) in enumerate(top, 1):
            log.info(f"  {i:2d}. [{score:.3f}] {key}")
            log.info(f"      novelty={nov:.2f} resonance={res:.2f} "
                     f"time={time_us}us output={summary}")

    db.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Poros — The Concept Explorer")
    parser.add_argument("--cycles", type=int, default=None,
                        help="Number of exploration cycles (default: until exhausted)")
    parser.add_argument("--siege", type=str, default=None,
                        help="Target a specific organism for focused exploration")
    parser.add_argument("--batch", type=int, default=500,
                        help="Chains per cycle (default: 500)")
    parser.add_argument("--threshold", type=float, default=0.3,
                        help="Minimum score to count as a crack (default: 0.3)")
    parser.add_argument("--gpu", action="store_true",
                        help="Use GPU for tensor operations")
    parser.add_argument("--status", action="store_true",
                        help="Show exploration status and exit")
    parser.add_argument("--tensor", action="store_true",
                        help="Use tensor navigator to find frontier, then explore top candidates")
    parser.add_argument("--tensor-top", type=int, default=100,
                        help="Number of top tensor candidates to explore (default: 100)")
    parser.add_argument("--tensor-rank", type=int, default=10,
                        help="TT decomposition rank (default: 10)")
    args = parser.parse_args()

    if args.status:
        if not DB_PATH.exists():
            print("No exploration data yet. Run explorer.py first.")
            return
        db = sqlite3.connect(str(DB_PATH))
        total = db.execute("SELECT COUNT(*) FROM compositions").fetchone()[0]
        executed = db.execute("SELECT COUNT(*) FROM compositions WHERE executed=1").fetchone()[0]
        cracks = db.execute("SELECT COUNT(*) FROM compositions WHERE score_combined >= 0.3").fetchone()[0]
        edges = db.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        orgs = db.execute("SELECT COUNT(*) FROM organisms").fetchone()[0]
        print(f"Organisms: {orgs}")
        print(f"Compositions: {total} tested, {executed} executed, {cracks} cracks")
        print(f"Lattice edges: {edges}")

        # Velocity trend
        vel = db.execute("""
            SELECT cycle_number, velocity, cumulative_cracks
            FROM velocity_log ORDER BY cycle_number DESC LIMIT 5
        """).fetchall()
        if vel:
            print(f"\nRecent velocity:")
            for cn, v, cc in reversed(vel):
                print(f"  Cycle {cn}: velocity={v:.3f}, cu