# NPE decisive experiments: designs that separate the competing theories (revision 2)

This is Nestor's inference harvest of 2026-09-30. Everything here is a design. **No experiment below is authorized or started.**
- Execution needs an Aporia dispatch (CWO-C s7). Anything beyond the MWO-0004 R2 envelope (≤ 16 CPU core-h per item) also
  needs operator authority.
- Theories T1–T7 are defined in NPE_COMPETING_THEORIES.md (revision 2). Evidence codes U-xx refer to NPE_UNMINED_EVIDENCE.md.
- Revision 1 had three broken designs, which the red-team found: E1's ruler could not fire and E1 tested the wrong condition
  for T4; E2's null was not a null; E4's predictions were not opposite (RT B4–B6). Those are redesigned here.
- Revision 1 also claimed prereg-readiness that four designs lacked. Those designs are now marked **SKETCH** (RT M7).

**Status labels:**
- **PREREG-READY (content)** means every field the directive requires is present. Each design still needs all of the following
  before exposure:
  - a frozen PREREG.md with a commit hash;
  - an instrument self-test (fail on old code, pass on new);
  - a **ruler-reachability gate** on real data (Harmonia F8; Bellerophon #1113);
  - a computed eligibility count.
- **SKETCH** means the question and treatment are defined, but the design is not ready to freeze.

---

## Ranking (by information, not by score)

| tier | item | what it separates | status | cost |
|---|---|---|---|---|
| **0 static** | S1 one-step map vs recorded per-donor outcomes | T6 vs a history-dependent account | **DONE: PARTIAL** (`forensics/FORENSIC_MAP_PREDICTS_OUTCOMES.md`) | done |
| 0 | S1b two-step map, out of sample (W1 first donors; criterion frozen before computing) | T6 (with closure) vs T4 | **DONE: PASS, qualified.** Predicts first-donor fate out of sample (AUC 0.89), but adds nothing beyond the known self-poisoning split. | done |
| 0 | S2 EXEC-motif audit of recorded births | T5 vs T6/T7 | design | ≤ 1 core-h, no world runs |
| 0 | **S3 pairwise knockout map of evolved state-free genomes** | **T4(c) epistasis vs T3** | design, PREREG-READY (content) | ≤ 2 core-h, VM calls only |
| **1 replay** | **E4 GENEALOGY (redesigned)** | T4(b) shared mechanism vs T1/T3 convergence; T1's count model | PREREG-READY (content) | ≈ 6 core-h |
| 1 | E9 cb7f occupancy replay | ruler validity (depth vs occupancy) | PREREG-READY (content) | ≈ 3 core-h |
| **2 small new populations** | **E1 RECONSTITUTION (redesigned, with a home arm)** | **T4(a) home advantage vs T3/T6** | PREREG-READY (content) | ≈ 2 + 7 + 14 core-h (3 items) |
| 2 | E2 NEWBORN-REGISTER factorial (redesigned, with a true reset null) | T1 vs T2 on *appearance* | PREREG-READY (content), eligibility gated on E4 | ≈ 20 core-h (2 items) |
| 3 | E5 EXECUTION CONTAINMENT | T5 vs T6/T7 | SKETCH (Stage 0 = S2) | ≈ 10 core-h |
| 3 | E3 OPERATOR SWAP | T1 supply vs cell ecology | SKETCH (eligibility problem, see below) | ≈ 16 core-h |
| 3 | E6 PHASE dose | T3/T6 (LDIR semantics) vs T2 | SKETCH (downgraded after S1, see below) | ≈ 10 core-h |
| 3 | E8 SELFCOPY | T7 vs T3/T4 | SKETCH (needs a Builder) | ≈ 20 core-h |
| 4 | E10 TAPE ROTATION | T2 vs T1/T3 on placement | SKETCH | 16+ core-h |

**The most discriminating next step** is a set of three T4 tests. Each targets one of T4's still-untested distinctive
predictions:
- **S3**, static: does organization show as multi-site epistasis?
- **E1's HOME arm**: is there a home-population advantage?
- **E4**: is the mechanism shared across independent origins?

If all three come back null, with rulers shown able to fire, "endogenous reproductive organization" in NPE reduces to an
evolving compact copy setup in a world that supplies the rest. If any one is positive, that is the first certificate T4 has
ever had. Either outcome is worth more than another recurrence sweep. S3 and E4 cost about 8 core-h together, and S3 needs no
world runs at all.

---

## S3. PAIRWISE KNOCKOUT MAP: is there multi-site organization that single knockouts miss? (static)

- **Question.** Do evolved state-free genomes contain pairs of individually dispensable positions whose *joint* knockout
  destroys competence or state-freedom (synthetic lethality), beyond what single knockouts and additivity predict?
- **Units.** Genomes. The primary panel is FOR's 48 state-free genomes, the 8 epoch-700 16000006 genomes included and
  stratified by run. The comparator is 48 state-dependent genomes from the same runs.
- **Treatment.** For each genome, take every pair of positions that is individually non-essential under random-value
  knockouts (3 draws each). Knock the pair out jointly with random values (3 draws). Score COMPETENT (zero context) and
  STATE_FREE (R1/R2 assay, as in `run_ci.sf`).
- **Ruler.** The synthetic-lethal pair rate, meaning the share of dispensable pairs whose joint knockout collapses the
  function, against a null. The null is the rate expected if each single knockout had an independent small effect,
  estimated from the single-knockout rate distribution.
- **Positive control.** A constructed genome with a known redundancy: two independent LD E,0x40 setters feeding one copy.
  Single knockouts must be dispensable and the pair lethal.
- **Negative control.** The minimal copier `LD L,0 ; LD E,40 ; E5` with random passengers. Pairs among the passengers must
  show the null rate.
- **Confounds.**
  - Assay noise near the 0.5 threshold. Re-assay flagged pairs with new seeds and count a pair only if lethal in ≥ 2 of 3.
  - The 16000006 genomes come from one lineage, so they are analysed as one cluster.
- **Expected outcomes.**
  - **T4(c):** the state-free genomes have a synthetic-lethal rate above the null *and* above the state-dependent
    comparators, concentrated in the address-sourcing chain.
  - **T3:** the rate is near the null for both groups.
- **Kill.**
  - **T4(c) is dead** if the state-free synthetic-lethal rate is ≤ 1.5x the null and ≤ 1.2x the state-dependent rate.
  - **T3's no-organization reading is dead** if the rate is ≥ 3x the null in ≥ 50% of state-free genomes.
- **Sample and cost.** About 60 non-essential positions per genome gives about 1,770 pairs × 3 draws × about 2 screens. That
  is too many for 96 genomes. Sample 200 random pairs per genome instead: 96 × 200 × 6 ≈ 115k screens at about 20 ms each,
  about 0.7 core-h.
- **Why.** It tests T4's one structural prediction statically and cheaply, with no world run.

---

## E4. GENEALOGY (redesigned): how many origins, and do independent origins share a mechanism?

- **Exact questions.**
  - (Q1) How many independent origins of state-freedom occur per run, and does that match T1's count model?
  - (Q2) Do independent origins, in different runs, converge on one transmitted mechanism (T4(b)), or on diverse
    constant-loading solutions (T1/T3)?
- **Correction to revision 1 (RT B6).** A monophyletic sweep does **not** separate T4 from T1. T1 predicts one:
  - at the ffa6 hazard (about 1 per 140k organism-epochs) and N = 256, expect about 1 origin per ~550 occupied epochs;
  - a paying variant sweeps in about 100 epochs.

  Q1 therefore tests T1's *count model* only. Q2 carries the T4 test.
- **Treatment.** None: these are exact replays of existing seeds, behind a replay-identity gate against the committed
  records.
  - The 8 C-A3 EVENT runs.
  - 4 near-misses: 7ae3 27000008 and 27000061; ffa6 27000053 and 27000043.
  - 6 REPLACEMENT runs.
  - Replacements are included to settle RT B3: were their founders already state-free?
- **Instrument.**
  - A per-site content genealogy: each accepted overwrite records the donor content hash and site.
  - At every 20-epoch check, every competent genome is screened for state-freedom with random passengers.
  - **Assay-repeatability null (RT B6):** each state-free call is re-assayed with 3 fresh seed sets. Only stable calls (≥ 3
    of 4) count.
  - For each stable state-free lineage segment, the most recent stable-non-free ancestor's child is the **origin**.
  - At each origin, record:
    - the address-sourcing mechanism class: which instructions set L and E (`LD DE,nn`, `LD E,n`, register-derived chain),
      and the copy side;
    - the CVT-R and transmission Jacobian of the trait.
- **Units.** Origins (Q2); runs (Q1).
- **Rulers.**
  - Q1: origins per run against T1's predicted count, computed from each run's own occupancy trajectory and the U-T5
    hazard, with its CI.
  - Q2: the number of distinct mechanism classes across origins in different runs, and whether a class is transmitted as a
    unit (CVT-R on the class-defining bytes).
- **Positive control (planted).** In one event replay, plant a unique state-free genome carrying a sentinel byte at the event
  epoch. It must be reported as one origin carrying ≥ 90% of its descendants' state-freedom.
- **Nulls.**
  - A shuffled-parent null (permute parents within epoch) for origin counts.
  - The assay-repeatability null above.
- **Also reported.** For every REPLACEMENT compartment, whether its first competent genomes were already stably state-free.
  This resolves "acquired vs founding" (U-C2).
- **Expected outcomes.**
  - **T4(b):** origins in different runs share one mechanism class, transmitted as a unit.
  - **T1/T3:** ≥ 3 mechanism classes, with no shared transmitted unit. Origin counts within 3x of T1's model.
- **Kill.**
  - **T4(b) is dead** if ≥ 3 distinct classes appear across ≥ 6 origins in different runs and no class is transmitted as a
    unit.
  - **T1's count model is dead** if observed origins per run deviate more than 3x from prediction in ≥ 6 of 8 event runs.
- **Eligibility.** At least 8 event origins are needed for Q2. The 8 C-A3 events plus any repeat origins should give ≥ 8. If
  fewer than 6 stable origins are found, report INSUFFICIENT.
- **Cost.** 18 replays × about 1.2x taint-level cost ≈ 6 core-h.

---

## E1. RECONSTITUTION (redesigned): is there a home-population advantage beyond the map?

**Why redesigned (RT B4).**
- Revision 1 implanted into a naive population, where T4 predicts *no* advantage.
- Its ruler, identity to the implant, decays to about 0 even under takeover (U-I1, U-I6), so it would have fired "T4 dead"
  whatever the truth.
- It scrambled outside a zero-context competence set, not a state-freedom set.

- **Exact question.** Do evolved state-free genomes hold their home field against invaders better than their own two-step map
  predicts? T4(a) says yes. T3/T6 say the map predicts it.
- **Panel.** 8 **independent lineages**: one stable state-free genome from each C-A3 EVENT run (ffa6 × 7, 7ae3 × 1), taken at
  the event checkpoint from E4's replays. Each runs in its own cell. The 8 epoch-700 genomes from 16000006, a single lineage,
  are an optional ninth cluster.
- **Derived genomes, per lineage:**
  - **SCR:** random bytes outside the **state-free knockout set**. That set is the positions whose random-value knockout drops
    COMPETENT or either STATE_FREE vector below 0.5. There is a static gate: an SCR must remain stably competent and
    state-free, or it is redrawn up to 5 times, else excluded and reported.
  - **SYN:** a synthetic state-free copier (explicit L/E constants, random passengers), chosen so its **two-step map
    predictor** (S1's P_run500_causal, as frozen in S1b) is within ±0.05 of the EVO genome's. If no match exists, report
    UNMATCHED.
  - **REF:** extra EVO clones, the neutral reference.
- **Arms:**
  - **HOME** (E1a): snapshot the home run's population at the event checkpoint. Replace 16 random sites with invaders of one
    class (REF, SCR or SYN), run 300 epochs, and record invader-class occupancy.
  - **NAIVE** (E1b): implant each class at k = 4 into a random background and run 500 epochs.
- **Ruler.** Content-ancestry occupancy: the share of sites whose content descends, by the E4 genealogy with
  transmitted-position identity ≥ 0.9 at each edge, from the implanted or invading class. It is not identity to the implant.
- **Ruler-reachability gate (before freezing).** On existing X-ATOMIC 7ae3 replays, the occupancy ruler must read ≥ 0.5 in
  ≥ 80% of the depth ≥ 20 runs and ≤ 0.1 in the depth ≤ 2 runs. Otherwise E1 is INSTRUMENT_UNREACHABLE and does not run.
- **Positive controls.**
  - HOME: a **known-sterile variant** must be excluded to occupancy ≤ 0.02. Per S1 this is a byte-0 mutant whose children
    convert at ≤ 0.03. REF must hold ≈ 16/256 (0.0625 ± 0.03).
  - NAIVE: 7ae3 must reproduce its ATOMIC establishment.
- **Null.** In NAIVE, a random-genome implant must give 0 occupancy.
- **Confounds.**
  - Donor side: every EVO genome is side-0 (FOR). Match SYN on side and report it.
  - Lineage heterogeneity: random effects by lineage.
  - Pseudo-replication: the 16000006 cluster is analysed separately.
- **Expected outcomes.**
  - **T4(a):** in HOME, SCR and SYN invaders are held below REF by more than their map difference. In NAIVE, EVO ≈ SYN.
  - **T3/T6:** HOME invader occupancy matches the map (SCR ≈ SYN ≈ REF). NAIVE outcomes track the predictor.
- **Kill.**
  - **T4(a) is dead** if SCR and SYN HOME occupancies are within ±0.03 of REF in ≥ 6 of 8 lineages, with the sterile
    positive control excluded as required.
  - **T3/T6 are dead** if SCR or SYN HOME occupancy is < 0.5 × REF in ≥ 6 of 8 lineages while their predictors are matched.
- **Power and eligibility.** With 6 seeds per (lineage, class), an occupancy SD of about 0.02 around 0.0625 detects a 0.03
  deficit at about 80% per lineage. The HOME kill needs 6 of 8 lineages. Pre-compute each lineage's predictor before
  freezing. A lineage whose EVO genome sits at ceiling cannot show an advantage and is flagged non-eligible.
- **Cost.**
  - Snapshots, from E4's replays: included in E4.
  - E1a HOME: 8 lineages × 3 classes × 6 seeds × 300 epochs ≈ 144 runs × 163 s ≈ 6.5 core-h, plus the sterile-control arm
    ≈ 7 core-h.
  - E1b NAIVE: 8 × 3 × 8 seeds × 500 epochs ≈ 192 runs × 270 s ≈ 14.4 core-h, including 7ae3 and random controls, within
    R2.
- **Why.** It is the only design that tests T4's population-level prediction where T4 actually makes it, with a ruler that
  is gated to be able to fire.

---

## E2. NEWBORN-REGISTER FACTORIAL (redesigned): appearance vs sweep, with a true no-payoff arm

**Why redesigned (RT B5).** A ZERO arm that resets only newborn registers still rewards state-freedom, because every organism
carries registers between interactions and so self-poisoning still bites. T1 and T2 also predict the same sweep ordering.

- **Exact question.** Is the *appearance* of state-freedom driven by supply (T1) or by demand (T2)?
- **Arms.** The C-A3 design otherwise frozen (random populations, dense VM, ATOMIC, ffa6, 2000 epochs):
  - **VICTIM:** current.
  - **RANDOM-PER-BIRTH:** maximal newborn noise.
  - **RESET-EVERY-INTERACTION:** both organisms enter every interaction at zero registers. This is the no-payoff arm: carried
    state never matters.
- **Instrument.**
  - E4's genealogy, with stable-call re-assay: appearance = stable origins per 10^5 copy events.
  - Copy-event counts per checkpoint.
  - State-freedom screened with random passengers.
- **Rulers.**
  - (a) Appearance hazard per copy event. This is the T1/T2 separator.
  - (b) Sweep: stable state-free share among competent genomes at 1,000 and 2,000. T1 and T2 predict the *same* ordering
    here; it is reported only.
- **Positive control.** The VICTIM arm must reproduce an X-A3-WITHDRAW-like sweep in ≥ 50% of established runs.
- **Null.** RESET-EVERY-INTERACTION.
- **Expected outcomes.**
  - **T1:** appearance hazard per copy event is equal across arms (within 2x). Sweep occurs only where state-freedom pays.
  - **T2:** appearance is ordered by demand (RANDOM ≥ VICTIM ≫ RESET).
- **Kill.**
  - **T1 is dead** if the RESET appearance hazard is < 1/3 of VICTIM's.
  - **T2 (demand-driven appearance) is dead** if the RESET appearance hazard is ≥ 0.5 × VICTIM's.
  - Between those ratios: INCONCLUSIVE.
- **Eligibility (gated on E4).** At least 10 stable origins per arm are needed. E4's origin counts give the per-run expectation.
  If 24 seeds per arm would not reach 10, the item stops before launch and requests more seeds.
- **Cost.** 3 arms × 24 seeds × 2000 epochs ≈ 20 core-h, split E2a (VICTIM + RESET, ≈ 13) and E2b (RANDOM, ≈ 7).

---

## E9. cb7f OCCUPANCY REPLAY: validating the replacement ruler

- **Question.** Is cb7f's depth cap near 6 (it copies in 8/8 ATOMIC runs) a case of takeover without turnover, or a failure to
  establish?
- **Treatment.** Exact replays of the 8 C-ATOMIC cb7f ATOMIC runs and 4 7ae3 runs, with content-ancestry occupancy logged every
  10 epochs.
- **Controls.**
  - Positive: 7ae3 runaway replays must read occupancy ≥ 0.5.
  - Negative: a random-implant replay must read ≤ 0.02.
- **Kill, in both directions (RT m15).**
  - Depth is retired as an establishment ruler if cb7f occupancy is ≥ 0.5 in ≥ 5 of 8 runs.
  - cb7f "failed to establish" is confirmed, and depth stands for it, if occupancy is < 0.5 in ≥ 5 of 8.
- **Cost.** 12 replays ≈ 3 core-h.

---

## SKETCHES (not prereg-ready)

- **E5 EXECUTION CONTAINMENT.**
  - Stage 0 is S2: an EXEC-motif audit of recorded births (copy, partner-exec, paint, residue, self-import).
  - Stage 1 is a world rule where pc cannot cross into the partner half.
  - Before any world run, it needs: a hijack prevalence ≥ 5% from S2, a recomputed-Φ prediction under containment, and a
    unit and eligibility definition.
- **E3 OPERATOR SWAP.**
  - **Eligibility problem (RT M7).** C-A3 had 1 event in 72 7ae3 runs, so raising the 7ae3 hazard is not measurable at 24–36
    seeds.
  - **Redirected design.** Make **ffa6** opcode-immune (7 events in 72 at baseline). T1 predicts a drop to about 1 event. That
    is detectable only at ≥ 72 seeds per arm, about 40 core-h.
  - Needs operator authority, or a cheaper appearance-hazard ruler from E4.
- **E6 PHASE dose.**
  - Downgraded after S1: real robust donors reload their pointers, and copy counts ≡ 0 mod 128 almost never occur (164–295
    observed). The dose pattern is predicted by T3 and T6 alike, since it is LDIR semantics (RT M8).
  - Keep it only as a T3/T6-vs-T2 test with a site-level budget, which holds the background fixed and so needs world code.
- **E8 SELFCOPY.** A register-free one-byte world copy op, used to test T7's demographic signatures. It needs a Builder and a
  ruler definition.
- **E10 TAPE ROTATION (WP-7).** Positive control: the 16000026 locator. Negative control: `LD E,40 ; E5` with random padding.
  Likely a floor. Run only if E2 supports T2.

---

## What NOT to do next

- **Another C-A3-style recurrence sweep.** The recurrence is established, and its unit (the D0 label) is the problem.
- **Any establishment, heredity or "runaway" claim read from depth or anc0 until E9 decides.**
- **Any competence or state-freedom screen with NOP or zero padding.** Use random passengers.
- **Any "not imported" claim without a planted-transplant positive control** (X-MAT lacked one).
