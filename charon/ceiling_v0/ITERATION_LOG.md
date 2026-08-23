# Iteration log

**THIS FILE IS A RECONSTRUCTION.** The original was destroyed in the 2026-08-22
08:33 data-loss event; see `RECOVERY.md`. Iterations 1-9 are summarised from the
session transcript rather than copied from the original file, and the numbers
below are those reported at the time. Deterministic results are re-derivable by
re-running; the model results are not.

---

## Iterations 1-9, condensed (reconstructed)

**Arena.** Hidden state Z_3^3 (27 states), 4 opaque actions each a hidden shift,
4 entry tags, lossy 4-symbol sensor. One command, `RUN <tag> <1..6 items>`,
returning len+1 readouts. Held-out queries are length 8-12, longer than anything
any arm may run. Chance 0.25. The actions generate a 27-element commutative
group; that is never named in any prompt and a leakage scan enforces it.

**Deterministic results, 20 universes, byte-reproducible.**

```
chance 0.239 | P3c simple proposer 0.364 | P3b algorithmic 0.483
P3d relevance-ranked proposer 0.647 | oracle rule-set ceiling ~0.93
```

Ablations: rules-alone 0.254, memo-alone 0.254, together 0.364 — neither half
works without the other. A store from a *different* universe still fires on 13%
of queries but scores 0.265, so artifacts carry universe-specific content rather
than prompt format. Deleting the 9 most-used rules costs 0.088, 9 random 0.042,
9 least-used 0.000. Six planted false rules are removed by re-testing within two
rounds and the poisoned run reconverges on the clean one.

**Funnel.** Driver changed from surprise to incompleteness (`I -> D -> R -> B -> G`)
because a verification-gated store is never wrong, only ignorant: ~2,040
commitments across 20 universes with zero errors. Contradiction rate survives as
a separate integrity axis and correctly fingered one universe holding 2
false-accepted rules.

**Verifier strength.** 3 vs 5 contexts: 5 improves every per-rule quality measure
and still *costs* 6.7 accuracy points at fixed budget, because volume dominates.
3 stands; recorded as a frontier measurement, not adopted.

**Inductive-bias sensitivity.** Compression ranking is the *worst* firing-aware
ranking (0.647) — coverage 0.710, novelty 0.713, anticompression 0.703, support
0.519. The operative variable is expected firing, not length reduction, which
killed the "commutative-group whispering gallery" worry.

**Model results (one usable lane window, 8 iterations of trying).** Under C0
(claims optional) the frozen llama-3.3-70b emitted 1 claim in 39 turns across two
different lanes. Under forced generation it emitted on 29/29 turns; Fisher
p = 3.8e-09. **The C0 zero was reluctance, not inability.** Stripping the
incentive from the forcing wording (C1 vs C1N) changed nothing — C1N emitted
more — so this is not instruction-following-with-a-bribe. Truth rate of forced
claims 4/37 = 10.8% against a 3.7% random baseline; one-sided p = 0.047 with a
95% CI of [0.008, 0.208] that contains the baseline. Suggestive, underpowered,
not established.

**Sufficiency (iteration 9).** Even a perfect proposer reaches only ~0.37 at the
control's emission rate — but see iteration 10, which found this number was
confounded.

---

## Iteration 10 — 2026-08-22 — mechanism partly refuted, own tool found confounded,
## then the working tree was destroyed

**Lane:** openrouter 402, nvidia timeout. No model calls.

**Committed test.** Iteration 9 asserted, without isolating it, that P3d's
advantage comes from *dynamic relevance* — ranking candidates by expected firing
on long words **after the rules already held have been applied** — rather than
from static relevance to raw query patterns. I said I would test it directly.

**Result: partly confirmed, and insufficient.** Sampling candidate left-hand
sides from the normalised population instead of raw queries:

```
3 claims/turn, true-rate 1.00   static relevance   0.374   D->R 0.62
3 claims/turn, true-rate 1.00   dynamic relevance  0.414   D->R ~1.00
1.5 claims/turn, true 1.00      dynamic relevance  0.417
```

Dynamic relevance **completely solves the D->R bottleneck** — every surviving rule
fires, up from 0.304 — and moves accuracy by only ~0.04. It does not come close
to P3d's 0.647. So the iteration-9 mechanism claim is **withdrawn as stated**:
dynamic relevance explains the firing bottleneck but not the accuracy gap.

**And the sweep exposed a confound in my own analysis tool.** `proposed` collapses
from ~60 at low true-rate to ~16 at 100%, because the true-claim generator kept
regenerating claims the store already held and `submit_rule` silently dropped them
as duplicates. The "perfect proposer" was therefore proposing four times *less*
than the others. **Iteration 9's headline — "even a perfect proposer only reaches
0.37" — was measuring generator saturation, not a ceiling, and must not be
quoted.** A proposal-count-matching fix was written and was destroyed before it
could run.

**Then the working tree was deleted.** Every source file, both pre-registered
SPECs, the original iteration log, the README, and every run directory. Full
forensics in `RECOVERY.md`. Surviving: `runs/*.log` (including all 48 emission
turns), `__pycache__` for 11 modules, and the published report artifact.

The directory was **untracked, not ignored** — `git status` shows `?? charon/ceiling_v0/`.
Nine iterations of work had never been committed. The experiment carried
pre-registration hashing, memo provenance, validity flags, leakage scans and 79
guard tests, and none of them guard the one failure mode that actually occurred.

---

## Iteration 11 — 2026-08-22 — restoration, verified against the pre-loss numbers

**Lane:** not retried. Nothing could have used it; there was no code.

**Restored from the session transcript**, cross-checked against surviving
`__pycache__` docstrings and symbol tables: `universe.py`, `substrate.py`,
`policy.py`, `baselines.py`, plus a new `config.py`.

**One structural change, made deliberately and flagged.** `ArmConfig` moved from
`arms.py` to `config.py`. It previously forced `baselines.py` to import the
entire LLM-arm module just to read a budget, which meant the deterministic half
could not run without the model half. Now it can — which is exactly why the
deterministic suite could be restored and verified before any model-facing code
exists.

### Fidelity check — the only thing that makes a restoration trustworthy

Re-ran the 20-universe deterministic suite and compared against the numbers
recorded before the loss:

```
                 restored   recorded
chance              0.239      0.239   MATCH
majority            0.330      0.330   MATCH
P3c-random          0.259      0.259   MATCH
P3c-datadriven      0.364      0.364   MATCH
P3d relevance       0.647      0.647   MATCH
P3b algorithmic     0.476      0.483   off by 0.007
```

**Five of six reproduce exactly**, including every arm that runs through the
substrate. That is strong evidence `universe.py`, `substrate.py`, `policy.py` and
the proposers are faithful: the substrate pipeline is long and chaotic, and an
error anywhere in it would not land on 0.364 and 0.647 by accident.

**P3b does not reproduce exactly and I have not fully isolated why.** It is the
one arm that bypasses the substrate. Ruled out: majority-fallback tie-breaking
(0/20 universes have a tied top-2 readout count, and both tie-break rules give
identical results). A standalone reimplementation of the same algorithm gives
0.4725, a further 0.0035 from the restored arm's 0.476, so the residue is in
probe-consumption bookkeeping rather than in the automaton.

Context that matters: **P3b was never stable across pre-loss revisions either** —
it read 0.467 in `base20`, 0.471 and 0.483 in the two `b2_p3d` tables. The
restored 0.476 sits inside that band. So this is drift in an already-drifting
arm, not evidence the restoration is wrong. Recorded as an open defect, not
resolved.

