# spec-capcarrere-r1-density: protocol, committed BEFORE the code and the run

Herakles, 2026-09-11. Backlog L-2 (recover the radius-1 density classifier)
and C-1 (a fifth criterion needs its convention declared beside the other
four before it is added). Built from c8d576e41 on branch
herakles/comms-queue-2026-09-11, worktree herakles-comms-queue.

## What is in hand

`original/density_ca.pdf`, sha256 e83ac56e..., ORIGINAL_SPECIMEN, manifest row
`art-capcarrere-1996-prl`. Capcarrere, Sipper, Tomassini, Phys. Rev. Lett.
77(24):4969-4971 (1996), DOI 10.1103/PhysRevLett.77.4969. Read in full
(3 pages, text layer at `derived/density_ca_text.txt`). Evidence tier for
every statement below: PRIMARY_SOURCE_READ, page and paragraph cited.

## What the paper states (p. 4969-4970, and footnote [13] p. 4971)

1. The rule is elementary rule 184 (Wolfram numbering, ref [9]):
   s_i(t+1) = s_{i-1}(t) if s_i(t) = 0, else s_{i+1}(t). Rule 226, its
   reflection, "holds the same properties".
2. Periodic boundary. Horizon T = ceil(N/2).
3. The OUTPUT CONVENTION is not a fixed point. Theorem, p. 4970:
   (1) density > 0.5  ->  (a) some adjacent pair is 11 at T, and
                          (b) for all i, s_i(T) = 0 implies s_{i+1}(T) = 1
                              (equivalently: no adjacent 00 pair);
   (2) density < 0.5  ->  some 00 pair exists and no 11 pair exists;
   (3) density = 0.5  ->  strict alternation (no 00 and no 11).
   Lemma 1: rule 184 conserves density; so the rule never reaches a
   uniform state from a non-uniform one, and under a FIXED-POINT criterion
   it must score approximately zero. That is the spurious failure the
   2026-09-10 catalogue warned about, and it is measured below as a
   control rather than assumed.
4. Footnote [13]: every one of the 256 elementary rules was tested on 1000
   randomly generated initial configurations, N = 149, with "correct"
   defined by the theorem. Rules 184 and 226: 100%. Rules 57 and 99:
   "trailing markedly behind at 60%". Nothing else is reported.

## Unspecified parameters (METHOD s7 step 2), each with the variants built

U1. The distribution of "randomly generated" initial configurations.
    Variant A: each cell i.i.d. Bernoulli(0.5) (density concentrated at
    0.5; the hardest case for an imperfect rule).
    Variant B: density drawn uniformly on [0, 1], then the configuration
    drawn at that density (the EvCA-line convention, evca.make_ics).
    > CORRECTION 2026-09-11, after the run (REPORT.md): the parenthetical
    > is wrong. evca.make_ics(density=None) is i.i.d. Bernoulli(0.5), i.e.
    > variant A, and the EvCA line's published PERFORMANCE figures use that
    > unbiased ensemble; its GA TRAINING ensemble is uniform-density. The
    > two variant definitions are unchanged and were run as written.
    Both are run. Footnote [13]'s 60% figure for rules 57/99 is the only
    number that can discriminate them; see P2 and the INDETERMINATE branch.
U2. Whether the 1000 configurations were shared across rules or redrawn
    per rule. Shared here (paired design), stated on every number.
U3. Whether a run "terminated after T steps" or "continued until the
    block arrives at two predetermined cells" (p. 4971, both are offered).
    Terminate at T = ceil(N/2). The theorem is stated at T.

## The criterion to be added: `block_output_score` in `herakles.eca`

Input: rule number, ICs (n, N), steps. For each IC: d = (number of 1s)/N
exactly; evolve `steps`; has11 = any adjacent (circular) pair is 11;
has00 likewise. Correct iff
    d > 0.5 : has11 and not has00
    d < 0.5 : has00 and not has11
    d = 0.5 : not has11 and not has00
Score = fraction correct. ELIGIBLE COUNT = n (every IC has a defined
answer under this convention, including d = 0.5; unlike `at_T` in the
radius-3 library there is no tie exclusion and no odd-N requirement).
The published-figure horizon is steps = ceil(N/2); the function takes
steps explicitly like every other criterion in these libraries.

