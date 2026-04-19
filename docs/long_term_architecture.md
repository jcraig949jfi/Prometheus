# Long-Term Architecture: A Version-Controlled Empirical Audit Substrate for Computational Mathematics

**Document version:** v2 (2026-04-19). Revised from v1 (`b81aa56f`) after
external frontier-model critique. Revision history at bottom.

---

## READ THIS FIRST

This document describes the intended long-term shape of Project Prometheus as a **software + epistemic substrate** for recording, auditing, and eventually querying empirical measurements in mathematics (and later, in physics and other exact sciences). It is not a description of a research result, a benchmark, a cognitive-architecture proposal, or a paper in preparation.

**Explicit framing for frontier-model reviewers:**

- This is a **long-term modeling exercise**, currently at prototype scale. Current implementation covers a narrow corner of computational number theory (LMFDB elliptic curves, number fields, modular forms, related L-functions). The architecture is designed to generalize far beyond this scope but has not yet been tested outside it.
- The goal is a **version-controlled empirical audit substrate over computational mathematics** — not proof search, not a capabilities evaluation, not a publication-ready dataset. The question the system answers for any measurement is *"what was measured, under what conditions, and does the result survive independent re-measurement?"* — not *"is this a new theorem?"* (An earlier version of this document phrased the goal as "raw mathematical truth"; a reviewer correctly pointed out that an empirical-sampling approach is not in the business of truth-claims, it's in the business of audit infrastructure. The correction matters: truth is the province of proof; audit is the province of this document.)
- There is **no near-term plan to publish papers**. The artifact being built is the tool, not the findings produced by the tool. Findings are instrumented byproducts of exercising the tool; the tool is the deliverable.
- This is **bottom-up, not top-down**. We are not deriving from a philosophical framework about what mathematics is or what intelligence requires. We are recording what happens when specific tests are run against specific data, with enough provenance that future readers (human or machine) can reproduce or refute every claim.
- Please do **not** browse external URLs, repositories, or prior conversations. Reviews should be grounded in this self-contained document. If information is missing, please say so rather than inferring from context.
- Please cite specific passages when offering critique; memory-augmented inference without citation is how prior reviews drifted into wrong framing.

The document describes five layers, their current state, and their intended evolution. Critique on any layer is welcome; the final section enumerates specific questions we would find most valuable.

---

## 1. Project goal, plainly stated

Most computational-mathematical knowledge today lives in papers: each paper observes something, notation varies between authors, cross-referencing is human-labor-intensive, and machine-queryable aggregation across papers is extremely limited. A graduate student exploring, say, "what's been established empirically about the rank-2 BSD identity at high conductor" spends weeks reading papers and often cannot replicate the numerical claims without substantial effort. (Note: "what's proved" is a distinct question that belongs to theorem-prover tooling, not to this substrate. We record what has been *measured*, not what has been *proved*.)

We are prototyping a substrate in which measurements are first-class objects:

- Each measurement has a **unique identifier** (F-ID for the claim, P-ID for the coordinate system or projection being measured through)
- Each measurement carries **full provenance** (which dataset, which null model, which parameters, which code version, which worker produced it)
- Each measurement is **cross-referenceable** to others in the same substrate by version-pinned references
- Each measurement is **auditable**: the recorded verdict (survives / collapses / tautology / provisional / etc.) is derived under explicit discipline and can be re-run from the stored specification
- **Retractions and corrections are first-class** events, preserved historically, not silent edits

The aspiration: when this substrate is dense enough across enough mathematical domains, a reader — human or AI — can query it as a queryable map of what has been measured, rather than grepping papers. We are a long way from that. The current prototype covers a few dozen features measured against a few dozen projections in one corner of number theory. The architecture is designed for the larger target.

A second-order motivation: if synthetic reasoning (LLMs, automated theorem provers, or their successors) continues developing in the direction it currently appears to be going, a structured substrate of this kind becomes much more valuable than the equivalent content scattered across unstructured papers. We consider this a reasonable bet but not a certainty; the substrate has value as a careful audit tool even if synthetic reasoning doesn't materialize as expected.

## 2. Five-layer architecture, with one honest correction

An earlier version of this document presented five layers as if they were cleanly independent. On review, the accurate picture is:

- **Layer 1 (Data) and Layer 5 (Replication) are genuinely separable concerns.** Data sits under the system; replication sits orthogonally across it.
- **Layers 2 (Measurement), 3 (Discipline), and 4 (Symbolic) are a single coupled system.** Null protocol (L3) defines the semantics of `+1/+2` verdicts (L2); those verdicts are produced by calling operator symbols (L4) that encode the null-protocol procedures. Changes in any of the three cascade through the other two.

We continue to describe them as three layers because they do three distinguishable *roles* — measure, discipline, encode — but a reader should expect that modifying any one requires thinking about the other two. There is one coupled kernel with three faces, plus two flanking layers.

### Layer 1 — Data sources and mirrors

At the bottom are the authoritative mathematical databases and our mirrors of them.

- **LMFDB Postgres mirror** at a local host: the source of truth for elliptic curves, number fields, modular forms, L-functions, genus-2 curves, and Artin representations. Tables include `ec_curvedata` (~3.8M rows), `nf_fields` (~22M rows), `bsd_joined` (~2.5M rows), `lfunc_lfunctions` (~24M rows), others.
- **External standards artifacts**, pinned by cryptographic hash: IUCr CIF dictionary (crystallography), OpenQASM 3.0 specification (quantum computing), ngspice manual (electrical engineering), NIST CODATA fundamental constants. These are present but not yet integrated into the measurement layer. They represent the first step toward cross-domain generalization.
- **Our own registry** — a Postgres schema `signals.specimens` recording measurements produced inside the system, with JSONB provenance fields.
- **Live-state Redis mirror** — derived from the measurement and symbolic layers, provides sub-millisecond cross-machine reads.

This layer is straightforward. Current data volume is modest (Postgres fits on one host; Redis state is ~1 MB). The layer is intentionally boring.

### Layer 2 — Measurement (the "battery")

The measurement layer is where tests get run. Its primitives are:

- **F-IDs**: each F-ID represents one specific empirical claim. Examples: `F011` is the measured ~38% deficit in first-gap variance of rank-0 elliptic-curve L-functions relative to the GUE pair-correlation prediction. `F003` is the BSD parity identity (theorem, used as calibration anchor). `F043` (recently retracted) was a claimed correlation between `log(Sha)` and a period-times-Tamagawa product.
- **P-IDs**: each P-ID is a coordinate system or projection through which F-IDs can be measured. Examples: `P020` is conductor-decile conditioning, `P028` is Katz-Sarnak symmetry-type stratification, `P104` is block-shuffle-within-conductor-decile permutation null.
- **The tensor** `T[F, P]` — a 2-dimensional integer matrix, rows indexed by F-IDs, columns by P-IDs, values in `{-2, -1, 0, +1, +2}`:
  - `-2`: coordinate system provably collapses this claim (known artifact)
  - `-1`: tested, claim does not resolve
  - `0`: untested
  - `+1`: resolves at conventional significance under some null
  - `+2`: resolves and survives the claim-appropriate stricter null (currently block-shuffle)
- Scripts that actually execute measurements — one per F-ID, committed alongside their results.

**Graduated verdict labels (planned Layer 2 extension).** The current tensor cell carries only the verdict integer. A reviewer correctly pointed out that different `+2` cells have different verification depth and are not cross-comparable. The planned extension tags each `+2` cell with its verification level:

- `+2@shuffle` — survives the claim-appropriate block-shuffle null (one implementation, one machine)
- `+2@replicated` — same code path agrees across independent machines / worker sessions
- `+2@reimplemented` — two independent code paths (clean-room alternates) agree byte-for-byte on the SIGNATURE tuple
- `+2@independent_source` — verified against a non-primary data source (e.g., LMFDB measurement verified by Sage / Magma / lcalc)
- `+2@anchor` — theorem-level calibration (F001–F009 set)

The tag does not replace the integer; it lives alongside it. A future reader can filter the tensor by verification depth. Under this scheme, the existing 44 `+2` cells are all `+2@shuffle` until Track D promotes any of them to higher tags.

**The tensor is, at its honest limit, a typed relation graph presenting as a matrix.** Different cells have different claim classes, different nulls, different sample sizes, different verification depths. The matrix form is useful at current scope (one domain, ~100 cells) but will stop being the right abstraction as scope widens. Planned future evolution is per-cell structured summary carrying effect size + uncertainty + null-spec + verification tag, with the matrix retained as an index.

Current scope: 31 features × 37 projections = 1147 possible cells; ~100 non-zero (about 9% density).

### Layer 3 — Discipline layer

The discipline layer is what keeps the measurement layer honest. Its primitives are:

- **Pattern library** — a growing collection of recognized failure modes, each with canonical anchor cases. Roughly 30 patterns exist; about 10 are formally promoted to "apply without exception." Recent additions include Pattern 30 (algebraic-identity coupling detection), which now has five severity levels 0–4 from CLEAN to IDENTITY. Patterns are versioned and immutable at each promoted version.
- **Null-protocol v1** — a written discipline specifying, for each of five claim classes, which null model is appropriate. Moment/ratio under conductor scaling uses conductor-decile block-shuffle. Rank-slope interactions use rank-bin block-shuffle. Construction-biased samples require a frame-based resample (not permutation). Algebraic-identity claims refuse null and invoke Pattern 30.
- **Retraction machinery** — when a measurement is found invalid (e.g., F043's algebraic coupling), the tensor cells are demoted to `-2`, the F-ID's tier changes to `killed`, the description is rewritten with the proof of invalidity, and the retraction is logged in a pending-decisions record. Old measurements remain accessible via git history.
- **Versioning rules** (`VERSIONING.md`) — every symbol carries an integer version, a timestamp, a `previous_version` link, an explicit precision declaration, and versioned references to its dependencies. Promoted versions are **immutable** — corrections create new versions, never rewrite old ones. Precision changes (in either direction — improvement or reduction) trigger version bumps.

### Layer 4 — Symbolic

Layer 4 encodes the compound primitives of inter-agent communication as versioned objects with full derivation trails. This is the most novel piece of the architecture.

- **Symbol types (current)**: `operator` (a procedure with pinned parameters — e.g., `NULL_BSWCD@v2` is block-shuffle-within-conductor-decile null, 300 perms, seed 20260417, balanced-stratifier guard built in), `shape` (a structural pattern descriptor like `LADDER`), `constant` (a numerical value with declared precision — e.g., `EPS011@v2 = 22.90 ± 0.78 %` with audit status), `dataset` (a pinned SQL query returning an exact row count), `signature` (a tuple schema for reporting findings).

- **Planned symbol types (extensions).** Two extensions are under consideration:
  - **`code_artifact`** — source code as a first-class versioned, hash-pinned symbol. Currently, operators reference their implementation via `harmonia/nulls/block_shuffle.py::bswcd_null@<commit>`; the code itself is not a symbol. Promoting code to a symbol type makes it: content-addressable (sha256 of the file), interface-bound (declares which operator symbol it implements), dependency-tracked (Python version, libraries with pinned versions), and equivalence-testable (multiple `code_artifact` symbols can implement the same `operator` interface and be behaviorally checked against each other — which is exactly what Track D replication needs). Extends cleanly from the external-artifacts work already done for IUCr CIF / OpenQASM / CODATA (same hash-pinning pattern, just applied to procedures instead of specifications).
  - **`sampling_intent`** — a declaration on any `dataset` symbol stating whether the dataset is *exhaustive-to-a-bound* (e.g., all EC of conductor ≤ N), *heuristically-sampled* (e.g., first 1000 of a search), or *pathologically-selected* (e.g., rank-record constructions from Stein/Elkies/Dujella). This makes the MNAR discussion structurally present in data provenance rather than confined to prose disclaimers. A verdict on an exhaustive dataset is epistemically different from a verdict on a pathologically-selected one; the substrate should encode that difference.

Neither extension is implemented yet; both are architecturally consistent with the existing scheme and would compose without breaking current symbol resolvers.
- **Redis key layout** (base Redis, strings/hashes/sets/streams only): `symbols:<NAME>:v<N>:def` (immutable JSON), `symbols:<NAME>:v<N>:meta` (immutable frontmatter hash), `symbols:<NAME>:latest` (mutable version pointer), `symbols:<NAME>:versions` (append-only sorted set), `symbols:by_type:<type>`, `symbols:refs:<ref>@v<N>`.
- **Reference grammar** — every reference to a symbol in inter-agent communication must include `@v<N>`: `NULL_BSWCD@v2[stratifier=torsion_bin]`, not `NULL_BSWCD`. References to non-symbol entities (F-IDs, P-IDs, Patterns) use `@c<short_commit>` until they're retrofitted into the symbol registry. A validator rejects unversioned references.
- **Provenance chain** — every symbol's MD carries its derivation history, references to papers (with DOI/arXiv), implementation path + commit hash, and a version history log. A future reader following the chain can reconstruct how and why each symbol was introduced.
- **External symbol extension** — the IUCr CIF, OpenQASM, ngspice, and CODATA artifacts downloaded earlier are positioned to become external symbols (`IUCr:cif_core@v2024.1`, etc.), giving the system a way to reference authoritative external standards with the same hash-pinned discipline we apply internally. Not yet integrated.

The bet in this layer is that versioned, cross-referenced, machine-queryable primitives are a better substrate than free prose for either (a) multiple worker sessions coordinating on the same measurement, or (b) a future automated reasoning system attempting to ingest the corpus. Neither of these is proven; Layer 4 is where the most speculative architecture lives.

### Layer 5 — Replication and independence

The fifth layer is intentionally thin at this time. It represents the discipline that turns "internally consistent measurements" into "measurements corroborated under conditions that do not share a single point of failure." A reviewer correctly pointed out that this is more than one dimension:

**Four dimensions of replication, in order of increasing independence:**

1. **Cross-machine, same code.** Run the same operator on the same data from a second machine, check byte-equivalence of SIGNATURE tuples. Catches environment-specific bugs (library version drift, floating-point determinism issues, filesystem-encoding issues like the Windows-backslash bug we already caught and fixed in the symbol layer). Cheapest tier; does not catch code bugs.

2. **Cross-implementation, same statistic.** Two independent code paths implementing the same operator interface. This is what Track D currently specifies: a clean-room reimplementation of `NULL_BSWCD` verified behaviorally against the original. Catches implementation bugs within the shared design.

3. **Cross-decomposition, different statistic.** The same empirical claim tested via a different statistical formulation — e.g., measuring F011's rank-0 residual via moment decomposition rather than first-gap variance, then checking whether both point at the same underlying effect. Catches bugs in the choice-of-statistic step, which cross-implementation cannot.

4. **Cross-source, different data pipeline.** The same computation run against a data source obtained from an independent pipeline — LMFDB vs Sage vs Magma vs lcalc. Catches bugs baked into the shared data provider.

Dimensions 1–2 can be achieved with current infrastructure (Track D's first delivery). Dimensions 3–4 require additional infrastructure (alternate statistics, Sage host setup) and will likely accumulate opportunistically rather than all at once.

**Failure mode this layer is meant to prevent**: "correlated implementations confirming the same mistake." Two workers running what looks like independent code but sharing a bug — either explicitly (copy-paste) or structurally (both read the same buggy library) — will agree without testifying to anything real. Cross-machine-same-code is the weakest protection against this; cross-source-different-pipeline is the strongest.

**Current state**: Layer 5 exists as a written protocol and a deferred task (`docs/prompts/track_D_replication.md`). External review has repeatedly identified this as the single most important missing piece. It remains deferred because current project priorities are tool-building outward rather than audit-hardening inward, but any claim that proposes to live in the substrate long-term should eventually carry a verification tag from dimensions 2–4, not just dimension 0 (single implementation, single machine, which is where everything currently sits).

---

## 3. How a single measurement flows through the system

A concrete trace for one measurement:

1. A worker session reads `docs/prompts/` to find an outstanding task, or reads `agora:work_queue` in Redis for a claimed task.
2. To identify the target claim, it resolves the F-ID via `agora.tensor.feature_meta(F)` against the Redis mirror.
3. For the dataset, it resolves `Q_EC_R0_D5@v1` (a dataset symbol) and executes its pinned SQL against the LMFDB Postgres mirror, producing an exact-row-count dataframe.
4. For the null model, it resolves `NULL_BSWCD@v2[stratifier=torsion_bin, n_perms=300, seed=20260417]` (an operator symbol) and invokes the pinned implementation.
5. It computes the statistic of interest, gets a z-score, formats a SIGNATURE@v1 tuple including all the inputs plus the output.
6. It registers the SIGNATURE in `signals.specimens` Postgres, updates the appropriate cell in the tensor via `build_landscape_tensor.py`, and pushes the new tensor state to Redis via `agora.tensor.push`.
7. Commit to git with the SIGNATURE embedded in the commit message.
8. Post a `WORK_COMPLETE` message on the Redis sync stream.
9. The Cartographer viewer, polling the tensor version every 5 seconds, reflects the new cell color on the heatmap.
10. The conductor session (typically the human or a dedicated LLM role) reviews the result and may accept, demote, or queue a re-audit.

Steps 1–9 are all implemented today for number-theoretic measurements. Step 10 is typically human + LLM hybrid.

## 4. Intended evolution

**Current (late April 2026):** ~100 tensor cells, ~42 projections, ~31 features, 5 seed symbols, 4 external artifacts pinned but not integrated, single code path per operator, no cross-source verification, one retraction demonstrated (F043), one survival-candidate under one properly-specified test (F011 rank-0 residual).

**Near-term (weeks to a few months):** Track D (replication pilot on F011), Sage integration for independent-source verification of rank-0 residual claims, extend the external-symbols layer (4 standards integrated as first-class references), push tensor density from ~9% to ~25–30% where aggregate structural claims become defensible, cross-machine replication habit established. Graded Pattern 30 applied during cell-filling to catch more F043-class failures before they land in the tensor.

**Medium-term (months to a year):** A second mathematical domain (number-field arithmetic dynamics, automorphic forms beyond weight-2, or analytic number theory proper) with its own F-ID and P-ID set bridged to the existing corpus via shared symbols (root number, conductor, CM discriminant). Multi-model-family workers to reduce single-implementation bias at generation. At least one frontier claim that has survived replication across two independent implementations and at least one non-LMFDB data source.

**Long-term (multi-year):** Extension beyond pure mathematics into physics. CODATA constants already pinned; the same symbol/versioning/null-protocol discipline would apply to, e.g., measurements of fundamental constants across independent experimental facilities, or to cosmological observations across independent telescopes. The long-term vision is infrastructure that can hold measurements from number theory through statistical mechanics through astronomy in one version-disciplined substrate.

**Very long-term (aspiration, not plan):** the substrate becomes useful to researchers or AI systems who weren't part of building it. At that point the question of whether it becomes a queryable tool for "exploring dimensions we only see shadows of" gets tested empirically by whether people use it. We do not have strong priors about when or whether that happens.

## 5. Explicit scope and non-goals

We are not:
- Proving theorems or generating novel mathematics
- Running a capabilities benchmark for any AI system
- Producing a publication-ready dataset of discoveries
- Building a cognitive architecture or intelligence framework
- Pursuing philosophical claims about the nature of mathematics
- Attempting to replace peer-reviewed literature

We are:
- Recording measurements on mathematical data with provenance
- Auditing those measurements against appropriate null models
- Maintaining a cross-referenceable substrate of compound primitives
- Retracting what fails audit, keeping the retraction accessible
- Extending incrementally to new domains when the architecture supports it
- Betting that this substrate has value even without synthetic reasoning, and more value if synthetic reasoning emerges as expected

## 6. Questions for frontier-model critique

We would find most valuable pushback on the following, specifically:

**Architecture questions:**
- Is the five-layer separation load-bearing, or are we describing functionally entangled concerns as if they were distinct layers?
- Is Layer 4 (the symbol registry with strict versioning) the right substrate for the long-term vision, or is it over-engineered for current scope and likely to collapse under its own bureaucracy as we scale?
- Are there missing layers? Model-based landscapes, topological/geometric extensions, proof-theoretic layers, something else we should design against now even if we don't build it soon?

**Methodology questions:**
- The MNAR (missing-not-at-random) problem with the tensor is known to us. Can the architecture itself structurally address it, or is MNAR an inherent limit of any measurement-recording system that doesn't control its own sampling? Specifically, would adding "controlled sampling of (F, P) pairs at some rate" as a layer-2 primitive help, or just pretend to help?
- The "+2 cells are not cross-comparable" problem is also known. Is there a way to normalize the +2 verdict across claim classes so it becomes a meaningful aggregate, or is per-cell provenance the best we can ever do?
- The graded Pattern 30 levels 0–4 are a response to one anchor (F043). Does the specific taxonomy generalize, or are we over-fitting to the BSD-identity failure mode?

**Vision questions:**
- The "synthetic reasoning substrate" thesis is a bet. Under what scenarios does the substrate have value even if synthetic reasoning fails to emerge in the expected form? Can we identify the minimum useful outcome and the maximum plausible outcome?
- The extension from mathematics to physics (medium-to-long-term plan) assumes the discipline translates. What aspects of our current discipline are mathematics-specific and will break when applied to measurements with real physical units, systematic errors, and experimental uncertainty?
- The substrate is designed for a reader we cannot specify (future human or future machine). What design choices hedge against different reader hypotheses, and which ones commit us to one specific reader class?

**Failure-mode questions:**
- We have one retraction (F043). What failure modes would we not catch even with current discipline? Specifically, what F043-analogues could hide in non-BSD data at what severity levels?
- The system pauses and retracts in response to external review. What if external review stops happening, or becomes stylized? What self-review discipline should substitute, and at what review-frequency does the system start accumulating uncaught errors?
- The Pattern library has grown to ~30 entries. At what size does a pattern library become unusable as an operational checklist rather than background advisory? We don't know; we'd value a frontier-model instinct on this.

---

## Appendix — current artifacts, for reference

- `harmonia/memory/build_landscape_tensor.py` — canonical tensor definition (31 features × 37 projections)
- `harmonia/memory/coordinate_system_catalog.md` — 42 projection descriptions with tautology profiles
- `harmonia/memory/pattern_library.md` — 30 patterns including graded Pattern 30
- `harmonia/memory/symbols/` — symbol registry with VERSIONING.md rules; 5 promoted symbols at v1–v2
- `harmonia/memory/symbols/external/` — 4 external standards pinned by hash (IUCr, OpenQASM, ngspice, CODATA)
- `agora/symbols/` — Python helpers for push/resolve against Redis
- `agora/tensor/` — Python helpers for tensor read/write Redis mirror
- `cartography/viewer/` — HTML heatmap viewer; polls Redis every 5 seconds
- `docs/prompts/` — task specifications for delegated worker roles (Track A complete, Track B complete, Track D deferred)
- `docs/landscape_charter.md` — original project reframe from "find cross-domain bridges" to "describe the terrain"
- `harmonia/memory/decisions_for_james.md` — running log of judgment calls, retractions, and standing limits

This is a prototype. It is not finished; it is not intended to be finished any time soon. Critique on direction and architecture is more useful than critique on current measurements, which are narrow by design.

---

## Revision history

**v2** (2026-04-19) — absorbed external review of v1 (`b81aa56f`).

Corrections applied:
- Goal phrasing reframed: "raw mathematical truth" → "version-controlled empirical audit substrate." The prior framing implied a truth-ontology; the correct framing is infrastructure. An audit substrate does not make truth claims; it records what was measured under what conditions.
- Five-layer separation honesty added. Layers 2–3–4 are correctly characterized as a coupled tri-layer kernel (measure + discipline + encode) rather than three independent layers. Layers 1 and 5 remain genuinely separable.
- Layer 5 (replication) expanded from "clean-room reimplementation" to four distinct dimensions: cross-machine, cross-implementation, cross-decomposition, cross-source. The failure mode "correlated implementations confirming the same mistake" is now explicit.
- Layer 2 planned extension added: graduated verdict labels (`+2@shuffle`, `+2@replicated`, `+2@reimplemented`, `+2@independent_source`, `+2@anchor`). Existing `+2` cells are all at `@shuffle` level until verification tags catch up.
- Layer 4 planned extensions added: `code_artifact` symbol type (hash-pinned source code as first-class versioned entity, extends the external-artifacts pattern to procedures) and `sampling_intent` (exhaustive / heuristically-sampled / pathologically-selected — encodes MNAR concerns in data provenance).
- Tensor honesty: explicitly stated as "a typed relation graph presenting as a matrix"; the matrix form is usable at current scope but will not scale.

Queued for future (not yet scheduled):
- Pattern library hierarchy (expected to hit operational non-scalability around 80–120 entries; we are at ~30).
- Split claim types into distinct tensor semantics (empirical-statistical vs deterministic-invariant vs identity/tautology vs derived/composite). Correct taxonomy; large reshape.
- Pattern 30 generalization from algebraic-coupling-severity to where-the-information-leaked (definitional / computational / shared-dataset / sampling). Useful wider frame.
- Pattern-tagging with metadata so only relevant patterns load for a given claim class.

Pushed back on:
- Automated pre-registration gates on `+2` cells (too restrictive; graduated labels achieve the honesty goal without blocking measurement).
- Formal Agent Orchestration Layer as separate component (current human + conductor arrangement works; premature to formalize).
- Symbol de-duplication, equivalence detection, type inference (premature at 5 promoted symbols; revisit at ~50+).

**v1** (2026-04-19, `b81aa56f`) — initial version for first frontier-model review.
