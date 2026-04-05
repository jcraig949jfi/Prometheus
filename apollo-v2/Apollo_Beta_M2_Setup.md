# Apollo-v2 (Beta) — M2 Setup Guide

## Overview

Apollo-v2 runs on M2 (i7-14700F, 20 cores, RTX GPU with 16GB+ VRAM).
It is a **completely independent** Apollo instance with its own codebase,
config, population, and checkpoints. It does NOT share code or state with
M1's Apollo (F:\Prometheus\apollo\).

The only shared resource is the **atom pool** — a directory on a network-
accessible path where both M1 and M2 deposit and withdraw verified atoms.

---

## Step 1: Create the Directory Structure

Run this on M2:

```bat
@echo off
echo Creating Apollo-v2 directory structure...

mkdir C:\Prometheus\apollo-v2
mkdir C:\Prometheus\apollo-v2\src
mkdir C:\Prometheus\apollo-v2\configs
mkdir C:\Prometheus\apollo-v2\checkpoints
mkdir C:\Prometheus\apollo-v2\logs
mkdir C:\Prometheus\apollo-v2\population
mkdir C:\Prometheus\apollo-v2\archive
mkdir C:\Prometheus\apollo-v2\graveyard
mkdir C:\Prometheus\apollo-v2\reports
mkdir C:\Prometheus\apollo-v2\gene_library
mkdir C:\Prometheus\apollo-v2\scripts

echo Done. Now copy src files from M1.
```

## Step 2: Copy Source Code from M1

Copy these from M1's `F:\Prometheus\apollo\src\` to M2's `C:\Prometheus\apollo-v2\src\`:

```
apollo.py           ← main evolutionary loop
genome.py            ← organism representation
compiler.py          ← compile/validate organisms
sandbox.py           ← safe execution with timeout
task_manager.py      ← rolling curriculum
fitness.py           ← multi-objective evaluation
novelty.py           ← behavioral signatures + archive
selection.py         ← NSGA-II
mutation.py          ← AST mutation operators
mutation_llm.py      ← LLM-assisted mutation (if exists)
logger.py            ← JSONL lineage tracking
checkpointer.py      ← population snapshots
```

Also copy:
- `forge_primitives.py` → wherever Apollo imports it from (check M1's imports)
- Gem source files (M1's `agents/hephaestus/forge_v7/` or wherever gems live)
- Trap generator files (M1's battery)

**IMPORTANT:** Do NOT copy M1's checkpoints, logs, population, or archive.
Beta starts fresh with its own evolutionary trajectory.

---

## Step 3: Beta Configuration

Save this as `C:\Prometheus\apollo-v2\configs\config.yaml`:

```yaml
# ============================================================
# APOLLO-BETA — Breadth-First Generalist
# ============================================================
# Strategy: Wide, shallow compositions targeting maximum
# category coverage. Many primitives in parallel branches
# with majority-vote integration. Optimizes for solving the
# MOST problem types, not solving any one deeply.
# ============================================================

instance:
  island_id: "beta"
  instance_name: "Apollo-Beta (Breadth Generalist)"

# --- Population ---
population:
  size: 50
  offspring_per_gen: 50
  max_generations: 50000

# --- Strategy (THIS IS WHAT DIFFERS FROM ALPHA) ---
strategy:
  # Breadth: use more primitives per organism, wired in parallel
  min_primitives: 5
  max_primitives: 12
  preferred_depth: shallow         # parallel branches > deep chains
  composition_style: parallel      # majority-vote / ensemble integration

  # Selection pressure: maximize category coverage
  primary_pressure: coverage       # how many categories solved > how well
  coverage_weight: 0.4             # boost coverage in fitness
  accuracy_weight: 0.3             # accuracy matters but less than Alpha
  ablation_weight: 0.2             # same ablation gate as Alpha
  diversity_weight: 0.1            # novelty search

  # Mutation bias: favor wiring changes over route changes
  mutation_rates:
    route: 0.20                    # Alpha uses 0.40
    parameter: 0.25                # same as Alpha
    wiring: 0.35                   # Alpha uses 0.20 — Beta rewires more
    primitive_swap: 0.20           # Alpha uses 0.15 — Beta explores more

