# NPE competing theories: mechanistic accounts of what the pair-tape world is doing (revision 2)

Nestor's inference harvest, 2026-09-30.

**Inputs:**
- dossiers A–G;
- two independent adversaries: ADV1 (deflationary) and ADV2 (ontology);
- two static forensics: FOR (functional core) and S1 (map predicts outcomes);
- Nestor's checks, coded U-xx in NPE_UNMINED_EVIDENCE.md;
- a red-team review of revision 1 (RT), whose corrections are applied here.

Nestor's pre-adversary draft is frozen at `drafts/THEORIES_DRAFT_NESTOR.md`. §9 records what changed and why.

The seven theories are **mutually distinguishable**: each makes at least one prediction another contradicts. Some predict the
same headline outcome. They are kept separate because they disagree about mechanism, and the mechanism decides what the next
experiment should be. Where two theories predict the same thing, this document says so. It does not manufacture opposition.

**Notation.**
- **Φ:** the single-interaction pair map.
- **W:** the world's write-back rule (BASE or ATOMIC).
- **Family:** the contents descended by content ancestry.
- **Occupancy:** the share of sites held by a family.

---

## T1. Reachability: mutational supply × exposure (the search theory)

**Mechanism.** Each NPE transition is a first-passage event in genotype space. Its rate is the density of functional
genotypes within reach, times the number of trials (occupied sites × copy events × effective mutation supply). Selection
decides what persists, not what appears.

**Explains.**
- **Acquisition as a base rate.** Random dense genomes are competent at about 2e-4 (3 hits; CI 4e-5 to 6e-4). That is
  consistent in order of magnitude with dense acquisition: 5% vs 7.3% at the first checkpoint, 66% vs about 55% over a run
  (FOR, corrected).
  - PLANT (32/96) and SHAM (0/96) are the same arithmetic.
- **Internalization appears only after takeover (8/8).** Takeover is what supplies trials.
- **Detection rises with population size.** P(a state-free genome is seen at a checkpoint) rises with the number of
  competent genomes: 0.08, 0.25, 0.71, 0.67, 0.78 across the bins, so it is not monotone (U-C2).
- **Within-run drift toward state-freedom** (FOR Q5).
- **The ffa6/7ae3 difference is consistent with the supply difference.** The hazard ratio is about 8x against a supply ratio
  of about 7x, but the 95% CI on the ratio is about 1.1x–370x (n = 1 event in 7ae3) (U-T5).

**Struggles with.**
- **Why walks stop where they do.** The 16000006 walk (multi-step; single knock-ins 0/5) ended at `LD DE,3200`, and T1
  offers no reason.
- **ffa6 27000053.** It took over with 409k exposure and produced 0 events, which has P ≈ 0.055 under T1's own ffa6 hazard.
- **The 7ae3 event is 91% execution-computed (MKL) bytes and ≤ 6% mutation-made.** The OPERAND operator's count is therefore
  not obviously the supply for it (RT M1).

**Unique prediction.** The appearance hazard per copy event is invariant across payoff regimes. State-free variants appear even
when state-freedom earns nothing, which requires a true reset-every-interaction world. Payoff moves only the sweep.

**Decisive falsifier.** Measured by genealogy, not first detection, the appearance hazard per copy event is far lower in a
reset-every-interaction world than under VICTIM registers. That would mean appearance is driven by demand.

**Existing test.** None in NPE. BEE's ZERO arm (18/100 state-free events, transient) is suggestive, but it is a different
engine (D:F 5.2).

