# PROPOSAL V2-T01 (arm)

## Hypothesis

Battery-output equivalence is a strictly weaker relation than the equivalence the
Foundry actually needs for safe deduplication when composing future organisms.
Directional claim (falsifiable, not neutral): **naive deduplication of two
artifacts on the sole grounds that they emit byte-identical outputs across the
standard evaluation battery is UNSAFE by default**, because at least one of four
independent axes will diverge between such a pair for a non-trivial fraction of
cases: (a) behavior off the battery (extended/held-out inputs), (b) metered cost
(VM steps / tokens / resource footprint), (c) causal contribution when spliced
into composite organisms (residue-ablation heredity), (d) mutational-neighborhood
/ evolvability under the standard mutation operators. Dedup is safe only for the
subset of pairs that pass a pre-registered multi-axis equivalence test strictly
stronger than "matches on the battery" — and even then, discarding an artifact's
distinct lineage record is a separate, non-statistical veto (provenance is
never behaviorally certifiable).

## Motivating evidence

All found under `F:\Prometheus\SerendipityFoundry` (see operation log); none
under evidence_wiki (out of scope, not consulted).

1. **The existing lineage already deduplicates only at content level, never at
   behavioral level.** `SerendipityFoundryEngine/sfe/store.py`: the `artifacts`
   table key is `artifact_id` = *content address*; blobs are stored once by
   `blob_hash`. D10 Phase 2's frozen gate corpus (`D10phase2/phase2/GATE_SPEC.md`
   §1) is explicitly "4110 **content**-deduped genotypes" — dedup-by-bytes, not
   dedup-by-output. There is no precedent anywhere in this lineage for merging
   two structurally distinct artifacts because their outputs agreed.
2. **The one place this codebase came close — D8's hoard — deduped by a small
   FIXED PROBE SET, not the full battery, and still produced a warning sign.**
   `D8/REVIEW_PACKET.txt` §7: "Dedup by probe behavior [8 fixed probe inputs];
   cap 3000 FIFO." §16 "Memorization checks fired: 3 eval solutions
   byte-identical to dev solutions ... all three excluded from reuse evidence."
   The system's own discipline treats output-identity as *grounds for
   suspicion/exclusion*, not grounds for merging.
3. **Output-identical does not imply consequence-identical under composition.**
   D8 §16: z2 "appears inside 8 novel eval solutions across four families, yet
   ablation changes nothing — the search routes around it." An object can be
   reused and still be causally inert; the converse risk for dedup is symmetric
   — an object can look inert on the standard battery yet matter downstream.
4. **Byte/behavior identity in one frame does not transfer to identical causal
   role in a compositional frame.** `D7/audit/redteam_synthesis.txt`, transfer
   dimension: "14 of 20 xfer artifacts are byte-identical to proof artifacts ...
   however the crossing-critical nonlinear writer, modulus, base semantics, and
   endpoints genuinely differ." Identity on one axis coexists with decisive
   difference on the axis that actually matters for composition.
5. **Design philosophy already rejects silent dedup on a weaker equivalence.**
   `store.py` `idempotency_keys` docstring (schema v3, F5): "`request_hash`
   binds the SEMANTIC request ... so the same key with a materially different
   request is a conflict, **never a silent dedup**." This is the same shape of
   hazard: two things that look the same under a coarse key must not be
   silently collapsed.
6. **Provenance is a stated non-negotiable, independent of behavior.**
   `roles/Daedalus/CHARTER.md`, standing order 4: "Provenance is permanent. An
   imported artifact carries `origin=IMPORTED` and its full source lineage
   forever; it can never be mistaken for an independent discovery." The
   `lineage_edges` table (`store.py`) is declared "the ONLY source of lineage —
   never reconstructed after the fact." Any dedup that discards an artifact
   discards edges that cannot be rebuilt from the survivor.
7. **A countervailing prior exists and must be weighed, not ignored** (from
   session context, not re-read here): ERGON GEN-1/1B found MUT_REDUNDANT
   retention beat the inherited MRU policy by +2.78pp (p=0.0008, Holm 0.0040)
   but did NOT beat arbitrary memory after correction, and "identity-level
   library composition carries no policy signature at all." This cuts two
   ways: redundant entries can carry latent, non-obvious value (argues against
   cheap dedup), yet identity-level composition choices were found to carry no
   detectable policy signature in that setting (argues the compositional axis
   below may come back null more often than the hypothesis predicts). Both
   readings are pre-registered as live possibilities, not resolved here.

## Prospective predictions

