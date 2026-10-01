# Nestor inference ledger, Wave 2 (2026-09-30 → 2026-10-01 04:30 ET)

**Directive:** `roles/Nestor/prompts/2026-09-30_inference_saturation_wave2/` (sha256 4c1f7353…8468).
**Starting point:** Wave 1 rev 2, `roles/Nestor/inference_harvest_2026-09-30/` (2ca81ab32).
**Purpose:** a record that stops us rediscovering the same thought twice. One entry per investigation; entries are appended
in completion order.

**Entry format:**
- question;
- evidence inspected;
- inference/result;
- confidence;
- strongest objection;
- unresolved issue;
- next questions generated.

## Active queue (opened about 00:25Z)

| id | investigation | directive item | owner |
|---|---|---|---|
| W2-1 | contradiction mine: evidence that would make each synthesis conclusion look wrong | A | Opus worker |
| W2-2 | near-miss science: precursor signatures and early-warning observables | B | Opus worker |
| W2-3 | heredity without our vocabulary: several independent re-descriptions, then divergent predictions | C | Opus worker |
| W2-4 | causal minimality: copied vs necessary vs establishment-only vs environment vs physics | D | Opus worker |
| W2-5 | historical error autopsy, with reusable instruments implemented | E | Opus worker |
| W2-6 | theory tournament: 21 pairs, existing evidence first | F | Opus worker, then attacked by Nestor |
| W2-7 | alien reproductive physics: VM modifications plus static competence-rate probes | G | Opus worker |
| W2-8 | executable-semantics audit of the NPE world, runners and rulers | code reading | Opus worker |
| W2-9 | statistical-method review of every CONFIRMED NPE verdict | review | Opus worker |
| W1-S3 | pairwise-knockout epistasis (T4(c)), carried over from Wave 1 | D/F | Opus worker (running) |

## Entries

### W1-S3: pairwise-knockout epistasis (T4(c)). Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Question.** Do state-free genomes carry multi-site organization that single knockouts miss?
- **Evidence.** 48 state-free + 48 state-dependent genomes (FOR panel), 100 dispensable pairs each, 3 draws, re-assay. Preregistration written before computing. Positive control: a redundant-setter construct. Negative control: passenger pairs of a minimal copier. See `inference_harvest_2026-09-30/forensics/FORENSIC_PAIRWISE_EPISTASIS.md`.
- **Result.** **T4(c) DEAD under the frozen rules.**
  - Excess: 0.77x null (state-free) vs 0.71x (state-dependent).
  - State-free rate is 0.56x the state-dependent rate. The ratio is 1.01 in the zero-null stratum.
  - Strict synthetic lethality is 3.7% in both groups, spread thinly, with no recurring motif.
  - Both controls passed. One deviation: 100 pairs per genome instead of 200, under the budget clause.
- **Confidence.** Moderate-high for "state-freedom carries no extra multi-site organization at the pair level".
- **Strongest objection.** The null over-predicts, so excess < 1 is uninformative. Pairwise knockouts cannot see higher-order or population-level organization. The test is static: competence and state-freedom screens, not in-world establishment.
- **Unresolved.** Establishment-level epistasis: a knockout pair that leaves the screens intact but kills the two-step map.
- **Next questions.** Does any pair change S1b's two-step predictor while leaving the screens intact? That is cheap and static, and it overlaps W2-4.

### N1: foreign-cell "victim magnet" (Nestor, primary session). Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Question.** Revision 2 moved the 9cba/e160 magnet to "unexplained", following RT B1. Is that right?
- **Evidence.** `inference_saturation_wave2/N1_foreign_magnet/magnet_rate.py` and `.json`. Static p11.interact with the C-SWAP-ACQUIRE cells, stock VM, ATOMIC predecessor criterion, 1,500 interactions per condition, attribution by `prov`.
- **Result.**
  - In both foreign cells the founder is overwritten (predecessor-accepted) by partners at about 0.1-0.5% per interaction, mostly at side 0:
    - 9cba: zero context 2/750, random 4/750;
    - e160: random 6+2/750.
  - The changed bytes are authored almost entirely by the partner's context (9cba random: 249 partner vs 2 founder bytes).
  - **LDIR knockout gives 0/1,500 overwrites in every cell and context.** SELF knockout does not remove them; SELF is absent from these cells' ops mask.
  - So the mechanism is a partner executing the founder's **LDIR**, not SELF.
  - Integrating per epoch: with a per-epoch hazard of about 0.07-0.27%, P(founder label lost by epoch 2000) is about 0.74 to 0.99. The observed figure is 100/240 lost, plus 44 spread. That matches in order of magnitude.
- **RT B1 contained a denominator error.** It compared a per-interaction rate (≤ 1.5%) with a per-run frequency (42%), and revision 2 accepted the comparison without checking the denominator.
- **Correction, in both directions.** The magnet is *plausibly* explained by partners executing the founder's LDIR, integrated over the run. That is a hijack via LDIR, not SELF. It is not demonstrated in-world.
- **Also measured.** In 7ae3's own cell the side-0 hijack is 320/750 (43%) per side-0 interaction under zero context, and 242/750 under random context.
- **Confidence.** Moderate: the mechanism dependence on the LDIR bytes is clean, and the integration is order-of-magnitude only.
- **Strongest objection.** Survival in 45-51 runs where the founder persists alone is hard to square with the integrated hazard. Possible reasons:
  - real contexts are not uniform random;
  - the founder is not paired every epoch (pressure or allocation);
  - other context effects.
  The hazard model over-predicts loss.
- **Unresolved.** In-world confirmation needs one instrumented replay.
- **Next questions.**
  - Does LDIR-hijack exposure explain founder loss in X-TICKET (the 28%)?
  - Does it predict which C-ATOMIC C2 specimens lose their founder?

### N2: X-TICKET founder loss at epoch 1 (Nestor). Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Question.** Does the side-0 hijack account for the 28% founder loss at epoch 1, which no experiment named?
- **Evidence.** N1's own-cell rate: 320/750 = 0.43 per side-0 interaction (zero context, founder intact), 0 with SELF knocked out. X-TICKET: 36/128 = 0.28 (binomial 95% CI about 0.20-0.36).
- **Result.** The founder is at side 0 with p = 0.5 at epoch 1, so the predicted loss is about 0.5 × 0.43 = **0.21**. That is inside the observed CI.
  - Caveat: X-TICKET used BASE write-back, while the N1 criterion is ATOMIC/predecessor.
- **Reading.** Most of the unnamed epoch-1 founder loss is partners executing the founder's SELF+LDIR code.
- **Confidence.** Moderate.
- **Objection.** BASE erosion adds other loss routes, and the predecessor criterion under BASE differs slightly.
- **Next questions.** Does a hijack-exposure-adjusted founder ticket reconcile X-TICKET's branching prediction (0.43 vs 0.078 observed wins)?

