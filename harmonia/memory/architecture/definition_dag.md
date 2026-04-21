# Definition DAG — Substrate Primitive

**Status:** specification, v0.1 DRAFT (2026-04-20). Not yet implemented.
**Architectural slot:** substrate primitive, alongside the symbol registry, tensor, signals.specimens, and Cartographer viewer. **Not a generator.**
**Audience:** Harmonia conductor, gen_06 / gen_10 / gen_11 implementers, future symbol-registry curators.

---

## Why this exists

Three in-flight pieces of infrastructure share a common need that nothing in the current substrate satisfies:

- **gen_06 Pattern 30 sweep** must answer "is X algebraically defined in terms of Y?" before letting a correlation test land in the tensor. Without a queryable algebraic-dependence structure, the sweep falls back to coarse symbolic-equivalence checks that miss non-obvious tautologies (the F043 class of failure).
- **gen_10 composition enumeration** must reject compositions that are tautological by construction (e.g., `correlation_scorer ∘ dataset_with_algebraically_coupled_columns`). Type compatibility alone doesn't catch this; algebraic-dependence semantics do.
- **gen_11 coordinate-system invention** must distinguish a *novel* candidate axis from a *re-encoding* of an existing one. P036 root_number aliases P023 rank parity on EC because BSD parity makes them definitionally coupled. A filter that doesn't know this promotes duplicates.

All three need the same thing: a directed graph whose nodes are mathematical concepts/quantities and whose edges encode algebraic dependence. This document specifies that graph as a substrate primitive — a queryable structure that generators read against, on the same architectural footing as the symbol registry.

**The DAG is not a generator.** Generators *do* work; the DAG is something they *query*. This distinction matters: the DAG sits next to `agora.symbols`, `agora.tensor`, `agora.datasets` in the architecture, with its own access module (`agora.dag`), its own MD-backed source of truth, and its own Redis mirror.

---

## Scope

**In scope:**
- Algebraic / definitional dependence between named quantities (atomic LMFDB columns; promoted symbols; Pattern-anchored derived quantities).
- Severity classification (the Pattern 30 levels 0–4 mapped to edge weights / edge types).
- Query API: "does X reduce to Y under any chain of edges?" "What is the minimal definitional path from X to Y?" "Are X and Y algebraically independent?"

