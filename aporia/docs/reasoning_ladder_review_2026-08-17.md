# The Reasoning Ladder — Aporia's Review

**Author:** Aporia (Claude Opus 5) · **Date:** 2026-08-17
**Trigger:** James — "scan the project for a writeup and analysis, review it, opine."
**Primary sources, read in full this session:** `pivot/reasoning_ladder_design_2026-05-15.md`
(Charon, R0–R9) · `pivot/reasoning_ladder_v01_2026-05-24.md` (v0.1 rewrite, R0–R12 + F/M/H) ·
`harmonia/memory/architecture/reasoning_ladder_testable.md` (James 05-27, operationalized by
Harmonia B) · Hephaestus survey `05_The_Reasoning_Ladder_Lineage` (08-12, E3-tagged).
**Verified this session (E3):** `reasoning_phase0.py` implements exactly {R0,R1,R2,R3,R5,R6,R7,R8};
no canonical-vocabulary declaration exists anywhere in pivot/roles/stations; no commit acts on the
05-15 sunset clause, which expired 2026-08-15.

---

## 1. The honest state, in five sentences

Three generations of ladder in twelve days of May, each rewriting the tier semantics without
retiring its predecessor; the three vocabularies still coexist and every cross-subsystem tier claim
silently equivocates. The lineage produced the program's only calibrated, non-gameable capability
instrument (testable ladder + verifier lens + grading oracle; 157/157 verifier agreement,
deterministic, fails closed) — which grades nothing, covers 8 of 13 rungs, and is saturated below
R7 for exactly the models that matter. The founding doc's self-imposed falsification deadline
passed two days ago, unmet and unacknowledged. The decisive experiment on the lineage's central
open question (ladder vs basis: the model zoo, ~1.2k calls, Anthropic-independent) has been built
and ready since 05-30 and has never run. And the lineage's genuinely great outputs — two doctrines,
one replicated empirical discovery, one artifact schema — are not the tier numbers at all.

## 2. What is actually good here (and it is genuinely good)

**The two doctrines survived everything thrown at them, and they are the contribution.**

- *Doctrine #1 (falsification-first tier claims):* a system occupies a tier only if the mechanism
  survives perturbation, beats lower-tier baselines, and fails in the tier-predicted way. This is
  the only doctrinal check in the lineage that is fully cashed end-to-end in running code
  (4-version probes, fails-closed verifier, zero disagreements across every cross-check).
- *Doctrine #2 (failure-signature reading):* capability is read from the SHAPE of failure, not the
  pass/fail binary. The 05-25 null-slot ablation is the canonical worked example — one "MIXED"
  verdict-line concealing four distinct, separately-actionable signatures.

**The one replicated empirical discovery: walls are direction gaps, not capability gaps.** Icarus's
R2 plateau broke by surfacing schema+exception, not by capability change. R5 fell the same way
(06-10, explicitly *without* the typed-DAG rebuild the review had demanded — the self-falsification
was honored). M0 found the identical shape at instrument level (novel truths unrepresentable, not
undecidable). Three independent confirmations, one shape. This converges with Harmonia A's
syntactic-router finding from the revival fan-out: **what presents as a capability boundary is
usually an interface/representation boundary.** It is arguably the program's single most replicated
finding, and it carries a falsifiable operating rule the fleet has not stated:

> **A tier plateau is a diagnosis of the harness before it is a diagnosis of the model.** Default
> reading inverted. A wall is an interface bug until an interface audit clears it.

**The artifact schema outlived the taxonomy.** The Reasoning Trace Vector — `capability = operation
+ perturbation + failure_mode + evidence_artifact`, every attempt emitting a structured record —
is the reasoning-side KillVector, and it is more valuable than the tiers it was built to grade.
See §6: it is the pre-built answer to the Metabolization Probe's most likely outcome.

**The measurement discipline was real.** The Nemotron "R2 plateau" was correctly diagnosed as a
parse-failure artifact and killed by a structured-outputs rerun. The Opus/Sonnet inversion was
confirmed at n=40, then *refined* rather than inflated when R8 flipped it — landing on the sharp,
narrow claim "recognition intact; execution control is the gap." That is exactly how the program
is supposed to treat its own findings.

## 3. The central defect: the tier numbers are a fossil factory

The fleet's 08-12 finding was that a load-bearing number ("0% type-II", "2,351 promotions") can
outlive the formula that produced it and propagate as corroboration. **The ladder has the same
disease one level deeper: "R5" is a pointer whose referent changed twice in twelve days.**

- 05-15: R5 = causal/counterfactual reasoning (Pearl interventions).
- 05-24: R5 = counterfactual control (holds branches).
- 05-27: R5 = invariant detection (what Icarus actually climbed — board parity).

