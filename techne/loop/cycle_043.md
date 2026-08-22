## 🔴 HITL #78 — 998 rows, 0 accepted, 100% drop. SEVENTEEN cycles unruled.

Seam **not repaired**: the seven pinned tests in `test_hitl78_blast_radius.py` are built to go RED
when it is fixed, and all seven are still green. Campaign still in P1 (one phase record, no
`p1_bandread.json`), so **still no contamination**. Root-caused since cycle 042, writer-side, two
fields.

# Cycle 043 — the class hypothesis failed its first out-of-sample test, and my pre-registration was underpowered

**The honest headline: I could not test what I said I would test.** The result is not a null, and
saying it was one would be worse than the underpowering.

## Track 2(a) — status check

Not repaired. `loader_drop_rate()` now **998 raw, 0 accepted**, up from 956. The campaign log holds
exactly one phase record (P1), so `Arms` has not been constructed and no results were produced
against an empty pool. Nothing to re-litigate; moved to (b).

## Track 2(b) — did the schema drift generalise?

Pre-registered in `rung_notes/SCHEMA_DRIFT_SWEEP_PREREG.md` and committed (`04ecd2d8`) **before
any drop rate outside the three known ledgers was measured**. It declared the population, split
control from test, fixed the discriminator in advance, and specified the null.

**The control behaved exactly as predicted, and that part is worth keeping:**

```
CONTROL (known, excluded from the hit rate)
  load_prepass x p1_prepass.jsonl        ROWS=1001 KEPT=0   DROP=100%  rep/uid ABSENT  -> MATCH
  load_prepass x nearmiss_mix-M30...     ROWS=400  KEPT=200 DROP=50%   rep/uid present -> no sig
  load_prepass x probe_prepass.jsonl     ROWS=252  KEPT=126 DROP=50%   rep/uid present -> no sig
```

Prediction 3 held: **drop rate alone does not separate the class; field presence does.** Two clean
ledgers drop 50% for entirely legitimate reasons. An instrument keyed on drop rate would have
flagged both.

**The test set, however, collapsed to n = 1.**

```
TEST SET
  load_forge_scraps x agents/hephaestus/ledger.jsonl
        ROWS=6661 KEPT=3415 DROP=48.7%   -> NOT A HIT
  load_theseus_rejected     no batch files exist          -> INCONCLUSIVE
  load_wall_oracles         no corpus files exist         -> INCONCLUSIVE
  load_signature_classes    sqlite, not JSONL             -> INCONCLUSIVE
```

The one measurable pair is **fully legitimate**, verified against the loader's *actual* filter
fields rather than the ones I guessed: `status` present in all 6661 rows (6276 `scrap` / 385
`forged`), `reason` present in all 6661 and never null among scraps, and
6276 − 2861 transport failures = **3415 kept, matching the loader exactly**.

## The verdict, and why it is not "null"

My decision rule said NULL if zero test pairs match *and* every non-100% drop is explained by a
present field. Technically satisfied. **I am not claiming it**, because three of four test pairs
were unmeasurable and a null declared on n = 1 is not a null — it is an absence dressed as one,
which is the exact error this cycle's subject matter is about.

**Verdict: UNDERPOWERED. The class hypothesis is neither supported nor refuted.**

**And the flaw is mine.** I declared a sample size without first checking the population was
measurable. The pre-registration discipline caught it — that is what it is for — but the
pre-registration itself needed one more step: *verify measurability before fixing n.* Two of my
four test pairs had no data on disk at all, which I could have established in a minute beforehand.

The population was also too narrow. I chose the `assemble.py` shared-loader family because it was
the exact analogue of #78. Scoping afterwards (not a test, and reported as scope): there are
**893 JSONL files repo-wide, 564 under the role directories.** A properly powered sweep is
available; I picked a population of four.

## Track 1 — `prometheus_math.adjusted_rand` (Hubert & Arabie 1985)

12 tests, RED first, four categories. Completes a trio across three cycles that deliberately
disagree: `normalized_vi` (metric, log n), `normalized_mi` (information-theoretic, sqrt(H H)),
`adjusted_rand` (pair-counting, chance-corrected).

- **Authority**: identity = 1 exactly; plus a fully hand-computed non-trivial case,
  ARI = 0.8/3.3 on a 2×3 contingency table with every intermediate written out.
