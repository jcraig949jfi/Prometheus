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

### W2-1: contradiction mine (worker; report saved by Nestor). Clock about 01:00Z
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

### N12: which register bits does "ZERO" supply? The HL ≡ 0 control W2-1 found missing (Nestor). Clock about 01:00Z
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

### N13: C-A3's "competent" counts use the wrong context for the world they describe (Nestor, reasoning). Clock about 01:02Z
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
