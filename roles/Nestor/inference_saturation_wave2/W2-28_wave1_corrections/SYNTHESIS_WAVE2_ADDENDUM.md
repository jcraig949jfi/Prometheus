# W2-28 draft: additional WAVE-2 CORRECTIONS (j)–(r) for NPE_MECHANISTIC_SYNTHESIS_2026-09-30.md

**Drafted:** 2026-10-01T02:33:37Z (`date -u`), by the W2-28 worker.
**Status:** this is a draft. The synthesis has **not** been edited.

**Where it goes.** Append these after correction (i), inside the existing blockquote (SYN:23–54).
- Items (j)–(o) are the ones the brief asked for.
- Items (p)–(r) are further supersessions found while drafting. Two of them, (p) and (r), amend existing corrections (e)
  and (f), which Wave-2 evidence has itself overtaken.
- Line numbers refer to revision 2 as committed.

**New numbers.** The only ones are in (j) and (p) and are marked **[W2-28]**. They are recounts from existing JSON; see
TRACE_CHECKS.md.

---

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

---

## Notes for Nestor (not part of the block)

- **Further stale lines in the synthesis body.** These are covered by (j)–(r) but sit outside the lines named above:
  - §2.5 :205 "They also all copy from side 0" is already flagged by (b). W2-24's DE mechanism now explains *why* side and
    destination co-vary: side is set by absolute DE.
  - §4 row "C-RUNAWAY": add "depth ≥ 20 is a world-depth ruler; 4/13 depth ≥ 20 runs have 0–2 founder births (W2-2)".
- **HANDOFF:115** repeats "early fate (3–10 epochs)". The handoff is outside this draft's remit; it is flagged so it does
  not drift from (j).
