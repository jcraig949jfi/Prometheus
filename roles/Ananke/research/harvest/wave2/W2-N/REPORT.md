<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-N; sha256(report)=557cfbdf387b861d; delimited; see REPORT.provenance.json -->
W2-N REPORT: why the swap certificate flips between seed namespaces (Wave 2, Opus worker W2-N, Ananke seat)
Directory: roles/Ananke/research/harvest/wave2/W2-N/ (scripts n_*.py, batch.sh; outputs in out/)

0. VERDICT
- At group level there is no excess once the comparison is modelled correctly. Expected 9.8 flipped groups (SD 2.2) at f = 1; observed 10.
- The apparent excess has four sources:
  - row double-counting: 22 rows are 10 measurements in 10 groups and 8 specimens;
  - comparing a plug-in expectation with two noisy draws;
  - selection on the first draw: AUDIT3 kept only rows W-U called DETERMINED, which drops near-threshold first-draw certificates, and it chose 31 groups because their first draw sat near a threshold;
  - not the estimator: 0 of 22 rows are attributable to it.
- Direct estimate of f:
  - W-O (namespace 0x600) vs W-Z (0x680), 124 groups, M = 512: f = 1.00 [0.91, 1.11] on DF and 0.96 [0.88, 1.06] on DN.
  - Fresh replicates, 6 groups x 3 new namespaces: f(DF) = 1.00 [0.78, 1.39]; DF and DN pooled 1.11 [0.87, 1.55].
  - f = 2 is rejected by both.
- No physics, topology, graph or champion draw is keyed by the namespace. The namespace is just the set of world seeds. It does act as a small common random effect across specimens of one family, because they share the same seeds and therefore the same task geometry.
- Recommended gate: predictive keep probability Phi(d / (sqrt2 * f)) with f = 1. For robustness use f = 1.12, the upper end of the M = 512 CI.
  - 95% keep needs d >= 2.33 SE at f = 1, or 2.6 SE at f = 1.12.
  - W2-H's 3 SE for certificates is conservative (keep >= .98), not required by the data.
  - W2-F's f = 2 rule is not supported; it would flag about 52 of 256 stable rows for nothing.

1. FINDINGS