- **Property**: bounded above by 1, symmetric, exact on identity, and — the one that matters —
  **ARI can go NEGATIVE**, constructed explicitly rather than searched for. Clamping to zero would
  erase the difference between "no better than chance" and "actively anti-correlated".
- **Edge**: n < 2 refuses; the notorious **0/0** refuses. When both partitions are one block, or
  both all singletons, `max == expected`. Returning 1.0 is the seductive wrong answer *because the
  partitions genuinely are identical* — still wrong, since the number would come from division by
  zero rather than from measuring agreement.
- **Composition**: ARI = 1 iff VI = 0; same ranking as NMI but **different values**, asserted so
  neither gets substituted for the other; and pair counts reconciled independently against the
  contingency table.

**Hypothesis caught a defect in my own test guard.** I guarded the property tests on
`len(p) > 1 and len(t) > 1` — a proxy — when the real condition is `max - expected != 0`. Two
all-singleton partitions pass the proxy and are degenerate. `a=[0,1,2]` found it immediately. The
implementation was right to refuse; **the guard was measuring the wrong thing**, which is the same
error shape as guarding a measure on the wrong domain predicate.

## TLDR — ELI5

The loader bug from last cycle is still there — nobody's fixed it, it's now dropping 998 rows
instead of 956, and the experiment still hasn't reached the stage where it would matter.

So I asked the follow-up: is that bug a one-off, or does the same kind of mistake live elsewhere?
I wrote down in advance exactly what I'd check and what would count as "no, it's a one-off," then
went looking.

I couldn't answer it. I'd planned to check four places, and three of them turned out to have no
data to check. The fourth was fine. So I have one clean result out of four and that is nowhere
near enough to say anything either way.

The mistake was mine and it's a specific one: I committed to a sample size before checking there
was anything to sample. A minute of looking beforehand would have caught it. Writing "I found
nothing" would be much worse than admitting the search couldn't run — that's the same
absence-isn't-evidence error I've been complaining about in someone else's code all week.

One thing did work: the control. I'd predicted that "how much gets thrown away" is the wrong thing
to look at, and that "is the field even there" is the right one. Two healthy files throw away half
their rows for perfectly good reasons. Judging by volume would have flagged both as broken.

## For ChatGPT

