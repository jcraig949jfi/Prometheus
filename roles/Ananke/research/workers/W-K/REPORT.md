<!-- DEPOSITED VERBATIM by Ananke for worker W-K; sha256(report)=c14882d9e1fcac7d; delimited; see REPORT.provenance.json -->
# W-K: What minimum evidence shows an intervention reached its mechanism?

Worker W-K, namespace 0x5F0, 64 worlds (32 mirror pairs), 99% pair bootstrap. CPU only, 2 threads, no lease. About 25 min of compute in total.
Files are in roles/Ananke/research/workers/W-K/:
- PLAN.md (frozen before any scoring) and LOG.md.
- wk.py (plants, harnesses, fixtures), checks.py, score.py, accept.py, posthoc.py.
- out/: matrix.md (the fixture x check matrix), matrix.json, scores.json, accept.json, posthoc_win_iti2.json.

I read W-D's REPORT (allowed as a hypothesis source) before writing PLAN. I read no principal interpretation file until scoring was done.

## What I tested
I built 21 runnable PTE fixtures: 10 BROKEN and 11 VALID. No engine, lens or plant files were edited. Each bug lives where it lived in the real cases: in the harness (the arm's own code), in the arm spec, or in the design.

Broken fixtures (W-D case in brackets):
- **WIN-B** [1a]: delay == delta, drop window [t0, ro).
- **INERT-B** [1b]: freeze_routing under dest_mode "all", with cue-signed w writes that are never read.
- **UNWIRED-B** [2a]: the harness builds Controls from an old field whitelist, so freeze_rule is silently dropped.
- **TARGET-B** [2b]: non-normal arms are scored against targets y * key.
- **DEAD-B** [3b]: a conditional flush whose condition never holds.
- **SEED-B** [3a]: the same, plus arm worlds seeded from the arm label (no common random numbers).
- **PROBE-B** (Hauser): the condition probe does an in-place abs_ on in-flight payloads. It reports 0 hits but changes the outcome.
- **MASK-B** (mis-target): the reset mask is built from world 0's sensor and used for every world.
- **FORCED-B** [4]: reset_S at the readout tick. The readout reads S0, so this is forced for any genome.
- **SAT-B** [5]: an energy income cut that drains E but never binds the emission gate.

Valid fixtures:
- **Twins:** the same arm correctly wired.
- **Three true, non-vacuous nulls:**
  - V0-WIN: arrivals carrying the cue reach the actuator but are unused.
  - V0-ROUTE: w is read, but the writes are decorative.
  - V0-RULE: r toggles and is read, but both rules are identical.
- **TARGET-V:** also a true null (the bit is in flight, not in S).

All specimens scored normal &gt;= 0.99. All readings matched the design; no fixture was repaired. The broken fixtures produced 5 nulls, 3 spurious EFFECTs (TARGET, PROBE, FORCED), 1 AMBIG (MASK) and 1 SEED-B null. I did not search seeds for a spurious effect in SEED-B.

The 16 checks, all as frozen in PLAN, each return PASS, FLAG or NA:
- **K0** flag every null (strawman).
- **K1** temporal reach at the actuator (lens).
- **K1g** generic twin reach: does the declared variable differ between cue twins inside the arm's footprint?
- **K2** a must-flip positive-control plant run through the arm's OWN harness and spec, at specimen physics (c1b A3.1 rule). **K2iso** is the same plant through a reference harness.
- **K3** arm trace identical to normal. **K3b** end-state digest plus trace (the c1b no-op guard). **K3c** fewer than half the pairs changed.
- **K4d** the harness's self-reported applied count. **K4c** a counterfactual applied count from a shadow world, every tick.
- **K5** the declared variable changed at all.
- **K6a** arm-diff of actual inputs and targets. **K6b** the declared factor is present in World.ctrl / World.ph.
- **K7** a could-fail counter-plant (must-not-flip).
- **K8s** scramble the declared variable in the specimen.
- **K9** sham identity (the arm's code with the factor neutralised).

## What held (scored; lenient rule, NA = not flagged)

| check | caught | false alarms | J | mean cost/fixture |
|---|---|---|---|---|
| K2 plant through own code | 7/10 | 0/11 | **0.70** | 2 runs, 7.5 s |
| K2iso plant in isolation | 6/10 | 0 | 0.60 | 2 runs, 8.0 s |
| K1g twin reach | 5/10 | 0 | 0.50 | 1 run, 3.9 s |
| K3c pair coverage | 6/10 | 2 | 0.42 | free |
| K4c counterfactual applied | 4/10 | 0 | 0.40 | 2 runs, 8.0 s |
| K3 identical arm | 5/10 | 2 | 0.32 | free |
| K4d, K5, K9 | 3/10 each | 0 | 0.30 each | free / free / 1 run |
| K0 null strawman | 6/10 | 4 | 0.24 | free |
| K8s scramble | 4/10 | 2 | 0.22 | 1 run |
| K6a arm-diff, K7 counter-plant | 2/10 each | 0 | 0.20 each | free / 1.6 runs |
| K3b digest guard | 3/10 | 2 | 0.12 | free |
| K1 actuator reach, K6b | 1/10 each | 0 | 0.10 each | 1 run / free |

- **No single check is universal.** K2 is the best single check and misses exactly the three spurious positives: TARGET, PROBE and FORCED.
- **Minimum zero-false-alarm cover:** {K2, K4d, K7} at 12 s per fixture. Equal-size alternatives are {K1g, K2, K7} and {K2, K7, K9}.
- **K7 is the only zero-false-alarm check that catches FORCED-B.** K8s also catches it, but K8s false-alarms on 2 true nulls.

Which checks catch which failure shape (class to required reach evidence):

| shape | checks that catch it |
|---|---|
| Window miss | K1 or K2. The realistic version needs K1 or K2 (see the post-hoc run below). |
| Inert channel / saturated gate | K2 at specimen physics. Identical-arm checks also fire, but they cannot tell this apart from a true null. |
| Unwired switch | K2 (not K2iso), K4c, K6b, K3 |
| Dead branch / condition never met | K4d, K4c, K1g, K2 |
| No common random numbers | K6a, K9, K4c |
| Probe side effect | K9, K4d, K1g |
| Mis-targeted units | K1g, K3c, K2 |
| Wrong target | K6a, K9, K7 |
| Forced by readout | K7 only (plus K8s, which has false alarms) |

Operationally: a NULL needs K2 plus bookkeeping (K6a/K6b and an applied count). An EFFECT needs K7 plus K6a/K9. Windowed arms also need K1.

## What failed or surprised me
1. **An identical arm does not mean the intervention never took effect.** K3 and K3b false-alarmed on V0-WIN and V0-RULE. There, the variable was changed and is read by the physics, but the specimen does not use it. Identical output plus applied &gt; 0 describes both INERT-B and V0-RULE. Only K2, asking whether a plant that uses the pathway can be affected at this physics, separates them.
2. **The end-state digest guard (K3b, which is c1b's no-op guard) is weaker than trace identity.** In V0-RULE, r toggles back to r0 by the end, so the end states coincide. It also misses INERT and SAT.
3. **My scored WIN-B was easier than the real C1 case.** Its C1 window dropped nothing at all (applied 0, arm bit-identical).
   - Post-hoc (unscored, declared in LOG A8): at iti 2, stale waves fall inside the window. The broken arm then changes 390 tick-worlds and reads normal 0.961 vs arm 1.000.
   - Only K1 (reach 0.0) and K2 still catch it. K1g, K3, K3c, K4c and K5 all pass.
   - So the realistic window miss needs actuator reach or a plant through the arm.
4. **Some zero false-alarm rates are partly vacuous.**
   - K4d catches only the hook arms, because only hooks count their own hits. For Controls arms the harness "believes" whatever its spec says.
   - K7's counter-plants are sometimes trivially intact: c1b.at_specimen strips plastic_route or rules from the plant, and RELAY has no non-transport solver, so K7 was NA on WIN, SAT and a few others.
5. **I found a bug in my own checks during the smoke test (LOG A5).** K5 compared the normal run's S with the arm's r, and so "passed" an unwired arm. It was fixed before the full run. It is a live example of a check that can pass while testing the wrong thing.
6. **Predictions:** mine held (K2 at J 0.70; K7 the only clean catch for FORCED; K6/K9 the only catches for TARGET/SEED).

## Disagreements
- **With SYNTHESIS_2026-09-28_ARC2 and W-D:** "three checks plus an identical-arms alarm cover all 8." The identical-arms alarm is not needed for coverage (a zero-false-alarm cover exists without it). It also costs 2/11 false alarms on true nulls. It is only safe as a prompt to run K2, never as a verdict.
- **With SYNTHESIS_2026-09-27 section 6 and PTE_ENGINE_CARD:** "Remedy: a reach check (cue_arrival_profile)." Actuator reach applies only to windowed drop arms (1/10 fixtures). The generalized twin reach misses the realistic window miss. Reach is necessary for window arms, but it does not fix inert, unwired, saturated, forced or wrong-target arms. K2 is the broader remedy.
- **With c1b.intact():** it returns True for NOT_APPLICABLE ("intact by construction"). On UNWIRED-B and DEAD-B, a vacuous null would then pass as an absence reading unless A3 eligibility gates it. It should return NOT_VERIFIED.
- **W-D's core claim is supported:** going through the arm's own code matters. K2 catches UNWIRED-B and K2iso does not. That is 1 fixture, so the evidence is thin.

## Limits
- The fixtures and the checks share one author, so this is not an independent failure mode.
- There is one specimen per fixture, and the plants are perfect solvers, so the confidence intervals are degenerate.
- K8s scrambles after the tick, which is an imprecise match for in-tick resets.

## Proposed threads
- **T-K1:** a reach bundle in lens and run_battery: K2 plus K6a/b plus K4c for every null, K7 plus K9 for every effect, K1 for windowed arms. Each arm is reported as REACHED / UNREACHED / NOT_VERIFIED.
- **T-K2:** change c1b.intact(NOT_APPLICABLE) to NOT_VERIFIED.
- **T-K3:** fill the plant-library gaps: must-not-flip plants for RELAY, and counter-plants that keep the fixture's genome-space fields.
- **T-K4:** run the bundle on the real M3 cells (0a23398f, f6b623cd) to confirm that K1 and K2 catch the real window miss.
- **T-K5:** a blind fixture set built by a different worker, to test these checks independently.
