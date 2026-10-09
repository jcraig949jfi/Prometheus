# Ananke 72h science push PTE-C3 / C4 / C5: integrated synthesis

**Provenance**
- Authority: the operator order of 2026-10-07, roles/Ananke/prompts/2026-10-07_72h_c3_c4_c5/ (8c48ebfdf).
- START 2026-10-07T09:36:58Z; hard stop 2026-10-10T09:36:58Z.
- Seat: Ananke, instance m1-46797183, on M1 (RTX 5060 Ti) under Fabric lease lse-7d61e3584398.
- Branch ananke/p2b-2026-10-05.
- Every number below is from a frozen reducer, or labelled DESCRIPTIVE.
- No C1/C2A/C2B/C2BX/C2C artefact or verdict was modified. New machinery has new namespaces (c3/, c4/; C3_NS, C4_NS,
  C5T_NS).

**Per-campaign packets:**

| campaign | packet | prereg |
|---|---|---|
| C3S | c3/RESULT_PTE_C3S.md | 7f049f1ec |
| C3R | c3/RESULT_PTE_C3R.md (f2c8351af) | 5169f7c0c |
| C4: L / T / D | c4/RESULT_PTE_C4.md (ff0a5ee48, e4f930b94) | aba974cf1 / 6e1ea0b98 / 216f50b24 |
| C5T | c4/RESULT_PTE_C5T.md | a5a8a62e4 |

**The ladder under test (order s13):**

| rung | status |
|---|---|
| 1. carry one bit | crossed before this push: RELAY-mh, rare but reachable (C2BX: 16/32 by 16x) |
| 2. retain one bit | crossed: HOLD is found by search (C4-L: 16/23 competent), and C3S shows retention of graded function under M32 |
| 3. condition one process on another (GATE, FLIP) | **BLOCKS**: 0/144 C3R, 0/168 C4-T, 2/32 from DESIGNED parts only, C5T [PENDING] |
| 4. reuse machinery | blocks with rung 3: solved modules are taken up and stay live, but never compose |
| 5. manage competing informational processes | not tested (order s9: no C5 turbulence without composition) |

## SUPPORTED

- **S1. Selector resolution (C3S).** At M8, graded FLIP function (B about .6) is erased by selector noise. M32 keeps it
  (23/24 vs 8/24 retained; M effect +.55, sign p 1e-7, positive in 4/4 cells) and sometimes climbs it to competence.
  All 9 climbs are causal: teacher_off and zero_comm kill them, and S0 swaps read FLIP in 5/9.
- **S2. Composition is representable.** The GATE plant runs in R4, and search assembled two-stage GATE solutions from its
  two designed halves in 2/32 searches (C4-D). Both are assay-confirmed:
  - fresh worlds TRUE;
  - halves -> NOP, zero_comm and context_off each give FALSE;
  - a non-readout register zeroed gives FALSE;
  - they are re-wired, not copied (3 and 7 of 15 plant lines verbatim).
- **S3. One-stage machinery is searchable at FLIP-cell physics (C4-L).** RELAY1H 11/24 and HOLD 16/23 competent;
  every (cell, task) has at least 2. That is enough to freeze an 8-module library.

## FALSIFIED

- **F1. "FLIP is blocked because the genome is too small or lacks a free persistent register" (C3R).**
  - R1 (24 lines), R2 (third non-decaying register) and R5 (both): 0/24 each at 1x.
  - The kill criterion MINIMAL_REPRESENTATION_ROUTE_FAILED is met.
- **F2. "Block duplication-and-divergence opens FLIP" (C3R R3/R4).** 0/24 each at 4x (CP95 .142). No partial-B shift
  (max +.013 against a .05 bar).
- **F3. "Duplication or module reuse makes two-stage tasks reachable" (C4-T).**
  - GATE 0/32 and FLIP 0/24 in every arm. DUPLICATION_HELPS and REUSE_IMPROVES_COMPOSITION are absent.
  - Pooled over arms, a per-search rate above .038 (GATE) or .050 (FLIP) is excluded at 95%.

## NULL (and what each excludes)

- **C3R: NO_REPRESENTATION_EFFECT.** Excludes capacity, persistence, duplication and their combination as the FLIP
  barrier, from random starts, at M32, to 4x for R3/R4 (rate > .14 excluded) and to 1x for R1/R2/R5 (> .14 excluded).
  Lower rates and larger budgets are not excluded.
