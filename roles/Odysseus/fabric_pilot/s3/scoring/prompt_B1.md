You are a blind quality scorer for research reports about the Prometheus research repository. You receive several
reports, each labelled X###. They come from different sources, and you do not know which. Score each report
independently against the rubric below. Do not try to find out where a report came from: do NOT search the
repository for a report's own sentences, title or label. Only verify the evidence its claims cite.

Tools: Read, Grep and Glob inside the repository, and `rogit` for git history (a single command, used exactly like
git).

Rubric (frozen, S3_PROTOCOL s5). Score each item 0, 1 or 2:
1. EVIDENCE: are the load-bearing claims tied to checkable primary evidence (path:line, commit:path, data)?
   0 = mostly unsupported, 1 = partly, 2 = consistently.
2. CORRECTNESS: pick the 3 highest-stakes claims and verify them in the repository yourself.
   0 = a load-bearing claim is false, 1 = unverifiable or partly true, 2 = all 3 verified true.
   Name the 3 claims and what you found.
3. ANSWERS THE QUESTION: does it answer what it set out to answer, or state precisely why it could not?
   0 = no, 1 = partly, 2 = yes.
4. LIMITS STATED: does it say what was not checked and what would change the conclusion?
   0 = no, 1 = partly, 2 = yes.
5. USABLE: could a research principal act on it without redoing the work?
   0 = no, 1 = with significant rework, 2 = yes.

Write `scores.json` in your output directory:
{"<label>": {"evidence": n, "correctness": n, "answers": n, "limits": n, "usable": n, "total": n,
             "checked_claims": ["claim -> verified/false/unverifiable, with path:line"], "notes": "one or two sentences"},
 ...}
Finish with one line per report: `<label>: <total>/10`.


---------------- THE REPORTS ----------------


======== REPORT X003 ========

REPORT -- Blind batteries and co-adapted generators (Apollo reasoning organism)

1. WHAT I SET OUT TO TEST
Apollo's best organism scores 0.60 (mix-adjusted) on its owner's home battery but 0.0667 on 42
tasks another seat wrote blind. Two questions follow. (a) Is that collapse a property of the
organism, or a quirk of one particular blind author -- i.e. does it replicate when a third,
independent author writes the tasks? (b) The revival review proposes validating any new task
generator by checking that it "reproduces the known blind result" before trusting it. Is that a
workable gate: does it reject co-adapted generators, and does it also reject generators that are
simply broken? I could only test this on Apollo; the other engines named as lenses (NPE Z80
worlds, [redacted], [redacted], BEE z80atlas) have no committed blind-authored battery that I found, so
"do current capability numbers survive" is answered here for Apollo only.

2. WHAT I DID
Code/data exported from the read-only clone at origin/main 6ff2b2f8a (git archive of apollo/src,
apollo/data, apollo/scripts, apollo/cycles/campaign_20260825, roles/Charon/apollo_e9,
agents/hephaestus/src) into work/[redacted]/src; run with GIT_* unset.
 - Reproduction: python3 apollo/scripts/e9_score.py -> raw 0.0476, mix 0.0667, home 0.6000,
   40 abstain / 2 correct / 0 guess. REPRODUCED exactly.
 - Wrote work/[redacted]/gen_blind.py: a third-author procedural generator, 7 categories, 3
   structurally different construction routes per category, 4 candidates, gold computed by
   construction. Written and hash-frozen (gen_blind.FROZEN.sha256) BEFORE reading any Apollo
   operator source, the home generator, the home prompts or the blind author's prompts. Known to
   me: category names, schema, and the two example prompts quoted in the revival review. One
   post-freeze edit: a distractor-collision bug fix (assertion crash), made before reading any
   organism code, re-hashed and logged.
 - work/[redacted]/calib.py: scores the recorded 0.833 organism (KNOWN_0833, same eval path as
   e9_score.py, home-category-mix weighting, E9 tolerance +/-0.15) on 30 batteries of 42 tasks
   (6/category) from each of six generators:
     home_reseed        the home generator (gen_clean_canary_v01.py) with fresh seeds
     home_reworded      home construction + synonym swaps (larger->bigger/greater, etc.)
     home_prefixed      home construction + the lead-in "Question: " on every prompt
     blind_third_author my gen_blind.py
     degenerate_shuffled  INVALID: my prompts with words shuffled (gold unrecoverable)
     invalid_wrong_gold   INVALID: home construction with gold replaced by a wrong candidate
   plus one 420-task battery from gen_blind. Output: calib_out.json.
 - work/[redacted]/leak.py: 100 batteries each at co-adapted fractions f = 0..1 (a task slot is a
   home-construction task with prob. f, else a third-author task). Output: leak_out.json.
 - Read the organism's parse operators afterwards to explain the answers it did give.

3. RESULT
Mix-adjusted accuracy of the 0.833 organism (30 batteries x 42 tasks each):
  generator             mean mix   sd     abstain  guess   passes "reproduce 0.0667 +/-0.15"
  home_reseed           0.600      0.000  0.57     0.00    0%
  home_reworded         0.600      0.000  0.57     0.00    0%
  home_prefixed         0.400      0.000  0.71     0.00    0%
  blind_third_author    0.026      0.027  0.90     0.07    100%
  degenerate_shuffled   0.000      0.000  1.00     0.00    100%
  invalid_wrong_gold    0.000      0.000  0.57     0.43    100%
  (fixed batteries: Charon 0.0667 / 95% abstain / 0 guess; home 0.600)
