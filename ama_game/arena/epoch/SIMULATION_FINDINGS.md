# Simulated epochs — what the cycle machinery does and does not establish

**Run:** 2026-08-25 · scripted seats, no language models · 12 runs × 50 epochs
per arm. Full output in `SIMULATION.txt` / `SIMULATION.json`; one run's graph in
`sim_graph.jsonl`.

This is instrument calibration, the same status as `generator/pilot.py`. It says
nothing about whether live agents produce anything worth scoring.

## 1. The cycle closes, and the metrics can tell when it doesn't

| metric | ADAPTIVE | NULL | perm p |
|---|---|---|---|
| bypasses | 19.08 | 11.08 | **0.000** |
| landed_rate | 0.43 | 0.26 | **0.000** |
| bogus_caught | 9.67 | 6.25 | 0.007 |
| promotions | 2.00 | 1.92 | 1.000 |

ADAPTIVE Red reads the promoted defenses and attacks a family none of them
covers. NULL Red picks uniformly and never looks. Identical machinery otherwise.

The separation matters more than the numbers: a simulated game always looks like
it works if you only run the arm designed to work. These metrics distinguish an
adapting Red from a random one, so a live game's "the loop closed" claim would
be falsifiable rather than decorative.

**`promotions` is not a cycle metric.** It does not separate (p = 1.000), and it
should not: promotion depends on Blue landing a kill and Purple proposing, not
on Red's strategy. Reporting it as evidence of adaptation would be an error, and
it is listed here so nobody makes it later.

## 2. Internal control: the defenses are doing the work

Between-arm separation could come entirely from Red's choice, with defenses
contributing nothing. The within-arm check settles it — after the first
promotion, landing rate on families a promoted defense covers vs families it
does not:

```
NULL       covered 0.00   uncovered 0.38   perm p 0.000
ADAPTIVE   no covered epochs at all
```

In the NULL arm Red blunders into covered families by chance and **never lands**
there. That is a promoted defense actually raising detection, measured
separately from Red's behaviour.

ADAPTIVE has no covered epochs to measure, which is not a gap — it is the
adaptation being total. Red never once attacked a covered family after the
defense was promoted.

## 3. Declared coverage was wrong every single time

The rulebook's "no defense becomes permanent merely because it catches the
example that inspired it" earned its place immediately:

| defense | declared | actually catches | FP on clean |
|---|---|---|---|
| `D_instantiation_spotcheck` | M8 | M8, **M10, M11** | 0% |
| `D_endpoint_spotcheck` | M4 | M4, **M5, M7, M9, M12** | 0% |
| `D_out_of_domain_instantiation` | M10 | M10 only | 0% |
| `D_case_cover_arity` | M6 | M6 only | 0% |
| `D_unjustified_generalization` | bounded-search | nothing in this pool | 0% |
| `D_range_start_outlier` | M4 | **nothing** | **42%** |

Every author under-declared or over-declared. The two that generalise do so
across the play/holdout boundary — `D_endpoint_spotcheck` was written against
M4 and independently catches M9 and M12, which its author never saw. That is
what promotion is supposed to detect, and it did:

```
epoch 11  D_instantiation_spotcheck  designed against M8, promoted on M10 hits
epoch 27  D_endpoint_spotcheck       designed against M4, promoted on M9 hits
```

`D_range_start_outlier` was written deliberately weak, and the machinery
rejected it on the right grounds: it flags 42% of valid reasoning and catches
nothing. Without the negative regression examples it would have looked harmless.

**First run had zero promotions in both arms.** Every candidate defense caught
only its own family — a fit statistic — so the bar correctly refused all of them
and the loop could not close. That was a defect in the defense library, not the
arena, and it is what forced the two cross-family defenses into existence.

## 4. The fingerprint hazard is large and needs fixing before live play

A grep over the mutation operators' prose flags **57 of 68 planted defects
(84%)**. Every operator appends a tell to the step it rewrites — "CONVERSE:",
"Cancelling the factor", "the same estimate is taken", and so on.

A Blue that string-matched those tells would post an 84% detection rate while
detecting nothing mathematical. That is the exact mirror of the rulebook's kill
condition about attacks exploiting model fingerprints.

The structural defenses above never read `text`, so their scores are clean. But
this is a live hazard for real games: **generator-authored prose must not carry
operator tells**, or a live Blue will find them and the arena will measure
string matching. Fixing it means rewriting mutated steps in the same register as
unmutated ones, which is work the alpha has not done.

## 5. What this cannot test

**The family set is closed.** Red picks from eight known mutation families. A
"bypass" here means selecting a family no promoted defense covers — never
inventing one that does not yet exist.

The rulebook's most interesting listed outcome is Red producing an unforeseen
attack. That is outside this simulation's vocabulary by construction: scripted
seats cannot invent. This machinery can prove the loop's *plumbing* works and
that the metrics are sensitive to adaptation. It cannot say anything about
whether real agents generate novelty, which is the actual open question and the
reason live seats exist.

It also inherits the bounded-menu problem directly: an arena whose attack menu
is fixed will show the loop closing and then stop, because there is nothing left
to bypass once every family is covered. In these runs that ceiling is visible —
after two promotions, six of eight families remain uncovered and Red simply
lives there.

## 6. Status

Machinery: works. Graph merge, promotion against a sealed holdout, bypass
detection, and bogus-kill auditing all behave, and the metrics separate a real
loop from a fake one.

Not established: anything about live agents, anything about invention, and
nothing that survives the fingerprint hazard until the mutation prose is
rewritten.