**Still missing:** `arms.py`, `prompts.py`, `reasoner.py`, `c4.py`, `lanes.py`,
`metrics.py`, `run.py`, `ablations.py`, `analyze.py`, `build4.py`,
`emission.py`, `sufficiency.py`, `tests/test_all.py`, `README.md`, and both
pre-registered SPECs. The guard suite does not currently exist, so the standing
instruction "tests must stay green" cannot be honoured this iteration — there is
nothing to run.

**Still uncommitted.** `charon/ceiling_v0/` remains untracked. I asked whether to
commit and have had no answer, and the standing rule is to commit only when
asked, so the restored tree is currently as vulnerable as the one that vanished.

---

## Iteration 12 — 2026-08-22 — guard suite restored; the P3b "drift" was a real bug

**Lane:** openrouter served a 3k-char payload in 3s. Not usable — no model-facing
module exists yet, so a working lane changes nothing about the priority.

**Restored:** `metrics.py` (the I->D->R->B->G funnel and generalisation distance)
and `tests/test_all.py`. The suite now covers determinism, eval sealing, budget,
artifact hygiene, ignorance-vs-error, verifier soundness, the solvable ceiling,
wrong-artifact removal, whole-pipeline reproducibility, and a **frozen reference
for every arm** so a future restoration can be checked the way this one was.

### The P3b discrepancy was not restoration drift. It was a latent bug.

Iteration 11 recorded P3b at 0.476 and called the 0.007 gap unexplained drift in
an arm that had "always been unstable". Running the identical restored code again
this iteration gave **0.4700**. Same code, same seeds, different answer.

Cause: `SignatureAutomaton.build()` iterated `{w for (_, w) in self.obs}` — a set
of string tuples. **Python randomises string hashes per process**, so set order
varied between runs, changing insertion order into `sigs`, which changed
`Counter.most_common` tie-breaking in `votes`, which changed the transition table
and the final accuracy.

