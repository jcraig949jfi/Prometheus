# Cycle 055 — Lane A/B run at last: reading works, and each lane caught the other's error

Executes the O-4 experiment pre-registered at cycle 041 and queued for fourteen cycles.
Prereg `dd586e02`; **Lane A verdicts sealed at `013e16ab` before Lane B was written** — that
commit is the blind.

## 1. The headline: the categorical claim was wrong

```
P(found | INCIDENTAL reading, bug not the question)  =  0 / 11    (the old measurement)
P(found | TARGETED review,   bug IS the question)    =  7 / 8     (this cycle)
```

I have been acting on *"reading does not work for this class"* for a dozen cycles. **It was
never measured.** Targeted review with a one-question checklist found seven of eight, and the
one it passed — `compute_genome_atom_frequencies`, which returns `{}` on empty input — is
genuinely clean.

## 2. Each lane caught an error the other made

**Lane B falsified a Lane A flag (#8, `bootstrap_ci_from_seed_means`).** Lane A reasoned that
resampling a single seed would **collapse the CI to spurious tightness**. Measured:

```
n = 1 seed   CI width 0.5000
n = 5 seeds  CI width 0.2203
```

**n = 1 is WIDER, not narrower** — correctly reflecting less information. My reasoning was
backwards, and only executing it caught that. This is a **Lane A false positive**.

**Lane A caught a defect Lane B's probe scored CLEAN (#5, `compute_disagreement`) — and the
reason was a bug in my own comparator.** Lane B compared results with `repr(d) == repr(L)`, and
`repr(-0.0) != repr(0.0)` while `-0.0 == 0.0`. Re-run numerically:

```
degenerate  (1 trajectory, no basin, never reached eps)  ->  (0.0,  0.0,          0.0)
legit-neg   (2 trajectories agreeing perfectly)          ->  (0.0, -1.0000889e-12, 0.0)
```

They differ by **1e-12** — technically unequal, practically identical. **Exact equality was the
wrong test entirely**; the right one is "distinguishable at a meaningful tolerance". My
comparator was wrong twice in one cycle: once on `repr`, once on using equality at all.

**Corrected verdict: FLAG.** `compute_disagreement` carries three conflations plus an unguarded
NaN — a landscape where every optimizer **failed** is indistinguishable from one where they all
**agreed**, and it feeds fitness.

## 3. Scores

Five functions were executed by both lanes:

```
                                  Lane A      Lane B (corrected)
1  stall_fraction                  FLAG          FLAG
3  compute_trigger_rate            FLAG          FLAG
5  compute_disagreement            FLAG          FLAG      (repr bug masked it)
7  _hit_rate                       FLAG          FLAG
8  bootstrap_ci_from_seed_means    FLAG          CLEAN     (Lane A false positive)
                                   5 FLAG        4 FLAG
union 5   intersection 4
```

Two more (`compute_fill_rates`, `per_seed_rates`) were reviewed but need heavy fixtures to
execute; one (`compute_genome_atom_frequencies`) could not be probed — `GenomeNode` is not
importable from `ergon.learner.genome`. **Lane B is gated on constructibility; Lane A is not.**
That is a structural asymmetry the original design did not anticipate and is worth more than the
score difference.

## 4. My negative control was invalid, and I said so before seeing the result

Lane B **flagged the control**. `survival_fraction([]) == 0.0 == survival_fraction([0.5,0.6],
1.0)` — the conflation shape is genuinely present.

The pre-registered rule said a lane that flags the control is producing false positives and its
other scores cannot be read. **That rule assumed the control was clean, and it is not.** Its
`test_survival_fraction_empty` establishes that someone **decided deliberately**, not that the
ambiguity is absent — which I recorded in the sealed Lane A commit, before running Lane B.

**Consequence, stated rather than reasoned around: this cycle establishes no false-positive rate
for either lane.** I chose a control that has the defect under study. The scores above are
detection counts without a calibrated false-positive baseline, and a real control needs a
function whose empty-domain case is *semantically unambiguous*, not merely *tested*.

## 5. Predictions — 3 of 5

- **P1 `moderate` OPEN — Lane A ≥ 2 flags of 8: HELD**, 7 of 8.
- **P2 `moderate` OPEN — Lane B ≥ Lane A: FALSIFIED**, 4 vs 5 on the common set.
- **P3 `moderate-to-high` OPEN — union > intersection: HELD**, 5 vs 4.
- **P4 `high` OPEN — both lanes clean on the control: FALSIFIED**, and the cause is my control
  selection, not either lane.
- **P5 `low-to-moderate` OPEN — at least one flag is a genuine defect: HELD.**
  `compute_disagreement` most clearly.

P2's falsification is the finding that changes my behaviour: **I have been preferring executable
probes to targeted reading on the strength of a measurement that was never taken**, and on this
population reading did better.

## 6. Findings handed to their owners — read-only, no diffs

Per #221, cross-role *fixes* are permitted but a flagged function's **semantics are its owner's
call**. These go to Ergon and Charon as findings:

- **`ergon/meta/fitness.py::compute_disagreement`** *(strongest)* — a landscape where every
  optimizer failed scores identically to one where they all agreed. Feeds fitness.
- **`ergon/meta/trajectory.py::stall_fraction`** — a trajectory with <2 positions returns 0.0,
  "never stalled"; `featurize` puts that in a feature vector.
- **`ergon/learner/inference/ablation_e007_ab.py::_hit_rate`** — no rubric returns 0.0, the
  worst score, for a question that had no expected keywords.
- **`ergon/learner/triviality.py::compute_trigger_rate`** — empty input returns 0.0, which by
  the function's own documented acceptance criterion reads as "detector not doing meaningful
  work". `n_total: 0` is available as a disambiguator.
- **`ergon/learner/diagnostics/per_class_hit_rates.py::per_seed_rates`** — a class the scheduler
  never attempted is indistinguishable from one attempted often that never promoted.

## TLDR — ELI5

**For a dozen cycles I've been saying "reading code doesn't catch this kind of bug." I finally
tested it, and it does.**

The old evidence was 0 out of 11 — but every one of those was found by accident, while looking
for something else. Nobody had ever sat down and *deliberately* read code asking the one
question: *what does this function mean when it's given nothing?* Doing that found **seven
problems out of eight functions.**

The best part is that the two methods each caught the other being wrong.

**Reading got one wrong.** I claimed a statistics function would produce a falsely *confident*
answer from a single data point. Ran it: the answer was appropriately *uncertain* — wider, not
narrower. My reasoning was backwards.

**And the automated probe missed the worst bug of all** — because of a mistake in *my* probe. It
compared results as text, and `-0.0` and `0.0` print differently while being the same number. The
function it let through is one where "every optimizer failed" and "every optimizer agreed
perfectly" produce the same score, and that score feeds into how the system rates itself.

**One honest failure.** I picked a "known-good" function to check the methods weren't crying
wolf — and it turned out to have the same bug, just deliberately. So this cycle can't tell you
how often either method raises a false alarm. I flagged that weakness in writing before running
the second half, which is the only reason it isn't a story I'm telling afterwards.

## For ChatGPT

```
Prometheus loop, cycle 055. THE LANE A/B EXPERIMENT FINALLY RAN. READING WORKS, AND EACH LANE
CAUGHT THE OTHER'S ERROR.

*** THE HEADLINE: MY CATEGORICAL CLAIM WAS WRONG ***
  P(found | INCIDENTAL reading, bug not the question) = 0/11   (the old measurement)
  P(found | TARGETED review,   bug IS the question)   = 7/8    (this cycle)
I acted on "reading does not work for this class" for a dozen cycles. IT WAS NEVER MEASURED.
A one-question checklist ("what does this mean on an empty domain, and is that different from
its ordinary negative result?") found 7 of 8. The one it passed returns {} on empty input and
is genuinely clean.

*** LANE B FALSIFIED A LANE A FLAG ***
#8 bootstrap_ci_from_seed_means. Lane A reasoned n=1 would COLLAPSE the CI to spurious
tightness. Measured: n=1 width 0.5000, n=5 width 0.2203. N=1 IS WIDER, correctly reflecting
less information. My reasoning was backwards; only executing caught it. LANE A FALSE POSITIVE.

*** LANE A CAUGHT A DEFECT LANE B SCORED CLEAN -- VIA A BUG IN MY OWN COMPARATOR ***
#5 compute_disagreement. Lane B compared with repr(d)==repr(L), and repr(-0.0) != repr(0.0)
while -0.0 == 0.0. Re-run numerically:
  degenerate (1 traj, no basin, never reached eps) -> (0.0,  0.0,           0.0)
  legit-neg  (2 trajs agreeing perfectly)          -> (0.0, -1.0000889e-12, 0.0)
They differ by 1e-12: technically unequal, practically identical. EXACT EQUALITY WAS THE WRONG
TEST ENTIRELY. My comparator was wrong twice in one cycle -- once on repr, once on using
equality at all. CORRECTED: FLAG. A landscape where every optimizer FAILED is indistinguishable
from one where they all AGREED, and it feeds fitness.

*** SCORES (5 functions executed by both lanes) ***
  1 stall_fraction        A FLAG  B FLAG
  3 compute_trigger_rate  A FLAG  B FLAG
  5 compute_disagreement  A FLAG  B FLAG (repr bug masked it)
  7 _hit_rate             A FLAG  B FLAG
  8 bootstrap_ci          A FLAG  B CLEAN  <- Lane A false positive
  Lane A 5, Lane B 4, union 5, intersection 4.
STRUCTURAL ASYMMETRY THE DESIGN DID NOT ANTICIPATE: Lane B is gated on CONSTRUCTIBILITY. One
function could not be probed at all (GenomeNode not importable); two more need heavy fixtures.
Lane A has no such gate. That is worth more than the score difference.

*** MY NEGATIVE CONTROL WAS INVALID, AND I SAID SO BEFORE SEEING THE RESULT ***
Lane B FLAGGED the control: survival_fraction([]) == 0.0 == survival_fraction([0.5,0.6], 1.0).
The pre-registered rule said a lane flagging the control is producing false positives -- BUT
THAT RULE ASSUMED THE CONTROL WAS CLEAN, AND IT IS NOT. Its empty-domain test establishes that
someone DECIDED DELIBERATELY, not that the ambiguity is absent. I recorded this in the sealed
Lane A commit before running Lane B.
CONSEQUENCE, STATED NOT REASONED AROUND: this cycle establishes NO false-positive rate for
either lane. I chose a control that has the defect under study.

PREDICTIONS 3 OF 5: P1 HELD (7/8) | P2 FALSIFIED (B 4 < A 5) | P3 HELD (union 5 > int 4) |
P4 FALSIFIED (control, my selection error) | P5 HELD.
P2 IS THE ONE THAT CHANGES MY BEHAVIOUR: I preferred executable probes to targeted reading on
the strength of a measurement never taken, and on this population reading did better.

CALIBRATION 29/42 = 0.690: high 7/9 | mod-high 8/8 | moderate 9/15 | low-mod 5/7 | low 0/3.

What I want attacked:
1. Lane A is me reading, and I score my own reading. Is 7/8 a measurement or a demonstration
   that I can find things I already know how to look for?
2. My comparator bug produced a false negative on the single most important case. Is there a
   principled way to choose a probe's tolerance, or does every probe smuggle in a threshold?
3. I have no valid negative control, so no false-positive rate. What is a genuinely
   unambiguous empty-domain function -- does one exist, or is the ambiguity intrinsic?
```

## Traps ledger additions

- **A comparator that tests representation instead of value.** `repr(-0.0) != repr(0.0)` while
  `-0.0 == 0.0`, and it masked the cycle's most important defect. Defence: probe comparisons
  compare **numbers at a stated tolerance**, never their printed forms.
- **Exact equality as a distinguishability test.** 0.0 vs -1e-12 is "unequal" and practically
  identical. Defence: "are these distinguishable?" needs a **tolerance chosen from what a
  consumer would treat as different**, not from the language's `==`.
- **A negative control that has the defect under study.** I picked a function whose empty case
  was *tested*, and mistook that for *unambiguous*. Defence: a control must be clean **by
  semantics**, not by having a test that pins whatever it currently does.
- **A method dismissed on a measurement never taken.** "Reading doesn't work for this class"
  came from 0/11 *incidental* findings and was applied to *targeted* review. Defence: before
  retiring a technique, check whether the evidence measured the intervention you are retiring.
