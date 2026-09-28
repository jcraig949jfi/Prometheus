# Z80 affordance threshold -- design (v0)

Currency: 2026-09-28. Odysseus. Pure ASCII. Status: DESIGN, not a campaign. Read PRIOR_WORK.md first;
item labels K1-K9 and G1-G6 refer to it.

Question (operator s7): how much reproductive machinery has to be authored into the substrate before
Darwinian dynamics becomes reachable? Operationally: along an ordered ladder of removals, at which rung
does each of COPYING, HEREDITY, SELECTION, ADAPTATION, ACCUMULATION first become unreachable at a stated
budget, and which single restored gift brings it back?

## 1. Convenience (affordance) inventory

"Authored" = supplied by the designer, not produced by the organisms. Sources: vm.py / z8.py headers,
PRIOR_WORK K1-K8. (u) = not verified from source in this pass.

| # | affordance | BEE (prometheus/z80atlas) | NPE (Nestor z8) | Archaeon (archaeon/z80atlas) | Cicala 2026 (2607.09211) |
|---|---|---|---|---|---|
| A1 | block copy op | LDIR 0x15, 1 byte, C-counted; C=0 sweeps to budget | ED B0 / ED B8 (2 bytes); 1-byte alias in DENSE; absent in BYTEWISE | none | LDIR/LDDR (ED B0/B8, 2 bytes) |
| A2 | copy-and-advance op | LDI 0x14 | LDI-class (u) | COPY op 20: mem[C]=mem[B]; B++; C++ (gated by copy_prim) | LDI/LDD (LDD loops = the no-block route) |
| A3 | whole-genome copy op | COPYALL 0x16 (VM_COPY rep only) | no | no | no |
| A4 | generic byte move | LD A,(S) / LD (T),A / LD (S),A | LD (HL),n etc. (0x36 = the painter) | LD A,(r) / LD (r),A | full Z80 |
| A5 | stack / PUSH route | ABSENT | ABSENT (LD SP,nn loads nothing) | ABSENT | PRESENT: SP reset 0xFF = partner's last byte; Load-Push replicators come first |
| A6 | self-location | reset: all registers 0 each execution, own tape at 0 (S=0 is "me") | carried registers by default; SELF / GETPC ops as a factor; donors borrow zero HL | registers 0, own at 0; LD A,LEN gives own length | reset HL=BC=E=PC=0 (HL=0 is "me") |
| A7 | destination / partner address | fixed window [L,2L) | pair tape halves / ALLOC slot base in DE | fixed window at 128 | SP into partner; DE must be set |
| A8 | genome boundary | fixed tape [0,L), window [L,2L) | pair-tape halves, ALLOC buffers | [0,G); outside reads 0, refuses writes | 32-byte halves, split after run |
| A9 | reproduction API / birth rule | world registers a birth from window writes (viability: all L window bytes written) | ALLOC / BIRTH / SPLIT world ops + certification | SEAL op snapshots window; >= 90% window write rule | none: split(exec(AB)); implicit |
| A10 | execution budget | 256 steps | slice (e.g. 360) | step_cap | 512 |
| A11 | neutral undefined bytes | ~80% of byte values = NOP (the slide) | undefined = NOP | dense decode (ops 0, 30 NOP) | real Z80: nearly all defined |
| A12 | task / fitness | task coupling physics (v3); IMPLICIT task inert (GROUNDING s3) | tasks per grammar (u) | inputs/outputs, energy (u) | polynomial validation -> interaction prob 0.3 -> 1.0; metabolic cost |
| A13 | world mutation | per-tick byte mutation | mutation operators + copy_mut_rate | mutation operator (u) | 1/64 per epoch byte reinit |
| A14 | world-made copies | POLLINATION v1 (removed in v2), reservoirs | none (u) | none (u) | cross-niche pollination pi = 0.05 |
| A15 | address wrap | mod 256 sandbox | mod tape | outside refused | mod 2L |

Notes. A5 and A6 are the gifts every successful soup has and our VMs split: BEE/Archaeon keep A6 and
lack A5; NPE lacks both by default. A9 is where "fixed reproduction API" lives: NPE's is explicit
(opcodes), BEE's and Archaeon's are world rules, Cicala's is the split. Contiguity is assumed by every
detector in all four (A8 + detectors).

## 2. The removal ladder

Primary axis = MACHINERY (cumulative). Secondary axes crossed only where a property first dies.

