<!-- DEPOSITED VERBATIM by Ananke for worker W-M; sha256(report)=d00d0163e5a151ee; delimited; see REPORT.provenance.json -->
W-M REPORT: T-INS-6, the mixture test for the carrier-swap instrument
(E-ANANKE-W-M, thr-8c7342a7d513 / T-INS-6, MWO-0001)

WHAT I TESTED

1. The algebra behind the question (PLAN.md s0)
   - Take a mirror pair A, B. A site swap gives A'=(site_B, chan_A). A channel swap gives A''=(site_A, chan_B), which is the same state as B'.
   - If no mirror-different input arrives before the readout, then out(A, chan) = out(B, site). Call this IDENTITY. It forces site_acc + chan_acc = 1.
   - Under IDENTITY, each (pair, trial) is one of three patterns:
     - S: site-follow
     - C: channel-follow
     - N: neither. Both chimeras give the same answer.
   - At pair level, site_acc = fC + fN/2 and chan_acc = fS + fN/2.
   - So "both swaps at chance" comes out the same for a 50/50 S/C per-trial mixture and for 100% N. The sum cannot tell them apart. The pattern census can.

2. The instrument, in W-M/lens_ins6.py (imports prometheus.ananke.lens; no frozen file edited)
   - run_arms: the batched arms promoted from W-I traj.run_arms. It has two modes:
     - EVERY: W-I's design, the swap is applied in every trial.
     - SINGLE: the swap is applied in one trial k only, only trial k is scored, and the run stops early after that readout.
   - selfcheck: checks that batched arms are bit-identical to lens.run.
   - census: per (pair, trial) with both partners normal-correct, it reports:
     - outcome identity and raw-S0 identity;
     - the pattern fractions fS, fC, fN;
     - world-level phi (corr of site-swap-wrong with channel-swap-wrong).
     All with 99% pair-bootstrap CIs (2000 draws).
   - classify (frozen): UNDEFINED/IDENTITY-BROKEN (eligible < 20 or identity < .90), SITE (fS >= .8), CHANNEL (fC >= .8), MIXTURE (fS, fC >= .15, fS + fC >= .7 and phi hi99 < -.3), NEITHER (fN >= .5), else UNRESOLVED.
   - census_follow: a secondary census, deviation D1 (details under DISAGREEMENTS AND DEVIATIONS).
   - handoff: the frozen KA7 rule.
   - twin_profile: promoted unchanged (the two-axis physical profile).

3. Application
   - The 7 census-JOINT cells plus designed echoes E2 (gap 11, the known answer) and E1 (gap 7, the must-fail input).
   - Offsets -1 .. ro_off-1, trials 1..n-1, both modes.
   - 64 worlds (seeds 0x5EE for the cells, 0x5F1 for E1/E2).

RESULTS (classes are SINGLE mode; 99% pair-bootstrap CIs)

P1 held. In SINGLE mode the outcome identity is 1.00 at every offset o >= 1 in all 7 cells. At o = 0 it drops to .32-.51, as expected, because the second cue tick arrives after the swap. In HOLD (E1/E2) it is .93-1.00 even though distractors arrive after the swap: the raw S0 values differ but the signs do not.

P2 was wrong. In EVERY mode, history across trials broke the identity in 5 of 7 cells:

| Cell | EVERY-mode identity |
|---|---|
| 369f5a5b | .34-.48 |
| 8c37f32e | .52-.79 |
| 4781b0a1 (o <= 7) | .72-.94 |
| c16d5231 | .87 |
| e06701a5 (follow census) | .72-.89 |
| 2dccdaa5 | 1.00 |
| 78f3b0ec | 1.00 |

Meanwhile W-I's pair-level sums stayed at .97-1.01, so a sum near 1 is not evidence that the identity holds.

Classes per cell:

- **2dccdaa5** (same in both modes)
  - CHANNEL at o1-4, SITE at o6-7.
  - o5 (W-I "M") is a MIXTURE: fS .62 [.53,.69], fC .36 [.28,.44], phi -.98 [-1.00,-.93].
- **c16d5231** (EVERY: IDENTITY-BROKEN at every offset)
  - o1-3: CHANNEL, fC .84 [.76,.91]. The follow census says MIXTURE, fS .26 [.20,.32].
  - o4: MIXTURE, fS .29 [.22,.35], fC .70 [.62,.78], phi -.93 [-.98,-.87].
  - o5 (W-I "M"): MIXTURE, fS .67 [.62,.72], fC .32 [.27,.36], phi -.94 [-.98,-.88].
  - o6-7: SITE.
