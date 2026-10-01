# Preregistration: key world, a first run of the ORIGIN ruler

Reviewer: FABLE-5.1 (seat Dionysus). Written 2026-10-01, before the
registered run. Committed with keys.py and before any receipt exists.

## Why this run exists

The gauntlet (PREREG.md, RECEIPT_gauntlet.json) showed that the section-19
protocol passes a selector among inherited procedures. The review proposes a
repair: decide where a capability came from by a counting bound. A repair
that has never returned a known answer is no better than the criterion it
replaces, and my own review says a ruler needs reachable positive and
negative outputs. So this run puts the proposed ruler on designed organisms
whose answers are known.

It tests one thing: can the ruler tell selection among inherited
alternatives from acquisition through experience, with a designed positive,
designed negatives and fire tests. It does not test anything about
"recursive".

## The world

A life has a hidden key: a permutation of 16 symbols, drawn fresh per life
(44.25 bits). A life is 6 families. Each family has a hidden offset. Every
symbol is shown once per family in random order; the organism predicts
(key[x] + offset) mod 16 and is then told the answer.

Exact bound. For a policy that carries nothing from one family to the next,
the answer on the t-th trial is uniform over the 17 - t outputs not yet
used. Its best expected score is H_16 = 3.3807 correct of 16.

## The ruler, fixed here (function `rule` in keys.py)

The independent unit is the life. Each organism runs 2,000 lives in the
normal condition and 2,000 in the irrelevant-history condition (first five
families from an unrelated key, last family from the life's key).

1. World check. If the declared key is no larger than the selection bound,
   return RULER_NOT_APPLICABLE.
2. If the first family's mean score exceeds the threshold, return
   INHERITED_OR_LEAK.
3. If the later families' mean score does not exceed the threshold, return
   NO_SAVINGS.
4. If the last family's mean score after irrelevant history exceeds the
   threshold, return INHERITED_OR_LEAK.
5. Certified bits carried: for each trial position 1 to 15 of the last
   family, a one-sided exact lower bound on accuracy (total error 1e-6
   across positions), turned into bits by Fano's inequality against the
   number of outputs still unused, and summed. This is a lower bound on the
   information the organism's carried state holds about the key.
6. If certified bits exceed the selection bound return CONSTRUCTED,
   otherwise WITHIN_SELECTION_BOUND.

Threshold: H_16 plus a Hoeffding margin at 1e-6 over 2,000 lives, 4.3210.
Selection bound: the cell allows 2,880 bits of inheritance (64 permutations
at 45 bits); a list held in G bits has at most G entries, so an index into
it carries at most log2(2880) = 11.49 bits.

## Organisms and expected verdicts (the EXPECTED table in the code)

| organism | what it is | expected |
|---|---|---|
| ELIM | carries nothing across families | NO_SAVINGS |
| SELECTOR(64) | inherits 64 ready permutations; an index develops | NO_SAVINGS |
| ACQUIRER(4) | learns the relative table of 4 symbols in the first family | WITHIN_SELECTION_BOUND |
| ACQUIRER(8) | the same for 8 symbols | WITHIN_SELECTION_BOUND |
| ACQUIRER(12) | the same for 12 symbols | CONSTRUCTED |
| ACQUIRER(16) | the same for all 16 | CONSTRUCTED |
| fire test A | SELECTOR(64) in a world whose key is drawn from its own list, honestly declared as 6 bits | RULER_NOT_APPLICABLE; with the world check skipped the ruler must be fooled (CONSTRUCTED) |
| fire test B | HARDWIRED: inherits the key; the harness reuses one key for every life and declares it fresh | INHERITED_OR_LEAK |
| fire test C | the power gate given 200 lives | refuses |
| fire test D | SANDBAGGER: as B, but hides the key in the first family | INHERITED_OR_LEAK; with the irrelevant-history arm skipped the ruler must be fooled (CONSTRUCTED) |

Known answers, checked by the code: for ELIM and each ACQUIRER(k) the exact
expected score is computed from the organism's definition with rational
arithmetic (3.3807, 6.1033, 9.7179, 13.0834, 15.0625 correct per later
family) and the observed mean must lie within five worst-case standard
errors of it. The certified bits must never exceed what the organism really
holds (0, 11.41, 24.95, 35.67, 40.25 bits).

Power gate, run before any organism: each exact expected score must sit at
least five worst-case standard errors (0.894) from the threshold. At 2,000
lives it passes.

The gate of this run is PASS only if every verdict, every known answer and
fire tests A, C and D come out as written above.

## Design runs, disclosed

I ran the script on design seeds (bases 23, 31, 47, 59; nothing written)
several times while building it, and changed it three times after seeing
output:

1. The first version counted every later family as an independent trial.
   Families of one life share a key, so they are not independent. The life
   is now the unit, which widened the margin from 0.42 to 0.94.
2. With the wider margin a two-symbol acquirer (expected 4.26) no longer
   cleared the threshold with power. I replaced it by ACQUIRER(4) and added
   the power gate.
3. I saw that an organism which inherits a reused key and hides it during
   the first family would be called CONSTRUCTED. I added the
   irrelevant-history arm and the SANDBAGGER fire test.

On the final script the design run matched every expectation. ACQUIRER(8)
was certified at 9.4 to 10.8 bits across design seeds and versions, below
the 11.49 bound, although it holds 24.95 bits. I expect the same on the
registered seeds: the ruler is conservative, and for a partial acquirer it
misses. That is a miss, not a false alarm, and I will report it as one.

The registered base is 2026100122. It has not been run.

## What I will and will not say

- If the gate passes: "on designed organisms in one toy world the proposed
  ruler separates a selector from an acquirer, refuses where the world is
  too small to tell, and catches two leaks". Not: that the ruler is
  qualified for any real substrate, and nothing about depth or recursion.
- If any verdict differs: the receipt is kept as GATE FAILED and the review
  says the repair failed its own first test.
- Level: one author, one host, designed organisms. C0 and I1 in my
  package's terms.
