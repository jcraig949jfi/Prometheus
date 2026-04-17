# Ergon Handoff — Start Here
## For the next Claude Code session
### 2026-04-17

---

## Current State

### What was done (2026-04-15 to 2026-04-17)

#### Session 2 (Apr 15): Agora polling test run
- Monitored Redis, tracked Batch 01 execution by Aporia (6/8 tests complete)

#### Session 2b (Apr 15-16): Active execution
- NF permutation null confirmed (Harmonia validated)
- AlignmentCoupling z=2.22 RETRACTED (seed artifact, 6/10 flat zero)
- P1.3 knot arithmetic re-encoding: null result (scorer bottleneck)
- GUE deviation: ~14% variance deficit (first-gap), not 40% (unfolding artifact)
- abc Szpiro controlled: decrease REAL at fixed bad-prime count (5 strata tested)
- Chowla N=10^8: SUPPORTED (0/100 violations)
- Artin linkage: CONFIRMED DEAD END (0 Artin L-functions in lfunc table)
- GradientTracker integration wired up
- CSV fallback for load_ec_rich and load_artin shipped

#### Session 3 (Apr 16-17): Tensor v2 + Explorer v2 + Fingerprints
**Tensor builder v2**: Rewrote to use Harmonia's DomainIndex loaders.
  - 7 domains -> 29 domains, 58K objects -> 5.08M objects
  - Three tiers: core (8), extended (22 w/ fingerprints), all (29)
  - EC scale-up: 10K -> 3.8M from local Postgres

**Gene schema v2**: 20 ACTIVE_DOMAINS with Harmonia feature indices (f0-fN).
  - 400+ domain pairs (was 49)
  - New: artin, ec_rich, belyi, bianchi, groups, oeis, chemistry, codata, pdg_particles, metabolism

**E-FP-1 (nf_cf)**: NF with continued fraction features of defining polynomial roots.
  - Loads from Postgres (22M NF), computes largest real root, CF expansion
  - 10 features: arithmetic + approximation modality

**E-FP-3 (artin_ade)**: Artin reps with ADE/Dynkin type classification.
  - Maps Galois labels (nTt) to root system types
  - 11 features: Artin invariants + is_weyl, is_cyclic, ade_rank

**Explorer v2 run** (5000 gen, 20 domains):
  - 60K hypotheses tested at gen 3000
  - 35 MAP-Elites cells filled, max depth 15
  - 72.6% killed at F1 (permutation null)

**CRITICAL FINDING: All survivors fail independent permutation null.**
  - 3 depth-15 survivors: all pdg_particles:f0 pairings, z<1 under permutation
  - 9 depth-12 survivors: all MI-on-small-samples artifacts, z<1
  - 5 depth-6 math-domain survivors: all noise under permutation
  - The battery passes hypotheses that permutation null kills
  - Root cause: coupling scorers measure feature GEOMETRY, not object pairing

### The Fundamental Problem (clear now)

The entire Ergon pipeline — tensor slicing, coupling scoring, battery testing —
operates on DISTRIBUTIONAL properties of features. Shuffling which specific
mathematical objects are paired does not change the coupling score because the
feature distributions are preserved.

This means:
1. **No object-level coupling detectable** by any current scorer (cosine, distributional, alignment, MI)
2. **Battery survival ≠ real structure** — the battery checks statistical significance of the coupling score, but the score itself is distributional
3. **MAP-Elites archive is populated by feature geometry artifacts**, not mathematical discoveries
4. **MI is especially bad** on small domains (pdg 226, metabolism 108, codata 286) — biased upward

### What needs doing

#### 1. Fix the battery: add permutation null as F0
The permutation null should be the FIRST test, not an afterthought. If shuffling
object labels within a domain doesn't change the coupling score, the hypothesis
is dead regardless of what other tests say. This would kill 100% of current
survivors and make the battery honest.

#### 2. Rethink the coupling methodology
The fingerprints report (Aporia) identified the right direction: mathematical
connections are SPECIFIC (knot K's Alexander polynomial evaluates to a specific
algebraic integer in a specific number field). Random-pair coupling cannot detect
this. Need MATCHING-based approaches:
- Join on algebraic identities (Alexander discriminant = NF discriminant)
- Join on shared L-function (EC L-function = MF L-function via modularity)
- Join on operator eigenvalues (Hecke eigenvalue = NF invariant)

#### 3. Investigate the shadow archive
The shadow archive (13MB at gen 3000) maps which domain pairs are dead zones.
Even though the coupling scores are distributional, the PATTERN of kills
(which tests kill which pairs) may reveal real structure about the tensor geometry.

---

## Infrastructure

- Redis: localhost:6379, password=prometheus
- Postgres on M1: lmfdb (30M+ rows, ec_curvedata 3.8M, artin_reps 798K, nf_fields 22M)
- lfunc_lfunctions: 342 GB, 24M rows, 1 index (conductor only), NO Artin L-functions
- Tensor v2: core (4.2M, 96 feat), extended (4.6M, 202 feat), all (5.1M, 263 feat)

## Key Files
- `ergon/tensor_builder.py` — v2, Harmonia loaders, 3 tiers
- `ergon/run_explore_v2.bat` — double-click explorer (22 domains)
- `forge/v3/gene_schema.py` — updated ACTIVE_DOMAINS (20), ACTIVE_FEATURES (f0-fN)
- `harmonia/src/domain_index.py` — load_nf_cf(), load_artin_ade(), CSV fallbacks
- `harmonia/src/landscape.py` — report_to_gradient_tracker() bridge

## Warnings
- Phoneme framework UNVALIDATED — use distributional scorer only
- MI biased on small N — pdg (226), metabolism (108), codata (286) produce spurious MI
- AlignmentCoupling W matrix is SEED-DEPENDENT — always replicate across 5+ seeds
- Permutation null kills ALL current tensor coupling claims — scorer measures geometry not objects