Attainable range: [0, 1]. CHANCE FLOOR, analytic: a constant rule (0 or
255) ends uniform, so it has exactly one of has00/has11 and is correct on
exactly the ICs whose density falls on the matching side of 0.5. Under
variant A with N odd that is 0.5 in expectation; under variant B also 0.5.
So the floor of this instrument is 0.5, NOT 0, and footnote [13]'s 60%
for rules 57/99 is 0.10 above the floor, not 0.60 above it. This is
stated before the run (NEM-14: an instrument number without a chance
floor is not a number).

## Controls (base rule 3), all run before any figure is read

POSITIVE  rule 184 and rule 226 must score exactly 1.000 on every IC
          under both variants. This is a theorem, so any other value is a
          defect in my implementation or my transcription of the
          convention, and NOTHING ELSE IN THIS PROTOCOL IS READ until it
          is fixed.
CHEAT     configurations constructed directly from a known density
          (alternating background with one planted 11 or 00 block, or pure
          alternation for d = 0.5), scored at steps = 0. The detector must
          fire (1.000). Proves the criterion can see the answer pattern.
NEGATIVE  rule 204 (identity): the IC is scored as itself. Expected near
          0 under variant A (a random string of 149 bits almost surely
          contains both a 00 and a 11). Rules 0 and 255: expected 0.5 (the
          floor). Rule 170 / 240 (pure shifts): the pattern is unchanged
          up to rotation, so expected equal to rule 204 exactly.
WRONG     rule 184 scored under a fixed-point criterion (uniform at T):
CRITERION expected approximately 0 (only ICs already uniform count).
          This is the "criterion mismatch" demonstration, measured.

## Preregistered predictions for the footnote [13] replication

Configuration: N = 149, T = 75, n = 1000 ICs per variant, seed 20260911,
all 256 rules, shared ICs. Per-rule SE at p = 0.6, n = 1000: 0.0155
(binomial). Wilson 95% intervals reported beside every quoted rule.

P1. Rules 184 and 226 score 1.000 under both variants. (Theorem.)
P2. Rules 57 and 99 fall in [0.50, 0.70] under at least one variant.
    "About 60%" is read as that band; it was chosen before the run and
    is 6 SE wide, so the gate exceeds its own measurement error.
P3. Under the variant where P2 holds, no rule other than 184/226 scores
    above rules 57 and 99. ("Followed by rules 57 and 99" -- they are
    third and fourth.)
P4. Rules 57 and 99 score identically up to sampling, being reflections.
P5. Variant discrimination: if P2 holds under exactly one variant, that
    variant is the best available reading of U1, reported as a LEAD with
    the number, not as a fact. If it holds under both or neither, U1 is
    INDETERMINATE and stays so.
P6. Rule 184 under the fixed-point criterion scores below 0.02.

Kill / indeterminate branches, in order:
  - P1 fails: implementation defect. Stop. Report the defect, fix, rerun.
    No other prediction is read from a run where P1 failed.
  - P2 fails under both variants: the IC distribution or N convention is
    not one of my two variants. Report INDETERMINATE on U1; P1/P3/P4/P6
    are still read because they do not depend on U1.
  - P3 fails: report the intruding rules with their intervals; the
    published footnote is then not reproduced on ranking and that is
    filed as a finding, not explained away.

## Replication floor

Five seeds (20260911..20260915) for the seven named rules (184, 226, 57,
99, 0, 255, 204) at n = 1000 each; the full 256-rule screen at two seeds,
and the ranking compared across them. Unit of analysis is the IC within
a rule; rules share ICs within a seed and are therefore not independent
of each other, which is stated on every cross-rule comparison.

## What this enables

- C-1: a fifth criterion with its published-figure convention declared,
  and a row in the criterion table stating that `block_output_score` is
  comparable to footnote [13] and to NOTHING in the radius-3 line.
- X-4: a second lineage (EPFL Logic Systems Laboratory, 1996) in the
  historical arm, with a hand-designed rule whose performance is a
  theorem rather than a sample. It is a REFERENCE organism, not an
  evolved one; the evolved rules of that laboratory (Sipper's cellular
  programming, refs [6], [7]) are the next recovery target and are not
  claimed here.
- L-2 closes as RECOVERED only when the run reproduces footnote [13].
