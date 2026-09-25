# CW01 priority loop - boundary report, cycle 7 (CYCLE7_2026-09-19)

Scope: computational artificial-life / algorithm-search research on integer programs in software
worlds. No biological material, organisms, sequences or wet procedures. No external model or service
was called; INFRASTRUCTURE_BOUNDARY count 0.

Primary question: can evolution discover computation whose behaviour depends on lifetime context when
no single invariant policy can achieve high reward? Answer this cycle: NO - and the obstruction is
below the boundary the question assumed. This is the CRITICAL NEGATIVE RESULT, recorded as required.

## 1. Reconcile and freeze

Six RECONCILE-7 notes; batch I added 9 candidates; 27 competed. Slots: deformation P (P-I03), W
(P-I01), X (P-I04); serendipity P-I06, P-I08; anti-gravity P-I09, P-I07; by score P-I02, P-H06,
P-F07 (a cycle-4 candidate the score admitted). P-I05 (bounded bundle: periodic's attractor, doses to
8, long neutral windows) waits at 30.

| rank | id | parent | slot | why it survived |
|---|---|---|---|---|
| 1 | P-I03 | T-X17 | deformation P | prefix as a control interface: six manipulations, geometry and competence apart |
| 2 | P-I01 | T-X21 | deformation W | context worlds A / B / C with formal ceilings and controls |
| 3 | P-I04 | T-X20 | deformation X | recombination under context pressure with new-surface archiving |
| 4 | P-I06 | T-ARCH5 | serendipity | grammar-B evolution in world B |
| 5 | P-I08 | T-ARCH4/W1 | serendipity | geometry census of context-evolved organisms |
| 6 | P-I09 | T-ARCH4/W1 | anti-gravity | cue-reliability / block dose: is C escaped by cue-following |
| 7 | P-I07 | T-X12 | anti-gravity | persist-channel knockouts during evolution |
| 8 | P-I02 | T-X21 | score (requires P-I01) | behavioural forensics of what evolved |
| 9 | P-H06 | T-ARCH4/M1 | score (bounded) | reach-weighted damage, floor-conditioned promotion |
| 10 | P-F07 | T-X13 | score (bounded) | weather dose in Proteus on the qualified ruler |

## 2. The worlds and their formal ceilings (before execution)

Regime 0 expects v, regime 1 expects 15 - v. No phase variable, mode bit, clock or memory operation.
A OBSERVABLE: [PUT tag v] [ASK tag r]. B REMEMBERED: [CUE 1 c] [PUT tag v] [ASK tag]. C PREDICTIVE:
one lifetime of 16 trials, regime held 4 trials then flipped, cue reliability .7. Ceilings on 200
sets (mean / p95): invariant A .60 / .75, B .59 / .75, C .50 / .50; cue-follow A 1.0, B = invariant,
C .69 / .88; tracker C .77 / 1.0. Thresholds A .90, B .80, C .80. Controls: destroyed-cue populations
evolved (B, C); shuffled / no-cue / destroyed evaluated on B tops.

## 3. Results

- **P-I01 NOT_CROSSED in A, B and C, every seed.** Top-4 held-out A .52 / .48 / .52, B .55 / .41 /
  .50, C .50 / .50 / .50 - at or below the invariant ceiling, including world A where the regime word
  is visible and cue-reading scores 1.0. Destroyed-cue controls reach the same .45-.53 (no loophole); B
  tops fall to .39-.50 under shuffled / no-cue and .20-.33 under destroyed cues.
- **P-I02 - the plateau named.** Every A and C top answers IDENTITY (answer = v on 100 percent of
  asks). In A the regime word is READ INTO A REGISTER (a register predicts the regime with accuracy 1.0
  in every top) and NEVER USED: overwriting it changes 0 percent of answers. B tops are cue-perturbed
  (the cue changes 94 percent of answers) but correctly only 58 percent. C: adaptation flat, anticipation
  at chance, recovery flat, transfer .50. The exploited invariant is identity; the obstruction is a
  ZERO-GRADIENT PLATEAU - from identity every single mutation scores <= .5 because the conditional
  complement needs read + branch + NOT + AND assembled at once, while the information is already present.
- **P-I09 BELOW_CUE.** World C tops score exactly .50 at cue reliability .55 / .70 / .90 and at block
  8 (cue-follow ceilings .56 / .74 / .93): even a 90-percent cue is not followed. Dose-independent.
- **P-I07 NONE_CROSS.** persist=none and persist=tape collapse to .02-.06 (registers cleared each tick
  cannot carry v from PUT to ASK); regs / all / inherited reach the plateau. Register persistence is the
  seat of value carry; the plateau is channel-independent.
- **P-I06.** Grammar B reaches the same plateau to three decimals (.547 / .406), immune tops.
- **P-I04.** Splice and mutation arms identical in crossing (none); shapes converge to the world
  attractor (B immune, C ask-time); one transient NEW surface (C, gen 75, held .50) archived, not followed.