- **8c37f32e** (EVERY: all broken)
  - CHANNEL at o1-4, SITE at o6-7.
  - o5 (W-I "J"): UNRESOLVED, with fS .53 [.46,.61], fC .25 [.17,.34], fN .21, phi -.29 [-.40,-.18]. The follow census says MIXTURE (phi -.54).
- **e06701a5**
  - The frozen census is UNDEFINED: this specimen abstains on one cue sign, so no pair-trial has both partners correct.
  - Follow census: EVERY is broken; SINGLE gives CHANNEL at o1-4, UNRESOLVED at o5 (fS .51, fC .13, fN .36), SITE at o6-7.
- **78f3b0ec**
  - The frozen census is UNDEFINED (also an abstainer).
  - Follow census (same in both modes): SITE at o1-8, MIXTURE at o9 (fS .68 [.62,.74], fC .16 [.11,.22], phi -.55 [-.70,-.39]), UNRESOLVED at o10-11, CHANNEL at o12-13, MIXTURE at o14 (the mirror of o9), UNRESOLVED at o15.
- **369f5a5b** (EVERY: all broken)
  - o1-14 UNRESOLVED: a three-way blend with fS .39-.77, fC .04-.21, fN .12-.41, and phi with CIs spanning 0 (not a mixture).
  - o15 SITE: fS .84.
- **4781b0a1** (MAJ)
  - o1-5 and o7 UNRESOLVED: site plus neither, fS .36-.77, fN .22-.49.
  - o6 NEITHER (fN .55). o8 NEITHER in SINGLE, UNRESOLVED in EVERY.
  - o9-11 UNRESOLVED. o11 (W-I "M") has fC .59, fS .19, fN .23, phi -.32 [-.48,-.13]: not a MIXTURE.
  - o12-13 CHANNEL (fC .87). o14-15 UNRESOLVED.
- **E2** (same in both modes)
  - CHANNEL at o0-2 and o4-6.
  - MIXTURE at o3: fS .42 [.36,.48], fC .51 [.44,.58], phi -.88 [-.94,-.80]. This is the relay neighbour's inbox versus the packet still in flight.
  - MIXTURE at o7 (lag -6): fS .48 [.39,.57], fC .50 [.41,.59], phi -.98 [-1.00,-.95].
  - SITE at o8-12.
  - The two-CHANCE result that designed_echoes reported at lag -6 is a real per-trial S/C mixture: the echo return time jitters from trial to trial.
  - E1 matches E2 exactly up to o8. The echo return sets the handoff time, and E2's pipeline adds 4 site ticks after it.

P3 was wrong. W-I's "M" offsets resolve as MIXTURE (2dccdaa5 o5, c16d5231 o5, 78f3b0ec o9 and o14) or UNRESOLVED (78f3b0ec o10, o11, o15; 4781b0a1 o11), never as NEITHER. NEITHER appears only at 4781b0a1 o6 and o8, which W-I labelled "J".

Does the single-trial variant change any classification? Yes. Under the frozen rule these change:
- c16d5231 o4 and o5: IDENTITY-BROKEN becomes MIXTURE.
- Follow census: c16d5231 o1-3 and 8c37f32e o5 become MIXTURE.

More generally, SINGLE mode turns every identity-broken EVERY offset in c16d5231, 8c37f32e, 369f5a5b, 4781b0a1 and e06701a5 into an interpretable class. Where both modes were informative (2dccdaa5, 78f3b0ec, E1, E2, and 4781b0a1 o6/12/13), the classes agree 100%. No cell flips between two informative carriers (for example CHANNEL to SITE). So P4 held only partly.

KNOWN-ANSWER TESTS (each with the input that makes it fail; the failure is asserted in the tests)

| Test | Result | Must-fail input, shown to fail |
|---|---|---|
| KA1: latch (hold_latch) reads SITE, fS = 1, identity 1 | PASS | echo reads not SITE |
| KA2: echo_hold reads CHANNEL, fC = 1 | PASS | latch reads not CHANNEL; neither plant reads MIXTURE |
| KA3: no-memory plant (null) reads UNDEFINED, 0 eligible | PASS | latch reads not UNDEFINED |
| KA4: statistic on synthetic tables | PASS | see note (a) |
| KA5: identity is 1 after the cue (latch, echo, RELAY relay_flood) | PASS | swap at o = -1 breaks identity (IDENTITY-BROKEN) |
| KA6: batched EVERY and SINGLE arms bit-identical to lens.run | PASS | lens.run hooked at the wrong trial's tick does not match |
| KA7: E2 designed channel-to-site handoff | PASS in both modes | see note (b) |
| D1: follow census reduces to the frozen census when both partners are correct | PASS | chimeras swapped read CHANNEL; a sign flip breaks identity |
| Twin profile equals W-I traj.twin_profile bit-for-bit; echo shows flight differences, latch shows none | PASS | latch versus echo |

