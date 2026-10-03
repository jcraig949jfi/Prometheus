# Review of the Phase 3 synthesis package, by FABLE-5.1 (seat Dionysus)

Written 2026-10-01 and 2026-10-02 (UTC) in answer to the operator's line:
"Consider these, synthesize, document and create response for each of the
3:" followed by three pasted documents. The inputs are saved as received in
`roles/Dionysus/prompts/2026-10-01_review_charter/`.

## The three responses

| file | answers | form |
|---|---|---|
| RESPONSE_1_REVIEW_REPORT.md | the Review Charter: its 12 questions, the 15 required sections, and the closing question | plain text, 80 columns, one paste block |
| RESPONSE_2_RSO_WIND_TUNNEL_v0.1.md | the wind-tunnel design, section by section (24), with replacement text for a v0.2 | same |
| RESPONSE_3_RACE_CAR_PORTFOLIO_R0-R9.md | the portfolio, candidate by candidate, with missing families and an amended strategy | same |

Each can be pasted alone. Responses 2 and 3 point to sections of response 1
for detail. `check_review.py` tests that they agree where they overlap.

## What I had and did not have

Had: the charter, the wind-tunnel design v0.1, the portfolio R0-R9, my own
Phase 3 package (`docs/phase3/design/FABLE-5.1/`) and the four forensic
crawls of the old record. The responses use the charter's file numbers (01
the design, 02 the portfolio); in the saved inputs folder those two are
files 03 and 04.

Not had: `00_README`, `03_GEMINI_CRITIQUE_AND_SYNTHESIS`,
`04_DECISIVE_EXPERIMENTS_AND_WORLD_PROGRAM`, `05_REVISED_90_DAY_PLAN`,
`07_FOSSIL_TO_FOUNDRY_AND_OPEN_DESIGN_SPACE`. The charter lists them as
required reading. They were not pasted and are not on origin/main (searched
by name at a059c0538). Consequences, stated in each response:

- "Scaffold Free-Fall" is reconstructed from the design's section on
  scaffold descent. "Stigmergy Bypass" is defined in file 04 and I do not
  rule on it.
- The 90-day plan in RESPONSE_1 is a standalone plan, not an edit of 05.
- One of my three flaws (no order of construction for the tunnel) is
  conditional: file 05 may supply the order.
- Where the design credits Gemini, I could not read what Gemini wrote.
- Where a response says something is missing, it means missing from the two
  files I had.

I did not open any other architect's own design directory. The charter does
not ask for that, and my seat file forbids it until the operator opens it.

## The synthesis in seven lines

1. Adopt the observatory as a discipline. v0.1 is not yet a build
   specification.
2. Its section-19 protocol has no arm that separates reuse of what was
   built from improvement of the builder, and it leaves five choices open.
   In each of the three settings I registered, an organism with fixed
   inherited machinery passed. In two stricter settings none of the
   organisms I ran passes, and nobody has a positive to show the steps
   would pass anything there.
3. Three of its definitions depend on the organism's shape, and the second
   substrate is not yet given a designed organism with a known answer.
4. One rule orders the work: build nothing before its known-answer case
   exists, where a known answer is a designed positive or one found by
   blind search and certified from behaviour alone.
5. The portfolio's own MVP with two changes: designed organisms with known
   answers in three or four physics in place of the R4 shadow, and a thin
   R3 as the second build. Retire R7 (my own arm).
6. For 90 days: about 65% instrument, 25% candidate architectures, 10%
   re-implementation and blind search. Nine conditions would reverse it.
7. What this tunnel can certify today is retention of random content.
   Certificates for structure, and any criterion for improvement of the
   builder, are open problems.

## New evidence produced for this review

Four preregistered runs in `counterfeit/`, and one file of exploratory
probes. In each run, code and expectations were committed before the
registered seeds ran, and every verdict came out as registered. The probes
are not preregistered and use design seeds only.

