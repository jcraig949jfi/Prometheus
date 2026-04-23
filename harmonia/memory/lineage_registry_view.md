---
name: LINEAGE_REGISTRY view (Pattern-30 lineage classifications by F-ID)
purpose: Surface `harmonia/sweeps/retrospective.py::LINEAGE_REGISTRY` as a navigable Markdown view. The registry is the substrate's source-of-truth for per-F-ID Pattern-30 lineage classification (closes the manual Pattern-30 gate per sessionA SUBSTRATE_AUDIT 1776902585762-0). Closes axis-1 sprawl observation #5 (concept_map.md): "LINEAGE_REGISTRY (Pattern 30 metadata) lives in Python code; future Harmonia looking for 'what's F045's lineage classification' has to grep Python."
source_of_truth: harmonia/sweeps/retrospective.py::LINEAGE_REGISTRY (Python dict — canonical; this file is auto-generated for human discovery)
regeneration: re-run `python -m harmonia.runners.regen_lineage_registry_view` (when shipped) OR hand-update from source dict; this MD is a view, not a source
discipline: never edit this MD as the source-of-truth — edit retrospective.py first, then regenerate. Pattern-17 discipline (avoid double-source).
generated_by: Harmonia_M2_auditor 2026-04-23 (axis-1 consolidation candidate #3)
---

# LINEAGE_REGISTRY view

Per-F-ID Pattern-30 lineage classification, surfaced from
`harmonia/sweeps/retrospective.py::LINEAGE_REGISTRY` for navigation. This is
the substrate's machine-readable record of which F-IDs are correlation-bearing
(and therefore subject to Pattern-30 algebraic-coupling audit), which are
non-correlational (variance deficit / existence / density / calibration),
which are killed (no correlation content to audit), and which are construction-
biased (frame hazard, Class-4 null required).

The registry was completed during this session per sessionA's substrate-audit
(2026-04-22, sync `1776902585762-0`); it closes the manual Pattern-30 gate that
had been riding along since gen_06 shipped. All 19 F-IDs catalogued in
`build_landscape_tensor.py` are now classified.

## Type distribution

| Type | Count | Verdict semantics |
|---|---|---|
| `killed_no_correlation` | 11 | killed F-IDs with no correlation content; auto-CLEAR |
| `algebraic_lineage` | 5 | correlation-bearing; subject to Pattern-30 audit (CLEAR / WARN / BLOCK per Level 0-4) |
| `non_correlational` | 2 | variance-deficit / fit-intercept type; no X-vs-Y coupling to audit |
| `frame_hazard` | 1 | construction-biased sample (Class-4); NULL_BSWCD insufficient; PROVISIONAL pending frame-based resample |

## By-F-ID table

### `algebraic_lineage` (5 F-IDs — Pattern-30 active)

| F-ID | Pattern-30 verdict | Rationale (one-line) | Cross-refs |
|---|---|---|---|
| F013 | WARN (Level 1) | spacing-rigidity slope vs rank; algebraic component small | F011, F003 |
| F015 | WARN (Level 1) | szpiro_ratio vs conductor; log-N-in-denominator partial coupling | F003 |
| F041a | PARTIAL_PENDING | rank-2+ moment-slope monotone in nbp; CFKRS arithmetic-factor coupling pending | F011, F045 |
| F043 | BLOCK (Level 3) | RETRACTED: BSD-Sha "anticorrelation" was rearrangement of BSD identity | F003 |
| F045 | WARN (Level 1) | isogeny-class-size murmuration; Spearman 0.455 with nbp axis | F041a |

### `non_correlational` (2 F-IDs — N/A_NON_CORRELATIONAL)

| F-ID | Claim shape | Rationale (one-line) | Cross-refs |
|---|---|---|---|
| F011 | variance_deficit | GUE first-gap deficit ε₀ = 22.90 ± 0.78 % at z=29σ; fit intercept not correlation | F013, F042, F043 |
| F014 | existence_density | Lehmer Salem-density in (1.176, 1.228); existence claim, not correlation | (none) |

### `frame_hazard` (1 F-ID — PROVISIONAL pending Class-4 null)

| F-ID | Class-4 null reference | Rationale (one-line) | Cross-refs | Pending audit |
|---|---|---|---|---|
| F044 | (none yet — frame-resample task seeded; recommend RETRACTION per auditor 2026-04-22) | rank-4 corridor disc=conductor; LMFDB selection-frame artifact | F033 | audit_F044_framebased_resample (RETRACTED_AS_SELECTION_ARTIFACT recommended; conductor approval pending) |

### `killed_no_correlation` (11 F-IDs — N/A_KILLED, auto-CLEAR)

These F-IDs are at `killed` tier in `build_landscape_tensor.py`; their
existing kill verdicts subsume Pattern-30 — there is no correlation content
to algebraically couple. Listed for completeness; future auditors confirm
status before re-opening.

| F-ID | Kill rationale (one-line) | Cross-refs |
|---|---|---|
| F010 | NF backbone via Galois-label; killed under block-shuffle null | F022 |
| F012 | Möbius bias at g2c aut groups; did not reproduce at clean-n | (none) |
| F020 | Megethos axis (sorted log-normals); ρ=1.0 is artifact | (none) |
| F021 | Phoneme framework (5-axis); 1D predictor gave ρ=1.0 trivially | (none) |
| F022 | NF backbone via feature-distribution; z=0 under permutation | F010 |
| F023 | Spectral tail ARI=0.55; killed by conductor conditioning | (none) |
| F024 | Faltings explains GUE; y-intercept outside CI | F011 |
| F025 | ADE splits GUE; |Δvar| below threshold | F011 |
| F026 | Artin proof-frontier ratio; observed 1.8:1 not 50:1 | (none) |
| F027 | Alexander Mahler × EC L-value; z=0 under permutation | F014 |
| F028 | Szpiro × Faltings; ρ=0.97 is near-identity not coupling | F015 |

## How to use this view

- **Discover:** "what's F045's lineage classification?" → look at the algebraic_lineage table → "WARN (Level 1), Spearman 0.455 with nbp axis."
- **Audit:** before any new correlation claim against an F-ID, check this view. If the F-ID is in `algebraic_lineage` → Pattern-30 sweep applies; if `non_correlational` → wrong claim type for Pattern 30; if `killed_no_correlation` → re-opening requires kill-rationale-rebuttal first.
- **Edit:** never edit this MD. Change `harmonia/sweeps/retrospective.py::LINEAGE_REGISTRY` and regenerate. Source-of-truth discipline.
- **Cross-axis:** axis-1 (falsification battery; this map's home), axis-2 (mapping; F-IDs live in the tensor), axis-3 (symbolic storage; gen_06 sweeps consume this registry).

## Pending audits (per registry's `pending_audit` field)

| F-ID | Pending audit task ID | Status |
|---|---|---|
| F044 | `audit_F044_framebased_resample` | COMPLETE (auditor 2026-04-22, verdict RETRACTED_AS_SELECTION_ARTIFACT, conductor approval pending) |
| F045 | `audit_F045_stratified_within_nbp` | SEEDED (auditor 2026-04-22, awaiting claim) — closes the F041a/F045 independence question per F045's PARTIAL_CONFOUND verdict |

## Discipline — keeping the source-of-truth aligned with this view

When `harmonia/sweeps/retrospective.py::LINEAGE_REGISTRY` is updated:
1. Update the Python dict (canonical edit).
2. Re-generate this MD by re-running the registry-view writer (or hand-edit if changes are small; mark as hand-edited in version log).
3. Post COMMIT_UPDATE on `agora:harmonia_sync` referencing both the Python edit + this MD update.
4. Pattern-17 discipline: NEVER let this MD be the source-of-truth. Drift between the two would silently corrupt automated Pattern-30 sweeps that consume the Python dict.

## Cross-references

- `harmonia/sweeps/retrospective.py::LINEAGE_REGISTRY` — source of truth.
- `harmonia/memory/symbols/PATTERN_30.md` — graded severity Level 0-4; the gate this registry feeds.
- `harmonia/memory/decisions_for_james.md` 2026-04-22 entry by sessionA — substrate-debt closure milestone (all 6 NO_LINEAGE_METADATA F-IDs registered).
- `harmonia/memory/concept_map.md` axis 1 — sprawl observation #5 (this view closes it) and consolidation candidate #3 (this file delivers it).
- `harmonia/memory/build_landscape_tensor.py` — F-ID definitions (rows of the tensor); each F-ID's `tier` field composes with this registry's `type` field.

## Version history

- **2026-04-23 first generation** (Harmonia_M2_auditor) — view of LINEAGE_REGISTRY at retrospective.py commit-time. 19 F-IDs catalogued. Closes axis-1 sprawl #5 + consolidation candidate #3.
