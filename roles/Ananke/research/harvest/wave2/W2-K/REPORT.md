<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-K; sha256(report)=bd89f23aa6fa4e81; delimited; see REPORT.provenance.json -->
W2-K REPORT: how statistically fragile are the C1b verdicts and the C1 high-accuracy labels? (Wave 2, Opus worker W2-K, Ananke seat)

Directory: roles/Ananke/research/harvest/wave2/W2-K/
- Scripts: reeval_c1b.py, c1_integration.py, elig_sham.py, c1b_fragility.py, label_boot.py, census_keep.py
- Pair arrays: out/pairs_*.npz, each with a .json sidecar recording the reproduction check
- Tables: out/c1b_fragility.json, out/label_boot.json, out/census_keep.json
- Fix: patches/inference_reading3_w2k.diff, tests/test_reading3_w2k.py, scratch/

0. SUMMARY (verdict first)

Interval method is not the problem; margin is.
- I recomputed 22 C1b readings from exact pair arrays. Every array reproduced the recorded pct triple to 4 dp on CPU in eager mode.
- Under t and BOOTT, 0 of the 22 flip. The largest bound shift is .022 (BOOTT, on a skewed difference array). Every shift goes in the conservative direction.
- 7 of the 22 sit within 2.33 SE of their cut (keep below .95). The expected number of reading flips on a fresh-world re-run is 1.6.

Specimen labels at risk:
- M2 (4ab2ba01) IN_FLIGHT_PLUS_JOINT_UNRESOLVED:
  - It rests on B = false at 0.89 SE (keep .73) and on K_w = false at 1.68 SE (keep .88).
  - Label bootstrap (plug-in): kept 62.5%. IN_FLIGHT_UNDECODED_UNRESOLVED 32.5%. MIXED:in_flight,w 5%.
- M3 (0a23398f and f6b623cd) TRANSPORT+RULE_SWITCH_UNRESOLVED:
  - It rests on T's absolute "C1 window lo99 >= .62" clause: 1.95 SE (keep .92) and 1.40 SE (keep .84).
  - Label bootstrap: kept 99% and 89.5%. The alternative label is RULE_SWITCH_ONLY.
  - Prediction C1b-P1 ("HELD, T true in both") has a joint predictive keep of about .77.
- Z NOT_ELIGIBLE: the F_sham_positive "fired" reading is 1.14 SE from firing (keep .79). If it fired, the _UNRESOLVED suffix would drop from the M2 label and from fresh k1.

Fresh-seed (S2) gates:
- 0a23 k2 is 0.03 SE below SIGNAL and 0a23 k0 is 0.73 SE below. Expected SIGNAL count for 0a23 on a replicate is about 0.8, not 0. 0/4 has a Clopper-Pearson 95% interval of [0, .60].
- f6b6 k0 passed SIGNAL by 0.37 SE.
- f6b6 k1 is 1.54 SE from T = true. That would give it the specimen's own label, which means M3_REPRODUCED. These rows are APPROX (see F3).

One label is an artefact, not a fragile reading:
- f6b6 k0 is C1_CONTROL_NOT_REPRODUCED although the C1 window changed accuracy by only +.007.
- The cause: the champion's battery normal already sits below the kill line (hi99 .578 <= .60). An absolute "kills" test then fires on any arm that does not improve the cell.

C1 high-accuracy labels:
- INTEGRATION (MAJ lo99 > .70) has exactly one call in C1: 4781b0a1, at 2.36 SE.
  - lo99 under pct / t / BOOTT: .7422 / .7401 / .7395. No flip.
  - An independent-world replicate exists in C1b S3 (lo99 .720 / .711 / .7125, 1.14 SE).
  - Pooled over 64 pairs: BOOTT lo99 .7425, 3.4 SE.
  - Verdict: replicated, not fragile.
- TRANSFER_SUPPORT: all 23 calls are at least 10.7 SE above the cut (6 of them have zero variance). The best cross-family row is 2.8 SE below. Nothing to recompute.
- The W2-H "pct misses 3-9% at high p" defect touches these labels only through 4781b0a1, and only by .0027.