| rung | world variant (what is removed) | why this order | BEE expression |
|---|---|---|---|
| L0 | all gifts (A1-A15 as BEE) | calibration; BEE density known (K2) | vm.execute ldir="on" |
| L1 | block copy made expensive (4 steps per byte) | a costed gift: does metabolic price act like removal? | ldir="cost4" |
| L2 | block copy removed | Cicala's one ablation; BEE P8 in-world 0/300 | ldir="off" (LDI stays) |
| L3 | copy-and-advance removed too: no op whose semantics encode copying | operator: "no instruction whose semantics directly encode replication" | variant: LDI decoded as NOP (pilot vmx) |
| L3s | L3 + stack route (PUSH/POP, SP reset into partner) | the route real Z80 uses first (K5); is a generic write-and-decrement a gift? | new op pair in a variant (not built) |
| L4 | L3/L3s + no reset self-location: registers carried or randomized per execution | K4: every soup supplies "I am at 0" | variant entry state (NPE X-P2-REGSTATE analogue) |
| L5 | + no genome boundary: one flat circular tape, random entry points; individuals identified post hoc by causal lineage | operator: "no designated genome boundaries" | new world (R2 V2) |
| L6 | + no reproduction API / birth rule: nothing is registered as a birth; descent is read only from write provenance | operator: "no fixed reproduction API" | new world observer only |
| L7 | + no externally supplied task, no privileged fitness: persistence only | operator; cross with L2/L3 FIRST (see below) | task off |
| L8 | + heredity not assumed contiguous: detector searches transmitted variants at any site, any transform (CVT-R) | operator: "eventually no assumption that heredity is contiguous bytes" | detector change, not world |

Crossings (not cumulative):
- TASK x {L2, L3, L3s}: Cicala's LDD route took over "only under task pressure" (K6), so task must be
  crossed with the first copy-less rungs, not left to L7. 2 x 3 cells.
- BUDGET x {L1, L3}: budget is itself an affordance (A10). A byte-move copier needs >= 4 steps per byte,
  so at L = 64 it is infeasible at 256 steps and feasible at 512 (pilot checks this). Budget {256, 512,
  1024}.
- RESTORATION at the first dead rung: add back ONE gift at a time (block op, LDI, PUSH, reset, boundary,
  birth rule, task) to name the minimal sufficient gift set. That set IS the threshold.
- ENGINE: rungs L0-L3 are expressible in all three VMs without engine edits except L3 in BEE
  (a vmx copy) -- NPE BLOCK/BYTEWISE factor, Archaeon copy_prim flag. L4 uses NPE's reset axis. L3s and
  L5-L6 need new substrates and are the expensive part.

## 3. Measures per rung (each property measured only if the lower one passed; copying at every rung)

COPYING (appearance)
- Replicator density by uniform sampling: N random tapes, op-agnostic functional detector (window
  pre-filled with random bytes; child fidelity >= 0.9 in 3 independent random windows). Exact binomial
  (Clopper-Pearson) CI. BEE's own-copy-op rule (probe.py run()) reported alongside for comparability;
  it cannot see byte-move copiers (LD (T),A is not in vm.COPY_OPS).
- Route-conditional importance estimator for densities below the sampling floor: enumerate the
  configurations C of a route's essential bytes (e.g. "LD T,64 at p ... LDIR at q>p"), plant a uniformly
  chosen configuration into random background, measure the functional pass fraction r, estimate
  density ~ |C| * 256^(-k) * r (union bound; overlaps negligible at these rates). Calibrated at L0
  against BASIN.json 3.0e-5. Reports log10 density per route per rung.
- Steps-to-first-copier by mutation random walk (Knierim baseline, K7): one uniform byte substitution
  per step, every step accepted, detector at every step; W walks, cap S steps; report hits, censored
  exponential MLE of the per-step hazard and its CI. Compare with 1/density: walk/sampling ratio > 1 means
  walks find copiers faster than independent draws.
HEREDITY (information)
- CVT-2 of Artemis (K3): per site, variants x^0x01, x^0x80, one random value; 3 random-window draws;
  generation 1 and 2; defined signature = same non-empty offspring difference in >= 2 of 3 draws;
  accepted variants must transmit in gen 1 and re-transmit in gen 2. Report TB2 = log2(1 + distinct
  classes) (max log2(193) = 7.6 bits for L = 64) and h2 = accepted variants / all variants.
  PAINTER = functional-detector pass with TB2 = 0. Homopolymer share reported as a diagnostic only.
SELECTION (in-world, only where heredity > 0)
- Fitness-heritability: parent-offspring regression of realised reproductive output (births per lineage
  per tick) and the Price covariance cov(w, z) for a heritable trait z (copy completion step, copier
  length); against a Bedau NEUTRAL SHADOW (same birth/death counts, parents drawn without regard to z).
  Selection = covariance outside the shadow's 95% band in >= 2/3 of >= 20 worlds.