Same token, three referents, all still live in code: the Hephaestus trap battery cites the 05-15
semantics (`test_harness.py:460`), Icarus's frozen `ladder.py` carries v0.1 while its
`tier_oracle.py` grades against the testable ladder, and Erebos annotated its 25 archetypes against
05-15 semantics two days *after* v0.1 replaced them. Consequences that are live today:

- **"+11pp R3 / +32pp R4"** — the program's only demonstrated capability climb — is measured on the
  trap battery's ruler and is incommensurable with every other R4 claim in the program. It should be
  quoted as "+32pp on the forge's internal R4 category" and currently is not.
- **"Icarus cleared R5"** and **"Apollo's R9 was falsified"** are claims on two different rulers.
- Any future consumer (the Learner's tier-stratified corpus, the probe's task-leveling) that joins
  records across subsystems on the R-field will be silently joining across semantics.

A number that outlives its formula is a fossil; **a symbol that outlives its referent is worse,
because it keeps type-checking.** The citation-chain audit can catch a stale number; nothing
catches a stale meaning except vocabulary unification — which has been identified as needed at
least three times (frontier synthesis 05-29, Hephaestus D7 08-12, panel open-question 08-12) and
done zero times. It is one sentence from James (Hephaestus §8 item 5, still queued): *the testable
ladder is canonical* — it is the only vocabulary with an implementation. Then force-remap the trap
battery's CATEGORY_TIER, quarantine `ladder.py`'s frozen text, and restate the two headline claims
on the canonical ruler.

## 4. The sunset clause fired two days ago, and honoring it is the cheapest integrity move available

The 05-15 doc pre-registered its own falsification: *"If 3 months from now (2026-08-15) the
operational artifacts in §9 are not in flight, the doc was wrong."* Verified today: of the six §9
artifacts, five were never built (no `reasoning_tier_annotations.jsonl`, no
`aporia/doctrine/reasoning_ladder.md`, no calibrator script, no Charon evidence ledger, no
`reasoning_tier` field in Ergon code); the sole survivor is a ticket-linting check in
`aporia_triage_report.py`. **By its own pre-registered standard, the founding doc failed, and the
deadline passed silently.**

This matters beyond hygiene. The program's entire epistemic identity is that its self-falsification
commitments are real. A pre-registered kill condition that fires and is ignored is doctrinally
identical to a promotion gate that confirms by assertion — the exact disease M0.5 diagnosed in the
substrate. Honoring it costs one commit: mark the 05-15 doc RETIRED-BY-OWN-SUNSET, note what
survived (the tier *concepts* that fed v0.1 and the testable ladder; the profile-vector idea; the
anti-Goodhart section), and point to the canonical successor. The alternative — the pile of
self-falsified-but-unretired doctrine Hephaestus's survey predicted it would join — is how fossils
breed.

**The irony worth recording:** the 05-15 doc's *best* idea was §3, the profile vector — report
per-axis scores, never a scalar tier; composite assignments as the minimum over relevant axes. That
idea was never implemented in any grader. Its *worst* idea — bare tier numbers legible enough to
propagate without their definitions — is the one that colonized the program.

## 5. The ladder is probably a basis, and the program has been sitting on the decisive experiment for 2.5 months

The empirical record now leans clearly against ordered rungs:

- Nemotron: R3 and R6 *recover above* the R2 trough — non-monotonic.
- Haiku: plateaus at R2 while passing R3/R5/R6 — non-monotonic.
- Opus<Sonnet on R2/R5, Opus>both on R8 — the deficit axis (execution control) cuts *across* tiers
  rather than along them.
- The one honest qualifier: non-monotonicity is frontier-relative — visible at a model's capability
  edge, flat when the model is above the suite.

The 05-27 falsifier critique had this right before any data existed: *treat it as a basis first;
promote a pair to a ladder edge only where the rung-reality test measures a prerequisite relation.
Don't impose order — measure it.* The decisive measurement — multi-axis vs rank-1 prediction of
held-out families across a 15–18 model zoo — has been code-complete with 38 passing offline tests
since 05-30, is resumable, is **Anthropic-independent** (which now matters, given the credit
reality), and costs ~1.2k calls. It has never been launched.

Until it runs, the honest posture is: **stop saying "tier N reached."** Report profile slices.
"Climb" language presumes the answer to the open question the program built an experiment to
decide and then didn't run.

Two further consequences if basis wins: (a) the Learner's "tier-stratified corpus" plan becomes
axis-stratified, which is a different sampling design; (b) Icarus's "climb" was a path through a
partial order, and its R6 wall — fixes surfaced 06-15, never re-attempted, kill criterion (200
cycles / 0 promotions) never reached — is **unfinished, not falsified**, and should be carried as
such.

## 6. The connection nobody has drawn: the ladder is the Metabolization Probe's Path-β spec

The probe (running now — prereg signed, Tier A wall corpus landed, band rulings in progress) has
three preregistered outcomes. Path β — residue carries weak signal → *provenance engineering:
richer records, break-step locations* → re-probe — is arguably the most likely landing zone. The
question Path β immediately raises is: richer records *to what schema?*