W2-H F10 is resolved by existing data:
- C1b S3 already re-ran 613162a3's C1-window packet ablation on disjoint worlds: drop .1615, 2.63 SE.
- Pooled with C1's own control pairs (64 pairs): drop .152, 2.96 SE (keep .98), BOOTT hi99 of the difference -.1048.
- The packet-ablation clause of that CAUSAL_SUPPORT is no longer fragile.

Census classes (lens_swap.classify, point thresholds):
- 930 unique CI-bearing census records (W-M, W-N, W-O, W-R). The recomputed class matches the recorded class in all of them.
- Of 284 SITE/CHANNEL/NEITHER records:
  - 14 lie within 1 SE of a class boundary and 31 within 2.33 SE;
  - expected class changes on a re-run: 8.1;
  - NEITHER is the most fragile class: 7 of 36 within 1 SE.
- Of the 132 S/C/N records that are not phase strata or follow-census rows, 9 lie within 1 SE.

1. FINDINGS

Commands (all from W2-K/, CPU only, CUDA_VISIBLE_DEVICES=-1, OMP_NUM_THREADS=2, torch 2 threads; torch.cuda.is_available() asserted False):
- python reeval_c1b.py {m2spec,m3_0a23,m3_f6b6,m2fresh,m2fresh_b,s3_6131}
- python c1_integration.py
- python elig_sham.py
- python c1b_fragility.py
- python label_boot.py
- python census_keep.py
- Definitions used throughout:
  - SE = sd(pairs, ddof 1)/sqrt(32);
  - d = SE distance of the deciding statistic beyond its cut, measured toward the RECORDED truth value (negative would mean the other side);
  - keep = Phi(d/sqrt 2) (inference.keep_prob, predictive). It is the chance that a re-run on FRESH worlds gives the same reading; re-running the same seeds is deterministic.

F1 [V] The C1b rows store no pair arrays. Confidence high.
- c1b_run.summarise keeps only (m, lo99, hi99) per arm, and the S2 rows do not store the fresh champions.
- Consequence: every paired-difference reading (B, Z, I, K_x, R, A3 "fired") cannot be checked from the rows.
- Fresh M2 champions exist in research/spikes/out/champions_m2.json (regenerated bit-identically, 09-27). Fresh M3 champions exist nowhere. Regenerating one is a full 96 x 36 search, about 20 min on CPU, so I did not do it.
- Re-evaluation coverage: specimens, M2 fresh champions, the S3 cell 613162a3, the eligibility plants and C1 4781b0a1. In total 9 battery calls / 34 evaluate calls, about 4 min wall.
- Every arm matched the recorded (m, lo, hi) exactly to 4 dp (the "match" fields in out/pairs_*.json). The C1 4781 held CI matched to 1e-12.

F2 [V] C1b flip table, exact rows. Confidence high on the numbers; medium on keep (see objection).

Columns: cell | reading | cut | rec | pct | t | BOOTT | d(SE) | keep

