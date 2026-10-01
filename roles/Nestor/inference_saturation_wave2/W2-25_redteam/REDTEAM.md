# W2-25: red team of the current Wave-2 picture

**Written:** 2026-10-01 02:01Z (taken from `date -u`).
**Scope:**
- Ledger through the W2-17/N18 entry (01:46Z).
- Reports W2-1 to W2-10, W2-13, W2-14, W2-15, W2-16, W2-17 and W2-19.
- W2-18 CORRECTION_PROPOSALS.
- Wave-1 SYN and THEO.

**How it was done:** read-only. No git writes, no world runs. Compute was under 1 CPU-min and consisted of JSON reads plus one timing script over the W2-17 `r3_out` replay logs.

**Conventions.** `file:section` refers to paths under `roles/Nestor/inference_saturation_wave2/` unless a path says otherwise.

## Answer first

1. **The new headline (W2-17, "the side-0 morph drives runaways") is overstated in four ways.** It survives in a narrower form.
   - **The count is misstated.** The ledger's "2/2 morph runs became runaways vs 0/61" is **2/3** in the JSON. Under the depth readout, s14 has a morph but depth 21.
   - **The morph often comes after the burst.** I timed it from the replay logs: in **2 of the 4 X-TICKET runaways (s121, s14), the lineage reached 27 causal births with zero side-0 edges.** The morph arrived after 84 and 123 births.
   - **"Type" is not a genotype.** It is the side of the birth event.
   - **"Supercritical" holds only after conditioning on the outcome.** Realized S0 m is 1.08 in runaways but 0.88 in controls.
   - **The founder's "static m 0.85" is a 30-partner draw.** The same estimator gives 0.96–1.17 at n = 400–1000. Against realized partners the morph advantage is +0.07, not +0.4.
   - **What survives:**
     - reaching about 27 births is the ordinary subcritical lottery (the law gives 0.025, the world 0.031);
     - *what happens next* is anomalous: 4/4 lineages reached ≥ 163 births, against 1.2% predicted;
     - side-0 copying dominates the deep chains.

     That joins W2-14 and W2-17 into one statement, given in F8 below.
2. **W2-14's "ATOMIC validation did not pass" repeats the error W2-14 itself diagnosed.**
   - The model's depth at 300 epochs was compared with world depth at 2,000 epochs.
   - On a matched "not extinct" readout the numbers are 14/30 vs 20/30 (p = 0.19).
   - Three map-level ATOMIC predictions agree with the world.
3. **F (the supplied rewrite field) is not falsifiable as practised.**
   - At the rungs where it can fail (W2-14 rungs 1–3), the BASE test has no power (0/40) and the ATOMIC test is mismatched on horizon.
   - W2-17's morph was absorbed through the mutation kernel, so F has now absorbed every anomaly without passing one frozen quantitative test.
   - A falsifiable restatement, F*, is given in §3.
4. **The most important unresolved contradiction is founder independence.**
   - Pooled k = 4: 73/144 = 0.507, against 0.366 under independence (z ≈ 3.5, plugged p1).
   - W2-6 gives joint p = 0.108; the W2-12 draft gives β̂ 1.18, p = 0.13.
   - Under F* with morphs, every founder is an independent ticket, so any genuine excess is the last evidence for T4(a).
5. **Record defects.**
   - W2-8 D10's premise "L_share ∈ {0, 0.664, 1}" is false on disk (84 distinct values).
   - THEO has **no** Wave-2 corrections block, despite the brief.
   - SYN still says "fate decided in 3–10 epochs".
   - W2-2's "1 vs 7.7 over 320 runs, P = 0.004" cannot be traced to any script and conflicts with a2_rulers.json.

## 1. Findings

Severity:
- **B** (blocking): it changes a handoff headline.
- **M** (major): it changes a confidence or a reading.
- **m** (minor).

### F1 (B). W2-17's 2×2 is misstated.
- **Evidence.**
  - `W2-17_runaway_departure/a6_unselected.json` gives `S0_arose_in_runaways 2/2`, `S0_arose_in_others 1/62`, and `P_runaway_given_S0 0.667`.
  - In `a6_unselected.py:41`, a runaway is `depth >= 22`.
  - s14 has 47 S0 edges and depth 21, but B = 163 (`W2-14/a2_kin_signature.json`), so W2-14 counts it as a runaway.
  - The ledger's W2-17 entry and the REPORT both say "2/2 … vs 0/61".
