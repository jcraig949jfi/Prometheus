REPORT -- Does the landscape of intermediates, rather than endpoint payoff, predict discovery?

1. WHAT I SET OUT TO TEST

The claim under test: across the program's engines, whether a mechanism is found by
adaptive search is decided by the construction landscape leading to it (how much
its first intermediates pay, how often the variation operators produce them, and
how robust they are to further variation) and not by the payoff of the finished
mechanism; and, as a sharper sub-question, whether any accessibility measure
predicts discovery better than plain current fitness does. I did this in two parts.
First, a read-only table built from committed receipts: one row per engine and
mechanism, filling only cells that some receipt actually measured. Second, one test
on existing data in the only engine (Ares) where the endpoint is tied and arrival
rate was manipulated. Ares has three alternative memory carriers (a recurrent
edge, a leak coefficient "keep", plastic weights). Each reaches the fitness cap
when it is the only carrier allowed. The test asks whether first-step payoff,
arrival frequency or mutational robustness, measured separately, predicts which
carrier evolution actually uses, and whether a content-addressed arrival measure
beats current fitness at predicting time to discovery.

2. WHAT I DID

Repository: read-only clone, origin/main at 6ff2b2f8a (Ares code and runs on main).
Code exported with `git archive origin/main ares | tar -x -C work/R-29/src` and run only
there. No new evolutionary runs. All scripts and outputs are in
/home/jcraig/artemis-selftest/work/R-29.

Receipts read for the table (path@sha):
 - docs/essays/2026-09-24-accessibility-frontier.md@391395aac (s3, s5), and
   crius/runs/C2_SUMMARY.md and crius/CRIUS_C2_TERMINAL_REVIEW.md@origin/main (PARTS numbers)
 - ares/ARES_CYCLE2_REPORT.md, ares/DESIGN_C2.md, ares/runs/sweep_c2/{battery,basin,
   c3_summary}.json and 90 run+dissect JSONs @origin/main
 - roles/Ananke/pte/C1_REPORT.md@e35fb9704 and prometheus/ananke/envs.py,
   plants.py@e35fb9704 (task definitions; which plants exist)
 - roles/Aphrodite/pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md@4f937e88f;
   commit message of 48e17a7d1 (slice 2C)
 - herakles/HERAKLES_HISTORICAL_COLLIDER_V0/ACCESSIBILITY_WITHOUT_ACQUISITION_NEGATIVES.jsonl
   rows 1 and 11@2a5ac0117
 - Aether/AETHER_DECISIONS.md:93@abe63ef42 and origin/aether/research-block-2026-09-27
   (the transplant is still only a decision; nothing was built)
I could not read the prior-art note that the question cites, because it exists only
under a path I was told not to read. I used only the facts the question quotes from it.

Ares analyses (all read-only over the committed runs; the only code that executes the substrate is
the robustness probe in (c)):
 (a) ares_arrival.py: 90 lineages (W4 arms c1_all, c2_keep_subsidy, c3_keep_reachable,
     c2_recur_unstable, c2_tax_low, c2_tax_high; and W14/W15/W16 _present). For each,
     the 120 per-generation champion snapshots give: the first generation with a USABLE
     carrier (keep >= 0.9 on a live node; recurrent edge with |w| >= 1; any nonzero
     plastic rate), the retention of that carrier afterwards, and the champion's
     fitness jump at first arrival. These were compared with the final
     load-bearing carrier from the committed dissect files. Summary: ares_summary.py.
 (b) ares_k7.py: a test of accessibility against fitness. Outcome: time to threshold
     (from dissect). Predictors, using only information available by generation 3 or 5:
     champion fitness, and first arrival of a usable carrier. Reported as Spearman rho,
     partial rank correlations and a 2000-sample bootstrap of the difference.
 (c) ares_robust.py: mutational robustness of each carrier ON EVOLVED GENOMES. The
     hand-wired basin in the Ares report was measured on hand-built organisms, so this
     repeats it on evolved ones. Inputs: the final champions of c1_only_recur,
     c1_only_keep and c1_only_plast (10 each). Each gets 200 single mutations drawn
     from the substrate's own operator mix, plus 200 mutations targeted at the
     carrier's own parameter with the substrate's step sizes. Scored on 32 fresh
     balanced W4 episodes (seeds from 60000, not used by any run).
 (d) The committed single-mutation gradient battery (battery.json) was pooled over its 5
     champions.
 (e) ares_paths.py tried to measure how graded the evolved fitness path is. It turned
     out to be uninformative (see 3.3).
Outputs: data/ares_arrival.json, data/ares_robust.json, data/ares_paths.json.

3. RESULT

