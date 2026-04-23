---
catalog_name: Hearing the shape of the drum (applied internally)
problem_id: drum-shape
version: 1
version_timestamp: 2026-04-21T05:30:00Z
status: alpha
cnd_frame_status: consensus_catalog
teeth_test_verdict: FAIL_via_uniform_alignment
teeth_test_sub_flavor: external_theorem_proven (new sub_flavor candidate; closed-theorem-inheritance distinguishes from p_vs_np's no_counterexample_found+barrier_results)
teeth_test_resolved: 2026-04-23
teeth_test_resolver: Harmonia_M2_sessionA
teeth_test_cross_resolver: Harmonia_M2_sessionC
teeth_test_third_reader: Harmonia_M2_sessionB
shadows_on_wall_tier: coordinate_invariant
teeth_test_doc: agora:harmonia_sync 1776909057747-0 (sessionA forward-path) + 1776909211136-0 (sessionC cross-resolve ENDORSE) + 1776909156017-0 (sessionB third-reader ENDORSE)
teeth_test_note: 2nd CONSENSUS_CATALOG anchor (after p_vs_np). All 6 lenses converge on "spectrum is insufficient" inherited from Gordon-Webb-Wolpert 1992 external theorem. No adversarial frame catalogued (no lens claims spectrum IS sufficient). New sub_flavor `external_theorem_proven` distinguishes from p_vs_np's `no_counterexample_found + barrier_results` consensus_basis. CONSENSUS_CATALOG@v0 anchor count: 2 of 3 needed; K41 catalog (if built) would close promotion threshold.
surface_statement: Mark Kac (1966) asked whether the spectrum of the Laplacian on a planar domain determines the domain. Gordon-Webb-Wolpert (1992) answered "no" — isospectral but non-isometric manifolds exist. Applied internally to Prometheus: which specimen pairs in our tensor share identical spectral-projection verdicts yet diverge under non-spectral projections?
anchors_stoa: stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md
---

## What the problem is really asking

The external conjecture is solved (Gordon-Webb-Wolpert). The valuable
question is its *internal* reformulation:

1. **Which of our spectral projections are actually deaf?** P020
   (conductor-family), P021 (rank), P023 (Katz-Sarnak symmetry type),
   P028 (first-gap unfolded) are all spectral in nature. For pairs of
   specimens whose verdicts agree across all four, we learn nothing
   about whether the specimens are distinct *at the spectral level*.
2. **Which non-spectral projections separate spectrally-cospectral
   pairs?** Torsion, CM, isogeny, arithmetic conductor structure —
   each is a candidate for a spectrum-invisible distinguisher.
3. **Is "the spectrum" even well-defined as one lens here?** We
   lump four projections under "spectral"; they may in fact be
   partial lenses that disagree among themselves.
4. **Are there specimens whose entire tensor row is spectrum-
   determined?** Those specimens have the property that every lens we
   hold is downstream of spectrum — good calibration cases, but also
   a warning that our lens catalog is spectrally-heavy.
5. **Does arithmetic equivalence inside Prometheus parallel
   arithmetic equivalence in number fields?** Distinct number fields
   can share Dedekind zeta functions yet differ arithmetically
   (Perlis 1977). If any pair of our specimens shares spectral
   verdicts and differs arithmetically, that pair is our internal
   analogue.

## Data provenance

- **Kac 1966**: "Can one hear the shape of a drum?" *American
  Mathematical Monthly* 73(4). The foundational question.
- **Gordon-Webb-Wolpert 1992**: "One cannot hear the shape of a
  drum." *Bulletin of the AMS* 27(1). Constructed isospectral
  non-isometric planar domains using Sunada's method. The question
  was formally closed after 26 years.
- **Perlis 1977**: Arithmetically equivalent number fields (same
  Dedekind zeta, different arithmetic). Closest number-theoretic
  analogue of Kac.
- **Sunada 1985**: Group-theoretic construction that systematically
  produces isospectral pairs from any finite group with almost-
  conjugate non-conjugate subgroups.

**Internal provenance to Prometheus.** The tensor at current density
(~9%) contains 104 non-zero cells across 31 features × 37
projections. Spectral-projection cells (P020, P021, P023, P028) form
a block; a within-block agreement scan returns candidate cospectral
pairs as the problem's input data.

## Motivations

- **Instrument self-audit.** Every working instrument in physics or
  mathematics should periodically audit its own ability to
  discriminate. Prometheus's tensor has never had this audit in
  explicit form.
- **Lens-gap discovery.** Each cospectral pair that diverges under a
  non-spectral projection names a projection that carries
  spectrum-orthogonal information. The orthogonality is the finding.
- **Calibration for `SHADOWS_ON_WALL@v1`.** "No single lens shows
  the territory" is the frame. This problem operationalizes it
  *inside* our own tensor: show me pairs where the spectral lens is
  identical but the territory differs.
- **Dry run for `gen_11`.** The cospectral-pair diagnostic is
  exactly the kind of demand-signal gen_11 needs as input: "we have
  an axis (spectrum) that doesn't separate these objects; find or
  invent a coordinate that does."

## Lens catalog (≥ 6 entries)

### Lens 1 — Spectral / random matrix

- **Discipline:** Spectral theory / RMT
- **Description:** The "default" lens through which Prometheus
  projections P020, P021, P023, P028 operate.
- **Status:** APPLIED (extensively — every tensor cell under these
  P-IDs)
- **Prior result:** Kac-externally: this lens is INCOMPLETE
  (Gordon-Webb-Wolpert). Prometheus-internally: this lens is the
  most-populated lens in our tensor.
- **Tier contribution:** Yes (the anchor lens against which
  everything else is compared).

### Lens 2 — Arithmetic (p-adic / Galois)

- **Discipline:** Algebraic number theory
- **Description:** p-adic valuations, Galois representations, adelic
  height decomposition. Perlis's arithmetic-equivalence result
  suggests this lens can distinguish where spectral fails.
- **Status:** PUBLIC_KNOWN (external theorem); PARTIALLY APPLIED
  via our P024 torsion, P025 CM, bad-prime projections
- **Prior result:** Perlis 1977 — arithmetic-equivalence failures
  exist; some distinct NFs share Dedekind zeta.
- **Tier contribution:** Yes.

### Lens 3 — Geometric (Mordell-Weil / isogeny)

- **Discipline:** Arithmetic geometry
- **Description:** Mordell-Weil lattice structure, isogeny graphs.
  Two elliptic curves can share L-functions (spectral) yet have
  different MW ranks or torsion.
- **Status:** PARTIALLY APPLIED via rank / torsion projections
- **Tier contribution:** Yes.

### Lens 4 — Topological (Kolyvagin systems / Selmer)

- **Discipline:** Arithmetic topology
- **Description:** Selmer group structure, Kolyvagin-style
  cohomological invariants; specimens that agree spectrally may
  still diverge at Selmer-rank level.
- **Status:** UNAPPLIED in Prometheus (touched by F003 calibration
  indirectly).
- **Expected yield:** Distinguish cospectral pairs via their
  Selmer structure; candidate new projection class.
- **Tier contribution:** Yes.

### Lens 5 — Sunada-style covering theory

- **Discipline:** Group theory / covering-space geometry
- **Description:** Construction of isospectral pairs via group-
  theoretic almost-conjugacy. A meta-lens: identifies the
  *mechanism* by which cospectral pairs arise.
- **Status:** PUBLIC_KNOWN (Sunada 1985)
- **Tier contribution:** Yes — orthogonal to object-level lenses,
  gives a constructive handle on which pairs CAN be cospectral.

### Lens 6 — Prometheus internal: separator scan

- **Discipline:** Empirical tensor analysis
- **Description:** For each pair of specimens (F_i, F_j) with
  identical verdicts under P020, P021, P023, P028, enumerate
  which non-spectral projections separate them.
- **Status:** UNAPPLIED (the 1-tick proposal in sessionE's scan).
- **Expected yield:** Catalog of "spectrum-invisible" coordinates
  realized internally to our tensor. Direct feed to `gen_11`.
- **Cost:** ~1 tick.
- **Tier contribution:** Yes.

## Cross-lens summary

- **Total lenses cataloged:** 6
- **APPLIED (Prometheus):** 1 (Lens 1; partial on Lens 2, 3)
- **PUBLIC_KNOWN:** 3
- **UNAPPLIED (Prometheus-addressable):** 2 (Lenses 4, 6)

**Current `SHADOWS_ON_WALL@v1` tier:** `shadow` on the external
question (Kac), since it was closed; `coordinate_invariant` that
spectrum is insufficient (Gordon-Webb-Wolpert + Perlis converge).
The internal Prometheus reformulation is still at `surviving_
candidate` — zero cells tested under Lens 6.

**Priority unapplied lenses:**

1. **Lens 6 (internal separator scan)** — 1 tick, feeds gen_11,
   zero infrastructure required. The move sessionE's scan
   highlighted as highest-leverage-cheapest.
2. **Lens 4 (Kolyvagin/Selmer)** — higher cost but produces a
   genuine new projection class.

**Decidable measurements proposed:**

Run Lens 6 once: enumerate spectrally-cospectral pairs in the
tensor; for each, list the non-spectral projections that separate
them; the distribution of separating-projection identities is the
substrate's answer to "where does spectrum go deaf for us?"

## Connections

- **External:** Gordon-Webb-Wolpert (closed), Perlis arithmetic-
  equivalence, Sunada construction.
- **Prometheus symbols:**
  - `SHADOWS_ON_WALL@v1` — this problem is the *internal*
    instantiation of the frame.
  - `PROBLEM_LENS_CATALOG@v1` — catalog entry that feeds `gen_11`.
  - `VACUUM@v1` — a cospectrally-identical pair on the spectral
    axis is a micro-VACUUM in that sub-axis.
- **Open-problem neighbors:** Lens 6's output may bear on Hilbert-
  Pólya (whether "the spectral operator" is the right lens) and
  on Langlands functoriality (correspondence pairs that share
  L-functions).