# --- LLM Mutation ---
llm:
  model: "Qwen/Qwen2.5-Coder-7B-Instruct"
  quantization: "8bit"
  device: "cuda:0"
  max_new_tokens: 2048
  temperature: 0.8                 # slightly higher than Alpha for more exploration

# --- Fitness (6 dimensions, NSGA-II) ---
fitness:
  dimensions:
    - name: accuracy
      type: margin_over_ncd
      weight: 1.0
    - name: calibration
      type: brier_score
      weight: 1.0
    - name: ablation_delta
      type: min_per_primitive
      threshold: 0.20              # same hard gate as Alpha
      weight: 1.0
    - name: generalization
      type: held_out_accuracy
      weight: 1.0
    - name: diversity
      type: novelty_distance
      weight: 1.0
    - name: coverage
      type: categories_solved      # Beta-specific: count of categories with >50% accuracy
      weight: 1.5                   # boosted — this is Beta's specialty

# --- Ablation Gate ---
ablation:
  min_delta: 0.20                  # per-primitive minimum
  test_interval: 10                # full ablation every 10 gens (top 20)
  deep_test_interval: 50           # full population ablation every 50 gens

# --- NCD Counterpressure ---
ncd:
  discrimination_threshold: 3      # must differ from NCD on 3/10 reference tasks
  decay_schedule:
    gen_0: 1.0                     # full NCD weight
    gen_100: 0.5                   # half NCD
    gen_500: 0.0                   # zero NCD — must reason without it

# --- Task Curriculum ---
tasks:
  reference_count: 50              # fixed, never changes
  evolution_count: 100             # rotates
  held_out_count: 50               # generalization test
  rotation_interval: 50            # rotate 10 tasks every 50 gens
  capability_step_interval: 500    # novel task type test

# --- Novelty Search ---
novelty:
  k_nearest: 15
  archive_max: 500
  archive_threshold: 0.3

# --- Warmup / Graduation ---
schedule:
  warmup_until: 50                 # diversity-only
  accuracy_activates: 50
  ablation_activates: 100
  full_suite_at: 200

# --- Operational ---
operational:
  checkpoint_interval: 10
  report_interval: 50
  dashboard_interval: 5            # console output every 5 gens
  sandbox_timeout: 0.5
  sandbox_max_memory_mb: 256

# --- Paths ---
paths:
  project_root: "C:\\Prometheus"
  instance_root: "C:\\Prometheus\\apollo-v2"
  checkpoint_dir: "C:\\Prometheus\\apollo-v2\\checkpoints"
  log_dir: "C:\\Prometheus\\apollo-v2\\logs"
  population_dir: "C:\\Prometheus\\apollo-v2\\population"
  archive_dir: "C:\\Prometheus\\apollo-v2\\archive"
  graveyard_dir: "C:\\Prometheus\\apollo-v2\\graveyard"
  report_dir: "C:\\Prometheus\\apollo-v2\\reports"
  gene_library_dir: "C:\\Prometheus\\apollo-v2\\gene_library"

  # Forge primitives and gems — copy these locally or point to shared location
  forge_primitives: "C:\\Prometheus\\forge\\forge_primitives.py"
  gem_source_dir: "C:\\Prometheus\\agents\\hephaestus\\forge_v7"

  # SHARED ATOM POOL — both M1 and M2 read/write here
  # Option A: Network share (if M1 and M2 can both see it)
  # shared_pool: "\\\\SERVERNAME\\shared\\apollo_pool"
  #
  # Option B: Local on M2, manually sync to M1
  # shared_pool: "C:\\Prometheus\\apollo-v2\\shared_pool"
  #
  # Option C: Shared drive letter mapped on both machines
  # shared_pool: "S:\\apollo_pool"
  #
  # SET THIS BEFORE LAUNCHING:
  shared_pool: "C:\\Prometheus\\apollo_shared_pool"
```

---

## Step 4: Shared Pool Setup

Create the shared pool directory (on whichever drive both machines can access):

```bat
@echo off
echo Creating shared atom pool...

