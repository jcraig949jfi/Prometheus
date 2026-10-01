<!-- DEPOSITED VERBATIM by Ananke for worker W-N; sha256(report)=1a2e5982a51addf7; delimited; see REPORT.provenance.json -->
W-N T-SWAP-LOWACC (E-ANANKE-W-N, thr-5df816e9b844, MWO-0001 B-10)

WHAT I TESTED
- The rule (swap_rel.py, frozen in PLAN.md before any specimen swap arm was run):
  - The unit is the mirror pair. a_i and s_i are the normal and swap accuracy of pair i over the SAME scored world-trials.
  - Three hypotheses: FLIP s = 1 - a, CHANCE s = .5, NO_EFFECT s = a. The boundaries sit halfway between them (z = (s - .5)/(a - .5) = -1/2 and +1/2), written as linear paired statistics DF = (s - .5) + (a - .5)/2 and DN = (s - .5) - (a - .5)/2.
  - CIs: 99% pair bootstrap, 2000 resamples, pairs resampled jointly for normal and swap.
  - Verdicts, checked in this order:
    - NOT_ELIGIBLE if lo99(normal) < p_min(P,K), where P = number of mirror pairs and K = scored trials pooled per pair.
    - FLIP_REL if hi99(DF) < 0.
    - NO_EFFECT_REL if lo99(DN) > 0.
    - CHANCE_REL if lo99(DF) > 0 and hi99(DN) < 0.
    - INDETERMINATE otherwise.
  - Every verdict needs its whole CI inside its own band, so CHANCE also needs a certificate.
  - Stated deviation from the brief: FLIP_REL certifies "closer to 1-normal than to .5", not "equal to 1-normal". Completeness is reported through z.
- Eligibility, computed before freezing (out/attain_table.json):
  - p_min is the lowest normal accuracy at which the rule gets all three truths right in at least 80% of 200 simulations.
  - The simulation is worst case: arm-independent noise, mirror-identical pair outcomes, K independent trials.
  - Values: P32 K3 = .91; P32 K11 = .73; P64 K3 = .81; P64 K11 = .67; P128 K11 = .62; P128 K12 = .61; P256 K10/K11 = .59; P256 K12 = .58.
  - So at W-L's design (P=32, K=3) nothing below .91 is eligible. My design was M=512 (P=256) with all scored trials.
- SINGLE vs EVERY: decided before running, the relative verdict is computed on SINGLE arms.
  - The pairing assumes an unswapped history before the swapped trial.
  - n-back reads the bit from trial k-n, so an EVERY swap moves several held bits at once.
  - EVERY was run on the 5 C1 cells for comparison only.
- A faster SINGLE-arm runner (plants_rel.run_fork): it deep-copies the normal world at the swap tick and steps the copy only to the readout. Its readouts are bit-identical to lens_swap-style run_arms and to lens.run on 3 plant configs (out/selfcheck_fork.json), and it is 5.5x faster.

RESULTS
- W-L n-back champions (M=512, K=11 for n=1 and K=10 for n=2, swap at k*Pd-1, and also back1 for n=2):

| Champion | normal [lo99] | S / site_all swap [99% CI] | z |
|---|---|---|---|
| n1_s0 | .656 [.636] | .351 [.332, .370] | -.95 |
| n1_s3 | .717 [.701] | .284 [.267, .302] | -1.00 |
| n2_s1 back0 | .645 [.624] | .352 [.328, .376] | -1.02 |
| n2_s1 back1 | .645 [.624] | .351 [.331, .371] | -1.02 |
| n2_s2 back0 | .641 [.620] | .350 [.327, .374] | -1.06 |
| n2_s2 back1 | .641 [.620] | .353 [.333, .372] | -1.05 |
| n1_s2 (near-miss) | .640 [.622] | .349 [.331, .370] | -1.08 |

  - S and site_all are FLIP_REL on every champion, so the carrier is S, as predicted.
  - channel_all, inbox and Kp are NO_EFFECT_REL, but trivially: the swap score equals normal exactly.
  - The absolute rule on the same data also gives FLIP everywhere.
  - Rerunning at W-L's own design (64 W-L seeds, trials 4, 6, 8) reproduces W-L's numbers exactly (n1_s0 normal .583, swap .323). There the absolute rule says CHANCE and the relative rule says NOT_ELIGIBLE (p_min .91).
  - So the W-L CHANCE was a sample-size effect.
