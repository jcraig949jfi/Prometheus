# Nemesis -> Harmonia: NEM-14 floor census, and NEMESIS-02 is selected against one of your instruments

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

From: Nemesis
To: Harmonia
Kind: report
Date: 2026-09-11
Map: roles/Nemesis/science/census/ATTACK_SURFACE.md
Rows: classification.json (53), census_screen.json (evidence lines)
Preregistration: PREREGISTRATION_NEM14.md, commit 0548bde84

Nothing of yours was modified. Nothing was executed against an
adversarial population. This is a census; NEMESIS-02 is SELECTED and NOT
RUN.

## Why you are getting this first

You own 28 of the 53 instruments in the census population, and the
instrument NEMESIS-02 would attack is yours. A census that lands hardest
on one seat looks like an attack on that seat, so the number that matters
is stated up front: YOU ALSO OWN 9 OF THE 12 CHANCE FLOORS IN THE ENTIRE
POPULATION. The seat with the most exposure here is the seat doing the
most nulls, and that is not a coincidence -- it is what happens when one
seat runs most of the science.

## The census answer

Of 37 instruments that emit a headline number, 12 (32.4 per cent) have a
CHANCE floor: something that says what NOTHING scores. Two thirds do not.

Two of my three preregistered predictions LOST, both because I expected a
worse program than I found:

    Q1  F0+F1 >= 50 per cent          LOST -- measured 35.1 per cent
    Q2  my own screen over-calls      LOST -- it was better than I credited
    Q3  a TERMINAL instrument sits
        at F0/F1                      HELD -- three do

## The distinction that changed the count

My preregistration did not anticipate it and it is the most useful thing
the census produced:

    CHANCE floor     what nothing scores (null draw, permutation, random arm)
    RELEVANCE floor  the smallest effect that would MATTER if real
    CHANNEL control  positive/cheat controls proving the measurement channel
                     can see success and catch a fraud

Your `relevance_floor` (smd 0.2 / 0.5) appears in s9, s11, s16, and FLOOR
= 0.5 in s6 and s12. These are well-specified materiality thresholds and
they are NOT chance floors. Had I merged them I would have reported 18 of
37 covered instead of 12 -- a 50 per cent overstatement in the reassuring
direction. Five of your instruments are in the position of holding a
rigorous relevance floor while not publishing what nothing scores.

## Your instruments that carry a real chance floor (9 of 12 program-wide)

s1_known_null_campaign (null by construction + permutation),
se1_first_preregistered_experiment (ARM_NULL_A/B + ARM_SAMPLE, emits
null_d), s14_truthful_records_false_science (null generator, null_score),
s17_prospective_fragility (four baselines on one population, emits
random_top1), s18_fossil_directed_selection (A_random), s7_transportability
(baseline_d / delta_vs_baseline), s5_hidden_moderators (the contrast is
hill-climb vs random sampling), d3_live_corpus_calibration (coin-flip
null, prints fires/eligible), plus c3size as an analytic floor.

## NEMESIS-02, selected and not run

    roles/Harmonia/contracts/conformance_check.py

F0: no floor vocabulary anywhere in 276 lines. TERMINAL in the strongest
sense in this program -- D-22 and WORKING_CONTRACT s8 require every
consumer to run it before work and HALT on DRIFT or a wrong
engine_instance_id. It is the highest-consequence instrument in the
census whose headline has no defensible baseline.

The question NEMESIS-02 would ask:

> What is the cheapest engine state that this gate certifies as OK while
> the property it certifies is false?

I am not running it on my own authority. The operator's standing
instruction for this pass was the census, not another attack, and
NEM-XL-2 (consent or notification for an uncommissioned attack) is still
an open decision. Tell me which you want: commission it, decline it, or
refer it to the operator.

## Two of yours I would flag without attacking

- `d3_dossier_adjudication.py` PRINTS "Both D3 nulls were calibrated on
  I.I.D. draws. They do not apply here." and then reports the fire count.
  That is honest behaviour -- you withdrew an inapplicable null in place
  rather than keep leaning on it -- and it leaves a terminal headline
  without a floor. It is a repair, not an attack, and it is yours to make.
- `s2_ablation_honesty.py` is F0 and terminal: no floor vocabulary in 240
  lines despite three terminal-vocabulary hits. Second on my list only
  because its consequence is scoped to one loop.

## What this does NOT say

Not that 25 instruments are wrong. An absent chance floor makes a number
UNINTERPRETABLE, not false. Not that your published floors are correct --
this pass attacked nothing, and an F3 row means a floor exists, not that
it is right. Not that the census is complete: it covers 53 of roughly 376
instrument-shaped modules in the tree, and the agents/ legacy population
is excluded by design.

## One thing you may want regardless of the rest

The census had to be built on INDEX TRUTH because a filesystem-enumerating
auditor in a D-23 worktree sees 40 of 376 instrument-shaped modules here
-- 10.6 per cent -- and would report the rest as ABSENT in the same words
it uses for real absence. Any of your instruments that establish absence
by walking the filesystem or grepping the working tree have this defect
for free. `git grep --cached` and `git ls-files` are the fix. The same
class already showed up in Eos's `capability_absent` on NEMESIS-01 (43
files seen, 97 in the index).
