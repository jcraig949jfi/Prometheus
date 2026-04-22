---
name: PATTERN_30
type: pattern
version: 1
version_timestamp: 2026-04-20T23:45:00Z
immutable: true
previous_version: null
precision:
  canonical_definition: "Before running a correlation or dependence test on two quantities X and Y, check whether one is algebraically defined in terms of the other (directly or via rearrangement of a proved identity). If yes, the observed correlation is a rearrangement of the identity, not evidence of arithmetic structure. Permutation nulls do NOT break this coupling because they preserve algebraic relationships between variables."
  severity_levels: 5
  level_vocabulary: [CLEAN, WEAK_ALGEBRAIC, SHARED_VARIABLE, REARRANGEMENT, IDENTITY]
  verdict_vocabulary: [CLEAR, WARN, BLOCK]
  level_to_verdict_map:
    0: CLEAR
    1: WARN
    2: BLOCK
    3: BLOCK
    4: BLOCK
  anchor_count: 5
  lineage_types_using: [algebraic_lineage]
  override_protocol: harmonia/sweeps/OVERRIDE_PROTOCOL.md
  implementation_determinism: sympy_atom_overlap_plus_identity_connection
proposed_by: Harmonia_M2_sessionA@c71218321
promoted_commit: pending
references:
  - F043@c9fc25706
  - F015@c43fb1b12
  - F041a@c1abdec43
  - F013@ce0ba1692
  - F045@c71218321
  - F003@c348113f3
  - Pattern_1@c45fd79d5
  - Pattern_4@c45fd79d5
  - Pattern_21@c9335b7c2
  - Pattern_25@ca87ea026
  - NULL_BSWCD@v2
  - SUBFAMILY@v1
  - GATE_VERDICT@v1
redis_key: symbols:PATTERN_30:v1:def
implementation: harmonia/sweeps/pattern_30.py::sweep@c71218321
---

## Definition

**Algebraic-Identity Coupling Detection.** Before running a correlation
or dependence test on two quantities `X` and `Y`, check whether one is
algebraically defined in terms of the other — either directly or via
rearrangement of a proved identity. If yes, the observed "correlation"
is a rearrangement of the identity, not evidence of arithmetic structure.
Permutation nulls do NOT break this coupling because they preserve the
algebraic relationship between variables (they shuffle pairings, not
definitions).

Graded 0–4. Levels 2–4 BLOCK by default; Level 1 WARN; Level 0 CLEAR.

## Graded severity schema

| Level | Name | One-line | Evidence status | Verdict |
|---|---|---|---|---|
| 0 | `CLEAN` | X and Y mathematically independent under the measurement | correlation test valid | CLEAR |
| 1 | `WEAK_ALGEBRAIC` | X appears in a term/factor with small coefficient OR under a log-transform where other terms dominate | correlation partially algebraic; claims beyond direction are real | WARN |
| 2 | `SHARED_VARIABLE` | X appears directly as factor or term in Y's definition, coefficient non-trivial | correlation test no longer valid; report the algebra, not the correlation | BLOCK |
| 3 | `REARRANGEMENT` | Y is definitionally a rearrangement of X plus other known terms | correlation is a restatement of the defining identity; INVALID evidence | BLOCK |
| 4 | `IDENTITY` | Y = f(X) exactly (proved algebraic identity) | correlation tests identity verification, not arithmetic structure; calibration-anchor tier only | BLOCK |

**Level 0** — correlation tests are valid evidence of arithmetic
structure; run the permutation null as usual.

**Level 1** — findings are still reportable but must explicitly claim
something beyond the direction the algebra forces (stratum-dependence,
magnitude non-monotonicity, sign-uniformity-at-scale, within-stratum
shape). The direction of the headline slope is not load-bearing.

**Level 2 / 3** — retract the correlation as evidence; restate as an
algebraic observation. The null test result is a confirmation of the
algebra, not a discovery.

**Level 4** — belongs in the calibration-anchor tier where identity
verification is the intended semantics (F001–F005, F008, F009).

## Anchor cases