- **C4-T: NO_COMPOSITION** (both tasks, all arms). It excludes:
  - solved RELAY/HOLD modules inserted with uniform register renaming, at 36 generations, as a route to GATE/FLIP;
  - "the library was ignored": MODULE_PRESENT 56/56, MODULE_LIVE 55/56.
- **C5T: [PENDING]** (terminal assay: arm C at 4x, 56 fresh searches).

## INCONCLUSIVE

- **C4-D s8 diagnostic: INCONCLUSIVE_SPARSE (2/32, 2 cells, CP95 .008-.21).**
  - The frozen bars were >= 4 across >= 2 cells for REPRESENTABLE_BUT_UNSEARCHABLE and <= 1 for
    REPRESENTATION_STILL_INADEQUATE. 2 meets neither.
  - The descriptive contrast is designed parts 2/32 vs evolved modules 0/32, on identical seeds and gen-0 populations.
  - Composition is reachable from the RIGHT parts, rarely. The evolved one-stage parts are not the right ones.

## NEW MECHANISMS

- **N1. Re-wired designed-half GATE solutions (C4-D).** Two independent two-stage solutions in which renaming and
  mutation re-routed the plant's halves.
  - In FLIP-0099 D 02 the cue sits in S2 (swap FLIP), the solution needs S1, and zeroing S0 every tick does not hurt.
    The readout path does not keep a value in S0, unlike the plant.
  - This is a new implementation of a known function, not a new function (cf. Theseus #1953).
- **N2. Library take-over without function (C4-T arm C, DESCRIPTIVE).**
  - Inserted modules came to occupy 18-19 of 24 lines; 4-6 are live; only about 18% of slots still hold the module's
    instruction.
  - Selection keeps library material because it is cheap and neutral, then mutates it. The library dominates the
    genome without contributing function.
- **N3. Duplication flood (C3R, DESCRIPTIVE).** OPD fills 23/24 lines with copied material by 4x, without moving training
  accuracy. Copying events accumulate neutrally.

## NEW BLIND SPOTS

- **B1. "Module = solved one-stage champion" assumes the target needs the same sub-functions.** GATE needs a context
  latch fed by the actuator-sensed channel. The evolved HOLD module latches the cue channel after a gap. A library built
  from the wrong sub-tasks is present and live, and useless. The library stage chose its tasks (RELAY1H, HOLD) by
  designer judgement, not by decomposition of the target.
- **B2. Uniform register renaming is a combinatorial tax.** Correct assembly needs compatible permutations across two
  insertions (about 1/9 with 3 registers), on top of position. Nothing in the representation binds a module's outputs to
  another module's inputs.
- **B3. Lease does not exclude the operator's own GPU apps.**
  - ComfyUI ran on the leased GPU during C4-T and C5T.
  - The driver reset 5 times at 01:35Z and killed all workers.
  - Caught by the watch; relaunched once (ledger).

## SEARCH LIMITS

- **One-bit carriage (RELAY-mh)** is a RARITY limit. Time crosses it (C2BX: 2.3% -> 16/32 by 16x).
- **Two-stage composition (FLIP, GATE)** is a COMPOSITION limit. Neither time nor operators cross it:
  - FLIP: C2A BASE 0/48; C2B B4X 0/32 and STEP 0/24; C2C arms 0 (e.g. OP0_STEP 0/28; Hestia #1897 tallies 0/290 across
    C2); 0/144 (C3R); 0/24 at 4x (R3/R4); 0/72 in C4-T.
  - GATE: 0/96 in C4-T.
- Selection CAN keep and climb graded partial function once it exists (C3S at M32). It cannot create it from random
  starts.
- Search can sometimes assemble correct parts (C4-D 2/32). The limit is therefore not solely the representation. Part
  of it is finding or holding the right parts and binding them.

## REPRESENTATION LIMITS

- The flat 16/24-line register program can REPRESENT both two-stage tasks: the GATE plant, P_FLIP, and the C4-D
  re-wired solutions.
- No tested generic extension makes the parts individually valuable under the target ruler: capacity, persistent
  register, block duplication, module insertion with renaming. The parts are worthless alone (the module-alone check
  is 0/56 TRUE), so selection has no gradient toward assembling them.
- **Missing:** a binding primitive, i.e. typed ports or wiring between one module's output register and another's
  input. Renaming without binding is too weak.

## TRANSPLANTS

- **C4-T:** no competent arm-C champion exists, so transplant_c4.py had no donor.
- **C4-D (DESCRIPTIVE):** the designed halves acted as a transplant of correct parts into fresh populations: 2/32 versus
  0/32 for evolved parts on the same seeds.
- **Cross-substrate (other seats; information, not our evidence):**
  - Theseus #1953: planted parts inert, composition only via collision-generated k-ary couplings.
  - Aphrodite #1957: inherited library does not enable recursion; even oracle selection fails, so the limit is at
    candidacy/representation.
  - This is the same pattern on three substrates: inserted parts do not compose under selection.

## WHAT CHANGED OUR MODEL

1. **Before:** "FLIP is lost because the representation is too cramped." **After:** room, persistence and copying are
   not the barrier (C3R). The barrier is that two-stage parts have no individual value.
2. **Before:** C2's graded-stone collapse meant no climbable path near FLIP. **After:** it was mostly selector noise
   (C3S). Near a working mechanism there IS a gradient, if M is large enough.
3. **Before:** "reuse of solved machinery" might open composition. **After:** solved one-stage modules are adopted
   (present and live in every champion) but never compose (C4-T 0/168). Designed correct parts compose rarely (2/32).
   The open question has moved from "can the substrate represent composition?" (yes) to "how do the right parts come to
   exist, and how do they get bound?".
4. The barrier is rung 3 of the ladder: conditioning one process on another.

## WHAT SHOULD ANANKE DO NEXT

[C5T-dependent; finalised after RESULT_PTE_C5T.]

Candidates, in priority order. Each is one variable.
1. **Binding primitive.** Typed module ports (or a wiring field that connects one module's output register to another's
   input) instead of uniform renaming. Re-run the C4-D designed-halves test with binding. If 2/32 rises to a majority,
   binding was the search gap.
2. **Target-derived library.** Library sub-tasks chosen by decomposing the target's causal graph (context latch on the
   actuator channel; cue relay), not designer-chosen RELAY/HOLD. Test whether evolved parts of the RIGHT kind compose
   like the designed ones (C4-D rate).