| cell | reading | cut | rec | pct | t | BOOTT | d(SE) | keep |
|---|---|---|---|---|---|---|---|---|
| M2 4ab2ba01 | A flush kills (hi) | <=.60 | T | .5052 | .5062 | .5051 | 29.6 | 1.00 |
| M2 4ab2ba01 | Z ITI-flush intact (lo diff) | >=-.10 | T | .0000 | .0000 | .0000 | inf | 1.00 |
| M2 4ab2ba01 | B nonpacket intact (lo diff) | >=-.10 | F | -.1185 | -.1189 | -.1372 | 0.89 | .735 |
| M2 4ab2ba01 | K_w drops, point clause | m<=-.10 | F | m -.0658 | (same) | (same) | 1.68 | .883 |
| M2 4ab2ba01 | K_w drops, lo clause | <-.05 | T | -.1191 | -.1216 | -.1415 | 3.4 | .99 |
| M2 4ab2ba01 | I inbox drops | m<=-.10 | F | 0 | 0 | 0 | inf | 1.00 |
| M2 4ab2ba01 | C census, comp 0 (lo) | >.60 | F | .3789 | .3761 | .3756 | 10.1 | 1.00 |
| M2 elig | F_sham_positive fired (hi diff) | <-.10 | F | -.0682 | -.0624 | -.0634 | 1.14 | .789 |
| M2 elig | F_sham_positive competent | >.55 | T | .7784 | .7737 | .7740 | 11.8 | 1.00 |
| M2 elig | F_echo fired (gates nothing) | <-.10 | F | -.0951 | -.0917 | -.0869 | 0.21 | .558 |
| M3 0a23398f | T: C1 window intact (lo) | >=.62 | T | .6549 | .6480 | .6505 | 1.95 | .916 |
| M3 0a23398f | X: C1 window kills (hi) | <=.60 | F | .7448 | .7465 | .7511 | 8.1 | 1.00 |
| M3 0a23398f | R freeze_rule drops | m<=-.10 | T | m -.1732 | (same) | (same) | 3.69 | .995 |
| M3 f6b623cd | T: C1 window intact (lo) | >=.62 | T | .6432 | .6406 | .6370 | 1.40 | .838 |
| M3 f6b623cd | X | <=.60 | F | .7292 | .7318 | .7307 | 7.8 | 1.00 |
| M3 f6b623cd | R freeze_rule drops | m<=-.10 | T | m -.1641 | (same) | (same) | 3.61 | .995 |
| fresh 4ab2 k1-k3 | Z, B, K_w, C (12 readings) | -- | as recorded | -- | -- | -- | >=3.18 (Z on k2 3.18; rest >=3.69 or inf) | >=.988 |
| D 613162a3, S3 recheck | C1-window drop (C1 CAUSAL point rule) | m<=-.10 | T | m -.1615 | (same) | (same) | 2.63 | .968 |
| D 613162a3, S3 recheck | corrected-window drop | m<=-.10 | T | m -.1992 | (same) | (same) | 4.21 | .999 |
| C1 4781b0a1 | INTEGRATION held lo99 | >.70 | T | .7422 | .7401 | .7395 | 2.36 | .953 |
| 4781b0a1 on C1b worlds | same statistic, replicate | >.70 | T | .7200 | .7108 | .7125 | 1.14 | .789 |

- The readout-tick and corrected-window kills in both M3 cells are 13 SE or more from the cut, or have zero variance (approximated from the recorded CI).
- Flips under t: 0. Flips under BOOTT: 0.
- Strongest objection: keep assumes the SE is correct and the same across runs. W2-H F6 found excess disagreement in the 1-3 SE band on AUDIT3, so keep may be OPTIMISTIC there. The readings also share one normal arm, so they are correlated. The label bootstrap (F4) keeps that correlation.

F3 [V by recorded CI; I on SE] Fresh-search (S2) rows, APPROX. Confidence medium.
- No arrays exist for these rows. SE = recorded CI width / 5.15. The SE of a difference is r x sqrt(se_a^2 + se_b^2), with r = .955 measured on the specimens. BOOTT cannot be computed.

| cell | reading | rec | pct | t~ | d | keep |
|---|---|---|---|---|---|---|
| 0a23 k0 | SIGNAL (lo99 > .55) | F | .5449 | .5428 | 0.73 | .70 |
| 0a23 k2 | SIGNAL | F | .5495 | .5473 | 0.03 | .51 |
| f6b6 k0 | SIGNAL | T | .5534 | .5519 | 0.37 | .60 |
| f6b6 k2 | SIGNAL | F | .5443 | -- | 0.96 | .75 |
| f6b6 k3 | SIGNAL | T | .5625 | .5594 | 1.00 | .76 |
| f6b6 k1 | SIGNAL | T | .5807 | -- | 1.91 | .91 |
| f6b6 k0 | X: C1 window kills | T | hi .5866 | -- | 1.47 | .85 (an artefact, see F5) |
| f6b6 k1 | T: C1 window intact | F | lo .5977 | -- | 1.54 | .86 |
| f6b6 k1 | R | T | m -.127 | -- | 2.09 | .93 |
| f6b6 k3 | R | F | m -.081 | -- | 1.16 | .79 |

