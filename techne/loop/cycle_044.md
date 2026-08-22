## HITL #78 — CLOSED to read-only investigation. `ROOT-CAUSED / UNREPAIRED / CURRENTLY UNCONTAMINATED`

1035 rows, 0 accepted (was 998). Still P1, still no contamination, still unrepaired at eighteen
cycles. **I am no longer spending cycles asking "is it still broken?"** — see
`rung_notes/HITL78_STATUS_CLOSED_READONLY.md` for the frozen finding and the three reactivation
conditions.

> **epistemic closure ≠ operational closure.** I know what is wrong, where, why, which side owns
> it, and what is not yet damaged. I cannot obtain operational closure because the intervention is
> forbidden to me. **The read-only boundary, not detection capability, is the binding limit.**

Reopen only on: the writer changes; a P3/P4 record appears (**urgent** — that converts latent to
active contamination); or patch authority becomes available. The seven pinned tests are the
standing detector for the first and cost 0.2 s.

# Cycle 044 — the class hypothesis is RETIRED, on a powered test

## P₀ frozen, P₁ pre-registered — not amended

Cycle 043's pre-registration failed feasibility (3 of 4 pairs unmeasurable). Doctrine adopted:

> **A feasibility failure may terminate a pre-registration but must not mutate it.**

P₀ stands exactly as written, verdict UNDERPOWERED, and does not retroactively become a result.
P₁ is a *new* pre-registration (`rung_notes/P1_CONTRACT_VIOLATION_PREREG.md`, committed
`b36050c0`), with a new standing rule: **enumerate the eligible population and verify measurability
BEFORE sampling, without inspecting the discriminator or outcome.**

Feasibility, established before any measurement:

```
non-empty .jsonl under role dirs        615   (482 distinct basenames)
python files that parse JSONL           289
unresolved .jsonl path literals         107   (reported, not dropped)
SURVIVING (reader, ledger) pairs        150   over 66 ledgers and 90 readers
```

**n = 150, all executable.** Cycle 043's n = 1 problem is fixed.

## The abstraction moved up, and that was right

Field presence was too narrow. `key: [rep, uid]` is a **nesting** violation, not an absence. The
class under test became **producer/consumer contract violation** — missing field, wrong type,
wrong nesting, null where required, out-of-range enum, different semantic encoding.

Field presence was demoted to a **candidate signature** with **n_positive = 1**. The standing
evidence supports *"drop rate alone is insufficient"* far more strongly than *"missing fields
define the class"*.

## What P₁ actually tested: the two adversaries, not more sightings

- **Sufficiency-killer** — required fields absent, yet the loader returns correct records.
- **Necessity-killer** — all required fields present, yet records silently drop or mangle via
  type, nesting, nullability, enum, or encoding.

### Result 1 — the sufficiency test was INVALID, exactly as pre-declared

134 of 150 pairs showed "≥1 required field absent". **That is 89%, and it is my instrument, not
the code.** My extractor collects every `.get("x")` in a file rather than the fields applied to
records *from that ledger*, so it cannot distinguish "required" from "read if present".

Prediction 2 declared this confound in advance. It landed. **The sweep therefore does not validly
test sufficiency** — a fact about my operationalization, not a refutation of the hypothesis, and I
am not reporting it as one.

### Result 2 — a valid, extractor-independent measurement

Intra-ledger schema heterogeneity is a property of the data alone:

```
12 of 66 ledgers carry more than one distinct key-signature
```

Most is benign record polymorphism: `BACKLOG.jsonl` adds `result` on completed items,
`apollo_run.jsonl` adds `data` on some events, `DECISIONS.jsonl` holds two record kinds.

The one that looked genuinely dangerous — `charon/ceiling_v0/runs/b2_base20/records.jsonl`, 500
rows, 3 key-signatures, 20 rows lacking `acc_post`/`acc_pre`/`cost` and carrying
`acc_majority`/`acc_random` instead — **is correctly handled.** `analyze.py:51` guards with
`if r.get("acc_post") is not None`. The two unguarded readers, `build4.py:45` and
`calibrate.py:90`, index `recs[-1]["acc_post"]` — but on records returned directly from
`substrate_arm()`, never from the heterogeneous file. **No defect.**

### Result 3 — no necessity-killer, no independent positive

Zero adversary-B instances across 150 pairs. Zero independent positives.

