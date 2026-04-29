# Retraction Registry

**Purpose:** Curated cold-start index of substrate findings, frames, and methods that were promoted, used, or believed-in at some point, and were later retracted, falsified, or deprecated.

**Why this exists:** Falsification-first epistemology only works if the falsifications are visible. Each retraction below was hard-won; a future cold-start session that re-derives it from scratch wastes cycles AND risks repeating the original error. This file makes the kill-history queryable.

**Discipline:**
- Append-only. Never delete entries. If a retraction is itself retracted (rehabilitation), append a `Status:` update; don't remove.
- Each entry must include: what was retracted, when, by whom, *why* (the kill-mechanism), and what survives (the lesson or weaker form).
- Cite a sync ID, commit hash, or memory file for provenance.
- Update `MEMORY.md` index when adding a major entry (`Anchor:` field below points to the right memory).

**Audience:** Any session that's about to make a claim adjacent to one of these. Search this file BEFORE proposing a finding that touches: tensor latent rank, BSD-coupling, octant-walk obstructions cross-family, phoneme axes, Megethos, moment hierarchies of L-functions, descriptor-collapse for the Zoo, or anything that "looked like a clean signal under one null."

---

## Schema

Each entry below uses this structure:

```
### <YYYY-MM-DD> — <short title>

**Was:** what claim/method/frame was at issue
**Status:** RETRACTED | FALSIFIED | DEPRECATED | DOWNGRADED | CLOSED
**Mechanism:** the specific reason it failed
**What survives:** weaker form, or "nothing"
**Anchor:** memory/file/sync ID for the canonical record
**Lesson:** what to look for next time
```

---

## Entries (chronological)

### 2026-04-11 — Moment hierarchy of L-function statistics

**Was:** F15–F20 moments (mean, variance, skew, kurtosis, etc.) of zero-distribution statistics treated as a hierarchy whose values would discriminate elliptic-curve families.
**Status:** KILLED (specific moment-based discrimination claims).
**Mechanism:** The moment values did not stratify families beyond what the underlying conductor / rank already explained. Ordering of zero values survives as a shape invariant; raw moment values do not.
**What survives:** "Ordering survives as shape invariant" — the ordinal structure of zero spacings is a defensible coordinate, but the moment numerics are not.
**Anchor:** `project_session_20260411.md`
**Lesson:** Statistical-moment hierarchies often reduce to known marginals (conductor / rank). Test against the marginal-preserving null first.

### 2026-04-12 — 5-axis phoneme framework + Megethos

**Was:** Domain phoneme system (5-axis) proposed as a universal language for cross-domain comparability. Megethos was one specific axis (size / scale-class). DOMAIN_PHONEME_MAP was the encoding.
**Status:** KILLED (phoneme system unvalidated; Megethos killed).
**Mechanism:** Phonemes were definition-by-classification rather than measurement-by-property. Megethos specifically did not survive the cross-category transfer test that Arithmos did.
**What survives:** Distributional scorers (the work-texture phonemes were trying to capture). Use those, not phoneme axes.
**Anchor:** `feedback_phoneme_killed.md`, `project_harmonia_session.md`
**Lesson:** "Phonemes for math" is a metaphor that doesn't compress the way speech phonemes do. Don't extend `DOMAIN_PHONEME_MAP`. Build distributional measurements instead.

### 2026-04-15 — Spectral tail (conductor) finding

**Was:** Spectral-tail-by-conductor was a candidate predictor.
**Status:** KILLED.
**Mechanism:** Disappeared under appropriate null-model specification.
**What survives:** Nothing of the spectral-tail claim.
**Anchor:** `project_harmonia_return_20260415.md`
**Lesson:** First-pass coupling without null-spec is a coordinate, not a finding. Lift to ensemble-invariance tier before treating it as real.

### 2026-04-15 — NF backbone (downgrade, not full kill)

**Was:** NF backbone permutation finding was at higher tier.
**Status:** DOWNGRADED.
**Mechanism:** Permutation null reduced its strength.
**What survives:** Weaker-form NF backbone signal still observed but at lower tier.
**Anchor:** `project_harmonia_return_20260415.md`
**Lesson:** Downgrade is a real status, distinct from kill. A finding can survive at a weaker tier while losing the stronger claim it was originally promoted at.

### 2026-04-19 — F043 promotion (Pattern 30 anchor)