- **P-I08.** No context-evolved shape outside the manifold (0/208): A immune 25 / ask-time 20 /
  start-anchored 3; B immune 48/48 (the cue tick selects idle-tick immunity); C ask-time 48/48.
- **P-I03 UNRESOLVED by rule; the prefix is NOT a control interface.** 640 host insertions transfer
  competence in 0 percent; JMP rewiring changes nothing. Ask-time donors: the first 8 instructions keep
  geometry 1.0 and reward .75, relocating the first 1-4 destroys the geometry - sequence content run
  from its entry; a jump over a NOP into the intact donor keeps everything. Start-anchored donors:
  whole-program (no truncation keeps it) and position-tolerant (relocation keeps .5-.75).
- **P-H06 PROMOTED (secondary).** Damage lives in reached code (.40 vs .05, disjoint bands); the
  operand-slot ordering a > b > c holds within reached code and on floor-conditioned held-out families in
  every stratum (59 / 91 programs): the register-field operand is the fragile slot - grammar-level.
- **P-F07 (bounded).** Weather never lowers loss on the qualified ruler (+.00 to +.12); the state
  response is dose-dependent: persistent words 652 (p .25) / 116 (.50) / 19 (.75) vs 270 sham at 120
  generations - light weather raises state, heavy weather strips it (T-X13's e01 direction at high dose).

## 4. CRITICAL NEGATIVE RESULT and the successor world

Exploited invariant: IDENTITY (echo v), with the regime word ingested into a register and unused.
Loophole record (mechanism): information without a fitness path - the world is valid (controls at the
ceiling, no leak) but the transform 15 - v is several coordinated mutations from identity, and every
intermediate scores no better than identity with balanced regimes.
Smallest successor (constructed, ceilings computed, preregistered as P-J01, NOT run): A' / B' / C'
identical except regime 1 expects v XOR 1 (the low bit flipped). Invariant ceilings unchanged (.60 /
.59 / .50); the conditional answer is ONE instruction (XOR of the regime register and the value
register) from the plateau, so the ingested register acquires a fitness path. Provable: any fixed
transform of v still matches one regime per v. loop/SUCCESSOR_WORLDS_CYCLE7.json.

## 5. Promotion standard applied

No context-sensitive mechanism was proposed: performance impossible for the best invariant policy was
not achieved in any world. Promoted this cycle: the operand-slot ordering (P-H06: floor-conditioned
held-out families, every stratum, within reached code) as a grammar-level mechanism of damage.

## 6. COORDINATE STATUS

| coordinate | LOCAL | CROSS_WORLD | CROSS_LINEAGE | RULER_INVARIANT | RULER_DEPENDENT | CAUSAL_SUPPORTED | BROKEN | UNRESOLVED |
|---|---|---|---|---|---|---|---|---|
| T-X21 world attractors | yes | yes | yes | yes | - | yes (selecting world; P-I08: the cue tick selects immunity) | as a route to context computation: the attractor is a PLATEAU | the successor world |
| identity plateau (new) | yes (A, B, C, all doses, both grammars, both birth operators, all persist channels) | yes | yes | yes | - | register transplant: the ingested regime word is causally inert | - | whether a one-instruction transform gives a path (P-J01) |
| prefix as interface | - | - | - | - | - | no (0/640) | BROKEN | - |
| ask-time geometry | yes | - | yes | yes | - | sequence content from entry (relocation kills, jump-entry keeps) | as separable prefix | - |
| start-anchored geometry | yes | W1_d4 attractor | yes | yes | - | whole-program, position-tolerant | as truncatable | mechanism |
| operand slot (M1) | yes | held-out families | yes (every stratum) | yes (scattered ruler) | - | reach-conditioned | - | PROMOTED |
| register persistence (P-I07) | yes | - | - | - | - | none/tape collapse to .02-.06 | - | - |
| T-X13 weather state response | yes | Proteus + e01 agree on the dose axis | - | yes | - | dose (p .25 raises, p .75 strips) | - | crossing dose |

## 7. Continuation

- P-J01 (cycle 8): the successor worlds; then transforms of increasing mutational distance (XOR 3,
  XOR 15, 15 - v) to measure the reachable step; population / episode-count doses if not crossed.
- P-I05 (waiting): periodic's attractor world, doses to 8, long neutral windows.
- T-X13: the weather dose crossing near p .5 (bounded).

## 8. Stasis, nodes, defects, interface, teardown

No new stasis (6: T-ARCH4/R1, T-E07, T-X15 scoped; T-E09, T-X06, T-X08 bare). No new node (the
plateau is recorded on T-X21 and as specimen SPEC-X21-PLATEAU; a node is opened when P-J01 shows whether
it is crossable). Pool 39. Ledger 89 (no new defects). Specimens 16 (added: the plateau with genomes,
the successor world, the prefix non-interface). Campaign 6 machinery untouched. All drivers exited;
writer lock checked; production seats untouched; Archaeon originals unedited (9cd33ff1e).