Stated before any run, one-sided where the hypothesis has a direction:
- P1: extended-probe divergence rate for battery-matched pairs will exceed the
  literal-duplicate control's divergence rate (which should be ~0) for >20% of
  pairs.
- P2: metered token/VM-step cost will differ by >10% relative for >30% of
  battery-matched pairs (cost is the axis least likely to be screened by any
  output-based battery, so predicted to show the highest divergence rate).
- P3: compositional/residue-ablation fitness delta between organisms built
  from A vs. from B will be individually small per pair, but non-zero for a
  detectable minority (>=15%) of pairs, mirroring D8's z2 pattern (reuse
  without consequence is common; consequence without reuse is the rarer,
  decision-relevant case).
- P4: mutational-neighborhood offspring-fitness distributions will show the
  weakest divergence of the four axes (most artifacts on this substrate are
  reached by broadly similar local search dynamics), consistent with the
  ERGON "no policy signature" caution in (7) above.
- P5: the provenance/lineage check will show >0 irrecoverable edges for close
  to 100% of import-sourced pairs, by construction of the schema (this is
  expected to be a near-certainty, not a live empirical question — included
  as a hard gate, not a statistical test).

## Experiment

Substrate: reuse the existing SVM-8-style deterministic substrate and GA/mutation
machinery already frozen in `D8/agent_d8` (26-opcode stack VM, sha256-keyed
named RNGs, full replayability) rather than building a new one — this keeps the
instrument itself already-validated (D8 §9 instrument-validation suite, 8/8
pass) instead of re-deriving sensitivity from scratch.

1. **Pair construction.** Run the standard battery B (the same eval battery
   convention as D8: F1–F3 dev+eval families, N tasks) over a large candidate
   pool generated by the existing GA/random search arms. Identify all pairs
   (A_i, B_i) of DISTINCT artifacts (different byte sequences / `blob_hash`)
   whose outputs agree on every task in B. Stratify the discovered pairs by
   artifact length, opcode-class histogram distance, and originating search
   arm (per the sampling-strategy doctrine — do not take the first N found).
   Target n=50 pairs, minimum n=30 to proceed to freeze.
2. **Axis (a) — extended/held-out probe.** For each pair, execute both members
   on M=2000 additional inputs drawn from (i) uniform random inputs and (ii)
   the D8 F4/F5/F6-style held-out/structureless/misleading families. Record
   per-pair disagreement rate.
3. **Axis (b) — metered cost.** Record tokens-executed and VM steps for both
   members over the SAME input set (battery ∪ probe). Compute relative cost
   delta.
4. **Axis (c) — compositional/residue-ablation heredity.** Following D8's
   donor-retrieval/splice mechanics, insert each of A_i, B_i as a fixed
   sub-segment into K=20 pre-generated composite host organisms (varied
   insertion positions and surrounding contexts), then run the standard
   residue-ablation heredity test (remove the segment, measure output-set
   change) on each composite. Compare the ablation-consequence distribution
   between the A-hosted and B-hosted composite populations per pair
   (paired, since host organisms are shared).
5. **Axis (d) — mutational neighborhood.** Apply the frozen M0c-style mutation
   operators (point/indel, R=200 draws) independently to A_i and B_i for
   R generations under identical seeds-per-offset, and compare the resulting
   offspring fitness distributions (KS test) and offspring solve-rate on a
   held-out task set.
6. **Axis (e) — provenance/lineage.** For each pair where one member is
   `origin=IMPORTED`, check whether its `lineage_edges` rows reference any
   `source_artifact`/`source_world` not reachable from the other member's own
   edge set. This is a binary structural check against the actual schema, not
   a statistical test.
7. **Composite verdict.** A pair is DEDUP-SAFE only if it clears the
   pre-registered thresholds on axes (a)-(d) simultaneously AND clears the
   hard veto on axis (e). Report the fraction of tested pairs that are
   dedup-safe, per axis and jointly, with CIs.

## Controls

- **Positive control (literal duplicate).** For each pair, also include a
  bit-for-bit copy of A_i as a second "pair" against A_i itself. Expected: zero
  divergence on all axes. Calibrates the floor / instrument noise level.
- **Planted negative control (mechanism-matched near-miss).** Construct pairs
  that match on battery B by explicit construction (padded dead code changing
  token cost; or an F2/F6-style behavioral collision as D8 §16 already
  documented occurring naturally) but are KNOWN to differ on at least one axis
  by design. MUST trip divergence on the axis it was planted to violate; if it
  does not, the instrument is declared insensitive and the run is aborted
  before any dedup-safe claim is issued (fail-closed, per Daedalus CHARTER
  standing order 4/discipline: "Fix fail-closed").
