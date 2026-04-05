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