- **Correction.** "Morph arose in 3 of 64 unselected seeds. Of these, 2 reached depth ≥ 22 and 3 reached B ≥ 163. Without a morph: 0/61 by either readout." Name the readout every time.

### F2 (B). The morph usually does not come before the burst.
- **Method.** New check, read-only, over `W2-17/r3_out/XTK_*.json` (birth logs: epoch, parent, side, causal flag). For each run, compare the epoch at the 27th causal birth with the first side-0 edge and with the first run of ≥ 2 consecutive side-0 edges.

  | run | e27 (27th causal birth) | first S0 edge | first S0×2 chain ("morph") | causal births before the morph | S0 edges by e27 |
  |---|---|---|---|---|---|
  | s35 | 12 | 9 | 10 | 12 | 5 |
  | s59 | 12 | 7 | 9 | 19 | 9 |
  | s121 | 9 | 10 | 15 | 84 | **0** |
  | s14 | 15 | 17 | 51 | 123 | **0** |

- **Reading.**
  - The morph comes before the burst in only 2 of 4 runaways.
  - With S1→S0 event switches at 3.5% per birth in controls (`a4_insitu_m.json` CTL: 36/1018), any lineage of 100+ births almost surely produces a morph. So "morph present in 12/12 runaways" is expected even under reverse causation.
- **Correction.** "Reaching about 27 births is the founder-type lottery. Side-0 morphs arise at a few % per birth and dominate deep chains. Whether a morph is *necessary for persistence* is untested; whether it is *necessary for the departure* is contradicted in 2 of 4 runaways."
- **Static follow-up.** Run the same timing script over all 12 W2-17 runaways (CRW, CNR and XH2N too).

### F3 (M). In W2-17, "type" is the side of the birth event, and "realized m" is conditioned on the outcome.
- **What "type" means.** `a4_insitu_m.py:1-5`: a node is "S0-born if its causal birth edge was written by a parent sitting at side 0". The genotype was checked only for the 12 deep-chain genomes (a3/a9).
- **Realized m by run class (a4 pooled):**

  | class | S0 | S1 |
  |---|---|---|
  | runaways | 1.077 (n 5,135) | 0.888 (n 2,977) |
  | controls | 0.879 (n 354) | 0.798 (n 1,275) |

  - In controls with morphs, S0 is subcritical: XH2N_s9 0.883 (248 births), XTK_14 0.851, CRW_71 0.944.
  - The relative S0 > S1 advantage is consistent across classes. The absolute "> 1" exists only in runs selected for running away.
- **Correction.** "S0 event-type has higher realized fecundity than S1 in every class (+0.05 to +0.26). Realized m > 1 is seen only in runaways, which is outcome-conditioned."

### F4 (B). The founder's per-call m is contradicted by the same estimator at larger n.
All of these use W2-3's `common.outcome` m_base:

| source | partners | n | founder m | morph (44→ac or 49→5c) |
|---|---|---|---|---|
| N17 `neighbours.json` | RAND | 60 | 0.78 | |
| W2-17 `a5_k2_morphs.json` | RAND | 30 per side | **0.85** | 1.23 |
| W2-17 `a5_k2_morphs.json` | ZERO | 30 per side | 1.017 | 1.25 |
| N17 `neighbours.json` | RAND | 400 | 0.96 | |
| N17b ledger | RAND / ZERO | 400 | 1.01 / 1.105 | 1.20–1.23 |
| N17e `bank_assay.json` | realized bank | 1,000 | **1.17** | **1.24–1.25** |

- W2-17's "subcritical founder, static m ≈ 0.85" uses the lowest row (n = 30, RAND).
- Against W2-14's realized partners, which W2-14 identifies as the dominant lever, founder and morph are both above 1 per call and differ by about 6%.
- **Correction.** Withdraw "static m ≈ 0.85". Per call, founder and morphs are both at or above 1 under realized partners. The two-type contrast lives in *realized lifetime* fecundity (F3), not in the per-call law.
- **Static test.** a5.k2 at NP = 1000 with bank partners, on the founder, 44→ac and 37→81. That is about 2 CPU-min, and the N17e harness exists.

