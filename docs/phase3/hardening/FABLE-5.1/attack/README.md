# Three adversarial reads of this package, and a final round

The record behind one sentence of the package: a gate that only its author
has tried to break is not yet a gate.

    python -B replay_attack.py     about four minutes; rewrites
                                   RECEIPT_attack_on_first_version.json

## What is here

    BRIEF_to_the_reader.md      first read: what I asked for, as sent
    REPORT_of_the_reader.md     what came back, as received: 11 blocking and
                                46 major defects, and minor ones
    first_version/              the harness as I first wrote it: 21 gates, 34
                                sound cases, 62 mutants, 31 tests, all mine,
                                every gate PASS. Its receipt is the one it wrote
    reader/                     the scripts the first reader wrote against it
    replay_attack.py            runs those scripts on a temporary copy of the
                                first version and counts
    RECEIPT_attack_on_first_version.json

    closure_reader/             the same reader, resumed. On version two:
                                BRIEF.md, REPORT.md, scripts/. On version
                                three: BRIEF_final.md, REPORT_final.md,
                                scripts_final/
    second_reader/              a fresh reader. On version two, with three
                                forks: BRIEF.md, REPORT.md, three fork
                                reports, scripts/. On version three, alone:
                                BRIEF_final.md, REPORT_final.md, scripts_final/
    second_version/             the harness the closure read and the second
                                read attacked: 44 sound cases, 148 mutants, 59
                                tests. Its two receipts are the ones it wrote
    third_version/              the harness the final round read: 48 sound
                                cases, 215 mutants, 103 tests. Its two
                                receipts are the ones it wrote

The first read is replayed. The others are records: their scripts point at
copies in a scratch folder of the machine they ran on, and are kept as
written. Their counts are quoted from the reports and were not run again.

The harness as it stands now is in `../harness/`. It differs from
`third_version/` by what was changed after the final round, and no reader
has seen those changes.

## What the replay of the first read returns

    broken cases written by the reader .......... 71
      passed by the first version ............... 65, in 19 of 19 parts probed
    sound cases written by the reader ........... 12
      rejected by the first version ............. 12
    one-line changes to gate logic .............. 25
      not noticed by the first version's tests .. 22

And the reader's simulation of the key world with a second nested boundary,
which my first draft proposed as a ruler for nested improvement (3,000 lives;
mean correct of 16 in the first family of a later epoch; the bound for
carrying nothing is 3.38):

    carries nothing .................................. 3.39
    offset-only solver that forgets at the boundary .. 3.39
    the same, without the forgetting ................. 4.10
    one cached table, 256 inherited re-indexings ..... 13.79

## How to read the first read

Broken and sound are the reader's labels (E and S in its output); 65 and 12
are my count of them, and the reader's report states neither number. Ten of
the 71 are two faults swept over a parameter. One of the 22 unnoticed changes
alters no verdict. Six of the 12 sound cases are refused by later versions
too, some of them on purpose. The reader's files are kept as it wrote them,
with one exception: they are run through a small driver that points them at
the receipts of my review. Two of its files are kept for the record and not
replayed: `drv.py` (its own driver, with a path on this machine) and
`p10_fire_checker.py` (its fire test of the first checker, which needs a
mirror of the repository; it reported 11 of 33 planted errors caught).

## What the two later reads found, in their own counts

Closure read (closure_reader/REPORT.md):

    defects of the first read ................... 57
      closed, partly closed, open ............... 45, 11, 1
    new defects ................................. 1 blocking, 13 major
    earlier broken cases still passing .......... 14, of which 6 unlisted
    new faults that passed ...................... 14, in 11 gates
    one-line changes to gate logic .............. 44
      not noticed by the tests .................. 34
    errors planted in the documents ............. 69
      not caught by the checker ................. 35

Second read (second_reader/REPORT.md):

    defects ..................................... 8 blocking, 38 major
    gates with a passing fault on no list ....... 21 of 21
    one-line changes, the reader's set .......... 32, of which 20 unnoticed
    one-line changes, a fork's set .............. 36, of which 26 unnoticed
    errors planted in the documents ............. 13
      not caught by the checker ................. 12

## What the final round found, in its own counts

Closure reader (closure_reader/REPORT_final.md):

    defects, new or still open .................. 1 blocking, 4 major
    one-line changes to gate logic .............. 26
      not noticed by the tests .................. 12
    errors planted, chosen by the reader ........ 26
      caught by the checker with its pins off ... 3
    errors planted, sampled by rule ............. 80
      caught by the checker with its pins off ... 35

Second reader (second_reader/REPORT_final.md):

    new defects ................................. 1 blocking, 5 major
    passing faults on no list ................... 15, in 12 gates
    sound cases refused ......................... 4
    one-line changes to gate logic .............. 54
      not noticed by the tests .................. 20
      of which alter no verdict ................. 2
    errors planted in the documents ............. 18
      caught by the checker with its pins off ... 5

The blocking defects: the fire test of the checker could not run in its own
copy, and an organism that combines nothing was called COMBINED in the
unseen-pair world where the life's own key was reused.

## How the reports were saved

As returned. Characters outside ASCII were replaced mechanically in 2 of the
reports, and HTML entities put in by the notification wrapper were turned
back into their characters in 4; each file says so at its head. All readers
are of my own model family. An author from another family would find other
things.
