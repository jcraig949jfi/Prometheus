# Prometheus Phase 3 -- falsifiers

Architect: FABLE-5.1 (seat Dionysus). What evidence would make me revise or
reject each major part of the design. Terms are defined in REQUIREMENTS.md
section 1; hypotheses H1 to H7 in RSE_ARCHITECTURE.md section 8.

Each entry says what would be observed, what it would mean, and what would
be done. Thresholds are defaults. A campaign fixes its own in its
preregistration, before data, and may not move them afterwards.

Three kinds of outcome are kept apart throughout:

- a hypothesis fails and the design stands (most of these);
- a part of the design fails and is replaced;
- the Phase 3 thesis fails and the program is rescoped or stopped.

----------------------------------------------------------------------

## 1. Falsifiers of the thesis

These answer the prompt's Q10: what result after 6 to 12 months would
convince me the thesis is wrong or badly framed.

**F-T1. Conventional learners do everything, and nothing else adds a
mechanism.**
- Observation: at month 12, for every relocation certified in any other
  substrate, the reference arm reaches the same or a higher certified level
  at equal or lower cost; and no certified mechanism (C3) in any substrate
  lies outside the reference class by the preregistered signature distance.
- Meaning: at this scale, alternative substrates buy nothing that
  conventional machinery does not already give. The premise that small-scale
  search over unlike substrates can expose unfamiliar reasoning machinery is
  unsupported.
- Action: reduce Phase 3 to the instrument program (certified worlds,
  qualification harness, the transition map for conventional learners), or
  stop.

**F-T2. Small does not predict large.**
- Observation: the construct-validity test fails. The preregistered rank
  correlation between certified profile and performance on the richer
  transfer set is below 0.5, with at least 20 organisms spanning the
  profile range.
- Meaning: assumption A1 is wrong, or the worlds certify something
  irrelevant.
- Action: stop adding substrates. Redesign the world families once, with
  the transfer set as the target. If the second design also fails, the
  small-world method is the wrong tool and the thesis must be reframed
  around larger worlds without certificates, which this design does not
  know how to make rigorous.

**F-T3. The relocations do not separate.**
- Observation: across at least 30 organisms from at least two substrates,
  certified levels on the six axes are almost perfectly rank-correlated
  (every pairwise correlation above 0.9), and no knockout moves one axis
  without the others.
- Meaning: the six-way decomposition does not describe these systems. There
  is one capability dimension at this scale.
- Action: collapse to a single certified depth, drop the knockout matrix,
  and treat "relocation" as a description, not a measurement.

**F-T4. Nothing regenerates.**
- Observation: at month 12, no capability at BUILD or above has been
  regenerated below scaffold level S4 in any substrate, in cells where
  search power for targets of the plant's size was at least 0.8.
- Meaning: at this scale, search under pressure does not rebuild even
  mostly-specified constructive machinery. Emergence of construction is out
  of reach here.
- Action: move the weight of the program from search to design: build and
  analyse designed constructive systems across substrates, and keep search
  as a calibrated side arm.

**F-T5. The gap is not where I said it is.**
- Observation: H1 fails (see F-H1) and the online-gradient reference learner
  passes BUILD, COMPRESS and COMPOSE at levels no other substrate exceeds.
- Meaning: within-lifetime construction is not a gap for conventional
  machinery once it is allowed to update weights. The target was badly
  chosen.
- Action: the apparatus stands. The question changes to what limits
  conventional online learners on RECURSE, which is where they would then
  be tested.

----------------------------------------------------------------------

## 2. Falsifiers of the hypotheses

**F-H1. Within-lifetime gap.**
- Prediction: in RETAIN, learners with only fast state score at the
  no-carry bound on probe trials once lifetime information exceeds their
  fast capacity.
- Falsified if: a fixed-window or recurrent reference learner scores above
  that bound with a 95% lower confidence limit clear of it, in sealed
  worlds, after the reset-equivalence test has passed.
- First suspicion on such a result: a leak or a failed reset. The result
  stands only after an attack round finds neither.
- Also informative: if the online-gradient learner fails, the RETAIN family
  is mis-specified, not the hypothesis.

> Annotation, 2026-10-01. F-H1 as written cannot be failed except by a leak:
> under the harness's state partition the prediction is a theorem. I found
> this while writing ENGINE_PORTFOLIO.md (its section 2) and recorded the
> correction in RSE_ARCHITECTURE.md section 13.5. F-H1 is now read as two.
>
> F-H1a (conformance, not a hypothesis): a fast-state-only learner above
> the no-carry bound in RETAIN means the harness is broken.
>
> F-H1b (the empirical claim). Prediction: a learner trained offline that
> carries only activations or a token window certifies COMPRESS within a
> lifetime only for kinds of structure present in its training
> distribution, and falls to the lookup bound on RECOMBINE families with
> withheld kinds of structure; a weight-updating learner passes on those
> families at a sample cost at least ten times the designed constructive
> organism's. Falsified if: a fast-state learner is certified above the
> lookup bound on withheld-structure families in sealed worlds, with a 95%
> lower limit clear of the bound, after an attack round on the withholding;
> or the weight-updating learner passes at a cost within a factor of two of
> the designed organism. Either outcome feeds F-T5, whose "H1 fails" now
> means H1b.

**F-H2. Payoff.**
- Prediction: in each dial, the boundary where the relocation appears lies
  where computed net payoff changes sign, within the instrument's stated
  resolution.
- Falsified if: in at least two of three substrates, relocations appear at
  better than chance rates where computed payoff is negative by more than
  the resolution; or fail to appear, at search power of at least 0.8, where
  it is positive by more than twice the resolution.
