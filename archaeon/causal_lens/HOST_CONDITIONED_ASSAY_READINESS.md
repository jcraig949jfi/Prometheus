# HOST_CONDITIONED_ASSAY_READINESS (contract v0.2.1; 2026-09-27)

Nothing here is preregistered or launched (ruling s2, s4). Precondition (s4): the phenomenon must remain coherent under v0.2.
It does. NPE gives 16 coherent events (section 3 of V02_REGRESSION_REPORT). Archaeon's host-mediated reproduction stands on
material-typed execution accounting. BEE has genuine foreign-MATERIAL-governed copying (8,166 births in r016299), at a much smaller
scale than location-based counts suggested (B6).

## 1. Is "host-conditioned reproduction" definable in one causal language across Archaeon, BEE and NPE?
Yes, in v0.2 terms and with no byte-copy criterion:
HOST_CONDITIONED(donor material X, host body H, event t) holds when all three do:
  (a) FACTUAL: X is a factual contributor to the output of t realized in H (share >= a declared minimum, basis TRACE or DERIVED);
  (b) NECESSITY(H's prior state | intervention: substitute H's state with a declared alternative | outcome: the realized
      reproduction predicate) = YES;
  (c) SHAM: the same substitution with a sham alternative (H's own state restored, or a matched irrelevant perturbation) leaves the
      outcome = YES.
Optional (d): SUFFICIENCY(X | intervention: randomized host | outcome) = NO, NPE's P-11 C2 form.
The "reproduction predicate" is engine-declared on material shares, e.g. "output carries >= s of X's material". It is not fidelity to
a byte string.

## 2. Independent manipulation (holding the others fixed)

| engine | donor / material | host / body state | environment | how |
|---|---|---|---|---|
| Archaeon | YES | YES | YES | the attributed core: insert_ecology() places chosen tapes; a chosen neighbour genome = host state; inputs are an explicit argument; _birth() on the frozen VM (as in tests 02/08/09) |
| NPE | YES (implant bytes) | YES (P-11 already substitutes the victim half) | YES (cell spec: niche/task) | p11.interact() re-executes one pair interaction on a private tape with a private RNG |
| BEE | YES | YES, with a new single-interaction harness around vm.execute (partner tape = host state) | YES (inputs) | engine-specific limit: no native single-event re-execution API; the harness must use BEE's traced VM to get code MATERIAL (B6) |

## 3. Same abstract contrasts without pretending the mechanics are identical?
Yes. The contrast is always the realized host state vs a declared substituted host state vs a sham, with the donor material fixed.
The mechanics differ:
- Archaeon: an executor copies through a neighbour window.
- NPE: two programs share one tape.
- BEE: LDIR into a window, with self-copied code executing from the window.
Only the host-state object differs per engine: neighbour genome, victim half, partner tape.

## 4. Common endpoint
Per event: the outcome predicate holds in the realized host, fails under the preregistered host-state substitution, and holds under
the sham. Aggregate: the paired difference (sham minus substitution), over events drawn from preserved specimens, per engine.
The claim is cross-engine only if the sign agrees in all three.

## 5. What would falsify the cross-engine claim
1. Substitution does not reduce the outcome relative to sham in >= 2 of 3 engines.
2. The effect disappears once donor-write necessity is controlled (a donor-blocked arm explains it on its own).
3. The effect disappears under code-MATERIAL accounting (B6), i.e. the "host" was only where the donor's own code ran.
4. Sham substitution itself breaks the outcome (the intervention machinery, not the host state, is causal).

## 6. Inadequate identifiability
- BEE: occupant identity and code material are not persisted; host body = cell is not in the rows. A FULL replay is required for every
  specimen.
- NPE: donor body NOT_IDENTIFIABLE; continuity NI in 25/34 because victim-retained and same-value-rewritten bytes are not separated
  (prov vs lit per position is not persisted).
- Archaeon: adequate.

## 7. Paired sham hosts
- Archaeon: yes (restore the identical neighbour genome; or a matched random genome that has the same input-window bytes).
- NPE: yes (the victim replaced by itself, alongside P-11's randomized victim).
- BEE: yes, with the new harness (partner tape identical vs randomized vs matched).

## 8. Compute
Small. Single-interaction re-executions: Archaeon ~0.1 ms, NPE ~ms, BEE traced ~ms. At N ~ 200 events per engine x 3 conditions x a
few draws, this is minutes of CPU. Specimen harvesting is 1-2 min per BEE/NPE replay. Total well under 1 CPU-hour, single worker. No
GPU.

## 9. Can it wait for Bellerophon's campaign?
Yes. Nothing is time-sensitive, and the BEE harness needs building first.

## Draft skeleton (NOT frozen, NOT a preregistration)
- Q: does reproduction of donor material depend on host state, beyond the donor's own writes, in three independent engines?
- Specimens: events with factual donor contribution >= s, harvested from preserved records (Archaeon block 13/15 fossils; NPE H2
  RESERVOIR pair births; BEE code-material-resolved foreign-governed births from FULL replays). Sampling is fixed before any
  outcome is computed.
- Arms per event: REALIZED, SHAM (host restored), SUBSTITUTED (host randomized, matched on engine-declared nuisance bytes),
  DONOR-BLOCKED (control for criterion 5.2).
- Endpoint: the outcome predicate per arm. Primary: per engine, the paired sign test SHAM > SUBSTITUTED. Cross-engine: all three
  signs agree (sign agreement is the claim; pooled p-values are not).
- Kills: section 5. Required instrument checks: sham == realized in >= 95% of events (else the machinery is causal); B6 code-material
  accounting on for BEE.

## Readiness status
**READY_WITH_ENGINE_SPECIFIC_LIMITS**
Limits:
- BEE needs a single-interaction harness on its traced VM (code material) before its arm is interpretable.
- NPE continuity is NOT_IDENTIFIABLE for most events, so its endpoint must be stated on donor-material share, not on HU continuity.
- The operator decides whether and when to preregister.