- Consequences:
  - If f6b6 k1's T flips to true, k1 gets TRANSPORT+RULE_SWITCH(_UNRESOLVED), which is the specimen's label, so M3_REPRODUCED becomes true for f6b6.
  - If f6b6 k3's R flips, k3 becomes RULE_SWITCH_ONLY.
  - If 0a23 k2 crosses the gate, a battery is run whose label is unknown. So "0a23 not reproduced" is a statement at the gate margin. With 0/4, the Clopper-Pearson 95% bound on the search-level reproduction rate is .60.
- No S2 SIGNAL gate flips under the t approximation (f6b6 k0 t lo99 ~.5519).
- Fresh M2 rows: the four SIGNAL gates are 6.3 SE or more from the cut. All 12 exact battery readings on k1-k3 are 3.18 SE or more from their cuts (C1b-P5 "exactly 1: k1" is robust).
- Unresolved: exact arrays for the M3 fresh rows. This needs regenerating the champions.

F4 [V] Specimen-label stability (label_boot.py). Confidence medium-high.
- Method: 400 pair resamples, with the same indices in every arm; the frozen pct rule and the frozen decision lists; the recorded NOT_ELIGIBLE lists.
- M2: IN_FLIGHT_PLUS_JOINT_UNRESOLVED 62.5%, IN_FLIGHT_UNDECODED_UNRESOLVED 32.5%, MIXED:in_flight,w_UNRESOLVED 5%.
- 0a23: 99% kept, 1% RULE_SWITCH_ONLY. f6b6: 89.5% kept, 10.5% RULE_SWITCH_ONLY.
- Plug-in resampling is more optimistic than predictive keep (M2 about .65, 0a23 .91, f6b6 .83).
- The verdict-level claims that do NOT depend on the fragile readings, because they rest on readings 8 SE or more from their cuts:
  - "M3 = transport landing on the readout tick" (readout-tick and corrected-window kills);
  - "M3 needs SETRULE" (R at about 3.6 SE);
  - "M2 bit in flight mid-gap" (A at 29.6 SE);
  - "M2 in-flight memory reproduced 3/3".

F5 [V] Two threshold-semantics defects in C1b (they act like a broken absence/presence symmetry, not like noise). Confidence high.
(a) Absolute kill line with no competence gate.
- "kills" = arm hi99 <= .60, applied without checking normal.
- On f6b6 fresh k0 the battery normal is .5566 [.5319, .5781], already below the line. The C1 window (.5632, effect +.0066) therefore "kills": X = true, label C1_CONTROL_NOT_REPRODUCED.
- On the C1b worlds this champion is not even SIGNAL (normal lo99 .5319).
(b) Absolute "intact" bar in T (C1_INTACT_LO .62).
- On the specimens, the C1 window's effect is +.0046 (diff lo99 -.005, 24 SE inside s3's relative intact band) and exactly 0 in f6b6.
- T's fragility (1.4-1.95 SE) therefore comes entirely from comparing an absolute .62 bar with a normal of about .69, not from any window effect.
- On the fresh champions (normal .59-.63) the bar is close to impossible: the eligibility-count problem.
(c) Burden asymmetry in the M2 list.
- Rule 8 IN_FLIGHT_PLUS_JOINT fires on "not B", that is, when the absence test fails (lo99 -.1185).
- "Drops" (point -.062, which is not <= -.10) is not met, and neither is A3's "decisively not-intact" (hi99 of the difference below -.10).
- So the label asserts a non-packet contribution on a reading that is INDETERMINATE under any symmetric rule.
- Objection: the labels are what the frozen prereg computes, and the C1b packet discloses (a) and (b) descriptively. I do not ask for relabelling; this concerns how much evidential weight the labels carry.