Every P3b figure this experiment ever published — 0.467, 0.471, 0.483 before the
loss, 0.476 and 0.470 after — was a sample from a hash-order-dependent
distribution, not a measurement of different code. **My iteration-11 diagnosis was
wrong**, and the convenient conclusion I flagged at the time ("exact agreement on
five arms outweighs one drift") happened to be right for the wrong reason.

Fixed by sorting the word set and breaking `Counter` ties on (count, lexical).
P3b now reads **0.475** identically across three separate processes.

**The whole-pipeline determinism guarantee never covered this.** The existing test
re-ran the pipeline *inside one process*, where the hash seed is constant, so a
cross-process hazard was invisible to it. Added `test_cross_process_stability`,
which runs an arm under three different `PYTHONHASHSEED` values in subprocesses
and asserts identical output. The substrate arms pass it — they were already safe,
because their proposers sort candidates into a total order before use, which is
why P3c and P3d reproduced exactly while P3b did not.

**Frozen references now guarded** (20 universes, 6 rounds): chance 0.239,
majority 0.330, P3c-random 0.259, P3c-datadriven 0.364, P3d 0.647, P3b 0.475.
All pass.

**Still missing:** `arms.py`, `prompts.py`, `reasoner.py`, `c4.py`, `lanes.py`,
`run.py`, `ablations.py`, `analyze.py`, `build4.py`, `emission.py`,
`sufficiency.py`, `README.md`, and both SPECs. Leakage and ladder guards return
with the prompts they scan.

**Still uncommitted.** Asked twice now.

---

## Iteration 13 — 2026-08-22 — SPECs reconstructed; ablations reproduce exactly

**Lane:** not retried; no model-facing module exists to use one.

**SPECs reconstructed first, deliberately.** I flagged last iteration that a
reconstructed pre-registration written later is more suspect the longer it is
delayed, and that argument gets worse every iteration, so this took priority over
more code. Both files carry a RECONSTRUCTED banner stating plainly that **no hash
survives**, that the only attestation is the verbatim quoting of falsifiers in
progress reports before the corresponding results existed, and that this is
weaker than a hash. Explicit instruction in the banner: **report Build 1 and
Build 2 results as exploratory-with-attestation, not as cryptographically
pre-registered.**

Where a later iteration overturned something, the original text stands and the
change is recorded elsewhere — F7's demotion from falsifier to branch condition
is noted inline in `SPEC.md` without altering the original falsifier text.

`SPEC_BUILD2.md` also now carries a section 9 of known-open items, so the two
unresolved problems travel with the spec rather than only living in the log:
P3d's 0.647 is unexplained, and reproducibility is a property of code that sorts.

**`ablations.py` restored and re-run — second independent fidelity check.**
Every recorded ablation number reproduces to three decimals:

```
                                 restored   recorded
intact store              acc       0.364      0.364    cov 0.140 / 0.140
A2 memo only              acc       0.254      0.254
A3 rules only             acc       0.254      0.254
A4 foreign-universe store acc       0.265      0.265    cov 0.131 / 0.131
A5 delete most-used       acc       0.276      0.276
A5 delete random          acc       0.322      0.322
A5 delete least-used      acc       0.364      0.364
A5 restored               acc       0.364      0.364
rules deleted / held                9 / 46     9 / 46
```

Nine independent quantities, all exact. Combined with iteration 12's five exact
arm references, the deterministic half is now confirmed faithful by fourteen
separate numbers. The substrate findings stand: neither rules nor memo works
alone; a foreign store still fires on 13% of queries while scoring at fallback,
so artifacts carry universe-specific content rather than prompt format; and damage
scales with how load-bearing the deleted rules are.

**Guards still green.** No new test added for ablations: the frozen-reference test
already re-runs 20 universes and adding a second full sweep would roughly double
suite runtime for a check that `ablations.py` performs on demand. Recorded here as
a deliberate omission rather than left implicit.

**Still missing:** `arms.py`, `prompts.py`, `reasoner.py`, `c4.py`, `lanes.py`,
`run.py`, `analyze.py`, `build4.py`, `emission.py`, `sufficiency.py`, `README.md`.
Leakage and ladder guards return with the prompts they scan.

**Still uncommitted.** Asked three times.

---

## Iteration 14 — 2026-08-22 — oracle audit; a false rule costs ~15x its own weight

**Lane:** not retried; still no model-facing module to use one.

**Motivation, from my own open question.** Restoration had been verified by
reproducing fourteen recorded numbers exactly. That is strong evidence the code
was restored FAITHFULLY and no evidence at all that it is CORRECT — deterministic
code reproducing itself proves self-consistency, and a restored bug reproduces
perfectly. So `validate.py` checks the implementation against the mathematics:
every expectation is derived from the definition of the universe (translations on
Z_3^3 seen through a lossy sensor), never from anything the pipeline emitted.

**It immediately found something the fourteen reproductions could not.**

```
universe conforms to definition        4/4 checks pass, 20 universes
held-out answers recomputed            800/800 match an independent computation
normalisation preserves meaning        119 of 4000 VIOLATIONS
accepted rules are true identities     7 false of 930 surviving (0.8%)
committed predictions correct          1 wrong of 112 commitments (0.9%)
budget and held-out isolation          pass
```

**Diagnosis, and it is clean.** Splitting by whether the store held a
false-accepted rule:

```
15 universes with NO false rule   0 / 3000 violations   (0.0%)
 5 universes WITH a false rule  119 / 1000 violations  (11.9%)
unattributed violations            0  (every one had a false rule fire)
```

The normaliser is **provably sound**: rewriting preserves the hidden group element
whenever every rule it uses is true, with zero exceptions in 3000 trials. Every
violation is downstream of the verifier admitting something false. The audit now
asserts that conditional property plus attributability, rather than an
unconditional soundness it can never have.

**The new quantitative finding: false rules amplify badly.** A 0.8% false-accept
rate among surviving rules corrupts **11.9%** of long-word normalisations in the
universes that catch one — roughly fifteen times its own weight. A length 8-12
word passes through many rewrite steps and only has to touch one bad rule to lose
its meaning.

That materially reframes iteration 4's verifier-strength decision. Raising
verification from 3 to 5 contexts was rejected because it costs 6.7 accuracy
points at fixed budget, on the reasoning that the extra precision bought little.
The cost of staying at 3 is not "a few bad rules" — it is a ~12% meaning-
corruption rate in a quarter of universes. The decision is not obviously wrong,
because the accuracy measurement is the outcome that matters, but it was made
without this number and should be revisited with it.

**Guards still green.** `validate.py` is a separate audit rather than part of the
suite: it re-runs 20 universes several times over and would dominate suite
runtime. Recorded as a deliberate split, to be run on demand and after any change
to the verifier or normaliser.

**Still missing:** `arms.py`, `prompts.py`, `reasoner.py`, `c4.py`, `lanes.py`,
`run.py`, `analyze.py`, `build4.py`, `emission.py`, `sufficiency.py`, `README.md`.

**Still uncommitted.** Asked four times.

---

## Iteration 15 — 2026-08-22 — P3d explained, and the explanation deflates it

**Lane:** openrouter 402, nvidia timeout.

**The question.** Why P3d reaches 0.647 where P3c reaches 0.364 has been open since
iteration 9, with two explanations proposed and both withdrawn: static relevance
to raw query patterns (refuted, 0.374) and dynamic relevance to normalised words
(refuted, 0.414, and its perfect-proposer comparison was confounded by generator
saturation). Both were about WHICH RULES get proposed. `mechanism.py` tests a
different hypothesis, at the level of the group.

**Result 1 — accuracy is entirely coverage.** The substrate answers a query only
when normalisation lands it on a canonical form the memo already holds, so
`accuracy ~ coverage + (1 - coverage) * fallback_accuracy` should hold exactly.
It does:

```
arm            measured  predicted  residual  fallback
random            0.259      0.263    -0.004     0.251
datadriven        0.364      0.357    +0.007     0.254
relevance         0.647      0.653    -0.005     0.244
```

Residuals under one point. There is no second mechanism.

**Result 2 — coverage is driven by canonical LENGTH, and nothing else.** Across
seven arms spanning 0.259 to 0.713:

```
arm                        canon len  coverage  accuracy  rules
random                          8.84     0.015     0.259    2.6
datadriven                      6.16     0.140     0.364   46.5
relevance:support               4.58     0.403     0.519   47.1
relevance:compression           4.24     0.545     0.647   24.1
relevance:coverage              4.03     0.606     0.710   22.0
relevance:novelty               3.94     0.626     0.713   22.5
relevance:anticompression       3.84     0.633     0.703   21.8

correlation, mean canonical length vs coverage:  r = -0.944
```

Perfectly monotone in length. Rule COUNT is irrelevant — `support` holds 47 rules
and scores 0.519 while `anticompression` holds 22 and scores 0.703.

**The mechanism, stated plainly.** The memo is harvested from prefixes of probes
of length <= 6, so it only ever contains SHORT canonical forms. An arm's accuracy
is therefore just how far down the length scale its rewriting can drive a
length-8-12 query. P3d is not acquiring high-leverage abstractions. **It is doing
length reduction until lookups hit a memo of short words.** That is a far more
mundane mechanism than anything claimed for it earlier, and it deflates the
substrate result accordingly.

**It also reconciles iteration 4's puzzle.** That sweep found `compression` was
the WORST firing-aware ranking, which seemed to rule out compression as the
mechanism. The reconciliation: per-rule compression preference is not the same as
aggregate shortening achieved. `anticompression` prefers rules with poor
individual length cuts but high firing, and applied repeatedly those shorten the
population MORE than a few large-cut rules that rarely apply. What matters is
total shortening; the firing term is what delivers it.

**Consequence for the model half.** The ladder asks the model to propose true
equivalences. Truth is not what separates the arms — every substrate arm runs at
~99% rule truth. What separates them is aggregate shortening of the query
population below the memo's length horizon. **Nothing in C0-C4 asks the model for
that**, which is a sharper version of the iteration-10 worry that the ladder tests
the wrong thing.

**Guards green.** `mechanism.py` is analysis, not a guard; it re-runs 20 universes
across seven arms and belongs on demand alongside `validate.py`.

**Still uncommitted.** Asked five times.

---

## Iteration 16 — 2026-08-22 — the arena is not the confound, and I was wrong twice

**Lane:** not retried this iteration; the horizon sweep took the budget.

**The test.** Iteration 15 concluded that substrate accuracy is entirely coverage,
that coverage is set by how far rewriting drives a query down the length scale
(r = -0.944), and — because the memo only holds forms harvested from probes capped
at 6 — that the whole result might be an artifact of the gap between what an arm
may RUN and what it is ASKED. `horizon.py` sweeps the probe cap with query length
tracking it (cap+2 .. cap+6), so the task shape is constant at every setting.

Prediction if compression-to-horizon were the whole story: the P3c/P3d gap should
SHRINK as the cap rises, because less shortening is needed to reach the memo.

**It does the opposite.**

```
cap  queries  arm           acc     cov   canon len  rules  memo
  4    6-10   datadriven  0.396   0.200        5.02   39.3   207
  4    6-10   relevance   0.535   0.396        4.38   18.6   212
  6    8-12   datadriven  0.362   0.125        6.16   47.8   313
  6    8-12   relevance   0.652   0.535        4.33   24.1   341
  8   10-14   datadriven  0.344   0.092        7.62   48.2   502
  8   10-14   relevance   0.675   0.585        4.50   27.9   485
 10   12-16   datadriven  0.283   0.046        8.51   48.4   710
 10   12-16   relevance   0.765   0.698        4.27   30.2   635

P3d advantage:  +0.140 at cap 4  ->  +0.481 at cap 10   (change +0.342)
```

P3c gets steadily WORSE as the arena grows (0.396 -> 0.283) while P3d gets BETTER
(0.535 -> 0.765). A clean dissociation.

**The actual mechanism.** Regressing achieved canonical length on query length:

```
d(canonical length) / d(query length)
  P3c datadriven   +0.597    canonical form tracks the input: a constant-offset
                             reduction of ~3-5 items no matter how long the word
  P3d relevance    -0.008    FLAT. It drives any input to a fixed point near 4.3
```

P3d's rewriting is **scale-invariant**: it reaches the same canonical length from
length-8 and length-16 inputs alike. P3c's is not — it shortens by a roughly fixed
amount and stops. That is the difference between a rule set that COMPOSES, so
rewriting cascades until it hits a fixed point, and one that fires a bounded number
of times.

Why P3d composes: it ranks candidates by expected firing on words *after the rules
it already holds have been applied*, so each new rule is selected against the
RESIDUAL population. The rule set therefore covers successive length scales.

**Two of my own explanations were wrong, in opposite directions.**

- Iteration 10 proposed exactly this dynamic-relevance mechanism and I **withdrew
  it** because a single-cap test showed only +0.04. That test was run at cap 6,
  where the effect is small, using a generator I later found saturating. The
  hypothesis was right; my test was underpowered and confounded. Withdrawing it
  was the correct call on the evidence I had, but the conclusion was wrong.
- Iteration 15 then explained the gap as compression-to-horizon and called the
  result "mundane" and "deflated". That is now refuted: if it were
  compression-to-horizon the gap would close as the horizon rises, and it widens.

**The result is stronger than iteration 15 claimed, not weaker.** Achieving a
scale-invariant fixed point is what a working rewriting system does, and it is the
property that generalises: the advantage grows with problem size, which is the
signature of composition rather than lookup.

**What this does to the model half.** The axis to ask a model for is now precise
and measurable: not "propose true equivalences" (every arm is ~99% true), and not
"shorten words" (iteration 15's framing), but **propose rules that compose with
the ones already held, so rewriting keeps cascading.** No ladder condition asks
for that.

**Guards green.** One plumbing change: the relevance proposer now reads the query
length range off the eval set instead of hardcoding 8-12, so it stays honest when
the arena changes. That is arm-visible information, disclosed in the task
statement.

**Still uncommitted.** Asked six times.

---

## Iteration 17 — 2026-08-22 — second family added; the artifact language, not the
## proposer, is the binding constraint

**Lane:** not retried; the family work took the budget.

**Why now.** I closed iteration 16 asking how much confidence the scale-invariance
account deserves given I had been wrong three times. The answer is to test it where
it could break. That is also standing priority (4) and `SPEC.md` section 5, which
asked for several latent structural families and has been deferred since iteration 1.

**Family F_P added.** Actions become (coordinate permutation, translation) pairs
instead of pure translations, so the action monoid is **non-commutative**: word
order matters and every commutation rule that holds in F_T is false here. Same 27
states, same lossy sensor, same budget. `true_word_element` now represents an
element by its action on every state, which is the correct equivalence for any
family and leaves F_T semantics unchanged — all six frozen references still pass.

**Result: everything collapses in F_P.**

```
family  arm            acc     cov   canon len  rules  accepted
F_T     datadriven   0.362   0.125        6.16   47.8     98.6%
F_T     relevance    0.652   0.535        4.33   24.1     96.5%
F_T     P3b algo     0.504
F_P     datadriven   0.290   0.046        7.77   31.5     72.4%
F_P     relevance    0.310   0.075        7.17   19.5     68.7%
F_P     P3b algo     0.285

P3d advantage:  F_T +0.290   ->   F_P +0.021
```

Rule acceptance also falls from ~97% to ~70%: matching observed signatures across
four tags is much weaker evidence when order matters, so many proposals are
coincidences that survive a 3-context verifier.

**But the arena is FLATLINED, and that governs the reading.** Oracle ceiling — the
best rule set the substrate machinery could ever hold:

```
F_T   oracle acc 1.000   coverage 1.000   64 oracle rules
F_P   oracle acc 0.280   coverage 0.055   23 oracle rules
```

**No proposer, however good, can win in F_P.** Words of length <= 3 denote ~70
distinct elements there versus ~17 in F_T, so there are almost no short-word
equivalences to find and the rewrite-rule language has nearly nothing to express.

**What I therefore cannot conclude.** I cannot say "the scale-invariance mechanism
fails to generalise", because a flatlined arena cannot separate arms — this is
exactly the regime the calibration sweep in iteration 2 was built to avoid and
that the external review warned about when it argued against optimising the arena
against a baseline.

**What I can conclude, and it is sharper.** The substrate's power comes from a
MATCH between its artifact language and the hidden structure's redundancy.
Length-reducing rewrite rules over a memo of short words only have purchase where
short words are highly redundant. Remove that redundancy and the binding
constraint moves from the PROPOSER to the LANGUAGE: the ceiling drops to 0.280
before any proposer is chosen.

**This is the honest answer to the whispering-gallery worry**, deferred since
iteration 4 and repeatedly postponed. The answer is yes, with a precise diagnosis:
not that the mechanism was tuned to the group, but that the artifact language is
only expressive enough for structures whose short words collapse.

**Guards green** — all six F_T frozen references unchanged after the family change.

**Still uncommitted.** Asked seven times.

---

## Iteration 18 — 2026-08-22 — my iteration-17 diagnosis was wrong; a
## pre-committed prediction failed cleanly

**Lane:** openrouter 402, nvidia timeout.

**Setup.** Iteration 17 concluded that in the non-commutative family F_P "the
artifact language has nearly nothing to express" and called that the binding
constraint. There was a cheaper competing explanation I had not ruled out: the
oracle rule set was built only from words of length <= 3, so perhaps F_P's
equivalences simply live at LONGER left-hand sides and the problem is the WINDOW,
not the language.

**Prediction stated before running:** if language-inadequacy is right, widening
the window leaves F_P's ceiling flat; if window-inadequacy is right, it rises.

**It rose. The prediction failed.**

```
family  window   ceiling  coverage   rules  distinct elements
F_T          2     0.310     0.080       9                 12
F_T          3     1.000     1.000      64                 21
F_T          4     1.000     1.000     316                 25
F_P          2     0.245     0.005       1                 20
F_P          3     0.280     0.055      23                 62
F_P          4     0.480     0.340     217                124
F_P          5     0.550     0.445    1211                154
```

The rewrite-rule language expresses F_P's structure perfectly well. It just needs
lhs of length 4-5 rather than 2-3. **Iteration 17's "the language is the binding
constraint" is withdrawn.**

**The correct diagnosis is affordability.** A rule test costs 6 interactions, and
the whole budget is 600, so at most ~100 rules are purchasable even if nothing
were spent on observation; arms actually buy 20-48.

```
family  rules needed for its ceiling   ceiling   affordable at this budget?
F_T                   64 (window 3)     1.000    yes  (0.64x the cap)
F_P                  217 (window 4)     0.480    no   (2.2x)
F_P                 1211 (window 5)     0.550    no   (12.1x)
```

So the substrate succeeds exactly when **the rule set required to collapse the
query population is affordable at the interaction budget.** F_T's characteristic
rule length is 3 and costs 64 rules; F_P's is 5 and costs over a thousand. Nothing
about expressiveness, everything about density.

Supporting this reading: relative to their OWN ceilings the arms perform similarly
in both families — P3d reaches 65% of the reachable maximum in F_T and 56% in F_P.
The arm is not broken in F_P; the reachable maximum is.

**Third correction in three iterations, but this one was pre-registered.**
Iterations 15, 16 and 17 each produced an explanation that a later test overturned.
The difference here is that I wrote the prediction down before measuring and the
measurement contradicted it, which is the only version of being wrong that carries
information. The methodological fix I was groping for in iteration 16 is now
concrete: **state the prediction and the falsifying observation before running the
sweep, not after.**

**Guards green.**

**Still uncommitted.** Asked eight times.

---

## Iteration 19 — 2026-08-22 — split verdict: P3d's edge is sample efficiency,
## not rule quality

**Lane:** openrouter 402, nvidia timeout.

**Method fix in force.** The prediction and its falsifiers were written to
`PREDICTION_iter19.md` and committed to disk BEFORE the sweep ran, per the
methodological note from iteration 18. The verdict was appended after.

**Test.** Iteration 18 claimed the substrate succeeds exactly when the required
rule set is affordable. That predicts: scale F_P's budget and claim allowance
together, and P3d should recover its F_T-like advantage. Falsifiers stated in
advance: F1 if the gap stays under +0.10 at 12x; F2 if accuracy stays under 0.40.

**Result — F1 fires, F2 does not.**

```
F_P budget   P3c acc   P3d acc     gap    P3c rules  P3d rules  canon len
   1x         0.287     0.312   +0.025       31.2       19.9    7.79/7.09
   3x         0.408     0.445   +0.037      112.0       60.1    5.20/4.79
   6x         0.465     0.512   +0.047      237.9       86.8    4.40/4.05
  12x         0.540     0.510   -0.030      442.7      117.5    3.65/3.50
F_T 1x        0.370     0.662   +0.292       47.9       23.5    5.99/4.21
```

**Affordability was right about ACCURACY.** F_P accuracy climbs 0.312 -> 0.510 and
at 12x P3d reaches **93% of F_P's 0.550 ceiling**, better than the 65% it manages
in F_T at 1x. Budget genuinely was the binding constraint on how well the arms do.

**Affordability was wrong about the ADVANTAGE.** P3d's edge never recovers: +0.025,
+0.037, +0.047, then **-0.030** — at 12x the simple proposer overtakes it.

**Why, and this is the real finding.** At 12x, P3c buys 443 rules and P3d only 118.
P3d's relevance filter discards candidates that do not fire on its synthetic
normalised words; in F_P far fewer candidates fire, so it proposes far less. P3c
proposes everything observation-consistent and, given enough budget, brute-forces
its way to 0.825 coverage.

So **P3d's advantage is a sample-efficiency advantage, not a rule-quality
advantage.** Selectivity pays when the budget is scarce relative to the rule set
the structure demands, and becomes a liability when budget is abundant, because
the selective arm leaves purchasable rules unbought. P3d's 0.647 in F_T is not
better representation learning. It is better use of a tight budget.

**Consequence for the model question.** If the frozen reasoner's contribution
would be selectivity — proposing the rules worth testing — that contribution only
has value under scarcity. Under abundance an indiscriminate proposer wins by
volume. Any model result therefore has to be read against where the arena sits on
this curve, and F_T at the standard budget is deep in the scarce regime, which is
exactly the regime that flatters selectivity.

**Guards green.**

**Still uncommitted.** Asked nine times.

---

## Iteration 20 — 2026-08-22 — no crossover in F_T; the axis is compressibility,
## not scarcity

**Lane:** not retried this iteration; the sweep took the budget.

**Method fix in force.** Prediction and falsifiers written to
`PREDICTION_iter20.md` before the run; verdict appended after.

**Test.** Iteration 19 concluded from F_P alone that "P3d's advantage is sample
efficiency, not rule quality — selectivity pays under scarcity and becomes a
liability under abundance." F_P showed a crossover between 6x and 12x budget. If
that is a property of selectivity rather than an F_P quirk, F_T must show one too.
This also matters for a sceptical reading: the standard arena is F_T at 1x, a
budget I chose during calibration, so if F_T's crossover sat near 1x the headline
result would have been obtained at a budget that specifically flatters selectivity.

**Result — falsifier F1 fires. There is no crossover in F_T.**

```
 x   budget   P3c acc   P3d acc     gap   P3c rules  P3d rules  P3c cov  P3d cov
 1      100     0.370     0.662  +0.292       47.9       23.5    0.135    0.550
 2      200     0.472     0.895  +0.422      103.6       35.2    0.300    0.890
 3      300     0.560     0.918  +0.358      155.7       40.7    0.450    0.963
 6      600     0.670     0.993  +0.323      314.7       50.8    0.600    1.000
12     1200     0.792     0.963  +0.170      633.8       74.2    0.745    1.000
```

P3d keeps +0.170 at 12x, above the 0.15 threshold set in advance. **Iteration 19's
generalisation was drawn from one family and is wrong for F_T.**

**The two families behave oppositely at 12x, and that identifies the real axis.**

```
family  arm   rules   coverage    acc
F_T     P3c   633.8      0.745  0.792
F_T     P3d    74.2      1.000  0.963
F_P     P3c   442.7      0.825  0.540
F_P     P3d   117.5      0.887  0.510
```

In F_T, P3d uses **8.5x fewer rules and achieves MORE coverage** — 1.000 against
0.745. In F_P it uses 3.8x fewer rules for roughly the same coverage. Selectivity
is not buying efficiency in F_T; it is finding a *sufficient* set that
indiscriminate proposing never assembles even with 634 rules.

**Revised account: the axis is COMPRESSIBILITY, not budget scarcity.**
Selectivity wins when a compact sufficient rule set EXISTS and can be found —
F_T's oracle needs 64 rules and P3d locates ~50 of the right ones. It gains
nothing when no such set exists — F_P's oracle needs 1211, there is no shortcut,
and filtering only costs volume. F_P's apparent crossover was never selectivity
failing under abundance; it was P3c grinding toward a ceiling that selectivity
could not shortcut because no shortcut is there.

This also subsumes the earlier accounts rather than replacing them arbitrarily:
short-word redundancy (iteration 17), rule density (iteration 18) and now
compressibility are the same property measured three ways.

**And it answers the sceptical reading.** The standard budget does not flatter
selectivity: P3d's advantage is largest at 2x (+0.422), not at 1x, and survives a
twelve-fold budget increase. The arena was not sited at the edge of a favourable
regime.

**Fourth revision, third consecutive pre-registered one.** Iterations 18, 19 and 20
each stated a falsifier before measuring; 18's and 19's fired, 20's fired. Being
wrong this way costs one iteration and yields a sharper claim; being wrong the
earlier way cost three iterations and produced a withdrawn headline.

**Guards green. Still uncommitted — asked ten times.**

---

## Iteration 21 — 2026-08-22 — the compressibility account PREDICTS, out of sample

**Lane:** not retried; the family build and sweep took the budget.

**Why this test.** I closed iteration 20 asking whether compressibility — the
fourth account of P3d's advantage, and the first to subsume its predecessors —
was right or was a story fitted to an accumulating pile of sweeps. Every previous
account was post-hoc. The only clean answer is an out-of-sample quantitative
prediction on a family that did not exist when the account was formed.

**Built F_M**, an intermediate family: exactly one action carries a permutation,
so the monoid is "mostly abelian" and its redundancy sits between F_T's and F_P's
by construction. Its STRUCTURE was measured first, with no arm run on it.

**A flaw in my own predictor, caught before any arm touched F_M.** My first
instinct was to interpolate on window-3 oracle rule count, but F_P has FEWER rules
there (22) than F_T (64) — because there is little to find, not because it is more
compact. Rule count at a fixed window measures scarcity of equivalences, not
compactness. The ceiling is the cleaner structural measure.

Rather than silently swap predictors, I registered BOTH with bands and recorded in
advance that I expected the ceiling-based one to do better.

**Result — neither falsifier fires, and the ordering is monotone.**

```
family   noncommuting  oracle rules  ceiling   P3d gap
F_T               0.0            64    1.000    +0.292   known before
F_M               4.0            52    0.560    +0.152   PREDICTED, then measured
F_P              11.2            22    0.310    +0.027   known before

predictor A, log rule count   +0.240   band +0.140..+0.340   IN (by 0.012)
predictor B, ceiling          +0.122   band +0.022..+0.222   IN (error 0.030)
ordering falsifier F2                                        HOLDS
```

Predictor B was more accurate, as recorded beforehand. **This is the first account
in twenty-one iterations to predict rather than explain**, which is materially
different evidence from the four post-hoc accounts that preceded it
(compression-to-horizon, scale-invariance-as-whole-story, language-inadequacy,
scarcity-vs-abundance).

**What this does NOT establish.** One out-of-sample family, 10 seeds, and bands of
+/-0.10 against a total range of 0.267 — wide. Predictor A passed by only 0.012 and
should be regarded as uninformative rather than confirmed. The claim earned here is
ordinal and roughly quantitative, not precise.

**Standing summary of the deterministic half.** The substrate accumulates
environment-verified artifacts that are causally load-bearing; its accuracy is
exactly `coverage + (1-coverage)*fallback`; coverage is set by how far rewriting
collapses the query population; and the advantage of selective proposing over
indiscriminate proposing scales with how compressible the hidden structure is,
predictably enough to forecast a new family within 0.03.

**Guards green. Still uncommitted — asked eleven times.**

---

## Iteration 22 — 2026-08-22 — noise estimated, a published verdict corrected,
## second out-of-sample test passes at low power

**Lane:** not retried; noise estimation plus a fourth family took the budget.

**Why.** I closed iteration 21 noting that its +/-0.10 prediction bands were chosen
without estimating measurement noise, and that predictor A had passed "by 0.012" —
possibly inside the noise. That is a flaw in a verdict I had already published to
the log, so it came first.

**Noise measured, paired per-seed, 20 seeds:**

```
family   mean gap      sd      SE   95% CI half-width
F_T         0.284   0.186   0.042              0.082
F_M         0.107   0.126   0.028              0.055
F_P         0.021   0.064   0.014              0.028
```

**Two corrections to iteration 21, both against my own reported result.**

1. **F_M's gap is +0.107 at 20 seeds, not the +0.152 I reported at 10.** The error
   (0.045) exceeds the standard error, so the published figure was noisy.
2. **Re-scored against a noise-justified band of +/-0.082:**
   ```
   predictor A, log rule count  +0.240  band +0.158..+0.322  measured +0.107  OUT
   predictor B, ceiling         +0.122  band +0.040..+0.204  measured +0.107  IN
   ```
   **Predictor A is refuted.** Its iteration-21 pass was an artifact of an
   unjustified band applied to a noisy measurement. Predictor B's error improves
   to 0.015. The corrected verdict is *cleaner* than the one I reported: the two
   predictors are now sharply discriminated rather than both nominally passing,
   and the expectation I recorded in advance (that B would win) is upheld properly.

**Second out-of-sample family, F_M2** (two of four actions permute). Structure
measured first — ceiling 0.360, 8 of 16 noncommuting pairs — then predictor B
applied with the noise-justified band, then the arms run.

```
PREDICTED  +0.040   band -0.042..+0.122
MEASURED   +0.019   SE 0.015, 20 seeds        F1 does not fire, error 0.021
```

**Reported honestly as low power.** The predicted gap is small and its band spans
zero, so a landing inside it cannot be distinguished from "no effect". F_M was the
discriminating test; F_M2 is corroboration only. And the ordering is not strictly
monotone at the point estimate — F_M2 (+0.019) sits 0.002 below F_P (+0.021)
against an SE of 0.015, so the ordering holds within noise but not cleanly.

**Standing position after two out-of-sample tests.** Predictor B — interpolating
the selective-vs-indiscriminate advantage on the family's oracle ceiling —
forecast a previously non-existent family to within 0.015, and a second to within
0.021. Predictor A is refuted. Compressibility remains the best account and is now
the only one in this experiment that has predicted rather than explained.

**Methodological lesson, third of its kind.** Iteration 18 established: state the
falsifier before the run. Iteration 22 adds: **estimate the noise before choosing
the band, and the seed count before trusting the point estimate.** A
pre-registered tolerance that is not justified by measured variance can let a
wrong predictor through.

**Guards green. Still uncommitted — asked twelve times.**

---

## Iteration 23 — 2026-08-22 — auditing my own provisional sweeps; one survives,
## one was decided by noise

**Lane:** not retried; two 20-seed re-runs took the budget.

**Why.** Iteration 22 found F_M's gap moved 0.045 between 10 and 20 seeds, more
than its standard error, which made every 5-12 seed sweep from iterations 15-21
provisional. Rather than keep building on them, this iteration re-ran the two most
load-bearing at 20 seeds with standard errors, under falsifiers written first.

**Horizon sweep (iteration 16) — SURVIVES.**

```
cap   P3c     P3d      gap     SE   12-seed gap   shift
  4  0.371  0.546   +0.175  0.047       +0.140   +0.035
  6  0.364  0.647   +0.284  0.042       +0.290   -0.006
  8  0.370  0.675   +0.305  0.040       +0.331   -0.026
 10  0.297  0.751   +0.454  0.052       +0.454   -0.027
```

Monotone increasing holds; the cap-4 to cap-10 rise of +0.279 is about 4 SE, well
clear of noise; no individual cap shifted more than 0.035. **Iteration 16's claim
that P3d's advantage grows with arena size stands, now with error bars.** The
12-seed sweep was adequate for it, because the effect dwarfed the noise.

**Iteration 20's verdict — the CONCLUSION survives, the TEST does not.**

```
10-seed gap at 12x budget   +0.170
20-seed gap at 12x budget   +0.101   SE 0.031   95% CI +0.040 .. +0.162
```

Iteration 20 recorded its falsifier "P3d keeps >= +0.15 at 12x" as FIRING. At 20
seeds the 0.15 threshold sits **inside** the confidence interval, so **that test
was decided by noise rather than by data**. The substantive conclusion still holds
on independent grounds: +0.101 is 3.3 SE from zero and the gap never turns
negative, so there is no crossover in F_T and selectivity is not merely a scarcity
technology. Right conclusion, invalid test — both halves recorded, because a
verdict that happened to land correctly is not the same as one the data decided.

**The generalisable lesson, and it is not "always use more seeds".** The horizon
sweep was fine at 12 seeds and the crossover test was inadequate at 10. What
separates them is not effect size alone but **the distance between the effect and
the DECISION THRESHOLD**. Horizon asked "is the trend monotone and large" against
an effect of 0.279 with SE 0.05. Iteration 20 asked "is the gap above 0.15"
against an effect of 0.101-0.170 with SE 0.031 — a threshold sitting on top of the
estimate. Seed count must be chosen relative to the threshold the falsifier turns
on, not relative to the raw effect.

Cumulative method rules now in force:
```
iter 18  state the falsifier before the run
iter 22  estimate the noise before choosing the band
iter 23  size the sample against the DECISION THRESHOLD, not the effect
```

**Guards green. Still uncommitted — asked thirteen times.**

---

## Iteration 24 — 2026-08-22 — the new rule applied to my own headline; it is fragile

**Lane:** openrouter 402, nvidia timeout.

**Why.** Iteration 23 established that a decision threshold sitting on top of an
estimate makes a verdict noise-decided rather than data-decided. The most-cited
model-side result in this experiment — forced claims true at 10.8% versus a 3.7%
baseline, one-sided p = 0.047 against alpha = 0.05 — is precisely that shape. It
had to be audited before anything else was built on it.

**Sensitivity analysis, and it is damning.**

```
2/37 true -> p = 0.400   not significant
3/37 true -> p = 0.156   not significant
4/37 true -> p = 0.047   significant     <- observed
5/37 true -> p = 0.011   significant
```

**One claim reclassified flips the verdict.** 3/37 gives p = 0.156. The whole
"the model's claims beat chance" result rests on the truth-scoring of a single
claim out of thirty-seven.

**A second error in my own earlier reporting.** Previous iterations quoted a 95%
CI of [0.008, 0.208] and noted it contains the baseline. That was a normal
approximation, which is inappropriate for a small-n proportion. The Wilson
interval is [0.043, 0.247], which **excludes** the baseline. The two intervals
disagree about the headline. Given the one-point fragility, neither should be
leaned on. Corrected statement: **the model's claims are plausibly but not
reliably above chance.**

**What would settle it:** ~61 claims for p < 0.01, against 37 in hand — about 48
forced turns, one working lane window. That is now the single highest-value
outstanding model measurement, and it is cheap by the standards of this experiment.

**The emission result is untouched by any of this.** Forced generation raises
emission from 1 claim in 39 turns to 29 in 29, Fisher p = 3.8e-09 — eight orders
clear of any threshold. The strong model finding survives the audit; the marginal
one does not.

**New standing rule and a new artifact.** `RESULTS.md` now holds every headline
number with its n, interval, and the decision threshold its claim turns on, each
marked DECIDED, INSIDE NOISE, or FRAGILE. Rule adopted: **no number enters the
record without those three, from the moment it is first written.** Building it
surfaced that F_M2's advantage (+0.019, SE 0.015) and F_P's (+0.021, SE 0.014)
are 1.3 and 1.5 SE from zero — both were reported earlier as though they were
measurements, and both are properly "not distinguishable from zero".

Cumulative method rules:
```
iter 18  state the falsifier before the run
iter 22  estimate the noise before choosing the band
iter 23  size the sample against the decision threshold, not the effect
iter 24  report n, interval and threshold with every number, from first writing
```

**Guards green. Still uncommitted — asked fourteen times.**

---

## Iteration 25 — 2026-08-22 — the discriminating out-of-sample test, and it passes

**Lane:** not retried; the family build and 20-seed sweep took the budget.

**The criticism being answered is my own.** Iteration 24's audit showed the low
end of the compressibility curve is noise — F_M2 (+0.019, 1.3 SE) and F_P
(+0.021, 1.5 SE) are not distinguishable from zero. That meant iteration 22's
F_M2 "prediction success" landed in a band spanning zero, which is not a test at
all, and the account rested on one genuine out-of-sample hit. The fix is the
discriminating test I proposed in iteration 22 and never ran: a family at the HIGH
end of the curve, where the predicted gap is large enough that its band excludes
zero.

**F_MT** restricts the single permuting action to a TRANSPOSITION (order 2) rather
than any permutation, so it disrupts less per application and should be more
compressible than F_M. Structure measured first, arms not run: ceiling 0.630, 3.6
of 16 noncommuting pairs — sitting between F_T (1.000) and F_M (0.560) as intended.

```
PREDICTED +0.143   band +0.061..+0.225   (excludes zero -> discriminating)
MEASURED  +0.142   SE 0.025, 20 seeds, 5.7 SE from zero
F1 does not fire (error 0.001).  F2 ordering HOLDS: +0.107 < +0.142 < +0.284.
```

**The error of 0.001 against an SE of 0.025 is luck and is reported as such.** The
defensible claim is that a discriminating prediction landed well inside noise, not
that the predictor is accurate to a thousandth.

**Standing position on the compressibility account:**

```
family  ceiling   gap      SE     SE from 0   status
F_T       1.000  +0.284  0.042        6.8     anchor
F_MT      0.630  +0.142  0.025        5.7     predicted out of sample, DISCRIMINATING
F_M       0.560  +0.107  0.028        3.8     predicted out of sample, DISCRIMINATING
F_M2      0.360  +0.019  0.015        1.3     predicted, but low power
F_P       0.310  +0.021  0.014        1.5     anchor
```

Two anchors, three out-of-sample predictions, **two of them discriminating and
both passing**. This is the strongest evidence in the experiment and it is the
only claim here that has been tested by forecasting rather than by explaining.

**What is still weak.** The two anchors are asymmetric: F_T is 6.8 SE from zero,
F_P only 1.5. The interpolation's low endpoint is a small number known to be
small, which is adequate for the arithmetic but means the curve is really pinned
at one end. A family below F_P would not help, since everything there is noise.

**Guards green. Still uncommitted — asked fifteen times.**

---

## Iteration 26 — 2026-08-23 — the compressibility predictor is REFUTED by the
## test I built to be harder

**Lane:** not retried; two 20-seed sweeps took the budget.

**What was tested.** The predictor is linear interpolation of the P3d-P3c gap on
oracle ceiling. Nothing had tested linearity, and the three interior residuals
were all negative (-0.001, -0.015, -0.021) — 3/3 same sign, suggestive of slight
concavity. More importantly, **every family so far differed only in how many
actions permute.** If the gap is really a function of ceiling, the predictor must
work when the ceiling is moved a DIFFERENT way. So the two new interior points
vary the ACTION COUNT (5 and 6) instead.

**Both falsifiers fire.**

```
family            ceiling  predicted  measured   SE     residual   band
F_MT 5 actions      0.810    +0.212    +0.075  0.023     -0.137    OUT
F_MT 6 actions      0.870    +0.234    +0.023  0.009     -0.212    OUT
```

Residuals across all five interior points: -0.001, -0.015, -0.021, -0.137, -0.212.
5/5 negative; F2 fires on magnitude.

**The predictor was not a function of oracle ceiling. It was a fit to the
permutation axis.** A family with ceiling 0.870 — nearly as compressible as
abelian F_T at 1.000 — produces a gap of +0.023 against F_T's +0.284.

**This retro-invalidates last iteration's headline.** I promoted compressibility
to "the strongest evidence in the experiment... the only claim tested by
forecasting rather than explaining", on the strength of two discriminating
out-of-sample passes. All five families in that curve shared `n_actions = 4`. The
predictor was interpolating WITHIN one knob and never generalised across knobs.
Both passes are downgraded from evidence for a law to confirmation of a
single-axis fit.

**What the new data suggests instead.** With 6 actions, words of length <= 3
number 258 versus 84 with 4 actions. The candidate space P3d must sift, and P3c
must propose into, grows fast. The gap appears to depend on the SIZE OF THE
CANDIDATE SPACE as well as the compressibility of the structure — and at 6 actions
the advantage nearly vanishes even though the structure is highly compressible.
That is a hypothesis generated by this data and it has not been tested; it is
recorded as such, not as a fifth account.

**Fifth account to fall.** compression-to-horizon, scale-invariance-as-whole-story,
language-inadequacy, scarcity-vs-abundance, and now ceiling-as-predictor. The
difference is that this one died to a pre-registered test explicitly designed to be
harder than the ones it had already passed — which is the method working, at the
cost of a headline claimed one iteration too early.

**Lesson, added to the standing rules.** Two out-of-sample successes along one
structural knob are not evidence of a general relationship. **A predictor must be
tested by moving its input through a DIFFERENT mechanism than the one used to fit
it.**

```
iter 18  state the falsifier before the run
iter 22  estimate the noise before choosing the band
iter 23  size the sample against the decision threshold, not the effect
iter 24  report n, interval and threshold with every number, from first writing
iter 26  vary the predictor's input by a different mechanism before believing it
```

**Guards green. Still uncommitted — asked sixteen times.**

---

## Iteration 27 — 2026-08-23 — tree committed; candidate burden is causal

**Structure taken from external review**: commit and reproduce, run exactly one
causal candidate-burden experiment that does not alter arena algebra,
pre-register a binary decision, then redirect toward the model lane.

**1. The tree is committed.** `charon/ceiling_v0` was untracked for eleven
iterations, which is why the working-tree loss at iteration 10 was unrecoverable.
24 files now tracked at `c578d044`. Local commit only, no push. This closes the
standing epistemic threat: the audit trail is the strongest thing this experiment
has and it was being gambled every iteration.

**2. Candidate burden manipulated downstream of the arena.** New `sig_tags` knob:
a candidate pair enters the proposal pool when its two words agree on that many
tags. All four is the original behaviour; fewer is weaker evidence, so the pool
floods with plausible-but-often-false candidates. Universe, sensor, algebra,
budget and verifier are byte-identical across conditions; only the admission
criterion changes. Both arms receive the same pool.

```
sig_tags  pool size  P3c acc  P3d acc      gap     SE   P3c rules  P3d rules
       4         78    0.364    0.647   +0.284  0.042        46.5       24.1
       3         87    0.346    0.560   +0.214  0.050        40.8       23.5
       2        167    0.285    0.414   +0.129  0.039        26.3       17.6
```

**Monotone shrink; change of -0.155 against 2*SE_diff of 0.114 (~2.7 SE).**
Neither falsifier fires. **Doubling the candidate pool roughly halves P3d's
advantage, with the hidden algebra untouched.**

This is the first causal evidence in the experiment about the LEARNER machinery
rather than about arena structure. Every previous account was a correlation across
families; this one intervenes on one variable and holds the rest fixed.

**Framing, taken from the review and adopted.** The result is reported as
phenomenon plus boundary, not as a law:

- **Tier A, findings.** P3d beats P3c substantially in F_T; rules and memo are
  complementary; frequently-used rules causally matter; foreign rules confer
  nothing; normalisation is sound given true rules; coverage nearly determines
  accuracy; the advantage grows with probing in the tested regime.
- **Tier B, boundary.** The advantage is strongly environment-dependent and no
  tested scalar predicts it across orthogonal structural interventions. **Five
  accounts refuted.** This is itself a finding: the gap depends on interactions
  among structural properties, not on one obvious scalar. It does NOT establish
  that no simple determinant exists — only that none of the tested ones
  generalises across mechanisms.
- **Tier C, mechanism.** Partially open. Candidate burden is now causally
  implicated but not shown sufficient.

**The conceptual point worth elevating over any account.** F_MT with 6 actions is
nearly maximally compressible by the oracle (ceiling 0.870) yet yields almost no
advantage. **Structure existing and a bounded procedure being able to exploit it
economically are different quantities.** A world can be rich in compressible
structure and still be hard for a bounded learner because the search economics of
acquiring that structure are hostile. Today's result is consistent with that: a
pure search-economics manipulation moved the gap by half while the structure stayed
identical.

**Sharpened method rule, replacing the iteration-26 phrasing.** Mechanism claims
require ORTHOGONAL intervention. Predictive replication along the generating axis
may strengthen an empirical relationship but cannot promote it to an explanatory
account.

**Binary decision, recorded before the run and now in force.** The prediction
survived, so exactly ONE confirmatory experiment is permitted: attempt the REVERSE
— reduce candidate burden in the 6-action arena where the gap collapsed to +0.023,
and see whether the advantage returns. If it does not, mechanism search in
ceiling_v0 terminates and mechanism is reported unresolved. Either way, mechanism
work stops after that and effort redirects to the model lane.

**Guards green.**

---

## Iteration 28 — 2026-08-23 — confirmatory test VOID; mechanism search closed as
## unresolved per the pre-registered stopping rule

**Lane:** openrouter 402, nvidia timeout. Nineteen iterations without a usable lane.

**The one permitted experiment.** Iteration 27 showed causally that ENLARGING the
candidate pool halves P3d's advantage with the algebra untouched. The binary
decision recorded before that run allowed exactly one confirmatory test: the
reverse direction, in the arena where the advantage had collapsed.

**Design.** `sig_depth=1` admits a candidate only if its two words agree on all
tags AND on every observed one-step continuation — strictly stronger evidence,
therefore a smaller purer pool. Orthogonal to iteration 27's intervention: that
loosened admission in a 4-action arena, this tightens it in a 6-action arena, in
the opposite direction, in the regime where the effect was absent.

```
arena                sig_depth  pool    P3c    P3d      gap     SE
F_MT 6 actions               0   122  0.276  0.299   +0.023  0.009
F_MT 6 actions               1     0  0.275  0.275   +0.000  0.000
F_T 4 actions (control)      0   124  0.364  0.647   +0.284  0.042
F_T 4 actions (control)      1     1  0.249  0.249   +0.000  0.005
```

**The test is void, and the control is what proves it.** Requiring agreement on
every observed continuation is so strict that essentially no candidate qualifies
at this observation density: the pool went to ZERO, both arms acquired nothing,
both scored fallback. F_T's advantage was destroyed as well, +0.284 -> +0.000. A
valid graded burden-reducer would have preserved it. The lever annihilated the
pool rather than shrinking it.

**Honouring the stopping rule anyway.** F1 fired by the letter of the
pre-registration, so mechanism search in ceiling_v0 is **CLOSED** and mechanism is
reported **UNRESOLVED**. That phrasing is deliberate: the question was not
answered, and burden was NOT refuted. I could repair the lever with a partial
depth and re-run, and I am choosing not to, because the stopping rule exists
precisely to prevent an indefinite account-per-iteration treadmill and its value
comes from being honoured when inconvenient.

**Final position on the three tiers.**

- **Tier A, findings — durable.** P3d beats P3c in F_T by +0.284 (SE 0.042); rules
  and memo are complementary (0.254 / 0.254 alone, 0.364 together); frequently-used
  rules causally matter (deleting 9 most-used costs 0.088 vs 0.042 random vs 0.000
  least-used); a foreign-universe store fires on 13% of queries but confers nothing;
  normalisation is sound given true rules (0 violations in 3000 words); accuracy =
  coverage + (1-coverage)*fallback with residuals under one point; the advantage
  grows with probing in the tested regime.
- **Tier B, boundary — also a finding.** The advantage is strongly
  environment-dependent and no tested scalar predicts it across orthogonal
  structural interventions. Five accounts refuted. This does not establish that no
  simple determinant exists, only that none of the tested ones generalises.
- **Tier C, mechanism — CLOSED, UNRESOLVED.** One causal factor implicated
  (candidate-pool burden: doubling the pool halves the advantage) but not shown
  sufficient. The confirmatory test was void.

**The conceptual result that outlives the failed accounts.** Oracle ceiling and
exploitable structure are different quantities. F_MT-6 is nearly maximally
compressible (0.870) and yields +0.023. A world can be rich in compressible
structure and still be hard for a bounded learner because the search economics of
acquiring it are hostile. That is the finding this experiment actually supports
about cognitive ceilings, and it came from the deterministic half.

**Effort now redirects to the model lane per the standing plan.** The deterministic
explanatory program is closed. Nine modules remain unrestored and no lane has
worked since iteration 8.
