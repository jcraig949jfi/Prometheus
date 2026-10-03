# Phase 3 hardening, FABLE-5.1 version (seat Dionysus)

Written 2026-10-02 (UTC) in answer to the operator's message, saved as typed
in `roles/Dionysus/prompts/2026-10-02_hardening_v0.2/`: compare the review by
Enceladus (ASTRA-6.0) with mine, synthesize, synthesize with the hardening
package by ChatGPT 5.6, and make my own version of that package.

## The three documents

Plain text, 80 columns, each one paste block.

- `01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md`: the two reviews compared
  and synthesized; where the package's design comes from, what it left out,
  its gaps; answers to its review charter.
- `02_HARDENING_DESIGN_v0.2_FABLE.md`: my version of the hardening design.
- `03_TEST_HARNESS_SPEC_FABLE.md`: my version of the test harness
  specification.

And `harness/`, a reference harness that runs, and `attack/`, the record of
the adversarial reads.

## The inputs

- A: my review, `docs/phase3/review/FABLE-5.1/` (ff1d7f0f4).
- B: the review by Enceladus (ASTRA-6.0), read in place on branch
  `enceladus/rso-review-2026-10-01` at f4d9e72d9. Five files; nothing else in
  that worktree was opened, and no file in a design directory of another
  architect.
- C: the hardening package v0.2 by ChatGPT 5.6. The operator pasted nothing;
  I identified five files in the Downloads folder by title and time. Copies
  and hashes are in the prompts folder above.
- O: the wind-tunnel design v0.1 and the portfolio R0 to R9 that A and B
  reviewed, as saved with my review's inputs.

Not received: any harness code. The package's archive holds five empty
folders, two of them compiled-code caches, and there is no file numbered 04.
The package describes a reference harness and asks reviewers to run it. Its
status here is NOT VERIFIED. Please send the files if they exist.

## The result in ten lines

1. The two reviews agree on the shape (a thin federation, no strong claim
   yet) and on the main fault (the steps of section 19 can be met without the
   thing they are named for). Each lists six repairs. Mine include an exact
   bound on what crossed a boundary; ASTRA's, interventions on the learner.
2. Mine was shown incomplete by a run. ASTRA's has not been run, and it
   promises no universal detector. My reading, not ASTRA's: both give a claim
   relative to something registered, so a nested claim should name the class
   it excludes.
3. ASTRA is right against my review on twelve points. Eight are taken into
   what runs or into the registration; four are rules nothing yet tests.
4. Read from my own receipts by code, 26 cells: at each of three settings
   the steps said yes to an organism with fixed inherited machinery. No
   positive for the strong claim has been built in either review, in the
   package or here.
5. The package's design is a fair merge of the two reviews and the original.
   Verdict on its design: REPAIR, for eight gaps. Its harness did not arrive.
6. My version: a ruler, a gate and a report are each believed only after
   passing a sound case and rejecting a broken one, and not on their author's
   word.
7. That clause is from experience in this pass. Each version of my harness
   passed every case I had given it, and each reader then found faults that
   got through. At first sight the tests missed 22 of 25, 34 of 44, 20 of 32
   and 26 of 36 one-line changes to the gates, and on the third version 12 of
   26 and 20 of 54.
8. The harness here is the third version, amended after a final round of
   reading: 21 gates, 50 sound cases, 258 cases that must not pass, 29 known
   escapes pinned, at least one in every gate. The list of escapes is not
   complete, and nobody has read the amendments.
9. Three claims about my bits certificate were refuted by readers'
   simulations: that it is a ruler for nested improvement (the draft), that it
   is a ruler for reuse of built parts (version two), and that its control
   catches an answer from outside the life (version three). It certifies that
   information crossed a boundary; on a pair never seen, with fresh keys, that
   three families shown separately were combined. It does not say how.
10. Smallest next experiment: combination on a pair never seen, against an
    exact bound. Simulated here; not registered.

## What ran, and what did not

Ran: `harness/` (110 unit tests; `run_harness.py` writes
`RECEIPT_harness_v0.json`; `mutation_probe.py` writes
`RECEIPT_mutation_probe.json`). It is a conformance skeleton on toy fixtures:
four small physics by one author, one world, no noise. It also reads four
receipts of my review, and holds two exploratory simulations of key worlds.
And `attack/replay_attack.py`, which replays the first reader's attack on the
first version of the harness.

Did not run: any registered experiment. The nested compiler, the genuine
learned updater, door two, the stochastic and continuous observer contracts
and the W1 world are specified and not built. The combination world is
simulated and not registered. Document 3 marks each.

## Checks

    python -B docs/phase3/hardening/FABLE-5.1/check_hardening.py
    python -B docs/phase3/hardening/FABLE-5.1/fire_test.py
    cd docs/phase3/hardening/FABLE-5.1/harness
    python -B -m unittest discover -v

`check_hardening.py` makes 61 checks.

- Form: ASCII, LF, no tab, 80 columns, in the three documents and the three
  READMEs.
- Sources. ASTRA's five files are read from their commit with git and must
  hash as recorded, so the clone must hold that commit (it is on origin). The
  copies of the package must match their manifest.
- Quotations. Each double-quoted string in the documents is registered with
  one source and must be found there word for word. The checker does not read
  who the sentence says spoke.
- Receipts. The receipts quoted here were written by the code on disk, and
  the three kept versions of the harness are the code that wrote theirs.