mkdir C:\Prometheus\apollo_shared_pool
mkdir C:\Prometheus\apollo_shared_pool\atoms
mkdir C:\Prometheus\apollo_shared_pool\challenges
mkdir C:\Prometheus\apollo_shared_pool\organisms
mkdir C:\Prometheus\apollo_shared_pool\leaderboard
mkdir C:\Prometheus\apollo_shared_pool\signatures

echo Done.
```

If M1 and M2 share a network drive, create it there instead and update
both configs to point to the same network path.

If they don't share a drive yet, start with local pools on each machine
and add the sync later. The atom pool protocol is append-only JSONL —
syncing is just copying new lines.

---

## Step 5: Shared Pool Protocol

Add this module to `C:\Prometheus\apollo-v2\src\shared_pool.py`:

```python
"""
Shared Atom Pool — deposit and withdraw verified atoms.

Protocol:
- Atoms are deposited as append-only JSONL (one atom per line)
- Each atom has an island_id so instances can track provenance
- Withdrawal reads all atoms and filters by cross-instance flag
- Behavioral signatures cached as numpy array for fast distinctness check
- File locking: not needed. Append-only + read-tolerant-of-partial-lines.
"""

import json
import os
import time
import numpy as np
from pathlib import Path


class SharedPool:
    def __init__(self, pool_dir: str, island_id: str):
        self.pool_dir = Path(pool_dir)
        self.island_id = island_id
        self.atoms_file = self.pool_dir / "atoms" / "atoms.jsonl"
        self.signatures_file = self.pool_dir / "signatures" / "signatures.npy"
        self.sig_index_file = self.pool_dir / "signatures" / "sig_index.json"
        self._ensure_dirs()
        self._imported = set()  # track what we've already read

    def _ensure_dirs(self):
        for subdir in ["atoms", "challenges", "organisms", "leaderboard", "signatures"]:
            (self.pool_dir / subdir).mkdir(parents=True, exist_ok=True)

    def deposit_atom(self, atom: dict, signature: np.ndarray):
        """
        Deposit a verified atom to the shared pool.
        atom dict must contain: atom_id, island_id, primitive_name,
        ablation_delta, problem_types, generation, code
        """
        atom["island_id"] = self.island_id
        atom["deposited_at"] = time.time()

        # Append atom to JSONL (append mode, no locking needed)
        with open(self.atoms_file, "a") as f:
            f.write(json.dumps(atom) + "\n")

        # Update signature cache
        self._append_signature(atom["atom_id"], signature)

    def withdraw_atoms(self, exclude_own: bool = True, max_count: int = 50):
        """
        Read atoms from the pool. Optionally exclude own deposits.
        Returns list of atom dicts.
        """
        atoms = []
        if not self.atoms_file.exists():
            return atoms

        with open(self.atoms_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    atom = json.loads(line)
                    if exclude_own and atom.get("island_id") == self.island_id:
                        continue
                    atoms.append(atom)
                except json.JSONDecodeError:
                    continue  # tolerate partial writes

        return atoms[-max_count:]  # most recent

    def check_distinctness(self, new_signature: np.ndarray, threshold: float = 0.85):
        """
        Check if a new atom is distinct from all existing atoms in the pool.
        Returns True if distinct (max cosine similarity < threshold).
        """
        if not self.signatures_file.exists():
            return True

        existing = np.load(self.signatures_file)
        if len(existing) == 0:
            return True

        # Cosine similarity
        new_norm = new_signature / (np.linalg.norm(new_signature) + 1e-10)
        existing_norm = existing / (np.linalg.norm(existing, axis=1, keepdims=True) + 1e-10)
        similarities = existing_norm @ new_norm

        return float(np.max(similarities)) < threshold

    def _append_signature(self, atom_id: str, signature: np.ndarray):
        """Append a behavioral signature to the cached numpy array."""
        if self.signatures_file.exists():
            existing = np.load(self.signatures_file)
            updated = np.vstack([existing, signature.reshape(1, -1)])
        else:
            updated = signature.reshape(1, -1)
        np.save(self.signatures_file, updated)

        # Update index
        if self.sig_index_file.exists():
            with open(self.sig_index_file, "r") as f:
                index = json.load(f)
        else:
            index = {}
        index[atom_id] = len(updated) - 1
        with open(self.sig_index_file, "w") as f:
            json.dump(index, f)

    def deposit_organism(self, organism_data: dict, generation: int):
        """Deposit a top organism for other instances to inspect/compose."""
        filename = f"{self.island_id}_gen_{generation:06d}.jsonl"
        filepath = self.pool_dir / "organisms" / filename
        with open(filepath, "w") as f:
            f.write(json.dumps(organism_data) + "\n")

    def deposit_challenge(self, challenge: dict):
        """Deposit an adversarial challenge (for Gamma-type instances)."""
        filepath = self.pool_dir / "challenges" / "challenges.jsonl"
        with open(filepath, "a") as f:
            f.write(json.dumps(challenge) + "\n")

    def read_challenges(self, since_timestamp: float = 0):
        """Read adversarial challenges deposited by other instances."""
        filepath = self.pool_dir / "challenges" / "challenges.jsonl"
        if not filepath.exists():
            return []

        challenges = []
        with open(filepath, "r") as f:
            for line in f:
                try:
                    c = json.loads(line.strip())
                    if c.get("deposited_at", 0) > since_timestamp:
                        challenges.append(c)
                except (json.JSONDecodeError, ValueError):
                    continue
        return challenges

    def update_leaderboard(self, metrics: dict, generation: int):
        """Update this instance's entry in the leaderboard."""
        entry = {
            "island_id": self.island_id,
            "generation": generation,
            "timestamp": time.time(),
            **metrics
        }
        filepath = self.pool_dir / "leaderboard" / f"{self.island_id}.json"
        with open(filepath, "w") as f:
            json.dump(entry, f, indent=2)

    def read_leaderboard(self):
        """Read all instances' leaderboard entries."""
        lb_dir = self.pool_dir / "leaderboard"
        entries = {}
        for f in lb_dir.glob("*.json"):
            try:
                with open(f) as fh:
                    entries[f.stem] = json.load(fh)
            except (json.JSONDecodeError, ValueError):
                continue
        return entries

    def pool_stats(self):
        """Quick stats on the shared pool."""
        atom_count = 0
        if self.atoms_file.exists():
            with open(self.atoms_file) as f:
                atom_count = sum(1 for line in f if line.strip())

        sig_count = 0
        if self.signatures_file.exists():
            sig_count = len(np.load(self.signatures_file))

        return {
            "total_atoms": atom_count,
            "signatures_cached": sig_count,
            "leaderboard_entries": len(list(
                (self.pool_dir / "leaderboard").glob("*.json")
            ))
        }
```

---

## Step 6: Modifications to apollo.py for Multi-Instance Support

The main apollo.py needs small changes to support the shared pool.
These should be added WITHOUT breaking M1's existing code — use
feature flags so the same codebase works with or without a shared pool.

### 6.1 Load shared pool from config

```python
# In apollo.py bootstrap section:
shared_pool_path = config.get("paths", {}).get("shared_pool", None)
if shared_pool_path:
    from shared_pool import SharedPool
    pool = SharedPool(shared_pool_path, config["instance"]["island_id"])
    logger.info(f"Shared pool connected: {shared_pool_path}")
else:
    pool = None
    logger.info("No shared pool configured — running standalone")
```

### 6.2 Deposit verified atoms after ablation

```python
# After ablation testing (every ablation_test_interval gens):
if pool is not None:
    for organism in ablation_passed:
        for primitive in organism.load_bearing_primitives:
            # Compute behavioral signature
            sig = compute_behavioral_signature(organism, reference_tasks)
            # Check distinctness against pool
            if pool.check_distinctness(sig, threshold=0.85):
                atom = {
                    "atom_id": f"{island_id}_{generation}_{primitive.name}",
                    "primitive_name": primitive.name,
                    "ablation_delta": primitive.ablation_delta,
                    "problem_types": organism.solved_categories,
                    "generation": generation,
                    "code": primitive.source_code,
                    "organism_fitness": organism.fitness_vector,
                }
                pool.deposit_atom(atom, sig)
                logger.info(f"Deposited atom: {atom['atom_id']}")
```

### 6.3 Withdraw atoms for seeding (every N gens)

```python
# Every 100 generations, check for atoms from other instances:
if pool is not None and generation % 100 == 0:
    foreign_atoms = pool.withdraw_atoms(exclude_own=True, max_count=10)
    if foreign_atoms:
        # Create organisms using foreign atoms
        immigrants = create_organisms_from_atoms(foreign_atoms, max_count=5)
        # Replace worst 5 in population
        replace_worst(population, immigrants)
        logger.info(f"Imported {len(immigrants)} organisms from shared pool")
```

### 6.4 Deposit top organisms (for Delta-type composition)

```python
# Every 100 generations, export top 5:
if pool is not None and generation % 100 == 0:
    top5 = select_top_pareto(population, k=5)
    for org in top5:
        pool.deposit_organism(org.serialize(), generation)
```

### 6.5 Update leaderboard

```python
# Every 50 generations:
if pool is not None and generation % 50 == 0:
    metrics = {
        "atoms_deposited": atoms_deposited_count,
        "best_accuracy": best_organism.accuracy,
        "best_ablation": best_organism.min_ablation_delta,
        "categories_covered": len(categories_solved),
        "population_diversity": diversity_index,
    }
    pool.update_leaderboard(metrics, generation)
```

---

## Step 7: Launch Script

Save as `C:\Prometheus\apollo-v2\launch_beta.bat`:

```bat
@echo off
echo ============================================================
echo   APOLLO-BETA v2 — Breadth-First Generalist
echo   %date% %time%
echo   Machine: M2 (i7-14700F, 20 cores)
echo ============================================================

cd /d C:\Prometheus\apollo-v2

REM Preflight checks
echo [preflight] Checking GPU...
python -c "import torch; print(f'  GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_mem/1e9:.1f} GB)')"

echo [preflight] Checking config...
python -c "import yaml; c=yaml.safe_load(open('configs/config.yaml')); print(f'  Strategy: {c[\"instance\"][\"instance_name\"]}')"

echo [preflight] Checking shared pool...
python -c "import yaml; c=yaml.safe_load(open('configs/config.yaml')); from pathlib import Path; p=Path(c['paths']['shared_pool']); print(f'  Pool: {p} (exists={p.exists()})')"

echo [preflight] Checking forge_primitives...
python -c "import importlib.util, yaml; c=yaml.safe_load(open('configs/config.yaml')); spec=importlib.util.spec_from_file_location('fp',c['paths']['forge_primitives']); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); funcs=[x for x in dir(mod) if not x.startswith('_')]; print(f'  Primitives: {len(funcs)} functions')"

echo [preflight] All checks passed.
echo ============================================================

REM Launch
echo [launch] Starting Apollo-Beta (no generation limit)
echo   Logs:        C:\Prometheus\apollo-v2\logs\apollo_run.jsonl
echo   Checkpoints: C:\Prometheus\apollo-v2\checkpoints
echo   Shared Pool: (see config.yaml)
echo   Stop: Ctrl+C    Resume: launch_beta.bat
echo ============================================================

python src\apollo.py --config configs\config.yaml

echo ============================================================
echo   Apollo-Beta stopped. Resume with: launch_beta.bat
echo ============================================================
pause
```

---

## Step 8: Code Changes Required in apollo.py

For Beta to work with the config-driven approach, apollo.py needs to accept
a `--config` flag instead of hardcoded paths. The minimal changes:

```python
# At the top of apollo.py, add:
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Apollo Evolutionary Engine")
    parser.add_argument("--config", type=str, default="configs/config.yaml",
                        help="Path to instance config file")
    parser.add_argument("--instance-dir", type=str, default=None,
                        help="Override instance root directory")
    parser.add_argument("--island-id", type=str, default=None,
                        help="Override island ID")
    parser.add_argument("--max-gens", type=int, default=None,
                        help="Override max generations")
    parser.add_argument("--smoke-test", action="store_true",
                        help="Run 100 gens then stop")
    return parser.parse_args()

# In main():
args = parse_args()
config = load_config(args.config)

# Apply overrides
if args.instance_dir:
    config["paths"]["instance_root"] = args.instance_dir
if args.island_id:
    config["instance"]["island_id"] = args.island_id
if args.max_gens:
    config["population"]["max_generations"] = args.max_gens
if args.smoke_test:
    config["population"]["max_generations"] = 100
```

---

## Step 9: What NOT to Change on M1

M1's Apollo at F:\Prometheus\apollo\ keeps running exactly as-is.
Do NOT:
- Add shared pool code to M1 yet (it's mid-run)
- Change M1's config while it's running
- Copy M1's checkpoints to M2

When M1 reaches a natural checkpoint (every 10 gens), you can optionally:
- Add the shared_pool.py module to M1's src/
- Add shared_pool path to M1's config
- Restart M1 — it will resume from checkpoint AND connect to the pool

But this is optional. M1 and M2 can run independently at first. The shared
pool becomes valuable when both have organisms worth sharing (~gen 200+).

---

## Step 10: Verification Checklist Before Launch

- [ ] Directory structure created on M2
- [ ] Source code copied from M1 (src/ files only)
- [ ] forge_primitives.py accessible at configured path
- [ ] Gem source files accessible at configured path
- [ ] config.yaml reviewed and paths verified
- [ ] Shared pool directory created
- [ ] Qwen-Coder-7B downloads and loads on M2's GPU
- [ ] `python -c "import torch; print(torch.cuda.is_available())"` returns True
- [ ] launch_beta.bat runs preflight checks without errors
- [ ] 10-gen smoke test completes without crashes

---

## What Beta Does Differently from Alpha

| Dimension | Alpha (M1) | Beta (M2) |
|-----------|-----------|----------|
| Composition depth | 3-5 primitives, deep chains | 5-12 primitives, shallow parallel |
| Primary pressure | Accuracy (solve problems well) | Coverage (solve many categories) |
| Mutation bias | Route-heavy (40%) | Wiring-heavy (35%) |
| LLM temperature | 0.7 (focused) | 0.8 (exploratory) |
| Expected atoms | Deep-chain specialists | Universal breadth atoms |
| Fitness boost | Accuracy dimension | Coverage dimension (1.5x weight) |

Same primitives. Same ablation gate. Same trap battery. Different search strategy.
The atoms that survive in BOTH populations are the real periodic table entries.

---

## Timeline

| Step | Time | What |
|------|------|------|
| Day 1 AM | 1 hour | Create directories, copy code, write config |
| Day 1 AM | 30 min | Install dependencies, verify GPU, download Qwen if needed |
| Day 1 PM | 15 min | Run 10-gen smoke test |
| Day 1 PM | 5 min | Launch full run |
| Day 2 | — | Both M1 and M2 grinding. Check dashboards. |
| Day 3 | 30 min | Connect shared pool (add to both configs, restart both at checkpoint) |
| Day 4+ | — | Ecosystem running. Leaderboard tells the story. |

---

*Beta searches wide where Alpha searches deep.*
*The atoms that survive both are the real ones.*



Addendum
==================

Perfect. Update one line in the Beta config:
yamlshared_pool: "\\\\SKULLPORT\\skullport_shared\\apollo_pool"
Create the pool structure on the share:
batmkdir \\SKULLPORT\skullport_shared\apollo_pool
mkdir \\SKULLPORT\skullport_shared\apollo_pool\atoms
mkdir \\SKULLPORT\skullport_shared\apollo_pool\challenges
mkdir \\SKULLPORT\skullport_shared\apollo_pool\organisms
mkdir \\SKULLPORT\skullport_shared\apollo_pool\leaderboard
mkdir \\SKULLPORT\skullport_shared\apollo_pool\signatures
When M1's Alpha hits a clean checkpoint and you're ready to connect it, add the same line to M1's config:
yamlshared_pool: "\\\\SKULLPORT\\skullport_shared\\apollo_pool"
Both machines see the same pool. Alpha deposits deep-chain atoms. Beta deposits breadth atoms. The atoms that survive cross-instance testing are the real primitives.
Skullport is the shared atom marketplace. Fitting name — a hidden port where different factions trade what they've found in the dark.