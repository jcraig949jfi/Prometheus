"""Kill tensor v0 — second Layer 2 primitive (Phase 1C ITER-41).

Per Erebos Doctrine v1.0 §"Layer 2 — cross-emission accumulator":
"Tensor operations over (generator x domain x invariant x
confusion_class)." This iteration ships the sparse 4D tensor over
exactly those axes -- the substrate's first navigable
representation of failure geometry.

## The four axes

  axis 0: plugin_id          (which generator)
  axis 1: domain             (mathematical domain)
  axis 2: invariant          (what was being probed)
  axis 3: kill_pattern       (the failure shape; "PROMOTED" for
                              passed verdicts)

A CELL is the 4-tuple (plugin, domain, invariant, kp). The cell
VALUE is the count of ledger rows matching that 4-tuple.

## Why sparse

The Cartesian product of axes is huge (25 plugins x ~10 domains x
arbitrary invariants x 27+ kps). Real catalogs will have well
under 0.1% of cells populated. Storing as dict[tuple, int] keeps
memory linear in the populated-cell count.

## What this primitive gives Layer 2

  - cell counts                (point queries)
  - axis values                (which plugins fired, which domains,
                                etc.)
  - marginals along any axis   (project the tensor to 3D / 2D / 1D)
  - populated cells            (the support set)
  - density of a sub-cube      (e.g., how dense is g11 x mahler?)

ITER-42 (null-space) reads the populated_cells / axis_values to
identify "should-exist but-doesn't" cells. ITER-43 (rank-expansion)
tracks distinct cell counts over time. ITER-44 (cross-domain)
uses marginals to predict analogs across domains.

## What this primitive is NOT

  - NOT a dense numpy tensor. No __getitem__ over slices; explicit
    cell / marginal methods only.
  - NOT a generator. Read-side only.
  - NOT load-bearing for Layer 1. Layer 1 verdicts are produced
    independently and ingested into the tensor afterward.

## Storage-backend independence

Builders accept Iterable[dict] of ledger rows. The tensor itself
is in-memory. A future iteration may add a persistent backend; the
current MVP is sufficient for Sprint-1 ablation experiments.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional


# Axis indices — used in marginal_over / axis_values
AXIS_PLUGIN = 0
AXIS_DOMAIN = 1
AXIS_INVARIANT = 2
AXIS_KP = 3
AXIS_NAMES = ("plugin", "domain", "invariant", "kp")
N_AXES = 4

# Sentinels for missing axis values on a ledger row. Kept as
# explicit strings so JSON serialization is unsurprising.
DEFAULT_DOMAIN = "unspecified"
DEFAULT_INVARIANT = "unspecified"
PROMOTED_KP = "PROMOTED"


# A cell is a 4-tuple. Type alias for clarity.
Cell = tuple[str, str, str, str]


def _default_invariant_extractor(row: dict) -> str:
    """Default invariant axis extractor.

    Looks at row['invariant'] first; falls back to
    row['input_signature'] (the signature is a useful proxy for
    "what was being probed"); finally DEFAULT_INVARIANT.

    Callers with richer invariant semantics should pass their own
    callable to KillTensor.from_ledger_rows().
    """
    return (
        row.get("invariant")
        or row.get("input_signature")
        or DEFAULT_INVARIANT
    )


@dataclass
class KillTensor:
    """Sparse 4D tensor over (plugin, domain, invariant, kp).

    Cells are a dict[Cell, int] of counts. All read operations
    are pure functions of the cell dict; the tensor is mutable
    (call add_cell / from_ledger_rows to populate) but never
    overwrites a cell's count on .add_cell — it accumulates.
    """
    cells: dict[Cell, int] = field(default_factory=dict)

    # -----------------------------------------------------------------
    # Construction
    # -----------------------------------------------------------------

    def add_cell(
        self,
        plugin: str,
        domain: str,
        invariant: str,
        kp: str,
        *,
        count: int = 1,
    ) -> None:
        """Increment the cell count by `count` (default 1)."""
        if count < 0:
            raise ValueError("add_cell: count must be non-negative")
        if count == 0:
            return
        key: Cell = (plugin, domain, invariant, kp)
        self.cells[key] = self.cells.get(key, 0) + count

    def add_row(
        self,
        row: dict,
        *,
        invariant_extractor: Optional[Callable[[dict], str]] = None,
        default_domain: str = DEFAULT_DOMAIN,
    ) -> bool:
        """Ingest one ledger row. Returns True iff the row was added.

        Rows without a plugin_id are skipped (return False); a
        kill_pattern of None becomes PROMOTED_KP.
        """
        plugin = row.get("plugin_id")
        if not plugin:
            return False
        domain = row.get("domain") or default_domain
        if invariant_extractor is None:
            invariant_extractor = _default_invariant_extractor
        invariant = invariant_extractor(row) or DEFAULT_INVARIANT
        kp = row.get("kill_pattern") or PROMOTED_KP
        self.add_cell(plugin, domain, invariant, kp)
        return True

    @classmethod
    def from_ledger_rows(
        cls,
        rows: Iterable[dict],
        *,
        invariant_extractor: Optional[Callable[[dict], str]] = None,
        default_domain: str = DEFAULT_DOMAIN,
    ) -> "KillTensor":
        """Build a tensor from a stream of ledger rows."""
        t = cls()
        for row in rows:
            t.add_row(
                row,
                invariant_extractor=invariant_extractor,
                default_domain=default_domain,
            )
        return t

    # -----------------------------------------------------------------
    # Point queries
    # -----------------------------------------------------------------

    def cell(
        self, plugin: str, domain: str, invariant: str, kp: str
    ) -> int:
        """Cell count at the 4-tuple. 0 for empty cells."""
        return self.cells.get((plugin, domain, invariant, kp), 0)

    def total_count(self) -> int:
        """Sum of all cell counts."""
        return sum(self.cells.values())

    def n_populated_cells(self) -> int:
        """Number of cells with count > 0."""
        return len(self.cells)

    def populated_cells(self) -> set[Cell]:
        """Set of all populated 4-tuples."""
        return set(self.cells.keys())

    # -----------------------------------------------------------------
    # Axis values
    # -----------------------------------------------------------------

    def axis_values(self, axis: int) -> set[str]:
        """Set of distinct values appearing on a given axis.

        axis must be one of AXIS_PLUGIN / AXIS_DOMAIN /
        AXIS_INVARIANT / AXIS_KP.
        """
        if axis < 0 or axis >= N_AXES:
            raise ValueError(
                f"axis_values: axis must be in 0..{N_AXES - 1}; "
                f"got {axis}"
            )
        return {key[axis] for key in self.cells}

    # -----------------------------------------------------------------
    # Marginals
    # -----------------------------------------------------------------

    def marginal_over(self, axis: int) -> dict[tuple[str, ...], int]:
        """Project the tensor by summing OVER the given axis.

        The result is a dict keyed by the (N_AXES - 1)-tuple of
        the OTHER axes. For example, marginal_over(AXIS_KP) returns
        a dict keyed by (plugin, domain, invariant) -- the kp axis
        has been collapsed.
        """
        if axis < 0 or axis >= N_AXES:
            raise ValueError(
                f"marginal_over: axis must be in 0..{N_AXES - 1}; "
                f"got {axis}"
            )
        result: dict[tuple[str, ...], int] = defaultdict(int)
        for cell, count in self.cells.items():
            reduced = tuple(v for i, v in enumerate(cell) if i != axis)
            result[reduced] += count
        return dict(result)

    def marginal_on(self, axis: int) -> dict[str, int]:
        """Project the tensor by summing ONTO a single axis.

        Returns a dict keyed by the axis value (a single string).
        The complement of marginal_over: marginal_over reduces by
        removing the given axis; marginal_on reduces by keeping
        only the given axis.
        """
        if axis < 0 or axis >= N_AXES:
            raise ValueError(
                f"marginal_on: axis must be in 0..{N_AXES - 1}; "
                f"got {axis}"
            )
        result: dict[str, int] = defaultdict(int)
        for cell, count in self.cells.items():
            result[cell[axis]] += count
        return dict(result)

    # -----------------------------------------------------------------
    # Sub-cube density / box queries
    # -----------------------------------------------------------------

    def density_in_box(
        self,
        *,
        plugins: Optional[Iterable[str]] = None,
        domains: Optional[Iterable[str]] = None,
        invariants: Optional[Iterable[str]] = None,
        kps: Optional[Iterable[str]] = None,
    ) -> float:
        """Fraction of cells in the bounding box that are populated.

        Each filter is a set of allowed axis values. None means
        "all values currently on this axis." Box size is the
        Cartesian product of allowed sets. Density is populated /
        product_size.

        Returns 0.0 for empty boxes.
        """
        p_set = set(plugins) if plugins is not None else self.axis_values(AXIS_PLUGIN)
        d_set = set(domains) if domains is not None else self.axis_values(AXIS_DOMAIN)
        i_set = set(invariants) if invariants is not None else self.axis_values(AXIS_INVARIANT)
        k_set = set(kps) if kps is not None else self.axis_values(AXIS_KP)
        box_size = len(p_set) * len(d_set) * len(i_set) * len(k_set)
        if box_size == 0:
            return 0.0
        populated = sum(
            1 for cell in self.cells
            if cell[0] in p_set and cell[1] in d_set
               and cell[2] in i_set and cell[3] in k_set
        )
        return populated / box_size

    def empty_cells_in_box(
        self,
        *,
        plugins: Optional[Iterable[str]] = None,
        domains: Optional[Iterable[str]] = None,
        invariants: Optional[Iterable[str]] = None,
        kps: Optional[Iterable[str]] = None,
    ) -> set[Cell]:
        """Cells in the bounding box that are NOT populated.

        ITER-42 (null-space detection) builds on this: voids in
        the box are candidates for "should-exist but-doesn't"
        analysis.
        """
        p_set = set(plugins) if plugins is not None else self.axis_values(AXIS_PLUGIN)
        d_set = set(domains) if domains is not None else self.axis_values(AXIS_DOMAIN)
        i_set = set(invariants) if invariants is not None else self.axis_values(AXIS_INVARIANT)
        k_set = set(kps) if kps is not None else self.axis_values(AXIS_KP)
        empty: set[Cell] = set()
        for p in p_set:
            for d in d_set:
                for i in i_set:
                    for k in k_set:
                        if (p, d, i, k) not in self.cells:
                            empty.add((p, d, i, k))
        return empty

    # -----------------------------------------------------------------
    # Rank-like measures (used by ITER-43)
    # -----------------------------------------------------------------

    def axis_cardinalities(self) -> tuple[int, int, int, int]:
        """Distinct value count per axis. The shape of the bounding
        box equals the product of these four numbers; the tensor
        is sparse iff product >> n_populated_cells.
        """
        return tuple(
            len(self.axis_values(i)) for i in range(N_AXES)
        )

    def shape(self) -> tuple[int, int, int, int]:
        """Alias of axis_cardinalities for numpy-like ergonomics."""
        return self.axis_cardinalities()

    def __len__(self) -> int:
        return self.n_populated_cells()

    def __repr__(self) -> str:
        return (
            f"KillTensor(populated={self.n_populated_cells()}, "
            f"total_count={self.total_count()}, "
            f"shape={self.shape()})"
        )
