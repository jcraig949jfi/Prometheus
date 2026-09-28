<!-- DEPOSITED VERBATIM by Ananke for worker W-L; sha256(report)=79667d243617dc56; delimited; see REPORT.provenance.json -->
# W-L REPORT: is a retention regime reachable when the task rewards it? (T-RET-EVO)

Worker W-L. Namespaces 0x5F2 (analysis) and 0x5F3 (held-out). Directory: roles/Ananke/research/workers/W-L/ (PLAN.md frozen before any check or search; LOG.md Attempts 0-6; scripts nback.py, checks.py, checks_v2.py, carriers.py, run_search.py, run_all.sh, carriers_champs.py, lagprofile.py; raw outputs in out/). Context: I did not read SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD, ARC3_PRIORITIES or any REPORT.md.

## What I tested
- **Physics and search.** Physics is M2 (4ab2ba014aac967e) unchanged: ring 144, radius 3, state_dim 2, prog_len 16, wimm 1, plastic_route 1, sync period 2. The search is the unedited search.evolve with the M2 cell's recorded SearchSpec (pop 96, gens 36, M 8). The n-back builder is injected by monkeypatching envs.build inside my process only. No frozen file was edited.
- **Task (N-BACK).** The timing is HOLD's: one site is both sensor and actuator, cue_len 2, gap 8 with ±64 distractors, iti 2, 12 trials. The readout of trial k is scored against c_{k-n}, and trials k &lt; n are unscored. Mirror worlds negate the whole cue and distractor sequence.
- **Arms.** n=1 and n=2 with 4 seeds each, plus a pipeline control n=0 (HOLD through my builder) with 2 seeds.
- **Success criterion (preregistered).** On 64 held-out worlds from 0x5F3, both must hold:
  - lo99 &gt; .60;
  - the paired difference against the best no-memory baseline (NULL, LAG0 latch, and for n=2 a lag-1 plant) has lo99 &gt; 0.

## Task validity (PASS, after one logged deviation)
- **Target independence.** Across 4096 fresh worlds, agreement between the target and every other cue lag is .487-.514. Agreement with the sign of the distractor sum is .500-.505. The mirror check is exact.
- **Sequential-exploit test, exhaustive on the host.** Every boolean function of the other lags scores at most .504.
- **Sequential-exploit test, through the engine on 512 worlds.** LAG0 scores .509 (n=1) and .495 (n=2); the lag-1 plant scores .498 on n=2. All CIs contain .5.
- **Deviation.** Two of my original T1 checks were badly specified, and one engine bound (hi99 &lt; .60 at 32 pairs) was too tight for the sample. I fixed the checks and re-ran them on fresh samples; details are in LOG Attempts 1-2. No task defect was found.

## Plants (the question is well posed)
All plants run at M2 physics and prog_len 16, and each scores 1.000 [1.000, 1.000] on both namespaces:
- **P1S** (n=1): 9 lines, bit held in S1.
- **P1K** (n=1): 13 lines, bit held in Kp through WIMM.
- **P2S** (n=2): 16 lines, two bits packed into S1.

The carrier-swap instrument gives the expected answers on these plants:
- P1S and P2S: S FLIP, everything else NO-EFFECT, reset_S drops accuracy to .50.
- P1K: Kp FLIP, S NO-EFFECT.

## Searches
All 10 ran on the GPU under a lease (about 62 s each); the lease is released. Held-out results on 0x5F3:

| run | acc | CI | vs baseline | result |
|---|---|---|---|---|
| n1 s0 | .686 | [.642, .737] | vs LAG0 .528 | SUCCESS |
| n1 s1 | .513 | | | fail |
| n1 s2 | .629 | lo .581 | | fail |
| n1 s3 | .737 | [.695, .783] | | SUCCESS |
| n2 s0 | .620 | lo .558 | | fail |
| n2 s1 | .671 | [.617, .723] | vs lag-1 plant .522 | SUCCESS |
| n2 s2 | .691 | [.639, .744] | vs lag-1 plant .547 | SUCCESS |
| n2 s3 | .489 | | | fail |
| n0 control s0 | .672 | lo .637 | | reached |
| n0 control s1 | .512 | | | not reached |