### F5 (M). The switch rate is about 47x higher than N17d's reachability.
- **N17d:** only 3 one-bit supercritical neighbours exist, giving **7.5e-4 per birth**. `_mutate` cannot reach positions 37–51.
- **W2-17 events:**
  - S1→S0 event switches are 36/1018 = **3.5%** of S1-parent births in controls and 366/2644 = 13.8% in runaways (`a4` trans).
  - 37 a5→81 is a **two-bit** change (10100101 → 10000001), so a single copy error cannot make it.
- **Candidate explanations:**
  - under BASE, many children carry partner-authored bytes (W2-3 K2 "carrier's half mostly scrambled"; N4 MKL), so side-switch variation has routes beyond single-bit copy errors;
  - or the event side is a noisy proxy for type.
- **Correction.** Withdraw N17d's "evolutionarily hard to reach" until this is reconciled.
- **Static test.** For the 402 S1→S0 edges, diff child against parent bytes (or replay and record them). Classify each as a single-bit copy error, a multi-byte change, or partner-authored (prov). Re-assay a sample of 50 "S0-born" children at n = 200 for genotype side.

### F6 (B for F's standing). W2-14's ATOMIC "not passed" compares unlike readouts.
- **The mismatch.** `W2-14/REPORT.md §2`: model depth ≥ 20 **at 300 epochs** (0.233) against world depth **at 2,000** (20/30).
- **Model readouts on the same seeds** (`a1_summary.json` ATOMIC|FIELD|BANK):
  - depth20: 0.233;
  - B163: 0.333;
  - maxA40 = not extinct: 0.467 (stops: 16 extinct, 7 at horizon, 7 decided).
- **Matched comparisons:** non-extinct 14/30 vs world 20/30 gives Fisher p = 0.19. Against C1 46/80, p = 0.39.
- **Map-level predictions agree with the world:**
  - N9 0.50 (zero partners) and 0.51 (random);
  - W2-2 0.43–0.50;
  - W2-6 c7c 0.55.
- **ATOMIC is insensitive to partner registers:**
  - N9: ZERO 0.50 vs RANDOM 0.51;
  - W2-14 B163 for FRESH0 / BANK / POOL: 0.375 / 0.333 / 0.273.

  So W2-14's "c7c's 0.55 is not credited (FRESH0 partners)" is unjustified *for ATOMIC*.
- **Correction.** "ATOMIC: not compared at matched horizon. No evidence of under-prediction."
- **Test.** W2-14 next-1: FIELD+FULL (the world) on C-ATOMIC seeds 0–29 for 300 epochs, about 10 CPU-min, with the same three readouts. C-ATOMIC stores no per-epoch series (`c_atomic/results/*.json` holds only depth and p11_events), so this is the only route.

### F7 (M). W2-14's "persistence, not fertility" rests on one comparison run.
- **One comparison run.** `a2_kin_signature.json` has a single non-runaway that passed 27: s2 (rate 0.247 → 0.011). s14, a runaway by B, has rate_after **0.038**, which is closer to s2 than to s35 (0.072).
- **Wrong readout.** Per-member births per epoch is depressed by victim depletion: kin overwrites are not births (W2-6 C5c).
- **Pooled arms.** "FIELD BANK family 7/120 vs FREE 0/40 (p = 0.13)" pools the ctx-ZERO and mutation-OFF arms. Plain FIELD BANK vs FREE BANK is 1/40 vs 0/40 (p = 1).
- **Correction.**
  - Cite the persistence contrast as n = 1.
  - Replace the pooled 7/120 with the plain arm.
  - Measure persistence as member *loss* rate, not births per member.

### F8 (B). The second-regime downgrade overshoots: the conditional anomaly is strong.
- **The size of the anomaly.** Under the certified law (`W2-2/a7_gw_vs_ticket.json` 7ae3_BASE_causal), P(≥ 163 | ≥ 27) = 0.0003/0.0243 = **0.012**. Observed: 4/4 (s14, s35, s59, s121) gives P ≈ 2e-8.
- **Kin re-conversion cannot explain s14.** s14's B exceeds its label growth by only 3, so its count is not inflated by kin re-conversions.
- **What the ledger says.** "Second regime not demonstrated" (W2-14 entry, point 1) treats *reach* agreement as if it settled *persistence*.
- **Correction.** "Reach (≥ 27) is the ordinary subcritical lottery (0.025 vs 0.031). Post-27 persistence is anomalous (4/4 vs 1.2%). It is associated with side-0 event-type dominance of deep chains. It is not caused by a morph present before the burst in 2 of 4 runs (F2), and its mechanism is open."

