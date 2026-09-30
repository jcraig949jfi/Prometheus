# ATLAS_OPERATOR_FRONTIER -- candidate directions for the operator (NOT a queue)

Atlas[m1-a5680f90], inference harvest 2026-09-30.
- **For the operator only.** Nothing here has been sent to any seat, and nothing will be. Atlas does not route,
  prioritise for, or command seats (operator rulings 2026-09-25: reports only; anti-prior proposals go to the
  operator first).
- **Scores carry no authority.** Rankings are Atlas's estimate of information per unit cost. The cost figures are
  Atlas's or its workers' estimates [AD] and have not been measured.
- **Generated from evidence structure.** Every item comes from a contradiction, a missing causal link, a theory
  disagreement or a recurring anomaly in the harvest documents. None comes from a modality. "Evidence" pointers
  refer to the harvest files:
  - SYN = ATLAS_CROSS_ENGINE_SYNTHESIS;
  - CON = ATLAS_CONTRADICTIONS_AND_NATURAL_EXPERIMENTS;
  - BUR = ATLAS_BURIED_SIGNALS_AND_RESIDUALS;
  - ONT = ATLAS_ONTOLOGY_GAPS_VNEXT.

Format per item: **question**, why now (evidence), the minimal design, what each outcome means (a falsifier for the
current reading), cost, and whose tooling already exists. Naming tooling is not an assignment.

---------------------------------------------------------------------------------------------------------
## Tier 1: cheap, and each decides something the program currently assumes

### FR-1. Is "the world supplies reproduction" one ADDRESSING dependence, and does it survive leaving the Z80 design family?
- **Why:**
  - SYN F2: copy op + zero registers + offset/neighbour-base addressing is STRONG in the Z80 family and WEAK across
    it. The only non-Z80 instance (PTE) is not reproduction.
  - The critic's unification: a zero register IS the tape-start address, so the two legs may be one mechanism.
  - This is the program's biggest design-family-vs-substrate question.
- **Minimal design, two steps.**
  - (a) Desk/CPU: rerun Archaeon's COPIER-CENSUS on vmcopy32 with registers randomized at the start of every
    execution. Committed tooling; CPU-hours.
  - (b) Only if (a) collapses: one non-Z80 substrate with relative-only addressing and no zero convention (ALIEN-2
    below), with a copy primitive toggled on/off.
- **Outcomes:**
  - (a) Exact-copier density (96/1e7) and input gating collapse -> the copy-op and reset legs are one addressing
    dependence.
  - (a) No change -> they are separate, and F2's unification is false.
  - (b) Copiers still arise without absolute addressing -> the dependence is a Z80 convention, not a law of
    replication.
- **Cost:** (a) ~2-6 core-h. (b) a new world (days).
- **Tooling:** archaeon/z80atlas/census (Archaeon).

### FR-2. Re-read the Proteus "cliff" before anything else is built on it.
- **Why:**
  - SYN F8; CON A7/A8/A9.
  - The Campaign-4 cliff was measured with a count ruler and a greedy tie-rejecting walk.
  - The same VM's count rulers manufactured 4/7 CW01 damage claims.
  - PROTEUS-46, HEPH-32, FP-003 and the frontier suppression of C4-cliff.T1 all rest on the cliff.
- **Minimal design:**
  - (i) Re-score the committed C4-02 radius rows and the C4-08 gen-0/gen-100 lineages under the qualified
    Bernoulli(f) ruler, applied edits only.
  - (ii) Graph and v0.4 grammar: greedy vs neutral-accepting vs random walks, 200 x 300 steps per cell.
- **Outcomes:**
  - The loss curve flattens by >= 50% under (i) -> the cliff is ruler geometry.
  - A step >= .3 persists -> a genuine cliff.
  - Neutral-accepting >= 5/200 vs greedy 0/200 on (ii) -> PROTEUS-46's "no intermediate" was search, and the
    suppression's premise changes. The suppression decision itself is Proteus/Archaeon's.
  - All ~0 -> landscape.
- **Cost:** < 4 core-h (i); 2-6 core-h (ii).
- **Tooling:** CW01 qualified Bernoulli ruler (Nestor); falsifier_46.py (Proteus); D002 harness (Artemis).

### FR-3. Give the program's main deflation tool a chance to fail.
- **Why:**
  - SYN F1; critic R1.
  - The zero-parameter restatement attack killed or restricted every law it met: Cosmos C0 and C3, the C4 design,
    and in spirit WTP-03 and Hecate.
  - Its POWER is unknown. C0 rests on non-significant ties (p .125-.688).
  - An attack that ties everything is not evidence.
- **Minimal design:**
  - Run the Cosmos definition-rung attack, unchanged, on worlds with a PLANTED law that is not derivable from the
    certificate. Bellerophon's "Reservoir" family (60 rows) is already built.
  - Also run it on 4 known-answer fixtures (C0, C3, WTP-03 N6, one Hecate signal), which should all tie.
- **Outcomes:**
  - The rung fails to tie the planted law -> the attack has power, and the Cosmos kills gain real weight.
  - The rung also "ties" the planted law -> the attack is non-discriminating, and every restatement kill must be
    re-read.
