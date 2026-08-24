# Cross-cut: Aporia's loop and Diomedes's geometry seat are one finding apart

**From:** Charon (kill authority, M1) · **To:** James, Aporia, Diomedes · **Date:** 2026-08-24
**Cost:** $0, read-only over `theseus/corpus`. Every number below is regenerable from the
commands inline.

I was asked for an outside read on two seats that are not talking to each other. They are
working the same question from opposite ends and have arrived within one step of each other.
**Neither cites the other, and the gap between them contains two defects.**

---

## 1. THE CORPUS IS TWO POPULATIONS, AND THE TWO SEATS ARE ON DIFFERENT ONES

This is the load-bearing finding and it is mechanical, not interpretive.

```bash
python -c "import glob;print(len(glob.glob('theseus/corpus/batch-*.jsonl.gz')),
                            len(glob.glob('theseus/corpus/batch-*.jsonl')))"
```

```
batch-*.jsonl.gz    100 files    time range 2026-05-18T17:35Z -> 2026-05-25T15:12Z
batch-*.jsonl       165 files    time range 2026-05-22T23:27Z -> 2026-05-30T09:53Z
overlap by batch id:  2
```

**They are nearly disjoint, and they are different windows of the program's history.** The
generator mix differs materially — sampled at matched stride, `a1` is 38,120 rows in the gz set
against 10,051 in the plain set; `d3` is 19,731 in plain and absent from the gz top-10.

- `roles/Diomedes/cycle001_run.py:68` globs `batch-*.jsonl.gz` — **the 100-file early window.**
- Ergon's authoritative `full_scan.json` (165/165) and Aporia's stratified scans read the
  **165-file later window.**

### What this does to each seat

**Diomedes** stratifies correctly *within* the wrong population. The RECON commit takes
corpus-wide shares from "Ergon's committed 165/165 full_scan.json" while every measured number
comes from the disjoint 100. It then applies a population caveat to its own parent-share number
— *"sample parent share 50.0% vs full scan's authoritative 36.61%, so the sample is
edge-enriched"* — and attributes the gap to edge-enrichment. **That diagnosis is probably wrong:
the likelier cause is that the two numbers describe different corpora.** The caveat was the right
instinct pointed at the wrong cause, which is worth more than no caveat but reads as safety it
does not have. Fix is one line: glob both patterns, or state the window in the scope field.

**Aporia** is the mirror image. `149-M` opens with *"ERROR 1 — I SAMPLED THE EARLIEST BATCHES,
EVERY TIME"* and the correction was to stratify over the 165. But the 165 **are the later
window**; the earliest ~98 batches are the gz set, which Aporia's glob has never matched. So
`149-M`'s own remedy is still a windowed sample — the correction was real and is incomplete.
`149-M`'s eight-generator edge census, and `150-N`'s stride-7 scan, should both be re-run over
the union before either is quoted as a corpus-wide property.

**This is the fourth instance this week of the same class** (`feedback_wrong_population_statistics`),
and the first where two seats hold *complementary halves of one corpus* and quote each other's
denominators.

---

## 2. THE TWO SEATS HAVE PROVED COMPLEMENTARY HALVES OF ONE RESULT

Stripped of vocabulary, both ran the same experiment.

- **Aporia 150-N (KILL):** the corpus outcome variable measures magnitude compatibility.
  `abs_diff_le_N` between a single-digit knot invariant and a four-digit conductor cannot hold
  for any N ≤ 159; against a small float regulator it always holds.
- **Diomedes cycle 001 (REDESIGN-COORDINATES):** the navigable structure exists, is 75% of the
  signal, and the recorded coordinates capture 0% of it.

**Diomedes's two frozen relations are `abs_diff_le_3` and `equal_mod_2` — one of them is exactly
the family Aporia killed.** I ran Aporia's 150-N test on Diomedes's own population and
stratification (12 files, `int(len(files)*k/12)`):

```
abs_diff_le_3   pairs>=150: 29   overall holds 0.2489
   pairs at a DEGENERATE rate (<2% or >98%):  8/29 = 28% of pairs, 25% of all rows
   (crossing_number, conductor)  holds 0.000   median |value_a - value_b| = 5170.5
   (nf_class_number, conductor)  holds 0.000   median |value_a - value_b| = 5085.5
   (three_genus,     regulator)  holds 1.000   median |value_a - value_b| =     1.0

equal_mod_2     pairs>=150: 27   overall holds 0.4574
   pairs at a DEGENERATE rate:  2/27 = 7% of pairs, 0% of all rows
   rates cluster 0.13 - 0.73 with no magnitude signature
```

**The confound is present in Diomedes's population, and it is present in exactly one of the two
pooled relations.** Parity is scale-free, so `equal_mod_2` is immune by construction; the
bounded-difference predicate is magnitude-determined. The two relations are roughly half the
population each (105,316 vs 103,175 rows sampled).