F6 [V] C1 INTEGRATION and TRANSFER_SUPPORT in the high-accuracy regime. Confidence high.
- 174 MAJ evolve/transfer rows; INTEGRATION is true only for 4781b0a1 (wave C). The next-best MAJ lo99 is .650, about 3 SE or more below the .70 cut.
- The C1 rows store no held pair arrays. I used W2-H's method: the recorded champion on world_seeds(H(search_seed, HELD_NS), 64), reproduced to 1e-12. Numbers are in F2.
- TRANSFER_SUPPORT: 23 calls, all HOLD->HOLD variants or identity, minimum 10.7 SE, 6 with zero variance (pct = t = BOOTT = point). The best cross-family row (RELAY->MAJ) has lo99 .512, 2.8 SE below the cut. P5 is unaffected.
- Objection: zero-variance rows have SE 0 by construction at P = 32. A near-deterministic HOLD latch makes this plausible, but no interval method can certify it; only more worlds can.

F7 [V] Census class fragility (census_keep.py). Confidence medium.
- Data: 2,152 census dicts crawled in W-M..W-Z; 1,510 carry ci99; 930 unique.
- Classes among the 930: IDENTITY-BROKEN 202, SITE 134, CHANNEL 114, MIXTURE 92, UNRESOLVED 352, NEITHER 36.
- SE is taken from the pair-bootstrap CI width. For each condition whose flip alone changes the class, I compute its distance.

| class | n | within 1 SE | within 2.33 SE | expected flips on re-run |
|---|---|---|---|---|
| SITE | 134 | 5 | 9 | 2.5 |
| CHANNEL | 114 | 2 | 10 | 2.3 |
| NEITHER | 36 | 7 | 12 | 3.3 |
| MIXTURE | 92 | 10 | 16 | 4.5 |
| UNRESOLVED | 352 | 28 | 57 | 14.9 |

- S/C/N within 1 SE (14), by source: W-R 6, W-M 4, W-O 4.
- Objections:
  - The SE comes from a percentile-bootstrap width.
  - fS+fC uses se(fN), which is exact only when fX = ftie = 0.
  - Independence across conditions is assumed.
  - The 642 records without CIs (census_follow, W-M summary copies) are not scored.

2. PROPOSED FIXES

P1 NEUTRAL (new functions in inference.py, which nothing frozen imports): reading3() and kill_eligible().
- reading3(pairs, cut, op, bound, method='BOOTT', margin_se=2.33) returns TRUE / FALSE / INDETERMINATE plus d_se and keep.
- kill_eligible(normal) is TRUE only if normal lo99 > KILL_HI by the margin.
- Diff: patches/inference_reading3_w2k.diff (git apply --check OK).
- Test: tests/test_reading3_w2k.py. Current code: 5 failed. Patched scratch: 5 passed.
- Command (from W2-K/):
  PYTHONPATH=../../../../../.. python -m pytest -q -p no:cacheprovider tests/      (current: 5 failed)
  PYTHONPATH=scratch python -m pytest -q -p no:cacheprovider tests/                (patched: 5 passed)
- The test pins C1b M2 B as INDETERMINATE (not FALSE), uses f6b6-k0-like normals for kill ineligibility, and covers the zero-variance and strict-operator cases.

P2 SEMANTIC, future preregs only. Reporting rule R-W2K, checked against W2-H:
(1) Interval: BOOTT 99% over mirror pairs for every bound-type reading, with pct reported beside it for continuity. AGREES with W2-H. In C1b this is second-order: maximum shift .022 and 0 of 22 flips.
(2) Margin gate on EVERY component reading, not only on SIGNAL and certificates.
  - This includes absence readings ("intact"), point-threshold readings (DROP_PT, the C1 CAUSAL drop >= .10, census fS >= .80 etc.; give them SEs) and A3 "fired" eligibility readings.
  - A reading is TRUE or FALSE only at |d| >= 2.33 (keep >= .95); otherwise it is INDETERMINATE. A label whose decision path touches an INDETERMINATE component is issued as <label>_FRAGILE, naming the alternative branch.
  - W2-H's 3-SE level for certificates stays. This EXTENDS W2-H, which gated only SIGNAL and certificates; 7 of the 22 C1b readings would be FRAGILE.
