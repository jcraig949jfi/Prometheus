# INV_H -- What predicts that a Pass-1 mechanism gets a world? (2026-09-30)

Analyst for Hecate. Read-only over hecate/programs/HT-*/program.json (16 programs)
and the two generator prompts. No git, network or model calls. Scripts lived in
the session scratchpad (invH/wsf.py, an.py, an2.py, an3.py); feature definitions
are restated below so the numbers can be rebuilt.

## 0. Population and outcomes (reproduces the verified fact)

    $ python wsf.py rows.json
    243 mechanisms; 117 spec_any; 109 spec_v1; 20 spec_v2; 58 tested(outcome!=None)

- spec      = mechanism id appears in any experiments[].mechanism_ids (P3 or P3v2)
- spec_v1   = appears in a P3 world (pass0_3_v1.md: same generator session wrote P1, P2, P3)
- spec_v2   = appears in a P3v2 world (pass3_v2.md: a later generator that read outcomes)
- tested    = appears in a world whose "outcome" is not null (58; matches)
- Mechanism list order is clean: position index == M-number - 1 for all 243.
- Field "layer" is EXCLUDED: 41 mechanisms read "implemented_candidate", all of
  them specified -- it was rewritten after P3 (outcome leakage).

What the P3 v1 prompt asked the generator to select on (pass0_3_v1.md l.107):
"3-5 worlds for the mechanisms you judge most experimentally tractable".
The same prompt (l.97-98) asked P1 to "Include strange ones. Include some whose
three-way dependency is weak and say so in knockouts". So tractability-filtering
was instructed, not emergent; the question is whether it correlates with strangeness.

## 1. Features (all from the generator's own P1/P2 text)

    relpos        position in M-list, 0 (M1) .. 1 (last), within program
    weak_s        # of 3 knockouts containing the word "weak" (strict)
    weak_b        # of knockouts matching a broader weak lexicon (weak|little|no change|
                  equally well|does as well|only relabel|cosmetic|incidental|generic|...)
                  ("nothing" alone NOT counted: "nothing to measure" is a STRONG knockout)
    dobs_words    word count of questions.distinguishing_observable; dobs_digits = has a digit
    stmt_words    word count of statement; stmt_digits
    sa_words      word count of simpler_alternative; sa_named = capitalised term or a
                  stock-method keyword in it (crude "names a known mechanism")
    lens_targets  # of P2 lenses whose targets[] include the mechanism
    n_derived     # of P0 interpretations in derived_from
    form          14-level P1 "form"

Primary test: within-program permutation (labels shuffled inside each program,
preserving per-program counts), statistic = difference in program-demeaned
feature means, B=5000, two-sided, floor p=0.0002. Secondary: logistic regression
with 16 program dummies (Newton; standardized covariates; Wald z). With ~15
rows per program the FE logit has incidental-parameter bias; trust the permutations.

## 2. Results, outcome = spec (117/243)

    $ python an.py spec
    feature       spec1   spec0   within-diff   perm p
    relpos        0.397   0.596     -0.199      0.0002
    weak_s        0.333   0.365     -0.008      1.0000
    weak_b        0.385   0.389     +0.019      0.7914
    dobs_words   13.205  11.675     +1.560      0.0002
    dobs_digits   0.137   0.095     +0.033      0.4169
    stmt_words   38.265  36.754     +2.051      0.0102
    stmt_digits   0.162   0.119     +0.026      0.5411
    sa_words     10.906   8.992     +1.984      0.0002
    sa_named      0.607   0.468     +0.053      0.2440
    lens_targets  1.530   0.730     +0.783      0.0002
    n_derived     1.359   1.516     -0.155      0.0204
    form heterogeneity (between-form variance of rates)   perm p=0.6641