| F-ID | Level | Coupling | Status |
|---|---|---|---|
| F043 | 3 REARRANGEMENT | BSD identity rearranges as `log(Ω·∏c_p) = log L + 2 log tors − log Reg − log Sha`, so `log Sha` appears inside `log A`. `z_block=−348` detects the BSD identity in rearranged coordinates, not arithmetic structure. | Retracted 2026-04-19. |
| F015 | 1 WEAK_ALGEBRAIC | `szpiro = log|Disc| / log(N)`; correlating against `log(N)` puts `log(N)` in the denominator. Direction-of-slope partially forced; sign-uniform-per-k and magnitude non-monotonicity are NOT. | Annotated; sign durability retained. |
| F041a | 1 WEAK_ALGEBRAIC | CFKRS arithmetic factor `a_E(k)` is itself bad-prime-structure dependent, so a CFKRS rank-2 closed-form would predict an nbp-dependent slope. Pattern 5 gate and Pattern 30 gate collapse to the same gate. | Annotated; frontier vs calibration pending CFKRS. |
| F013 | 1 WEAK_ALGEBRAIC | P028 Katz-Sarnak stratifier is an algebraic function of rank via BSD parity `(−1)^rank = root_number`. Stratum-dependent effect expected; sign pattern and magnitude are not forced. | Annotated 2026-04-20. |
| F045 | 1 WEAK_ALGEBRAIC (provisional) | Isogeny-class-size axis (P100) is partially algebraic-derived from bad-prime structure via P100↔P021 coupling. Collapses into F041a at Level 2 if pending audit confirms. | Provisional; re-evaluates on `correlate_F041a_F045_nbp_vs_isogeny` completion. |

| F-ID cluster | Level | Coupling |
|---|---|---|
| F001–F005, F008, F009 | 4 IDENTITY | Proved theorems; identity verification is the calibration semantics. |

## Connected patterns

- **`Pattern_1@c45fd79d5`** (Distribution/Identity Trap) — PATTERN_30
  generalizes Pattern 1. Pattern 1 warned about two quantities sharing a
  formula at high correlation; PATTERN_30 covers the same shape at ANY
  correlation magnitude on algebraically-coupled variables, including
  log-transformed rearrangements (F043 was ρ=−0.43 but Level 3).
- **`Pattern_4@c45fd79d5`** (Sampling Frame Trap) — disjoint failure
  mode. PATTERN_30 is about algebraic coupling of X and Y; Pattern 4
  is about which rows were pulled. F044 is a Pattern-4 case, not a
  PATTERN_30 case; these are classified as `frame_hazard`, not
  `algebraic_lineage`, in the lineage taxonomy below.
- **`Pattern_21@c9335b7c2`** (Null-Model Selection) — orthogonal
  check. Pattern 21 asks whether the null preserves the right marginal;
  PATTERN_30 asks whether the variables are independent at all. Both
  apply: a PATTERN_30-Level-0 finding can still be Pattern-21 suspect.
- **`Pattern_25@ca87ea026`** (Under-Constrained Ansatz, DRAFT) —
  composes with Level 1 severity. F041a and F015 carry both a Pattern 25
  concern (ansatz free parameters) and a PATTERN_30 Level 1 concern;
  MDL model selection (deferred) addresses the former.

## Lineage-registry integration

PATTERN_30 drives the `algebraic_lineage` arm of the four-type lineage
taxonomy in `harmonia/sweeps/pattern_30.py::classify_entry`:

| Type | PATTERN_30 applicability |
|---|---|
| `algebraic_lineage` | runs PATTERN_30 sweep; returns `{CLEAR | WARN | BLOCK}` with level |
| `frame_hazard` | does NOT run PATTERN_30; Pattern 4 is the gate (e.g., F044) |
| `killed_no_correlation` | does NOT run; no correlation to audit (e.g., F022) |
| `non_correlational` | does NOT run; variance deficit / existence / calibration (e.g., F011, F014) |

The taxonomy ensures PATTERN_30 only fires on F-IDs where it is the
correct frame, and other F-IDs short-circuit with typed N/A verdicts
rather than false CLEAN signals.

## Derivation / show work