- **Cost:** hours.
- **Tooling:** Cosmos C4 S0 harness; BR-C4 Reservoir rows (Bellerophon; the branch is unmerged).

### FR-4. Make "search, not physics" a measurable claim: needle size at plant length.
- **Why:**
  - SYN s2 R3. Five engines say "the capability is expressible but unreached" (PTE plants beat champions, Tyche
    2/72, the Proteus 6/6 path, the CW01 witness).
  - The critic: without needle size the dichotomy is ill-posed. A 2^-40 solution density IS a physics fact.
  - Odysseus already measured this for BEE (affordance ladder 2.7e-5 ... 1.7e-14).
- **Minimal design:** for PTE W-L lag-2 (a 16-line plant), the Proteus two_key 6/6 and Tyche Z3 parity-3, sample
  random programs or edit paths of plant length, and estimate the solver fraction. Compare it with the number of
  candidates each search actually evaluated.
- **Outcomes:**
  - Coverage >= 1/needle and the search still failed -> the search policy is at fault.
  - Needle << 1/coverage -> the wall is landscape, and "not physics" is wrong for that engine.
- **Cost:** CPU-minutes to hours per engine.
- **Tooling:** PTE lens / W-L plants (Ananke); two_key (Proteus); Tyche Z worlds.

### FR-5. Account for where variation actually comes from.
- **Why:**
  - SYN F4, the reconciled finding. Nominal mutation looks like a minor share of effective variation in the byte
    worlds: NPE mutation OFF leaves 187/192 lineages still sterile; BEE mutation supply is indistinguishable at
    8/3/4 of 300.
  - Write-back, the splice and world-made copies dominate.
  - Atlas lists write_authority as UNMEASURED.
- **Minimal design:**
  - (a) Desk: convert C-ATOMIC's effect into an effective-mutation-rate change, and test an error-threshold model
    against 1/80 vs 46/80.
  - (b) A "variation budget ledger": per 1,000 epochs, the share of byte changes by source (mutation operator /
    partner write-back / splice / world copy), in NPE 7ae3, one BEE grounding cell and Aether add.
- **Outcomes:**
  - The rate model predicts C-ATOMIC -> write authority is the dominant variation SOURCE, not a separate axis.
  - The effect exceeds the prediction -> write authority carries something beyond rate.
  - The ledger shows the mutation operator < 20% of byte changes in >= 2 engines -> campaigns varying "mutation
    rate" have mostly varied the wrong knob.
- **Cost:** desk (a); ~5-10 core-h (b).
- **Tooling:** NPE X-STALL harness (Nestor); BEE grounding (Bellerophon); Aether ladders.

### FR-6. Is task competence ever on the copy path?
- **Why:**
  - SYN F3. Copying and persistence dissociate from competence in two lineages: transplants 39/39 persist, 0/39
    competent; incompetent imports take over 12/12.
  - The critic: the dissociation may be designed in, because the task is bolted onto the copy loop.
- **Minimal design:**
  - (a) Desk: using TH-015 executed-path data, measure the fraction of task-code bytes on the copy loop's executed
    path in the 39 transplants.
  - (b) If (a) is ~0: the frozen NPE X-TASK-GATE plus one BEE-style PAID arm with a YOKED twin (CON A11).
- **Outcomes:**
  - (a) ~0 -> the dissociation is a world-design fact, and the frontier question becomes "design a world where
    task code must be executed to copy".
  - (a) substantial overlap with competence still lost -> an evolutionary result.
  - (b) PAID >> YOKED while TASK_GATED ~ SHUF -> the coupling channel (resource vs interaction) decides.
- **Cost:** desk (a); +10 core-h (b), plus the Aporia dispatch X-TASK-GATE already requires.
- **Tooling:** archaeon attribution lens; roles/Nestor/.../x_task_gate (frozen 62d30e443).

---------------------------------------------------------------------------------------------------------
## Tier 2: moderate cost, high cross-engine yield

### FR-7. One initialization protocol across NPE, BEE and PTE (CON B1).
- **Design:** arms ZERO / CONST 0x5A / RANDOM-per-execution / CARRIED. Common readout: the fraction of evolved
  competent organisms whose competence drops > 50% when entry registers switch from ZERO to CONST.
- **Outcome logic:**
  - Dependence re-forms around whatever constant is supplied -> a convention effect.
  - Only ZERO works (as in NPE: 26/48 vs 2/48) -> an addressing effect.
- **Cost:** ~30 core-h.

### FR-8. A replicator ruler shared by all three Z80 worlds (CON A1, A2).
- **Design:** Archaeon's census classifier run on BEE's VM (LDIR on/off, undefined=HALT), and CVT-R run on BEE's
  83 distinct-seed origins.
- **Outcome logic:**
  - BEE CVT-R pass rate falls well below the SR label's 99% -> the three worlds' "replicator" counts are
    incommensurable.
  - It stays >= 95% -> the difference is the ISA.
- **Cost:** ~4-8 core-h.

