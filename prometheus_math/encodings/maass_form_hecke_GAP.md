# Maass Form Hecke Eigenvalue Encoding — Design (T-2026-05-07-T023)

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T023 (P1, calibration anchor density in under-explored harmonic-analysis territory per HARD-4)
**Status:** Design landed; minimal impl in companion file.

---

## Per HARD-5: not "Maass form" the discipline label, but "(object, operator-output) pair"

The substrate does not care that this object is "from harmonic analysis" or "an automorphic form." It cares about:
- An object identifiable by a chart-canonical signature (level, weight, archimedean type, eigenvalue index)
- An operator (Hecke at prime p) producing a high-precision eigenvalue
- Operator-output sequence indexed by primes

Per HARD-5: discipline label "Maass form" lives only in `notes` / docstring metadata. The substrate's coordinate is the operator-output sequence shape, not the form itself.

---

## Proposed primitive

### `OperatorOutputSequence`

```python
@dataclass(frozen=True)
class OperatorOutputSequence:
    """Typed operator-output sequence indexed by a discrete parameter
    (e.g., primes for Hecke eigenvalues; conductors for L-function values;
    levels for modular form coefficients).

    Per HARD-5: the substrate-grade primitive for any "object that
    produces a sequence of values under a parameterized operator." Maass
    forms are one instance; modular form q-expansion coefficients are
    another; L-function values at integer arguments are another.
    """
    operator_id: str                           # e.g. "hecke_eigenvalue"
    index_parameter_name: str                  # e.g. "prime"
    index_values: Tuple[int, ...]              # e.g. (2, 3, 5, 7, 11, ...)
    output_values: Tuple[str, ...]             # high-precision strings (mpmath.mpf serialized)
    output_precision_dps: int                  # decimal places of precision
    output_unit: str                           # e.g. "real_eigenvalue", "complex_eigenvalue"
    object_canonical_form: Mapping[str, Any]   # the source object's chart-canonical form
    chart_id: str                              # registered chart this object lives in
```

Note the deliberate use of **string-encoded high-precision values** to avoid the multi-precision contract gap surfaced by T029. This is the additive-pattern: the existing `KillComponent.margin: Optional[float]` stays unchanged; high-precision output lives in a sister field via string serialization until the v2 multi-precision contract change lands.

### CoordinateChart placement

Proposed new chart: `harmonic_analysis:maass_form:level_N_weight_W` (one chart per level/weight slice). Coordinate system: `(level, weight, archimedean_type, eigenvalue_index, n_terms_known)`. Canonicalization: identity (Maass forms are uniquely identified by their LMFDB labels).

Initial chart instance to register: `harmonic_analysis:maass_form:Selberg_PSL2Z` for Selberg's classic Maass form on PSL2(Z).

---

## Worked encoding example

Selberg's Maass form on PSL2(Z) — Hecke eigenvalues at the first few primes (LMFDB label provisional):

```python
seq = OperatorOutputSequence(
    operator_id="hecke_eigenvalue",
    index_parameter_name="prime",
    index_values=(2, 3, 5, 7, 11, 13),
    output_values=(
        "1.5491353837...",   # placeholder; real values from LMFDB at dps=50
        "0.2456789012...",
        "...",
        "...",
        "...",
        "...",
    ),
    output_precision_dps=50,
    output_unit="real_eigenvalue",
    object_canonical_form={
        "level": 1,
        "weight": 0,
        "archimedean_type": "real_analytic",
        "eigenvalue_label": "Selberg_PSL2Z",
    },
    chart_id="harmonic_analysis:maass_form:Selberg_PSL2Z",
)
```

The substrate's downstream consumers (TriangulationProtocol, OperatorPortabilityCertificate, NearMissCorpus) treat this as a typed object exactly like a Lehmer polynomial — same `chart_id`/`object_id` discipline, same provenance walk, same anti-leakage emission semantics.

---

## Capability gap status

**SUBSTRATE-SHIPS-NOW (with this design):**
- The `OperatorOutputSequence` primitive is purely additive — new module + new dataclass; no existing surface modified
- Chart registration follows the established pattern (Lehmer chart was the prototype)
- LMFDB ingestion is OUT OF SCOPE for this dispatch — separate Charon/Mnemosyne coordination ticket required to populate real LMFDB Maass form values

**OPEN follow-on for v2 contract-change window:**
- KillVector v2 multi-precision sister field (per T029 audit) so margin computations against high-precision Maass eigenvalues don't lose precision
- Hecke operator registration in `arsenal_meta` so the operator itself is a substrate-level callable
- Cross-chart portability certificate linking Maass form chart to BSD chart (if/when modularity-style operator transports are validated)

---

## Cross-references

- `aporia/doctrine/critical_memories.md` HARD-4 (calibration anchors in under-explored territory) + HARD-5 ((object, operator-output) pairs, discipline labels are docstrings)
- `prometheus_math/MULTIPRECISION_AUDIT.md` (T029 sister concern; this primitive uses the audit's recommended Option-B pattern preemptively)
- `harmonia/memory/architecture/operator_portability_GAP.md` (T030 — Maass form chart will be a target for cross-chart portability certificates once chart registers)
- `sigma_kernel/coordinate_chart.py` — chart-registration pattern this primitive follows
- `aporia/meta/queue/techne_inbox.jsonl#T-2026-05-07-T023` — original ticket

---

*Design landed; minimal impl in companion file. — Techne, 2026-05-07*
