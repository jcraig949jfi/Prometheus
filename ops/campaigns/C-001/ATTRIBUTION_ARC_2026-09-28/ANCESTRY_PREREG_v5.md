# Byte-level ancestry replays -- preregistration v5 = v4 + the replacements below (Archaeon, 2026-09-28)

- **Basis:** adversarial Review 6 (review6/REVIEW_6.md; REVIEW_6_ADJUDICATION.md). It replayed v4's drawn run r025144 exactly
  (92/92 rows) and showed that v4 returns BROKEN on it for reasons unrelated to ancestry. In short: a non-replicating sample; Q8c
  counting the performer and birth suppression; vacuous arms; whole-execution ctrl scope de-identifying ordinary task-performing
  replicators.
- **What stands:** everything in ANCESTRY_PREREG_v4.md (with Amendments A and B1) stands EXCEPT the sections replaced here. Where
  v4 and v5 differ, v5 governs.
- **Freezing:** v5 is frozen at the commit that adds it together with BEE_POPULATION_v5.json.

## R1 (replaces v4 s2.1): identification is INTERVENTIONAL; the label sets are reported, not gating
A written locus is IDENTIFIED iff:
1. **Provenance:** its data label is (ENTITY X, j) MOVE.
2. **Flip:** the path-preserving flip test (s4.1 with B1 and R4) does not FAIL it.
3. **Dependence:** in the single-interaction intervention arms (K = 8 draws each), randomising any source group OUTSIDE {X, the
   performer entity} changes that locus's value in 0 of K draws.
   - The source groups are: every other ENTITY's bytes, the INPUT bytes that were supplied, and (NPE) the persisted registers.
   - A draw in which the write or the birth is suppressed counts toward Q8c-whether, not here.

ctrl_deps (both scopes), addr_deps and exec_deps are still exported and reported. They are a declared over-approximation; they do
not gate identification. Consequence: a task-then-copy replicator whose copy does not depend on the input is identified (Review 6
s1.1).

**NO_MATERIAL class:** births with <= 10% ENTITY-labelled written loci are reported as their own class and excluded from the
identifiability denominator.

**Class key:** the majority performer entity over written loci (self = the executing organism / other entity / none). A class with
0 rule-identified loci is "not gated".

## R2 (replaces v4 Q8c): value dependence outside {donor, performer}
- Q8c per written ENTITY-MOVE locus = Pr over K = 8 draws (randomising the source groups outside {data-label entity, performer})
  that the locus VALUE changes, among draws in which the write occurs.
- Q8c-whether (write/birth suppression) is reported separately and never enters Q8c.
- CONSTANT/COMPUTED loci get their own estimand, Q8c-nonmove: randomising each ENTITY in turn, with the same rules. It is
  reported and does not gate.
- Estimand: the mean over loci, with a birth-clustered bootstrap CI (run-clustered for NPE).

## R3 (replaces v4 s2.4 verdict rules), precedence INSTRUMENT_FAILED > SPEC_DEFECT > BROKEN > INCONCLUSIVE > ALTERED > VALIDATED
- **INSTRUMENT_FAILED, SPEC_DEFECT:** as in v4.
- **BROKEN:** ONLY a named channel absent from s1, reproduced by a fixture, that the policy cannot represent.
- **INCONCLUSIVE:** fewer than 80% of non-NO_MATERIAL births are identifiable (>= 90% of written loci identified) for a by-design
  Q, OR the transmission class (R5) has fewer than 30 births.
- **ALTERED:**
  * DOMINANT if the Q8c lower 95% bound > 50%;
  * WEIGHTED if the lower bound >= 5%;
  * or a prediction with an ALTERED consequence decides so.
  All three name the v0 field required.
- **VALIDATED:** the Q8c upper bound < 5%, AND every by-design Q is expressible in v0 plus the agreed extensions, AND the
  round-trip check passes.

## R4 (amends v4 s4.1): opcode-equivalent flips
- A flip that changes an opcode byte keeps the path "preserved" if the two opcodes are semantically equivalent.
  * In BEE: both undefined (NOP), or both the same defined opcode (this happens only for operand-free bytes).
- The store-address sequence includes OUT stores.
- IN pad bytes (beyond the supplied inputs) are (CONST, "in_pad").

## R5 (replaces v4 s4.2 arms and adds the transmission class)
- **TRANSMISSION class:** births whose written loci are majority IDENTIFIED (ENTITY writer) MOVE. Predictions P1, P2 and P5 are
  evaluated ONLY on this class.
- **Per-byte completeness:** for a random 20% of sampled births, randomise each single byte NOT named in any of the locus's sets,
  one at a time, K = 4. Share of such bytes that change the locus value with the path and the birth preserved: <= 5% per class.
- **Per-byte precision:** for the same births, randomise each single NAMED base-label byte, K = 4. Share that ever change the
  locus value, the write or the birth: >= 20% per class, else OVER-TAINT -> INSTRUMENT_FAILED (unless a fixture shows it is
  required).
- The whole-entity arms of v4 s4.2 are dropped: Review 6 measured them as vacuous (0.992 for an over-taint mutant).

## R6 (replaces v4 s5 BEE): the run is drawn from the relevance-screened population
- **Population (committed WITH this file):** BEE_POPULATION_v5.json, built by archaeon/attribution/bee_run_population_v5.py.
  * 53 of the 73 v4-cell runs have >= 30 births with row field 8 >= 32 and row field 9 >= 32.
  * This screen is a relevance condition only and never enters a measurement.
- **Draw (a later commit):** seed = this commit's full SHA; index = sha256(seed) mod 53.
- **Pre-committed fallback:** if the drawn run's TRANSMISSION class (R5, computed by the owner's replay) has fewer than 30 births,
  take index + 1 mod 53, and so on, recording every step.
- r025144 is withdrawn (non-replicating; Review 6). There is no second draw.
- NPE is unchanged: all pair interactions in the 11 T-003 runs.

## R7 (amends v4 s6): predictions
- Each prediction names its decision locus set (IDENTIFIED loci of TRANSMISSION-class births), its interval (birth-clustered
  bootstrap 95%), and its treatment of NONE/TIED (excluded from the denominator and counted separately).
- P1 (Q-homology), P2 (Q2) and P5 (Q8c) are evaluated on the TRANSMISSION class only.
- P2 "holds" iff the lower bound >= 10%; it is "certified" iff the upper bound < 10%; otherwise INCONCLUSIVE.

## R8 (amends v4 s3, s1.3)
- Pins are "sha256 prefixes", not git blob ids.
- The per-tick RNG-state hash is a self-consistency record (the preserved runs stored rows only).
- Per birth, export mechanism flags: LDIR entered with C == 0 (wrap), in-window source, budget-ended.
- exec_deps scope is stated: every fetched byte from interaction start UP TO the store (reported), and over the whole
  interaction (also reported).