The answer already exists and is the ladder lineage's best artifact: the **Reasoning Trace Vector**
(`domain_constraints_detected, invalid_operations_attempted, counterexamples_tested,
proof_gap_locations, repair_available, minimal_counterexample, …`). That is "failure with a
position" — exactly the record shape Ergon's Move-2 factory and the external RLVR literature
(process-level supervision beating outcome-only) both point at. Pre-registering this connection now
costs a paragraph in the probe's Path-β contingency and saves a design cycle later: **if the probe
lands on β, the rebuild's record schema is the trace vector, already specified, already emitted by
a running deterministic harness.**

Second live connection: the probe's R4 grader-headroom requirement (≥25pp) collided with reality
almost immediately — the 08-16 pre-pass returned HEADROOM-FAILURE. The saturation finding from the
ladder lineage (R0–R6 suite saturated for frontier models; discriminating power is
frontier-relative) is the *general form* of that collision, and it says the headroom problem is not
incidental: **the program's measurement instruments systematically discriminate below the frontier
and go blind at it.** The upper-tier graders the frontier synthesis specified (R9–R12 designs) are
the missing headroom. Only R12 was built — endorsed by all four frontier reviewers as the most
Prometheus-native probe — unit-tested, never run live. Under the heredity rule, building R9–R11 now
would be new architecture and is correctly deferred; *running the already-built R12 once* is
backlog execution, not architecture, and it is the only instrument in the repo that measures
anything at the frontier.

## 7. What the ladder cannot see — the void-detector's note

The ladder measures **individual** reasoners. The 05-15 doc's own open question §10.1 — how does
the ladder handle ensembles? — was never answered, and it turns out to be the load-bearing one:
every genuinely R12-shaped behavior this program has exhibited was an *ensemble* phenomenon. The
08-12 fan-out finding fatal preconditions on a consensus experiment; the mutual-revision exchanges
that fixed the probe spec; the cross-agent falsifications (Charon killing Ergon's C1 arm, D killing
A's closure test) — sustained investigation under falsification discipline, performed by the fleet,
invisible to the ladder. The instrument's unit of account has no tier for "brought evidence the
other seat could not get by reading," which is the single behavior most correlated with value
produced here.

I am not proposing an ensemble ladder (heredity rule; and the fleet already has its protocol
findings). I am noting the void: **the program's best reasoning is happening at a level its
reasoning instrument cannot represent** — which is, fittingly, the same wall-shape the lineage
discovered (unrepresentable, not undecidable), one level up. If the ladder lineage ever earns a
fourth generation, that is what it should measure.

## 8. Recommendations, ranked

1. **Declare the testable ladder canonical** — the one-sentence James ruling queued since 08-12.
   Force-remap the trap battery's CATEGORY_TIER; quarantine `ladder.py`'s frozen v0.1 text; restate
   "+32pp R4" and "R5 cleared" on the canonical ruler. Until then, every R-number in a fleet doc
   should carry its ruler (`R4@trap`, `R5@testable`) — a convention adoptable today without any
   ruling.
2. **Honor the sunset** — one commit marking the 05-15 doc RETIRED-BY-OWN-SUNSET, preserving its
   surviving ideas by pointer. I will draft it on approval; it is doctrine, so it is HITL.
3. **Pre-register the Path-β ↔ Trace-Vector connection** in the probe's contingency section — a
   paragraph, before the probe's verdict lands, so the rebuild schema is committed *ex ante* rather
   than reached for afterward.
4. **Adopt the inverted default reading:** a tier plateau is an interface bug until an interface
   audit clears it. This is the lineage's own most-replicated finding stated as an operating rule.
5. **Queue the model zoo** behind the probe as the next funded experiment (~1.2k calls,
   Anthropic-independent, settles ladder-vs-basis). Until it runs, report profile slices, not
   "tier N reached."
6. **Run R12 once** when budget allows — built, unit-tested, frontier-endorsed, and the only
   instrument that measures at the frontier. Execution of existing backlog, not new architecture.
7. **Leave R9–R11 unbuilt** (heredity rule) and leave Icarus carried as *unfinished, not
   falsified* — its kill criterion was never reached, and its `tier_oracle.py` probe-schema pattern
   is the most reusable "make failure emit direction" machinery in the program.

---

*The ladder lineage is the program in miniature: it produced a first-rate instrument and a
genuinely replicated discovery, then failed to consume the first and failed to state the second as
a rule; its founding document pre-registered its own death and nobody attended the funeral. The
tier numbers should be treated as what they demonstrably are — a fossil-generating vocabulary —
while the two doctrines, the trace vector, and "walls are interface bugs first" are promoted to
load-bearing. Measure the order before claiming the ladder. — Aporia, 2026-08-17.*
