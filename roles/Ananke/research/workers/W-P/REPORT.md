<!-- DEPOSITED VERBATIM by Ananke for worker W-P; sha256(report)=d56d1a56a4695d7d; delimited; see REPORT.provenance.json -->
W-P REPORT: T-INS-8 (successor of T-INS-6, thr-8c7342a7d513), E-ANANKE-W-P, MWO-0002
What interaction produces the N ("neither") fraction in 369f5a5b (RELAY) and 4781b0a1 (MAJ)?

WHAT I TESTED

1. The algebra (PLAN.md s0, frozen before any run on the champions)
   - After the cue (o >= 1), the readout depends only on the state at the swap tick.
   - I split that state into sub-arrays and ran the FULL truth table: every subset z of sub-arrays swapped between mirror partners.
   - f(z) = 1 means world A with swap set z gives world B's answer.
   - IDENTITY says world B with swap set z behaves like world A with the complement of z. That lets me read the whole cube from half the blocks.
   - For each eligible (pair, trial) I computed:
     - the relevant set R: the sub-arrays that change f anywhere in the cube;
     - the function class: DICT (one sub-array decides), AND/OR, MUX (a 3-variable gate), or HIGHER;
     - the minimal decisive set: the smallest Z where f(Z) = 1 and f(complement of Z) = 0.
   - A lemma, proved in PLAN.md: N always needs at least one site and one channel sub-array in R. So "N is a site x channel interaction" is true by construction. The real content is WHICH sub-arrays and WHAT function.
   - Two hypotheses compete:
     - JOINT-2: exactly two sub-arrays in R, combined by AND/OR. The readout takes a "dominant" sign d unless both carriers hold the other sign.
     - GATED: a 3-variable MUX, where a mirror-different gate or phase register chooses which carrier is read (the brief's alternative).

2. Instrument
   - W-P/tt.py: runs the normal worlds to the swap tick, takes a full-state snapshot, runs one chimera block per subset to the readout, SINGLE-trial.
   - Bit-identical to lens_swap.run_arms (normal / site_all / channel_all / joint SINGLE arms) on both champions and all 4 plants (C1: True x4 everywhere).
   - Worlds: assays.world_seeds(0x610, 256) = 128 mirror pairs; offsets 1..15; 99% pair-bootstrap CIs (2000 draws).
   - Coarse sub-arrays:
     - 369f5a5b: S, inbox (Acc_sum + Acc_cnt), Kp, r, Msum, Mcnt. w was left out of the main run because dest_mode 'all' never reads it; it is kept in the verification slice.
     - 4781b0a1: S, inbox, Kp, w, Msum, Mcnt.
     - E was dropped for both, because the economy is off.
   - Stage 2 (frozen procedure) refined the modal minimal decisive set into parts, at 3 offsets per cell. It covered only the stage-1 N pair-trials.

3. Deviations, made on wall-time grounds before any result was inspected
   - D1: trials cut from 1..11 to 369f5a5b {1..5} and 4781b0a1 {1,2,5,6,9,10}. This is still 245-495 eligible pair-trials per offset.
   - D2: the verification slice used offsets {-1,1,5,10,14} only.

RESULTS (fractions of N pair-trials unless stated; [99% CI])

The classes below come from the frozen rules; mechanism readings added afterwards are labelled "post-hoc".

4781b0a1 (MAJ): N is a clean two-carrier AND/OR.

| Offset | fN [99% CI] | Frozen class | JOINT-2 share [CI] | Polarity (share with d = +) |
|---|---|---|---|---|
| o1 | .27 [.21,.33] | JOINT-2(S, Msum) | .95 [.89,.99] | RECTIFIED(-), d+ .10 |
| o2 | .30 [.25,.36] | JOINT-2(S, Msum) | .97 [.93,1.00] | RECTIFIED(-) |
| o3 | .28 [.22,.33] | JOINT-2(S, Msum) | .98 [.94,1.00] | RECTIFIED(-) |
| o4 | .42 [.37,.47] | JOINT-2(S, Msum) | .97 [.94,1.00] | RECTIFIED(-) |
| o5 | .44 [.38,.49] | JOINT-2(S, Msum) | .98 [.95,1.00] | RECTIFIED(-) |
| o6 | .54 [.48,.60] | JOINT-2(S, Msum) | .91 [.85,.95] | d+ .14 [.09,.19] |
| o7 | .51 [.45,.56] | JOINT-2(S, Msum) | .88 [.83,.92] | d+ .18 [.13,.24] |
| o8 | .51 [.45,.57] | JOINT-2(S, Msum) | .79 [.73,.85] | d+ .24 [.17,.31] |
| o9 | .34 [.29,.40] | JOINT-2(S, Msum) | .74 [.66,.82] | d+ .30 [.22,.39] |
| o10 | .42 [.37,.48] | MIXED | .48 [.40,.56] | d+ .54 [.46,.62] |
| o11 | .29 [.25,.34] | HIGHER | .18 [.11,.26] | d+ .85 [.77,.92] |
| o12 | .15 [.10,.19] | HIGHER | .14 [.05,.22] | RECTIFIED(+) |
| o13 | .14 [.10,.18] | HIGHER | .06 [.00,.14] | RECTIFIED(+) |
| o14 | .35 [.31,.40] | JOINT-2(inbox, Msum) | 1.00 [1.00,1.00] | RECTIFIED(+), d+ 1.00 |
| o15 | .32 [.27,.36] | JOINT-2(inbox, Msum) | 1.00 [1.00,1.00] | RECTIFIED(+) |

- At o1-9, AND and OR each account for about half of the N trials; the minimal decisive set is {S, Msum} in 74-98% of them.
- The HIGHER class at o10-13 is itself a readable function (post-hoc): about 85-94% of N at o12-13 are Msum AND (S OR inbox), or its dual. The site half of the pair is held redundantly in S and inbox, and either copy is enough.
- Stage 2 names the parts:
  - o1: {S1, payload 1 of Msum}, 95% of N.
  - o6: {S1, payload 1 of Msum}, 91% of N.
  - o15: {Acc_sum, payload 1 of Msum}, 100% of N.
  - S0, payload 0 of Msum, and Acc_cnt are never relevant. Kp and w are never in R at any offset.
- Post-hoc: 4781b0a1 updates on every second tick (sync, update_period 2), and N is concentrated in one phase of that clock.
  - The swap tick's parity is set by t0 + o. The period is 19 (odd), so trials alternate phase.
  - Examples:
    - o4: fN .73 on even ticks vs .12 on odd ticks.
    - o14: channel-follow 1.00 on even ticks vs N .70 on odd ticks.
    - o15: site-follow 1.00 on even ticks vs N .64 on odd ticks.
  - So pooling trials mixes two clock phases, and part of each offset's S/C/N blend comes from this shared clock, not from state.
- Reading from the decompiled genome (interpretation, not checked tick by tick):
  - S1 := 256 * (S1 + SENSE > CNT0) is a one-sided latch holding 0 or 256.
  - PAY1 := MAX(IN0_1, SENSE) is also rectified.
  - These fit "+ needs both carriers", i.e. RECTIFIED(-) early.

369f5a5b (RELAY): N is not one interaction. It is higher-order early and a JOINT-2 of S1 with channel-1 packets late.

| Offset | fN [99% CI] | Frozen class | JOINT-2 share [CI] | HIGHER share | Polarity (share with d = +) |
|---|---|---|---|---|---|
| o1 | .33 [.26,.40] | HIGHER | .07 [.01,.16] | .81 | d+ .39 |
| o2 | .33 [.26,.40] | HIGHER | .11 [.03,.20] | .74 | d+ .51 |
| o3 | .36 [.28,.43] | HIGHER | .09 [.01,.19] | .69 | d+ .61 |
| o4 | .36 [.28,.43] | HIGHER | .14 [.05,.25] | .68 | d+ .68 |
| o5 | .40 [.31,.48] | HIGHER | .15 [.07,.23] | .76 | d+ .65 |
| o6 | .39 [.31,.47] | HIGHER | .25 [.14,.37] | .65 | d+ .71 |
| o7 | .39 [.31,.46] | HIGHER | .33 [.20,.48] | .54 | d+ .72 |
| o8 | .39 [.31,.47] | HIGHER | .28 [.15,.41] | .62 | d+ .78 |
| o9 | .42 [.34,.49] | MIXED | .51 [.36,.64] | .43 | d+ .81 |
| o10 | .36 [.28,.43] | MIXED | .54 [.40,.68] | .38 | RECTIFIED(+), d+ .95 |
| o11 | .33 [.26,.40] | JOINT-2(S, Msum) | .67 [.52,.82] | .28 | RECTIFIED(+) |
| o12 | .29 [.23,.37] | JOINT-2(S, Msum) | .62 [.48,.76] | .30 | RECTIFIED(+) |
| o13 | .22 [.16,.28] | JOINT-2(S, Msum) | .67 [.50,.82] | .24 | d+ .91 |
| o14 | .14 [.08,.20] | JOINT-2(S, Msum) | .79 [.59,.95] | .18 | RECTIFIED(+), d+ 1.00 |
| o15 | .06 | UNDEFINED (15 N trials) | — | — | — |

- Ties are 1-11% of eligible pair-trials.
- Early offsets (o1-8):
  - |R| is 3-5 in most N trials.
  - Kp is in R for 37-72% of them, r for 24-49%, Mcnt for 50-69%.
  - Only 39-56% of the functions are monotone.
  - In 10-22% of N trials a site-only set such as {S} is decisive on its own. For those trials a co-swapped Kp or r cancels S inside site_all.
  - Stage 2 at o1: the modal minimal decisive set is {S1, rest}, where rest = Kp, r, inbox and Mcnt lumped. Channel-1 packets are in R for 46% of N trials, channel-0 packets for 37%.
- Late offsets (o9-14):
  - The pair is {S1, channel 1 of Msum}: 53% of N at o9 and 69% at o13 in stage 2.
  - This fits the genome line S1 := MAX(IN1_0, SENSE + S1).
  - The dominant answer is + (RECTIFIED(+) at o10-12 and o14).
- GATED (MUX) never met its rule: MUX is at most 16% of N at any offset, in either cell.

Verdict on the question
- "Joint carrier" is right for 4781b0a1 at every offset and for 369f5a5b late (o11-14). The joint pair is the site latch S1 with the in-flight payload that feeds it.
- The "register that makes both chimeras answer the same" hypothesis gets no support as a state gate: MUX is at most 16% of N, and the frozen rule never classified any offset GATED.
- Post-hoc, the shared update clock does play that role in 4781b0a1: its phase decides whether a pair-trial reads C, S or N.
- 369f5a5b's early N is higher-order and involves Kp, r and Mcnt. My data do not reduce it to a single named interaction.

KNOWN-ANSWER CHECKS (plants in W-P/plants_joint.py; c1b_echo_physics, HOLD gap 8, offsets 3..8, seeds 0x611 x 64)

| Check | Result | Must-fail input, shown to fail |
|---|---|---|
| KA-AND (max_plant): readout S0 := MAX(arrival sign, S1), bit in both the latch and the echo | fN 1.00; JOINT-2(S, Msum) at every offset; RECTIFIED(+); minimal decisive set {S, Msum} in 100% | see rows below |
| KA-MUX (mux_plant): gate Kp[J] := cue sign; readout S0 := (Kp[J] > 0 ? S1 : arrival sign) | fN 1.00; GATED(Kp); R = {S, Kp, Msum} in 100%; minimal decisive set {S, Msum}; not JOINT-2 | — |
| Dictator controls | — | hold_latch: fS 1.00, 0 N trials, UNDEFINED. echo_hold: fC 1.00, UNDEFINED. Neither reads JOINT-2 or GATED. |
| Incomplete component list (KA-AND with Msum omitted), full cube, no identity assumption (ka_mustfail.py) | complete list: identity 1.0, decisive {S, Msum} in 32/32 | Msum omitted: identity .50, NO-DECISIVE in 32/32 |
| Synthetic classifier tables (test_ana.py, 6 passed) | AND and OR read AND/OR; MUX reads MUX; DICT reads DICT | XOR of 3 reads HIGHER; AND is not read as MUX or OR |
| C2 identity on the champions (trial 6, full cube) | 1.000 at o1/5/10/14 in both cells | o = -1: .265 (4781b0a1) and .602 (369f5a5b) |
| C3 w inert in 369f5a5b | w in R for 0 pair-trials | — |

- Found along the way (LOG A4): the half-cube shortcut on the Msum-omitted list reads a spurious fS = 1.00. The shortcut assumes identity, so the C2 identity check is essential for any half-cube result.
- In the C2 slices, a decisive set was found directly (no identity assumption) for every eligible pair at o >= 1.

DISAGREEMENTS

1. With my own predictions
   - P2 failed. Kp[7] enters 4781b0a1's readout line (S0 := IN0_1 - 3 + Kp[7]), but Kp is never in R. The site carrier is S1.
   - The polarity is RECTIFIED(-) early, not (+).
   - P3 held only partly.

2. With W-M
   - Agreement: the census numbers match W-M's within CIs. For example, 4781b0a1 o6 fN .54 vs W-M's .55; o12-13 fC .84/.86 vs .87.
   - W-M: "369f5a5b 'J' is not joint carriage in a clean sense". I agree for o1-8 (HIGHER, non-monotone, involving Kp/r/Mcnt). It is clean joint carriage at o11-14: JOINT-2(S1, channel-1 packets) in 62-79% of N.
   - W-M's per-offset "UNRESOLVED" blends in 4781b0a1 are partly a pooling of the two update-clock phases, which it did not separate.

3. With the corrections register (W-O corrections_WI.csv)
   - It re-letters 4781b0a1 o14 J->C, o15 J->S and o11 M->C, and 369f5a5b o2 J->S and o14 J->S.
   - Pooled over pair-trials, the dominant pattern supports those letters: 4781b0a1 o14 fC .56, o15 fS .60; 369f5a5b o14 fS .80.
   - But N stays at .35 / .32 at 4781b0a1 o14/o15. There it is a 100% JOINT-2(inbox, Msum), and it is .64-.70 inside one clock phase. The C/S letters hide a clean joint carrier in about a third of pair-trials.
   - 369f5a5b o2 is not SITE here: fS .45, fN .33, HIGHER.

4. With W-I: W-I's sub_chance "S+channel_content" at 369f5a5b o3-14 names the right pair for o9-14, but it misses the Kp/r/Mcnt involvement at o1-8.

LEASES
- Fabric lse-feb3419a6fe6 on skullport:cpu8, taken --as Ananke at 10:02Z. Renewed at 10:22Z (ttl 5400 s). RELEASED at 10:49Z; `python -m fabric lease status` then returned [].
- Incident (LOG A6): a launch I believed had failed had actually started 3 processes, plus a verify run they queued. For about 12 min, 7 processes ran (14 threads on the 8-thread lease). I killed the duplicates with taskkill after listing Win32_Process. No output file was written twice.
- After that: at most 4 processes x 2 threads. No GPU. No git writes. Nothing modified outside W-P. No processes left running (checked).

FILES (all under F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-P/)
- PLAN.md, LOG.md (A0-A12)
- Code: tt.py, ana.py, analyze.py, posthoc.py, stage2.py, run_champ.py, common.py, plants_joint.py, run_ka.py, ka_mustfail.py, test_ana.py, timing.py, launch*.sh
- out/summary_{369f5a5b,4781b0a1}.json and analyze_*.txt: per-offset tables with CIs and parity splits
- out/posthoc_*.json, out/recs_*.pkl
- out/s2_*.json (stage 2)
- out/verify_*.json (C2/C3)
- out/C1_*.json
- out/ka_plants.json, out/ka_mustfail.json
- Raw truth tables: out/tt_<cell>_{main_k*,verify_k6}.npz
- logs/*.log

Proposed follow-ups
- Stratify every carrier-swap census by update-clock phase when the physics is sync with update_period > 1.
- Split 369f5a5b's early "rest" (Kp, r, Mcnt) in its own stage-2 run to name the non-monotone S1-Kp-r interaction.
- Check tick by tick why Kp[7] is not mirror-different at 4781b0a1's readout.