3.1 Cross-engine table (cells only from committed receipts; "--" = not measured)

 engine / mechanism        endpoint payoff     first-intermediate payoff    arrival / prior freq.      outcome
 Crius procedural reuse    +15.97, 10/10       recorder -0.001, invoker     partial machinery executed  not found, 0/36
                           (measured)          -0.002 (0/10), pair +1.14    by hundreds-thousands of
                                               at 26 edits (measured)       candidates per run (HIGH)
 Ares recurrence carrier   cap 40 alone        single-mutation: mean -0.03, raw 0.049, usable 0.017   found; load-bearing
                           (evolved, 10/10);   p_improve 0.013 (n=78)       /mutation; first usable     60/90 lineages
                           hand-wired 40.0                                  median gen 7
 Ares plasticity carrier   cap 40 alone        mean +0.42, p_improve 0.125  raw 0.049; earliest to      found but second;
                           (10/10)             (n=88) -- the BEST first step arrive (median gen 5)     load-bearing 32/90
 Ares keep carrier         cap 40 alone (9/10) mean -0.00, p_improve 0.00   raw 0.037, usable 0.000;    rarely used; load-
                           hand-wired 33.75    (n=55)                       0.023 under c3 (> recur)    bearing 10/90
 Ananke RELAY/HOLD/MAJ     --                  single-sensor or latch       random-program distal      found (50/196,
                                               already scores (by task      influence 0.3-0.7%         97/155, 19/162)
                                               definition; MAJ one-sensor
                                               ceiling 0.70)
 Ananke XOR, FLIP          -- (no hand-built   any single-input rule scores  --                         not found, 0/165
                           XOR plant exists)   exactly 0.5 (y = x1*x2 with
                                               independent coins): FLAT
 Aphrodite slice-2C fold   1.00 (measured)     n/a (exhaustive enumeration  search space 60-480        found 16/16
                                               of 60-480 candidates)        candidates: prior HIGH
 Aphrodite non-additive    --                  n/a                          task supply: mul/mod/powr   not tested (no
 abstractions (A16)                                                         0/32 qualify                qualifying family)
 Aether transplant         not built           not built                    not built                  --
 Herakles HC-T01 (control) --                  --                           breadth accessibility      fitness predicted
                                                                            effect large               acquisition as well
                                                                                                       or better
 Crius counters/fossils    ~0                  ~0 (neutral hitchhikers)     high                       found (syntax only)

Reading of the table. The table is mostly empty, which is itself a result. Only
Crius and Ares have both a measured endpoint and a measured intermediate profile.
Ananke's intermediate column is derived from the task definitions, not measured.
Aphrodite is enumeration, not incremental search, so it cannot test the claim.
Aether has no data.

3.2 Ares: the three accessibility axes, pulled apart on committed data
 - First-step payoff does NOT predict the winner. Plasticity has by far the best
   first step: p_improve 0.125 against 0.013 for recurrence and 0.00 for keep.
   Recurrence has essentially no first-step gradient, yet it is the most used
   carrier (60/90 lineages against 32/90), fastest when alone (median 10 gens,
   against 17.5 for plasticity and 30 for keep), and sets the pace when all
   three are available. This is exactly the case the question calls
   belief-moving: a found mechanism with a flat measured first step.
 - Arrival frequency or order does NOT predict it either. Two pieces of evidence:
   (i) when the keep carrier was made more reachable than recurrence (usable-keep
   creation rate 0.023 against 0.017), keep was load-bearing in only 2/10; and
   (ii) per lineage, in the 21 lineages where both usable keep and usable
   recurrence appeared and exactly one became load-bearing, the first to arrive
   won 11 of 19 non-tied cases. Under the raised keep rate, usable keep arrived
   first in 4 lineages and lost all 4. Plasticity arrives earliest overall
   (median gen 5) and is not the main carrier.
 - Robustness at the endpoint does NOT separate them on evolved genomes. Fraction of
   carrier-targeted single mutants keeping >= 50% of fitness, median of 10
   champions: recurrence 0.968, keep 0.970, plasticity 0.958 (Mann-Whitney p >= 0.38
   for every pair). The same holds under the full operator mix (0.92-0.94). The
   narrow keep basin (12% versus 61% viable) exists only in the report's
   hand-wired one-node organisms. Evolved keep champions carry several keep nodes,
   and the 0.98 clip ceiling actually shields them: half of all keep mutations clip
   back to 0.98.
 - Retention after first arrival differs a great deal (median: keep 0.16,
   recurrence 0.95, plasticity 0.97). But it is circular: a carrier that is not
   load-bearing is not held by selection. So it cannot serve as a predictor.
 - Current fitness against a content-addressed accessibility measure (time to
   threshold, n=90). At generation 3, champion fitness gives rho = -0.42 (p = 4e-5).
   Arrival of a usable recurrent edge gives rho = +0.37 (p = 3e-4). The bootstrap
   of |rho_fit| - |rho_acc| is 0.05, 95% CI [-0.18, 0.28]. The accessibility measure
   does not beat fitness. It does carry independent information: partial rho given
   fitness = 0.30, and the two are only weakly correlated (rank r = -0.25). At
   generation 5 neither predictor is significant.
 - Endpoint premise. The Ares design document says the hand-built keep carrier
   "is better" than recurrence (33.75 against 24.56). The Ares committed
   basin.json shows that 24.56 is recurrence at weight 3.0: a hand-built
   recurrence at weight 4 or more scores 40.0, the cap. So the hand-built optimum
   of recurrence is higher, not lower, and the "intrinsic superiority killed"
   step in the cycle-2 report rests on an untuned comparison. For evolved
   single-carrier lineages the endpoint is genuinely tied at the cap.