| | prereg commit | what it shows |
|---|---|---|
| run 1, `gauntlet.py` | 8dc9ef542 | the section-19 steps as written can be met by a selector over three inherited procedures, under easy readings of four open choices |
| run 2, `gauntlet2.py` | 619472376 | cost, content, sham and donors read strictly, with B, D and E kinds never met and built from parts just learned: a library learner passes all six of my conjuncts in 24 of 24; a selector over 90 ready parts and pairs fails |
| run 3, `gauntlet3.py` | c6adb3a57 | one composite development family and targets made of other parts: the library learner fails; a selector over 32 inherited search orders passes, at half the threshold and under weaker controls |
| run 4, `keys.py` | 635b3cba1 | bits acquired across families can be bounded from behaviour against an exact null; 0, 0, 1.44, 9.46, 23.39 and 38.99 bits on six designed organisms |
| `probes_exploratory.py` | none | what the passes of runs 2 and 3 rest on: the curriculum, the savings factor, the acceptance rule, how worlds are chosen, an easy reading of family C |

See `counterfeit/README.md` for tables, conditions and limits. All of it is
observation about a criterion: designed organisms, toy worlds, one author.

Everything else cited is from my earlier package: the prototype receipts in
`prototype/p1_slice/` and the salvage matrix.

## How the review was reviewed

Three read-only reviewers of my own model family attacked drafts in turn:
one for accuracy against the sources, one arguing as the authors of the
package, one checking the code and claims of runs 2 and 3. They found 38,
21 and 26 defects. The ones that changed the answer:

- The accuracy reviewer re-ran my first counterfeit and showed its pass
  leaned on four open choices read the easy way. Run 2 is the correction.
- The reviewer arguing as the authors showed that the reading they would
  choose (B shares no built part with the history) defeats my library
  learner. Run 3 followed.
- The third reviewer showed that run 3 changed the curriculum as well as
  the parts, so its two verdicts follow the curriculum; that its sham
  cannot fail and its arms coincide, the faults I had named in run 1; that
  run 2 still reads family C the easy way; and that three summary
  sentences claimed more than the runs show. The probes reproduce its
  numbers, and section 11 of RESPONSE_1 was rewritten around them.
- The reviewer arguing as the authors also showed that the repair I had
  proposed (classify where a capability came from by a threshold on
  acquired bits) measures only the size of a memory. I withdrew the
  classification and kept the measurement.
- The reviewer arguing as the authors also showed that my entry rule, as
  drafted, admitted only physics a designer finds legible. It now has a
  second door.
- The accuracy reviewer showed that a self-correction I had drafted (that
  my own requirement XFER-07 was fooled) was wrong.
- Most of the rest, in every round, were places where a draft blamed the
  package for lacking a safeguard it has. Those passages now say what the
  package does and what I would add.

Each round found that the round before had claimed too much. The third
reviewer then checked the revision: 22 of its 26 closed, 4 partly, no new
blocker, and ten new small findings, all addressed in this version. A
fourth reviewer would find more.

The four registered runs are deterministic. Copies of the four scripts
were re-run in a scratch folder on 2026-10-02 and reproduced every receipt
exactly, timestamps apart.

## Where the review goes against my own design, and what it keeps

Against:

- BUILD depends on a declared split of state into fast and persistent.
- My own strict transfer requirements (XFER-01, XFER-03, XFER-05) were not
  applied in my first counterfeit run.
- My tensor-network arm (R7) should be retired.
- My full workspace machine should not be built first; a thin kernel shared
  with R2 should.
- My six coordinates may be a prior shared with the synthesis and not a
  finding. RESPONSE_2 section 4.1 proposes two measured axes in their
  place.
- My scaffold-descent proposal is called the strongest in the synthesis. My
  own reach data show its result is dominated by the acceptance rule.

Keeps: class exclusion against exact bounds, key worlds, a thin integer
kernel pinned to an oracle, designed organisms with known answers, power
gates. They are the parts that have run and returned known answers. They
are also one kind of instrument, and what it certifies is memory.

Stake: six portfolio entries trace to my design in whole or part, and the
builds I recommend coincide with three of my own substrates. RESPONSE_1
section 5 says so and asks the other reviewer to check that ranking.

The delivered design package is not edited by this review.

## Checks

    python docs/phase3/review/FABLE-5.1/check_review.py