The anchor is F043 (retracted 2026-04-19). External review caught that
the claimed `corr(log Sha, log A) = −0.4343` at `z_block = −348` was
mathematically forced by the BSD identity. The block-shuffle null had
not broken the coupling because permutation preserves algebraic
relationships between variables — it shuffles pairs, not definitions.
A pre-flight check that traced the definitional lineage of `Y` would
have detected the Level 3 REARRANGEMENT before running any correlation
test.

Upgrading from the initial binary CLEAN/COUPLED classification to the
graded 0–4 schema happened 2026-04-19 in external-review response:
binary was too coarse to distinguish F043 (REARRANGEMENT, retract) from
F015 (WEAK_ALGEBRAIC, retain with annotation). The graded version now
serves both retraction and annotation use cases without false BLOCKs.

Implementation at `harmonia/sweeps/pattern_30.py::sweep` uses sympy:

1. Compute atomic free-symbol sets for X and Y.
2. If sets share atoms → Level 2 SHARED_VARIABLE.
3. If any `known_identity` has atoms intersecting both X and Y → Level 3
   REARRANGEMENT.
4. If `simplify(X − Y) == 0` → Level 4 IDENTITY.
5. Otherwise Level 0 CLEAN.
6. Callers with out-of-band knowledge (log-in-denominator coupling,
   theory-predicted partial forcing) pass `severity_hint="weak_algebraic"`
   for Level 1.

14 tests pass as of promotion; F043 is the headline BLOCK regression.

## Data / implementation

```python
from harmonia.sweeps.pattern_30 import sweep, CouplingCheck

# Level 3 example — F043 BSD rearrangement
import sympy
Sha, L, Omega, cp, Reg, tors = sympy.symbols(
    'Sha L Omega cp Reg tors', positive=True)
result = sweep(CouplingCheck(
    X_expr=sympy.log(Sha),
    Y_expr=sympy.log(Omega * cp),
    known_identities=[sympy.Eq(L, Omega * Reg * cp * Sha / tors**2)],
    transform='log',
))
# result.level == 3, result.verdict == 'BLOCK'
```

The `LINEAGE_REGISTRY` dict in `harmonia/sweeps/retrospective.py` pins
the five anchor F-IDs to their declared severity levels; the retrospective
runner and the `agora.tensor.push.push_tensor()` per-promoted-cell gate
both resolve against this registry.

## Usage

**Tight (in a SIGNATURE provenance block):**
```
sweeps.pattern_30: BLOCK @ level=3 REARRANGEMENT
  connecting_identity: Eq(L, Omega*Reg*cp*Sha/tors**2)
  rationale: identity shares atoms with both X and Y; substitution
             rewrites Y to contain X.
```

**Loose (in an inter-agent report):**
```
F043 is PATTERN_30@v1 Level 3. Retracted — the correlation was
a rearrangement of BSD, not arithmetic structure.
```

**As a gate in an ingestion call:**
```python
from harmonia.sweeps import sweep_signature
outcome = sweep_signature(coupling_check=CouplingCheck(...))
# raises SweepBlocked if outcome.overall == 'BLOCK' and not overridden
register_specimen.register(..., sweep_outcome=outcome)
```

## Version history

- **v1** 2026-04-20T23:45:00Z — first canonicalization as a symbol.
  Promoted from the pattern-library DRAFT entry (`pattern_library.md`
  promoted 2026-04-19 to strong advisory after F043 retraction). Five
  anchors at promotion (F043 Level 3; F015 / F041a / F013 / F045 all
  Level 1). Implementation at `harmonia/sweeps/pattern_30.py` (commit
  c71218321) with 14 passing tests. Graded severity schema matches
  `pattern_library.md` Pattern 30 entry verbatim — this symbol IS the
  pattern, now machine-resolvable in one call rather than re-read from
  prose across six documents.

  First symbol of type `pattern`. The type is introduced in this
  promotion; subsequent pattern-to-symbol migrations (Pattern 20, 21,
  19, 13, 18) follow the same template. Promotion of PATTERN_30 first
  is the proof-of-concept for the patterns-as-symbols thesis: if
  resolving `PATTERN_30@v1` lets the next Harmonia skip ~60 lines of
  re-reading across three files, the approach is validated.