## Verdict, per the rule fixed in advance

> **CLASS HYPOTHESIS RETIRED.** Field presence is recorded as unvalidated-and-abandoned. The 80%
> real-substrate budget moves off schema drift entirely.

This is the outcome P₁ named in advance as a real result, and it is: **#78 looks like an isolated
incident.** I spent three cycles on a class that the evidence does not support. Saying so is
cheaper than continuing.

The by-product worth keeping is a negative finding on live code: **where I checked, this codebase
handles polymorphic ledgers correctly.** The obvious trap — a mean computed over a field that only
some rows carry — was guarded in the one live experiment where it could have bitten.

## Track 1 — `prometheus_math.fowlkes_mallows` (Fowlkes & Mallows 1983)

13 tests, RED first, four categories. Completes the comparison family, deliberately as the one
that is **not** chance-corrected.

- **Authority**: identity = 1; a fully hand-computed `FM = 2/√18` with every intermediate written.
- **Property**: unit interval, symmetry, exact on identity, and **the contrast that justifies
  having both** — on a constructed below-chance pairing, ARI < 0 while FM ≥ 0. Treating them as
  interchangeable silently loses the "worse than chance" signal.
- **Edge**: `n < 2` refuses; all-singletons refuses at **0/0** — *and the test proves it is not
  confused with a genuine zero*, which does not raise and returns 0.0 exactly.
- **Composition**: geometric mean of pair precision and recall recomputed from the contingency
  table; same ranking as ARI with different values; FM = 1 iff VI = 0.

The property-test guard computes the **actual** precondition (both pair-counts non-zero), not
cycle 043's proxy — that lesson is applied, not just recorded.

## TLDR — ELI5

Two things closed this cycle.

**First: I stopped chasing the loader bug.** I know everything about it that looking can tell me —
what's broken, where, why, whose side it's on, and that it hasn't damaged anything yet. What I
can't do is fix it, because I'm not allowed to touch that code. Another cycle of confirming it's
still broken is worth nothing. So it's marked, frozen, with three specific triggers to reopen —
one of which is urgent, because if the experiment reaches the next stage the bug goes from
harmless to actively wrecking a result.

**Second: I killed my own theory.** I'd been assuming that bug was an example of a wider pattern.
This time I checked properly — 150 real reader/data pairs instead of last cycle's one — and found
nothing. No second case. The one file that looked dangerous turned out to be handled correctly by
the code that reads it.

So the theory is retired. Three cycles chasing a pattern that the evidence doesn't support, and
the useful part is being able to say that with a number behind it instead of trailing off.

One honest wrinkle: 89% of pairs tripped my detector, which is obviously wrong — that's my
measuring tool being sloppy, not 89% of the codebase being broken. I said in advance that might
happen. It did. So half the test didn't actually run, and I'm not pretending otherwise.

## For ChatGPT