### N3: the shape of depth after saturation (Nestor). Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Question.** Is post-saturation depth linear turnover, as both adversaries assumed?
- **Evidence.** `c9x/x_runaway/RESULTS.json` series for 2 runaways, every 20 epochs.
- **Result.** No, it is not linear.
  - Depth reaches about 50 by epoch 140-160 (causal-descendant share about 0.7, i.e. saturation).
  - Then it climbs in **steps with long plateaus**: 102 from epoch 620 to 1,100; 114 from 500 to 1,100; 179 constant over the last 500 epochs. The average is about 0.1 per epoch, while P-11 copying stays at about 90-100 events per epoch.
  - So depth behaves like a **record statistic of the longest unbroken certified chain**. It is neither turnover nor establishment.
- **The depth gap follows from two facts:**
  - establishment is decided early (3-10 epochs, U-T1);
  - after an early saturation, about 1,800 epochs of record growth reach about 100+.
  So intermediate depths need a late saturation, which is rare.
- **Prediction.** Runaways whose saturation is late should fill the gap (ADV1/ADV2 noted that k ≥ 2 partly fills it). Final depth is a noisy function of the post-saturation time.
- **Confidence.** Moderate (n = 2 series).
- **Next questions.**
  - Fit record growth on C-CORE and X-CORE-TIME (do their files carry depth series?).
  - Is the plateau length set by the certification-break rate (X-CERT-BREAK)?

### N4: copy errors are the dominant mutational supply. The U-T5 "8x ≈ 7x" agreement is likely coincidental (Nestor). Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Question.** RT M1 objected that the 7ae3 event is 91% MKL, so OPERAND supply is not its source. What *is* MKL made of?
- **Evidence.**
  - `z8.py:413-417`: a copy error flips a random bit of **any** copied byte at rate cmr.
  - `z8taint.py:283-286`: the flipped byte takes the executor's tag, which X-MAT classifies as MKL.
  - `world.py:150`: copy_mut = mut_rate = 0.002.
  - Copy lengths in real donors are 164-295 bytes (S1).
- **Result.**
  - Each execution makes about 0.3-0.6 copy-error flips, including in opcodes, in every cell.
  - In runaway populations (about 90-100 certified copies per epoch), copy errors supply far more variation than world mutation. That is why 7ae3's L genomes are 91% MKL and ≤ 6% MUT: world mutation cannot touch 7ae3 opcodes, but copy errors can.
  - The ARC3 "34 vs 239 effective mutations per neutral lineage" counts world mutation on a non-copying lineage. It is **not the relevant supply** for internalization in runaway populations.
  - **The U-T5 agreement between the ≈ 8x hazard ratio and the ≈ 7x supply ratio is therefore likely coincidental.** The ffa6 > 7ae3 difference (7 vs 1 events) has no supply explanation. Candidates: cell structure (Z8_SLOTTED frame, NICHES_HIGH_MIG), or the different MUT/MKL route to the needed bytes.
- **What it explains.** The MUT-vs-MKL composition difference between cells: world mutation reaches opcodes only in ffa6.
- **Confidence.** High for the mechanism (from code). Moderate for "coincidental": copy-error supply per lineage-epoch has not been measured per cell.
- **Strongest objection.** The *useful* variants (e.g. creating an `LD DE,nn` opcode) might still need world mutation of opcode positions in a specific frame. That is unknown.
- **Next questions.**
  - Measure the copy-error count per occupied site-epoch in both cells; X-MAT replays have ctx.copy_errors.
  - Decompose the 8 events' state-free-defining bytes into MUT vs MKL origin.
  - Revise U-T5 and the T1 text.

### N5: the cell axis (CF vs C7). Does mutation-operator access to opcodes let founders escape self-poisoning? (Nestor) Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Question.**
  - S1: the interaction map cannot see the cell axis; CARRY establishment is 0.36 (CF) vs 0.16 (C7).
  - C-A3: internalization ffa6 7 vs 7ae3 1.
  - Code reading: niches only gate the task environment, pairing is global, and QD kills nothing. The only reproductive difference is that Z8_SLOTTED mutation reaches instruction starts, while C7 OPERAND never does.
- **Evidence.** `inference_saturation_wave2/N5_cell_axis/escape.py` and `escape.json`.
  - 16 C-ZERO-SPECIFIC donors × 80 single world-mutation mutants per cell operator.
  - Scored for copying from the genome's own carried registers.
  - Exact map_common cell construction, dense VM.
- **Result.**
  - Poisoned donors (12): escape mutants **CF 13/960 vs C7 4/960** (about 3x; Fisher one-sided p ≈ 0.02). The escapes come from donors 7, 8, 13 and 14.
  - Self-OK donors stay OK about 56-89% of the time in both cells.
- **Quantitative check: it fails for establishment.** At a world-mutation rate of about 0.13 per genome per epoch, a ~1% escape rate gives about 0.1-0.2% escape per epoch. That is negligible in a 3-10 epoch establishment window, so it **cannot explain** the CARRY 0.36 vs 0.16 difference.
  - It **could** contribute over the hundreds to thousands of epochs of post-takeover internalization, in the ffa6 > 7ae3 direction. But N4 shows copy errors, which are cell-independent, dominate supply there.
- **Confidence.** High that the escape-rate difference is real but small. Moderate that it is not the establishment cause.
- **Strongest objection.** The map_common "C7/CF" cells are the BRIDGE construction (CF = 7ae3's cell with ffa6's representation and structure), not the exact ffa6 cell. The C-A3 ffa6 cell may differ further.
- **Unresolved.** The cell-axis establishment difference remains unexplained. Remaining candidates: the founder's *own* world mutations destroying its copy setup more or less often under each operator (degradation, not escape); a migration side effect on validation/COEVO_ENV spec; something not yet seen in the code.
- **Next question.** Measure the per-mutation *destruction* rate of zero-context competence under each operator; static and cheap.

### N6 + N7: the cell axis has no static mechanism, and the niche component has none in code (Nestor). Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Question.** What makes CF establish more than C7 (BRIDGE PERSIST: C7 4/32, C7S 9/32, C7N 10/32, CF 14/32; S1's CARRY 0.16 vs 0.36)?
- **Evidence.**
  - N6 `destroy.py`: per-mutation destruction of zero-context copying.
  - N7 `field.py`: founder fate against background pools aged 0/60/240 mutations under each operator, 1,920 interactions per condition.
  - A code read of every `niche` use in world.py.
- **Results.**
  - **N6, destruction.** C7 168/1,200 (14%) vs CF 217/1,200 (18%). CF destroys *more*, which is the wrong direction to explain the CF advantage.
  - **N7, background field.** Founder loss 0.096-0.122 and conversion 0.448-0.461 for both operators at every pool age. There is no field difference.
  - **N5, escape.** CF is 3x C7 but tiny (≈ 1%/mutation), negligible inside the 3-10 epoch establishment window.
  - **Code: niches are reproductively inert in these cells.**
    - Niches change only the COEVO_ENV task spec, the QD bookkeeping map, `here` tags, and migration RNG draws.
    - Pairing is global (`_pair_epoch` shuffles all alive organisms).
    - QD pressure kills nothing; nothing dies, and no reaping happens on the pair tape.
    - So C7N vs C7 (10/32 vs 4/32, Fisher p ≈ 0.06) has **no mechanism**. It is most plausibly a realization difference: migration consumes world-RNG draws, so the runs are not paired.
