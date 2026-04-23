"""
map_elites.py — MAP-Elites Archive for Apollo v2c.

Grid-based archive replacing random replacement. Each cell holds
the most novel organism with that (depth, category_count) profile.

Axes:
  - DAG depth (primitive count): bins [1,2,3,4,5,6,7+] -> 7 bins
  - Number of unique primitive categories: bins [1,2,3,4,5+] -> 5 bins
  - Grid: 7 x 5 = 35 cells

Integrates with existing k-NN novelty scoring — archive entries
still used for distance computation.
"""

import numpy as np


# Primitive category mapping — used to count unique categories
PRIMITIVE_CATEGORIES = {
    # Logic / formal reasoning
    'solve_sat': 'logic', 'propositional_check': 'logic',
    'modal_logic': 'logic', 'temporal_logic': 'logic',
    'deontic_check': 'logic', 'argument_validity': 'logic',
    # Probabilistic
    'bayesian_update': 'prob', 'probability_chain': 'prob',
    'expected_utility': 'prob', 'entropy': 'prob',
    'info_gain': 'prob',
    # Causal
    'causal_graph': 'causal', 'counterfactual': 'causal',
    'causal_strength': 'causal',
    # Constraint
    'constraint_propagation': 'constraint', 'graph_coloring': 'constraint',
    'planning_strips': 'constraint',
    # Meta / linguistic
    'semantic_similarity': 'meta', 'analogy_mapper': 'meta',
    'pattern_match': 'meta', 'decision_matrix': 'meta',
    'ensemble_vote': 'meta', 'game_theory': 'meta',
    'abductive_reason': 'meta',
}


def _get_depth_bin(primitive_count):
    """Map primitive count to bin index 0-6."""
    return min(primitive_count - 1, 6) if primitive_count >= 1 else 0


def _get_category_bin(organism):
    """Map unique category count to bin index 0-4."""
    categories = set()
    for pc in organism.primitive_sequence:
        cat = PRIMITIVE_CATEGORIES.get(pc.primitive_name, 'other')
        categories.add(cat)
    n_cats = len(categories)
    return min(n_cats - 1, 4) if n_cats >= 1 else 0


class MAPElitesArchive:
    """Grid-based quality-diversity archive.

    Each cell holds (organism_signature, novelty_score, organism_info).
    New entry replaces incumbent only if it has higher novelty score.
    """

    def __init__(self, depth_bins=7, category_bins=5):
        self.depth_bins = depth_bins
        self.category_bins = category_bins
        # Grid: each cell holds (signature, novelty_score, info_dict) or None
        self.grid = [[None for _ in range(category_bins)]
                     for _ in range(depth_bins)]
        self._signatures = []  # flat list for k-NN queries

    def get_cell(self, organism):
        """Get (depth_bin, category_bin) for an organism."""
        d = _get_depth_bin(organism.primitive_count)
        c = _get_category_bin(organism)
        return d, c

    def try_insert(self, organism, signature, novelty_score, info=None):
        """Try to insert an organism into the archive.

        Args:
            organism: Organism instance
            signature: behavioral signature (np.ndarray)
            novelty_score: float novelty score
            info: optional dict with extra info (genome_id, fitness, etc.)

        Returns:
            True if inserted (new cell or higher novelty), False otherwise
        """
        d, c = self.get_cell(organism)

        current = self.grid[d][c]
        if current is None:
            # Empty cell — insert
            self.grid[d][c] = (signature.copy(), novelty_score, info or {})
            self._rebuild_signatures()
            return True
        else:
            # Replace if new organism has higher novelty
            _, old_novelty, _ = current
            if novelty_score > old_novelty:
                self.grid[d][c] = (signature.copy(), novelty_score, info or {})
                self._rebuild_signatures()
                return True
        return False

    def _rebuild_signatures(self):
        """Rebuild flat signature list from grid."""
        self._signatures = []
        for row in self.grid:
            for cell in row:
                if cell is not None:
                    self._signatures.append(cell[0])

    def get_all_signatures(self):
        """Return all signatures in the archive (for k-NN)."""
        return list(self._signatures)

    @property
    def size(self):
        """Number of occupied cells."""
        count = 0
        for row in self.grid:
            for cell in row:
                if cell is not None:
                    count += 1
        return count

    @property
    def max_size(self):
        """Total grid capacity."""
        return self.depth_bins * self.category_bins

    def coverage(self):
        """Fraction of grid cells occupied."""
        return self.size / self.max_size

    def get_stats(self):
        """Return archive statistics for logging."""
        novelties = []
        for row in self.grid:
            for cell in row:
                if cell is not None:
                    novelties.append(cell[1])
        return {
            "size": self.size,
            "max_size": self.max_size,
            "coverage": self.coverage(),
            "mean_novelty": float(np.mean(novelties)) if novelties else 0.0,
            "min_novelty": float(np.min(novelties)) if novelties else 0.0,
            "max_novelty": float(np.max(novelties)) if novelties else 0.0,
        }

    def get_occupancy_map(self):
        """Return a 2D array showing which cells are occupied."""
        occ = np.zeros((self.depth_bins, self.category_bins), dtype=int)
        for d in range(self.depth_bins):
            for c in range(self.category_bins):
                if self.grid[d][c] is not None:
                    occ[d][c] = 1
        return occ
