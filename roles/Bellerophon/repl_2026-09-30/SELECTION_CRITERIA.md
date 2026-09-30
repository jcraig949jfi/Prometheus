# E-BEL-REPL-01 -- selection criteria (written BEFORE the candidate ranking was read)

Lane: CWO 2026-09-30 s3 BELLEROPHON CURRENT (Aporia #1033). Work order: MWO-0004 + CWO-2026-09-30.
Author: Bellerophon (M2 / SPECTREX5). Written 2026-09-30 ~09:25Z, while a read-only fleet survey was running and
before its output was read. Disclosure: I am not blind to the candidate universe; I already know the fleet's
recent history from my own sessions (Archaeon ENVGATE/PORTABILITY/attribution, my own coupling and multi-day
results). These criteria are fixed so that the pick can be checked against them, not so that it is blind.

## Hard filters (a candidate failing any one is ineligible)

F1 Custody. Rebuilding and attacking it must not read, execute against or otherwise consume a sealed holdout
   (Cosmos D2 and anything marked sealed/holdout/custody), and must not break an independence protocol that
   another seat's claim depends on.
F2 Unresolved. Not already killed by a baseline or control, and not already independently replicated. A disputed
   or contested kill counts as unresolved.
F3 Emergence-like. The claim is that some structure, mechanism or capability arises that was not put in by the
   designer: a mechanism change, an unexpected organisation or a capability jump. A plain statistical association
   does not qualify.
F4 Reconstructable. It can be rebuilt in BEE (prometheus/toolbox) from its PUBLISHED description and public
   code/artifacts, within MWO-0004 R2 (<= 16 CPU core-hours for the item). "Rebuilt" means re-implemented from the
   text. Re-running the source engine is a reproduction, not an independent replication, and does not count.
F5 Killable. At least one untried kill path exists (null, cheap baseline, confound, representation swap,
   seed/pseudo-replication audit, admission-gate selection) whose outcome can be written down before running.

## Ranking (applied in this order among eligible candidates)

R1 Strength of the existing evidence: effect size against its own control, number of independent seeds or
   worlds, and whether a replay exists.
R2 Load: how many fleet decisions or next experiments depend on the claim being real.
R3 Independence: another seat's signal is preferred to my own (I cannot independently replicate myself). Own
   residuals (multi-day LADDER1/COPIER, coupling ECHO) enter only with that discount stated.
R4 Kill cost: the cheapest decisive kill battery wins ties.

## What "make it disappear" means here

The rebuild is scored against a kill battery frozen in the prereg (S1) before any run. Outcomes are:
- SURVIVES: the phenomenon reappears in BEE and outlives every kill in the battery. It goes to NEXT (mutant/falsifier
  expansion). It is not promoted.
- DISAPPEARS: a named kill removes it. The failure shape is recorded (which kill, by how much, on which population).
- NOT_REBUILT: BEE cannot express it. The missing concept is recorded; this is a finding about BEE, not about the
  claim.
- INCONCLUSIVE: the positive control fails, or the power is too low. The reason is recorded.
A rebuild that does not reproduce the phenomenon is not by itself a kill of the source claim (instrument error is
not evidence). It is reported as a transfer failure, with the gap named.
