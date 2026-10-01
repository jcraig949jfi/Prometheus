# NPE mechanistic synthesis, 2026-09-30 (revision 2, after red-team review)

This is Nestor's inference harvest, done under the operator directive committed verbatim at
`roles/Nestor/prompts/2026-09-30_inference_harvest/` (c8023bde4).

**Inputs:**
- seven reader dossiers (`dossiers/A`–`G`), which reconstruct the NPE history from raw files;
- two independent adversaries (`adversaries/ADVERSARY_1_DEFLATIONARY.md`, `ADVERSARY_2_ONTOLOGY.md`), which were not shown Nestor's theories;
- two static forensics (`forensics/FORENSIC_FUNCTIONAL_CORE.md`, `FORENSIC_MAP_PREDICTS_OUTCOMES.md`);
- Nestor's own verification checks;
- a fresh-context red-team of revision 1 (`adversaries/REDTEAM_SYNTHESIS_REVIEW.md`). Its 7 blocking and 9 major findings were all accepted. §8 lists what changed.

**What was run.** No world campaign or evolution run. New numbers come from committed data, from single-genome or single-interaction VM calls, and from one exception: ADV2 ran a small toy population process built from single-interaction calls (256 sites, 300 epochs, 3 seeds × 2 genomes). That process is not `world.Runner`. It is cited only as illustrative (U-I6).

**Companion files:**
- NPE_COMPETING_THEORIES.md
- NPE_UNMINED_EVIDENCE.md (the U-xx codes)
- NPE_DECISIVE_EXPERIMENTS_NEXT.md
- BUILDER_EXPERIMENT_SPECS_PRIMITIVES.md
- INFERENCE_HARVEST_HANDOFF.md