3. **Lifetime plasticity (Hestia s4.4 THEN).** Use registers already present to learn the mapping within life. This
   attacks the "parts worthless alone" wall from the other side (Hinton-Nowlan).
4. **Frontier archive** keyed on the swap certificate, with a random-archive control (Hestia s4.4 NEXT).
5. **Preserve** the instruments:
   - packet-superposition physics;
   - exact replay and golden digests;
   - mirror-pair swaps (swap_v2);
   - P/R/V admission;
   - search-limit localisation;
   - GPU many-world evaluation.

## Q1-Q10

- **Q1.** Yes, largely. At M8 a B of about .6 is indistinguishable from noise, and lineages drift to chance. M32
  retains it in 43/47 searches and sometimes climbs to competence (C3S).
- **Q2.** No. 24 lines vs 16: 0/24 vs 0/24 (C3R R1 vs R0, 1x).
- **Q3.** No. A generic non-decaying third register: 0/24 (R2), 0/24 (R5) at 1x; 0/24 (R4) at 4x.
- **Q4.** No. Block duplication-and-divergence: 0/24 (R3), 0/24 (R4) at 4x. In C4-T, B vs A is 0 vs 0 for GATE and FLIP.
- **Q5.**
  - Evolved one-stage modules: no (C4-T arm C 0/56, modules present and live).
  - Designed correct halves: rarely (C4-D 2/32).
  - C5T at 4x: [PENDING].
- **Q6.** Where composition occurred (C4-D), the reused machinery IS causally necessary. Library lines -> NOP removes
  competence in 2/2, and the non-readout state registers are necessary.
- **Q7.** Not established. The 2 C4-D solutions are at 2 different cells, each with its own cell's halves. No
  cross-cell transfer test was possible without replicated competence.
- **Q8.** Not tested, by design. The order s9 condition (a reproducible composing mechanism) was not met, so turbulence
  did not run. Inability to survive turbulence is not interpreted.
- **Q9.** Not tested (same reason). No interference-management machinery could be assessed without composition.
- **Q10.** [C5T-dependent.]
  - If the C5T kill fires: demote PTE's flat evolutionary search architecture as a candidate route to richer cognition.
    Keep the substrate and the causal instruments (order s10). The next substrate work starts from a binding primitive
    or lifetime learning, not from more operators.
  - If C5T finds replicated composition at 4x: PTE continues, and the C5 turbulence question becomes runnable.