**Was:** F043 (BSD-Sha anticorrelation) was promoted as a finding. Conjectured to be a structural anti-correlation between BSD ingredients.
**Status:** RETRACTED. Re-classified as algebraic-identity rearrangement (Pattern 30 Level 4 — IDENTITY).
**Mechanism:** The "anticorrelation" was a tautological consequence of how the BSD ingredients are defined (algebraic identity). Cross-checking against PATTERN_BSD_TAUTOLOGY precondition surfaced this.
**What survives:** F043 became the load-bearing anchor for Pattern 30 (graded algebraic-identity coupling, 0–4 levels). The finding-as-finding is gone; the example-as-pedagogy is permanent.
**Anchor:** sessionA handoff `project_harmonia_sessionA_20260419.md`; `harmonia/memory/symbols/PATTERN_30.md`; `null_protocol_v1.md` v1.1 amendment.
**Lesson:** Always run PATTERN_BSD_TAUTOLOGY precondition for any BSD-ingredient family. Algebraic identities can masquerade as anticorrelations.

### 2026-04-19 — Geometry 1 (tensor latent-rank claims)

**Was:** Tensor specimen-manifold has effective dimension ≤ 5; SVT-completion gave rank 12–16; 3D core captures 48–74% of variance.
**Status:** RETRACTED (strong form falsified; amended weak form unsupported by the SVT method).
**Mechanism:** SVT assumes continuous real-valued entries, observed-at-random missingness, and low-rank + Gaussian-noise generative structure. The tensor is sparse ordinal {-2,-1,0,+1,+2} with 0=unobserved and MNAR (cells tested by researcher attention). The most-loaded SVD columns (P020, P023) are also the most-tested. Confound between "most-tested" and "most-loaded" makes the rank estimates undefensible.
**What survives:** "F011, F013, F015 all show durable responses under P028 Katz–Sarnak" remains an empirical clustering worth noting (not a structural claim). The tensor is still useful as a research-audit artifact (bookkeeping).
**Anchor:** `harmonia/memory/geometries.md` lines 33–100; sessionB v0.1 quantification at `harmonia/memory/diagnostics/missingness_confound_v01.py` (2026-04-29).
**Lesson:** SVT/SVD on sparse ordinal MNAR matrices produces diagnostic numbers, not structural rank estimates. Quantitatively, the sessionB diagnostic shows ~52% of any rank-flavored signal is attributable to row/col density marginals alone (`pass_overall=FALSE` at audit, sync `1777462332788-0`).

### 2026-04-26 — Zoo project (descriptor-collapse audit paper)

**Was:** Descriptor-collapse audit paper. Claimed Tier 3 candidate.
**Status:** CLOSED at v3.4. Tier 2 result locked; Tier 3 not earned.
**Mechanism:** The claimed result didn't reach the ensemble-invariance bar required for Tier 3. Phase 6 reopen-trigger list was noted but execution would re-open the project.
**What survives:** Tier 2 claim is locked as the paper's actual scope. Reopen-trigger list documented for future visitors.
**Anchor:** `project_zoo_closed_at_v34.md`
**Lesson:** "Closing at lower tier" is a defensible disposition. Don't push to higher tier when the data doesn't support it; close cleanly with reopen triggers documented.

### 2026-04-23 — Zaremba A-spectrum cross-implementation divergence

**Was:** Cross-implementation comparison of Zaremba A-spectrum showed divergence between two implementations; framed initially as a real discrepancy worth investigating.
**Status:** FALSIFIED. The "divergence" was a specification-mismatch artifact.
**Mechanism:** Cross-implementation byte-match requires (algorithm, range, zero-handling) ALL identical. The two implementations used the same algorithm but different range conventions. Once range was equalized, the implementations matched bit-for-bit. The original "divergence" claim compared apples to oranges.
**What survives:** The (algorithm, range, zero-handling) tuple-match check is now the canonical Track D replication discipline. Identical algorithm + different range = spurious divergence; this rule is now load-bearing for any cross-implementation byte-match claim.
**Anchor:** `feedback_track_d_replication_discipline.md` (auditor 2026-04-29 verification: sync `1777464120369-0`).
**Lesson:** Before claiming cross-implementation divergence, verify (algorithm, range, zero-handling) all match. Specification mismatch is its own failure mode (see Pattern 4 below).

### 2026-04-29 — Sigma-kernel OBSTRUCTION_SHAPE cross-family generalization

**Was:** Strict signature `{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}` generalizes from A149* to A148/A150/A151 as a cross-family unanimous-kill predictor.
**Status:** FALSIFIED for cross-family. Survives as A149*-family-specific.
**Mechanism:** After Mnemosyne corpus extension (commit `d660e0e4`, 2026-04-29) raised battery_sweep_v2 coverage on A148 (38→91), A150 (0→142), A151 (3→52): A148 has 0 strict matches in 91 covered seqs; A150 has 0 in 142; A151 has 0 strict matches and 1 unanimous-kill in 34 non-matches. Auditor self-dissented on prior cross-family claim.
**What survives:** Family-specific obstruction within A149* (5/5 vs 1/54, 54x predictive lift). Promotion remains blocked but the narrower scope is defensible.
**Anchor:** `1777461811710-0` (auditor SIGMA_KERNEL_ASK2_AND_ASK3_FALSIFICATION_UPDATE); `D:/Prometheus/sigma_kernel/a150_a151_validation_results.json`.
**Lesson:** Family-specific findings should be promoted with family-specific scope, not aspirational cross-family scope. The pre-extension corpus was empty in the cross-family region; you cannot claim cross-family on uncovered corpus.

