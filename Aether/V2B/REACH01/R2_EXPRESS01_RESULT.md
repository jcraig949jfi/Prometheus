# REACH01 R2 / EXPRESS01 RESULT: minimum physics for composition (planted; expressibility only)

Code: R2/express01.py. Evidence: R2/express01_results.json. CPU reference kernel (deterministic; no GPU needed).

## Physics family
aeth01.op_<OP> = aeth01.v1 unchanged, except a winning TEMPLATE write stores OP(existing, incoming). P0. The
historical law (REPLACE = aeth01.v1) is untouched.
- Calibration ops: XOR, ADD (mod 256), AND.
- Alien ops, each with a stated rationale:
  - SPLICE = (existing & 0xF0) | (incoming & 0x0F): an asymmetric part-state / part-input merge;
  - ROTX = rotl8(existing, incoming & 7) ^ incoming: an input-keyed state rotation plus mixing.
Gadgets run in the ECONOMICS.md execution-only regime (w=1, m=0, no rain), so one-shot writers and activation-chain
delays are exact. The same C3 gadget gives an identical function table under B_balanced over its 4-tick life, for
every op.

## Planted gadgets (deliberately designed; NOT discoveries)
- C0 transmission
- C1 state-dependent combination
- C2 delayed retention (4-step activation chain)
- C3 two-input response
- C4 two-part composition: part 1 computes x = OP(a, b) in T1; part 2 activates T1 and combines x with c in U
- C5 three-stage multi-step: C4 plus U -> V combined with d

Inputs range over {0x0F, 0x33, 0x55, 0xAA}. "Depends" means STRICT dependence: in every slice of the other inputs,
varying the input changes the output. Ablated arms must show no dependence in any slice.

| op | C0 | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|---|
| REPLACE (aeth01.v1) | pass | **fail** (no dependence on prior state) | pass | **fail** (last writer wins) | fail | fail |
| XOR | pass | pass | pass | pass | pass | pass |
| ADD | pass | pass | pass | pass | pass | pass |
| AND | pass | pass | pass | pass | fail (information loss: strict 3-input dependence fails in some slices) | fail |
| SPLICE (alien) | pass | pass | pass | fail (the second input overwrites the first's nibble) | fail | fail |
| ROTX (alien) | pass | pass | pass | pass | pass | pass |

C4 certificate, for XOR, ADD and ROTX alike:
- the output depends strictly on a, b and c;
- removing part 1 kills dependence on a and b; removing part 2 kills it; removing both kills it;
- invariant under translation (3, -4) and under random surroundings beyond a 4-site energy-0 moat (2 seeds);
- 3/3 component shuffles (one component re-aimed and re-fielded) break the table.

C5 for XOR/ADD/ROTX: removing any one stage (P1, P2, P3) removes dependence on every input upstream of that stage.

## Dispositions
- aeth01.v1 (REPLACE): **EXPRESSIBILITY_STILL_BLOCKED** at C1. The exact missing capability is STATE-DEPENDENT
  COMBINATION. An incoming value replaces the target byte, so a site's next value never depends jointly on its
  prior state and an input. Transmission (C0) and retention (C2) are available; combination is not. This confirms
  Hestia's diagnosis by direct construction.
- XOR, ADD, ROTX: **EXPRESSIBILITY_SUPPORTED** and **PLANTED_COMPOSITION_SUPPORTED**: two causally necessary,
  designed substructures compose into a capability (3-input combination) neither has alone, and a three-stage
  chain is multi-step causally dependent.
- AND: EXPRESSIBILITY_SUPPORTED (C1-C3); planted composition fails by information loss.
- SPLICE: combination with state (C1) but no accumulation of successive inputs (C3 fails).

## World-demand check (minimal ladder, for the C4 task "output depends on a, b and c")
- Constant output: 0 inputs.
- Reflex / latest-input (REPLACE semantics): 1 input (the last writer).
- Short fixed history on one register: cannot hold three independent inputs under REPLACE.
- A direct-state lookup that reads one site: 1 input.
So the task requires the combination the gadget performs. Oracle: the closed-form OP-composition table, which the
gadget matches exactly.

## Cognitive accounting
- Substrate: the local op (one write, one combination) plus the frozen v1 contest/energy rules.
- Developmental machinery: none.
- Search: none.
- Experimenter: the arrangement, timing chains, input placement and activation-init per op.
- Certifier: function tables and ablation comparisons.
**Nothing here was discovered by the substrate.** It establishes what the physics can express when arranged by
hand.

## Qualifies R3
R3 may use XOR, ADD or ROTX. XOR is selected as the R3 primary: it is the simplest op that passed C0-C5. ROTX is
the alien-reserve arm.