(3) Relative, competence-gated cuts.
  - A kill reading is eligible only if kill_eligible(normal).
  - "Intact" bars are relative to normal (s3's lo99(diff) >= -.10), never absolute (no .62-style bars).
  - Before freezing, compute the eligible count at the expected competence (cf. feedback_preregistered_rules_need_an_eligibility_count).
(4) Search seed as the unit for physics-level claims. AGREES with W2-H F9.
  - "Reproduced" becomes k of n searches with an exact binomial CI, reported together with the gate fragility of the non-SIGNAL searches (expected SIGNAL count = sum of their 1-keep values).
  - n = 4 cannot exclude a 60% reproduction rate. Use n >= 8 (0/8 gives CP95 <= .37).
(5) Independent-world replicate for single-draw labels below 3 SE, pooled by pairs: INTEGRATION and 613162a3 both pass when pooled (3.4 and 2.96 SE).
(6) Save pair arrays in every row. c1b_run.summarise stores triples only; this is a driver change for the next prereg. No diff is written, because c1b_run is frozen code under the SHA guard.

3. DISAGREEMENTS
- W2-H F10 ("613162a3 fragile, keep .88"): superseded by data W2-H did not use. The C1b S3 recheck is a disjoint-world replicate (2.63 SE); pooled, it is 2.96 SE with BOOTT hi99 below -.10. Only the packet clause is covered: zero_comm and env_permutation were not rechecked.
- W2-H Q1 ("re-score all 777 rows, ~50k evaluations, especially INTEGRATION/TRANSFER"): not needed for those labels. There is 1 INTEGRATION call (replicated) and no TRANSFER_SUPPORT within 10 SE.
- C1b packet s7, P1 "HELD (T true, both)": fragile (joint keep about .77). The fragility comes from the absolute .62 bar, while the window's measured effect is about 0. P1's substance (transport lands on the readout tick) is robust, from the kills.
- C1b packet P3 "LOST (C and B false)" and s12 "M2 pure delay line: no": C false is the component-0 artefact (CORRECTIONS K1), and B false is INDETERMINATE (0.89 SE). LOST stands mechanically, but carries almost no evidence.
- C1b packet "0a23398f does NOT reproduce at this budget": that is a statement at the margin of a coin-flip gate (k2 at 0.03 SE).
- C1b packet f6b6 k0 C1_CONTROL_NOT_REPRODUCED: a kill-line aliasing artefact (F5a). It is not evidence against the C1 control.
- Narrative claims that rest on census readings within 1 SE of a class boundary:
  - W-M "NEITHER appears only at 4781b0a1 o6 and o8": o8 SINGLE fN .504 (0.14 SE, keep .54); o6 EVERY .526 (0.79 SE, keep .71). The W-O 512-world rerun is also .508 (0.72 SE). Stable finding: fN is about .50-.53. The class is a coin flip.
  - W-R "4781b0a1 o1-4 PARTLY resolve": o2 rests on q1 SITE fS .803 (0.16 SE, keep .54).
  - W-R P4b "failed for 4781b0a1 o12/o13": o12 pooled CHANNEL fC .809 (0.70 SE, keep .69); o13 (.87) is robust.
  - W-R 8c37f32e o5 pooled UNRESOLVED is 1.16 SE from MIXTURE via phi_hi.
  - W-O rerun 4ab2ba01 o5 CHANNEL fC .8009 (0.14 SE).
  - W-O rerun c868a87b o10 SITE: identity .9044 vs .90 (0.56 SE).

4. NEXT QUESTIONS (ranked)
1. Re-run M2 4ab2ba01's reset_all_nonpacket and reset_w, and F_sham_positive at M2 physics, on 2 more world namespaces. Cost: about 1.5 min CPU each. This settles the M2 label (B, K_w) and Z eligibility.
2. Regenerate the f6b6 k1 and k3 and 0a23 k0 and k2 champions (1 GPU min each, or about 20 CPU min each) and save them. Then run the M3 battery on 2 namespaces. This tests whether M3_REPRODUCED becomes true (k1 T at 1.54 SE).
3. Calibrate keep_prob on the existing C1-to-C1b replicate pairs. 12 D cells x (normal, C1 window) were measured in both C1 and C1b S3 on disjoint worlds. Is Phi(d/sqrt 2) right in the 1-3 SE band?
4. Recompute W-R's phase letters and W-M's classes with three-valued margin classes. How many letters in the T-INS-8/9 corrections register survive as definite?
5. Replace the census point thresholds with interval-and-margin rules, and measure how many of the 284 S/C/N records become FRAGILE at 2.33 SE (31 by my estimate).
6. Save pair arrays (and fresh champions) in c1b_run-style drivers. Specify this for C2 and later preregs.
7. For a planned M3 replication: choose the number of searches n for a target CI on the search-level reproduction rate.

5. INFERENCE LEDGER
question | evidence | result | confidence | strongest objection | unresolved | next
C1b arrays saved? | c1b_run.summarise; rows.jsonl.gz 6 KB | triples only; M3 fresh champions absent | high | -- | M3 fresh exact SE | Q6
C1b re-eval reproduces | reeval_c1b.py, 34 evals, 4-dp match | exact on CPU eager | high | -- | -- | --
C1b flips pct->t/BOOTT | c1b_fragility.py, 22 exact readings | 0 flips; max shift .022 | high | -- | APPROX rows have no BOOTT | Q2
C1b margin fragility | d and keep per reading | 7/22 below 2.33 SE; expected flips 1.6 | med-high | keep optimistic in 1-3 SE (AUDIT3) | calibration | Q3
specimen labels | label_boot.py, 400 resamples | M2 62.5% kept; M3 99% / 89.5% | med | plug-in optimistic | predictive joint | Q1
C1b-P1 | T at 1.95 / 1.40 SE | joint keep ~.77; window effect ~0 | high | T NOT_ELIGIBLE anyway | -- | Q1
M3_REPRODUCED | S2 gates + k1 T (APPROX) | 0a23 k2 at 0.03 SE; f6b6 k1 1.54 SE from reproducing | med | approx SE | champions | Q2
kill-line aliasing | recorded f6b6 k0 arms | C1_CONTROL_NOT_REPRODUCED with +.007 effect | high | -- | -- | P1 fix
Z eligibility | elig_sham.py exact | fired reading 1.14 SE from firing | high | -- | -- | Q1
INTEGRATION | c1_integration.py + C1b replicate | 2.36 SE; pooled 3.4 SE; replicated | high | -- | -- | --
TRANSFER_SUPPORT | 23 rows, CI widths | min 10.7 SE; 6 degenerate | high | SE 0 at P=32 | -- | --
613162a3 packet clause | C1 control pairs + S3 re-eval | pooled 2.96 SE; BOOTT hi < -.10 | high | other clauses unchecked | -- | Q3
census classes | census_keep.py, 930 records | S/C/N: 14 within 1 SE, expected flips 8.1 | med | SE from pct width; independence | W-F taxonomy not scored | Q4/Q5
reporting rule | all of the above vs W2-H | BOOTT + margin on ALL readings + relative cuts + seed unit (n >= 8) | med-high | one prereg's evidence | -- | P2

6. COMPUTE
- CPU only, at most 2 threads per process, every process under 2 min.
- About 6 min wall in total across all runs, including the pytest runs and the census crawl. That is about 0.2 core-hours or less, within the 0.5 cap.
- No search was run (the fresh M3 champions were deliberately not regenerated). No git writes, no lease actions.
- Every write is under W2-K/ (out/, patches/, tests/, scratch/ and the scripts).