### F9 (M). W2-2's "1 vs 7.7 over 320 runs, P = 0.004" cannot be traced.
- **No script.** Neither a1, a2 nor a7 computes it.
- **The 320-run depth pool contradicts it.** In `a2_rulers.json` the pool (128 ticket + 192 x_decay) contains at least 4 runs with B in 27–162 (`B_ge27_depth_lt20`: f0 70 and 51, f0.25 39, f1 35).
- **What the data support:**
  - the f = 1 pool (n = 192) has 1 in the gap against 4.6 expected (P ≈ 0.056);
  - the gap fills at f < 1 (6/192, 3/64).
- **Correction.** Drop P = 0.004. "The empty gap is an f = 1 feature with P ≈ 0.05–0.06, edges data-chosen."

### F10 (M). "BASE is critical" vs "BASE is subcritical" is papered over.
- **Two different objects.** W2-3's m_BASE ≈ 1 is **per call**. Its 1/d tail is on **world depth**, the maximum P-11 chain anywhere. W2-2 a2 shows 4/13 depth ≥ 20 runs have only 0–2 founder births.
- **The lifetime law is subcritical.** W2-2's lifetime founder-certified m_c is 0.77, giving a mean total progeny of about 4.3. W2-17's realized S1 m is 0.80–0.89.
- **The ledger's reconciliation.** The W2-3 entry calls both "near-critical", which conflates per-call with lifetime readouts.
- **The tail does not discriminate.** N18 shows the tail shape cannot separate one type from two.
- **Correction.** "Per call, m ≈ 1. Lifetime founder fecundity is subcritical (0.77–0.89). The 1/d law is a world-depth record statistic and is not evidence of founder criticality."

