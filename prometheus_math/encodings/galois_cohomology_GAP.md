# Galois Cohomology Class Encoding — Design (T-2026-05-07-T026)

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T026 (P2)
**Status:** Design landed; impl deferred.

---

## Per HARD-5

Not "Galois cohomology" the discipline. The substrate cares about: an object that IS a function (cocycle) from a group to a module, with the group acting on the module. The substrate-grade content is the **cocycle relation** under the group action; the cohomological interpretation is metadata.

---

## Proposed primitive

### `Cocycle` + `GroupActionContext`

```python
@dataclass(frozen=True)
class GroupActionContext:
    """Specifies a group + module + action. Substrate-grade: this is a
    typed pair of registered objects, not a discipline category."""
    group_id: str                                  # registered group
    module_id: str                                 # registered module
    action_id: str                                 # registered action (group → automorphisms of module)
    chart_id: str                                  # "group_action:group_X:module_Y"


@dataclass(frozen=True)
class Cocycle:
    """A 1-cocycle (function from group to module) satisfying the
    cocycle relation under the registered action. Higher-degree cocycles
    are a sister primitive; this dataclass covers H^1 only at v1.

    The substrate verifies the cocycle relation as part of __post_init__
    (or via a registered operator that checks the relation modulo the
    module's equivalence). Coboundary equivalence — when two cocycles
    represent the same cohomology class — is a separate operator output.
    """
    context: GroupActionContext
    cocycle_function_id: str                       # callable id; the substrate verifies via apply
    sample_evaluations: Mapping[str, str]          # group_element_id → module_value_id (sparse witness)
    cocycle_relation_verified: bool                 # True iff relation has been checked
    chart_id: str                                   # "cocycle:group_X:module_Y:degree_1"
```

### CoordinateChart placement

`group_action:group_<G>:module_<M>` for the action context.
`cocycle:group_<G>:module_<M>:degree_<d>` for the cocycle objects themselves.

---

## Worked encoding example — Hilbert 90 class for cyclic Galois extension

For a cyclic extension `K/F` with Galois group `G = <σ>` of order `n`, Hilbert 90 says `H^1(G, K*) = 0` — every 1-cocycle is a coboundary. Encoding a specific cocycle `χ: G → K*`:

```python
ctx = GroupActionContext(
    group_id="cyclic_n_3",                          # G = Z/3
    module_id="multiplicative_group:K_extension",   # K*
    action_id="cyclic_galois_action",
    chart_id="group_action:cyclic_n_3:multiplicative_group:K_extension",
)

cocycle = Cocycle(
    context=ctx,
    cocycle_function_id="hilbert_90_witness:K_F:n_3",
    sample_evaluations={
        "identity": "1",
        "sigma": "alpha",
        "sigma^2": "alpha * sigma(alpha)",
    },
    cocycle_relation_verified=True,
    chart_id="cocycle:cyclic_n_3:multiplicative_group:K_extension:degree_1",
)
```

---

## Capability gap status

- Cocycle dataclass + GroupActionContext are additive
- Group / module / action registries are larger work (orthogonal to this primitive — they live in `prometheus_math/groups.py`, `prometheus_math/modules.py`, etc., which don't yet exist as substrate-grade primitives)
- For v1: cocycle is "registered" as a callable + sparse witness pairs; full action verification is operator infrastructure

---

## Cross-references

- `aporia/doctrine/critical_memories.md` HARD-4 (categorical/topos/cohomological territory on hunt list) + HARD-5
- `harmonia/memory/architecture/operator_portability_GAP.md` (cohomology → number-field operator transports)

— Techne, 2026-05-07
