# NPE decisive experiments: designs that separate the competing theories

**Inference harvest, 2026-09-30 (Nestor).** These are designs only. **Nothing here is authorized or started.**
- Execution needs an Aporia dispatch under CWO-C s7, and operator authority for anything beyond the MWO-0004 R2 envelope
  (≤ 16 CPU core-h per item).
- Theories T1–T7 are defined in NPE_COMPETING_THEORIES.md. Evidence codes (U-xx) refer to NPE_UNMINED_EVIDENCE.md.
- Every design below is prereg-ready in content. Before exposure, each still needs:
  - a frozen PREREG.md with a commit hash;
  - an instrument self-test (a fail-on-old / pass-on-new check);
  - a planted positive shown to reach PASS on real data (Harmonia F8; Bellerophon #1113);
  - an eligibility count (memory `preregistered_rules_need_an_eligibility_count`).

## How the designs are ranked (by information, not by a score)

The ordering follows three properties, in this order:
1. How many theory pairs a design separates **with opposite predictions**, not merely different effect sizes.
2. Whether it runs on **static computation or replays** instead of new populations.
3. Whether its result **changes which rulers every later experiment should use**, and so changes the meaning of all later
   work.

| tier | design | separates (opposite predictions) | cost class |
|---|---|---|---|
| **0: static, do first** | S1 map atlas vs recorded per-donor outcomes | T6 against T4 (lineage-level residuals) | minutes; running now (FORENSIC_MAP_PREDICTS_OUTCOMES) |
| 0 | S2 EXEC-motif audit of recorded births | T5 against T6/T7 | minutes to 1 h, no runs |
| 0 | S3 phase orbits on real donors | T6 against T2 | minutes, no runs |
| **1: replays of existing seeds** | **E4 GENEALOGY** | **T4 against T1/T7** | about 6 core-h |
| 1 | E9 cb7f occupancy replay | ruler validity: depth vs occupancy (T6) | about 1 core-h |
| **2: small new populations** | **E1 RECONSTITUTION (the aggressive one)** | **T4 against T3/T6/T7; T5 as a side channel** | about 16 core-h (R2) |
| 2 | E2 NEWBORN-REGISTER factorial (with the ZERO no-payoff null) | T2 against T1 against T4 | about 20 core-h (split into 2 items) |
| 2 | E6 PHASE dose (slice budget) | T6 against everything else | about 10 core-h |
| 3: world rules / bigger | E5 EXECUTION CONTAINMENT | T5 against T6/T7 | about 16 core-h |
| 3 | E3 OPERATOR SWAP | T1 (quantitative) against cell ecology | about 16 core-h |
| 3 | E8 SELFCOPY register-free control | T7 against T3/T4 | about 20 core-h |
| 4: expensive / likely floor | E10 TAPE ROTATION (WP-7) | T2 against T1/T3 on placement | about 16+ core-h |

**The most discriminating next experiment is E1 run together with S1.** Each genome's single-interaction map yields a
preregistered, quantitative prediction for that genome. Evolved genomes are then placed beside synthetic genomes built to
match those predictions, and beside scrambled versions of themselves.

- **If evolved genomes do no better than their own map predicts, and no better than their synthetic twins:** the "endogenous
  reproductive organization" reading reduces to "a compact copy setup, evolving under selection, in a world that supplies
  the rest". A broad sweep can never settle that.
- **If they beat their predictions:** there is lineage-level organization, and it is located by the residual.

E4 is the cheapest decisive test of the one T4 prediction still standing (monophyletic, inherited organization versus
recurrent de novo origin). It runs on replays of existing seeds.

---

## E1. RECONSTITUTION: is there reproductive organization beyond a compact copy setup? (aggressive)

- **Exact question.** Do evolved state-free genomes carry reproductive properties (establishment, persistence, competitive
  occupancy) beyond:
  - (a) what their own single-interaction map predicts, and
  - (b) what κ-matched synthetic minimal copiers achieve?
- **Treatments.** One cell (ffa6), dense VM, ATOMIC runner, VICTIM newborn registers (the current world), random background
  population, founder implanted at k = 4.
  - **EVO:** 8 evolved state-free genomes. Draw them from FOR's 48 state-free genomes: the 8 epoch-700 16000006 modal
    genomes plus corpus late genomes, stratified by origin run.
  - **SCR:** the same 8 genomes with every byte outside the FOR necessary set replaced by **random** bytes, 2 independent
    scrambles each. Random, not NOP: NOP padding inflates competence (FOR Q3; ADV2 D8).
  - **SYN:** 4 synthetic state-free minimal copiers with explicit L/E constants and random padding (e.g. `LD L,0 ; LD E,40 ;
    E5`, and an LDDR variant), chosen so their computed κ over the full phase grid spans the EVO range.
  - **HEAD:** EVO vs its own SCR at equal frequency (k = 8 each), 8 pairs.
- **Frozen per-genome predictions, computed before any run (S1 method):**
  - κ over the full 128×128 phase grid;
  - retention ρ;
  - offspring law m and GW P_est under ATOMIC with VICTIM contexts;
  - closure index.
- **Experimental unit.** A run (genome, seed). Analysis is hierarchical, with the genome as a random effect.
- **Ruler.** Content-family occupancy O_F(t): the share of sites whose content is ≥ 0.9 identical to the implant on
  **transmitted positions** (FOR/ADV2), with aligned identity. Readouts:
  - establishment: O_F ≥ 0.5 by epoch 500;
  - persistence: O_F ≥ 0.5 at epoch 1,000;
  - for HEAD, the final occupancy share of EVO vs SCR.
  - Depth is reported, never used for the decision. CVT-R on endpoint genomes is reported too.
- **Positive control.**
  - A zero-dependent synthetic (`LD E,40 ; E5`, random padding) in a ZERO-register world must establish within ±0.15 of
    its computed P_est.
  - 7ae3 under ATOMIC must reproduce its 0.52 (U-S1).
- **Negative / null controls.**
  - A random-genome implant must give 0 establishment.
  - A 0x36 painter with random padding must not register as occupancy (transmitted-position identity).
  - A sham arm with the implant's labels but random content.
- **Confounds and handling.**
  - Donor heterogeneity (D U4): random effects, and a stratified draw.
  - Padding inflation: random passengers only.
  - Side asymmetry (U-W2): randomized sides, reported per side.
  - Hijack exposure (T5): record EXEC motifs.
- **Expected outcomes per theory.**
  - **T3, T6, T7:** observed establishment ≈ P_est for every class; the EVO − P_est residual ≈ the SYN − P_est residual ≈ 0;
    HEAD shares near 0.5 (or as the map predicts).
  - **T4:** EVO residual > 0; EVO beats SCR head-to-head (share ≥ 0.65); EVO beats SYN even at matched P_est.
  - **T5:** differences track hijack exposure (EXEC ≠ owner rates), not organization.
- **Kill criteria (frozen):**
  - **T4 (organization) is dead** if all three hold:
    - the mean EVO residual is ≤ the SYN residual + 0.10 (95% CI);
    - the HEAD EVO share is < 0.60;
    - SCR establishes within 0.10 of EVO.
  - **T3/T6 are dead** if EVO beats its prediction by ≥ 0.15 in ≥ 5 of 8 genomes, *and* beats SCR head-to-head (≥ 0.65) in
    ≥ 5 of 8.
- **Smallest useful sample.**
  - 8 EVO + 16 SCR + 4 SYN genomes × 8 seeds × 500 epochs = 224 runs, plus HEAD 8 × 8 = 64 runs.
  - Timing: about 1085 CPU-s per 2000 epochs means about 4.5 CPU-min per 500-epoch run, so about 21 core-h. The stock-VM
    figure is lower.
  - To fit R2, split into E1a (EVO/SCR/SYN establishment, about 16 core-h) and E1b (HEAD, about 5 core-h).
- **Why this beats a broad sweep.** A sweep samples outcomes. E1 tests a mechanism against a **preregistered quantitative
  prediction made for each genome**, so every run yields a residual, not just a count. It is the only design here that
  separates "has a compact copy setup" from "has reproductive organization" in the world itself, not only in a static
  knockout.

---

## E2. NEWBORN-REGISTER FACTORIAL, with the ZERO no-payoff null

- **Exact question.** Is state-free internalization an adaptive response to the world scrambling newborn entry state (T2)?
  A mutational by-product that appears at a supply-set rate (T1)? Or a lineage-specific process (T4)?
- **Treatments.** The C-A3 design, frozen as-is: random populations, dense VM, ATOMIC, ffa6, 2000 epochs. Only the rule for
  the newborn's registers on an accepted overwrite changes:
  - **VICTIM:** the current rule;
  - **ZERO:** always-scaffolded, so there is no payoff for state-freedom;
  - **RANDOM-PER-BIRTH:** maximal noise;
  - **DONOR:** a copy of the donor's post-execution registers. Optional; fourth arm only if budget allows.
- **Instrument additions.** Copy-event counts per checkpoint, so exposure can be measured in copy events (T1's supply term).
  State-free share is measured by the FOR STATE_FREE assay with random passengers, and also by the closure index.
- **Experimental unit.** A run. 24 seeds per arm.
- **Ruler.**
  - (a) Appearance hazard: first state-free genome per 10^5 copy events.
  - (b) Sweep: state-free share among competent genomes at 1,000 and 2,000.
  - (c) Persistence: present at 2,000.
- **Positive control.** The X-A3-WITHDRAW ABRUPT result must reproduce as a sweep in VICTIM runs: a share ≥ 0.5 within 500
  epochs after establishment in ≥ 50% of established runs. This was shown on real data.
- **Null.** ZERO is itself the no-payoff null.
- **Confounds.**
  - Establishment differs by arm, so all readouts are conditioned on establishment. The C-A3 design is unchanged.
  - "State-free" must be measured with random passengers.
  - VM equivalence across arms is shown by a self-test: arms are identical until the first accepted overwrite.
- **Expected outcomes.**
  - **T1:** appearance hazard per copy event equal across arms (within 2x); sweep only where state-freedom pays
    (VICTIM, RANDOM ≫ ZERO).
  - **T2:** appearance and sweep both ordered RANDOM ≥ VICTIM > ZERO.
  - **T4:** a D0-lineage-specific effect independent of the register rule, which contradicts U-C2.
- **Kill criteria.**
  - **T2 is dead** if the ZERO sweep share is ≥ 0.75 × VICTIM's.
  - **T1 is dead** if the ZERO appearance hazard per copy event is < 1/3 of VICTIM's.
  - **T4 (lineage-specific) is dead** if, as in U-C2, non-D0 compartments internalize at ≥ 0.75 of D0-compartment rates.
- **Smallest useful sample.**
  - 3 arms × 24 seeds × 2000 epochs × about 1000 CPU-s ≈ 20 core-h.
  - Split into E2a (VICTIM vs ZERO) and E2b (RANDOM). Each fits R2 except E2a, which is about 13 core-h, still within R2.
- **Why this beats a sweep.** It isolates the one world rule (newborn registers, U-W7) that makes state-freedom valuable.
  It separates appearance from sweep, which no C-A3-style readout could.

---

## E4. GENEALOGY: monophyletic inheritance vs recurrent origin of state-freedom (replay)

- **Exact question.** Within a run, does state-freedom originate once and spread by inheritance (T4)? Or does it arise
  repeatedly from mutation in whichever family holds the field (T1/T7)?
- **Treatment.** None. These are exact replays, with a replay-identity gate against committed records, of:
  - the 8 C-A3 EVENT runs;
  - 4 near-misses (7ae3 27000008 and 27000061; ffa6 27000053 and 27000043);
  - 6 REPLACEMENT runs.
- **Instrument.**
  - A per-site content genealogy: each accepted overwrite records the donor's content hash and site.
  - A content-keyed ancestry graph, not the lineage label.
  - At every 20-epoch check, each competent genome is tested for state-freedom (random passengers, FOR assay), with its
    ancestry path.
  - At first appearance, state-free genomes get a CVT-R and transmission-Jacobian check.
- **Experimental unit.** An origin event. For each state-free content, the most recent ancestor in its content ancestry that
  was not state-free; its child is the origin.
- **Ruler.**
  - The number of independent origins per run.
  - The share of state-free occupancy descended from the first origin.
  - Transmission (CVT-R pass) of the state-free trait.
- **Positive control (planted).** In a replay of one event run, plant a unique state-free genome at the event epoch, tagged
  by a sentinel byte. The instrument must report it as a single origin carrying ≥ 90% of its descendants' state-freedom.
- **Null.** A shuffled-ancestry null, which permutes parent pointers within each epoch, sets the expected number of origins
  under no inheritance.
- **Expected outcomes.**
  - **T4:** in ≥ 6 of 8 events, ≥ 80% of state-free occupancy descends from 1–2 origins, and the trait passes CVT-R.
  - **T1/T7:** many origins (≥ 5 per run), especially in the flicker runs (27000020), with low descent share.
  - **Replacement runs:** the same pattern as events (U-C2).
- **Kill criteria.**
  - **T4's inheritance claim is dead** if the median number of origins per event run is ≥ 5 and the first-origin descent
    share is < 0.5.
  - **T1's recurrence claim is dead** if ≥ 6 of 8 are monophyletic sweeps.
- **Smallest useful sample.** 18 replays × about 1.2× taint-level cost ≈ 6 core-h, within R2.
- **Why this beats a sweep.** It answers the one open question T4 still owns, on existing seeds, with no new populations,
  and it answers it for replacement runs as well.

---

## E6. PHASE DOSE: slice budget as hidden heritable geometry (T6's unique prediction)

- **Exact question.** Are self-poisoning, state-robustness and establishment non-monotone functions of copy count mod 128,
  as the pair-map field theory predicts?
- **Stage A (static, no runs).** For the 16 C-ZERO-SPECIFIC donors and the 16 BRIDGE donors, at slice budgets
  {256+pre, 280, 300, 320, 360}, compute:
  - the pointer advance Δ = count mod 128;
  - the carried-context conversion series;
  - the predicted P_est under CARRIED.
  Freeze the per-donor, per-budget predictions.
- **Stage B (world).** 4 donors (2 predicted to flip between robust and poisoned) × 3 budgets × 12 seeds × 500 epochs,
  CARRIED world, ATOMIC.
- **Ruler.**
  - In-world copying of the founder itself: its own P-11 births, since U-F1 showed run-level labels mislead.
  - O_F establishment.
- **Positive control.** A synthetic copier whose copy count is ≡ 0 mod 128 at budget X must be robust at X and poisoned at
  X ± 8. This was shown statically by ADV2 D4 and must replicate in-world.
- **Null.** A donor whose Δ is predicted invariant across the budgets.
- **Expected outcomes.**
  - **T6:** per-donor flips at the predicted budgets (non-monotone).
  - **T2, T3, T7:** monotone in budget (more budget, longer copies) or no pattern.
- **Kill.** **T6's arithmetic claim is dead** if fewer than 3 of the 4 donors flip as predicted (with the positive control
  passing).
- **Smallest useful sample.** Stage A is minutes. Stage B is 144 runs × about 4.5 CPU-min ≈ 11 core-h.
- **Why.** It is the only design where one theory predicts a specific non-monotone signature that the others cannot
  produce.

---

## E5. EXECUTION CONTAINMENT: is reproductive machinery a public good? (T5)

- **Stage 0 (static audit, no runs).** Classify every recorded birth for which the world state can be reconstructed, by EXEC
  motif, using `prov`/`prov_lit` plus an EXEC trace from exact replays: copy (owner executes), hijack (EXEC ≠ owner),
  paint, or residue. Sources: X-CERT-BREAK births, the 34 Archaeon replay births, and the C-ATOMIC founder-overwrite events.
  - **T5 needs** hijack in ≥ 20% of founder overwrites and ≥ 5% of all births.
  - **Kill T5** if hijack is under 5% everywhere.
- **Stage 1 (world rule).** A world variant in which pc wrap into the partner's half halts execution. Writes are unchanged.
  Arms: 7ae3 k = 1 ATOMIC, normal vs contained, 64 seeds each.
- **Frozen predictions.** Recompute Φ under containment and its P_est (T6/T7 prediction).
- **Readouts.** Founder loss at epoch 1; establishment; the hijack share of births.
- **Expected outcomes.**
  - **T5:** founder loss at epoch 1 falls from about 0.28 toward the Φ-no-hijack value, and establishment *exceeds* the
    containment-Φ prediction's change. Winners change identity in random-population arms.
  - **T6/T7:** the observed change equals the containment-Φ prediction.
- **Smallest sample.** 128 runs × 2000 epochs ≈ 35 core-h; at 500 epochs ≈ 10 core-h (establishment is decided early,
  U-T1).
- **Why.** It tests whether "who reproduces" is a property of organisms or of the execution field. That question decides
  whether *any* organism-level heredity claim on the pair tape is well-posed.

---

## E3. OPERATOR SWAP: does mutation supply set the internalization hazard? (T1, quantitative)

- **Question.** Does the ffa6/7ae3 internalization hazard ratio (about 8x, U-T5) follow the effective mutation supply
  (about 7x)?
- **Treatment.** The 7ae3 cell with `mutation_operator = BOTH` (opcodes mutable), against the frozen OPERAND. Everything else
  is the C-A3 design.
- **Prediction (T1).** The 7ae3 hazard per copy event rises by 5–10x, toward ffa6's. Cell-ecology alternatives predict no
  change.
- **Kill.** **T1 (supply) is dead** if the hazard rises by less than 2x while the effective mutation count rises by ≥ 5x.
- **Positive control.** A measured effective-mutation count per lineage under BOTH vs OPERAND (static, ARC3 accessibility
  method) must show the ≥ 5x supply change.
- **Sample.** 2 arms × 36 seeds × 2000 epochs ≈ 20 core-h. Split, or reduce to 24 seeds (≈ 13 core-h).

---

## E8. SELFCOPY: which regularities are demographic properties of the world? (T7)

- **Treatment.** A one-byte world op that copies the executing site's 64 bytes to the partner half, ignoring registers, with
  the same per-byte budget and copy-error rate [ADV1 K4]. Implant it vs 7ae3; BASE vs ATOMIC; splice on vs off; k ∈ {1, 2,
  4, 8}.
- **Prediction (T7).** The following reappear with the register-free op:
  - the dose curve's independence;
  - the depth gap;
  - BASE ≪ ATOMIC;
  - splice tail-suppression.
  Only zero-specialization, poisoning and internalization vanish.
- **Kill.** **T7 is dead** if one of the demographic signatures changes qualitatively, beyond the op's own computed offspring
  law.
- **Sample.** About 20 core-h (500-epoch runs). It needs a world-code change, so a Builder is needed.

---

## E9. cb7f OCCUPANCY REPLAY: validating the replacement ruler (prerequisite for E1)

- **Question.** Is cb7f's depth cap near 6 (8/8 ATOMIC runs copy, 163–1,053 events) takeover without turnover, or failure to
  establish?
- **Treatment.** Exact replays of the 8 C-ATOMIC cb7f ATOMIC runs, plus 4 7ae3 runs, with occupancy O_F(t) logged every 10
  epochs.
- **Prediction.** T6: cb7f O_F ≥ 0.5 in most runs, with depth low. The heredity ontology: O_F low.
- **Kill.** Depth is retired as an establishment ruler if cb7f O_F ≥ 0.5 in ≥ 5 of 8 runs.
- **Sample.** 12 replays ≈ 3 core-h.

---

## E10. TAPE ROTATION (WP-7), kept as design only

- **Question.** If placement becomes unreliable, do locators internalize (T2), or does reproduction collapse because locators
  are unreachable (T1/T3)?
- **Controls.**
  - `LD E,40 ; E5` (random padding) must fail under rotation: the self-test positive control.
  - The 16000026 locator must pass.
  - A seeded-locator arm is the positive control.
  - A no-rotation arm.
- **Expected.** T1/T3: collapse; locator rate set by density (2 of 332). T2: locator emergence where reachable.
- **Why last.** A floor effect is likely, and the build cost is high. Run it only if E2 supports T2.

---

## What NOT to do next

- **Another C-A3-style recurrence sweep.** The recurrence is established. Its unit (the D0 label) is the problem (U-C1,
  U-C2, U-C4).
- **Any heredity or "runaway" claim read from depth or anc0.** Use occupancy and transmitted-position identity (E9 decides).
- **Any competence or state-freedom screen with NOP or zero padding.** Use random passengers (FOR Q3; ADV2 D8).
