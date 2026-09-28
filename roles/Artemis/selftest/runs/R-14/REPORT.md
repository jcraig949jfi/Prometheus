# REPORT

## 1. WHAT I SET OUT TO TEST

The briefing asked, in several forms, whether an outcome used as evidence is already predicted by who
generated the row, by a single number scale, or by a shared source; whether cross-world invariants survive
recomputation inside a single world and inside matched parameter strata; and whether the way a sample was
assembled can manufacture a "law". I applied all of these to the most concrete target available in
committed material: the Cosmos law-foundry campaign (CWE/C0), whose two frozen laws ("law A", v3
coordinates; "law B", v4 coordinates) predict the SELECTIVE_PAYS verdict and are recorded as having
SURVIVED three sealed universes (well D, swarm E, clone F). The questions were: (a) does family (generator)
identity or any single coordinate already predict the verdict; (b) does a zero-parameter formula written
straight from the task/certificate definition (shared source) predict it as well as the mined laws, on
visible pools AND on the already-spent sealed universes; (c) do the laws hold within each family and within
matched strata (cost decile; family x V x K x R); (d) how much of the headline balanced accuracy (BA) comes
from how the pools were assembled (share of worlds far from the decision boundary), measured against a
replicate noise ceiling.

## 2. WHAT I DID

Code and data: origin/cosmos/c3-public-2026-09-24 @ 917edba0a7b9 (prometheus/cosmos/, roles/Cosmos/campaigns/),
exported with git archive into src/ and run only there (numpy; env -u GIT_DIR ...). Nothing in the clone was run.

- gen_pool.py: rebuilt the private oracle pools of configs c2 (seed 20260929) and c0b (seed 20260924) with the
  repo's own build_pools + Chamber.observe: 3 visible families (regs, ring, ca) x 1200 worlds each, 400 episodes.
  Check: per-family PAYS rates reproduce the committed oracle_summary.json exactly for both configs
  (c2: regs .160 ring .2683 ca .2608; c0b: .140 .2592 .2625). Output out/pool_{c2,c0b}_1200.json.
- analyze.py <cfg>: frozen laws rebuilt atom-for-atom from the committed mine_initial.json thresholds
  (law A: C-(G+exp(-N)) <= -1.0548 AND (C-log Q)K >= .1792, v3; law B: log(Q-CK) <= -.1577 AND C-G exp(-N) <= -.1022, v4)
  and evaluated with the repo's miner.law_from_json. Rungs compared: family identity (best BA over family
  subsets; AUC of family base rate); every single coordinate and two composites, best threshold in-sample and
  leave-one-family-out; family + one variable (per-family threshold, 5-fold CV); the zero-parameter analytic
  economy "PAYS iff G e^-N - C >= .10 AND (Q<1 OR CK/2 >= .10)" (the form Cosmos wrote post hoc in
  c0e/PREREG.md; it follows from the certificate: SEL beats LAST by G e^-N - C, beats LOG by about CK/2);
  the ceiling atom alone. Each scored pooled, within family, within log-C deciles per family, within
  family x V x K x R cells, and in bands |margin - 0.10| <= 0.02/0.05/0.10/0.20.
- replicate.py: re-ran the 2009 c2 pool worlds with |margin-0.10| <= 0.10 at replicate=1 (independent seed)
  to get a noise ceiling (how well one replicate's verdict predicts another's).
- holdout_audit.py, mcnemar.py: read-only audit of the ALREADY-SPENT, committed sealed adjudication rows
  (c0b/run_21fd1b2cc/G5_holdout.json, c0e/C0E.json G5E, c2/F_adjudication.json). Nothing was refit on them;
  single-variable thresholds come from the visible c2 pool. No sealed module was imported or run; no unspent
  holdout was touched.
Outputs: out/analysis_c2.json, out/analysis_c0b.json, out/replicate_c2.json, out/holdout_audit.json, out/mcnemar.txt.

## 3. RESULT

Visible pools (c2 pool; c0b pool in brackets), balanced accuracy:
- Generator (family) identity alone: 0.566 [0.578] (AUC 0.568). No generator-identity leak.
- Best single variable: K 0.699 in-sample, 0.679 leave-one-family-out [0.703/0.683]; C alone 0.651; G e^-N - C
  0.680; family + one variable (CV) <= 0.683. No single-scale leak. The ceiling atom alone gets only 0.677:
  the verdict needs both competitor terms.
- Zero-parameter analytic economy (no data, no fit): 0.960 [0.965], accuracy 0.977.
  Frozen law A: 0.964 [0.974]; frozen law B: 0.978 [0.980].
- Within-context re-tests: within family A .967/.935/.992, B .975/.980/.978 (regs/ring/ca); within log-C
  deciles A .941 B .950 (analytic .941); within family x V x K x R cells A .963 B .975. The laws do not
  depend on between-family or between-scale differences; they hold inside every context tested.