- **Random-pairing null.** For each artifact A_i, also test it against a
  RANDOMLY drawn artifact from the same pool that does NOT match on the
  battery, to establish the baseline divergence rate between genuinely
  unrelated artifacts on axes (a)-(d). This bounds how much of any observed
  battery-matched-pair divergence is "still mostly similar because most
  artifacts on this substrate are similar" versus specifically diagnostic.
- **H-BAG/H-SHUFFLE-style structural ablation on axis (c).** Repeat the
  compositional test with the host organisms' own wiring destroyed (segment
  positions shuffled, per D8 §8 H-SHUFFLE), to check whether any measured
  compositional divergence is an artifact of a specific host structure rather
  than a general property of the A/B pair.

## Confound defenses

- **Battery-narrowness confound.** The standard battery may be too small to
  expose real divergence (D8's F4 held-out family was vacuous, 0.00 in every
  arm — a documented failure mode of narrow batteries in this exact lineage).
  Mitigated by axis (a)'s M=2000 extended/held-out probe, stratified across
  input regions, not sampled from the front of any list (per the
  prefix-sampling lesson).
- **Cost blindness.** A pair can be output-identical and cost-divergent; the
  battery alone would never surface this. Axis (b) is metered independently
  and is not gated on axes (a)/(c)/(d) passing.
- **Post-hoc rationalization / memorization confound.** Per D8 §16, any
  discovered pair where one member is a trivial recombination of the other's
  dev-phase provenance must be flagged and excluded from the "genuinely
  independent artifacts" stratum before computing the headline safe-dedup
  rate, exactly as D8 excluded byte-identical eval/dev collisions from reuse
  evidence.
- **Multiple comparisons.** n_pairs x 4 axes x (primary + control) tests are
  Holm-corrected jointly, following the ERGON GEN-1B precedent (Holm 0.0040
  on its own primary result) rather than reporting raw per-axis p-values.
- **Single-context compositional underpower.** D7's irreducible-compositionality
  finding (only 8/1024 artifact-pairs crossed a barrier, and only in specific
  roles) shows a single splice context can trivially fail to expose a real
  compositional difference. Axis (c) therefore uses K=20 varied host contexts
  per pair, not one.
- **Provenance is a hard veto, not a statistical finding.** Even a pair that
  is statistically indistinguishable on axes (a)-(d) is not thereby licensed
  for a delete-one dedup if axis (e) finds unreconstructible lineage edges —
  this is declared out of the statistical frame entirely, per the CHARTER's
  "provenance is permanent" clause, and reported as a separate binary gate.

## Preregistered falsifiers (numeric thresholds)

- F1 (axis a): SUPPORTS narrow behavioral equivalence only if mean extended-probe
  divergence for battery-matched pairs is within 0.02 absolute of the
  literal-duplicate control (TOST equivalence margin 0.02) AND differs from the
  random-pairing null by Cohen's h >= 0.3 (Holm-corrected p<0.05). Otherwise
  REJECTS "battery match implies off-battery match" for that pair-set.
- F2 (axis b): dedup declared cost-unsafe if >30% of pairs show relative
  token/VM-step cost divergence > 10%.
- F3 (axis c): dedup declared composition-unsafe if >15% of pairs show a
  residue-ablation heredity delta >= 0.03 absolute solve-rate difference
  between A-hosted and B-hosted composites (0.03 chosen to match the D10
  Phase-2 `DELTA_MIN` convention for a materially meaningful effect on this
  scale of task battery).
- F4 (axis d): dedup declared evolvability-unsafe if offspring fitness
  distributions differ (KS test, Holm-corrected p<0.05) for >20% of pairs.
- F5 (axis e, hard veto): ANY pair with n_unreconstructible_edges > 0 is
  declared NOT dedup-eligible regardless of F1-F4, no threshold to tune.
- F6 (instrument validity): if the planted negative control fails to trip its
  designed axis, the entire run is INVALID — no safe/unsafe verdict is issued,
  matching D8's fail-closed instrument-validation discipline.
