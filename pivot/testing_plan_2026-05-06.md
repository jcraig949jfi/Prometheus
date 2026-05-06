# Testing the Sister Projects — Dual-Track Plan

**Date:** 2026-05-06
**Owner:** Aporia (plan); execution split across Ergon (Learner track), Techne + Charon (Substrate track)
**Status:** Plan; awaits James greenlight before tracks begin

We have two distinct testing problems:

1. **Testing the Learner** — does Ergon's LoRA-tuned Qwen actually learn substrate-grade structure, or is it surfing trivial features / memorizing / failing for protocol reasons?
2. **Testing the Substrate** — does Techne's v2.3 kernel actually enforce the discipline it claims to enforce, or is the test suite green while the gauntlet is decorative?

These are different questions. Test suites verify code correctness; they don't verify epistemic claims. v2.3 has 607 tests passing in 53s — that's necessary, not sufficient. The substrate's claim is *the gauntlet catches false positives*. Verifying that requires adversarial work, not just unit tests.

---

## Track 1 — Testing the Learner (Ergon)

### Phase 0: Eval-protocol fix sub-sprint (~1 day)

**Why first:** the v0.5 tire-kick named the eval-protocol mismatch as the binding constraint. Fixing it surfaces the deeper diagnosis (capacity? feature rep? training scale?). Until this lands, all subsequent Learner measurements are confounded by the prompt-format prior toward numeric continuation.

**Implementation:** any of three fixes (logit masking restricted to label-vocabulary subset; yes-no reformulation; classification head over the 4 (or 2 post-fold) labels). Recommend logit masking — minimal architecture change, preserves the LoRA-on-base-model pattern.

**Acceptance test:**
- Re-run W4.1 with logit-masked decoding on the 17-entry corpus
- Re-run W4.2 with logit-masked decoding on the synthetic env
- W4.0 synthetic-null gate must re-pass under the new protocol

**Three possible outcomes, all pitch-positive:**
- **PASS_BEATS_MAJORITY:** LoRA hits >LR ceiling. Strongest pitch artifact. Names Phase 0 as the unblock.
- **CALIBRATED_FAIL_DEEPER:** LoRA matches LR within CI. Eval-protocol was real but not sufficient — deeper diagnosis (capacity / feature rep / scale).
- **SYNTHETIC_NULL_FIRES:** label-shuffled training under new protocol shows above-chance accuracy. The fix introduced its own pathology. Stop, document, redesign.

### Phase 1: Corpus discrimination via LR-control (~2-3 days)

**Why:** the 17-entry corpus has a 94-100% LR ceiling. No headroom for non-trivial Learner measurement. v1.0 needs a corpus where LR doesn't ceiling.

**Method:** run logistic-regression baseline on each candidate corpus. Pick the one with documented LR headroom + structural diversity.

**Candidate corpora (in priority order):**
1. **Cross-domain near-miss pairs from OBSTRUCTION envs** (when Techne v2.3 cross-domain rollout produces them — Days 14-17 of joint sprint)
2. **Different finite slices via bug-fixed brute-force** (deg12 ±5 palindromic, deg14 ±3 palindromic — Techne queued items)
3. **Mixed-feature corpora** combining poly_coefficients with KillVector v2.2 +8 components (RH-conditional bounds, isogeny-class membership, interpretive_slack signals)

**Acceptance test:** pick the corpus where LR baseline accuracy < 80% on held-out. Document the LR-control numbers. If no corpus passes the headroom test, name the corpus-quality bottleneck as the v1.0 binding constraint.

### Phase 2: Capability measurement on the LR-headroom corpus (~1 week)

**Method:** train LoRA on the corpus selected in Phase 1. Compare to LR baseline on the SAME held-out splits.