It checks form (ASCII, LF, 80 columns, no code fence); every double-quoted
string against the saved inputs or my own files; every figure quoted from
the four runs, from the probes and from my prototype against the receipts;
the preregistration order of all four runs; that the probes ran on the
preregistered code and on design seeds; agreement of the R0-R9 dispositions
between responses 1 and 3; the section tally in response 2; that sentences
withdrawn after review are gone; figures cited from the salvage matrix and
the requirements. I fire-tested it with deliberate mutations; it failed on
each and passed again after restore.

What the checker does not test: whether the arguments are right.

## Literature pointers

Cited as pointers to prior work, not as evidence for any claim about
Prometheus.

Checked by web search this session (title, authors, venue):

- Kirsch and Schmidhuber, "Eliminating Meta Optimization Through
  Self-Referential Meta Learning", arXiv 2212.14392 (2022).
- Szilagyi, Zachar, Fedor, de Vladar, Szathmary, "Breeding novel solutions
  in the brain: a model of Darwinian neurodynamics", F1000Research 5:2416
  (2016).
- Stern and Murugan, "Learning Without Neurons in Physical Systems", Annual
  Review of Condensed Matter Physics 14:417-441 (2023).
- Dillavou, Stern, Liu, Durian, "Demonstration of Decentralized
  Physics-Driven Learning", Physical Review Applied 18, 014040 (2022).
- Kramar and Alim, "Encoding memory in tube diameter hierarchy of living
  flow network", PNAS 118 (2021).
- Mikulik et al., "Meta-trained agents implement Bayes-optimal agents",
  NeurIPS 2020.
- Kruszewski and Mikolov, "Emergence of Self-Reproducing Metabolisms as
  Recursive Algorithms in an Artificial Chemistry", arXiv 2103.08245
  (2021).

From memory, not re-checked this session: Schmidhuber 1993 (self-referential
weight matrix); Fontana and Buss 1994 (AlChemy); Hinton and Nowlan 1987
(learning guiding evolution); Stephens 1991 (change and regularity in the
evolution of learning); Kashtan and Alon 2005 (modularly varying goals) and
their later paper with Noor on search speed; Miconi, Clune and Stanley 2018
(differentiable plasticity); Najarro and Risi 2020 (evolved Hebbian rules);
von Neumann 1956 (reliable organisms from unreliable components); sparse
distributed memory, vector-symbolic architectures and modern Hopfield
networks as families; the relation of coupled learning to contrastive
Hebbian learning.

## Files

    00_README.md                              this file
    RESPONSE_1_REVIEW_REPORT.md               response to the charter
    RESPONSE_2_RSO_WIND_TUNNEL_v0.1.md        response to the tunnel design
    RESPONSE_3_RACE_CAR_PORTFOLIO_R0-R9.md    response to the portfolio
    check_review.py                           the checks
    MANIFEST.md                               hashes
    counterfeit/README.md                     the four runs: results, limits
    counterfeit/gauntlet.py, PREREG.md, RECEIPT_gauntlet.json            run 1
    counterfeit/gauntlet2.py, PREREG_gauntlet2.md, RECEIPT_gauntlet2.json  run 2
    counterfeit/gauntlet3.py, PREREG_gauntlet3.md, RECEIPT_gauntlet3.json  run 3
    counterfeit/keys.py, PREREG_keys.md, RECEIPT_keys.json               run 4
    counterfeit/sweep_gauntlet1_exploratory.py and its receipt (not
        preregistered: the budget sweep of run 1)
    counterfeit/probes_exploratory.py and its receipt (not preregistered:
        probes of runs 2 and 3 on design seeds)
    counterfeit/MANIFEST.md                   hashes

## Limits

One reviewer, one session, five of seven package files missing. The new
evidence is small and about an instrument. The two measured axes, the
isomer panel and the separate recording of claim kind are proposals; only
the bound on bits acquired has been run, once, on designed organisms. The
plan's percentages are judgments. Three reviewers found 85 defects in
drafts, and each round changed the answer, so a further reviewer should
expect to find more, and the right response to that is to fix them.
