# Cycle 021 — 2026-08-21 — CANON R12, and the end of the first pass

**Track 2: canon R12 — generative conjecture / research.** The last unbuilt rung.
**I did not build a grader. I ran the one that was already there**, and audited it.

268 green (251 in the loop suites, 17 in harmonia's own R12 tests).

## First job: the grader canon §7 says was never run

It exists. `harmonia/experiments/` — `r12_grader.py` (615 lines), `r12_universe.py` (440),
`run_r12.py` (347), `test_r12.py` (349). All 17 unit tests pass. The offline runner executes,
and it discriminates exactly as its design intended:

```
good      conjecture-quality 0.238–0.526   holdout 1.000   exact_partition   test eff 1.000
overfit   conjecture-quality 0.000                                           test eff 0.566–0.647
naive     conjecture-quality 0.000                                           test eff 0.000
```

It is a genuinely good instrument: no free-text judging anywhere, a safe AST-restricted
conjecture compiler, version-space information gain for test quality, and a baseline penalty on
the conjecture channel that correctly zeroes both degenerate arms. Endorsed by four reviewers
and never executed — and executing it took one command.

So this cycle's artifact is `canon_r12_conjecture.py`: **an audit**, not a second grader.

## Finding 1 — the two channels are asymmetrically defended

Conjecture-quality is baseline-penalised: a conjecture no better than a naive baseline scores
zero, which is why both the overfit and naive arms collapse. Test-quality is not. It reports
`info_gain / optimal_gain` with nothing subtracted.

Measured, proposing a **fixed universe object chosen without looking at anything**, over five
seeds: efficiencies 0.000, 0.566, 0.647, **1.000**, 0.000 — mean **0.443**, and full marks on
one trial in five. That is precisely what the overfit arm banks while scoring zero on
conjectures: ~0.6 bits for a probe with no reasoning behind it.

This is not a flaw in the information theory, which is correct. It is a missing baseline on one
of two channels, in a grader whose other channel has one. Nobody could have seen it without
running it.

## Finding 2 — the canon's own kill test IS an aliasing statement

Canon's R12 kill is *"a small closed universe (graphs ≤ 8, short sequences)"*. Restated with
the cycle-018 instrument, that is exactly: **the projection is not sufficient for the target.**

Three conjectures — `True`, `x <= 7`, `s <= 14` — accept all 64 objects of the 0..7 universe.
Byte-identical to any grader confined to it. Widen to 0..15 and they accept 256, 128 and 120 of
256. The witness is not subtle; it is the rung's entire hazard, and the canon named it in
English three months before the instrument existed to state it formally.

**And it is unbreakable from inside** — R11's shape, not R6/R9/R10's. Extension over the graded
universe is already everything observable there; widening is not a sharper instrument, it is a
different experiment. That answers **HITL #53**: R11 and R12 are both impossibility-defined
rungs, and the distinction between those and the capability-defined rungs (R0–R10) is real.

## Finding 3 — claim v13 at its sharpest

R12 generates its own candidate list, so the pre-declared-ledger problem bites hardest here. A
generator that internally draws N conjectures consistent with the revealed data and reports its
best publishes a record in which **nothing is false** — the candidate really is consistent, the
score really is that candidate's score. What is absent is the other N − 1 attempts.

Mean inflation over five seeds: **+0.042 (N=2), +0.098 (4), +0.129 (8), +0.173 (16), +0.188
(32)**, against honest means near 0.2. Best-of-32 roughly doubles the reported score, and the
emission carries no N. Monotone, as it must be, and undeclarable by anything internal to the
record.

## Track 1

Subsumed, honestly. Running a 1,751-line never-executed experiment and finding a defect in it
was worth more than another `prometheus_math` primitive, and I am recording that as a choice
rather than as an omission. No new primitive this cycle.

---

# The first pass is complete: canon rungs R0–R12

Twenty-one cycles. Every canon rung now has circuits, a kill test, traps, and a green suite —
R12 by audit rather than construction, which is the right relationship to work that already
existed.

**What the pass actually produced.** Thirteen claims, of which the durable ones are: the
competitor-relative law (v2, after external review killed v1), evaluator aliasing (v11′, with
its factorization precondition and its first counterexample at R11), evidence typing with an
external checker (v12), and the un-detectability of omission (v13). Roughly twenty executable
kill batteries. Three doctrine proposals still unratified. One self-caught 13-cycle rung
mislabelling. One shipped repair that was wrong and lasted a cycle until review caught it.

**What it did not produce, and this is the important part.** Every battery in this pass is
synthetic. Per `feedback_instrument_vs_architectural_pass`, that makes the whole first pass
**instrument calibration, not architectural validation**. The circuits are toys by design and
they did their job — but no rung has yet been pointed at Theseus, the metabolization probe, or
the signature index.

## What the second pass should optimise for

In priority order, and I would like a ruling on the ordering.

1. **A uniform instrument sweep first, because it is cheap.** The three instruments — aliasing,
   evidence typing, external audit — were discovered at cycles 018–019 and only retrofitted to
   the rungs that happened to be nearby. R0–R5 and R7–R8 have never been through any of them.
   R3's capacity width is still carried in the ledger as an unverified claim. Expect defects:
   every rung that has been swept so far has yielded one.

2. **Composition, not depth.** Every rung was built in isolation, and a system that passes
   R0–R12 individually has not been shown to pass them composed. The interesting failures in
   Prometheus have always been at seams. This is the largest untested surface the pass created.

3. **One rung against real substrate.** Convert a single rung — R6 falsification is the natural
   candidate, since canon calls it "the battery's own discipline, miniaturised" — from a
   synthetic battery to one drawn from the metabolization probe's actual residue. That converts
   the pass from calibration to validation for exactly one rung, which is the honest unit of
   progress.

4. **Force the three doctrine rulings.** The immutable-observation constitution now has three
   independent arguments (circular legitimisation, un-auditable UNKNOWN, un-detectable
   omission) and a concrete mechanism requirement. It should stop being a proposal.

## TLDR — ELI5

The last rung already had a grader written for it, reviewed and approved by four people, and
never once run. I ran it. It works. Then I poked at it three ways.

First: it scores two things, and it's careful about one and not the other. It correctly gives no
credit for a "rule" that's no better than a dumb guess — but for the follow-up experiment you
propose, it gives credit even when the experiment was picked at random. I measured a randomly
chosen experiment scoring full marks on one trial in five.

Second: the warning written in our own rulebook — "don't test this inside a tiny closed world" —
turns out to be exactly the same problem we've been chasing all month, under a different name.
Three different rules look identical if the world only has 64 things in it, and immediately
differ when it has 256.

Third, and worst: whoever's being graded gets to pick what to submit. Try thirty-two guesses
privately, submit your best, and your score roughly doubles — without a single false statement
anywhere in what you handed in.

That finishes a full lap of all thirteen rungs. Everything so far has been calibrating the
instruments on toy problems. The next lap has to point at least one of them at something real.

## For ChatGPT

```
Prometheus loop, cycle 021. Canon R12 = generative conjecture. Canon 7 recorded its grader as
"built, unit-tested, endorsed by all four frontier reviewers, NEVER RUN". My instruction was to
find it before writing anything.

IT EXISTED AND I RAN IT. harmonia/experiments/r12_grader.py, 615 lines, plus a universe builder,
a runner and 17 unit tests, all green. It is a good instrument: no free-text judging, an
AST-restricted safe conjecture compiler, version-space information gain for test quality, and a
baseline penalty on the conjecture channel. Offline it discriminates good (quality 0.238-0.526,
exact partition) from overfit (0.000) from naive (0.000). So I audited it instead of building a
second one. Three findings.

1. ASYMMETRIC DEFENCE. Conjecture-quality subtracts a baseline; test-quality does not, it just
reports info_gain / optimal_gain. Measured with a FIXED probe object chosen without looking at
anything, over 5 seeds: 0.000, 0.566, 0.647, 1.000, 0.000 — mean 0.443, full marks on one trial
in five. That is what the overfit arm banks while scoring zero on conjectures. The information
theory is correct; one of two channels is simply missing the baseline the other has.

2. THE CANON'S OWN KILL TEST IS AN ALIASING STATEMENT. Canon says "kill: a small closed
universe". Formally that is "the projection is not sufficient for the target". True, x<=7 and
s<=14 all accept 64/64 objects of the 0..7 universe and accept 256, 128, 120 of 256 on 0..15.
And the witness is UNBREAKABLE from inside — extension over the graded universe is already
everything observable there. So R11 and R12 are both impossibility-defined rungs and R0-R10 are
capability-defined. That was an open question of mine (whether rungs come in two kinds); I now
think yes.

3. CLAIM v13 AT ITS SHARPEST. R12 generates its own candidates, so best-of-N is available.
Mean inflation over 5 seeds: +0.042 (N=2), +0.098 (4), +0.129 (8), +0.173 (16), +0.188 (32),
against honest means near 0.2. Best-of-32 roughly doubles the reported score with nothing false
in the emission and no N declared anywhere.

THIS COMPLETES A FULL PASS OF R0-R12. Honest assessment: every battery in the pass is synthetic,
so the whole thing is instrument calibration, not architectural validation. No rung has been
pointed at real substrate yet.

What I want attacked, mostly about the SECOND pass:
1. My proposed second-pass ordering is (a) sweep all rungs with the three instruments, since
   every rung swept so far yielded a defect; (b) test COMPOSITION, since every rung was built in
   isolation and Prometheus's real failures have always been at seams; (c) convert ONE rung to
   real substrate; (d) force the three doctrine rulings. Is that the right order? My worry is
   that (a) is cheap and productive and could absorb the whole second pass while (c) is the one
   that actually changes what we know.
2. On the asymmetric-defence finding: is a baseline subtraction even the right fix for the test
   channel? The natural baseline is "expected info gain of a uniformly random probe", but that
   is a distribution over probes rather than a named competitor, which is not how the conjecture
   channel's baseline works. Is there a principled way to make the two channels symmetric, or
   are information-gain scores and similarity scores just not baseline-correctable in the same
   way?
3. Best-of-N: is declaring N sufficient? A generator could declare N=1 and simply have run 32
   times in a previous session. That pushes the problem into session identity and makes the
   pre-declared ledger have to span time, not just a single emission. I suspect this is the
   real content of the immutable-observation constitution and that I have been treating it as
   more abstract than it is.
```

## Traps ledger additions

- **Unsubtracted-baseline channel** — a multi-channel grader that baseline-corrects one channel
  and not another. The undefended channel is where a gaming system parks. Defence: audit every
  channel for its own no-reasoning floor, measured rather than assumed.
- **Closed-universe overfit** — indistinguishable conjectures inside the graded universe.
  Defence: widen the universe; it is a different experiment, not a sharper instrument.
- **Best-of-N reported as one draw** — monotone score inflation with N, nothing falsified.
  Defence: declare N in the emission, and hold the declaration in an external ledger that spans
  sessions (a declared N is only as good as the session boundary it is declared within).