### F11 (M). W2-8 D10's premise is false on disk.
- **The claim.** `W2-8/REPORT.md §5` says "L_share only ever takes the values {0, 0.664, 1}".
- **The data.** `npe-arc3-2026-09-28/c_a3_internalize/results/*.json`:
  - 84 distinct L_share values;
  - 12 of the 16 runs that ever reach L ≥ 0.5 have intermediate values;
  - ffa6 27000053 rises 0.18 → 0.35 → 0.45 → … → 1.0 (consistent with W2-2's "slow creep").
  - "free_in_L == free iff L ≥ 0.5" holds in 15/16 and fails in 7ae3_27000033.
- **Correction.**
  - Keep D10's event recount (8 / 4 / 3) only if it is re-derived without the ternary premise.
  - Withdraw "X is close to determined by L_share because L is binary" (X-MAT).
  - W2-15's C-A3 and X-MAT relabels inherit this.

### F12 (M). HARV is not "the clean causal test", and the "four independent lines" share one harness.
- **What W2-7 itself says.**
  - HARV "gains side-1 copiers because the halt at the half edge acts as a terminator".
  - Its attack table lists "HARV adds a terminator".
- **The ledger's claim.** The W2-4/W2-7 cross-link 1 calls it "the clean causal test of the wrap/partner-execution field".
- **Cleaner tests already exist.** W2-16 s3/s4 (all-HALT partner 17/17; no partner run 1020/1020) are cleaner static tests.
- **The lines share a harness.** N1, N2, W2-3 K3 and W2-16 all use single `p11.interact` calls against uniform-random or static partners.
- **Correction.**
  - "HARV confounds confinement with a terminator; compare against Φ recomputed under HARV (W2-7's own fix)."
  - "Convergent mechanism, one harness, one partner proxy; not demonstrated in-world."

### F13 (M). SYN still says "fate decided in 3–10 epochs" (Wave-1 C6).
- **Gap in the corrections block.** Correction (e) covers only independence.
- **Contrary evidence:**
  - W2-2: nothing on disk distinguishes runaways before epoch 10, and the best early warning is births in epochs 11–15;
  - W2-14 and F2: divergence happens after the 27th birth (epochs 9–20), and morphs appear at epochs 9–51.
- **Correction.** Add (j) to the SYN block: "Establishment of a burst is decided early; whether a burst becomes a runaway is decided at epochs 10–50 by persistence."

### F14 (M, record). THEO carries no Wave-2 corrections.
- **What is missing.** `grep -i "wave-2\|W2-"` on `inference_harvest_2026-09-30/NPE_COMPETING_THEORIES.md` returns nothing. The brief says rev 2 has a corrections block.
- **Stale lines:**
  - **:57.** "Existing test. None in NPE": the FAIR ZERO no-payoff arm exists (W2-1).
  - **:41, :354.** "8x consistent with 7x supply": now confounded (N14 / D4); about 13x with competent exposure (W2-1).
  - **:181.** T4 "untested": T4(c) is dead (S3), T4(c′) is weakened (W2-13), T4 is eliminated as a theory (W2-6).
  - **:298-303.** T6 holds at the first-donor stage. W2-14 now limits F to rungs 1–3.
- **Correction.** Add a dated Wave-2 block to THEO before handoff.

### F15 (M). W2-13's "T3 suffices" uses a corruption ruler.
- **The ruler.** W2-13 scores strict synthetic lethality with random-value pair knockouts. W2-4 shows random-value knockouts are a **corruption** screen:
  - 36% of "necessary" bytes are corruption-only;
  - only 12/26 EST calls survive a second value.
- **Why that biases the result.** Corrupting an executed byte is lethal roughly in proportion to how much is executed. So "lethality tracks executed length" is partly built into the ruler. W2-13's pair-class table agrees: lethality sits almost entirely in executed code.
- **The "independent" check is not independent.** "1.8e-4 matches minimal_prior" uses the same VM and the same COMPETENT screen, so it is a replication, not an independent validation.
- **Correction.**
  - "T4(c′) is not supported on a corruption readout; the deletion (NOP-pair) readout is untested."
  - Add the NOP-pair arm to W2-20's preregistration as a secondary.

### F16 (m). N17e's "strongest single-step gain" (43→C3, m 1.39) is a per-call statement.
- No runaway uses it (W2-17).
- Per-call ranks do not predict fate within a regime (N10, ρ ≈ 0).
- **Correction.** "Largest per-call gain found."

### F17 (m). The wrap wording is too narrow.
- N1/N2 founder losses happen at side 0, by the second mover wrapping **127 → 0** into the founder's code. W2-16's smear is the first mover wrapping **63 → 64**.
- **Correction.** "Either occupant's pc can wrap into the other half's entry point."

### F18 (B for T4(a)). Founder independence: the numbers disagree, and the arm set is not frozen.
- **The estimates:**
  - W2-1: C-CRITICAL-MASS k = 4 41/80 vs 29.3 expected (p = 0.005); X-CRITICAL-MASS 32/64 (p = 0.02).
  - Pooled k = 4: 73/144 = 0.507, against 1 − (1 − 0.108)⁴ = 0.366.
  - W2-6: joint p = 0.108.
  - W2-12 draft (no report): β̂ 1.18, p = 0.13 at d ≥ 5.
- **My check.** From k = 1 at about 0.12 (n ≈ 798) and k = 4 at 0.507 (n = 144), β̂ ≈ 1.23 with SE ≈ 0.11, so z ≈ 2. The draft's p = 0.13 therefore needs its arm set and its overdispersion term disclosed.
- **The arms are heterogeneous** (`W2-12/table_summary.json`). C-NORECOMB k = 1 is 5/24 (21%) while C-CRITICAL-MASS's own k = 1 is 5/80 (6%). W2-9 flags NORECOMB as a fluke (p = 0.003 against C-RUNAWAY BASE).
- **Correction.** Keep this UNRESOLVED and make it the single most important open contradiction (see §4).
- **Static test.** One frozen LRT on the "comparable" set in `table_summary.json`:
  - batch as a random effect;
  - each depth threshold reported;
  - leave-one-experiment-out;
  - the within-experiment C-CRITICAL-MASS 2×2 reported separately.

### F19 (m). N12's "geometry decided" is static, and the panel screen flickers.
- **The flicker.** ZERO-competent is 16/16 in N11 (20 partners) but 15/16 in N12 (12 partners), on the same donors.
- **The other direction.** P11 (W2-18): within the two dual-competent donors, ZERO 1/6 < CONST 2/6 < RANDOM 3/6.
- **Correction.**
  - "HL phase is the main static supply from zero (this panel)."
  - The in-world PATTERN rescue (7/16 predicted) remains the test.

## 2. Readout mismatches (beyond the three known ones)

| # | comparison | why the readouts are unlike | finding |
|---|---|---|---|
| R4 | W2-17 founder "static 0.85" vs morph 1.2–1.3 | n = 30 RAND draw vs the same estimator at n = 400–1000 and with realized partners | F4 |
| R5 | "realized m 1.08" (S0) vs per-call m | outcome-conditioned event-side fecundity vs per-call genotype law | F3 |
| R6 | W2-14 ATOMIC model vs world | depth at 300 vs depth at 2000; three model readouts span 0.23–0.47 | F6 |
| R7 | W2-14 "fertility does not rise" | births per member per epoch (victim-depleted) vs per-call m | F7 |
| R8 | W2-3 "critical" vs W2-2 "subcritical" | per-call m + world-depth tail vs lifetime founder-certified m_c | F10 |
| R9 | W2-17 runaway (depth ≥ 22) vs W2-14 runaway (B ≥ 163) | s14 flips class | F1 |
| R10 | W2-13 lethality vs "function" | corruption screen vs deletion screen | F15 |
| R11 | U-T5 / THEO "8x vs 7x" | hazard per takeover vs supply per site; 13x with competent exposure | F14 |
| R12 | keep under BASE: 0.50 (W2-4) vs 0.61 (N17 confirm) vs 0.72 (N17e) vs about 0.80 (W2-6 C7) | panel vs founder; RAND vs bank; any-author ≥ 0.9 vs overwrite | not reconciled; never compare across sources |

## 3. Theory standing

**F, the supplied rewrite field, as stated.** The claim (W2-6 §3) is that fate is computable from the iterated Φ under W, against the *realized* partner distribution, with no lineage term.
- **Rungs 4–5.** W2-14 shows the claim is unfalsifiable there, because the world computes itself.
- **Rungs 1–3.**
  - BASE: "no over-prediction" at 0/40 cannot separate 0.0003 from 0.031.
  - ATOMIC: never compared at a matched horizon (F6).
  - The one field-vs-free contrast on a matched readout (ATOMIC B163: FREE BANK 13/40 vs FIELD BANK 10/30, p = 1) is *consistent with* no lineage term, but has no power.
- **Absorption.** W2-17's morph was absorbed through the mutation kernel (T1 inside F), as were the hijack (T5), erosion (T7) and the partner lever. **No frozen quantitative prediction made at a falsifiable rung has yet been passed.**
- **Standing:** a framework (ordinal, descriptive), not a tested theory.

**Falsifiable restatement, F\*.** For founder genotype g in cell c under write-back W, three readouts must match within the stated tolerance:
- P(reach ≥ 27 certified births);
- P(occupancy ≥ 40 at 300 epochs);
- P(≥ 163 | ≥ 27).

They are matched against a multitype branching process with these properties:
- the types are g and its realized variants;
- each type's offspring law is measured statically against an **exogenous** partner stream drawn from the founder-free BANK at the matching epoch (rung 3);
- **offspring laws do not depend on partner kinship.**

F\* is killed by any of these:
1. FIELD vs FREE BANK differ by more than 0.05 in P(occupancy ≥ 40 at 300). This is W2-22's own test; freeze the tolerance now.
2. An implanted morph founder's runaway rate falls outside the 95% band of its static-law escape (Experiment 1).
3. A kin-swap ablation (each kin partner replaced by a bank partner with matched register state) moves P(≥ 163 | ≥ 27) by more than 0.2.

**T4(a), home advantage.**
- It is still untested directly.
- Its only data are the contested k = 4 excess (F18).
- W2-17 a7 rejects kin as the cause of the departure: kin repair is 60–75% of conversions at q ≥ 0.3, but the S1 net stays ≤ 0.
- F\* with morphs predicts β = 1 exactly. A frozen β > 1 would be the first positive evidence for R.

**T4(c′), generic evolved epistasis.** "Not needed" on a corruption readout (F15). It is not excluded: CI upper bound +1.46 pp, every point estimate positive. W2-20 (prereg) and a deletion arm decide it.

**T4(c).** Dead as specified (S3); unchanged.

## 4. Handoff candidates (ranked)

### Strongest new result since Wave 1
1. **Partner execution of a donor's own code after the pc wrap is the dominant loss mechanism in the static harness.**
   - N1: LDIR knockout gives 0/1,500 overwrites in every cell.
   - W2-3 K3: knockout gives 0/60 chain relabels (p = 2.4e-13).
   - W2-16: with no partner run, 17/17 and 1020/1020; 300/528 damage events are the copier's own LDIR.
   - N2 predicts the epoch-1 loss: 0.21 vs 0.28.

   Several clean knockouts back it. It is limited to one harness and has not been shown in-world.
2. **W2-19: H1 competence was a cached single draw.**
   - The true held is exactly the 0.495 echo floor.
   - There were 0 readers in any H1 population.
   - The true I of 0.125–0.142 flips C9-H1R below its own threshold.

   This is the highest-confidence result of the wave, but it is a ruler result.
3. **W2-14 + W2-17 joined (as restated in F8).** BASE reach is the ordinary subcritical lottery. Post-27 persistence is a 4/4-vs-1.2% anomaly, associated with side-0 event types in deep chains. It is the most consequential result, but the weakest of the three after F1–F5.

### Strongest Wave-1 conclusion weakened or killed
1. **"Internalization pays because newborns inherit the victim's registers"** (SYN stage 4, C11 cause).
   - The FAIR ZERO no-payoff arm shows sweeps without payoff (185/187).
   - The only victim-channel test was null.
   - It was the mechanistic core of the "alter itself" answer.
2. **"Zero is special for establishment"** (C-ZERO-SPECIFIC reading).
   - 14/16 donors cannot copy from 0x5A at all.
   - Within the two dual donors the order reverses (ZERO 1/6, CONST 2/6, RANDOM 3/6).
3. **"Fate decided in 3–10 epochs; BASE depth is bistable with a gap"** (C6 + C10).
   - The gap premise is broken.
   - The runaway/burst split happens at epochs 10–50 (F13).

### Most important unresolved contradiction
1. **Founder independence (F18).** The k = 4 excess (z ≈ 3.5 plugged; p = 0.005 within experiment) against joint p values of 0.108 and 0.13. It is the only bearing on T4(a), and F\* with morphs predicts β = 1.
2. **Founder vs morph per-call m (F4/F5).**
   - The founder reads 0.85 at n = 30 but 1.17 against realized partners.
   - The morph advantage reads +45% or +6%.
   - The switch rate reads 3.5% per birth against 7.5e-4 reachable.

   This decides whether the two-type story is "subcritical vs supercritical" or "two near-critical types plus luck".
3. **ATOMIC calibration (F6).** Three map predictions agree with the world, while W2-14's process "fails". The comparison is horizon-mismatched, and 10 CPU-min decides it.

### Strangest observation
1. **Takeover without a measured reproducer.**
   - 4/16 takeovers end with 0 competent genomes while L = 0.66–1.0.
   - ffa6 27000053 creeps L 0.18 → 1.0 over 1,200 epochs with 8–33 competent genomes and 0 state-free genomes throughout.
   - The ruler (N13) is the likely cause, but this is unverified.
2. **3 of 12 runaways root outside the founder's labelled family** through frameshift label leakage (W2-17).
3. **A one-bit change, 43→C3 (POP BC → JP), raises own-half survival 0.72 → 0.94** without changing conversion. The mechanism is untraced (N17e).

## 5. The three most decisive experiments not yet authorized

### Experiment 1: implanted-morph founders under BASE
- **Design.**
  - X-TICKET physics: 7ae3 cell, BASE, splice-off, horizon 300, world.Runner.
  - Arms: founder, 44→ac, 37→81; 128 seeds each, the same seeds across arms.
  - Log the per-epoch causal births and the event side.
- **Cost.** About 2–3 CPU-h. W2-14 ran about 25 s per 300-epoch run.
- **Frozen predictions:**
  - **H-SUPER** (two-type, supercritical morph; W2-17): P(B ≥ 163) for a morph founder ≥ 0.15, and ≥ 4x the founder's rate.
  - **H-NEAR** (per-call +6% under realized partners; N17e): the morph's rate is ≤ 2x the founder's (≤ 0.08).
  - Under both, the founder arm reproduces 0.031 ± its CI as a positive control.
- **What each outcome kills:**
  - ≤ 0.08 kills "supercritical morph" and with it the W2-17 headline.
  - ≥ 0.15 kills "near-critical plus luck" and makes the morph a *sufficient* type.
  - Morph-arm runs that reach 27 but do not persist would show that persistence needs something beyond the morph: a field or kin term, which bears on F\* and R.

### Experiment 2: same-batch founder independence with morph logging
- **Design.**
  - BASE, X-TICKET physics, splice-off.
  - Arms: k = 1 (320 seeds) and k = 4 identical founders (160 seeds), in the same batch with the same seed scheme.
  - Endpoints:
    - primary: d ≥ 5 at 300;
    - secondary: B ≥ 163.
  - Log the epoch at which each founder's family first shows S0 events.
- **Cost.** About 3–4 CPU-h.
- **Frozen predictions:**
  - **F\*/T7:** P4 = 1 − (1 − P1)⁴ within the binomial 95% band, with β̂ CI covering 1.
  - **R/T4(a):** P4 exceeds that band, with β̂ lower bound > 1.
  - **Morph-mediated:** k = 4 morph-arrival epochs are 4 independent clocks; the excess, if any, is not explained by earlier morphs.
- **What each outcome kills:**
  - β = 1 kills T4(a)'s only existing evidence (C-CRITICAL-MASS was a batch artifact).
  - β > 1 with independent morph clocks kills F\*'s "no kinship term".

### Experiment 3: F\* rung-3 calibration under ATOMIC, matched horizon
- **Design.**
  - FIELD+FULL (the world, bit-exact) on C-ATOMIC 7ae3 seeds 0–29 at 300 epochs, scored with the three readouts W2-14 used.
  - Alongside it, the frozen FIELD BANK prediction already on disk: B163 0.333, maxA40 0.467, CI [0.30, 0.64].
  - Then FREE BANK vs FIELD BANK at 120 seeds each.
- **Cost.** About 10 CPU-min for the matched-horizon part, plus about 1 CPU-h for the FREE/FIELD contrast.
- **Frozen predictions (F\*):**
  - world maxA40 at 300 lies inside [0.30, 0.64];
  - FREE vs FIELD maxA40 (or B163) differ by ≤ 0.10.
- **What each outcome kills:**
  - World ≥ 0.70 at 300 kills F\* at rung 3 for ATOMIC (a real under-prediction).
  - World inside the band withdraws "ATOMIC validation did not pass".
  - FREE ≠ FIELD by more than 0.10 kills "no lineage term".

**Cheap static items, run first** (each ≤ 5 CPU-min):
- F2 timing over all 12 runaways;
- F4 at NP = 1000 with bank partners;
- F5 edge diffs;
- F18 frozen LRT;
- F11 re-derivation of the D10 counts.

## 6. Ledger entry (W2-25)

- **Question.** Where does the current Wave-2 picture contradict itself, compare unlike readouts or overclaim? What is F's standing, and what goes in the handoff?
- **Evidence.**
  - The ledger through 01:46Z; all W2 REPORTs; W2-18; SYN and THEO.
  - JSON reads: W2-2 a2/a7, W2-14 a1/a2, W2-17 a4/a5/a6/a9 and r3_out, N17 neighbours/bank_assay, W2-12 table_summary, and the C-A3 and C-ATOMIC result files.
  - One new timing check (F2), under 1 CPU-min.
- **Inference.**
  - W2-17 is misstated (2/3, not 2/2). Its morph follows the burst in 2 of 4 runaways. Its "types" are event sides. Its supercriticality is outcome-conditioned. Its founder m of 0.85 is a 30-partner draw (0.96–1.17 at n ≥ 400).
  - The reconciled statement: reach is the ordinary lottery; post-27 persistence is a strong anomaly (4/4 vs 1.2%) associated with side-0 events.
  - W2-14's ATOMIC "fail" is horizon-mismatched.
  - W2-8 D10's ternary-L premise is false.
  - THEO has no Wave-2 block.
  - F is unfalsifiable as practised. F\* is proposed.
  - Founder independence is the key open contradiction.
- **Confidence.**
  - High: F1, F9, F11 and F14 (read from disk); F2 for the 4 X-TICKET runaways.
  - Moderate: F4–F7 and F10 (arithmetic on recorded values).
  - Moderate-low: F18's β back-of-envelope, which awaits W2-12's model.
- **Strongest objection.**
  - F2 covers only the 4 X-TICKET runaways. The 8 CRW/CNR/XH2N runaways may show the morph first.
  - The event side may be a good genotype proxy (heritability 0.86–0.93), which would weaken F3.
  - W2-14's ATOMIC gap may turn out real at a matched horizon.
- **Unresolved.**
  - Whether a morph is necessary for persistence.
  - The routes of side switching (F5).
  - The β model's arm set (F18).
  - Whether D10's 8/4/3 survives without its premise.
- **Next questions.**
  - Run the five cheap static items in §5.
  - Then Experiments 1–3, in that order, if authorized.
  - Freeze W2-22's tolerance as F\*'s kill criterion before it reports.