- Overall verdict "Foundry CAN safely dedup a defined pair-class" requires
  F1-F4 to clear AND F5 = 0 violations AND F6 = instrument valid, for a
  pre-named subset of pairs (e.g., "same originating search arm, cost delta
  <5%, no import-sourced member"); a global "always safe to dedup on battery
  match alone" claim is not attainable by this design and is explicitly
  disclaimed regardless of outcome.

## Stopping rule

Freeze order, mirroring D8/D10 discipline: (1) instrument validation
(positive + planted-negative controls) run and checked BEFORE any pair-level
axis data is inspected; (2) pair discovery and stratification frozen; (3) all
axes (a)-(e) computed once for all pairs; (4) stats computed once from frozen
ledgers. No re-running of a failed axis with adjusted parameters. Minimum
n=30 pairs to reach a verdict; target n=50; if fewer than 30 battery-matched
pairs are discoverable within a 2,000,000-candidate-evaluation search budget,
the experiment reports "pair-scarcity — verdict not reached" rather than
lowering n post hoc.

## Expected failure modes

- Underpowered at n=30-50 (D8's own primary gate at n=60 came back with a CI
  spanning both directions on a comparably-sized effect) — plan to report wide
  CIs honestly rather than reading a marginal point estimate as a verdict.
- Extended-probe axis vacuous like D8's F4/F5 (0.00 everywhere) if the
  substrate's held-out families are too easy or too hard — disclose rather
  than paper over.
- Pair scarcity: battery-matched-but-distinct pairs may be rare enough that
  the discovery budget dominates cost and n never reaches 30.
- The "no policy signature" ERGON precedent may generalize: axis (c) may come
  back null for most pairs, which would be a genuine result (narrow-battery
  equivalence generalizes further than expected for THIS substrate) rather
  than an instrument failure — F6's planted negative control is the only
  thing that can distinguish these two explanations.
- Any pair discovered to be a memorization/near-duplicate of the SAME dev
  provenance (D8 §16 pattern) inflates the apparent "safe" fraction if not
  excluded before headline computation.

## Compute estimate

n_pairs=50: extended probe 2000 evals/pair, compositional test ~20 contexts x
~400 evals/context/pair, mutation test ~200 offspring x ~50 evals/pair =>
roughly 50 x (2000 + 8000 + 10000) ≈ 1.0M candidate evaluations, the same
order of magnitude as D8's per-arm eval-phase budget (0.67-0.76M cand evals/arm,
§15). Deterministic, stdlib-only, single machine, CPU-only; D8's comparable
scale (382,613 dev-phase evaluations) ran without needing special infrastructure.
No GPU, no network calls, no new substrate code — reuses frozen `D8/agent_d8`
machinery plus the Foundry's existing `import_artifact`/`lineage_edges` schema
for axis (e).

## Prior evidence that materially changed this design (or 'none found')

Materially changed the design (see Motivating evidence, all found this
session): (1) D8's hoard-level "dedup by probe behavior" plus its
byte-identical-solution exclusion from reuse evidence — reframed this proposal
away from "does dedup work" toward "under what pre-registered stronger
equivalence is dedup licensed," and supplied the composite-verdict structure.
(2) D7's transfer-dimension finding that byte-identical artifacts across
frames can carry decisively different causal roles — motivated axis (c)/(d)
as first-class, not optional. (3) D10's `GATE_SPEC.md` "content-deduped"
convention plus `store.py`'s content-addressed `artifact_id` and the
idempotency-key "never silent dedup" design note — established that no
precedent in this lineage has ever deduplicated on behavioral grounds, which
is why this experiment is needed rather than assumed answered. (4) Daedalus
`CHARTER.md`'s "provenance is permanent" standing order — converted axis (e)
from a statistical test into a hard, non-negotiable veto. (5) The ERGON
GEN-1/1B MUT_REDUNDANT result (session context, not re-read this session) —
supplied the countervailing prior that redundant/duplicate-looking entries can
carry latent value, and that identity-level composition choices have
previously shown no detectable policy signature, tempering how strongly axis
(c)/(d) results should be read either direction.

## Unresolved uncertainty

- Whether "output" as scoped by the task (byte-identical on the standard
  battery) is meant to include intermediate/side-channel state (stack
  residue, register contents at halt) or only the declared return value; this
  experiment tests the declared-value reading and flags the broader reading
  as a distinct, larger experiment.
- Whether a merged-provenance artifact representation (a schema change
  recording BOTH source lineages on one surviving row) could satisfy both
  "reduce storage/composition search space" and "provenance is permanent"
  simultaneously — not designed here; if F1-F4 come back favorable, this
  schema question becomes the next design problem, not something this
  experiment can adjudicate.
- How representative the discovered battery-matched pairs are of the
  artifact population the Foundry will actually accumulate at scale (this
  substrate's pairs may be enriched for short/degenerate programs, understating
  real-world divergence risk).
- Whether the ERGON "no policy signature" finding and this experiment's axis
  (c)/(d) are measuring the same underlying phenomenon on different substrates,
  or are genuinely independent — left open pending the ERGON gen-1a materials
  this session did not read (out of budget/scope; see operation log).