- Meaning if falsified: something other than payoff decides. The cells
  where it failed are the first real leads the program has had.

**F-H3. Reach.**
- Prediction: observed transition probability equals the payoff indicator
  times the measured recovery rate for a planted target of the same needle
  size, with no fitted parameter; and a curriculum that rewards
  intermediate stages raises it by the amount the shortened needle predicts.
- Falsified if: the product misses the observed probability by more than
  the binomial interval in more than a quarter of cells; or curriculum has
  no effect where the needle is shortened by half or more.

**F-H4. Addressing.**
- Prediction: in WM, replacing tag addressing by absolute addressing, or
  removing call and return, abolishes COMPOSE at S2 and S3 and leaves BUILD
  intact.
- Falsified if: COMPOSE is certified at S2 or S3 with either switch off, in
  at least 3 of 5 independent lineages.
- Meaning if falsified: built structure can be reused at depth without
  designed addressing or invocation. That would be worth more than the
  hypothesis.

**F-H5. Opposite weaknesses.**
- Prediction: WM is deeper in expressibility and shallower in reach than
  PN, with the crossing at COMPOSE.
- Falsified if: PN reaches COMPOSE at S2, or WM reaches T1 to T4 at S2 with
  reach equal to PN's at matched budget.
- Meaning if falsified: one of the two substrates is simply better, and the
  search for a hybrid is unnecessary.

**F-H6. Compounding.**
- Prediction: for the designed adaptive learner in CHAIN and FAMILIES, the
  savings ratio rises with stage; for the fixed-procedure learner it is
  flat.
- Falsified at the level of the world if: the designed adaptive learner
  shows no rise. Then the families do not afford compounding and are
  redesigned.
- Not falsified by: no found organism exceeding the fixed-procedure learner.
  That is a null, and it is reported with its search power.

**F-H7. Prior restriction.**
- Prediction: at equal certified level, mechanisms found by model-guided
  generation have lower signature dispersion than those found by blind
  variation, and some blind finds lie outside the model-guided set.
- Falsified if: dispersion is equal within the preregistered margin and no
  blind find lies outside, with at least 20 certified finds per arm.
- Meaning if falsified: no restriction by the model's prior is detectable
  at this scale. Model-guided generation is then simply the faster route,
  and the blind share (ANTI-04) can be reduced.

----------------------------------------------------------------------

## 3. Falsifiers of design components

**F-D1. The kernel cannot be qualified.**
- Observation: by day 45 the P1 calibration set (builder, holder, smuggler,
  constant, lookup) is not sorted with at least 95% accuracy at a 95% lower
  confidence limit, or a fire test cannot be made to fail.
- Action: stop all other work. Simplify the kernel until P1 passes. If it
  cannot pass in a second 45 days, class exclusion for BUILD is not
  practical and the design's central instrument is wrong.

**F-D2. Bounds are wrong in code.**
- Observation: the shortcut audit finds a cheap policy beating a claimed
  bound, or the two solver implementations disagree.
- Action: the world is not admitted. This is the audit working. It becomes
  a falsifier of the method only if more than a third of authored families
  fail admission after two revisions.

**F-D3. Stores leak.**
- Observation: the smuggler impostor passes the BUILD ruler, or the
  reset-equivalence test fails on a substrate.
- Action: no BUILD claim in that substrate until the harness closes the
  channel.

**F-D4. Independent implementation is not obtainable.**
- Observation: a second implementation from another model family cannot be
  obtained within a tenth of the first implementation's token cost, or
  differential tests keep disagreeing after three rounds.
- Action: cap claims at C2 and say so in every report. Do not relabel a
  same-family review as independent.

**F-D5. Search power cannot be measured.**
- Observation: recovery rates for planted targets are at floor or ceiling
  for every distance tried, so no curve exists.
- Action: no certified null in that substrate. Report "reach unmeasured".

**F-D6. The reference arm was a straw man.**
- Observation: an attack round with a tuning budget equal to the compared
  substrate's search budget raises the reference arm's certified level by
  one staircase step or more.
- Action: every comparison that used the old reference arm is marked STALE
  and re-run.

**F-D7. The state partition is too coarse.**
- Observation: on a designed organism with a known multi-part circuit, the
  interchange ruler cannot localise the carrier better than the whole
  store.
- Action: mechanism claims (C3) are closed for that substrate.

**F-D8. The overhead is too high.**
- Observation: at day 90, qualification, independent implementation and
  fixtures have taken more than 60% of all tokens and the frontier table
  has fewer than six certified cells.
- Action: cut the open arms and P8 and P9; keep one substrate and the
  reference arm; re-plan.

**F-D9. The staircase is not valid.**
- Observation: psychometric curves are non-monotone for more than a quarter
  of organisms.
- Action: report full curves; drop thresholds as the summary.

**F-D10. Throughput is far below the estimate.**
- Observation: the first real WM kernel runs below 10 million organism
  instructions per second on M1 (the design assumes at least 100 million).
- Action: rewrite the hot loop before any campaign; if it stays below,
  shrink lifetimes and say which map cells are no longer affordable.

----------------------------------------------------------------------

## 4. What would not falsify anything

Stated so that these are not later presented as evidence either way.

- A run in which nothing interesting was seen, without the four
  certificates. That is an apparatus null.
- A mechanism no model can describe. That raises priority after C2 and is
  never evidence (ANTI-03).
- Agreement between two runs of the same code on the same seeds.
- A positive at C0 or C1, however striking.
- My own, or any model's, judgement that a result looks right.