- Assembly and noise: only 3.9% of the pool lies within +-0.02 of the 0.10 threshold and 11.6% within +-0.05.
  There, BA falls to A .70/.83, B .68/.87, analytic .57/.78, but the replicate noise ceiling is also low:
  .72 (+-0.02), .86 (+-0.05), .94 (+-0.10). The mined laws sit at the noise ceiling near the boundary; the
  analytic formula sits below it. The high headline BA is mostly a property of a pool dominated by
  easy worlds far from the boundary; near the boundary no rule can do much better with one replicate.

Already-spent sealed universes (240 worlds each; committed rows, recomputed BA matches the reported values):
                 law BA   analytic 0-param BA   reported 5-NN   best visible 1-var   rows far (|m-.1|>.1)
  D / law A      0.983    0.973                  0.841           C 0.725              51%
  E / law A      0.972    0.971                  0.769           K 0.708              52%
  F / law A      0.930    0.887 (v3 coords)      0.841           C 0.719              35%
  F / law B      0.955    0.943 (v4 coords)      0.833           C 0.713              35%
Paired exact McNemar, mined law vs analytic formula (law-right/analytic-wrong vs reverse): D 2 vs 4 (p .69),
E 2 vs 4 (p .69), F-A 4 vs 0 (p .13), F-B 3 vs 8 (p .23). On none of the three sealed universes is a mined
law distinguishable from the formula written from the task definition. Errors within +-0.05 of threshold:
law B on F 11 of 11; law A 4 of 7 (D), 3 of 8 (E), 4 of 11 (F).

Plain conclusion: there is no generator-identity or single-number-scale tautology, and the laws survive every
within-context re-test. But the outcome is a near-deterministic function of spec-side coordinates through the
certificate's own definition (shared-source tautology): a formula with zero fitted parameters, derivable
without running any world, matches the mined laws on visible pools and on all three sealed universes. The
sealed-transfer numbers therefore test the correctness of each substrate's declared coordinate map (and the
v4 expected-cost correction, which is where F-A vs F-B differ), not the discovery of a law. The comparison
baseline the campaign reported (5-NN, majority) is far weaker than the relevant rung.

## 4. DID IT RESOLVE THE QUESTION

Partly. For the one engine where committed data allowed it (Cosmos), yes: generator-identity and scale leaks
were measured and are absent; within-world and within-stratum re-tests were run and the laws hold; the
shared-source tautology was measured directly and dominates the evidence; the assembly effect was quantified
against a noise ceiling. Not done: the same audit for the other engines named in the briefing (SFE, Aether,
Ares, NPE Z80 worlds, Ensorain), the "which world maximizes the metric" audit for other world-level metrics,
and the random-projection control for the two-representation agreement claim. A constraint-preserving
permutation null was not needed separately: the miner's null already permutes within family, and the
within-cost-decile BA (.94-.95) already exceeds any stratum-permuted null (about .5).

## 5. CONSEQUENCES

- Reproduction of something already known, now quantified: Cosmos itself records law A as a
  "planted-invariant recovery" with 97.5% agreement with a hand-derived law on D and E. This run extends it
  to F and to law B, shows the mined-vs-formula difference is not significant on any sealed universe, and
  shows the same on the visible pools.
- Instrument/harness point (for Cosmos, and whoever adjudicates Cosmos results, e.g. Harmonia): the baseline
  ladder for any law should include a zero-parameter "definition" rung (the outcome's own economics written in
  the declared coordinates) and a replicate noise ceiling, not only majority and 5-NN. Transfer credit should
  be counted as the margin over that rung (here +0.001 to +0.043 BA, none significant), and BA should also be
  reported in a near-boundary band, because pool assembly (35-52% of sealed worlds far from the threshold)
  sets most of the headline number.
- Clean nulls: no generator-identity tautology (family BA ~0.57) and no single-scale tautology (best single
  variable ~0.70) in Cosmos's SELECTIVE_PAYS data; within-context re-tests pass. These are not failures of
  the laws.
- The planned Cosmos research threads that ask "is the shared ceiling the transferable core" and "effective
  number of universes" should treat the analytic formula as the null law to beat; a new sealed or foreign
  generator only adds information if its verdicts are not already fixed by that formula (e.g. a mechanism or
  coordinate the formula gets wrong, as the v3-vs-v4 cost correction on F shows).

## 6. COST

About 1.5 hours of my time. CPU: about 8 CPU-minutes (two pool rebuilds of ~2 min each run in parallel,
1.5 min replicate pass, seconds for analysis); at most 2 processes; well under 2 GB. Not done: other engines,
the second-representation random-projection control, and fresh sealed worlds (none created or consumed).