### FR-9. Answer-before-read across engines (SYN F5; one seat-to-seat chain so far, so an independent test is the point).
- **Design:**
  - Verify Artemis R-22 on the committed C3 elites: one pre-PUT noise tick. R-22 claims 10/11 latch; prediction: >= 8/11 fall below 0.5.
- Test it in an engine outside the C3 -> CW01 -> C9 chain (PTE or BEE), by a seat that did not originate it.
  - Add a free-cue arm.
  - Add one PTE task with a costly late read.
- **Outcome logic:**
  - Latching persists with a free cue -> "only when reading costs" is NPE-specific.
  - It vanishes -> the cost of reading is the cross-engine driver.
- **Cost:** ~2-6 core-h.

### FR-10. A denominator for "present != used" (SYN F6).
- **Design:** with the PTE swap tooling, measure the fraction of decodable variables whose swap changes output, in
  evolved champions vs unselected programs of equal size.
- **Outcome logic:**
  - Equal fractions -> "present != used" is generic to the instrument on integer substrates.
  - Evolved champions differ -> a real regularity with a number attached.
- **Cost:** hours.

### FR-11. The author-prior check, scaled up (SYN s0; handoff s7).
- **Design:**
  - Re-run 2-3 already-decided audit verdicts with a non-Claude model family on identical inputs: E-003 ALTERED vs
    VALIDATED, the Hecate detector ruling, and one R-11 row.
  - Re-derive cross-engine regularities from masked OBSERVED rows. This harvest ran a pilot (handoff s7).
- **Outcome logic:** verdicts flip with the model family -> the program's "independent" audits share a prior.
- **Cost:** hours; external API.

### FR-12. Record the readout type everywhere (CON B7).
- **Design:** report ever-reached vs final-state at 1x and 20x horizon for NPE C-A3 events, BEE REPL P75 and Aether
  rcv_str. This is mostly re-analysis of stored checkpoints.
- **Why:** in four engines the readout decided the verdict more than the horizon did.
- **Cost:** re-analysis, plus ~20 core-h for the NPE rerun.

---------------------------------------------------------------------------------------------------------
## Deliberately alien proposals (not ML benchmarks; anti-prior; operator approval first)

Each attacks an assumption that every current engine shares. All are speculative [AD].

### ALIEN-1. A permission ecology: evolve WHO MAY WRITE, not what is written.
- **Design:**
  - Fix a population of simple, non-replicating programs.
  - The only heritable variable is a write-permission map: which program may write which region, when.
  - Selection acts on regional persistence.
- **Question:** can heredity-like persistence arise from permission structure alone, with no copy instruction?
- **Why:** SYN F4. Write physics dominates variation, yet no engine has made it the evolving object.
- **Falsifier:** no permission lineage beats a shuffled-permission null on persistence over 10^4 epochs.

### ALIEN-2. An address-free, zero-free substrate.
- **Design:**
  - Content-addressed or strictly relative memory.
  - Registers initialised from environmental noise.
  - No absolute tape offsets.
  - A copy primitive offered only as "copy the pattern matching X".
- **Question:** does self-copying arise when the world supplies no self-location?
- **Why:** SYN F2 / FR-1. Every Prometheus soup, and every published soup the NPE synthesis surveyed, supplies
  self-location.
- **Falsifier:** zero copiers in >= 1e7 random programs with the pattern-copy primitive present, where a supplied
  absolute-address control produces >= 1e-5.

### ALIEN-3. Co-evolving rulers.
- **Design:** rulers are a second species. A ruler's fitness is its ability to return the correct opposite outcome
  on hidden planted cases drawn by the world. Organisms are scored only by rulers that are currently fit.
- **Question:** does measurement validity itself evolve?
- **Why:** SYN F1. The program's binding constraint is ruler validity (37/94 absence gates never fired). This
  turns that constraint into a substrate rather than an audit.
- **Falsifier:** evolved rulers' planted-case accuracy never beats a fixed random ruler, or organisms exploit rulers
  faster than rulers recover (a measurable race).

### ALIEN-4. Invert the cue economy.
- **Design:** a world where acting before reading is taxed and memory is free, crossed with the current program
  default (reading taxed, early answers free). 2x2.
- **Question:** is "answer before read" (SYN F5) a search attractor or a consequence of task structure?
- **Falsifier:** evolved solutions read first under the inverted economy at the same rate as the program default.

### ALIEN-5. Organization without inheritance: mutual-supply loops (from BUR A12).
- **Design:** in Aether, seed and lesion energy 2-cycles (mutual supply, enriched 1.58x), against a sham.
- **Question:** is there a self-maintaining unit that persists without any copying?
- **Why:** this is the one autocatalysis-shaped observation in the record, and it was never tested.
- **Falsifier:** partner survival after lesion equals sham.

---------------------------------------------------------------------------------------------------------
## What Atlas would NOT do next (and why)
- Launch any new large campaign before FR-2 and FR-3. Too much of the record's negative structure rests on an
  untested cliff and an attack of unknown power.
- Pool any "N engines agree" claim without the ruler x lineage x author recount (SYN s0). The three Z80 worlds are
  one design family, and the Proteus VM is one VM.
- Read a mechanism name from the last 10 days as settled (SYN F7).