Third-author n=420: mix 0.022; per category 0 everywhere except transitivity 0.067 and
consistency_check 0.083. Where the organism did fire on my tasks it was at or below chance:
transitivity 4 correct / 16 wrong of 20 fired; consistency 5 / 17 of 22 fired (4 options).
Cause, from source: the transitivity parser only accepts "greater-direction" comparatives
(taller|bigger|...|richer than), silently drops "younger/slower/poorer than" facts, and only
recognises a few superlatives, so it answers from a partial chain.
Leak sensitivity of the gate (pass rate at f = co-adapted fraction):
  f=0.0 100%, 0.1 100%, 0.2 96%, 0.3 72%, 0.4 30%, 0.5 10%, 0.7 0%, 1.0 0%.
Conclusions:
 (a) The collapse replicates with a third, independent author: 0.60 at home -> ~0.02-0.03 blind,
     dominated by abstention (non-recognition). It is not an artefact of one author. Home-number
     fragility is also extreme on the co-adapted side: a single harmless prefix "Question: "
     drops numeric_comparison from 1.0 to 0.0 (0.60 -> 0.40), while synonym swaps inside the
     regex's word list change nothing.
 (b) "Reproduce the known blind result" rejects fully co-adapted generators (0% pass) but
     ACCEPTS every broken generator I tried (100% pass) and accepts generators that are up to
     ~20-30% co-adapted most of the time. Because the calibration target sits at the floor,
     reproducing it is evidence of NOT being co-adapted with this organism, never of being a
     valid task generator. As a trust gate it is necessary but far from sufficient.

4. DID IT RESOLVE THE QUESTION
Partly. For Apollo, yes: its capability number does not survive a different author (now shown
with two independent authors), and the proposed generator-validation gate is shown to be one-sided
with measured leak tolerance. Not resolved: whether numbers from NPE, [redacted], [redacted] or BEE survive
a blind author -- none has a committed blind battery and building one per engine does not fit
this budget. I also did not run the state-injection (parser vs capability) experiment; the
fired-task accuracy above is only a weak hint that the reasoning layer does not transfer either.

