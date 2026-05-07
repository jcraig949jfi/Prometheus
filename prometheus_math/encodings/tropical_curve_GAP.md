# Tropical Curve Encoding — Design (T-2026-05-07-T024)

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T024 (P1)
**Status:** Design landed; impl deferred to next contract-change window.

---

## Per HARD-5

Substrate doesn't care "tropical geometry" the discipline. It cares about an object with operator-derived structural metadata: a lattice polytope (Newton polytope) with attached valuation data. The polytope IS the structured signature.

---

## Proposed primitive

### `LatticePolytope` + `ValuationTag`

```python
@dataclass(frozen=True)
class LatticePolytope:
    """A lattice polytope identified by its vertex set (in ZZ^d).
    The substrate's coordinate is the vertex set + its convex-hull
    structure under the lattice action; the polytope's "tropical
    interpretation" lives in the ValuationTag, separately.
    """
    ambient_dimension: int                     # d in Z^d
    vertices: Tuple[Tuple[int, ...], ...]      # canonicalized: lex-min over lattice translations
    canonical_form_method: str                 # "lex_min_translation_class"
    chart_id: str                              # "lattice_polytope:dim_d:vertex_count_n"


@dataclass(frozen=True)
class ValuationTag:
    """Operator-output metadata: assigns a valuation to each lattice
    point (or vertex) of an associated polytope. Tropical curves are
    the canonical instance, but the primitive is more general
    (Newton-Okounkov bodies, mixed integer programming, etc.).
    """
    polytope_id: str                           # references LatticePolytope
    valuation_function_id: str                 # operator id (e.g. "min_plus_evaluation")
    valuations: Mapping[Tuple[int, ...], str]  # lattice point → high-precision value (string-encoded)
    base_field_characteristic: int             # 0 for Q, p for F_p
    notes: str                                 # tropical interpretation lives here, NOT in coords
```

### CoordinateChart placement

New chart family: `lattice_polytope:dim_<d>:vertex_count_<n>`. Canonicalization: lex-min over lattice translations + GL(d,Z) representatives.

---

## Worked encoding example — tropical genus-1 curve from a square Newton polytope

A tropical elliptic curve from the Newton polytope of `1 + xy + x²y + xy² + x³y² + ...` (vertices in the (x-deg, y-deg) plane forming a hexagon). Encoded:

```python
poly = LatticePolytope(
    ambient_dimension=2,
    vertices=((0,0), (3,0), (0,3), (3,3), (1,2), (2,1)),  # placeholder hexagon
    canonical_form_method="lex_min_translation_class",
    chart_id="lattice_polytope:dim_2:vertex_count_6",
)

trop = ValuationTag(
    polytope_id=poly.id,
    valuation_function_id="min_plus_evaluation",
    valuations={
        (0,0): "0", (3,0): "1", (0,3): "1",
        (3,3): "2", (1,2): "0", (2,1): "0",
    },
    base_field_characteristic=0,
    notes="tropical elliptic curve over Q (Mikhalkin's hexagon)",
)
```

---

## Capability gap status

- LatticePolytope primitive is moderate work (canonicalization over lattice translations + GL(d,Z) is non-trivial)
- ValuationTag is straightforward additive
- Both deferred to a future contract-change window; design lands now so reviewers can evaluate the dataclass shape

---

## Cross-references

- `aporia/doctrine/critical_memories.md` HARD-4 + HARD-5
- `harmonia/memory/architecture/operator_portability_GAP.md` (tropical→algebraic operator transports would use this)
- `aporia/meta/queue/techne_inbox.jsonl#T-2026-05-07-T024`

— Techne, 2026-05-07