- **Reading.** The BRIDGE / S1 "cell axis" may be largely noise plus a weak operator effect. The S1 map's "blindness to the cell axis" is not evidence against the map. Dossier D already rated M6 ("cell axes raise baseline establishment") as Weak; this strengthens that grading.
- **Confidence.** Moderate. The static probes cover the founder only; the founder's children are mutated in-world too.
- **Strongest objection.** C7S alone (operator only) also rose, 4 → 9/32. If both single-axis changes are realizations, the CF 14/32 combination is still p ≈ 0.006 against C7. A real interaction effect that the static probes miss cannot be excluded.
- **Next question.** A paired-RNG re-run (same seeds; niche RNG draws taken from a private stream) would decide whether niches matter. That is cheap but it is a world run: a design item, not executed.

### N8: hypothesis on why internalization is transient (Nestor, reasoning from code). Open
- **Mechanism, from code.**
  - Under the predecessor criterion, a copy onto a victim that is already ≥ 90% identical to the donor is **not** a birth (fid_self < 0.9 fails).
  - Under ATOMIC, a non-promoted half is restored.
  - So once one family saturates the field, reproduction among near-identical members is **invisible and inoperative**. Selection acts only through overwrites of victims that have drifted ≥ 10% from the copier.
- **Prediction.** Post-saturation selection strength scales with within-family diversity. With low diversity, state-free variants (made by copy errors) drift in and out. That gives transience, flicker such as 27000020, and the ffa6 27000052 total loss of competence while L = 1.0.
  - Corollary: selection for state-freedom is *strongest during takeover*, while victims are still foreign.
  - That fits the data: 8/8 events appear at or shortly after takeover, and pre-takeover foreign bytes are purged.
- **Testable on existing data?** Partly. In X-MAT replay tags, whether a site's MUT/MKL composition correlates with free-share volatility needs per-site data that was not stored. The P-11 event rate per epoch after saturation is in X-RUNAWAY series (about 90-100 per epoch). What matters is how many of those are true content changes.
- **Next question.** Measure, in one instrumented replay, the fraction of post-saturation accepted births whose victim differed by ≥ 10% (all, by definition) vs the rate of rejected near-kin copies. The ratio gives the effective selection rate. A design item.

### N9: static decomposition of ATOMIC. The world's fidelity gate carries the heredity (Nestor). Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Question.**
  - What in the composite ATOMIC rule produces C-ATOMIC C1 (46/80 vs 1/80)?
  - Can the single-interaction map predict BASE as well as ATOMIC? RT B7 found ADV2's BASE prediction (0.26) missed the observed 0.03.
- **Evidence.** `inference_saturation_wave2/N9_atomic_decomp/wdecomp.py` and `wdecomp.json`.
  - 7ae3 in its own cell, stock VM, copy errors at the cell rate.
  - 1,500 interactions per context against uniform random partners, founder side 50/50.
  - Four write-back rules applied to the same post-interaction tape.
- **Result (P_est = Galton-Watson survival from the offspring law).**

  | rule | ZERO context | RANDOM context |
  |---|---|---|
  | BASE | m 0.965 → **P_est 0.00** | m 0.97 → 0.00 |
  | ATOMIC | m 1.18 → **0.50** | 1.18 → 0.51 |
  | ATOMIC + self-writes kept | 0.38 | 0.29 |
  | WRITE-GATED (keep a half if the partner wrote ≥ n/4; no fidelity clause) | **0.003** | 0.008 |

  - Observed: BASE about 0.03 (4/144); ATOMIC 0.52 pooled, 0.575 in C-ATOMIC C1.
  - **The map predicts both regimes for 7ae3.** RT B7's "BASE miss" came from omitting copy errors and the founder's own erosion. With BASE semantics applied to the founder's own half, BASE is subcritical.
- **Reading.**
  - About 75% of ATOMIC's establishment benefit comes from the **fidelity clause**: the world keeps a written half only if it is a ≥ 0.9 template of the writer. The rest comes from discarding self-writes.
  - Keeping all heavily written halves without the fidelity clause is as bad as BASE.
  - ADV1's K3 deflationary claim is supported statically: **the world's detector, not the organism, maintains copy fidelity** under ATOMIC. Every post-09-25 heredity result inherits this.
- **Confidence.** Moderate-high for 7ae3 (static, uniform random partners). It is a single genome.
- **Strongest objection.** In-world partners are not uniform random, and copies interact with copies. The Galton-Watson model ignores frequency dependence after the first generations.
- **Next questions.**
  - Run the same decomposition on S1's 16 donors × policies. Does WRITE-GATED collapse for all of them?
  - Frozen prediction for K3: a WRITE-GATED arm of C-ATOMIC would give ≤ 5/80 runaways. A design item, with a static prediction now on record.

### N10: the N9 decomposition across 16 dense panel donors (Nestor). Closed before 00:42Z (clock-checked; earlier guessed times removed)
- **Evidence.** `N9_atomic_decomp/panel_decomp.py` and `panel_decomp.json`.
  - C-ZERO-SPECIFIC donors, CF cell, dense VM, ZERO context, copy errors at the cell rate.
  - 600 interactions per donor.
  - Compared against the observed ZERO S5 (3 runs per donor).
- **Result.**
  - BASE is subcritical or near-critical for every donor: m 0.65-1.05, P ≈ 0 except 2 donors at ≤ 0.10. BASE never establishes, as the world shows.
  - ATOMIC predicts P 0.40-1.00, mean 0.73. The observed ZERO mean is 0.54 (26/48).
  - WRITE-GATED drops the mean to 0.19; 4 donors fall to 0.
  - **Within-ZERO rank correlation with observed: ρ ≈ 0 for every rule** (−0.08, −0.01, 0.07). The high-predicted failures are donors 0, 2 and 7, which S1 identified as sterile-copy donors.
- **Reading.**
  - The world's write-back rule sets the regime: BASE ≈ 0, ATOMIC about 0.5-0.7. The fidelity clause is the dominant component across the panel, not just for 7ae3.
  - **Per-donor rank within a regime needs the two-step "do the copies copy" term.** Write-back semantics do not supply it. This confirms S1 from a different construction.
- **Confidence.** Moderate-high.
- **Next questions.**
  - Combine N9's W semantics with S1's children's law. Does a two-step + correct-W map recover the within-ZERO ranks? S1's post-hoc repair already did (ρ 0.81). Its out-of-sample test (S1b) passed on W1 donors, where the content was mostly self-poisoning.
  - An out-of-sample test of the two-step term within ZERO specifically: which panel? Fresh donors would need new acquisitions (a world run), so this is a design item.