**Missing data.**
- a true no-payoff arm;
- copy-event counts per checkpoint;
- genealogy-based appearance events;
- a mutation-operator swap with an adequate event count (see E3's eligibility problem).

---

## T2. Scaffold tracking: the world defines reproduction (the ecological theory)

**Mechanism.** The world supplies most of what "reproduction" means:
- placement at offset 0;
- HL = 0 as the address;
- a long count;
- the 64/128 geometry;
- the pairing schedule;
- write-back;
- the newborn's registers, which are the victim site's leftovers (`world.py:812/877`, U-W7).

A family takes over those supplied functions that the world provides unreliably, and never those it provides reliably.

**Explains.**
- **Zero-specialization is HL = 0 geometry** (C-ZERO-SPECIFIC 26/48 vs 2/48). It tracks the world supplied (X-A3-FAIR).
- **Self-location is never internalized:**
  - 280/280 SELF-free copiers are tape-anchored;
  - only 2 of 332 are locators.
- **The address source is internalized.** State-free copiers take their address from constants, not entry registers (27% vs
  56% world-dependent; FOR Q2).
- **Self-poisoning is the copier's own pointer advance destroying the supplied address.** Carried E/L reproduces it on 32/44
  sides, and robust donors reload their pointers (S1).
- **The cell axis.** The single-interaction map cannot see it: observed CARRY is 0.16 (C7) vs 0.36 (CF). The ecological
  differences between cells (mutation, migration) matter (S1).
- **World rules decide outcomes:**
  - the energy "wall" is an asymmetry between birth paths (U-F4);
  - the splice matters;
  - so does the write-back rule.

**Struggles with.**
- **The wait.** Why internalization waits for takeover when the entry noise exists from epoch 0. T2 needs T1's supply term.
- **Transience.** Under steady demand T2 predicts persistence, yet 4/8 events are gone by epoch 2000.

**Unique prediction.** When only the demand is changed (the newborn-register rule), the *sweep* is ordered by how
uninformative the newborn's entry state is: RANDOM ≥ VICTIM > DONOR > per-interaction-reset ≈ no payoff. When placement is
made unreliable (tape rotation), either locators internalize, if they are reachable, or reproduction collapses.

T1 predicts the same sweep ordering. **T2 and T1 separate only on appearance**: T2 expects appearance to track demand, T1
expects it to track supply (RT B5).

**Decisive falsifier.** State-freedom sweeps as far under a per-interaction reset (no payoff) as under VICTIM registers.

**Existing test.** Indirect only. X-A3-WITHDRAW's CONTROL_ZERO keeps a standing 10–33% robust fraction that never sweeps,
while ABRUPT sweeps to 0.96 within 100 epochs (U-C5).

**Missing data.**
- the newborn-register factorial with a true reset arm;
- tape rotation (WP-7).

---

## T3. Compact copy setup: the representation does the work (the representation theory)

**Mechanism.** The instruction set supplies a half-duplicator. A competent genome is that instruction plus a short chain
computing its operands modulo 128.

**Evidence (FOR):**
- The knockout **collapse set has a median of 8 bytes** (IQR 6–10), about 5 beyond the last-setter motif, and the chain is
  mostly incidental.
- State-free genomes have the same collapse size, 8 vs 8. They differ in *where the address comes from* (constants) and in
  copying from side 0.
- 128/128 sampled genomes are copiers; 0 are painters.
- All BYTEWISE P-11 survivors are near-homopolymers (U-X5).

**Explains.**
- Copy_primitive's 5x effect on P-11.
- Dense encoding.
- Core composition.
- Function conserved while bytes regenerate: any chain yielding the right operands will do, and copy direction is neutral.
- **The phase arithmetic of self-poisoning.** It follows from LDIR semantics (count mod 128), so T3 predicts the same
  non-monotone budget pattern as T6 (RT M8).

**Struggles with.**
- **The 16000006 walk.** Single knock-ins do not confer robustness, and the adapted graft succeeds in only 1/12. Something
  in the background mattered.
- **Per-donor outcome differences need more than the setup.** The failure of the one-generation map and the success of the
  post-hoc two-generation map (S1) show that whether *the copies* can copy matters. That is a closure property, not a bare
  "compact instruction" property.

**Unique prediction.** Genomes matched on their full (two-generation) map perform the same in-world, whether evolved or
synthetic, and whether passengers are intact or scrambled with random bytes. Scrambling outside the *state-free* knockout
set costs nothing.

**Decisive falsifier.** Evolved genomes beat map-matched synthetic genomes or their own scrambles, in their home population,
by a frozen margin.

**Existing test.** The static half is done and supports T3 for single-site dependence. Single knockouts cannot see multi-site
dependence. The in-world half has never been run.

**Missing data.**
- the reconstitution test E1 (revision 2);
- a pairwise-knockout map;
- a register-free copy-op control (E8).

---

## T4. Reproductive organization: a self-maintaining lineage process (the program's former default)

**Mechanism.** The hereditary unit is a lineage process, not a byte string. It:
- regenerates its own material;
- keeps function while material turns over;
- maintains a core;
- reorganizes its reproductive setup by distributed, multi-site change when the scaffold becomes unreliable.

On this view, organization is carried and rebuilt by the family's own activity, and parts of it may be kin- or
population-context dependent.

**Explains.**
- The 16000006 walk (the strongest single residue; ADV1 R1–R2).
- Material turnover with function conserved.
- CVT-R transmission of organism-authored setup variation (83/100; 8/8).
- The primitive regenerated in foreign cells.

**Status: unsupported and untested. It is not contradicted (RT M3).**
- None of T4's distinctive predictions has been measured:
  - (a) kin- or home-context benefit;
  - (b) heritability of the *mechanism* across independent origins;
  - (c) multi-site epistasis beyond the single-knockout core.
- The grounds revision 1 gave for demoting T4 were mostly void:
  - the 1.009 enrichment ratio is near-automatic when L's share is bistable;
  - the Galton-Watson match was measured on the unevolved founder;
  - the 8-byte core comes from single knockouts;
  - "generic internalization" depends on unassayed founders (U-C2).
- **What does legitimately remove T4 as the *default*:**
  - burden symmetry (memory `verdict_mapping_burden_symmetry`): support needs a certificate, and T4 has none beyond one
    exploratory lineage;
  - everything else in the record is accounted for by T1/T2/T3/T6/T7 without it.

**Unique predictions.**
- (a) Evolved genomes outperform their map-matched synthetic twins and their own random-byte scrambles **in their home
  population**, but not in a naive one.
- (b) State-freedom from independent origins in different runs shares a mechanism that is transmitted as a unit (CVT-R /
  Jacobian), rather than converging on different constant-loading solutions.
- (c) Pairwise knockouts reveal dependence that single knockouts miss.

**Decisive falsifier.** Two findings together would falsify it:
- E1 (revision 2) finds no home-population advantage, with a ruler shown able to register one;
- pairwise knockouts find no epistasis beyond single-knockout predictions.

**Missing data.**
- a home-population reconstitution arm;
- a pairwise knockout map;
- a mechanism comparison across independent origins (E4 revision 2).

---

## T5. Executable machinery: reproduction partly performed by whoever reaches the code (the execution-field theory)

**Mechanism.** On the pair tape, code is data and data is code. pc crosses the half boundary, so a copy routine can be executed
by a context other than its owner.

**Verified case (U-W1).**
- 7ae3 is a SELF-using copier in a SELF-enabled cell. With 7ae3 at side 0, it is overwritten by the partner's content in
  200/400 random pairings.
- The overwrite happens in 0/400 once its SELF+LDIR bytes are zeroed.
- The partner's context authored 12,485 of 12,549 changed bytes.
- The overwrite falls to 1/400 when the partner is confined to its own half.
- Artemis previously reported the execution-order (side-1) hijack.

**Scope (RT M2, B1).** In the 24 corpus copiers tested (typical, SELF-free), partner-like overwrites of their half do occur,
and depend on their own copy byte. The changed bytes are mostly written by **the copier's own context**:
- 17,203 own vs 13,391 partner (state-free, side 1);
- 10,277 own vs 648 partner (not state-free, side 0).

For typical copiers the dominant mode is therefore **wrong-side self-import**, and partner execution is the minority. In the
foreign cells 9cba and e160 the SELF hijack cannot operate, because their ops masks exclude SELF: the single-interaction rate
is ≤ 1.5%. The foreign-cell victim magnet (100/240 vs 0/240) is **unexplained**.

**Explains.**
- Founder loss at side 0 in SELF-enabled cells: part of the 28% in X-TICKET.
- Why every copier is single-sided (U-W2).
- The attribution errors in the record: FF-31, AN8 candidates, founder-less runaways (candidates, untested).

**Struggles with.**
- **Frequency dependence.** No frequency dependence of erosion is visible up to 15 members (U-W5).
- **Internalization.** T5 says nothing about it.

**Unique prediction.** If pc may not cross into the partner's half (writes allowed):
- hijack births vanish;
- the founder's epoch-1 loss drops, in SELF-enabled cells;
- the winning genomes change beyond what a recomputed Φ predicts.

**Decisive falsifier.**
- An EXEC-motif audit of recorded births finds partner execution in < 5% of founder overwrites and births.
- Containment changes outcomes only by what the recomputed Φ predicts.

**Missing data.**
- the EXEC-motif audit (S2, static);
- an execution-containment world rule.

---

## T6. First principles: a stochastic rewrite field (stated without program vocabulary)

**Mechanism** (ADV2 §2).
- The system is a fixed set of 256 **sites**. Each holds a **content** (a 64-symbol string) and a **context** (a small state
  that stays with the site; only 7 bits of each pointer are observable on a 128-cell ring).
- Each step, a random matching pairs the sites.
- For each pair, a deterministic-plus-noise map Φ rewrites both contents and both contexts.
- A post-processing rule W then decides what each site keeps.
- A content spreads across sites to the degree that it:
  - (i) turns partner contents into copies of itself over a large share of partner contents and contexts (κ);
  - (ii) keeps its own site (ρ);
  - (iii) leaves copies that themselves do (i)–(ii) (the two-step closure the S1 repair found necessary);
  - (iv) restores, through its own action, a context in which it still works (context closure).
- The field has two kinds of stable configuration: a mixed configuration in which no content has growth rate above one, and
  single-content-class configurations.
- Changes of which class holds the field are rare transitions between them.

**Explains, in these terms.**
- **Which strings end up holding the field.** It is roughly predictable from pair statistics once (iii) is included:
  post-hoc ρ = 0.81–0.86. From one-step statistics alone the prediction is only coarse (S1).
- **Why outcomes are all-or-none.** There is no stable configuration between "absent" and "holding the field".
- **Why names attached to sites drift away from the strings they were first attached to.** A threshold rule moves the names,
  while Φ, residue and noise rewrite the strings (U-I6).
- **Why a string's usefulness decays across its own consecutive steps.** Its action moves its own context, and strings that
  rewrite their own context back persist (S1).
- **Why padding with a constant symbol inflates apparent copying.**

**Struggles with.**
- **Which class wins when several are present.**
- **Frequency dependence before a class holds the field.**
- **The cell differences Φ cannot see** (CARRY 0.16 vs 0.36).
- **Why a particular multi-step path was taken** (16000006).

**Unique prediction.** Holding-the-field outcomes are predicted by pair statistics computed string by string, including (iii),
with no history. Once (iii) is included, the prediction transfers to strings not used to build it.

**Decisive falsifier.** The two-step pair statistics fail on an independent string panel.

**Existing test (S1b, static, criterion frozen before computing): PASS, qualified.**
- The donor's own causal offspring law over a horizon predicts first-donor fate for 43 W1 first donors out of sample: AUC 0.89,
  ρ 0.71, permutation p 5e-5.
- The content is essentially "does it copy from its carried state". The simplest statistics do best, and W1's self-poisoning
  measurements do as well.
- So T6 holds at the first-donor stage. Post-takeover prediction is untested.

**Missing data.**
- a panel beyond W1;
- occupancy trajectories (E9);
- partner-conditioned statistics after takeover.

---

## T7. Demography: finite-population birth–death with a world-set offspring law (the deflationary quantitative theory)

**Mechanism.** The quantitative regularities are properties of a branching process in a finite population of 256, read at a
fixed horizon:
- the early fate;
- independent founders;
- the depth gap;
- the horizon effect;
- transient events.

**Explains.**
- X-DOSE-CURVE independence at the runaway endpoint (LRT p = 0.42; 0.70 pooled).
- Win given size: 7/9 at ≥ 8 members, 5/5 at ≥ 16.
- The horizon effect (U-T6).
- The depth gap, as extinction vs saturation.
- The splice as an offspring-mean reducer that cuts the tail only.

**Struggles with.**
- **The k = 4 excess at depth ≥ 5.** p = 0.0013 against pooled p1, although the joint LRT p = 0.108.
- **The BASE miss.** The map's zero-context BASE P_est is 0.26, against 0.03 observed: T7 needs content sterility (erosion)
  that a plain offspring law does not contain.

**Unique prediction.** The same demographic signatures appear with a register-free supplied copy op (E8):
- independent tickets;
- the depth gap;
- BASE ≪ ATOMIC;
- splice tail suppression.

**Decisive falsifier.** Those signatures change qualitatively with such an op, beyond its own offspring law.

**Missing data.** The SELFCOPY control world.

---

## 8. Collision table

Cells read "untested" where no test bears on the theory. Revision 1 marked some of these as contradictions (RT M3).

| observation | T1 reach | T2 scaffold | T3 setup | T4 organization | T5 execution | T6 field | T7 demography |
|---|---|---|---|---|---|---|---|
| dense acquisition ≈ base rate (order of magnitude) | predicts | neutral | predicts | neutral | neutral | predicts | neutral |
| state-freedom after takeover (8/8) | exposure | needs T1 | neutral | lineage process | neutral | context set becomes family-set | neutral |
| ffa6 > 7ae3 (≈ 8x, CI ≈ 1–370x) | consistent (supply ≈ 7x) | cell ecology | neutral | neutral | neutral | neutral | neutral |
| state-free in 25/29 large compartments; non-D0 founders unassayed | consistent | consistent | consistent | untested (acquired vs founding unknown) | neutral | consistent | neutral |
| collapse core ≈ 8 bytes; state-free no larger (single KO) | neutral | predicts | predicts | untested (multi-site) | neutral | predicts | neutral |
| 16000006 multi-step walk | allows | allows | strained | predicts | neutral | allows | neutral |
| one-step map: coarse pattern yes, within-ZERO no; two-step map ρ 0.81 (post hoc) | neutral | neutral | strained (closure matters) | untested (unevolved donors) | neutral | predicts (with iii) | consistent |
| side-0 hijack of 7ae3 (SELF cells) | neutral | neutral | neutral | neutral | predicts | predicts (Φ contains it) | absorbs |
| foreign-cell victim magnet (no SELF) | neutral | neutral | neutral | neutral | **not explained** | not explained | not explained |
| depth gap 22–161 | neutral | neutral | neutral | takeoff | neutral | extinction vs holding | predicts |
| transience (4/8) | appearance without payoff | strained | neutral | strained | neutral | weak closure advantage | drift balance |
| self-poisoning 12/12 vs 3/29; robust donors reload pointers | neutral | predicts (supplied address destroyed) | predicts (LDIR semantics) | neutral | neutral | predicts (context closure) | neutral |
| cell axis invisible to the map (0.16 vs 0.36) | predicts (mutation/migration) | predicts | neutral | neutral | neutral | fails | partly |

---

## 9. How the adversaries and the red-team changed Nestor's draft

1. **T4 was removed as the default on burden grounds, not on contradiction.** Revision 1 overstated the grounds (RT M3).
   Burden symmetry is the legitimate reason: T4 has one exploratory residue, and its distinctive predictions are untested.
2. **T5 is new and scoped.** It came from ADV2's hijack probe, which Nestor verified with independent code. The RT then
   narrowed it: typical SELF-free copiers mostly self-import, and the hijack cannot explain the foreign-cell magnet.
   Kin-pairing (Allee) is a secondary idea, and U-W5 shows no effect up to 15 members.
3. **T6 was sharpened** into ADV2's site/content/context ontology. S1 then added the two-step closure term (iii), which the
   one-step map lacked. The T6 statement is now written without program vocabulary (RT m13).
4. **T7 was split off from T1** (ADV1). It needs erosion (content sterility) to explain the BASE miss (RT B7).
5. **T2 gained the newborn-register mechanism** (U-W7). T1 and T2 separate only on appearance, not on sweep (RT B5).
6. **T3 was strengthened by FOR and corrected by FOR.** NOP-padded `1E 40 E5` passes partly by zero-painting. The honest
   minimal copiers are 6 exact 3-byte strings. Competent genomes are 50–70x more common than the reachable-motif prior. T3
   is also strained by S1: whether copies can copy matters.
7. **Where Nestor departs from ADV1:** the 1.009 enrichment ratio is uninformative. It is not evidence of label independence.
8. **Where Nestor departs from ADV2:** ATOMIC makes the *label* individuality valid by construction. Material regeneration
   under ATOMIC is still real, and it is expected under T6 as well.