- Establishment contrast: planted copier vs planted inert twin (copy byte NOPed) at equal initial count.
ADAPTATION
- Monoclonal worlds from each founder; evolved-vs-ancestor head-to-head competition (reciprocal
  invasion from 10%) with relative fitness > 1 beyond the shadow; the trait that changed is named by
  knock-in into the ancestor (mutation sufficient) and knock-out from the evolved (necessary).
ACCUMULATION
- ACCUMULATION_v0 R0-R6 with its controls (history-ablated twin, deletion, permutation, recompute arm,
  producer destroyed). Candidate objects: cargo routines behind the copier; a second copy route or a
  repair routine. Only at rungs that pass adaptation.

## 4. Predictions (to be wrong about)

P1 density: L0 ~3e-5 (known); L1 ~0.3-0.5 x L0 at budget 256 (only copiers whose LDIR starts by ~step 26
   still finish: 4 steps per byte); L2 1e-10 to 1e-8 (LDI plus a back-jump inside a <= 3-step loop, ~5
   essential bytes); L3 exactly 0 at budget 256 for L = 64 (>= 4 steps per byte, >= 256 + setup), and
   <= 1e-15 at 512 (>= 8 essential bytes). Slope: roughly one decade per extra essential byte-pair
   beyond what the NOP slide absorbs -- a Adami-LaBar exponential in essential information.
P2 heredity: every functional copier at L0-L2 carries TB2 >= 5 bits; below L2 functional passes are
   painters (TB2 = 0), as NPE BYTEWISE and the P-11 naturals.
P3 stack: L3s restores density to within 100x of L0 (PUSH copies 2 bytes per step: a Load-Push loop
   is short and fast).
P4 reset: removing reset self-location costs >= 2 more essential bytes (LD S,0), i.e. ~1e-4-1e-5 x
   density at L0, and more at L2.
P5 selection and adaptation appear wherever heredity > 0 in-world; task pressure is needed for
   takeover by the slower copy route (Cicala), not for appearance.
P6 accumulation stalls at R2/R3 at every rung, including L0.

## 5. Kill criteria and decision rules

- K-DET: planted copiers not detected (pass < 0.9 at a clean placement) or a planted painter receives
  TB2 > 0 -> detector invalid; stop.
- K-EST: importance estimate at L0 outside [1e-5, 1e-4] (BASIN 3.0e-5, CI 0.6e-5-5.4e-5, widened 2x)
  -> estimator not calibrated; report sampling bounds only.
- K-FRAME: L2 density >= 1e-6 (within sampling reach) -> "the block op is the BEE threshold" is false;
  move the threshold question to L3.
- K-NOVELTY: if L0-L3s results only reproduce Cicala (block op dispensable given PUSH + reset + task),
  stop after L4 and write it as a cross-ISA replication; the rest of the ladder is not worth its cost
  unless L4 or L5 breaks something Cicala keeps.
- THRESHOLD READINGS: (a) a property survives every removal -> no authored reproductive machinery is
  needed in this substrate beyond generic writes (headline, and against K1); (b) the first dead rung
  plus the single restored gift that revives it = the affordance threshold for that property;
  (c) copying survives but heredity bits = 0 (painters) -> "copying without heredity" boundary, the
  NPE BYTEWISE pattern, generalised.

## 6. Why this is not Cicala 2026 and not Nestor npe-p2

- Cicala: one ablation (block copy) in one world keeping stack, reset registers, boundaries, split,
  task; byte-pattern detector; no density or walk numbers. Here: an ordered ladder with the same causal
  detector and heredity bits at every rung; sub-floor densities; walk baselines; removals of the
  ENVIRONMENT gifts Cicala keeps (reset self-location A6, boundary A8, birth rule A9); stack treated as
  a removable gift, not background.
- Nestor npe-p2: NPE-internal acquisition and establishment, fixed ISA, carried-state physics, the
  endogenization of scaffolding. Here: ISA-level, cross-engine, comparative; NPE's reset finding enters
  as rung L4 and is tested in BEE/Archaeon; no NPE campaign is run. Hand-off: L4 cross-engine result to
  Nestor; L0-L2 in-world questions (task x route) to Bellerophon.
- Honest limit (FR-010): the three VMs share one design ancestor (the directive paraphrases Cicala), so
  cross-engine agreement is an implementation check; the ladder's value is the within-VM ISA contrast.

## 7. Cost sketch

L0-L3 densities, estimator, walks, CVT: laptop-hours (the pilot below does a first pass in < 40 min).
L3s, L4: a VM variant each, ~1 day build + CPU-hours. Selection/adaptation at L0-L2: world runs
(Bellerophon-class, CPU-days). L5-L6: a new flat-tape world and a provenance observer (days-weeks).
L8: detector work only.
