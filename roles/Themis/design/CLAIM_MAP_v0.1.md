# Moonshot -> RSO claim map (R-CLAIMMAP) -- v0.1 DRAFT for Palamedes

Owner: Themis (Moonshot). Counterparty: Palamedes (RSO). Date: 2026-10-10. Authority: design v0.3 R-CLAIMMAP / s9
(F03: "A versioned native-claim->predicate map is agreed with Palamedes before adapter work"); OP-NF2 2026-10-10
("Continue ... independent RSO claim-mapping work with the respective owners"). Status: DRAFT, nothing agreed.
No RSO contract, predicate or schema changes here: where RSO lacks something, the row says so and names the
versioned route (a successor campaign or a contract amendment -- the operator's gate, CONTRACT.md:130-132).

Ground rules (from both sides, verbatim where it matters):
- A W-S1 / slice-001 pass supports only the W-S1 claim (design v0.3 :251-253); slice-001 excludes "origin,
  mechanism, economy, recursion, any class of organisms, any other world, any stochastic setting, or any native
  physics" (rso/slice001/contract/drafts/A_world_reset_observer.md:37-38). Moonshot will not impose an artificial
  reset and call it native physics.
- RSO's producer/consumer split: "A producer cannot qualify its own instrument"; "No `authority` key exists in a
  producer receipt" (B_evidence_receipt_authority.md:44-46, :144). Moonshot is a PRODUCER; RSO assembles verdicts.
- The nearest precedent for native predicates is C-010 (rso/witness/PREREGISTRATION.md, world W15): P-CAL, P-OBS,
  P-ERASE, P-PRES, P-RET, P-CHAN, P-FLAT and the custody gate.

## The chain each row must complete

Moonshot proposition -> native state/boundary -> interventions -> trace fields -> existing or new RSO predicate ->
calibration -> verdict/authority.

## Rows (proposed)

### R1. H2 -- retained-information dependence of survival (the native science claim)

- Proposition (v0.3 :145-147): survival-only evolution produces an organism whose SURVIVAL depends on retained
  hidden information, surviving the reactive-null family and the R6 interventions.
- Native state/boundary: the organism (Proteus VM state) inside a wforge world; carriers to classify (v0.3 :217-219):
  location, charge, pending writes, other organisms, world marks, adapter caches, observation buffers. PROPOSAL:
  adopt slice-001's COMPOSITE boundary form (organism + named channels, each ALLOWED / FORBIDDEN / SCHEDULE /
  BOOKKEEPING; A:85-104) with exactly one ALLOWED carrier per claim, declared before any run. OPEN Q2.
- Interventions (R6, v0.3 :211-214): channel-cut and information-destroying state resample MUST drop; an
  information-preserving sham MUST NOT drop. PROPOSED mapping: channel-cut ~ P-CHAN's disable arm (paired, exact
  McNemar); destroying resample ~ a new gate in P-CHAN's form (paired, same seeds); the sham has NO RSO predicate
  (shams appear only in the hardened design HD:57, :77-79) -> new predicate. Each with a fire member, as P-ERASE has
  X-LEAK (a known-leaky subject that must be detected).
- Trace fields: none defined yet (R9: "a complete structured log sufficient to compute R6 from logs alone", v0.3
  :264). PROPOSAL: per tick per organism: tick, observation, action, charge, alive, the declared carrier's value,
  intervention marker; per episode: seeds, world genome + implementation hash (the native epoch runtime already
  names wforge's implementation hash; C-012-T007), outcome. Layout to follow C-010's roles (WP:89-95). OPEN Q5.
- Predicate: P-RET answers a bit above a no-carry bound; Moonshot's outcome is SURVIVAL (time-to-absorption /
  survival at horizon). NEW predicate needed ("P-SURV-DEP": survival advantage of the subject over its matched
  memory-disabled arm, paired seeds, exact test) -- a legitimate Phase-3 output (design v0.3 s9 :327-328). OPEN Q3.
- Calibration: P-CAL's pattern -- NULL and shuffled controls at or under the no-carry bound AND a planted POSITIVE
  (a hand-built organism known to carry the cue) reads POSITIVE, else every outcome UNQUALIFIED. For survival, the
  no-carry bound is the reactive-null family's best (exact where tractable, else best-found, LABELLED). OPEN Q2.
- Verdict/authority: RSO's vocabulary (RAN | BLOCKED; PASS | FAIL; POSITIVE | NEGATIVE | NOT_SHOWN; standing
  BLOCKED > UNQUALIFIED > UNMET > SATISFIED). H2 needs a statistical slot (INDETERMINATE) which slice-001 lacks;
  C-010 has one. OPEN Q6.

### R2. H1 -- RSO types an unfamiliar external producer correctly (Moonshot as the producer under test)

- Proposition (v0.3 :127-130): Phase 3 types Moonshot's evidence and its limits without relaxing its ruler.
- Moonshot's planned producer cases vs RSO's evidence cases today (B9): honest -> honest result; underpowered ->
  (no RSO type; INDETERMINATE missing); tamper-visible ~ BYTEFLIP (G-BIND FAIL, UNMET, B:501); consistent
  fabrication ~ FAB_CONSISTENT (ELIGIBLE with "execution not authenticated" as DISPLAY text only, B:479-482);
  violation -> (route unclear). EXECUTION_NOT_AUTHENTICATED is not an RSO type (render.py:177).
- PROPOSAL: score H1 against RSO's CURRENT behaviour first (no schema change), and list each mismatch as a
  candidate amendment for the operator. OPEN Q1.

### R3. H3 -- the integer neural primitive helps and is used (deferred)

- v0.3 :150-153. Depends on R1's predicate and a comparison design (HD B-row). Not mapped in v0.1.

### R4. Infrastructure (no claim): epochs and receipts

- C-012's native epochs and receipts are transport, never evidence of H1-H3 by themselves. rso/scale
  LONG_DURATION_EXECUTION_ARCHITECTURE.md s3.5 already aligns: "CheckpointRecord = a Moonshot epoch (do not
  duplicate)". The Observatory's asks N1-N5 (s5) are answered separately (comms).

## Open questions for Palamedes (to settle before any adapter work)

Q1 Verdict mapping: score H1 against RSO as it is, or add typed states (a versioned schema change, operator)?
Q2 Native boundary: within-life delayed-cue survival has no episode reset. What is the named boundary; which
   carriers are ALLOWED/FORBIDDEN; is the reactive null an exact no-carry class or a labelled best-found baseline?
Q3 Interventions -> predicates: channel-cut as P-CHAN's disable arm? Which gate covers the destroying resample? A
   new predicate for the preserving sham? Survival (not an answer bit) as the outcome -> a new P-SURV-DEP?
Q4 The S-meter's role: producer or consumer instrument (the design says both, v0.3 :294-295 vs :325)? Who generates
   and holds the fresh qualification challenge (R-QUAL)? Stages recorded by Palamedes after an independent challenge
   (B:210-212)?
Q5 Vehicle: a new operator-authorized campaign in the C-009/C-010 pattern, or an amendment to slice-001? Which trace
   roles and layouts must be emitted (cf. WP:89-95)?
Q6 Statistics and origin: adopt C-010's INDETERMINATE and rso/reach's UNDERPOWERED/Holm for H2/H3? Can any ORIGIN
   claim be admitted (HD:39 "ORIGIN is a separate unresolved inference")?

No urgency: C-013 runs to 2026-10-12T06:45Z; this waits for it. Nothing here gates C-012.