(a) KA4 details. The two cases share site_acc = chan_acc = .5 and sum = 1, yet 50/50 S/C reads MIXTURE (phi -1) and 100% N reads NEITHER (phi +1). The must-fail inputs:
- 95% S + 5% C gives phi = -1.00 but reads SITE. The degenerate-marginal trap is stopped by the fraction rule, not by phi.
- S + N gives positive phi and reads UNRESOLVED.
- An X-broken table reads IDENTITY-BROKEN.
- 8 pairs reads UNDEFINED.

(b) KA7 details. Channel-dominant at o0-2 and o4-6; the SITE run starts at o8 (lag -5, inside the frozen window -8..-4). Rules a, b, c and d are all true. The must-fail inputs:
- E1 fails (b) and (d): it is CHANNEL at lags -4 and -3. This is shown on the full 64-world run and in pytest.
- The latch fails (a).
Caveat: the KA7 windows were frozen after I read instruments.json, so (b) and the E1 must-fail were partly known in advance. (a), (d) and the lag -6 mixture were not.

DISAGREEMENTS AND DEVIATIONS

1. With the brief's premise. The sum is not only unable to diagnose a mixture; in EVERY mode it is not even evidence that the identity holds. For example, 8c37f32e has sums .97-1.01 while per-trial identity is .52-.79. The EVERY-mode swap does not reliably measure the trial it scores.

2. With W-I (the only worker interpretation I read, via its traj_table labels and phi values).
   - W-I's "M" label is ambiguous by construction.
   - W-I's phi values in c16d5231 (-.64, -.72) and 8c37f32e were computed on identity-broken EVERY arms. In SINGLE mode they become -.93/-.94 (c16d5231 o4/o5) and -.29 (8c37f32e o5).
   - W-I's identity for 369f5a5b was .65 over all trials; mine is .43 because I count only pair-trials where both partners were correct.
   - 369f5a5b "J" is not joint carriage in a clean sense. It is a three-way S/N/C blend with phi near 0.

3. With designed_echoes/PLAN.md. It predicted that E2 would FLIP on channel or pay1 at lag -6 or -4. In fact lag -6 is an S/C mixture, lag -4 is SITE, and the channel phase ends at lag -7.

4. Deviation D1 (logged, made after seeing results). The frozen census requires both partners to be correct, so it is blind to one-sided abstainers (78f3b0ec, e06701a5). I added a secondary sign-based "follow" census. Its results are reported separately and marked.

5. A bug in D1, found and fixed (LOG A7). Its identity check used raw S0 equality where it should use sign equality. The fix is recomputed from the raw arrays in out/summary.*. The follow blocks inside census_<spec>.json for the 8 specs launched at 03:51Z are stale; census_e06701a5.json ran after the fix.

6. P2, P3 and P4 were wrong or only partly right, as described above.

PYTEST

`python -m pytest roles/Ananke/research/workers/W-M/test_lens_ins6.py -q` gives 20 passed in 227.81 s, RC=0. It is CPU only with 2 threads. The E1/E2 known-answer fixtures account for most of the time.

LEASES

- Fabric lease `lse-10ae2cf693e4`, taken as `--as Ananke` on `skullport:cpu8` from 03:43Z to 04:44Z. It was renewed once (ttl 5400 s) and RELEASED at 04:44Z; `fabric lease status` no longer lists it.
- Peak use was 4 processes × 2 threads, plus a 2-thread pytest while 3 processes were running. No GPU.
- No git writes. Nothing outside W-M was modified according to git status (only .pyc caches from imports).

FILES (all under F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-M/)
- PLAN.md, LOG.md (A0-A12)
- lens_ins6.py, test_lens_ins6.py
- apply.py, summarize.py, smoke.py
- out/census_{2dccdaa5,c16d5231,78f3b0ec,8c37f32e,e06701a5,369f5a5b,4781b0a1,E1,E2}.json
- out/raw_<spec>_{every,single}.npz
- out/summary.txt and out/summary.json (these are the authoritative tables)
- logs/apply_*.log, logs/pytest.log

Proposed follow-ups:
- Make SINGLE mode the default for the carrier-swap instrument, since EVERY mode lets history break the identity.
- Promote census_follow for abstainers.
- Split 369f5a5b and 4781b0a1's N fraction by sub-array (S, inbox, Kp, flight content) to name the interaction.