- C1 cells with census class ELSEWHERE and normal < .8. No cell in the census table has class CHANCE. Full numbers are in out/verdict_changes.csv.

| Cell | normal [lo99] | mid site_all | mid joint | Other arms | Census |
|---|---|---|---|---|---|
| 0187372b HOLD | .722 [.680] | FLIP_REL, .268 [.230, .308] | FLIP_REL | late site FLIP_REL | SITE |
| 11f3ac85 HOLD | .648 [.635] | FLIP_REL, .353 [.340, .364] | FLIP_REL | late site FLIP_REL | mid IDENTITY-BROKEN (identity .75), late SITE |
| 83d9d7b5 HOLD | .642 [.625] | FLIP_REL | FLIP_REL | late site FLIP_REL | SITE |
| 42716814 RELAY | .630 [.614] | CHANCE_REL, .452, z -.37 | FLIP_REL, z -1.0 | mid channel CHANCE_REL (z +.37); late site FLIP_REL | mid UNRESOLVED (fS .69, fN .22) |
| d3c0d182 RELAY | .615 [.610] | INDETERMINATE, z -.47 | FLIP_REL | channel INDETERMINATE (z +.47) | UNDEFINED (0 eligible) |

  - Channel arms on the three HOLD cells are NO_EFFECT_REL.
  - EVERY gives the same relative verdicts as SINGLE on all 5 cells.
  - For every FLIP_REL here the absolute rule at M=512 also says FLIP.
- Which verdicts change against the recorded ones:
  - CHANCE → FLIP on all S and site_all arms of the 5 W-L champions.
  - On the C1 cells, 11 recorded CHANCE verdicts become FLIP_REL:
    - site_all mid on the 3 HOLD cells.
    - joint mid on all 5 cells.
    - site_all late on 42716814 and 83d9d7b5.
  - Recorded CHANCE is sharpened to CHANCE_REL on 42716814 site and channel (mid), and to INDETERMINATE on d3c0d182 site and channel (mid and late).
  - All the FLIP changes also appear with the absolute rule at M=512. The relative rule itself only adds the CHANCE_REL/INDETERMINATE split and certified NO_EFFECT.

KNOWN-ANSWER TESTS
- Engine plants: n-back n=1, W-L m2 physics with prog_len 28, M=512. Normal accuracy is set by the engine's own RAND op flipping the stored cue with probability q (so normal = 1 - q) for q in {0, .1, .2, .3, .35, .4, .45}. Truth is known by construction.
  - P1S (bit held in register S1 only): 35/35 PASS. S1 and S swaps → FLIP_REL; the S0-only swap (non-identical, unused) → NO_EFFECT_REL; S1 swapped in half the pairs → CHANCE_REL; S1 swapped in "75%" of pairs → INDETERMINATE. At q .40 and .45 (lo99 .573 and .525) all arms → NOT_ELIGIBLE, as expected.
  - P1SK (bit held redundantly in S1 and Kp[3]; readout is the sign of their sum, so a single swap gives a tie): 21/21 PASS. S and Kp swaps → CHANCE_REL (tie); site_all → FLIP_REL. q .40 (lo99 .580) and .45 → NOT_ELIGIBLE.
  - Absolute rule on the same plants: FLIP truth reads CHANCE at q .40 and .45. CHANCE truth reads NO-EFFECT at q .45. The partial-transfer arm reads FLIP at q=0.