F1 [V] The two namespaces differ ONLY in world seeds. Confidence: high.
- W-O runner.py uses NS = 0x600 and W-Z zcommon uses NS = 0x680. Both run the same fork_single, M = 512, the same loader, the same sct_offset rule, the same trial set and the same arm map. W-Z imports W-O's code.
- Physics, genome and env come from the specimen row.
- envs.build draws source and readout site, cues and distractors from H_int(lead_seed, ENV, family, variant), per world.
- engine.py keys every stream (INIT, WAKE, RANDOP, MUT, ROUTE, LOSS, LAT, NOISE, CTRL, DUP) by (ws, stream, t, site).
- No engine, envs or lens file changed between the W-O run (09-29 ~07Z) and the W-Z run (09-30 ~12Z). Checked with git log on prometheus/ananke/*.
- Known-answer check: world_seeds(ns, M) is a prefix of world_seeds(ns, 512). Fresh M = 256 runs in 0x680 reproduced the first 128 recorded W-Z pairs bit-exactly:
  - 047aa8ed channel_all and 2a776b0a inbox, 0 differing cells (out/ka.jsonl);
  - this also shows the worlds in a batch are independent.
- Objection: KA used the M = 256 prefix, not all 512 pairs.

F2 [V] Deduplication: 22 rows are 10 measurements in 10 groups. Script: n_decomp.py, part D.
- Within a group, arms with identical or mirrored (s1 + s2 = 1) pair arrays are one measurement.
  - 301 DETERMINED rows -> 182 measurements, 110 groups; 117 arm instances are mirrors.
  - 22 disagreeing rows -> 10 measurements -> 10 groups (0 measurements with mixed row outcomes).
- Beyond site_all/channel_all (W2-F F4), duplicates include:
  - S = site_all;
  - channel_count, channel_content and pay0 = channel_all at some offsets;
  - 59b89e9d lists site_all and channel_all twice each in the inventory.
- New: the normal run is shared across ALL offset groups of one specimen. Cross-group correlation of pair-level normal accuracy for the same specimen is 0.993 (n_xcorr.py). So the cluster unit for normal-arm noise is the specimen: the 10 groups are 8 specimens. W2-H's group-level cluster bound under-clusters.

F3 [V] The estimator difference explains 0 of 22. Script: n_attrib.py.
- Same estimator on both draws: W-N's PCT REL2 rule on W-Z pairs vs W-O's recorded REL2 ('rel'). It changes label in exactly the 22 rows (plus 1 row where W-Z and W-U agree anyway).
- Every disagreement is a seed flip under an unchanged rule.
- Same data, different estimator (E0: W-U's marginal-bounding pipeline run on W-Z's own data vs exact H2): 8 of 316 determined rows differ (2 groups, INDETERMINATE vs CHANCE). None of the 8 is among the 22.
- Structural point: W-U's pipeline can never certify a row that REL2 left INDETERMINATE (kept combos force INDETERMINATE at Z99 and TQ > Z99). Its labels can only lose certificates relative to REL2.
- This refutes W2-H's attribution of the excess to "W-U's first-draw estimator".

F4 [V] Selection explains the direction and the remaining excess. Scripts: n_attrib.py inline count, n_sim.py.
- Over all 365 covered rows, same-estimator REL2 flips are balanced: 21 INDETERMINATE -> certificate and 20 certificate -> INDETERMINATE.
- 18 of the 20 certificate -> INDETERMINATE flips are in W-U AMBIGUOUS rows, which the consistency check excluded. That produces the 20:2 asymmetry in the 22.
- Group selection: 5 of 17 AMBIG-priority groups flipped, against 5 of 93 REST groups.
- Decomposition table, expected flips among the 110 DETERMINED groups (observed 10). A = noise only, labelled with BOOTT multipliers.

| model step | f = 0.71 (plug-in) | f = 1 (predictive) | f = 1.25 | f = 1.5 | f = 2 |
|---|---|---|---|---|---|
| A noise only (BOOTT labels) | 5.38 | 7.83 | 9.88 | 11.84 | 15.35 |
| B + estimator (W-U normal/TQ) | 5.54 | 7.94 | 9.98 | 11.93 | 15.41 |
| C + row selection (row DETERMINED) | 7.41 | 9.11 | 10.54 | 11.99 | 14.99 |
| D + group selection (full status pattern) | 8.21 | 9.78 | 11.02 | 12.34 | 14.96 |
| SD of D (independent groups) | 2.0 | 2.2 | 2.4 | 2.5 | 2.8 |

- Rows (observed 22): D = 13.5 / 16.9 / 19.7 / 22.5 / 28.3 across the same f columns. Row counts carry duplicate measurements, so they are not a valid statistic.
- At f = 1 the decomposition of the 10 observed groups is:
  - W2-F's plug-in baseline: about 4.6-5.4;
  - two noisy draws (predictive): +2.5;
  - estimator: +0.1;
  - row selection: +1.2;
  - group selection: +0.7;
  - residual: +0.2.
- W2-F's "f ~ 2" is a plug-in-convention number. sqrt2 of it is the second draw's own noise, and the rest is selection plus duplicates.
- Objections:
  - normal approximation with a flat prior centred on W-Z;
  - the simulated SD treats groups as independent, while F2 says specimens are the unit, which makes the SD larger.

F5 [V] Direct f with no new compute: W-O vs W-Z on every covered unit. Script: n_fdirect.py.
- z = (m_WZ - m_WO) / sqrt(se_WZ^2 + se_WO^2). se_WO comes from the recorded pair_ci width; the median SE ratio W-O/W-Z is 1.01.

| statistic | f (RMS z) | 95% CI | cluster-bootstrap CI | REST only (unselected) |
|---|---|---|---|---|
| a (normal arm) | 0.94 | [0.83, 1.07] | -- | 0.95 |
| s (swap arm) | 1.00 | [0.91, 1.10] | -- | 1.01 |
| DF | 1.01 | [0.92, 1.12] | [0.91, 1.11] | 0.98 [0.87, 1.09] |
| DN | 0.96 | [0.88, 1.06] | -- | 1.00 |

- Share of |z| > 2.576: 0.5-1.6%, against a nominal 1%.
- Mean z is -0.18 ± 0.12 at specimen level (59 specimens); RELAY alone -0.46. See F7.

F6 [V] Direct f from fresh namespaces. Scripts: n_runs.py, batch.sh, n_repl.py.
- Groups at intermediate z:
  - flipped: 2a776b0a inbox, 6edf00dc inbox, 48c5f7d4 site_all;
  - stable: 047aa8ed channel_all, b7e29626 inbox, 561ed71c site_all.
- Each was run in namespaces 0x4e01, 0x4e02 and 0x4e03 at M = 256, one arm plus the normal run. M = 256 instead of 512 was a budget choice; f is a ratio of SDs, and F1 shows worlds are iid.
- Q = sum of w_j (m_j - m_w)^2, which is ~ f^2 chi2.

| draw set | f(a) | f(s) | f(DF) | f(DN) | DF+DN pooled |
|---|---|---|---|---|---|
| 5 draws incl. W-Z prefix and W-O (24 df) | 0.95 | 1.10 | 1.00 [0.78, 1.39] | 1.22 [0.95, 1.69] | 1.11 [0.87, 1.55] |
| fresh only, unselected (12 df) | 0.62 | 1.11 | 0.99 [0.71, 1.64] | 1.24 [0.89, 2.04] | -- |
| within-namespace halves (6 df) | -- | -- | 0.67 | 1.20 | 0.97 [0.63, 2.15] |

- Objections:
  - the DN point estimate is 1.2-1.3 at M = 256 (p = .06 with W-O, .02 without), while the far tighter M = 512 data give 0.96;
  - 6 groups is a small panel, and 3 of them were chosen because they flipped, which biases f upward if anything.

F7 [V] Is there a genuine between-namespace component? None per row. There is a small common effect across groups. Script: n_xcorr.py.
- Cross-group correlation of pair-level normal accuracy within one namespace:
  - different family: -0.004;
  - same family, different specimen: mean +0.037 (6.6% of pairs above 0.2);
  - same specimen: 0.993.
- Mechanism: every group uses the same 512 seeds, and the task geometry H_int(lead, ENV, family, variant) is shared across specimens of a family and variant.
- Effects:
  - flips across a family's specimens are slightly positively correlated, so count variances are larger than an independent model gives (design effect about 1 + (G - 1) x 0.037);
  - per-row SEs are unaffected (f ≈ 1).
- This is the namespace-keyed effect the brief asked about. It is common random numbers, not a draw that within-run CIs miss.

2. PROPOSED FIXES
- No code fix. NEUTRAL analysis rules for any future replication or consistency check:
  - (i) compare same-estimator labels;
  - (ii) count deduplicated measurements, clustered by specimen;
  - (iii) never filter or choose units on the first draw's status, or else condition on that selection as n_sim.py does;
  - (iv) replication gate keep = Phi(d / (sqrt2 * f)) with f = 1, and f = 1.12 as a robustness bound.

3. DISAGREEMENTS
- W2-F F6, "f ~ 2": not supported. Directly f ≈ 1.0 (M = 512 CI upper about 1.11). The 2.4x row excess has four parts:
  - plug-in vs two-draw (about sqrt2);
  - duplicated rows (22 rows are 10 measurements);
  - first-draw selection;
  - specimen clustering.
- W2-H F6, "the excess comes from W-U's first-draw estimator": refuted. 22 of 22 are seed flips under the same PCT rule, and the estimator term is +0.1 groups. W2-H's "cluster bound" uses the group, but the normal run is shared per specimen.
- W-Z REPORT: "92.7% below the 95% bar" was a biased test, not seed sensitivity beyond the CIs. The bar was applied to a set that excluded W-U AMBIGUOUS rows, which only removes certificate -> INDETERMINATE flips.
- Plan T-SWAP-AUDIT3 s4: its 95% consistency bar has no eligibility count. Under correct noise alone the expected agreement on those rows is about 94.4% at row level (16.9 / 301).

4. NEXT QUESTIONS (ranked)
1. Should consistency and replication checks use specimen x measurement as the unit, with the predictive rule? Recompute the W-Z/W-U "consistency" as two-sided same-estimator flips on all 365 rows: 41 observed vs the expectation at f = 1.
2. DN at M = 256 gave f ≈ 1.2-1.3. A 12-group panel of fresh namespaces at M = 512 for DN only would settle whether DN SEs are slightly low for skewed arms (about 0.4 core-h).
3. Do family-level common-seed effects (F7, r about .04) inflate any C1 cross-specimen counts, such as "RELAY 50/196"? All C1 held evaluations share namespace conventions.
4. Should W-U's REL3 column be retired as a comparison target? It is structurally unable to certify rows REL2 left INDETERMINATE (F3).
5. The 8 same-data E0 rows where BOOTT certifies CHANCE and PCT does not: is BOOTT's one-sided narrowness on skewed DN calibrated? W2-H's FC_mirror covered FLIP-type boundaries.
6. Should the inventory duplicates (59b89e9d's double site_all/channel_all rows) be purged before any row-count claim?

5. INFERENCE LEDGER
```
N1 namespace diff | runner.py, zcommon, envs.build, engine rng, git log, KA prefix runs | world seeds only; worlds iid; KA exact 128/128 x2 | high | KA on prefix not full 512 | none | -
N2 dedupe | n_decomp D on W-Z pairs | 301->182 meas, 22->10 meas->10 groups->8 specimens; same-specimen normal r=.993 | high | allclose tolerance | inventory duplicates | Q6
N3 estimator share | n_attrib (REL2 PCT both draws), E0 W-U pipeline on W-Z data | 22/22 seed flips; E0 8/316 disjoint | high | REL2_WZ recomputed with copied W-N rule | BOOTT one-sided calib | Q4,Q5
N4 selection | all-365 transition count; n_sim D | flips balanced 21:20 over 365; 18 of 20 cert->INDET hidden in AMBIG; D(f=1)=9.78 vs 10 groups | high/medium | normal approx, W-Z-centred prior | specimen-level SD | Q1
N5 direct f (no compute) | n_fdirect W-O vs W-Z, 124 groups | f(DF)=1.01 [.91,1.11], f(DN)=.96 | high | W-O SE from CI width | family common effect | Q3
N6 direct f (fresh ns) | 6 groups x 3 ns, M=256 | f(DF)=1.00 [.78,1.39]; pooled 1.11 [.87,1.55]; DN 1.22 | medium | small panel, M=256 | DN at M=512 | Q2
N7 namespace-level component | n_xcorr | none per row; same-family cross-specimen r=.037 | medium | normal arm only | effect on C1 counts | Q3
N8 gate | N4-N6 | Phi(d/(sqrt2 f)), f=1 (1.12 robust): 2.33 / 2.6 SE for 95% keep; 3 SE conservative | medium-high | threshold choice is policy | count-level gate needs clustering | Q1
```

6. COMPUTE
- CPU only (CUDA_VISIBLE_DEVICES=-1, torch.cuda.is_available() asserted False), at most 2 threads, eager stepping (fork_single; no graph).
- Engine runs: 20 runs (2 KA + 18 replicates), 655 CPU-s.
- numpy analyses: about 1,000 CPU-s, of which n_sim about 750.
- Total about 0.45 core-h, under the 0.6 cap. Every run was under 10 min wall; the longest single process was n_sim at 15 min wall but low CPU share on the loaded host.
- No leases, no git writes, nothing written outside W2-N.
- Hygiene: W2-N/__pycache__ (n_decomp.cpython-312.pyc) was created; my rm was denied, so the principal may delete it.