**Acceptance test (LoRA must beat all):**
- LoRA > LR on standard held-out (LoRA learned something LR can't)
- LoRA ≈ LR on reflection-pair held-out (LoRA isn't memorizing labels)
- LoRA > LR on structurally-distinct held-out (LoRA's learning generalizes beyond reflection symmetry)

If any of the three fails, document which specific failure mode fired. Don't ship a "LoRA wins" claim that wins only on one held-out structure.

### Phase 3: Cross-domain transfer (~2 weeks)

**Gated by:** Aporia standing constraint (≥100 per-claim kill records in ≥2 domains). Pre-Tier-0 0b cross-domain telemetry shipping (Techne ~1 day).

**Method:** train LoRA on domain A's records, evaluate on domain B held-out. Domain A and B must share a real bridge (per Study 03 / Study 14: BSD ↔ modular forms via modularity theorem; mock theta ↔ harmonic Maass via shadow operator).

**Acceptance test:** LoRA's cross-domain accuracy must exceed the per-domain LR baseline of domain B. If it doesn't, the cross-domain training is decorative — single-domain training would have produced the same numbers.

---

## Track 2 — Testing the Substrate (Techne + Charon)

This is the harder track. Test suites pass when code does what code-author thinks it does. Substrate testing verifies what the substrate CLAIMS — that the gauntlet catches false positives, that triangulation requires real independence, that ExclusionCertificates scope what's actually ruled out, that the KillVector components carry independent information.

Five testing protocols, each with an explicit acceptance criterion.

### Test 1: F-gate orthogonality MI audit (Charon G4 — already queued)

**Claim under test:** the 4-fold battery (F1 permutation null, F6 base rate, F9 simpler explanation, F11 cross-validation) provides four *independent* falsification gates. If F1 fires whenever F9 fires (high MI), the battery is effectively 3-fold or 2-fold, and the "4-fold" framing overclaims.

**Method:** compute pairwise mutual information between F1/F6/F9/F11 fire patterns across the existing 314K kill records. Per Charon pending task G4 (`aporia/meta/charon_pending_tasks.md`).

**Acceptance criterion:**
- All pairwise MI < 0.4 bits → battery is genuinely 4-fold
- Any pair MI > 0.8 bits → that pair is effectively redundant; battery is overstated
- Any pair MI > 1.5 bits → strict redundancy; one of the gates is decorative

**Pitch-positive regardless:** if MI is low, the substrate's 4-fold claim is empirically validated. If MI is high, the substrate's discipline catches the overstatement (file the finding, revise to N-fold where N is the empirical orthogonal-gate count).

### Test 2: ExclusionCertificate adversarial replay

**Claim under test:** an ExclusionCertificate scopes what's been ruled out. The Lehmer 97M poly brute-force enumeration produced one ExclusionCertificate (`certificate_type = exhaustive_enumeration`, `strength = complete`).

**Method:** introduce a single deliberate corruption — a known polynomial with M < 1.18 NOT in Mossinghoff but inside the deg-14 ±5 palindromic subspace. Re-run the brute-force with the corruption. The substrate should:
1. Detect the new candidate (it's in-band)
2. Produce a new INCONCLUSIVE on it
3. Refuse to upgrade to local lemma without triangulation
4. NOT mistakenly extend the existing ExclusionCertificate's `strength = complete` claim to cover it

**Acceptance criterion:** the substrate produces a different verdict (INCONCLUSIVE on the new candidate) AND flags that the existing ExclusionCertificate is no longer `strength = complete` (it now has at least one known unverified entry inside its scope). If the substrate silently extends the certificate, the ExclusionCertificate discipline is performative.

### Test 3: TriangulationProtocol independence test

**Claim under test:** TriangulationProtocol upgrades INCONCLUSIVE → LOCAL_LEMMA only when ≥1 proof-bearing path AND ≥1 independent replay path AND no contradicting path. The "independence" requirement (per `independence_class` in MethodSpec, v2.2 §6.2 P3) catches correlated methods masquerading as independent.

**Method:** submit a triangulation request where two of the three paths share underlying dependency (e.g., both invoke mpmath at different precision but same library version; same `independence_class`). The protocol should reject the triangulation as not-independent.

**Acceptance criterion:**
- Protocol detects the shared `independence_class` and rejects the upgrade
- If protocol accepts, the independence enforcement is decorative — log this as substrate finding, fix the protocol, re-test

### Test 4: Cross-domain gauntlet test

**Claim under test:** the substrate's pipeline is domain-aware. A claim PROMOTED in domain X should be killed (or marked inappropriate) when re-submitted in domain Y where it doesn't apply.

**Method:** take the deg-14 ±5 Lehmer triangulated local lemma. Re-submit through the BSD rank prediction env. The substrate should:
1. Detect the domain mismatch (the Lehmer claim has type `polynomial Mahler measure` but BSD env expects `elliptic curve rank prediction`)
2. Either reject the submission with a typed-mismatch error OR run the gauntlet and produce a kill at F1/F6 for trivial type-mismatch reasons

**Acceptance criterion:** the substrate refuses or kills the cross-domain submission. If it silently PROMOTES the Lehmer claim into BSD's substrate state, the cross-domain isolation is broken.

### Test 5: Synthetic-null at the substrate layer (gradient archaeology re-run)

**Claim under test:** the gradient archaeology finding (kill_pattern carries 0.725 bits MI with operator class across 314K kills) reflects real failure-shape geometry, not corpus artifact.

**Method:** shuffle the operator-class labels across all 314K kill records. Re-run gradient archaeology. If the same 0.725 bits MI appears under shuffled labels, the original finding was capturing corpus correlation, not operator-induced kill-pattern structure.

**Acceptance criterion:**
- Shuffled-label MI < 0.1 bits AND original MI ≥ 0.5 bits → operator-class effect is real
- Shuffled-label MI ≈ original MI → original finding was corpus artifact; substrate-grade negative finding, file and revise downstream claims

This is the same synthetic-null discipline Ergon's W4.0 uses, lifted to the substrate-layer claim.

---

## Sequencing

Track 1 and Track 2 are independent. They can run in parallel.

**Week 1 (this week):**
- Track 1 Phase 0: Ergon eval-protocol sub-sprint (1 day)
- Track 2 Test 1: Charon G4 F-gate orthogonality MI audit (1-2 days; gates on Pre-Tier-0 0b telemetry — already queued for Techne)

**Week 2:**
- Track 1 Phase 1: corpus discrimination (LR-control on 3 candidate corpora)
- Track 2 Test 5: substrate-layer synthetic-null on gradient archaeology
- Track 2 Test 2: ExclusionCertificate adversarial replay

**Week 3:**
- Track 1 Phase 2: capability measurement on LR-headroom corpus
- Track 2 Test 3: TriangulationProtocol independence test
- Track 2 Test 4: cross-domain gauntlet test

**Weeks 4+:**
- Track 1 Phase 3: cross-domain transfer (gated on Aporia standing constraint + Pre-Tier-0 0b)
- Both tracks: file results dossier, update watchlist with empirical findings

## What outcomes look like for the pitch

Every test in both tracks produces a pitch-positive result regardless of direction:

| Outcome shape | Track 1 (Learner) | Track 2 (Substrate) |
|---|---|---|
| Test passes (positive) | "Learner beats LR baseline at scale" | "Substrate's claims empirically validated" |
| Test fails calibratedly | "Substrate's discipline named the binding constraint; v1.0 plan reflects it" | "Substrate caught its own overstatement; revised claim filed" |
| Synthetic-null fires | "Memorization detector worked at expected layer" | "Substrate-layer null caught corpus artifact masquerading as structure" |

The only failure mode that's pitch-negative: running tests without the synthetic-null guards. The guards are non-negotiable.

## What this plan does NOT cover

- Performance benchmarking (substrate runtime, Learner inference latency) — engineering measurement, not epistemic
- Stress testing under load (high-throughput claim submission) — engineering measurement, not epistemic
- Adversarial prompt injection on Ergon's LoRA — relevant for v1.0+ deployment, not substrate-grade testing
- Full G6 (Lehmer ExclusionZone topology) — gates on Techne's ExclusionCertificate schema being stable; it is post-v2.3, but G6 work itself is downstream of the testing track. Track G6 separately.

## Standing offer

I can dispatch each Track 2 test as a Charon mandate (paste-ready prompt in the same format as the Substrate Cartography Suite). Track 1 work is Ergon's lane; my role is reviewing the outcomes and updating the watchlist.

Say go on which tests to fire first and I'll produce the Charon prompts.

— Aporia, 2026-05-06