3.3 Instrument limit found: the champion training fitness in the Ares snapshots
reaches 90% of the cap within 2.5-6 generations in every arm (4 training
episodes, maximum of 128). So the evolved fitness path cannot be read for
gradedness from training fitness. Held-out evaluation is logged only every 5
generations.

Plain conclusion. Across engines, every case is still post hoc. In the one place where
the axes can be separated, Ares, none of the three named properties of the first
intermediate (its payoff, its arrival frequency, its endpoint robustness) predicts
which mechanism evolution uses. The only measurement that orders the carriers
correctly is the Ares hand-wired one-dimensional parameter sweep, and it
confounds "graded path along the parameter" with "basin width". No accessibility
measure beat current fitness.

4. DID IT RESOLVE THE QUESTION

Partly. For the cross-engine claim: no. The table shows it cannot yet be tested.
Only two engines have a measured intermediate profile, none has varied the
landscape at fixed endpoint in a paired design, and Aether's transplant does not
exist. For the Ares sub-question: yes, as far as committed data allows. Payoff,
frequency and robustness were separated and none predicts the outcome, and the
fitness-baseline test was passed only in the weak sense (the measure adds
information but does not beat fitness). Limits: 3 carriers in one world; the
gradient battery has only 5 champions (55-88 carrier-creating mutations per
carrier); "usable" thresholds are my choice (keep 0.9, |w| 1) and some keep-
load-bearing lineages never crossed 0.9; time to threshold is on a 5-generation grid.

5. CONSEQUENCES

 - Against a simple form of the claim. "Found mechanisms have a graded or frequent
   first intermediate" is contradicted in Ares: recurrence has a flat first step
   and wins, while plasticity has the most graded and most frequent first step and
   loses. Crius already showed that high frequency of partial machinery does not
   suffice (recorders and invokers were frequent and neutral). Together these say
   frequency is not sufficient in either engine and first-step payoff is not
   necessary in Ares. The claim survives only in a weaker, less falsifiable form
   ("something about the path"). Anyone building an accessibility ruler should
   know this: a scalar built from first-step payoff and/or frequency would have
   mis-ranked the Ares carriers.
 - False premise (small) and interpretation defect for Ares. The design-document
   comparison (keep 33.75 against recurrence 24.56) uses recurrence at a non-optimal
   weight. Ares's own basin.json gives recurrence 40.0 at weight 4 or more. So
   "intrinsic superiority killed" does not stand as written, and the "keep has the
   higher peak" framing in the cycle-2 headline should be corrected. The Ares seat
   and anyone citing its cycle-2 result as "wide basin beats higher peak" should
   know.
 - The basin-width explanation does not transfer from hand-wired to evolved
   genomes, at least at the endpoint (targeted-mutation robustness about 0.97 for
   all three carriers). This supports the Ares seat's own later note that
   decoupling keep's hold/load trade-off, rather than measuring basin width, is the
   decisive next test. It also suggests the relevant property is the payoff along
   the path to the carrier's working region, not robustness once there.
 - Fitness-baseline result reproduced in a second engine. A content-addressed arrival
   measure (as the Herakles diagnosis recommends) adds independent information
   (partial rho 0.30) but does not beat current fitness. Herakles, and whoever builds
   the proposed rulers, should know that content addressing alone did not clear the
   bar here.
 - What would actually test the claim: the paired same-endpoint, different-path
   experiment. In Ares, the cheapest version is the keep-decoupling arm Ares already
   specified. It changes the path to keep's working region while leaving the evolved
   endpoint at the cap.

6. COST

About 1.5 hours of my time. Under 1 CPU-minute in total: the snapshot scan took 2 s,
and the 6,000 robustness rollouts took a few seconds. Single process, under 100 MB
RAM. Not done: I could not read the prior-art note (it is in an excluded path). I ran
no new evolutionary arms (none are needed to answer what the committed data can
answer). I did not measure plasticity's hand-wired basin, because the basin code is
not committed. I did not measure Crius's arrival rate as a per-mutation number (only
the essay's qualitative "hundreds to thousands of candidates"). The Ananke and
Aphrodite rows are from reports and task definitions, not from re-analysis of their
rows.