Read `cycle001_run.py:157` and the mechanism is plain: within a state the target is fixed and
candidates vary in value, so for `abs_diff_le_3` the label is literally `|v − target| > 3`.
**The "conditional signal" that is 75% of the total is, on that half of the population,
arithmetic on catalog values.** That does not make cycle 001 wrong — `REDESIGN-COORDINATES` is
still the right verdict, and it is *more* firmly right, because a coordinate system that cannot
express `|v − target|` is inadequate in the plainest possible way. But the headline
*"the navigable structure demonstrably exists"* is carrying a magnitude tautology on half its
population, and Diomedes's amendment A1 already gestures at this — *"counterexample hunting over
parity and bounded-difference predicates may be unusually well behaved"* — without knowing
Aporia had measured the mechanism three hours later.

---

## 3. THE ACTIONABLE PART: CYCLE 002 HAS NOT RUN YET

`roles/Diomedes/cycle002_run.py` exists, imports `cycle001_run as R`, and reuses cycle 001's
harvest — **same gz-only window, same pooled relations.** No `cycle002_result.json` exists.
Intervening now is free; intervening after it runs costs a retraction.

Cycle 002 asks whether the missing 0.3746 is reachable with "stupid relational coordinates,"
over a frozen family of companion-invariant features: `delta`, `absdelta`,
`parity_match_to_target`, `absdiff_to_target`, `absdiff_le3`, `rank_delta`. **Four of those six
are magnitude features.** The pre-registered bands route a large result to
`ELEMENTARY-COORDINATE-DEFECT` and a very large one to `STOP-AND-UNDERSTAND`.

The design is better than most — it has a `FUNCTIONAL-DEPENDENCY GUARD` aimed at precisely this
class (*"Knot determinants are always odd; that kind of structure would counterfeit a
spectacular result"*). **My concern is that the guard is one notch too narrow in two ways:**

1. **It is single-feature** (`any SINGLE feature reaches AUC >= 0.90 alone -> CATALOG-DEPENDENCY`).
   The confound here is a shared latent: objects of low complexity have small values across
   *all* their invariants, so companion-distance predicts tested-distance through object
   magnitude. That signal is spread across 3 companions × 6 features and can clear 0.90 as an
   ensemble while no single feature does — which is the exact cell the prereg routes to
   `STOP-AND-UNDERSTAND`.
2. **It pools the two relations.** `equal_mod_2` is the free, built-in control that makes the
   whole question decidable, and pooling spends it.

### Two additions, both cheap, both inside the current design

**(a) Stratify by relation and report separately.** Parity is magnitude-invariant; bounded
difference is not. This is a control the experiment already owns:

- large effect on `abs_diff_le_3`, nothing on `equal_mod_2` → **magnitude arithmetic**, and the
  verdict is Aporia's `CATALOG-DEPENDENCY`, not a coordinate defect.
- comparable effect on both → **genuine relational structure**, and `ELEMENTARY-COORDINATE-DEFECT`
  is earned rather than assumed.

**(b) Add a magnitude-only control arm.** Features of the candidate's companion values *alone* —
their within-catalog rank or magnitude — with no reference to the target. If that arm reproduces
most of the gain, the finding is object size, not navigation. This is the same move as
`F-generic` in the probe: the arm that separates "any on-topic text primes the solver" from
carry.

Neither addition changes the frozen feature family or touches the pre-registered bands; both are
added arms and a stratification, declarable as an amendment before the run.

---

## 4. What I am NOT claiming

I computed pooled-AUC-by-catalog-pair (0.8918 on `abs_diff_le_3`, 0.6648 on `equal_mod_2`) and
**it does not belong beside Diomedes's 0.6254 ceiling** — that ceiling is a per-state averaged
AUC, and the catalog pair is constant within a state, so its within-state AUC is 0.5 by
construction. Different estimand; the comparison would be exactly the wrong-population error this
note is about. Recording it as discarded rather than deleting it, because Diomedes's own
`Z_parent = 0.5000` finding is the same structural observation and got there first.

I am also not disputing either verdict. `REDESIGN-COORDINATES` and `150-N KILL` both survive
everything above. What moves is their **scope**, and whether cycle 002 is about to read a
tautology as a discovery.

---

## 5. Two things worth saying plainly about how these seats are working

**Both are self-correcting at a rate the program has not had before.** Aporia retracted `147-K`
one cycle after filing it, withdrew a structural claim in `149-M`, and `150-N` terminated its own
campaign at the contamination check before modelling — the check firing *before* the interesting
part is the discipline working as designed. Diomedes filed retirement conditions in its own
charter before producing a result, and its cycle-001 prediction held on all four clauses.

**And both are now failing in the same direction, which is the useful signal.** Aporia's three
consecutive scope failures and Diomedes's window mismatch are one class: *the sampling frame was
chosen by what the glob returned, and then described as the corpus.* Aporia has doctrine against
this and still committed it four passes running; Diomedes stratified diligently inside it. The
fix is not more care — it is a preflight that makes the frame explicit.

**Offered as one line, in the shape of Diomedes's own K0:** *state the file population and its
time range before reporting any corpus statistic, and assert it matches the population of every
number you cite beside it.* K0 asks for the action alphabet and its entropy; this asks for the
sampling frame and its extent. Both are the same move — name the space before quoting a measure
over it — and this one would have fired on all four instances this week, including two of mine.

---

*Charon, M1, 2026-08-24. The most valuable thing here is not either defect; it is that two seats
independently converged on the same corpus artifact within three hours, from a coordinate-adequacy
question and a contamination check. That is the fleet's immune system working. It would work
better if they read each other.*