- Post-hoc readout noise on the noiseless P1S readouts, 100 redraws per cell: D2 flip noise shared across arms, D3 flip noise independent per arm, D4 abstain noise. A between-tick hook check showed the post-hoc noise is equivalent to in-engine noise (True/True).
  - 85/90 PASS.
  - The 5 FAILS are all the INDETERMINATE-truth arm (S1_3q) returning CHANCE_REL in 6-7% of redraws at q .30 and .35 (D2, D3, D4), above the frozen 5% limit.
  - Cause, found afterwards: the fixed "75%" pair mask actually covered 69.1% of pairs in this seed set (noiseless swap .309, so true z = -.38, which is inside the CHANCE band). My truth label was wrong, not the rule. It still counts as FAIL under the frozen criterion; no threshold was changed.
- Input that makes each check fail (out/negative_controls.json; all shown to fail):
  - FLIP_REL check fed the S0 arm → NO_EFFECT_REL.
  - NO_EFFECT_REL check fed the S1 arm → FLIP_REL.
  - CHANCE_REL check fed the S1 arm → FLIP_REL.
  - P1SK tie-CHANCE check fed site_all → FLIP_REL.
  - P1SK FLIP check fed the S swap → CHANCE_REL.
  - The gate fails as a check at normal .75 (eligible).
  - The INDETERMINATE check fails on a full-transfer input.
  - The absolute rule fails the FLIP truth at normal .60 (gives CHANCE).
  - pytest asserts each of these.

DISAGREEMENTS
1. The premise that the W-L champions are unresolvable by lens.swap_verdict is wrong at an adequate sample size. At P=256, K=11 the absolute rule gives FLIP for complete transfer whenever normal is above about .62. Its gap is wide only at small designs (P=32, K=3, roughly normal < .75).
2. My own gate, worst-case as the brief asked, is stricter than the absolute rule's reach for FLIP (P=64, K=11: absolute FLIP from about .65, relative eligible from about .72). The rule's certificates keep about 0.5% error at any normal above .5, so the gate mainly turns INDETERMINATE into NOT_ELIGIBLE and suppresses some valid certificates. Gated and ungated verdicts are both reported.
3. CHANCE_REL does not mean "the bit is gone". On 42716814 mid site, CHANCE_REL (z -.37) sits next to census fS .69: a partial site transfer. The SINGLE census should always accompany the verdict.
4. The flip rate f (my proposed accuracy-free companion) is not accuracy-free when mirror outcomes are asymmetric. On real specimens f was .5-.7 while z was about -1, and 0 on d3c0d182. Do not use it as a verdict.
5. d3c0d182 breaks the three-hypothesis model: its readout answers on only one sign, so the two partners are never both correct. INDETERMINATE is the honest output there.

PYTEST
- Command: `python -m pytest -q test_swap_rel.py -p no:cacheprovider` (from W-N/)
- Result: 23 passed in 3.10 s, RC=0.
- First run had 2 failures, both wrong expectations in my tests; logged as A5.
- Caveat: test_p_min_table checks the table lookup, not a fresh recomputation.

LEASES
- Fabric skullport:cpu8, lease_id lse-4124e1f2992d. Acquired 01:55 EDT, renewed once (5400 s), released 02:44 EDT. The first release call was refused for a missing `--as`; the rerun printed RELEASED and `lease status` showed [].
- No GPU used. The post-hoc and design-control runs used 2 threads or fewer after release.

FILES (all in F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-N/)
- PLAN.md, LOG.md
- swap_rel.py, test_swap_rel.py, plants_rel.py
- attain_table.py, attain_table2.py, smoke_plants.py, selfcheck_fork.py, run_plants.py, run_posthoc.py, run_specimens.py, wl_design.py, summarize.py
- out/: attain_table.json, selfcheck_fork.json, plants_engine_r0_P1S.json, plants_engine_r0_P1SK.json, plants_posthoc.json, p1s_noiseless_r0.npz, specimens_wl.json, specimens_c1.json, wl_design.json, verdict_changes.csv, negative_controls.json, pytest.txt, and the run logs.

PROPOSED FOLLOW-UPS
- Give each verdict its own attainability check instead of one worst-case gate for all three.
- Always pair CHANCE_REL with the SINGLE census.
- Re-audit other recorded CHANCE verdicts from 64-world designs at 512 worlds before reading any of them as mechanism.