> **WAVE-2 CORRECTIONS (2026-10-01; ledger `roles/Nestor/inference_saturation_wave2/INFERENCE_LEDGER.md`).** These supersede
> the corresponding text below.
>
> **(a) The cause of internalization.** "It pays because newborns inherit the victim's registers" is **withdrawn as stated**.
> - X-A3-FAIR's ZERO world, which resets all registers before every interaction, is an existing no-payoff arm (W2-1).
> - State-free genomes appear and sometimes sweep there too: 2/23 de novo majorities, one at 185/187. The end-of-run robust share
>   is 0.11 under ZERO vs 0.70 under CARRIED.
> - So **carried register state, the organism's own or inherited, raises prevalence about 6x, and payoff is not required for
>   appearance.**
> - Which carried channel matters (own post-execution state vs the victim's inherited state) is untested. X-DD-STATE-RESET's
>   null concerned establishment, not state-freedom.
>
> **(b) The side-0 switch is not a marker of state-freedom.** The genomes that state-free genomes replaced are side-0 copiers too
> (271/295 vs 432/433).
>
> **(c) "Dominate" is too strong for C-A3.** The event rule needs a single state-free genome. A state-free majority is reached in
> 4/8 events, 2/8 are single-genome blips, and 13 non-founder populations are already majority state-free when first sighted.
>
> **(d) The depth gap premise is false.** Omitted arms put runs inside 22–161: X-ATOMIC BASE has 44 and 50; ATOMIC runaways
> fall there in 8/36 and 6/47; C-A3 in 21/34. The turnover reading survives: depth vs time since first donor, ρ = 0.74.
>
> **(e) Founder independence is weakened.** The single-founder batches are homogeneous (p = 0.43), so the multi-founder excess at
> depth ≥ 5 is real (C-CRITICAL-MASS k = 4, 41/80 vs 29.3 expected, p = 0.005). It vanishes at the runaway endpoint.
>
> **(f) The foreign-cell magnet is plausibly explained** by a partner executing the founder's LDIR, compounded over the run
> (N1 / W2-1).
>
> **(g) T4(c) is dead.** S3 found no state-free-specific multi-site epistasis.
>
> **(h) C-ZERO-SPECIFIC's contrast is largely built in by its donor screen.** 14 of 16 donors cannot copy from 0x5A at all (N11).
>
> **(i) X-TASK-GATE must not be dispatched as frozen** (Stage 0 cannot exercise CD; see the erratum).
>
> **(j) "Establishment is decided within 3–10 epochs" (SYN:160, :243; U-T1) is withdrawn as worded.**
>
> **What the trace shows [W2-28].**
> - The figure is the range of the *latest first-copy epoch among established runs* in two arms. A third arm's maximum, 82
>   (BRIDGE PERSIST), was dropped from the summary.
> - Pooled over the 704 implanted-panel runs (C-ZERO-SPECIFIC, X-P2-BRIDGE, X-P2-REGSTATE; S5 judged at epoch 500):
>   - **failure is usually decided early:**
>     - 196 of 199 established runs made their first accepted founder copy by epoch 10;
>     - runs without one by then establish 3/48;
>     - runs that never copy establish 0/267;
>   - **success is not decided early:**
>     - P(S5 | first copy by epoch 10) = 196/389 = 0.50;
>     - P(S5 | certified grand-offspring birth by epoch 10) = 147/184 = 0.80.
> - Under BASE in X-TICKET, burst and runaway are indistinguishable before about epoch 10 (U-T2; W2-2). The 27th causal
>   birth falls at epochs 9–15 (W2-25 F2). Whether a burst becomes a runaway is settled by post-27 persistence at about
>   epochs 10–50.
>
> **Replacement for SYN:160:**
> > "An early first copy is close to necessary for establishment and far from sufficient. Of runs with a first founder copy
> > by epoch 10, 0.50 establish. Whether a BASE burst becomes a runaway is decided later, at epochs 10–50, by persistence."
>
> **Replacement for the SYN:243 table cell:**
> > "Early failure (no founder copy by epoch 10: 3/48 establish), partly the side-0 hijack in SELF-enabled cells. Success
> > after an early copy is about a coin flip (0.50). A two-generation single-interaction map predicts the policy pattern
> > and, post hoc, per-donor ranks."
>
> The handoff's identical wording (HANDOFF:115) needs the same change.
>
> **(k) "Critical" and "subcritical" are different readouts. Do not equate them (W2-25 F10).**
>
> | readout | value | source |
> |---|---|---|
> | per call, m_BASE | ≈ 1.0 (corpus mean 1.02/0.99; 7ae3 ≈ 1) | W2-3 K2 |
> | per call, founder against realized bank partners (halves with fidelity ≥ 0.9, any author) | 1.17 | N17e |
> | per call, founder, n = 400 RAND | 0.96 | N17 |
> | **lifetime** founder-certified m_c | **0.77**; all accepted births 0.93 | W2-2 h1 |
> | realized side-1 event-type fecundity | 0.80–0.89 | W2-17 a4 |
>
> **Reconciliation.**
> - Per call, the founder is near-critical at its first interaction.
> - BASE erosion then decays its conversion from 0.46 to 0.01 over 9 interactions (W2-6 C7b).
> - So its **lifetime** law is subcritical.
> - The 1/d depth tail is a *world-depth record statistic*: 4/13 depth ≥ 20 runs have only 0–2 founder births (W2-2). It
>   is not evidence of founder criticality, and it cannot separate one type from two (N18).
> - Under ATOMIC the lifetime law is supercritical: founder m_c 1.76, descendants 2.30 (W2-2).
>
> **Replacement for SYN:177's last sentence** ("It is not explained by a near-critical offspring mean"):
> > "Per call the founder is near-critical (m ≈ 1). Erosion makes its lifetime law subcritical (m_c 0.77), and that lifetime
> > law reproduces the bulk of X-TICKET lineage sizes (0 / 1–4 / 5–26: predicted 0.57 / 0.28 / 0.13 vs observed 0.54 /
> > 0.29 / 0.14)."
>
> Every future m must name its readout: per call or lifetime; certified or any-author; partner stream; n.
>
> **(l) The BASE "second regime": downgraded, then partly restored. Its cause is open.**
>
> **1. Downgrade (W2-14).**
> - W2-2's "100x excess of runaways over the individual law" compared unlike readouts.
> - On a shared readout, P(reach ≥ 27 certified births), the law gives 0.025 and the world 0.031. Reaching the burst is the
>   ordinary subcritical lottery.
> - The "empty 27–162 gap" is weak: P ≈ 0.045 (X-TICKET) or 0.054–0.056 (f = 1 pool), with data-chosen edges. W2-2's
>   "1 vs 7.7, P = 0.004" is a denominator mismatch; see TRACE_CHECKS.
>
> **2. Partial restoration (W2-25 F8).**
> - *After* 27 births, 4/4 X-TICKET lineages reached ≥ 163, against 1.2% under the individual law (P ≈ 2e-8).
> - s14's B exceeds its label growth by only 3, so the excess is not kin re-conversion inflating B.
> - **There is a post-27 persistence anomaly.**
>
> **3. It is not kin or density (W2-22, pre-registered).**
> - FIELD BANK vs FREE BANK conditional persistence: ratio 1.31 [0.60, 2.80] under C−. Under C+, FIELD is significantly
>   *lower* (0.27 vs 0.65, p = 0.0014).
> - The verdict is fragile at the CI edge: Katz gives 2.87, bootstrap 3.15.
>
> **4. Against which comparator?**
> - The 1.2% comes from the infinite-population individual law. A kin-free, density-free *field* process with bank
>   partners and mutation on (FREE BANK) already gives 0.21 (C−) to 0.65 (C+).
> - What remains unexplained by any process short of the world is world 4/4 vs FIELD BANK 9/33 (p = 0.011, n = 4,
>   unmatched seeds). W2-22 places it in the realized FULL background (background interactions and residue), which is
>   rung 5.
>
> **5. It coincides with side-0 morphs (W2-17), with these corrections:**
> - **The count.** Morphs arose in 3 of 64 unselected seeds; 2 reached depth ≥ 22 and 3 reached B ≥ 163. Without a morph:
>   0/61 by either readout. This replaces "2/2 vs 0/61".
> - **The timing.** In 2 of the 4 X-TICKET runaways (s121, s14), the lineage passed 27 causal births with zero side-0 edges.
>   The morph arrived after 84 and 123 births.
> - **The types.** W2-17's "types" are parent-side event tags. Genotypes were checked only for the 12 deep-chain genomes.
> - **The switch rate.** Event-side switches occur at 3.5% per birth in controls, against 7.5e-4 per birth for one-bit
>   genotype side switches (N17d). This is unreconciled; W2-26 is assigned.
> - **Fecundity.** Against realized partners, the per-call morph advantage is about +6% (1.24–1.25 vs 1.17). It is not +45%.
>   Realized S0 m > 1 is seen only in runaways, so it is outcome-conditioned.
>
> **6. The mechanism of the morph (W2-24, traced at register level).**
> - The 7ae3 family copies "own base → absolute DE".
>   - The founder has DE = 0: it converts from side 1 and is hijacked at side 0.
>   - Side-switch morphs (44→AC, 49→5C) have DE = 64.
> - The morphs' gain is run-first protection. The founder at side 1 fails only when the first mover has already damaged it
>   (173/516). The morph's converter side is never pre-damaged (484/484 intact).
>
> **Standing.**
> > "Reach (≥ 27) is the ordinary subcritical lottery. Post-27 persistence is anomalous against the individual law and,
> > more weakly, against field processes with bank partners. It is not explained by kin or density. It is associated with
> > side-0 event types in deep chains, but a morph is *not* shown to precede the departure (it does not in 2/4 runs).
> > Cause open."
>
> **Decisive tests:**
> - W2-25 Experiment 1 (implanted morph founders);
> - the K4 test in the THEO block (seed-matched FIELD FULL vs FIELD BANK on B_xk);
> - event-side logging in FREE BANK runs, to see whether morphs also accompany persistence there.
>
> **(m) Partner execution of the donor's own code after the pc wrap is causal for loss (W2-23, W2-24).** This amends
> SYN:73, :90–93, :126, :162 and :228.
>
> **The causal test (W2-23, pre-registered; Harvard confinement, which stops pc crossing into the partner's half).**
>
> | measure | stock | confined | prediction |
> |---|---|---|---|
> | N2 side-0 hijack | 0.224 | 0/750 in both contexts | P3 PASS |
> | K3 chain relabel (9cba / e160) | 0.60 / 0.43 | 0.025 / 0.125 | P2 FAIL, by one chain |
> | side-1 per-interaction good copies | 0.62 | 0.88 | |
> | side-1 CVT-R | 3/17 | 10/17 | P1 FAIL; the target was ≥ 14 |
>
> - The confinement-without-terminator arm (WRAP) removes P3 equally and P2 nearly equally. So **confinement, not the added
>   terminator, is the active ingredient** for hijack. This answers W2-25 F12's confound for P2/P3; the terminator matters
>   only for P1.
>
> **The mechanism (W2-24).**
> - In 226/232 of the founder's side-0 losses, the final author is the partner, running the founder's own LDIR at pc 52
>   (HL = 0x0040, DE = 0, BC = 0x4040).
> - **The donor's own code is the weapon.**
> - Either occupant's pc can wrap into the other half's entry point (W2-25 F17):
>   - the second mover wraps 127 → 0 into a side-0 donor;
>   - the first mover wraps 63 → 64 into a side-1 copier.
>
> **Residuals.**
> - Data-path writes by the partner's *own* LDIR and byte stores: 114 block pre-damage events remain in P1.
> - Copy-back by descendants the implant had converted: 3 of 6 K3 residual relabels. That is heredity, not hijack.
>
> **Two limits on the claim.**
> - Competence does not need partner execution: 128/128 evolved copiers survive confinement (W2-7). Partner execution is a
>   **loss** mechanism, not part of how copiers copy.
> - **Scope.** Static harness only (single `p11.interact` calls, random or bank partners). It has not been shown in-world;
>   that needs HARV in-world on X-TICKET, which is not authorized.
>
> **What stays open.** U-W1b's 24-copier panel, where own-context writes dominated, has not been re-tested under
> confinement. So SYN:92's "mostly their own wrong-side copying" should be scoped to that panel.
>
> **Replacement for SYN:73's "Reproduce" row cell:**
> > "Loss of a copier's half is mainly partner execution of the copier's own code after the pc wrap. This is causal in the
> > static harness for 7ae3 and for 17 side-1 corpus copiers (W2-23). For the U-W1b panel, own-context writes dominate
> > (untested under confinement)."
>
> **(n) 43→C3 is a NOP → JP flip, not "POP BC → JP".** This corrects the ledger's N17e entry and W2-25 §4 "strangest
> observation" 3. The synthesis does not carry the claim.
> - **The flip.** 0xC1 is a one-byte NOP on this VM, which has no POP. The flip 0xC1 → 0xC3 is one bit (11000001 →
>   11000011).
> - **What it makes.** `JP 22EC`. Its operand is bytes 44–45 (EC 22), and 0x22EC mod 128 = 108, which is side-1 position
>   44.
> - **At side 1** it jumps to its own next instruction. Nothing changes: keep 0.907, conversion 0.874 vs 0.870.
> - **At side 0** it throws any runner out at position 43, before the LDIR at 52:
>   - partner runs of the donor's LDIR fall from 277 to 11 (N = 1,000);
>   - side-0 keep rises from 0.52 to 0.97;
>   - children inherit the higher keep (0.94).
> - **Falsified.** "Changes the BC count" (N17e) is falsified.
> - **How to describe the gain.**
>   - Per-call m_base 1.17 → 1.39 counts keep by fidelity. On exact keep at side 0 (251/484 vs 154/484) the gain survives
>     but is smaller.
>   - No runaway uses it (W2-17).
>   - Call it the "largest per-call gain found" (W2-25 F16), not the "strongest single-step gain".
> - **The double mutant.** C3 + AC is two one-bit flips from the founder: m 1.47, keep 0.98. It is the only genotype that
>   invades the founder in exact-identity contact (2 vs 0).
>
> **(o) The ~2e-4 base rate is a property of the encoding, not of reproduction (W2-7).** This amends SYN:71, :79, :153 and
> :156.
> - **The physics moves the random-genome copier rate by more than 3 orders of magnitude:**
>
>   | physics | random-genome copier rate |
>   |---|---|
>   | stock | 2/12,000 |
>   | RING192 | 90/12,000 (about 40x stock); minimal copier 2 bytes |
>   | SELFCOPY | 702/3,000 = 23% |
>   | NOWRAP, NOBLOCK, ROTATE, REGRAND | 0/12,000 each |
>
> - **Evolved copiers depend on the stock physics:**
>   - absolute placement (0/128 survive ROTATE);
>   - the 7-bit wrap (7/128 survive NOWRAP);
>   - the block op (0/128 survive NOBLOCK);
>   - slice 300 (66/128 survive a 5x slice);
>   - the long count doubling as terminator (113/128).
> - **The replication is not independent.** W2-13's 1.8e-4 (33 / 180k) uses the same VM and the same COMPETENT screen, so
>   it is a replication, not an independent validation (W2-25 F15).
> - **Required scope.** Every quantitative rarity claim needs the scope "under stock Z8 physics (128-byte ring, 7-bit wrap,
>   block op, slice 300)". That covers minimal_prior, "50–70x the reachable-motif prior", and the ARC3 accessibility
>   delegate.
>
> **Replacement for SYN:156:**
> > "On the dense pair tape under stock Z8 physics, copying occurs at a random-genome base rate (about 2e-4) that is set by
> > the encoding and geometry, and that moves by more than 1,000x with the physics. It is not an evolutionary achievement,
> > and it is not a generic rarity of reproduction."
>
> **(p) Correction (e) is itself superseded: founders behave as independent tickets (W2-12).** This also amends SYN:179.
> - A common p1 fits 798 k = 1 runs plus 416 dose runs (p = 0.31), with no block heterogeneity (p = 0.64).
> - β = 1.13 [0.98, 1.29], p = 0.095. Leave-one-experiment-out prefers independence.
> - Over 17 thresholds from 1 to 300, β stays within 0.86–1.29, with no p < 0.10.
> - **Where the excess came from:**
>   - "p = 0.0013" is a plug-in artifact, because p1 is treated as exact.
>   - (e)'s "41/80 vs 29.3 expected, p = 0.005" uses the pooled p1. On its own joint fit, C-CRITICAL-MASS alone still rejects
>     independence (p = 0.014). That comes from its low k = 1 arm (5/80, against about 11 expected), not from a high k = 4
>     arm. Drop that experiment and β = 1.06 (p = 0.64).
> - Mild superadditivity, β ≤ about 1.3, is not excluded.
>
> **Replacement for SYN:179:**
> > "Founders act as independent tickets at every depth threshold tested (W2-12). The earlier k = 4 excess was a plug-in
> > artifact plus one low k = 1 arm."
>
> **(q) The BASE "8x miss" and the ATOMIC calibration (SYN:176).**
> - **BASE.** The miss came from empty-register partners (FREE FRESH0 → POOL: B ≥ 163 falls 5/40 → 0/40, p = 0.027) plus an
>   uncertified occupancy readout (about 3x). With realistic partner registers the process stops over-predicting (0–0.025
>   vs 0.031). The test has no power at 0/40 (W2-14).
> - **ATOMIC.** On matched readouts at 300 epochs (W2-22, seeds 0–29):
>   - world depth_world ≥ 20 is 20/30 vs model 14/30 (p = 0.19);
>   - B ≥ 163 is 14/30 vs 10/30 (p = 0.43);
>   - nothing is significant.
>
>   The world at 300 epochs equals the world at 2,000 epochs seed for seed, so horizon censoring is excluded. W2-14's
>   "ATOMIC validation did not pass" is withdrawn.
>
> **Replacement for the BASE sentence at SYN:176:**
> > "Under BASE, the map's ZERO-context P_est of 0.26 against about 0.03 observed is explained by empty-register partners
> > and an uncertified readout (W2-14). With realistic partner registers there is no over-prediction (low power)."
>
> **(r) Correction (f) is strengthened: the magnet mechanism is causal in the static harness.**
> - Harvard confinement cuts the single-site chain relabel from 24/40 to 1/40 (9cba) and from 17/40 to 5/40 (e160)
>   (W2-23 P2).
> - About half the residual is copy-back by partners the implant had converted.
> - In-world: still untested.
> - SYN §5 item 2's "integrated hazard over-predicts loss by 3–6x" stands.
>
> **(s) The side-1 heredity failure is closed causally (W2-31, pre-registered, both predictions PASS).**
> - With Harvard confinement plus order-protected confinement of the partner's writes into the copier's half before the
>   copier runs, side-1 CVT-R is 16/17 and good copies are 1020/1020 (= no partner).
> - The 125 residual bad copies under HARV are all partner data-path writes: 81% need a block copy, 19% are byte stores only.
> - The chain has three parts:
>   1. partner execution of the copier's code (W2-23);
>   2. partner data-path writes (W2-31);
>   3. a small read-path coupling through wraparound LDIRs.
> - **Order protection removes side-0 conversion (0/18).** Conversion and vulnerability are the same act seen from opposite
>   sides, so this is a structural trade-off of pair-tape physics, not a defect.
> - Static harness only.
>
> *(j)–(r) drafted by W2-28; (s) added by Nestor. Inserted 2026-10-01 per the Wave-2 ledger.*

---

## 0. The answer to the harder question, stated first, with its confidence

The directive asks: *What causal organization allows hereditary machinery to arise, persist, reproduce and alter itself
without the result being reducible to seeding, transplantation, world scaffolding, input gating, bookkeeping, or a trivial
copier encoding?*

**Answer for NPE as it stands.** In the first three stages, most of what the evidence shows is supplied by the world and the
instruction set, together with the world's write-back rule. The fourth stage leaves an organism-side residue. It is real, but
small. Whether anything *beyond* that residue exists, meaning a lineage-level organization, has **not been tested**. The
current evidence does not require it.

| stage | what the evidence shows | reducible to | confidence |
|---|---|---|---|
| **Arise** | See the notes below this table. | encoding + geometry, as a base rate | order of magnitude |
| **Persist / establish** | See the notes below this table. | world rule + a two-generation interaction map | coarse pattern: good. Per-donor: post hoc only |
| **Reproduce** | See the notes below this table. | an execution field + bookkeeping, for SELF-using copiers. For typical copiers: its own wrong-side action | shown on 7ae3 + 24 corpus copiers |
| **Alter itself** | See the notes below this table. | **not fully reducible.** Selection acts on an organism-authored reproductive parameter | recurrence: confirmed. Mechanism: partial. Lineage-level organization: untested |

**Arise.**
- The instruction set supplies a half-duplicator: block copy on a 128-byte wrapped tape.
- Competent dense genomes add a small setter chain around it. The collapse set has a median of 8 bytes (IQR 6–10), of which about 5 lie beyond the last-setter motif. Those counts come from single-site knockouts.
- Random genomes are competent at about 2e-4 (3 hits, CI 4e-5 to 6e-4). That is consistent in order of magnitude with dense acquisition: 5% predicted vs 7.3% observed at the first checkpoint, and 66% vs about 55% by the end.

**Persist / establish.**
- The world's write-back rule sets the regime. BASE writes back the whole half. ATOMIC keeps only detector-promoted overwrites and discards all other writes, self-writes included.
- The single-interaction offspring map predicts the coarse pattern:
  - the ordering of register policies;
  - the anti-zero donor;
  - the fact that only state-robust donors succeed from non-zero registers.
- The same map does **not** predict per-donor establishment within ZERO (ρ = 0.08) and is poorly calibrated.
- Adding the product's own conversion law (whether the copies copy), post hoc, gives ρ = 0.81 within ZERO and 0.86 pooled.

**Reproduce.**
- In SELF-enabled cells, partners can execute a SELF-using copier's code and copy themselves over it. For 7ae3 this happened in 200/400 pairings, falling to 0/400 when its SELF+LDIR bytes are knocked out.
- For typical SELF-free copiers, loss of their own half is mostly their **own** wrong-side copying.
- The foreign-cell "victim magnet" is **unexplained**.

**Alter itself.**
- After a founder lineage takes over, genomes whose copy address comes from constants rather than from the noisy inherited registers come to dominate. This happened in 8 of 15 takeover runs, or 8 of 11 if the lineage also ran away.
- State-free genomes are present in 25 of 29 large, sustained competent compartments. For the non-founder compartments, whether the trait was *acquired* or *founding* is unknown.
- No extra bytes are needed, by single knockouts, and state-free copiers also copy from side 0 (but so do the genomes they replace; see Wave-2 correction (b)).
- In one lineage (16000006) the trait arose through a multi-step walk.

**So:** the causal organization that makes hereditary machinery possible in NPE is **largely supplied**. What is endogenous
and demonstrated is **the adaptive relocation of the copy's operand sources into the genome**. Selection favours it because
newborns inherit the victim site's leftover registers. This is a real, material change, not a bookkeeping artifact. It does
not, on current evidence, amount to a self-maintaining reproductive organization. Current evidence also does not rule such an
organization out: its distinctive predictions (kin-context benefit, multi-site epistasis, heritability of the mechanism across
independent origins) have not been tested.

---

## 1. The world as it actually is: the mechanics that matter

Each of these facts was invisible to the program's rulers at some point.

1. **The pair tape is a fixed field of 256 sites.**
   - Each site has *content* (64 bytes) and a *context*: a register file that stays with the site.
   - Each epoch, random pairs are laid on a 128-byte wrapped tape. Side 0 (offset 0) runs first, then side 1 (offset 64).
   - Both halves are written back (ADV2 §0; `world.py:782–889`).
2. **Nothing is born and nothing dies on the pair tape.**
   - A "birth" relabels a site when a 0.9 fidelity threshold is crossed (`world.py:877`).
   - The newborn content runs in the **victim site's leftover registers**, which are never reset (`world.py:812`) (U-W7, verified in code).
3. **Only 7 address bits matter** on a 128-byte tape. A copier's effective context is its pointer phase.
4. **The instruction set supplies a half-duplicator.**
   - Block copy with DE − HL ≡ 64 and a long count leaves a period-64 tape (ADV1 §1.1).
   - Zero registers supply HL = 0, which is the copier's own start.
   - The copy count is set by the leftover slice budget: 164–295 in real donors (S1).
5. **Code is executed by whichever context reaches it.** pc runs across the half boundary. How much this matters depends on the copier (U-W1, U-W1b).
6. **Write-back rules are world physics.**
   - BASE writes back what is on the tape. 57% of member interactions change a genome, by about 5.5 bytes each; self-writes are as common as partner writes.
   - ATOMIC keeps only detector-promoted overwrites and discards other writes, self-writes included (U-X2).
   - The RECOMBINATION splice rewrites halves at p = 0.2 per call.
7. **Mutation operators differ by cell.** In 7ae3 opcodes never mutate: about 34 effective mutations per lineage in 2000 epochs, against 239 in ffa6. Nothing dies in these cells, so being overwritten is the only selection (U-E1).

---

## 2. The causal story, reconstructed

### 2.1 The detector era: what looked like replication was not (09-19 to 09-24)

- A 90% similarity test on a converged population reported replication "loudest exactly where nothing is happening". It was fixed for private slots but not for the pair tape (dossier C §1.1).
- **The 1,031 "spontaneous replicators".**
  - 910 came from the world's own splice (Z80A-D05). `births_similar_no_write > 10` marks the artifact: 906/910 vs 0/121.
  - Scheduler feedback steered late tier-L runs back into splice cells. The unbiased tier-M rate was 7.1% flagged and 0.55% P-11, with 0/102 on the splice axis (U-X4).
- **P-11 left 57 of the 1,031**, with maximum depth 2. Functional recertification of those 57 found 3 real copiers, 17 painters (mostly `LD (HL),0x36`) and 28 bare LDIRs driven by host registers.
- **The pattern of this era:** each ruler certified one level below the claim made from it. Resemblance was read as construction, construction as heredity, a label as descent, and an event as a genome property. The program and its auditors found each correction themselves. The certificate ladder (B1) generalizes the lesson.

### 2.2 What copying is here (09-24 to 09-26)

- **Non-pair physics never searched:** 0 births means 0 mutation. Once search and self-location were supplied, an implanted copier worked (C-SELFLOC 13/36 vs 0/36).
- **One-byte copy aliases** made replication appear from random bytes (C-DENSE 13/40 vs 0/40). On the pair tape they made donor acquisition common (C-DENSE-COPY 1/64 vs 39/64).
- **The functional-core forensic (FOR):**
  - Competent dense genomes are real copiers: 128/128 have source diversity 56–64, and none are painters.
  - Their knockout collapse set has a median of **8** bytes (IQR 6–10): the copy op plus a mostly *incidental* chain of register moves that yields aligned operands. About 5 of those bytes lie beyond the last-setter motif. Single-site knockouts cannot see multi-site dependence.
  - Random genomes are competent at about 2e-4, which is 50–70x the reachable-motif prior of (3–4)e-6.
  - This is consistent in order of magnitude with acquisition: 5% vs 7.3% at the first checkpoint, 66% vs about 55% by the end (FOR erratum).
- **Correction:** the widely cited `1E 40 E5` with NOP padding passes partly by zero-painting. With random padding there are 6 exact 3-byte copiers (FOR Q3).
- **Reading.** On the dense pair tape, copying is consistent with a random-genome base rate set by encoding and geometry. It is not an evolutionary achievement.

### 2.3 Establishment: the regime is set by the world's rule; the donor's own map predicts the coarse pattern

- **Establishment is decided within 3–10 epochs** (U-T1).
- **In X-TICKET (7ae3's own cell, SELF-enabled), the founder is lost at epoch 1 in 28% of runs** (U-T3).
  - A side-0 hijack mechanism operates in that cell: partners execute 7ae3's SELF+LDIR and copy themselves over it. This was verified: 200/400 pairings, 0/400 once the four bytes are knocked out, and the partner's context authored 12,485 of 12,549 changed bytes (U-W1). The execution-order hijack itself was first reported by Artemis (side 1).
  - The share of the 28% it explains has not been computed. ADV2 estimated 0.18–0.30 from the map.
- **Self-poisoning.**
  - It predicts almost perfectly whether a first donor copies at all: 12/12 vs 3/29 (U-F1).
  - W1's "half of established donors self-poison" was a run-level label artifact.
  - Carrying only the E and L pointer bytes reproduces poisoning on 32 of 44 poisoning sides, and clearing them rescues 26 (S1).
  - Real donors that stay robust **reload their pointers**. A copy count ≡ 0 mod 128 almost never occurs in real donors: counts are 164–295 (S1). So the phase-arithmetic route shown on synthetic copiers (ADV2 D4) is possible but not the observed one.
- **ZERO rescue** (C-ZERO-SPECIFIC 26/48 vs CONST 2/48) is the geometry of HL = 0 = own start.
- **Predicting establishment from single interactions (S1: PARTIAL).**
  - The single-interaction offspring map predicts the register-policy ordering, picks out the anti-zero donor, and identifies the donors that convert from non-zero registers, which carry all the CONST/RANDOM successes.
  - It does **not** rank donors within ZERO (ρ = 0.08, p = 0.38).
  - It overpredicts every arm by 0.12–0.42. Its Brier score is worse than a constant.
  - It cannot see the cell axis: observed CARRY is 0.16 in C7 vs 0.36 in CF, with near-equal predictions. Mutation and migration differ between the cells; the interaction does not.
  - Adding **whether the donor's copies are themselves copiers** plus a 500-epoch horizon gives ρ = 0.81 within ZERO and 0.86 pooled, with Brier 0.052 vs 0.076 for policy means. That repair is **post hoc**: it was designed after the failure. Four donors predicted high made sterile copies. In a spot check, every child differed from the donor at byte 0.
  - For 7ae3, the map's ATOMIC P_est is 0.49–0.52 (ADV2) and 0.57/0.63 (S1, ZERO/CARRY). The observed 109/208 = 0.52 counts depth ≥ 20 runaways, a ruler this synthesis suspects (§2.4). Under BASE, the map's ZERO-context P_est is 0.26 against about 0.03 observed, a miss of about 8x. **"Establishment is computable" is therefore not established.** What is established: establishment needs at least a two-generation map, and the world's write-back rule sets the regime.
- **Why copying stops under BASE.** Losers make 13 copy writes in 11,181 interactions, against 0.56 per interaction in winners (U-W3). That collapse is content sterility from write-back erosion. It is not explained by a near-critical offspring mean.
- **The splice** cuts the tail, not the start: 81 vs 77 runs make any copy, while runaways are 0/222 vs 22/630 (U-F3).
- **Founders act as independent tickets at the runaway endpoint** (X-DOSE-CURVE LRT p = 0.42). There is a residual k = 4 excess at depth ≥ 5 (p = 0.0013; joint LRT p = 0.108; runaway endpoint p = 0.70).

### 2.4 Takeover, and the depth question

- **Depth is bistable:** no single-founder run ends between depth 22 and 161. Both adversaries read this as extinction vs saturation plus within-family turnover (U-N4). If they are right, depth after saturation measures turnover, not establishment. **That is suspected, not shown.** cb7f copies in 8/8 ATOMIC runs at depth 4–6, and whether it took over is what E9 would decide (U-N2).
- **Label and content separate.** In the record:
  - X-CONTENT: founder bytes are 13–25% of the population.
  - X-MAT: founder bytes are 3–33% of the endpoint state-free L genomes; the trajectory runs 0.94 → 0.04 in 7ae3 27000023.
  - Early and late genomes share about 5/64 bytes.
  - In 9cba the founder label spreads with 0/120 certified founder edges (U-W6).
  - ADV2's toy process separates label from content from the map alone (U-I6, illustrative).

### 2.5 After takeover: regeneration, conservation, internalization

- **Material turns over while function is kept.**
  - L's D0 bytes fall 0.94 → 0.04 (7ae3 27000023).
  - MKL rises to 0.91.
  - The ffa6 lineages accumulate 43–67% mutation-made bytes.
  - Foreign-computed bytes enter only during takeover (≤ 0.19) and are later gone (U-I1).
  - In foreign cells the copy primitive is regenerated elsewhere (9cba) or flipped in direction (e160) (U-I5).
- **Conservation** is purifying selection on essential, opcode-immune positions (C-CORE). The knockout map predicts retention only partly (Spearman 0.29).
- **Internalization: what is solid.**
  - C-A3-INTERNALIZE is a confirmed recurrence: 8/144 runs, 8/15 given takeover, 8/11 given takeover plus runaway.
  - In 8/8 events the state-free genomes appear at or after takeover.
  - X-MAT shows they were not imported from coexisting non-founder populations.
  - Within runs the corpus drifts toward state-freedom: 28% → 62%, 16 runs up and 0 down (FOR Q5).
  - Mechanistically, state-free copiers source their copy address from constants rather than entry registers: 27% vs 56% world-dependent (FOR Q2). They also **all copy from side 0**: 48/48, against 23/80 side-1 copiers among the others. So part of what "state-freedom" registers is a switch to the side that runs first.
  - It is favoured about 6x when registers persist across executions; see Wave-2 correction (a). The X-A3-WITHDRAW sweep, 0.22 → 0.96 within 100 epochs, is selection on standing variation within the lineage (U-C5).
- **Internalization: what is open.**
  - Whether it is *generic*. State-free genomes are present in 25/29 large, sustained compartments. But the founders of non-founder compartments were never assayed. In 4/17 of them state-freedom is already the majority at the first competent checkpoint, and in 7/17 at the first checkpoint with ≥ 25 competent genomes. So for those compartments "acquired" cannot be told from "founding" (U-C2). The persistence comparison (founder lineage 4/8 vs replacements 16/18) is unmatched for the same reason (U-C3).
  - Whether its rate is supply-limited. The ffa6/7ae3 hazard ratio (about 8x) is *consistent with* the mutation-supply ratio (about 7x), but its 95% CI runs from about 1.1x to 370x, and 7ae3 has n = 1 event. That one event's state-free bytes are 91% execution-computed (MKL) and ≤ 6% mutation-made, so the OPERAND operator's supply is not obviously its source. Dossier E rated the operator account a cell-confounded hypothesis (U-T5).
  - Whether it is lineage-specific. The enrichment ratio in L (1.009) is close to tautological, because L's share is almost always 0 or 1. It cannot tell (U-C1).
- **The strongest organism-side residue: the 16000006 walk.**
  - 49–54 bytes changed over 118–126 replications, and the copier came to set its own destination: `LD DE,3200`, a phase reset to 0 mod 128.
  - Single knock-ins do not reproduce it (0/5), and an adapted graft reaches full robustness in only 1/12. It passes CVT-R 8/8.
  - It is n = 1 and exploratory, and it is an adaptive walk *in the reproductive setup*.
  - Whether it reflects organization beyond that setup is untested.

---

## 3. What "endogenous" can honestly mean in NPE now

| sense | status |
|---|---|
| **Not imported from a coexisting population** | **Supported, not validated** (X-MAT 8/8). Pre-takeover foreign bytes are gone before state-freedom appears. There is no planted-transplant positive control. MKL is keyed on the audited label. After L = 1.0 no non-L source exists, so X ≈ 0 is nearly forced. |
| **Made by the population's own execution** (regenerated material) | **Supported.** The same thing happens in a toy map, so it is expected, not special. |
| **The organism supplies a function the world used to supply** (address source moves from registers to constants, plus a side-0 switch) | **Supported as a trait change** (FOR Q2/Q5; C-A3). The selective cause is a world rule. The rate's source is unresolved. |
| **The founding lineage specifically did it** | **Not shown.** The D0 label is not a demonstrated causal unit. |
| **A self-maintaining reproductive organization beyond a compact copy setup** | **Not required by current evidence, and untested.** Its distinctive predictions (kin-context benefit, multi-site epistasis, heritability of the mechanism across independent origins) have never been measured. |
| **The organism owns its reproduction** | **Qualified.** SELF-using copiers can be executed by partners (7ae3). Typical SELF-free copiers mostly lose their half to their own wrong-side copying. |

---

## 4. Standing claims with proposed revised wording

These are proposals for FINDINGS after review. No frozen verdict of record is rewritten.

| claim as recorded | proposed wording |
|---|---|
| C-A3-INTERNALIZE: "endogenous internalization of register initialization, recurrent" | After a founder lineage takes over, state-free copy setups (address from constants, side-0 copying) come to dominate in fresh runs: 8/144 runs, 8/15 given takeover. The trait is often transient (4/8 absent at 2000). Whether it arises in other populations as well is unresolved, because their founders were not assayed. |
| X-MAT-INTERNALIZE: ENDOGENOUS | The state-free genomes were not imported from coexisting non-founder populations. Their bytes were made by the occupying population, with founder bytes a minority (3–33%). No planted-transplant control was run. |
| C-ATOMIC C1: "tape-write erosion stops heredity; removing it sustains heredity" | Under a world rule that keeps only detector-promoted overwrites and discards all other writes (self-writes included), 7ae3 runs away in 46/80 vs 1/80. |
| C-RUNAWAY / "runaway heredity" | World-level causal depth ≥ 20. It is suspected to reflect saturation followed by within-family turnover (E9 pending). |
| C-CORE: conserved core | Purifying selection retains essential, opcode-immune positions of the copy interface in 7ae3's cell, but not in foreign cells. |
| "Establishment lottery" | Early fate (3–10 epochs), partly side-0 hijack in SELF-enabled cells. A two-generation single-interaction map predicts the policy pattern and, post hoc, per-donor ranks. |
| C-ZERO-SPECIFIC | Zero entry state supplies the address (HL = 0 = own start). Self-poisoning is the copier's own pointer advance, and robust donors reload their pointers. |
| "Competent donor" / "replicator" | Construction-competent at the zero-register context point. Report the certificate level (B1), with random-passenger controls. |
| X-A3-WITHDRAW, "not sorting" | Selection on standing variation within the lineage. |

---

## 5. What remains genuinely unexplained

1. **The 16000006 path.** Why a multi-step walk ended at a destination phase reset, and whether such walks recur. The C-A3 events have no per-event mechanism.
2. **The foreign-cell victim magnet.** 9cba/e160: founder overwritten in 100/240 runs vs 0/240 for a random implant. Wave-2 N1 shows it is a partner hijack of the founder's **LDIR**. The rate is about 0.1-0.5% per interaction, all of it removed by LDIR knockout. Integrated over a run that is the right order. RT B1 had compared a per-interaction rate with a per-run frequency. Not demonstrated in-world, and the integrated hazard over-predicts loss by 3-6x.
3. **Why ffa6 27000053 took over** (L = 1.0, exposure 409k) and never became state-free: P ≈ 0.055 under the ffa6 hazard.
4. **The k = 4 excess** at depth ≥ 5.
5. **Founder-less runaways, C5 dominance in 14000013, AN8 self-conversion.**
6. **Field scramblers** (ADV2 D9).
7. **cb7f:** takeover without depth, or failure?
8. **The cell axis the map cannot see:** CARRY 0.16 (C7) vs 0.36 (CF).
9. **Whether single-interaction statistics predict anything beyond first-donor fate.** S1b passed out of sample, but only for first-donor fate, which self-poisoning already predicts. Post-takeover dynamics are untested.

---

## 6. S1 result (static, completed): `forensics/FORENSIC_MAP_PREDICTS_OUTCOMES.md`

**Verdict: PARTIAL.** Details are in §2.3.

- **The specified map (GW P_est).** Pooled ρ is 0.53–0.56, significant under within-policy permutation. It gets the coarse structure right and fails within ZERO (ρ = 0.08). It is badly calibrated.
- **The post-hoc two-generation map.** ρ is 0.81 within ZERO and 0.86 pooled. Its causal and finite-horizon variants recover exactly the top 4 donors {0, 4, 14, 15}.
- **Phase.** Pointer carry-over reproduces poisoning (32/44). Robust real donors reload their pointers; they do not rely on Δ ≡ 0.
- **The central open point is the two-generation property: whether the copies copy.** It is a reproductive-closure measure (B4) that single-interaction thinking omitted. It is still genome-computable, not lineage-level.

**S1b out-of-sample test (static; criterion frozen before computing): PASS, qualified.**
File: `forensics/FORENSIC_MAP_OUT_OF_SAMPLE.md`.
- **Test.** 43 W1 first donors, never used to build the predictors.
- **Frozen predictor.** P_run500_causal. As coded, this is the donor's own causal offspring law over a 500-generation horizon.
  It is *not* the children's-law repair; that is P_run2.
- **Result.**
  - AUC 0.891 (CI 0.77–0.98) for "the donor made ≥ 1 causal birth".
  - Spearman 0.706 with the donor's causal births.
  - Both permutation p = 5e-5. Both frozen thresholds were met.
  - Scoring the 5 unrecoverable donors worst-case still passes: AUC 0.775.
- **Qualifications.**
  - The specified one-step P_est also passes, only just (AUC 0.779, ρ 0.41).
  - The simplest statistics predict best: mean offspring m (AUC 0.993) and the children's conversion rate (0.991).
  - What is predicted is essentially **whether the donor copies from its carried state at all**. 23 of the 28 donors with no
    births never copy in that context.
  - W1's own carried-state measurements on the same genomes predict as well: OWN_REAL AUC 0.92; SELFSTATE rate_k1 0.90.
- **Reading.**
  - First-donor fate in W1 is predictable out of sample from the donor's own single-interaction behaviour under carried
    registers. That is a genome-level property, and no lineage history is needed.
  - The map re-derives the known self-poisoning split. It adds no new information beyond it.
  - Together with S1, this supports T6/T2 at the **first-donor** stage. It says nothing about post-takeover evolution, where
    T4's untested predictions live.

---

## 7. The next experiment

See NPE_DECISIVE_EXPERIMENTS_NEXT.md (revision 2). In brief:
- E1 was redesigned. It uses a content-ancestry ruler validated on a replay, and adds a home-population arm, because T4 predicts no advantage in a naive population.
- E2's null became a true reset-every-interaction arm.
- E4's predictions were restated, because a monophyletic sweep is T1's prediction too.

The out-of-sample map test has now been run (S1b: PASS, qualified; §6). The cheapest remaining decisive steps are the static pairwise-epistasis map S3 (T4(c); result in the handoff) and the replay E4 (T4(b)).

---

## 8. What changed from revision 1 (red-team findings, all accepted)

- **B1.** The foreign-cell victim magnet is no longer attributed to the hijack; it is moved to unexplained.
- **B2.** Acquisition is order-of-magnitude only: 5% and 66%.
- **B3.** "Generic internalization" is downgraded; the non-D0 founders were not assayed.
- **B4–B6.** E1, E2 and E4 redesigned.
- **B7.** "7ae3 verified" removed. Both BASE rows reported. Depth caveat added.
- **M1.** The hazard ratio is now *consistent with*, CI about 1–370x, with the MKL caveat.
- **M2.** Hijack scoped to SELF-using copiers; typical copiers mostly self-import.
- **M3.** T4 is untested, not contradicted.
- **M4.** Depth is suspected; cb7f is open; 8/15 given takeover.
- **M5.** X-MAT is "not validated".
- **M6.** Side-0 switch disclosed.
- **M7–M9.** Experiments doc repaired. S1 filled in.
- **Minor items.** m1–m16 applied where they touch these files.