**Out of scope (initial v0.1):**
- Statistical dependence (that's what nulls + tests measure; the DAG is for *definitional* coupling only).
- Implication chains in proofs (that's the Machinery Graph from the four-candidates discussion; separate substrate).
- Full symbolic algebra (the DAG records *named relationships*, not arbitrary expression rewriting; sympy lives at the leaves).

---

## Schema

### Nodes

A node is a **named quantity**. Three node classes:

- **`atomic`** — a column in a primary data source (e.g., `lmfdb.ec_curvedata.conductor`, `lmfdb.ec_curvedata.rank`, `lmfdb.bsd_joined.sha`). Atoms are root-level; they do not have incoming definitional edges.
- **`derived`** — a quantity defined in terms of other nodes via a pinned expression (e.g., `szpiro_ratio = log(disc_abs) / log(conductor)`; `A := Omega_real * prod_p c_p`). Derived nodes carry a `definition` field with the canonical expression and the list of input nodes.
- **`symbol`** — a promoted registry symbol (NULL_BSWCD@v2, EPS011@v2, etc.). Symbol nodes are first-class because operators and datasets participate in algebraic relationships (an operator output's algebraic lineage matters for Pattern 30; a dataset's column composition matters for joint-coupling detection).

Each node carries:
```
{
  "name": "<canonical name, scoped by class>",
  "class": "atomic | derived | symbol",
  "definition": "<sympy-parseable expression, null for atomic>",
  "inputs": ["<node_name>", ...],         # empty for atomic
  "domain": "<EC | NF | MF | g2c | ... | universal>",
  "added_by": "<agent>@<commit>",
  "added_at": "<ISO-8601>",
  "references": ["<symbol@v>", "<F-id@c>", "<P-id@c>", ...],
  "notes": "<free text, optional>"
}
```

### Edges

An edge encodes a **definitional dependency** from a node to one of its inputs. Edge type carries the Pattern 30 severity:

| Edge type | Pattern 30 level | Meaning |
|---|---|---|
| `weak_term` | 1 (WEAK_ALGEBRAIC) | Input appears as one of several terms with small coefficient or under a transformation that other terms dominate. |
| `shared_factor` | 2 (SHARED_VARIABLE) | Input appears as a factor or term with non-trivial coefficient. |
| `rearrangement` | 3 (REARRANGEMENT) | Source node is a rearrangement of input plus other known terms (the F043 case). |
| `identity` | 4 (IDENTITY) | Source node equals a function of input exactly (proved algebraic identity; F003 BSD parity, F008 Scholz reflection). |

Edges are typed; queries can filter by edge type. A correlation test between two nodes is **valid evidence only if the path between them contains zero edges of type ≥ shared_factor**.

### Storage

**Primary source of truth:** MD files at `harmonia/memory/dag/<NAME>.md`, one per node. Frontmatter carries the schema fields above; the body documents the derivation, the references, and the version history.

**Redis mirror:** `agora.dag` module, mirroring per `dag:<NAME>:def`, plus index sets:
- `dag:nodes` — all node names
- `dag:by_class:<class>` — names of that class
- `dag:by_domain:<domain>` — names in that domain
- `dag:edges:<NAME>:out` — outgoing edges from this node (set of `<input_name>:<edge_type>` tuples)
- `dag:edges:<NAME>:in` — incoming edges (the reverse index)
- `dag:edges:by_type:<edge_type>` — all edges of this severity (for sweeps that filter by Pattern 30 level)

Push idempotent, immutable per node version. Promotion gating mirrors the symbol registry: ≥ 2 references in committed work OR drafter + reviewer sign-off.

---

## Query API

Five core queries that gen_06, gen_10, and gen_11 all need:

```python
from agora.dag import (
    resolve_node,         # get a node by name
    upstream,             # all nodes that this node depends on (transitive)
    downstream,           # all nodes that depend on this node (transitive)
    paths,                # list paths from X to Y, each annotated with edge types
    coupling_severity,    # max edge-type severity along any X-Y path; 0 if none
)

# Pattern 30 check
sev = coupling_severity('log_A', 'log_Sha')   # returns 3 (REARRANGEMENT) for F043
if sev >= 2: BLOCK

# Composition-validity check
sev = coupling_severity(operator_output, operator_input)
if sev >= 2: REJECT_COMPOSITION

# Coordinate-novelty check
for existing_p_id in catalog:
    if coupling_severity(candidate_axis, existing_p_id) >= 3:
        REJECT_AS_REPARAMETERIZATION

# Kill-inversion (gen_11 source E)
killed_axes = [n for n in upstream(killed_F_ID) if class == 'symbol']
non_overlapping_axes = [n for n in catalog if coupling_severity(n, killed_F_ID) == 0]
```

All queries are O(graph_size) at worst; expected O(small) because the DAG has few edges per node. Cache results in Redis with TTL on the source-of-truth version.

---

## Construction path

### Phase 0 — Manual seed (this spec landing)

Hand-curate ~20 nodes covering the live specimens' algebraic universe:
- **Atomic:** conductor, rank, analytic_rank, root_number, sha, regulator, omega_real, c_p (per-prime Tamagawa), torsion, disc_abs, num_bad_primes, mahler_measure, a_p (per-prime), zero_spacing, num_ram
- **Derived:** szpiro_ratio (log disc / log cond), faltings_height, A := omega_real * prod(c_p), L_value, leading_term, var_first_gap
- **Symbol:** the five promoted operators/datasets/constants currently in the registry

Edges: ~30 edges spanning the F003/F008/F009 calibration identities and the F043 rearrangement (as the canonical Level-3 example).

This is one tick of human-curated work. Output: enough graph to make gen_06 Gate 1 testable on retrospective +1/+2 cells, and enough to seed gen_11's filter on the first run.

### Phase 1 — Automated extraction from symbol definitions

Every promoted symbol's MD has a `references:` field and (for derived ones) a `definition` expression. Write `agora.dag.extract_from_symbol_md` that parses these and proposes DAG edges. Human reviewer accepts/rejects per node before promotion.

### Phase 2 — Literature-pull (gen_07 hook)

The Aporia paper stream and gen_07's literature-diff log mention named identities (BSD identity rearrangements, modular form / EC coefficient relations, Scholz reflection). Each identified identity proposes a candidate edge. Human review at the same gate as Phase 1.

### Phase 3 — Symbol-registry trigger

Make DAG-node-creation a side effect of every `symbols.push` for derived/operator/constant types. Symbol promotion that introduces a new derived quantity automatically proposes the corresponding DAG node + edges; conductor accepts or refines.

---

## Integration points (consumers)

**`gen_06_pattern_autosweeps`** — Gate 1 of the Pattern 30 sweep replaces the coarse symbolic-equivalence check with `coupling_severity(X, Y) >= 2 → BLOCK` against the DAG. This is the single largest immediate consumer; without DAG, gen_06's Gate 1 is the spec's weakest gate.

**`gen_10_composition_enumeration`** — composition validator checks `coupling_severity(operator_output_target, operator_input_source) == 0` before emitting a composition. Catches `correlation_scorer ∘ algebraically_coupled_data` before computing it.

**`gen_11_coordinate_invention`** — Gate 1 of the candidate-axis filter checks `coupling_severity(candidate, existing_p_id) < 3` for every existing P-ID. Without DAG, gen_11 is unsafe to seed because the filter would over-pass re-parameterizations.

**`Pattern_30` sweep symbols (when promoted)** — every `algebraic_lineage` block referenced in F-ID descriptions becomes a candidate DAG fragment. The DAG is where those lineages live as queryable structure rather than as prose.

**`SIGNATURE@v2.computation_spec`** — when a SIGNATURE references a derived quantity, the DAG provides the audit trail for what that quantity is defined as. A future SIGNATURE@v3 might carry a `definitional_lineage_hash` field that identifies the DAG snapshot the SIGNATURE was computed against.

---

## Epistemic discipline

1. **The DAG records *known* algebraic structure, not all algebraic structure.** Coupling that exists in the math but isn't yet recorded will not be caught. This is a slowly-decaying false-negative rate that improves as Phases 1–3 accumulate. The substrate must not pretend the DAG is complete.

2. **Edge severity is a judgment call at the boundary.** Level 1 vs Level 2 is sometimes ambiguous (does a `log` transformation count as a "term" or as the whole quantity?). Promotion requires drafter to explicitly justify severity in the node MD, and reviewer to sign off. Pattern 30's graded levels carry over directly, with the same interpretive caveats.

3. **The DAG is versioned.** Edges are immutable once promoted; corrections promote new versions of the source node. Old SIGNATUREs computed against old DAG versions remain reproducible.

4. **Performance is not a near-term concern.** Expected DAG size at one year: 200–500 nodes, 500–1500 edges. All queries fit in memory. Premature optimization (graph databases, GraphQL endpoints, etc.) is rejected; base Redis suffices.

5. **The DAG is not a proof checker.** It records "these quantities are algebraically related" with severity, not "this implies that" with rigor. Proof-theoretic structure is the Machinery Graph, a separate substrate not in scope here.

---

## Acceptance criteria for v0.1 (this spec) to ship

- [ ] `harmonia/memory/dag/` directory with ≥ 20 hand-curated node MDs covering the live-specimen universe.
- [ ] `agora/dag/` Python module with `resolve_node`, `upstream`, `downstream`, `paths`, `coupling_severity` plus a `push` script that mirrors MD nodes to Redis.
- [ ] Smoke test: `coupling_severity('log_A', 'log_Sha')` returns 3 (the F043 anchor case).
- [ ] gen_06 Gate 1 stub-replaced to call `coupling_severity` instead of the coarse symbolic check.
- [ ] gen_11 Gate 1 (when worker claims) calls `coupling_severity` instead of the coarse check.
- [ ] `harmonia/memory/architecture/definition_dag.md` (this file) updated with v1.0 status when the above lands.

---

## Composes with

- **Symbol registry** — DAG nodes and registry symbols overlap (`symbol` is one of the three node classes). Promotion of a derived symbol triggers DAG-node proposal automatically (Phase 3).
- **Pattern library** — Pattern 30 graded levels map directly to DAG edge types. The DAG is Pattern 30 made queryable.
- **`null_protocol_v1`** — Class 5 (algebraic-identity claims) is precisely the case where DAG `coupling_severity ≥ 4` for the (X, Y) pair the correlation purports to test. The DAG can flag Class 5 cells automatically rather than relying on prose classification.
- **`methodology_toolkit.md`** — `MDL_SCORER@v1` interaction: a Level 3 (REARRANGEMENT) edge means the data-bits cost is zero (the model is the algebra), so MDL trivially picks it as best — exactly the correct automated flag for a definitional coupling.
- **`gen_03_cross_domain_transfer`** — when porting a projection across domains, the DAG can verify the projection's algebraic lineage doesn't depend on domain-specific atoms.

---

## Version history

- **v0.1 DRAFT** — 2026-04-20 — initial spec, written same evening as gen_11 spec and Tier 1 generator seeds. Marked DRAFT because the Phase 0 hand-curation hasn't happened yet; v1.0 ships when acceptance criteria above are met. The architectural framing (substrate primitive, not generator; sits next to symbol registry) is load-bearing — do not silently re-architect this as a generator without conductor sign-off.