**Preregistered readings:** n=1 REACHED (2/4), n=2 REACHED (2/4), neither robust. The zero_comm accuracy equals normal accuracy in every SUCCESS, so the mechanisms are local and use no packets.

## Carrier (what the search actually built)
- **Only site state S carries the bit.** In every SUCCESS champion (and the n1_s2 near-miss), only the S swap moves accuracy: it falls to .32-.39 against a normal of about .60, i.e. at or below 1 − normal. Kp, w, inbox, channel_all, pay0 and pay1 are all exactly NO-EFFECT. Only reset_S hurts. For n=2, swapping one trial further back shows S again. Kp and routing are never used, even though WIMM instructions appear in the programs.
- **Formal verdict is CHANCE, not FLIP.** When normal accuracy is about .6, even a complete transfer only reaches about .4, so the FLIP rule (hi99 &lt; .40) cannot fire at this accuracy. This is a limit of the rule, not evidence of a split carrier.

## What surprised me (post-hoc, not preregistered)
A lag-agreement profile (256 fresh worlds) measures how often the champion's answer matches the cue j trials back, for j = 0..4:
- **n1_s0, n2_s1, n2_s2 and n2_s0 are pure integrators.** Their profiles are flat at .60-.65, matching an S0 += SENSE plant (.63-.65). They answer with the sign of the summed cue history, which beats chance on any lag, including the current cue. The decompiled programs agree (n2_s2 runs S0 += SENSE twice).
- **n1_s3 is a weighted integrator.** It has a lag-1 peak (.694 against .588 at lag 0 and .513 at lag 3).
- **Only n1_s2 is lag-selective, and it failed the criterion.** Its profile is .513 / .635 / .510 / .384 / .487, including a negative weight at lag 3.
- **No champion built a selective lag-n store like P1S or P2S**, and no n=2 champion shows any preference for lag 2.
- **The n=0 control champion is also an integrator.** The search reaches retention as a side effect even when the task rewards only the current cue.

## Answer
- **A retention regime is reachable** by the declared search at the M2 budget (4/8 searches pass the frozen criterion, carrier = S).
- **What it reaches is integration** (S accumulating the whole cue history), not selective lag-n retention.
- **Selective lag-2 retention was not reached** (0/4), even though a 16-line plant solves it perfectly at the same physics and program length. At this budget that is a search-reachability limit, not a physics limit.
- **Caveat on the criterion.** A pure integrator scores about .63, so it passes the preregistered .60 bar. The frozen criterion cannot tell "retains" apart from "retains selectively". The integrator finding is post-hoc.

## DISAGREEMENTS
- **With the brief's premise** that champions don't retain because tasks never reward it: at this budget the search builds a retaining integrator even on HOLD (n0_s0). The absence of retention in the C1 champions is therefore not explained by task incentive alone; a lag-0 latch simply wins when it is found.
- **With my own PLAN.**
  - Criterion (b) cannot be met for n=0, because LAG0 is the n=0 solution; I read the control on (a) only.
  - Criterion (a) is too weak to show selective retention, since an integrator passes it.
  - The swap FLIP rule has an eligibility gap below about 0.8 normal accuracy.

## Proposed follow-ups
1. A preregistered selectivity criterion: the answer must beat an integrator on lag n, for example lag-n agreement minus the maximum agreement at other lags, with lo99 &gt; 0. Re-run n=1 and n=2 with 8+ seeds.
2. Budget scaling (gens 36 → 144, pop 96 → 384) to see whether selective stores appear.
3. A distractor-cue variant, where old non-target cues carry opposite-sign weight, so integration no longer pays.
4. A lower-accuracy variant of the swap verdict (swap acc ≤ 1 − normal with a CI).