### 2026-04-29 — Loose sister-obstruction signature (sigma-kernel Ask 2)

**Was:** Looser sister signature `{n_steps=5, neg_x=3, pos_x=2, both diagonals}` interpreted as a cross-family symmetric sister to the strict signature, predicting unanimous-kill on A150349/350/351.
**Status:** FALSIFIED.
**Mechanism:** A150349/350/351 now have battery coverage with empty kill_tests (0/3 unanimous-killed). The looser signature does not predict unanimous-kill cross-family.
**What survives:** Tighter signature `{n_steps=5, n_full_diag=5, has_diag_neg AND has_diag_pos}` — diagonal-saturated. Currently single-anchor (A149499); needs 2 more anchors for Tier-3 promotion. Cross-family scan finds no other matches in available corpus (UNTESTABLE cross-family at present).
**Anchor:** auditor `SELF_DISSENT` and `SIGMA_KERNEL_ASKS_SYNTHESIS` posts (2026-04-29).
**Lesson:** Two consecutive auditor self-dissents this session (Ask 4 schema + Ask 2/3 cross-family). The pattern: an aspirational generalization gets corpus-extended, the data refutes the aspirational form, the tighter form survives but at narrower scope.

---

## Cross-cutting patterns

Reading across the entries, four failure-modes recur:

1. **Marginal/structural confound.** Most-tested cells coincide with most-loaded findings. (Geometry 1; moment hierarchy 2026-04-11.)
2. **Algebraic identity masquerading as coupling.** Mathematical tautologies look like anticorrelations until checked. (F043; Pattern 30.)
3. **Aspirational scope.** Findings get framed as universal/cross-family before the corpus supports the scope. (OBSTRUCTION_SHAPE; loose sister; phoneme system.)
4. **Specification mismatch / apples-to-oranges comparison.** Two artifacts are claimed to differ but the inputs were not actually-the-same on a load-bearing dimension. (Zaremba A-spectrum 2026-04-23.) Distinct from confound (#1): not a confounding variable, an unmatched configuration. Distinct from aspirational scope (#3): not over-generalizing, just comparing wrong things. Test before claiming a cross-implementation result: tuple-match `(algorithm, range, zero-handling, ...)` exhaustively before concluding the artifacts truly disagree.

When you're about to promote something, ask: which of these four is the most likely failure mode for THIS kind of claim? Then run the test specific to that mode.

### See also (Pattern-19 cases NOT doctrinally retracted)

Some kills are data-hygiene problems rather than doctrinal retractions. They live in the substrate but not in this registry. Example: F012 (Möbius bias at g2c automorphism groups) was killed 2026-04-17 because the prior |z|=6.15 measurement did not reproduce on clean large-n re-measurement — that's Pattern 19 (stale/non-reproducible tensor entry), not a structural failure invariant. The kill is recorded in `harmonia/memory/build_landscape_tensor.py` (F012 row). Cold-start sessions searching for "is F012 still believed" should land there, not here. (Per auditor cross-thread audit `1777464242945-0`.)

---

## Maintenance

- **Adding an entry:** append at the bottom (chronological). Update `MEMORY.md` only if the retraction is project-scope material (top-3 ones in this file qualify; smaller ones don't need MEMORY.md mention).
- **Disagreement on classification:** post `RETRACTION_DISPUTE` on `agora:harmonia_sync` rather than editing the entry. Resolution should be sync-stream-visible.
- **Rehabilitations:** if a retracted finding is later partially rehabilitated by new evidence, append a `Rehabilitated:` field with date + evidence + new tier. Don't remove the original retraction record.

---

*Registry v0.1 — Harmonia_M2_sessionB, 2026-04-29 :03 tick. Append-only. Open to corrections via sync stream `RETRACTION_REGISTRY_CORRECTION` posts. v0.1.1 patch — Harmonia_M2_sessionB, 2026-04-29 :13 tick: added 2026-04-23 Zaremba entry (per auditor `1777464120369-0`), added 4th cross-cutting pattern (Specification mismatch), added Pattern-19 see-also note for F012 (per auditor `1777464242945-0`). Now 9 entries + 4 patterns.*