> Correction (00:42Z, from `date -u`): earlier entries carried invented 'Closed HH:MMZ' times that ran ahead of the
> clock. They are replaced. From now on, times come from `date -u` only (the same lesson as Harmonia #1057's WORK_STATE note).

### W2-9: statistical review of the CONFIRMED verdicts (worker; report saved by Nestor). Closed by 00:55Z (clock-checked at save)
- **Result.**
  - All 20 frozen statistics reproduce exactly.
  - ROBUST: 8 decisions in 7 experiments.
  - FRAGILE: SEARCH, RUNAWAY, CORE, A3.
  - ARTIFACT-RISK: H1R, X-MAT, and C-ZERO's reading.
  - Uninformative nulls: ENERGY_FOR_DEPTH, NORECOMB, ATOMIC C2. SWAP-ACQUIRE is a near-miss.
  - Expected false CONFIRMEDs about 0.02-0.05.
  - New: the C9-H1R 2×2 is degenerate **by design** (M = −I/2 always).
- **See** `W2-9_stats_review/REPORT.md`.
- **Attacked by Nestor: N11** (below) confirms the C-ZERO selection argument.

### N11: are the C-ZERO-SPECIFIC donors competent from 0x5A at all? (Nestor). Clock 00:58Z
- **Evidence.** `N5_cell_axis/const_screen.py` and `const_screen.json`. The 16 donors, dense CF cell, both sides, 20 random partners per entry state.
- **Result.**
  - ZERO-competent: 16/16.
  - 0x5A-competent: **2/16** (donors 1 and 15).
  - RANDOM-competent: 2/16 (the same two).
- **Reading.** C-ZERO-SPECIFIC's ZERO 26/48 vs CONST 2/48 is **largely built in by the zero-state donor screen**. 14 of 16 donors cannot copy from 0x5A at all, so CONST success was impossible for them. The 2 that can carry all non-zero successes, as D U4 and S1 had found.
  - The verdict's statistic is correct.
  - Its reading, "zero is special for establishment", is mostly a statement about the screen.
  - The independent support for zero-specialization is X-A3-FAIR's treatment-blind ruler: zero-competent donors are discovered first even in the 5A world, and are later replaced by K_ONLY. That is the claim to keep. C-ZERO should be cited as "establishment in the world the donors were screened for".
- **Confidence.** High.
- **Next questions.**
  - Re-score C-ZERO restricted to the 2 dual-competent donors: within-donor ZERO vs CONST.
  - Does any other P2/W1 contrast use a screen-selected panel in the same way? X-P2-REGSTATE and BRIDGE use similar panels.

### W2-5: historical error autopsy (worker; report saved by Nestor). Clock 00:50Z
- **Result.** 58 mistaken interpretations in 20 classes.
  - RCF (a ruler or guard that cannot fire or cannot refuse) is the most common class and recurred 15 times after its lesson.
  - Unit mismatch (label/run/event vs content/organism/genome) is the largest family.
  - Code repairs stopped their class; prose repairs moved it.
  - 9 checks, 37 tests passing. On real records they re-find C9-D16, the H1R identical pair, and D U1 8/23.
  - Sweep: live vulnerabilities in the BEE library (`prometheus/z80atlas`), Archaeon, Ananke W-U and cosmos ps1. Owners not yet notified.
- **Nestor attack/verify.** The x_task_gate Stage-0 defect is **confirmed in code** (CD = 0 by construction in EXTERNAL arms). The oid-provenance defect is downgraded to LOW: under ATOMIC, oid tracks content apart from mutation.
- **Action.** Filed `campaigns/npe-frontier-2026-09-30/x_task_gate/ERRATA_2026-10-01_DO_NOT_DISPATCH_AS_FROZEN.md`. Aporia notified.
- **Next questions.**
  - Can a genome that is both a copier and task-competent be constructed? Decide statically.
  - Notify the cross-seat owners. A short comms note in the handoff; I do not fix other seats' code.

### N8 (revisited): the "invisible selection after saturation" mechanism is contradicted by existing data (Nestor). Clock 00:56Z
- **Attack.** N8 proposed that once a family saturates the field, overwrites among near-identical kin are not accepted births, so selection stops and state-freedom drifts (transience).
- **Evidence against.**
  - `c9x/x_runaway/RESULTS.json`: after saturation (epoch ≥ 160), P-11 events keep accruing at about 90-100 per epoch for 1,800 epochs. There are 128 pairs per epoch.
  - The dominant genome holds only 3-12% of the population, with identity to the implant ≈ 0.
  - So the family is **diverse**, and accepted overwrites among diverged kin are frequent. Selection events do not vanish.
- **Status.** N8's mechanism is **REFUTED for the BASE / 7ae3 / splice-off runaways**. It is untested under C-A3's dense + ATOMIC conditions, where the family may be less diverse, but there is no positive evidence for it.
- **What remains.** Why state-freedom is transient in half the C-A3 events.
- **New candidate.** In a diverse kin field, the newborn's inherited context is a *kin* copier's post-execution registers. A zero-dependent copier is poisoned by a kin context unless the kin's advance Δ ≡ 0. So selection *for* state-freedom should be strong, which deepens the transience puzzle rather than resolving it.
- **Next question.** In C-A3 event replays, measure the conversion rate of state-free vs non-free members *in the realized kin context* (static, from replay snapshots). Without genomes on disk this needs a replay: a design item.

### W2-1: contradiction mine (worker; report saved by Nestor). written before 00:59Z (clock-checked)
- **Result.**
  - Of 13 conclusions: 3 SURVIVE, 7 WEAKENED, 1 UNDECIDABLE. C4 survives with its HL = 0 geometry half undecidable; C13 is weakened by S3.
  - BROKEN parts: C10's depth-gap premise, C11's "dominate" and side-0 marker, C7's magnet dismissal.
  - **Biggest correction:** X-A3-FAIR's ZERO world (per-interaction register reset) is an existing no-payoff arm. State-free genomes appear and sweep there (0.11 vs 0.70 end share).
- **Nestor verification.**
  - `reset_axis.py` confirms ZERO resets both organisms before every interaction.
  - X-DD-STATE-RESET's endpoint was establishment, not state-freedom. So "the victim channel's only test was null" is true for establishment only.
- **Applied.** A WAVE-2 CORRECTIONS block, (a)-(i), at the top of the Wave-1 synthesis and handoff; targeted line fixes.
- **Self-correction.** **N3** explained the depth gap as early establishment plus record growth. The gap premise is false: omitted arms contain runs inside it. N3's record-growth shape (stepwise plateaus) still stands. Its gap explanation is withdrawn, and replaced by W2-1's turnover correlation (depth vs time since first donor, ρ = 0.74).
- **Next questions.**
  - Own vs inherited carried channel: a world rule resetting only newborn registers, combined with STATE_FREE checkpoints. A design item.
  - k = 4 distinct vs identical founders: the kin-context T4(a) datum (W2-12 running).
  - The HL ≡ 0 PATTERN control.

### N12: which register bits does "ZERO" supply? The HL ≡ 0 control W2-1 found missing (Nestor). written before 00:59Z (clock-checked)
- **Evidence.** `N5_cell_axis/pattern_screen.py` and `pattern_screen.json`.
  - The 16 C-ZERO-SPECIFIC donors, dense CF cell, both sides, 12 random partners per pattern.
  - Register order B C D E H L (HL) A, as in `reset_axis`.
- **Result: competent donors out of 16.**

  | entry pattern | competent |
  |---|---|
  | ZERO | 15 |
  | HL = 0x8080, rest 0 (phase 0 mod 128, different page) | **15** |
  | A = 0x5A only | **15** |
  | BC = 0x5A only | 11 |
  | L = 0x01 (phase 1) | 11 |
  | DE = 0x5A only | 9 |
  | all 0x5A except HL phase 0 | **7** |
  | CONST 0x5A | **2** |

- **Reading.**
  - ZERO supplies mainly the **HL pointer phase**. The page byte is irrelevant, which confirms that only 7 address bits matter.
  - Restoring HL phase 0 alone, with everything else at 0x5A, lifts CONST from 2 to 7 donors.
  - DE (destination) and BC (count) are supplied by zero for a minority, 5-7 donors.
  - The accumulator is irrelevant.
  - **W2-1's C4 "geometry undecidable" is now decided: SUPPORTED-PARTIAL.** HL = own start (phase 0) is the main thing zero supplies, but not the only one.
- **Confidence.** High (static, exact code path), for this panel.
- **Next questions.**
  - Does a PATTERN world with H = L = 0x80 and everything else 0x5A rescue in-world establishment toward ZERO levels? A design item; the static prediction is about 7/16 vs 2/16 donors.

### N13: C-A3's "competent" counts use the wrong context for the world they describe (Nestor, reasoning). written before 00:59Z (clock-checked)
- **Observation (W2-1).** L takes over in 5/16 takeovers with ≤ 10 zero-screen-competent genomes. 27000053 reaches L = 1.0 with ≤ 4, at depth 11. 4/16 takeovers end with 0 competent genomes while L stays at 0.66-1.0.
- **Mechanism, from code and prior results.**
  - C-A3's per-checkpoint `competent` uses `run_de.competent`: zero entry state, blank partner.
  - The world is CARRIED: sites keep their registers, and newborns run in the victim's leftover context.
  - S1b showed first-donor fate is decided by copying from *carried* state.
  - So the organisms actually reproducing in a CARRIED world can be carried-state copiers that fail the zero-context screen. They are invisible to the `competent`, `free` and `free_in_L` counts. This is dossier D's U8 ("heredity without competence") operating inside C-A3.
- **Consequences.**
  - (i) C-A3's state-free share is measured on the *zero-competent subset* of the reproducing population, which is not the population that reproduces.
  - (ii) "Transient" events may partly be the zero-competent subset fluctuating while carried-state copiers carry the lineage.
  - (iii) ffa6 27000052's "competence went to 0 while L = 1.0" may be a ruler event, not a functional collapse.
- **Prediction.** In replay snapshots of takeover-without-competence runs, most L members convert partners from their realized carried context and fail the zero screen. A design item: one replay with per-checkpoint carried-context conversion.
- **Confidence.** Moderate. This is reasoning consistent with U8, S1b and W2-1, untested on these runs.
- **Class.** A single-context-point ruler (W2-5 class SCP) inside a CONFIRMED verdict's own counts.

### W2-6 (theory tournament), W2-2 (near-miss) and W2-8 (semantics audit): reports saved by Nestor. written before 01:01Z (clock-checked)
- **W2-6.**
  - Six theories collapse into **F, the supplied rewrite field**: content T3, rules T2+T5, dynamics T7+T1, within an iterated T6.
  - T4 is eliminated as a theory. R = T4(a) (home advantage) and T4(c′) (generic evolved epistasis) remain open.
  - E2 as designed decides by its counting unit.
  - The cell axis is at the noise floor.
  - Erosion is the iterated map under BASE.
- **W2-2.**
  - Under BASE, bursts follow one subcritical individual law (m_c 0.77), but runaways are about 100x in excess with an empty gap: a **second regime**.
  - ATOMIC is quantitative.
  - cb7f is very probably takeover without depth.
  - C-A3 near-misses are mostly artifacts; 27000053 is the one genuine near-miss.
  - A byte-42 sweep occurs after takeover.
  - Best early warning: births in epochs 11-15.
- **W2-8.** 15 code defects, 4 INVALIDATES.
  - D1: cross-niche cache.
  - D2: C9 H3 A ≡ B, so H3 could not be positive.
  - D3: 7 of 12 pressures identical on the pair tape; "native QD" = no pressure.
  - D4: SLOTTED ignores the operator; ffa6 has about 8x supply, 87% on opcodes.
  - D5: anticheat guards cannot fire.
  - D10: C-A3 counts 8 → 4 → 3.
  - X-TASK-GATE: D1, D6, D15, D14.
- **Contradictions found between workers (Nestor):**
  1. **The BASE map models disagree about 600x.** W2-6's c7c *over*predicts BASE (0.175 vs 0.03); W2-2's h1 *under*predicts BASE runaways (0.0003 vs 0.031). Sent to W2-14 for reconciliation, top priority.
  2. **Founder independence.** W2-6 says "decided for T7" (joint p 0.108). W2-1 and W2-5 say the multi-founder excess is real (k = 1 batches homogeneous; C-CRITICAL-MASS own-data p 0.005-0.014). W2-12 is assigned.
  3. **N4 ("copy errors dominate supply, so the 8x ≈ 7x match is coincidental") is revised by D4.** World-mutation supply in ffa6 really is about 8x 7ae3's and hits opcodes 87% of the time. So the operator asymmetry is a real candidate cause, and every 7ae3-vs-ffa6 contrast is confounded by it. N4's copy-error mechanism (MKL dominance in 7ae3) still stands; its "coincidental" verdict is withdrawn and becomes "confounded and undecided".
- **Actions.** X-TASK-GATE erratum extended with W2-8's D1/D6/D15/D7/D9/D13/D14. C9 H3 → INVALID and C-A3 final-checkpoint re-read are proposed for FINDINGS in the Wave-2 handoff.

### N14: reconciling W2-8 D4 (the SLOTTED operator confound) with N4-N7 (Nestor, reasoning from code). written before 01:01Z (clock-checked)
- **Code fact (world.py:516-551).**
  - The per-genome world-mutation *attempt* rate is the same in both cells: about 64 × rate per epoch.
  - In 7ae3 (Z8_64, OPERAND), attempts at instruction-start bytes are **skipped**. About 52 of 64 positions are instruction starts, so only about 12 positions are mutable. That gives about 5-7x fewer effective world mutations: ARC3's 34 vs 239.
  - In ffa6 (SLOTTED), the slot-offset rule ignores the operator, and 87% of edits hit opcodes (W2-8 D4).
- **What N4 got wrong.** N4 called the 8x ≈ 7x hazard agreement "likely coincidental", because copy errors dominate supply in runaways. **That is withdrawn.** World-mutation supply differs about 7x between cells and reaches opcodes only in ffa6. It is a live candidate for the ffa6 > 7ae3 internalization difference, along with copy errors, which are present in both cells. Status: CONFOUNDED / UNDECIDED. N4's other point stands: 7ae3's state-free bytes were built by copy errors (MKL 91%).
- **Per-epoch establishment arithmetic** (CF uses the full rate, C7 about 1/7 of it):

  | effect | CF | C7 | implication |
  |---|---|---|---|
  | escape from self-poisoning (N5) | ≈ 0.128 × 1.35% ≈ 0.17%/epoch | ≈ 0.018 × 0.42% ≈ 0.008%/epoch | ≈ 20x CF advantage, but only ≈ 1.7% over a 10-epoch window: too small |
  | destruction of zero-context copying (N6) | ≈ 0.128 × 18% ≈ 2.3%/epoch | ≈ 0.018 × 14% ≈ 0.26%/epoch | predicts CF establishes **less** |

- **Net.** The operator confound does not explain CF's higher establishment. That agrees with W2-6 C9 (the cell axis is at the noise floor; the code-inert structure factor shows an equal effect) and with N6/N7.
- **What D4 does affect.** Long-horizon contrasts: internalization over thousands of epochs, MUT composition, X-MAT tag mixes. Every 7ae3-vs-ffa6 contrast must name it.
- **Confidence.** Moderate-high (code-derived, per-epoch arithmetic). Establishment-window effects are second-order.


### N15: kin pairing protects against BASE erosion. A candidate population-level mechanism for W2-2's "second regime" (Nestor). Written at 01:05Z (clock)
- **Evidence.** `N15_kin_erosion/kin.py`, `kin_fine.py` (+ .json).
  - 7ae3, own cell, BASE write-back, copy errors on.
  - The founder is chained through successive interactions, carrying its BASE-written content and its registers.
  - Partners are exact copies of the founder's current content with probability q, otherwise fresh random genomes.
- **Result, 12-step lives (150 lives).**

  | q | founder identity, step 1 → 12 | conversions per step at the end | still a copier at step 12 |
  |---|---|---|---|
  | 0 | 0.66 → 0.08 | 0.013 | 0.02 |
  | 1 (all kin) | 0.99 → 0.87 | ≈ 0.40 | 0.52 |

  Intermediate q falls in between.
- **Result, 20-step lives (300 lives): mean lifetime conversions by q.**
  - q 0 → 1.20
  - q 0.02 → 1.44
  - q 0.04 → 1.52
  - q 0.06 → 1.53
  - q 0.10 → 1.60
  - q 0.15 → 1.74

  Absolute values are inflated, because overwritten individuals are not removed here. The relative boost is about 25-30% at q 0.04-0.06, i.e. 10-15 kin among 256.
- **Reading.**
  - Under BASE, erosion comes from non-kin partners. A copy written onto an identical copy changes nothing.
  - Lineage density raises the kin-pairing fraction (q ≈ N/256), which lowers erosion and raises lifetime fecundity. That is **positive density dependence (an Allee effect)**.
  - W2-2's single-individual BASE law is near-critical (m ≈ 0.93). A 25-30% boost at about 10-15 members plausibly crosses 1, giving a **size threshold**. That fits X-TICKET: win given ≥ 8 members 7/9, ≥ 16 5/5, and the empty 27-162 gap.
  - It is a **population-level term absent from the single-individual law**, but it is still inside F: the iterated map against the *realized* partner distribution, not uniform random partners.
- **Consistency checks.**
  - U-W5 (no erosion change up to 15 members, ρ 0.02) does not contradict this. At N ≤ 15, q ≤ 6%, and the per-interaction erosion change is small. The effect accumulates over a lifetime.
  - Under ATOMIC (no erosion) the mechanism predicts no Allee effect, and ATOMIC is quantitative (W2-2). That agrees.
- **Confidence.** Moderate. The mechanism and direction are clear; the threshold location is approximate.
- **Strongest objection.**
  - Individuals were not killed on overwrite.
  - Kin partners here are exact copies of the *current* founder. Real kin are diverged copies, and the protection drops with divergence.
  - W2-2's h2 found that lineage-*touched* partners were worse. Exact kin and touched partners differ.
- **Next questions.**
  - Fold q(N) into W2-2's branching law and predict the runaway fraction and the gap. W2-14 is working on this.
  - Test protection against diverged kin (1, 3, 8 byte differences).


### W2-3 (no-vocabulary frames): report saved, plus a collision with N15 resolved (Nestor). Written at 01:07Z (clock)
- **W2-3 result.** The merged "labelled site field + position-anchored ring operators" frame passed three tests:
  1. The victim magnet is an integrated per-site hazard: 0.60 / 0.43, within the record bounds; LDIR knockout 0/60. This **independently confirms N1.**
  2. BASE is *critical* by ring geometry (m ≈ 1.0). The existing depth tail follows 1/d with no free parameter (dAIC 133); with the splice on it turns geometric.
  3. X-TICKET activity is age-structured (0.69 → 0 by age 8; R0 ≈ 1.04). There is **no Allee (n²) term at n ≤ 40**.
- **Collision with N15** ("kin pairing protects, so a density-dependent second regime"). Resolved as follows:
  - W2-3's K5 rejects any density term **at n ≤ 40**.
  - N15's own numbers predict only a modest boost at q ≤ 0.15 (N ≤ 38). The X-TICKET pre-takeoff range sits there, so the two results do not conflict.
  - N15's mechanism is real (static), but it can only matter at **larger N**. It is therefore a candidate for W2-3's open puzzle: *why the critical regime ends near depth 20, with 16/19 runs past d = 22 reaching ≥ 161.*
  - Revised claim: under BASE, early dynamics are critical branching (W2-3); a late density-dependent escape via kin protection (N15) is a hypothesis for the d ≈ 20 departure, not for the early threshold.
  - **Withdrawn from N15:** the link to "win given ≥ 8 members". W2-3 shows X-TICKET lineage size mostly counts inactive labels.
- **Reconciling W2-2 and W2-3 on criticality.** W2-2's individual law has m 0.93 (all births), m_c 0.77 (certified). W2-3's corpus mean is m_BASE 1.02/0.99, and 7ae3 sits around 1. Both are "near-critical". The 1/d tail favours critical. W2-2's "100x excess of runaways over the individual law" becomes "the excess beyond critical branching above d ≈ 20". The same open puzzle, stated more precisely.
- **Corrections from W2-3 for the record:**
  - C-CORE positions 24/53 are mutable in place (ED second bytes), so "opcode-immune core" is half wrong.
  - U-W7 is exact only for side-1 writers.
  - "Erosion brake" should read "one-sided op unmakes its carrier at the other side".
  - X-TICKET "lineage size" mostly counts inactive labels.
- **Next question.** N15b at larger N: does kin protection make R0 > 1 once q reaches about 0.1-0.3, and is that the d ≈ 20 departure? W2-14 is building a field process with realized partners and should show it.


### N16: attack on W2-3 K5 ("age-structured, no Allee"). Nestor, code read, written at 01:11Z (clock)
- **Question.** Does K5 really show per-site activity declining with age and no density term?
- **Evidence.** `W2-3_no_vocabulary/k5b_age_profile.py:20-37` and `k5_kinetic_order.py`. The data are run-level trajectories `traj = (n, alive, cumulative births)` with no per-site identity. The "young" covariate is `cb - cb(t-K)`, which is **the run's own births over the last K epochs**. The age classes are cut from those lagged birth counts.
- **Inference.**
  1. The "age-structured" model is a **self-exciting (Hawkes/AR) model of the birth series**, not an age model. It wins by AIC over b·n and b·n + c·n² for any bursty series, whatever the cause.
  2. Aggregate trajectories cannot attribute a birth to a site's age. Suppose one old, persistently active site writes every epoch. Its products would appear as "young", and its births would be credited to youth.
  3. So **the 0.687 coefficient is a self-excitation coefficient, not a per-site rate.** The "2x the single-call rate" puzzle in W2-3 is therefore an estimator artifact, not physics. The puzzle dissolves.
  4. "c → 0 once age is added" does not show the absence of a density term. A lagged-births regressor absorbs any density effect that acts through recent births.
- **What survives.**
  - **Age decline is independently supported by W2-2's h1 individual law:** 93% of births at age ≤ 6, built from single-interaction lives and so not aggregate-confounded.
  - **"No Allee at n ≤ 40" is DOWNGRADED from "rejected" to "not detected by an unidentifiable test".**
- **Confidence.** High that the K5 estimator is confounded (by reading the code). Moderate that the age decline is real (via W2-2).
- **Strongest objection.** K5b's "winners only" check removes run-level heterogeneity, but not within-run burstiness of a single site.
- **Unresolved.** Is there a density or kin term at n ≤ 40? Only per-site tracking can settle it (W2-2-EW snapshots or an E9-style occupancy replay).
- **Next.** Add to the W2-2-EW spec: record a per-site write log (writer oid, target oid, epoch), so that age and density are identifiable. This is a reusable infrastructure point: **aggregate trajectories cannot carry age claims.**
- **Effect on the N15/W2-3 resolution above.** The reconciliation still holds, but the "no Allee at n ≤ 40" premise is weaker. N15's kin protection could act at small n too. It is undetermined either way.


### N17: why are "essential" 7ae3 positions 30/34/49 lost in C-CORE runaways? (Nestor, written at 01:19Z (clock))
- **Question.** W2-3 K1 called positions 30/34/49 essential (E about 0.67), yet founder material there is lost in 24/27, 26/27 and 27/27 C-CORE runaways.
- **Evidence.**
  - Script and data: `N17_setter_turnover/scan.py` and `scan.json`.
  - Design: a full 256-value substitution at positions 23, 30, 34, 49 and 52; 40 random partners; ZERO and RAND contexts; both sides; copy errors off; 24 s wall time.
- **Results.**
  1. **The founder converts ONLY from side 1:** 0.80 ZERO, 0.775 RAND. Side 0 gives 0.
  2. **Position 30 (C6, ADD A,n) is NOT essential.** 198/255 substitutes are at or above the wildtype under ZERO, and only 22 are dead. K1's E = 0.67 came from **3 sampled values** (KOV = 3). That is a ruler artifact, of the small-sample kind.
  3. **Position 34 (7A, LD A,D) is truly essential.** 218/255 substitutes are dead. Its founder-tag retention (0.04) nonetheless sits at the turnover background (non-core positions are about 0.1).
  4. **Position 49 (66, LD H,(HL)): a single-byte SIDE SWITCH.** 0x59 (LD E,C) and 0x5C (LD E,H) give side-0 conversion **1.0** and side-1 conversion **0**, in both contexts. 219/255 other substitutes keep side-1 function under ZERO.
  5. Controls: positions 23 and 52 (SELF and LDIR first bytes) are dead under every substitute.
- **Inference.**
  - The "essential yet lost" puzzle is mostly dissolved. Founder-tag retention at 30, 34 and 49 is at the run-wide turnover background (about 0.1), so they are not *specifically* lost. Only the SELF and LDIR world-op bytes rise above background, which is consistent with C-CORE.
  - K1's essentiality vector is too coarse (3 values per position) to rank positions.
  - New: one byte separates a side-1 copier from a side-0 copier. A side-0 copier runs first and is not exposed to the side-0 wrap hijack (W2-10). This is a candidate fitter morph and a candidate for the departure near depth 20. Passed to W2-17.
- **Confidence.**
  - High for the scan numbers.
  - Moderate for "background turnover".
  - Low for the side-switch mattering in the world.
- **Strongest objection.**
  - `freq` is the founder *tag*, not the byte value. A value-preserving rewrite (through a register path such as LD (BC),A at 42) would also read as "lost".
  - Final-population genomes are not stored in the C-CORE records, so the value at 34/49 cannot be checked from disk.
- **Unresolved.** Whether runaways actually carry 49 = 59/5C.
- **Next.**
  - W2-17 is to measure m for the 49→5C variant and to check any runaway snapshots.
  - Any future C-CORE-like run should store the final consensus genome bytes, not only tag frequencies (instrument note).


### W2-15: defect × verdict impact matrix (report saved; Nestor attack). Written at 01:22Z (clock)
- **Result.**
  - Matrix: 95 verdicts × 17 defects.
  - **Flip:** C9-H3 NOT_DEMONSTRATED → INVALID (D2, D1 and D3 each suffice). X-H3-FLOW → UNINFORMATIVE.
  - **No CONFIRMED verdict flips.**
  - **22 relabels.** The main ones:
    - C-A3 → CONFIRMED-FRAGILE (4 persistent events = the bar; cell split 3:1);
    - C9-H1R → DEGENERATE;
    - C-ZERO-SPECIFIC → run-level only;
    - X-A3-WITHDRAW → CEILING NULL;
    - X-MAT → 4 persistent + 4 transient. On 7ae3 alone it is ENDOGENOUS under either convention.
  - **D1 and D9 reach no heredity verdict**, because comp does nothing in the QD pair cells.
  - D12 re-scored: C-DENSE-COPY unaffected; C-STATELESS-FFA6 B+ but survives (cite the unconditional p = 2.3e-6).
  - 23 FINDINGS line-ranges listed.
- **Nestor attack.**
  1. **The weakest INV cell is X-H1-GRADIENT.** It rests on an un-rescored held ≈ 0.9 vs an expected 0.5. This is decidable statically, so W2-19 is assigned to re-score on fresh seeds. The same applies to D8 vs E-3's depth-2 runs.
  2. **"D1 reaches no heredity verdict" depends on `_reap` being unreachable on the pair tape.** That is consistent with W2-8 D3 and with my own read of `_pair_epoch` (no comp read except under TASK_GATED / MINIMAL_CRITERION). Accepted.
  3. **The matrix omits the N16/N17 corrections**, which are W2-3-level and not FINDINGS verdicts. W2-18 is refocused to cover residual narrative claims plus an adversarial pass over W2-15's relabels, to avoid duplication.
- **Confidence.** High for the flip and the D10/D12 numbers. Moderate for H1-GRADIENT pending W2-19.
- **Strongest objection.** Breadth invites over-flagging (W-cells). NA was assigned by applicability rules while reading.
- **Next.**
  - W2-19: H1 re-score and D8 vs E-3.
  - FINDINGS correction appendix at closing: dated proposals only; no frozen verdict is rewritten.


### W2-13: U1, chain length vs evolved epistasis (report saved; Nestor attack). Written at 01:24Z (clock)
- **Result.**
  - Strict synthetic lethality: evolved (EVO_SD) 3.71% vs never-evolved random-hit copiers (33 new, 1.8e-4 of 180k) 2.32%. Raw gap +1.39 pp, p = 0.048.
  - At matched executed pre-copy chain length (L_pre): c_EVO = +0.27 pp, CI [−0.90, +1.46], p_FL = 0.83. Length-matched 2.08% vs 2.32%; Mantel-Haenszel OR 1.08.
  - **T3 (chain length) is sufficient. T4(c′) (generic evolved epistasis) is not supported.**
  - The earlier evolved vs PLANT contrast (3.7% vs 0.45%) was mostly a length confound.
- **Effect on the theory tournament (W2-6).** T4(c′) was one of the two residuals left after T4 was eliminated. It is now **demoted to "not needed, not excluded"**: the CI upper bound is about the raw gap. **The only residual not yet absorbed into F is R = T4(a), home advantage.**
- **Nestor attack.**
  1. Selection on competence acts on random hits too, so "never evolved" means "not shaped by world dynamics beyond the screen". That is the right comparison for T4(c′).
  2. The consistently positive point estimates plus d > 0 are a pattern, not noise, until power says otherwise. W2-20 is assigned to enlarge the long-chain random stratum, with a pre-stated rule:
     - SUPPORTED if the CI lower bound is > 0;
     - SUFFICIENT if the upper bound is < 0.7 pp;
     - otherwise UNRESOLVED.
  3. **Reusable prior:** the competent random-hit rate in 7ae3 is 1.8e-4, matching minimal_prior. That is an independent check of the minimal-prior instrument.
- **Confidence.** Moderate.
- **Next.** W2-20.


### W2-16: side-1 copiers fail CVT-R (report saved; Nestor attack and cross-link). Written at 01:29Z (clock)
- **Result.**
  - Side-1 copiers are genuine replicators in isolation: 17/17 with no partner run; 1020/1020 good copies.
  - They fail because of execution order. The side-0 first mover wraps into the copier's offset 0 with non-FRESH registers and runs the copier's own LDIR as a smear (300/528 damage events).
  - They are also register-fragile: 1/17 register-independent, against 49/111 for side 0 (p = 0.0015).
  - CVT-R compounds this: p = 0.62 becomes about 0.15 acceptance (12/85).
  - Against side-0 copiers they transmit 0/340.
  - Single-seed CVT-R is a coin flip when p < 1. Two of the six recorded side-0 failures pass all 4 reseeds.
- **Cross-links (Nestor).**
  1. **The same physics appears three times.** The pc wrap at 63 → 64 makes every copier's entry point an entry point for its partner. It drives:
     - the foreign-cell magnet (N1);
     - the X-TICKET epoch-1 loss (N2);
     - the side-1 CVT failure (W2-16);
     - and it is W2-10's "SELF floor".

     This is plausibly **the most consequential single feature of NPE physics.** In the no-vocabulary frame, every half is code that either context can execute.
  2. **N17: a single-byte side switch, and a sweep prediction.**
     - The 7ae3 founder converts only from side 1 (0.80), yet it is register-robust (0.775 under random contexts). It is the structural exception.
     - Changing position 49 to 0x59 or 0x5C makes it a side-0 converter (1.0).
     - By W2-16, a side-0 copier is safe from the first-mover smear and destroys side-1 copiers on contact (340/340).
     - **Prediction: a side-0 morph sweeps once it arises.** This fits founder material at position 49 being lost in 27/27 C-CORE runaways. It is a concrete candidate for the departure near d ≈ 20 and for the BASE second regime. Sent to W2-17.
  3. **Hypothesis for the register asymmetry.**
     - A side-1 copier is entered at offset 0 as a *continuation of side-0 execution*, carrying side-0's registers.
     - A side-0 copier is entered only by the second mover after its own code has run.
     - The corpus side-1 copiers were screened from FRESH contexts and never had to tolerate foreign-register entry, so the asymmetry may be a sampling or screen effect.
     - Test: disassemble the setups (W2-16 next step 5).
- **Instrument consequences.**
  - CVT-R should be multi-seed, with a no-partner arm and a swapped-order arm.
  - P-11's side-1 rate measures the order hazard, not competence.
- **Confidence.** As in the report. Cross-link 2 is a hypothesis, with a moderate prior.


### W2-18: FINDINGS correction proposals (file written by the worker; Nestor note). Written at 01:33Z (clock)
- **Result.** `W2-18_findings_corrections/CORRECTION_PROPOSALS.md` has 17 proposal rows layered on the W2-15 matrix: 8 NEW, 9 ADJUSTED. The new ones that matter most:
  - **P01, an unwired factor.** 90/334 and 81/304 of the A-3 read-order pairs sit in COEVO_ENV cells. There the declared read order reaches the scorer only at the first validation, and its effect there is about 0. In the 467 pairs where the factor is wired, the effect is +0.13 / −0.10.
  - **P02, INVALID clause.** E-9 H1R's "harmless when the cue is free" compares two identical arms (0.1972 = 0.1972; 60/60 seeds), which breaks FINDINGS' own lesson 9. The gated + paid-cue fact (0/60) stands.
  - **P03.** X-A3-WITHDRAW's "not sorting": the robust share jumps 0.22 → 0.96 between epochs 300 and 400, which looks like a sweep of members already present.
  - **P04.** The 16000006 path "lost and regained" is scored by a flickering 20-draw screen.
  - **P08.** Lesson 1, "every test ships with a negative control", is false in practice: the cannot-fire class recurred 15 times after it.
  - **P11.** In C-ZERO, every CONST/RANDOM success comes from donors 1 and 15. Within those donors: ZERO 1/6, CONST 2/6, RANDOM 3/6.
  - **P14.** W2-15 over-flags X-H1-GRADIENT; it needs a re-run (W2-19 is assigned).
  - **P16.** Three proposed lessons:
    - screen context must match the world;
    - aggregate trajectories cannot carry per-site age claims;
    - each declared factor must be shown to reach the scorer.
- **Confidence.**
  - high: P01, P02, P05a, P08, P09, P11;
  - moderate: P03, P04, P13;
  - low: the size of P15.
- **Nestor note.**
  - These are **proposals**. FINDINGS frozen verdicts are not rewritten. At closing, a dated "Wave-2 audit: proposed corrections" appendix will point to W2-15 and W2-18.
  - P13 cites W2-12's *unreported draft* (pooled 798 single-founder runs, min p 0.105). It is not to be used until W2-12 reports.
