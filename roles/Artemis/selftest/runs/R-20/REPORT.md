REPORT -- Blind batteries and co-adapted generators (Apollo reasoning organism)

1. WHAT I SET OUT TO TEST
Apollo's best organism scores 0.60 (mix-adjusted) on its owner's home battery but 0.0667 on 42
tasks another seat wrote blind. Two questions follow. (a) Is that collapse a property of the
organism, or a quirk of one particular blind author -- i.e. does it replicate when a third,
independent author writes the tasks? (b) The revival review proposes validating any new task
generator by checking that it "reproduces the known blind result" before trusting it. Is that a
workable gate: does it reject co-adapted generators, and does it also reject generators that are
simply broken? I could only test this on Apollo; the other engines named as lenses (NPE Z80
worlds, Aether, Cosmos, BEE z80atlas) have no committed blind-authored battery that I found, so
"do current capability numbers survive" is answered here for Apollo only.

2. WHAT I DID
Code/data exported from the read-only clone at origin/main 6ff2b2f8a (git archive of apollo/src,
apollo/data, apollo/scripts, apollo/cycles/campaign_20260825, roles/Charon/apollo_e9,
agents/hephaestus/src) into work/R-20/src; run with GIT_* unset.
 - Reproduction: python3 apollo/scripts/e9_score.py -> raw 0.0476, mix 0.0667, home 0.6000,
   40 abstain / 2 correct / 0 guess. REPRODUCED exactly.
 - Wrote work/R-20/gen_blind.py: a third-author procedural generator, 7 categories, 3
   structurally different construction routes per category, 4 candidates, gold computed by
   construction. Written and hash-frozen (gen_blind.FROZEN.sha256) BEFORE reading any Apollo
   operator source, the home generator, the home prompts or the blind author's prompts. Known to
   me: category names, schema, and the two example prompts quoted in the revival review. One
   post-freeze edit: a distractor-collision bug fix (assertion crash), made before reading any
   organism code, re-hashed and logged.
 - work/R-20/calib.py: scores the recorded 0.833 organism (KNOWN_0833, same eval path as
   e9_score.py, home-category-mix weighting, E9 tolerance +/-0.15) on 30 batteries of 42 tasks
   (6/category) from each of six generators:
     home_reseed        the home generator (gen_clean_canary_v01.py) with fresh seeds
     home_reworded      home construction + synonym swaps (larger->bigger/greater, etc.)
     home_prefixed      home construction + the lead-in "Question: " on every prompt
     blind_third_author my gen_blind.py
     degenerate_shuffled  INVALID: my prompts with words shuffled (gold unrecoverable)
     invalid_wrong_gold   INVALID: home construction with gold replaced by a wrong candidate
   plus one 420-task battery from gen_blind. Output: calib_out.json.
 - work/R-20/leak.py: 100 batteries each at co-adapted fractions f = 0..1 (a task slot is a
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
with measured leak tolerance. Not resolved: whether numbers from NPE, Aether, Cosmos or BEE survive
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
   the generator by reproducing a known blind result" (NPE, Aether world generators; Cosmos's
   replacement for spent sealed universes) needs at least: (1) an independent gold verifier for
   every generated task, (2) a positive anchor -- a solver or organism that should score HIGH on
   the generator and does, and (3) a profile check (abstain/guess shape, per-category), since a
   single mix number within +/-0.15 cannot detect up to ~20-30% co-adapted content at n=42.
   Anchor target results should ideally be mid-range, not at the floor.
 - Who should know: Apollo (revival plan step "X-heldout generator calibrated against the blind
   battery"), Aporia (counterfeit/X-heldout doctrine), Lexis, and any seat building world/task
   generators (NPE, Aether, Cosmos).

6. COST
About 1.25 hours of my time. CPU: under 10 CPU-seconds total (all scoring is deterministic
regex/pipeline code); peak RSS ~50 MB; single process. Not done: state injection; blind batteries
for other engines; a positive-anchor solver for my generator (its validity rests on
construction-time gold, spot-checked by hand on 14 tasks, not on an independent solver).