Multiple comparisons: 11 features + form = 12 tests on this outcome; Bonferroni
0.05/12 = 0.0042. Survivors: relpos, dobs_words, sa_words, lens_targets.
stmt_words and n_derived do not survive. Form does not predict specification
(consistent with ATTACK_D's p~0.18 for admission-by-form).

Position (primacy), rate of spec by M-number (n=16 each for M1-M14):

    M1 .88  M2 .75  M3 .88  M4 .56  M5 .50  M6 .31  M7 .38  M8 .44
    M9 .44  M10 .50 M11 .31 M12 .44 M13 .19 M14 .44 M15 .31(n13) M16 .20(n5) M17 0(n1)
    first third .70 | middle third .42 | last third .33

It is mostly a STEP, not a slope: M1-M3 40/48 = 0.83; M4+ 77/195 = 0.39, and
within M4+ the residual trend is weak (r = -0.13, p = 0.073). With an M1-M3
indicator in the FE logit, relpos drops out (early3 z=+2.76, relpos z=-0.64).
World order also follows list order: Spearman(world index W1.., lowest
mechanism number in it) = +0.37, p=0.0024, n=64; W1 contains M1 in 9/16 programs.

FE logits (z values):

    main          relpos -2.72  weak_s +1.15  dobs_words +0.80  dobs_digits -0.28  sa_named +0.06  lens_targets +6.08
    no lens       relpos -3.89  weak_s +0.26  dobs_words +1.68  dobs_digits +0.63  sa_named +0.49
    text lengths  relpos -2.36  dobs_words +1.63  sa_words +1.69  stmt_words +0.85  n_derived -0.99
    step model    early3 +2.76  relpos -0.64  dobs_words +1.25  sa_words +2.03

Collinearity: length shrinks down the list (within-program Spearman with relpos:
dobs_words -0.42, sa_words -0.47, stmt_words -0.28, all p<1e-4; n_derived +0.30).
The univariate length effects are therefore largely position effects; once
position is in, only sa_words keeps marginal support (z~2, not multiplicity-safe).

Lens targeting is NOT an independent predictor: 64/64 P3 v1 worlds list a lens
whose targets[] include one of the world's own mechanisms. P2 and P3 were written
in the same session; lens targeting and world choice are one plan, not cause and
effect. Untargeted mechanisms: 49, specified 2 (0.04).

Other outcomes (same table, abbreviated): spec_v1 (109) -- same survivors
(relpos, dobs_words, sa_words, lens_targets; weak_s within-diff +0.034 p=0.57).
tested (58) -- relpos p=0.0018 and lens_targets p=0.0002 survive; nothing else.

## 3. The selection question: are the never-specified mechanisms the stranger ones?

On every in-record strangeness/familiarity marker available, NO detectable filter:

    marker (generator's own words)                      spec rate with / without
    any knockout flagged "weak" (strict)                 0.481 (n=81) / 0.481 (n=162)
                                                         diff +0.000, 95% CI [-0.133, +0.133]
    any knockout weak (broad lexicon)                    0.506 (n=89) / 0.468
    distinguishing_observable has a number               0.137 vs 0.095 share; p=0.42
    simpler_alternative self-flags familiarity           5/10 = 0.50 / 0.48
      ("disguise|familiar|is just|reduces to|equivalent...")
    P1/P3 'unexplained' notes naming an M as            4/9 = 0.44
      "familiar ... in disguise"
    Jaccard(statement, simpler_alternative)              0.042 vs 0.047, MWU p=0.24
    form                                                 perm p=0.66

So on the generator's text: weak-three-way-dependency mechanisms, numberless
observables and self-declared-familiar mechanisms were specified at the base
rate. The weak flag is also flat across position (first/middle/last third
any-weak 0.32/0.32/0.35; Spearman with relpos +0.06, p=0.39), so primacy does
not proxy for it either.

One exploratory exception (found after looking, one of many possible cuts; do
not count it): the P3v2 generator, told to "prefer the world that could most
cleanly fail", newly specified 8 mechanisms and none had a weak knockout, from
a never-specified pool of 67 in its 8 programs of which 22 were weak;
hypergeometric P(0 of 8) = 0.033. Uncorrected and post hoc; it reads as
"attainability pressure avoids weak-dependency claims", worth a preregistered
check on the next v2 round, not a finding.

## 4. Adversarial loop on the main conclusion

Main conclusion C: "World specification is driven by list position (M1-M3)
and by co-planned lens targeting, not by how strange the mechanism is; the
126 never-specified mechanisms are not systematically stranger."

A1. Shared assumption -- the generator's text is a valid strangeness proxy.
    It is not, for the marker that carries most weight. "Weak three-way
    dependency" is a claim about whether all three concepts are needed, not
    about whether the mechanism is unfamiliar. A weak-dependency mechanism is
    often a FAMILIAR one with a decorative concept ("FEP only relabels the two
    states", "any moving average does as well"). The prompt asked for "strange
    ones" and "weak ones" as two separate requests; no field records which
    mechanisms were the "strange ones". The familiarity self-flags (n=10, n=9)
    are too small to rule anything out. The autopsy already records that no
    novelty detector was ever run on these 243 mechanisms and that the detector
    that exists cannot reach UNFAMILIAR. Verdict: C's second half is
    DOWNGRADED from "not stranger" to "no evidence of a strangeness filter on
    in-record proxies; strangeness itself is unmeasured".

A2. Position may itself BE the familiarity filter. If generators write the
    intuitive mechanisms first and the requested "strange ones" last, primacy
    and familiarity-filtering are the same event. Evidence against: none of the
    in-record markers trends with position (weak flag flat; sa_named rho -0.09
    p=0.15; self-flagged-familiar mechanisms sit at relpos 0.0..1.0, spread).
    Evidence for: text gets shorter down the list (dobs/sa/stmt word counts),
    consistent with less-developed -- possibly stranger -- ideas, or with
    fatigue. Cannot be adjudicated without an external familiarity rating of
    all 243 (blind to position and outcome). Verdict: OPEN; this is the residual
    risk in C.

A3. Primacy vs intent. Same session wrote P1 and P3, so "M1-M3 got worlds" may
    be the generator listing the mechanisms it already meant to build first,
    not an order bias in choosing. The data cannot separate these; both mean
    selection happened at enumeration time. Verdict: C should say "early-listed",
    not "primacy bias".

A4. Lens targeting is leakage, not a predictor (64/64 co-planned). Verdict:
    drop it from any causal reading; position survives without it (z=-3.89).

A5. Post-hoc record edits. "layer" was rewritten for all 41 implemented
    mechanisms; knockouts/observables could also have been edited after P3
    (e.g. sharpened for tested mechanisms), which would inflate the length
    effects. Not checked (no git in this task). Verdict: length effects
    unverified; position is immune (ids are not renumbered: pos == num-1).

A6. Statistics. 12 tests per outcome x 3 outcomes plus tables; only effects at
    the permutation floor are claimed. FE logit has ~15 rows per stratum. The
    null on the weak flag has a 95% CI of +/-13 points, so a small filter
    (<13 pp) on that proxy is not excluded.

Surviving conclusion C': Which mechanisms get worlds is explained mainly by
being listed early (M1-M3 specified 83% vs 39% for M4+) and by being in the
same plan as the P2 lenses. On the generator's own markers (weak dependency,
numbers in the observable, self-declared familiarity, form) the never-specified
126 are indistinguishable from the specified 117. Whether they are stranger in
fact is unmeasured: the only in-record "strangeness" marker is a dependency
claim, and position -- the dominant predictor -- could still encode intuitive-
first ordering.

## 5. What would settle it

- Blind external familiarity rating (statement + simpler_alternative only, ids
  and position stripped) of all 243, then test rating ~ spec within program and
  rating ~ relpos. If rating rises with position, A2 is confirmed and primacy
  IS the familiarity filter.
- Next generator round: shuffle mechanism order before P3 (or run P3 in a fresh
  session on a randomized list). If the M1-M3 advantage vanishes, it was order.
- Have P1 record an explicit "strange: yes/no" tag, since the prompt asks for
  strange ones but nothing records which they are.
- Preregister the P3v2 weak-avoidance check (section 3) before the next v2 round.