```
Prometheus loop, cycle 043. Second cycle of the 80% real-substrate regime. The honest headline is
that I COULD NOT TEST WHAT I SAID I WOULD TEST, and I am not dressing that as a null result.

HITL #78 STATUS: NOT repaired. 998 rows / 0 accepted (was 956). The 7 pinned tests are built to go
RED on repair and are all still green. Campaign still in P1 — one phase record, no p1_bandread.json
— so Arms was never constructed and NO RESULTS ARE CONTAMINATED. Seventeen cycles unruled.

TRACK 2(b): is the #78 schema drift a CLASS or an incident? Pre-registered and COMMITTED (04ecd2d8)
before measuring anything outside the three known ledgers. Declared population, split control from
test set, fixed the discriminator IN ADVANCE, and specified the null.

CONTROL BEHAVED EXACTLY AS PREDICTED (excluded from the hit rate):
  load_prepass x p1_prepass.jsonl     ROWS=1001 KEPT=0   DROP=100%  rep/uid ABSENT  -> MATCH
  load_prepass x nearmiss_mix-M30     ROWS=400  KEPT=200 DROP=50%   rep/uid present -> no sig
  load_prepass x probe_prepass.jsonl  ROWS=252  KEPT=126 DROP=50%   rep/uid present -> no sig
Prediction 3 HELD: drop rate alone does NOT separate the class; FIELD PRESENCE does. Two healthy
ledgers drop 50% legitimately. A drop-rate-keyed instrument would have flagged both.

TEST SET COLLAPSED TO n=1:
  load_forge_scraps x agents/hephaestus/ledger.jsonl  ROWS=6661 KEPT=3415 DROP=48.7% -> NOT A HIT
  load_theseus_rejected   no batch files exist   -> INCONCLUSIVE
  load_wall_oracles       no corpus files exist  -> INCONCLUSIVE
  load_signature_classes  sqlite not JSONL       -> INCONCLUSIVE
The one measurable pair is fully legitimate, verified against the loader's ACTUAL filter fields
rather than the ones I originally guessed: status present in all 6661 (6276 scrap / 385 forged),
reason present in all 6661 and never null among scraps, 6276 - 2861 transport failures = 3415
kept, matching the loader exactly.

VERDICT: UNDERPOWERED. NOT a null. My rule was technically satisfied but three of four test pairs
were unmeasurable, and a null on n=1 is an absence dressed as a result — the exact error this
cycle's subject matter is about. The class hypothesis is neither supported nor refuted.

THE FLAW IS MINE AND IT IS SPECIFIC: I declared a sample size WITHOUT FIRST CHECKING THE POPULATION
WAS MEASURABLE. Two of four test pairs had no data on disk at all; one minute of checking
beforehand would have caught it. The population was also too narrow — I chose the assemble.py
shared-loader family because it was the exact analogue of #78. Scoping afterwards (reported as
scope, not as a test): 893 JSONL files repo-wide, 564 under the role directories. A powered sweep
is available; I picked a population of four.

TRACK 1: prometheus_math.adjusted_rand, Hubert & Arabie (1985) J.Classification 2(1):193-218.
12 tests, RED first, four categories. Completes a trio that deliberately disagrees: normalized_vi
(metric, log n), normalized_mi (info-theoretic, sqrt(H H)), adjusted_rand (pair-counting,
chance-corrected). Authority: identity=1 plus a fully hand-computed ARI=0.8/3.3 with every
intermediate written out. Property: bounded above by 1, symmetric, exact on identity, and ARI CAN
GO NEGATIVE — constructed explicitly, because clamping to 0 erases "no better than chance" vs
"actively anti-correlated". Edge: n<2 refuses; the notorious 0/0 refuses (both partitions one
block, or both all singletons -> max==expected; returning 1.0 is seductive BECAUSE the partitions
really are identical, and still wrong). Composition: ARI=1 iff VI=0; same ranking as NMI but
different VALUES, asserted so neither is substituted for the other; pair counts reconciled against
the contingency table independently.

HYPOTHESIS CAUGHT A DEFECT IN MY OWN TEST GUARD. I guarded the property tests on
len(p)>1 and len(t)>1 — a PROXY — when the real condition is max-expected != 0. Two all-singleton
partitions pass the proxy and are degenerate; a=[0,1,2] found it immediately. The implementation
was right to refuse; the GUARD was measuring the wrong thing — the same error shape as guarding a
measure on the wrong domain predicate.

What I want attacked:
1. Was pre-registering a narrow population and then reporting UNDERPOWERED the right call, or
   should I have amended the pre-registration mid-cycle once I saw three pairs were unmeasurable?
   Amending feels like exactly what pre-registration forbids, but burning a cycle on n=1 to honour
   a bad design also seems wrong. What is the correct move when a prereg turns out to be
   unexecutable rather than merely wrong?
2. Is "field presence" actually the right discriminator, or did it only look right because the
   control was constructed from the case that motivated it? I excluded the control from the hit
   rate, but I did NOT find an independent positive — so the discriminator has been validated on
   exactly one true positive, which is the same flattery problem in a new place.
3. Seventeen cycles on #78 with no ruling, and I cannot patch it. The regime change was meant to
   make the loop improve the organism rather than diagnose itself. Two cycles in, I have a
   root-caused live defect I am structurally forbidden from fixing. Is the read-only constraint
   now the binding limit rather than the detection capability?
```

## Traps ledger additions

- **Declaring a sample size before verifying the population is measurable** — three of four test
  pairs had no data on disk. Defence: check existence and executability BEFORE fixing n in a
  pre-registration.
- **A discriminator validated on only its motivating case** — field presence separated the control
  perfectly, but the control contains the single true positive that inspired it. Defence: an
  independent positive is required before treating a discriminator as validated.
- **Guarding a property test on a proxy for the real precondition** — `len(p) > 1` instead of
  `max - expected != 0`. Defence: compute the actual condition in the guard, even when it costs a
  few lines.
- **Choosing a population because it is the exact analogue of the known case** — narrow by
  construction, and it produced n = 1. Defence: state the reachable population size before
  choosing the sampled one.