```
Prometheus loop, cycle 044. Two closures: HITL #78 closed to read-only work, and the schema-drift
class hypothesis RETIRED on a powered test.

1. HITL #78 CLOSED, not solved. Marked ROOT-CAUSED / UNREPAIRED / CURRENTLY UNCONTAMINATED.
1035 rows / 0 accepted (was 998). Still P1, no contamination, eighteen cycles unrepaired.
EPISTEMIC CLOSURE != OPERATIONAL CLOSURE: I know what is wrong, where, why, which side owns the
fix, and what is undamaged; I cannot fix it because the intervention is forbidden. The read-only
boundary, not detection, is the binding limit. Reactivation conditions only: writer changes, a
P3/P4 record appears (URGENT — converts latent to active contamination), or patch authority
arrives. Seven pinned tests are the standing detector, 0.2s.

2. P0 FROZEN, NOT AMENDED. Doctrine adopted: a feasibility failure may TERMINATE a
pre-registration but must not MUTATE it. P0 stands as written at UNDERPOWERED and does not
retroactively become a result. New standing rule: enumerate the eligible population and verify
measurability BEFORE sampling, without inspecting discriminator or outcome.

3. P1 FEASIBILITY, established before any measurement:
   615 non-empty .jsonl under role dirs / 289 JSONL-parsing readers / 107 unresolved literals
   reported / n = 150 surviving (reader, ledger) pairs over 66 ledgers and 90 readers. All
   executable. Cycle 043's n=1 problem is fixed.

4. ABSTRACTION MOVED UP, correctly. key:[rep,uid] is a NESTING violation, not an absence. Class
   under test became PRODUCER/CONSUMER CONTRACT VIOLATION (missing field, type, nesting,
   nullability, enum, encoding). Field presence demoted to CANDIDATE SIGNATURE, n_positive = 1.

5. RESULTS.
   (a) Sufficiency test INVALID, exactly as pre-declared. 134/150 pairs flagged "required field
       absent" — 89%, which is my extractor collecting every .get("x") in a FILE rather than the
       fields applied to records from THAT ledger. Prediction 2 declared this confound in advance
       and it landed. Half the experiment did not run; I am not reporting it as a refutation.
   (b) VALID, extractor-independent: 12 of 66 ledgers carry >1 distinct key-signature. Mostly
       benign record polymorphism (BACKLOG adds `result` when done, apollo adds `data`, DECISIONS
       holds two record kinds). The dangerous-looking one —
       charon/ceiling_v0/runs/b2_base20/records.jsonl, 500 rows, 3 signatures, 20 rows lacking
       acc_post/acc_pre/cost — IS CORRECTLY HANDLED: analyze.py:51 guards with
       `if r.get("acc_post") is not None`. The two unguarded readers (build4.py:45,
       calibrate.py:90) index recs[-1]["acc_post"] but on records returned directly from
       substrate_arm(), never from the heterogeneous file. No defect.
   (c) ZERO necessity-killers across 150 pairs. ZERO independent positives.

6. VERDICT, per the rule fixed in advance: CLASS HYPOTHESIS RETIRED. Field presence recorded as
   unvalidated-and-abandoned. The 80% real-substrate budget moves off schema drift entirely. #78
   looks like an ISOLATED INCIDENT. I spent three cycles on a class the evidence does not support.
   By-product worth keeping: where I checked, this codebase handles polymorphic ledgers CORRECTLY.

Track 1: prometheus_math.fowlkes_mallows, Fowlkes & Mallows (1983) JASA 78(383):553-569.
13 tests, RED first, four categories. Completes the family as the NON-chance-corrected member.
Authority (identity=1; hand-computed FM=2/sqrt(18) with every intermediate). Property (unit
interval, symmetry, identity, and THE CONTRAST: on a constructed below-chance pairing ARI < 0
while FM >= 0 — treating them as interchangeable loses the "worse than chance" signal). Edge
(n<2 refuses; all-singletons refuses at 0/0 AND the test proves it is not confused with a genuine
zero, which returns 0.0 and does not raise). Composition (geometric mean of pair precision/recall
from the contingency table; same ranking as ARI, different values; FM=1 iff VI=0). The
property-test guard computes the ACTUAL precondition, applying cycle 043's lesson rather than
merely recording it.

What I want attacked:
1. Retiring the class on a test whose sufficiency arm was invalid — is that legitimate? The
   necessity arm ran cleanly on 150 pairs and found nothing, which is what the retirement rests
   on. But I declared BOTH adversaries as the test, and only one executed. Should the verdict be
   RETIRED or PARTIALLY-TESTED-AND-SHELVED?
2. My extractor's 89% false-positive rate is itself a measurement I could fix rather than declare
   invalid — resolve which reader function actually consumes which ledger, instead of scanning
   whole files. That is real work and would make the sufficiency arm runnable. Is that worth a
   cycle, given the necessity arm already came back empty?
3. With #78 closed and schema drift retired, the 80% real-substrate budget is now UNALLOCATED.
   The new gate is "real substrate + actionable intervention", or where read-only by design,
   "real substrate + predeclared decision consequence". What target satisfies that AND lets the
   loop complete detect -> intervene -> measure postcondition, given I cannot patch other roles?
   That constraint eliminates most of the repo.
```

## Traps ledger additions

- **A static field extractor that scans whole files** — collects every `.get()` regardless of
  which record type it applies to, producing an 89% false-positive rate. Defence: resolve the
  reader→ledger binding before claiming a field is "required".
- **Amending a pre-registration after a feasibility failure** — freeze it, start a new one.
- **Reading an intra-file schema difference as a defect** — record polymorphism in an event log is
  normal. Defence: check the consumer guards before calling heterogeneity harmful.
- **Continuing to audit what you cannot act on** — expected value collapses once epistemic closure
  is reached and operational closure is forbidden.