- Numbers. Statements that the checker builds from a receipt or a source
  must appear in the documents, and eight tables are parsed and compared row
  by row.
- Pins. The text of each of the six files is hashed, with nothing collapsed.
  An edit made after pinning fails the check until a person pins the file
  again. A pin freezes a text. It does not verify it.

`fire_test.py` plants errors in a copy and counts what the checker catches.
Of 78 errors I planted, the pins catch 78 and the content checks alone catch
60. By kind, with the pins off: number 39 of 39, pinned number 0 of 3,
quotation 3 of 3, attribution 1 of 4, table 11 of 11, word 3 of 13, form 3 of
3, whitespace 0 of 2.
Those plants are mine, so that figure is fitted to the checker. On plants the
readers chose in the final round, with the pins off, the checker as it then
stood caught 3 of 26, 35 of 80 sampled by rule, and 5 of 18. A few checks of
one statement against another were added since. The content checks cover
numbers that have a receipt behind them, and little else. A changed word, or
a cell moved to the other column of a table, is caught by the pin alone, and
a pin only freezes. In the list above a pinned number is one that nothing
rebuilds.

The checker does not test whether the arguments are right, and it cannot
check a judgment, such as which gate covers which historical fixture.

## How this pass was reviewed

Three adversarial reads and a final round, read-only, all by readers of my
own model family. Briefs and reports are in `attack/`, as sent and as
received.

- First read, of the draft: 11 blocking and 46 major defects.
  - Fairness. The draft charged the package, and in places ASTRA's review,
    with lacking things their text contains, and credited my review with
    ideas that are in the original design. Document 1 was rewritten.
  - The harness. By my count of the labels in the reader's scripts, 65 of
    its 71 broken cases got through and all 12 of its sound cases were
    refused; 22 of 25 one-line changes to the gates went unnoticed by the
    tests. The harness was rewritten. `attack/replay_attack.py` replays this.
  - The ladder. The draft offered a key world with a second nested boundary
    as a ruler for nested improvement. The reader simulated it: one cached
    table with 256 inherited re-indexings scores 13.79 of 16 where the bound
    is 3.38.
  - The checker. 22 of 33 errors the reader planted passed the first one.
- Closure read, of version two, by the same reader: of the 57 defects, 45
  closed, 11 partly, 1 open; and 1 blocking and 13 major new ones. Among
  them: I had dropped ASTRA's adversarial pass from the comparison; I had
  put my synthesis in ASTRA's mouth; the mutation score I quoted was taken on
  changes the tests had been written against (34 of 44 fresh ones went
  unnoticed); and a cache that reads no label passes the world I proposed as
  the next experiment.
- Second read, of version two, by a fresh reader with three forks: 8 blocking
  and 38 major defects. Among them: the next experiment's headline claim was
  contradicted by my own gate, and its falsifier could not fire; two kit
  verdicts depended on which receipt rows I had typed in; three gates passed
  faults the documents said they caught; every one of the 21 gates had an
  escape that was on no list.
- Final round, of version three, by both readers: 2 blocking and 9 major
  defects, new or still open. Among them: the fire test could not run in its
  own copy; the pins did not freeze the columns of a table; an organism that
  combines nothing passed both arms of the next experiment where one arm's
  key was reused; fifteen faults on no list passed the gates; and the tests
  missed 12 of 26 and 20 of 54 fresh one-line changes.

What was changed after the final round: the corrections it asked for in the
documents; in the harness, stricter registration, a search held to its
registration, torture checks on the whole panel, audits refused at other
sizes than 24, and a custody check on keys in the unseen-pair world; in the
checker, pins on the raw text and a fire test that runs. These changes were
checked by code only: the unit tests, the mutation probe, the checker and its
fire test. No reader has seen them.

This is the failure three readers had already found in my review, found
again here in every round: sentences stronger than the evidence, sources
blamed for lacking what they contain, and checks only their author had tried
to break.

## Files

    00_README.md                                      this file
    01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md    document 1
    02_HARDENING_DESIGN_v0.2_FABLE.md                 document 2
    03_TEST_HARNESS_SPEC_FABLE.md                     document 3
    check_hardening.py                                the checks
    fire_test.py, RECEIPT_fire_test.json              errors planted for it
    harness/README.md, run_harness.py, mutation_probe.py
    harness/mutation_sets_final.py                    the final round's changes
    harness/RECEIPT_harness_v0.json, RECEIPT_mutation_probe.json
    harness/rso_harness/*.py                          twelve modules
    harness/tests/test_harness.py                     110 tests
    attack/README.md, replay_attack.py, RECEIPT_attack_on_first_version.json
    attack/BRIEF_to_the_reader.md, REPORT_of_the_reader.md
    attack/first_version/, attack/reader/     first read: harness, scripts
    attack/closure_reader/                    briefs, reports, scripts
    attack/second_reader/                     briefs, reports, scripts
    attack/second_version/                    the harness the two reads attacked
    attack/third_version/                     the harness the final round read
    MANIFEST.md in every folder               hashes
    .gitattributes                            LF line ends in every checkout

## Limits

I am one of the two reviewers compared, and the author of every gate in the
harness. Three model outputs agreeing is not evidence. Five of the seven
files of the original synthesis package never reached me or ASTRA. I
identified the hardening package by file name and time, not from a paste.
Every reader is of my own model family, and the last changes have had no
reader at all.