5. CONSEQUENCES
 - Reproduction of something known: E9 is reproducible from source and replicates with a third
   blind author (my gen_blind.py is a renewable, frozen, independently authored instrument that
   Apollo/Lexis can use; Lexis's notes say a second blind author was needed for admission of
   their G7 measurement -- this can serve, with the caveat that its author has now read the
   organism source, so future versions are no longer blind).
 - Harness/method defect (new): a generator-validation gate anchored only on a floor-level blind
   result cannot tell an independent generator from a broken one. Any engine adopting "validate
   the generator by reproducing a known blind result" (NPE, [redacted] world generators; [redacted]'s
   replacement for spent sealed universes) needs at least: (1) an independent gold verifier for
   every generated task, (2) a positive anchor -- a solver or organism that should score HIGH on
   the generator and does, and (3) a profile check (abstain/guess shape, per-category), since a
   single mix number within +/-0.15 cannot detect up to ~20-30% co-adapted content at n=42.
   Anchor target results should ideally be mid-range, not at the floor.
 - Who should know: Apollo (revival plan step "X-heldout generator calibrated against the blind
   battery"), [redacted] (counterfeit/X-heldout doctrine), Lexis, and any seat building world/task
   generators (NPE, [redacted], [redacted]).

6. COST
About 1.25 hours of my time. CPU: under 10 CPU-seconds total (all scoring is deterministic
regex/pipeline code); peak RSS ~50 MB; single process. Not done: state injection; blind batteries
for other engines; a positive-anchor solver for my generator (its validity rests on
construction-time gold, spot-checked by hand on 14 tasks, not on an independent solver).



======== REPORT X002 ========

# REPORT -- can a declared varied / held / observed lens field make engine convergence measurable?

## 1. WHAT I SET OUT TO TEST

The proposal is that if every engine's experiment record declared what it varies and what it observes
(and, in the extended form, what substrate it holds fixed), then convergence between seats -- the known
case being three independent Z80 byte-VM builds made from one directive -- would become detectable
mechanically. I tested three things on real, already-committed experiment records: (a) whether the field
can be assigned reliably at all (two independent annotators agreeing), (b) whether collisions on the
proposed (varied, observed) pair recover the known Z80 convergence and how many false alarms they raise,
and (c) whether adding a held-substrate code changes (b). I did not build an index or modify any
registry; this is a retrospective measurement of whether the field works as an instrument.

## 2. WHAT I DID

- Corpus: 33 preregistration records from 11 seats/engine lines, extracted verbatim (first 24 KB each)
  from the read-only clone: 31 from origin/main @ 6ff2b2f8a and 3 [redacted] records from
  origin/[redacted]/multiday-campaign-2026-09-26 @ ee7a7d954. The full list with paths is in
  corpus_index.tsv; the texts are in corpus/X01..X33.txt. 13 records are Z80-family ([redacted] z80atlas x4,
  [redacted] coupling/multiday/grounding x3, [redacted] envgate/envgate2/census/denovo x4, [redacted]
  z80_threshold x2, which runs on [redacted]'s VM); the rest cover [redacted], [redacted], [redacted] (WTP),
  [redacted] (PTE), [redacted], [redacted]'s SFE campaigns, [redacted] CW01, [redacted], SFE D8, the [redacted]
  kernel and [redacted] natural-induction.
- Codebook (CODEBOOK.md): varied = the seven proposed values (environment, representation, physics,
  organism-boundary, memory, communication, improver) plus none/other; observed = 9 values plus other
  (replication, descent, population-stats, complexity, task-skill, law-invariant, signal-dependence,
  improvement-rate, instrument); held = 10 substrate families (byte-vm, lattice-field, world-graph,
  float-memory, packet-network, neural-swarm, bitstring, code-worker, llm-agent, other).
- Two independent annotators (separate model sub-agents) coded all 33 records from the record text and
  the codebook only. They were not told the engine names, the landscape document, or the ground truth.
  One worked forward and one worked in reverse order. Outputs: annot_A.json and annot_B.json.
- Ground truth for "known convergent": every cross-seat pair of records where both records are Z80-family
  (62 of 480 cross-seat pairs). This is the convergence the source document named.
- Analysis: analyze.py plus an inline follow-up (output in analysis_out.txt). I computed Cohen's kappa
  and flagged-pair recall and precision under three keys: (varied1, observed1), held, and the triple.
- Premise checks: atlas/harvest/archaeon_campaigns.py on origin/main still matches only
  [redacted]/campaignN/, so envgate, envgate2 and z80atlas are not harvested (the premise holds). No
  varied/observed field exists anywhere under atlas/. The named lens-card prototype exists only under
  an excluded path, so I did not read it or use it.

## 3. RESULT

Reliability (n=33, primary code): varied kappa 0.73 (79% agreement); observed kappa 0.74 (79%; the
annotators' code sets overlapped on 100% of records); held kappa 0.76 (82%). The combined (varied,
observed) pair is less reliable: kappa 0.57 (61%). Disagreements cluster where the seven-value varied
vocabulary does not fit. [redacted] "change almost everything" was coded environment by A and physics by
B on all 3 records. PTE C1 was coded communication by A and physics/environment by B. [redacted] and
[redacted] CW01 got memory or none versus representation or environment.

Detection of the known Z80 convergence (62 cross-seat pairs; annotator A / B):

| key                         | flagged | true pos | false pos | recall    | precision |
|-----------------------------|---------|----------|-----------|-----------|-----------|
| (varied1, observed1)        | 25 / 25 | 21 / 14  | 4 / 11    | 0.34/0.23 | 0.84/0.56 |
| any varied & any observed   | 52 / 52 | 34 / 33  | 18 / 19   | 0.55/0.53 | 0.65/0.63 |
| held only                   | 100/ 87 | 62 / 62  | 38 / 25   | 1.00/1.00 | 0.62/0.71 |
| (held, varied1, observed1)  | 21 / 14 | 21 / 14  | 0 / 0     | 0.34/0.23 | 1.00/1.00 |

What the collisions contain:
- Under both annotators, the triple collides only for [redacted], [redacted] and [redacted] Z80 records
  (physics x replication on a byte VM). [redacted]'s Z80 records (environment x descent/replication)
  never collide with any other seat under either annotation.
- So the varied/observed pair does not measure the Z80 triplication as such. It splits it. [redacted]
  and [redacted] (plus [redacted], which reuses [redacted]'s VM) ask the same question on the same
  substrate; [redacted]'s build, on that substrate, asks a different question. This matches the source
  document's own verdict: not distinct as a world, distinct as a method. Here that verdict was reached
  independently by blind coding.
- The substrate (held) is what captures "three builds of one world". It does so with recall 1.00 but
  precision 0.62-0.71. The false alarms are shared generic families, for example several different
  world-graph systems, and SFE D8's stack VM counting as byte-vm.
- Collisions on the pair alone outside the Z80 family (4 for A, 11 for B) are mostly vocabulary
  coarseness: BEE kernel versus WTP (representation x task-skill), and CWE versus PTE (physics x
  law-invariant, B only). One looks like a possibly real overlap nobody had listed: [redacted]'s
  SFE-driven campaign records and [redacted] both code as improver x improvement-rate, under both
  annotators. SFE D8, [redacted] and [redacted] natural-induction all code as improver x task-skill.
- Within one seat, varied is not constant. [redacted] spans environment, improver and none; NPE spans
  physics, environment and memory. The lens is a property of an experiment, not of an engine, so an
  engine-level tag would hide both convergence and divergence.

Plain conclusion: the field can be assigned with substantial reliability, and it does make convergence
measurable, but only as the three-part key (held, varied, observed). The two-part varied/observed pair
alone has 23-34% recall and 56-84% precision on the known case. It cannot see "same world built three
times", because that convergence is in the held substrate, not in the lens. The seven-value varied
vocabulary is the weakest part: most disagreements and most false alarms trace back to it.

## 4. DID IT RESOLVE THE QUESTION

Partly. It settles whether the field is workable (yes, with kappa about 0.73-0.76 per field) and what
it detects (lens convergence, not substrate convergence), on 33 records with one known convergence
case. Four things remain open:
- The ground truth is defined by substrate, which makes the held key's perfect recall partly circular.
  The informative numbers are the pair's low recall and the triple's zero false alarms.
- The annotators were model sub-agents, not the seats. Self-declared tags might agree more, or might
  be gamed.
- There is only one known-convergent case, and 33 records is a small sample.
- I did not test whether "must justify or merge" changes seat behaviour.

## 5. CONSEQUENCES

- False premise, partly: "two engines on the same varied/observed pair must justify or merge" would
  not have caught the Z80 triplication as a whole. It would have cleared [redacted]'s build and flagged
  only [redacted] versus [redacted]. A held/substrate code is needed. Recommend the record carry
  held_substrate plus a concrete substrate_name (implementation path), and that convergence be
  defined on the triple.
- Instrument design fix: the varied vocabulary needs sharper boundaries between environment and
  physics (the CWE and PTE disagreements), a "communication-physics" rule, and an explicit "none"
  for census/instrument records. Declare the field per experiment, not per engine.
- A candidate lead, not verified: [redacted]'s SFE campaigns and [redacted] both test whether an
  improver gets better at improving (improver x improvement-rate), and SFE D8, [redacted] and [redacted]
  natural-induction share improver x task-skill. The seats involved, or whoever owns the cross-engine
  standard, should check whether this is real duplication.
- A known result reproduced independently: [redacted] and [redacted] Z80 work share one lens; [redacted]'s
  Z80 work is methodologically distinct.
- Premise confirmed: the Atlas harvester still does not index envgate, envgate2 or z80atlas, and no
  lens field exists in atlas/. Whoever owns Atlas and the cross-engine contract should know. The
  artefacts (CODEBOOK.md, annot_A/B.json, analyze.py) are a ready-made pilot for that standard.

## 6. COST

About 45 minutes of my own time. Local CPU was negligible (well under 1 CPU-minute; git extraction and
a pure-Python analysis). Two annotation sub-agents ran concurrently for about 5-6 minutes each. I did
not use Postgres, did not run any repository code, and did not consult the lens-card prototype (it sits
in an excluded path). Not done: annotation by the seats themselves, a larger corpus (more than 280
prereg files exist on main), a non-substrate-defined ground truth, and any registry change.



======== REPORT X011 ========

# REPORT

## 1. WHAT I SET OUT TO TEST

The briefing asked, in several forms, whether an outcome used as evidence is already predicted by who
generated the row, by a single number scale, or by a shared source; whether cross-world invariants survive
recomputation inside a single world and inside matched parameter strata; and whether the way a sample was
assembled can manufacture a "law". I applied all of these to the most concrete target available in
committed material: the [redacted] law-foundry campaign (CWE/C0), whose two frozen laws ("law A", v3
coordinates; "law B", v4 coordinates) predict the SELECTIVE_PAYS verdict and are recorded as having
SURVIVED three sealed universes (well D, swarm E, clone F). The questions were: (a) does family (generator)
identity or any single coordinate already predict the verdict; (b) does a zero-parameter formula written
straight from the task/certificate definition (shared source) predict it as well as the mined laws, on
visible pools AND on the already-spent sealed universes; (c) do the laws hold within each family and within
matched strata (cost decile; family x V x K x R); (d) how much of the headline balanced accuracy (BA) comes
from how the pools were assembled (share of worlds far from the decision boundary), measured against a
replicate noise ceiling.

## 2. WHAT I DID

Code and data: origin/[redacted]/c3-public-2026-09-24 @ 917edba0a7b9 (prometheus/[redacted]/, roles/[redacted]/campaigns/),
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
  economy "PAYS iff G e^-N - C >= .10 AND (Q<1 OR CK/2 >= .10)" (the form [redacted] wrote post hoc in
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

Partly. For the one engine where committed data allowed it ([redacted]), yes: generator-identity and scale leaks
were measured and are absent; within-world and within-stratum re-tests were run and the laws hold; the
shared-source tautology was measured directly and dominates the evidence; the assembly effect was quantified
against a noise ceiling. Not done: the same audit for the other engines named in the briefing (SFE, [redacted],
Ares, NPE Z80 worlds, [redacted]), the "which world maximizes the metric" audit for other world-level metrics,
and the random-projection control for the two-representation agreement claim. A constraint-preserving
permutation null was not needed separately: the miner's null already permutes within family, and the
within-cost-decile BA (.94-.95) already exceeds any stratum-permuted null (about .5).

## 5. CONSEQUENCES

- Reproduction of something already known, now quantified: [redacted] itself records law A as a
  "planted-invariant recovery" with 97.5% agreement with a hand-derived law on D and E. This run extends it
  to F and to law B, shows the mined-vs-formula difference is not significant on any sealed universe, and
  shows the same on the visible pools.
- Instrument/harness point (for [redacted], and whoever adjudicates [redacted] results, e.g. [redacted]): the baseline
  ladder for any law should include a zero-parameter "definition" rung (the outcome's own economics written in
  the declared coordinates) and a replicate noise ceiling, not only majority and 5-NN. Transfer credit should
  be counted as the margin over that rung (here +0.001 to +0.043 BA, none significant), and BA should also be
  reported in a near-boundary band, because pool assembly (35-52% of sealed worlds far from the threshold)
  sets most of the headline number.
- Clean nulls: no generator-identity tautology (family BA ~0.57) and no single-scale tautology (best single
  variable ~0.70) in [redacted]'s SELECTIVE_PAYS data; within-context re-tests pass. These are not failures of
  the laws.
- The planned [redacted] research threads that ask "is the shared ceiling the transferable core" and "effective
  number of universes" should treat the analytic formula as the null law to beat; a new sealed or foreign
  generator only adds information if its verdicts are not already fixed by that formula (e.g. a mechanism or
  coordinate the formula gets wrong, as the v3-vs-v4 cost correction on F shows).

## 6. COST

About 1.5 hours of my time. CPU: about 8 CPU-minutes (two pool rebuilds of ~2 min each run in parallel,
1.5 min replicate pass, seconds for analysis); at most 2 processes; well under 2 GB. Not done: other engines,
the second-representation random-projection control, and fresh sealed worlds (none created or consumed).



======== REPORT X006 ========

# REPORT

## 1. WHAT I SET OUT TO TEST

The program has three connected proposals that were never started. (a) A "reversible
core" experiment: an agent whose update is a bijection, whose state is bounded and which
receives fresh input, must push one item per step out through a priced export channel.
Does it learn to export irrelevant state, compared with random export (and FIFO export)
at a matched elimination curve? (b) A distinction-survival assay: which input distinctions
survive in a system's accessible state, with counter-keyed RNG and a matched blind control.
(c) A common replay-and-perturb hook with full-state hashes (RNG included). No reversible
agent substrate exists on any host, so within this budget I built the smallest honest one
myself and used it to answer the design question behind (a), and to calibrate the parts of
(b) and (c) that can be checked on a toy: does the experiment as specified discriminate
anything, and do the proposed controls and fixtures behave as the stewards expected?

## 2. WHAT I DID

Inputs: only the design memo, falsifier table and M2 attack notes (read, not run) at
repo origin/main 6ff2b2f8a (memo first committed at d50103524). No engine code was run;
I did not archive or execute repository code. All code is new, under
[redacted]
- revcore.py (sha256 27cff279...): bounded reversible agent. K=8 slots; each step one new
  item (value bit, tag bit, birth stamp) arrives; the policy picks one of the K+1
  candidates and swaps it onto an export tape (outside the boundary, never read back).
  Latent relevance rel~Bern(0.25) is generator-side; tag = rel with prob (1+rho)/2.
  Competence = recall of target weight held (accuracy = 0.5 + 0.5*recall), queried every
  step after t=100 of N=400. Two regimes: "decorr" (target uniform over all relevant items
  so far: relevance independent of age by construction) and "coupled" (target weight
  exp(-age/16): relevance correlated with recency). RNG is counter-based splitmix keyed by
  (seed, t, site, purpose), with a "seq" option (sequential stream whose tie-break draw
  count depends on state) for the cheat fixture. Includes an explicit inverse and a
  full-state SHA-256 (slots + RNG counter/key + clock).
- [redacted].py: inverse run from final state + tape back to the empty initial state
  (64 episodes x 400 steps): exact. Replay to t=200 gives identical full-state hashes in
  both RNG modes; a perturbation at t=150 changes the hash.
- experiment.py (sha256 4eb9181c...): per (regime, rho in {0,.1,.25,.5,1}): learn a
  3-weight linear export score (tag, age/K, tag*age/K) by cross-entropy ES (12 gens x 16,
  256 training seeds); evaluate on 2000 held-out seeds with common random numbers:
  learned, random, FIFO, blind_matched (the learned policy fed an independent tag with
  the same marginal: relevance-blind, same dynamics), planted (export lowest tag; positive
  control). Equivalence margin = 95th pct |random - random| over 10 independently keyed
  pairs on 512 dev seeds; verdicts by 90% CI (TOST) against that margin. Merge-time curve =
  distribution of residence time at export (KS distance reported).
- dsa.py (sha256 bac18a34...): paired runs (2000 pairs) differing only in one item born at
  t*=200 (value flip = inert distinction; tag flip = dynamics-relevant distinction);
  fraction of pairs whose accessible state still differs at t*+h, stratified by that
  item's generator relevance; random vs tag-selective export; keyed vs sequential RNG.
Commands: python3 [redacted].py; python3 experiment.py (outputs experiment.log,
out_experiment.json); python3 dsa.py (dsa.log, out_dsa.json). A first experiment run
(experiment_v1.log, out_experiment_v1.json) scaled age by N; that made the age feature
too small for the learner to use (it could not rediscover FIFO in the coupled regime,
learned 0.297 vs FIFO 0.368 on training seeds). I fixed the scaling to age/K and reran; v2
is reported. The decorr results are unchanged between versions.

## 3. RESULT

Reversible core (recall; margin decorr 0.0005, coupled 0.0036; CI = 90%):

  regime   rho  I(tag;rel)  learned random fifo  blindM planted  learned-random (verdict)      learned-blindM (verdict)
  decorr   0    0.000       .0370   .0369  .0369 .0363  .0370    +.0001 [-.0006,.0008] UNRESOLVED +.0007 UNRESOLVED
  decorr   .1   0.005       .0429   .0369  .0369 .0369  .0429    +.0060 SELECTIVE             +.0060 SELECTIVE
  decorr   .5   0.143       .0745   .0369  .0369 .0370  .0745    +.0375 SELECTIVE             +.0375 SELECTIVE
  decorr   1    0.811       .1501   .0369  .0369 .0364  .1501    +.113  SELECTIVE             +.114  SELECTIVE
  coupled  0    0.000       .3676   .3090  .3676 .3676  .2301    +.0586 SELECTIVE (false)     .0000 EQUIVALENT
  coupled  .1   0.005       .3745   .3090  .3676 .3577  .2601    +.0655 SELECTIVE             +.0168 SELECTIVE
  coupled  .25  0.034       .4147   .3090  .3676 .3231  .3090    +.106  SELECTIVE             +.092  SELECTIVE
  coupled  1    0.811       .8505   .3090  .3676 .2073  .6307    +.542  SELECTIVE             +.643  SELECTIVE

- Export rate is identical for every policy (exactly 1 item/step) by conservation; it
  needs no matching. The merge-time (residence) curves are NOT matched by random export
  (KS learned vs random 0.17-0.83) but are matched by blind_matched (KS <= 0.001).
- The outcome is set by the generator: whenever the observable features carry any
  information about future relevance (even 0.005 bits/item), the learned exporter beats
  random far beyond dev noise. With zero information (decorr, rho=0) every policy is
  identical in expectation; the "random = learned" reading then comes out EQUIVALENT or
  UNRESOLVED depending only on how noisy the arbitrary learned weights are (v1:
  EQUIVALENT; v2: UNRESOLVED, CI half-width just above the margin).
- Coupled regime, rho=0: the learner rediscovers FIFO. Against RANDOM export it earns a
  large, significant "selective advantage" (+.059) that is pure recency. The
  curve-matched blind control (and FIFO) read EQUIVALENT (0.0000), correctly.
- The planted positive control (tag-only selective policy) FAILS to beat random in the
  coupled regime at rho <= .25 (-.079 at rho=0, 0.000 at .25), because it discards recency.
  A positive control that works in one task can be silent in another.
- blind_matched can be WORSE than random (coupled rho=1: .207 vs .309): holding the
  learner's age profile with blind content is a different, harsher baseline.

Distinction-survival assay on the reversible core (fraction of pairs still differing):
- Keyed RNG: every distinction leaves accessible state once its item is exported (differ
  -> 0.000-0.003 by h=199). In a reversible core "merging" in accessible state is export
  and nothing else; the full state (including the tape) never merges.
- Relevance stratification works on this substrate: rho=1, selective export, inert (value)
  flip: relevant items differ 0.906/0.743/0.349/0.027 at h=0/8/32/128, irrelevant items
  0.000 at all h; random export shows no strata difference (0.131 vs 0.129 at h=16).
- Cheat fixture reproduced: with a sequential RNG whose draw count depends on ties, a
  tag flip leaves 49% (rho=0) and 67% (rho=1) of pairs NEVER reconverging at h=199,
  versus 0.0% and 0.3% with keyed RNG. The inert value flip is immune (does not change
  draw counts). The contamination starts at once (h=1: 0.96 seq vs 0.85 keyed).
- Pair-type matters: tag flips (which change how the item is treated) erase the relevance
  strata (rel .743 vs irr .698 at h=8), value flips show them cleanly.
- My own harness bug, fixed before reporting: the first DSA run took the relevance oracle
  from the keyed generator path while the sequential-RNG runs drew items from another
  stream, so the strata were wrong in seq mode. The oracle must come from the same
  generator path as the specimen.

Replay-and-perturb hook: a common interface is small in a toy (replay to t, perturb one
item, full-state hash including RNG counter; bit-identical replays). On origin/main a
term grep found checkpoint state hashes only in SFE (currently down); no cross-engine
replay-and-perturb interface. That was a grep, not a code audit.

## 4. DID IT RESOLVE THE QUESTION

Partly. On the design question behind the reversible-core experiment: yes, at toy scale.
The experiment as specified is mostly decided by construction. A bounded reversible
agent that can learn will export selectively exactly when observable state carries
information about future relevance; the falsifying reading "random export does as well
as learned export" holds exactly when the generator provides none. The quantity that
determines the result, I(observable features at export time; future relevance), is
fixed by whoever designs the task. The real experiment was not built on an engine (no
NPE substrate), and the DSA was not applied to any frozen specimen (PTE, AGE, Z80). The
replay hook was demonstrated only in the toy. Those remain.

## 5. CONSEQUENCES

- False or weak premise: the reversible-core experiment is not a strong attack on the
  "reversible" and "indiscriminate loss" countermodels unless the preregistration (i)
  measures and reports I(features; relevance) per task before the run, (ii) treats a
  "random = learned" result at I=0 as uninformative (decided by the generator, not the
  agent), and (iii) says what it would mean for the law if a learner is selective whenever
  I>0 (which is close to a theorem about learners). Whoever owns the selective-
  irreversibility hypothesis and falsifier table, and the engine seat named to build the
  reversible core, should know.
- Positive result for the stewards' design rules: rate matching is automatic on a
  reversible substrate and random export is NOT curve-matched; the random control issues a
  false selectivity certificate when relevance tracks recency (+.059), while a
  curve-matched blind control (same policy fed a shuffled cue) catches it. The FIFO third
  arm only helps where recency-relevance decorrelation is measured. Recommend the
  shuffled-cue, curve-matched control as the primary blind arm, with random reported too.
- Instrument caution: a planted positive control can be silent when the task has a
  second relevant axis (recency). Positive controls must be validated per task.
- Reproduction of a predicted defect: the sequential-RNG cheat fixture behaves exactly as
  the M2 attack predicted (up to 67% false non-merging). Engines whose RNG streams consume
  state-dependent draw counts must be keyed before any DSA reading.
- DSA on reversible substrates must read export (distinction leaves accessible state), not
  exact merge; the relevance oracle must come from the same generator path as the
  specimen; inert vs dynamics-relevant perturbations give different strata.
- Harness lesson from my own run: feature scaling in the learner (age/N) silently hid a
  whole policy class; a "learned" arm needs a check that it can rediscover known
  baselines (FIFO) before its non-difference is read.

## 6. COST

About 1.5 hours of my time. CPU about 40 minutes total (experiment v1 12 min, v2 20 min,
DSA two runs about 4 min, one accidental duplicate start about 2 min that I killed before
it wrote output, small checks). At most 2 processes of mine at a time, under 150 MB RAM,
CPU only. Not done: an engine-hosted reversible core (NPE), DSA adapters on frozen PTE /
AGE / Z80 specimens, a code audit of each engine's RNG and state for a common replay hook,
a closed-form bound linking advantage to I(tag; rel), and replication over K, p, N and
learner seeds.



======== REPORT X004 ========

REPORT -- persistence vs equal-information context; portable executable organs

1. WHAT I SET OUT TO TEST

The proposal under test says a persistent, growing library of executable procedures (the Voyager-style skill library) is a distinct scientific object, not just a way of managing context. The cheapest test that could kill it is this: with the same information and the same compute, does keeping acquired procedures as a persistent executable library beat keeping the same experience as raw context (episodes or demonstrations)? A related proposal asks whether acquired machinery can be packaged as "organs" (identity + description + executable payload + retrieval key). Such organs would have to stay useful when the payload is ablated, and when they are moved to another agent or another world. I built the smallest deterministic world without a language model that the proposal itself specifies. I ran the matched-information comparison, a closed-loop version with a late library swap, and the payload and transplant ablations this world can express.

2. WHAT I DID

Sources read (read-only clone):
- The ladder and experiment records in roles/Atlas/proposals/2026-09-21_prior_art_raid/{ENGINE_FIVE_EXPERIMENT_LADDER.md, EXPERIMENTS.jsonl} @ 2c7a19adb.
- The portable-organ section of roles/Chiron/prompts/2026-09-21_synthesis_directive/SYNTHESIS_DIRECTIVE.md @ 9e54a51ce.

No repository code was run, and I found no existing implementation in the repo. The nearest engine branch (origin/[redacted]/compounding-2026-09-27) has no library-vs-context test.

All code is new, in [redacted]
- f50.py: world, controllers, memories (sha256 70a424ac281a...)
- phase1.py: matched-information test (1e6b70b91739...)
- phase2.py: closed loop plus swap and transplant tests (e13820901a64...)
- phase2bx.py: closed loop, context-only arm (e46d4708004e...)
- calib.py: budget calibration
- Outputs: phase1_*.json, phase2_*.json, phase2bx_*.json, p*.log, agg1.py

The world is generated synthetically by this code. No committed data and no holdout were used.

World:
- Tasks transform lists of integers using 14 primitives (rev, sort, inc, dbl, dedup, tail, cums, ...).
- Each world seed draws 10 hidden "motifs". A motif is a 3-primitive sub-procedure that cannot be reduced to 2 primitives.
- A task is a hidden program of 2-3 motifs, plus one extra "glue" primitive with probability 0.5. It is given as 5 I/O examples, and a solution must also pass 5 held-out examples.
- Four world seeds (1-4).

Controller: breadth-first enumeration over a set of tokens (the primitives plus whatever the memory supplies). Candidates that produce identical outputs are pruned. Every arm gets the same hard budget of 20000 primitive applications per task.

Memory arms, all capped at K primitive-tokens (the equal-byte budget):

| Arm | What it holds and how the controller uses it |
|---|---|
| A | nothing (primitives only) |
| B_edit | raw past solution programs, adapted by up to 2 edits ("demonstration adapted in context") |
| B_macro | raw past solution programs, callable whole as tokens ("retrieved demonstrations / whole-fossil reuse") |
| BX | the same raw context as B, but the controller extracts a fragment library from it before searching; nothing persists beyond the raw context |
| D | persistent library: fragments extracted from all history by a greedy compressor that keeps the most token-saving repeated fragments, capped at K tokens |
| D_shuffled | same fragment lengths, random payload |
| D_foreign | library extracted from a different world's history |

Phase 1 (information matched):
- All arms are built from the same 100 ground-truth training programs.
- 40 held-out tasks per seed per condition.
- Recurrence 0 or 0.5 (the fraction of test tasks that repeat a training program on new inputs).
- K in {30, 100, 300, all (~650-700)}.

Phase 2 (closed loop, not information matched):
- Each arm learns only from its own solutions, over 50 one-motif, then 50 two-motif, then 60 three-motif tasks (K=100; BX also at K=300).
- The final memories are then tested on 40 fresh three-motif probe tasks.
- For D, the library is also swapped to empty, shuffled, another lineage in the same world (different task stream), and a lineage from a foreign world.

Commands: `python3 phase1.py 1 2` and `python3 phase1.py 3 4`, run in parallel; the same for phase2.py and phase2bx.py. At most 2 processes at a time.

3. RESULT

Phase 1, recurrence 0 (tasks solved out of 160, summed over 4 worlds; mean primitive applications per task in brackets):

| K | B_edit | B_macro | BX | D | D_shuffled | D_foreign |
|---|---|---|---|---|---|---|
| 30 | 11 | 20 | 31 | 125 (10.0k) | 9 | 17 |
| 100 | 17 | 25 | 67 | 123 | 9 | 17 |
| 300 | 20 | 37 | 131 | 123 | 9 | 17 |
| all | 27 | 31 | 123 | 123 | 9 | 17 |

- A (no memory) solved 20 (18.3k).
- At K=all, BX and D are identical by construction, a sanity check that passed.
- In 3 of 4 worlds, D at K=30 recovered exactly the 10 hidden motifs.

Phase 1, recurrence 0.5, K=all:
- B_macro solved 71/71 repeated tasks against 55/71 for D; overall 92/160 against 127/160.
- Replaying whole episodes wins on exact repeats; the library wins on new combinations.

Phase 2, closed loop (solved per block, summed over 4 worlds; out of 200 / 200 / 240):

| Arm | one-motif | two-motif | three-motif |
|---|---|---|---|
| A none | 196 | 35 | 11 |
| B_edit | 11 | 4 | 1 |
| B_macro | 176 | 50 | 13 |
| BX, raw context K=100 | 184 | 101 | 29 |
| BX, raw context K=300 | 182 | 145 | 91 |
| D persistent, K=100 | 182 | 145 | 101 |

B_edit cannot start from empty memory: two edits from nothing only reach 2-primitive programs.

Probe on fresh three-motif tasks (out of 160):
- D with its own library: 50.
- D with the library swapped: empty 2; shuffled payload 6; other lineage in the same world 28; foreign-world lineage 1.
- Raw-context arms: B_macro 10, B_edit 0, BX K=100 18, BX K=300 46.

Plain conclusion. A persistent executable library beats naive use of the same information in context by a wide margin (125 vs 20-31 at K=30). Almost all of that advantage goes away once two things hold: the controller may extract a library from its own context (BX), and the budget holds about 30 past solutions (K=300). BX then ties or beats D: 131 vs 123 in phase 1, 418 vs 428 in the loop.

What is left of "persistence" breaks into two parts:
- (a) Compression under a byte budget. The library holds distilled information from all of history in K tokens, which raw context cannot do.
- (b) Amortised derivation. Extraction took 0.4-36 ms per task, against about 90 ms of search. That is a modest wall-clock cache, and it does not show in primitive-application units.

Neither part needs persistence as such. Under the ladder's own kill criterion (no advantage at matched information and compute), the rung kills whenever the context arm is allowed to extract. It survives only when the context arm cannot abstract or the byte budget is tight.

Organ findings:
- The payload is everything. A shuffled payload does worse than no memory in phase 1 (9 vs 20), and in the loop swap it is about as useless as an empty library (6 vs 2).
- The swap test collapses competence (50 to 2), so progress in the loop really did depend on the retained structure.
- Moving a library to another agent in the same world works partially (28 vs 50 for the agent's own library).
- Moving it across worlds with different regularities gives nothing (phase 1: 17 vs 20 for no memory; loop: 1/160).
- Description and retrieval-key ablations cannot be expressed here: there is no natural language, and the whole library is always inside the search.

4. DID IT RESOLVE THE QUESTION

Partly.

For a search-based controller without a language model the answer is clear: persistence adds nothing beyond "equal-information context plus an extraction step", apart from compression per byte and caching. Against naive use of context it wins big. The question as posed is therefore partly ill-posed: whether context wins depends mostly on how well the context-using controller can abstract and on the byte budget, not on persistence.

What is still open:
- The language-model case. There, "equal-information context" means a model that may abstract implicitly. That needs a language-model arm, which was out of scope (CPU only, no API).
- Generality. The world deliberately favours libraries: it has discrete, exactly reusable motifs, which is the assumption cost the ladder names itself. The run covers 4 seeds, one compute budget and one world family, where the ladder's promotion gate asks for 2 or more.

5. CONSEQUENCES

- The kill rung is badly posed; Atlas (ladder owner) should know. It should be restated as a per-byte and per-compute comparison that includes an explicit "same raw context + on-the-fly extraction" arm. Without that arm, any library beats a controller that cannot decompose its context, so the rung cannot kill. With it, persistence reduces to compression plus caching. That points to the ladder's memory-forms-per-byte experiment as the informative test. It also supports the ladder's own fallback of making the library a memory component inside an existing engine. Whoever next designs the fifth engine should know too.
- New positive result (small, expected): in a closed loop the retained library carries the competence. The swap collapses it (50 to 2), and a shuffled payload does no better than an empty library. Organs transfer partially between agents in the same world and not at all across worlds. This gives Nyx and Techne a cheap working harness for swap and transplant tests.
- Harness warning: a controller that adapts demonstrations by edits cannot start from empty memory. Using it as the context arm in a closed loop is unfair by construction.
- Design hint: replaying whole solutions beats a fragment library on exact repeats, so libraries should keep whole solutions as well as fragments when tasks recur.
- No defect was found in the program's own code, since none of it was run.

6. COST

- About 1.5 hours of my own time.
- About 39 CPU-minutes: phase 1 ~25, phase 2 ~10.5, context-only loop arm ~2.7, calibration ~1.
- At most 2 processes, under 200 MB RAM.
- Not done: a language-model context arm; a second world family; retrieval-key and description ablations; a test of composition depth on withheld composite tasks; learning curves across budgets; confidence intervals beyond 4 seeds.

