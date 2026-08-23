# Cycle 049 — the constraint came off, and the fix I had been asking for was wrong

**James, 2026-08-23:** ruled #221 — *"you can act."* Also directed: *"Loop again but make a
pass over prior iterations, review what you did. Look for errors and omissions."*

Both tracks below are that directive. Prereg `aac126e0` committed before any measurement.

## 1. HITL #78 CLOSED — and the two-field fix would have been harmful on its own

Eighteen cycles of escalation (#78 → #192 → #202 → #221) asked for one thing: lift `rep`/`uid`
out of `key` in `load_prepass`, exactly as `campaign.py::best()` already does it. That fix,
applied alone, **would have leaked.**

**Three defects sat behind the 100% drop, not one:**

1. `rep`/`uid` read as flat fields; the campaign producer writes them inside `key`.
2. Count-family prose was routed by a **filename prefix** —
   `ledger_id.startswith("nearmiss")`. The campaign ledger carries **no `ledger_id` at all**,
   so it fell to the default `probe_prepass`, and fixing (1) alone would have shipped raw
   count-family attempt prose into `F-prom-retrieved` — precisely the channel
   `method_projection` exists to withhold (measured 45% vs 25% chance answer leakage).
   **The broken loader was accidentally acting as the firewall.**
3. The gold screen sat **downstream of the rep filter**, so it inspected none of the 1,604
   KEY-form rows. Screen coverage was silently zero for the file I had been escalating about.

**Fixed** (`c6736671`): `_prepass_identity` reads both wire forms with the contract written
into the docstring (HITL #209's ask, open since cycle 042); `withhold_prose` lets the caller
state the task family instead of inferring it from a filename; the gold screen moved ahead of
all filters after measuring blast radius first — **0 forbidden fields across all 3,456 live
rows**, so the reorder was measured-safe before it was made.

```
campaign p1_prepass   1248 rows:  0 -> 625 accepted,  0 shipping raw prose
nearmiss_mix-M30                200 -> 200   (FLAT path bit-for-bit unchanged)
probe_prepass                   126 -> 126   (FLAT path bit-for-bit unchanged)
ergon/probe/tests               163 passed, 0 failed   (8 new contract tests)
```

Three campaign dry-run tests went **red under the fix** and were **green-because-vacuous**
before: with an empty pool nothing was cited, so no firewall could fire. They caught the
`ledger_id` mismatch that fix (1) alone would have shipped.

## 2. The claim itself was a wrong-population error — mine

**"The loader throws away every row" is false**, and I said it for eighteen cycles.

```
FLAT form  {"uid","rep",...}   5 files  1,852 rows   loader CORRECT (accepts rep-1 exactly)
KEY  form  {"key":[rep,uid]}   2 files  1,604 rows   loader accepts ZERO
```

It was broken for **one producer's wire format**. I measured one file and quoted the result as
a property of the consumer — the **fourth** instance of `feedback_wrong_population_statistics`,
committed by the role that files that trap against everyone else. Memory updated.

The mis-framing was not cosmetic: it is *why* the fix I lobbied for was wrong. Had I enumerated
the producers at the seam in cycle 042, defect (2) would have been visible then.

## 3. Retrospective audit — two of three predictions falsified

Full findings: `rung_notes/CYCLE049_RETROSPECTIVE_FINDINGS.md`.

- **P1 — `O-PROMISE` >= 5: FALSIFIED at 4.** Reported as falsified rather than reclassifying
  the `O-DANGLE` to reach five.
- **P2 — a new `E-INFER`: HELD**, and it is §2 above.
- **P3 — the red counts do not reconcile: FALSIFIED.** They reconcile exactly:
  `30 → 29 → 28 → 29 → 30` across 045-048, each cycle's *before* equal to the prior cycle's
  *after*. **The name-diff discipline worked.** I predicted my own bookkeeping was sloppier
  than it was, and it wasn't.

**The four omissions:**

- **O-1 — Band H (H1, H2) was never built and never withdrawn.** The charter's Track 2 reads
  *"R0→R12, then Band H (H1, H2), then restart at R0."* R0-R12 finished at cycle 021. Band H
  is **never mentioned again in 48 cycles**. Canon §6 calls it *"James's thesis, formalized
  and falsifiable"*, and the charter explicitly allowed theory to substitute for building in
  the upper bands — so non-measurability did not block it. **This is the omission that matters.**
- **O-2** — the second pass restarted at **R3**, not R0.
- **O-3** — the R0 baseline lane promised in HITL #2 was never wired into
  `grading_oracle.py`, and the real fault is that it was **never withdrawn** when the read-only
  rule made it impossible. Silence is not a withdrawal.
- **O-4** — the Lane A/B reading experiment: pre-registered 041, queued 045, never run.
- **O-DANGLE** — `egglog` was installed at cycle 003 on a stated leverage claim and is
  referenced by **one demo file and nothing else**. Filed against my own #242 ask.

## 4. The near-miss that nearly became a false finding

I nearly filed *"`tensor_train.py` violates Standing Order #1 — it imports only numpy."*
It wraps quimb through a **lazy import inside `_mps`**. I had used top-level imports as a
**proxy** for "does this wrap the library."

That is the guard-on-a-proxy trap for the **fourth** time — cycles 043, 045, this near-miss,
and ergon's `ledger_id`-prefix gate found this cycle. **The fourth one is in another role's
code, which is the useful part: the trap is not idiosyncratic to me, it is what happens
whenever a cheap observable stands in for the real precondition.**

The prereg's self-guard — *every finding must diff against a checkable artifact, never a
re-reading of my own prose* — is the only reason the findings doc has no false entry.

## 5. Track 1 — the standing fix, built rather than declared

`techne/scripts/arsenal_red.py`. **No cycle in 48 recorded the command that produced its
"arsenal red" count.** The script states the scope in code, emits the invocation beside the
number, and diffs by **failing node id** rather than by count — because a count that holds at
29 while one test goes green and another goes red reads as "no change" and is not.

Also: a full-scope run is in flight and **I am not comparing its number to cycle 048's.** The
historical scope was never recorded and today's collection is wider (4,306 vs ~3,576).
Comparing them would be the same wrong-population error this cycle is about, committed twice
in one cycle. New baseline starts here, with its command attached.

## TLDR — ELI5

**The rule that I could only look, never touch, came off today. The first thing I fixed proved
I had been asking for the wrong fix for eighteen cycles.**

For months I have been reporting a bug: a piece of code that loads data was throwing away every
row, and I kept asking for a two-line fix. Today I could finally do it myself. So I looked
properly — and two things turned out to be wrong with what I had been saying.

First, the loader was never broken in general. There are seven data files; **five of them load
perfectly.** Only two use a different format, and those are the ones that dropped to zero. I had
measured one file and announced a fact about the whole loader.

Second — and this is the part that matters — **the bug was accidentally protecting something.**
The dropped rows contained the model's full written reasoning on a counting task, including its
answers. There is a filter that is supposed to strip that prose out, but the filter decides
whether to run **by looking at the filename**, and these files have no name it recognises. So
the moment I "fixed" the loader, all that answer-revealing text would have flowed straight into
a live experiment. The broken thing was holding the door shut.

I fixed all three problems, wrote the data format down so the next person cannot drift, and
checked every one of 3,456 rows before moving a safety check.

Then I audited my own 48 cycles for mistakes. I made three guesses about what I would find and
**two were wrong** — my bookkeeping was better than I expected. But I found four things I said
I would do and never did, and the biggest one stings: the plan said to work through the
reasoning ladder and then take on **James's own thesis** — and I finished the ladder, quietly
skipped his part, and never mentioned it again for 27 cycles.

## For ChatGPT

```
Prometheus loop, cycle 049. THE READ-ONLY CONSTRAINT CAME OFF, AND THE FIX I SPENT EIGHTEEN
CYCLES REQUESTING WOULD HAVE BEEN HARMFUL ON ITS OWN.

*** WHAT I HAD BEEN SAYING WAS A WRONG-POPULATION ERROR ***
Eighteen cycles: "the prepass loader throws away every row." FALSE. Measured over all SEVEN
prepass ledgers instead of the one that prompted it:
  FLAT {"uid","rep",...}   5 files 1,852 rows -> loader CORRECT, accepts rep-1 exactly
  KEY  {"key":[rep,uid]}   2 files 1,604 rows -> accepts ZERO
Broken for ONE PRODUCER'S WIRE FORMAT, never in general. Fourth instance of the
wrong-population trap, committed by the role that files that trap against everyone else.

*** THREE DEFECTS BEHIND THE 100% DROP, NOT ONE — AND THE DROP WAS A FIREWALL ***
1. rep/uid read flat; campaign.py writes them inside `key` (best() always read it correctly).
2. Count-family prose routed by a FILENAME PREFIX: ledger_id.startswith("nearmiss"). The
   campaign ledger carries NO ledger_id, so it defaulted to probe_prepass. FIXING (1) ALONE
   WOULD HAVE SHIPPED RAW COUNT-FAMILY PROSE into the F-prom-retrieved arm — exactly the
   channel method_projection exists to withhold (measured 45% vs 25% chance answer leakage).
   THE BROKEN LOADER WAS ACCIDENTALLY ACTING AS THE FIREWALL.
3. The gold screen sat DOWNSTREAM of the rep filter, so it inspected none of the 1,604
   KEY-form rows. Screen coverage was silently zero on the file I was escalating about.
POSTCONDITION: campaign 0 -> 625 accepted, 0 raw prose; FLAT ledgers 200->200 and 126->126
bit-for-bit; ergon/probe/tests 163 passed. Blast radius measured BEFORE reordering the screen:
0 forbidden fields across all 3,456 live rows. Contract now WRITTEN DOWN (HITL #209, open
since cycle 042). Three campaign dry-run tests went red under the fix — they were
GREEN-BECAUSE-VACUOUS before (empty pool -> nothing cited -> no firewall could fire).

*** RETROSPECTIVE AUDIT OF CYCLES 001-048: TWO OF THREE PREDICTIONS FALSIFIED ***
P1 O-PROMISE >= 5: FALSIFIED at 4 (reported as falsified rather than reclassifying an
   O-DANGLE to reach five).
P2 a new E-INFER: HELD — it is the loader claim above.
P3 red counts don't reconcile: FALSIFIED. They reconcile EXACTLY, 30->29->28->29->30 across
   045-048, each cycle's "before" equal to the prior's "after". The name-diff discipline
   worked; I predicted my own bookkeeping was sloppier than it was and it wasn't.
THE FOUR OMISSIONS:
 O-1 BAND H (H1,H2) NEVER BUILT, NEVER WITHDRAWN. Charter: "R0->R12, then Band H, then
     restart at R0." R0-R12 done at cycle 021; Band H never mentioned again in 48 cycles.
     Canon section 6 calls Band H "James's thesis, formalized and falsifiable", and the
     charter allowed THEORY to substitute for building in upper bands — non-measurability did
     not block it. I finished the ladder, skipped the operator's own thesis, said nothing.
 O-2 second pass restarted at R3, not R0.
 O-3 the R0 baseline lane (HITL #2) never wired into grading_oracle.py and NEVER WITHDRAWN
     when the read-only rule made it impossible. Silence is not a withdrawal.
 O-4 Lane A/B reading experiment: pre-registered 041, queued 045, never run.
 O-DANGLE egglog installed cycle 003 on a stated leverage claim; referenced by ONE DEMO FILE
     and nothing else. This weakens my own #242 dependency-install ask and is filed where
     James sees it BEFORE he rules.

*** THE PROXY TRAP, FOURTH INSTANCE, AND ONE IS SOMEONE ELSE'S CODE ***
I nearly filed "tensor_train violates Standing Order #1 — imports only numpy". It wraps quimb
via a LAZY IMPORT inside _mps. I used top-level imports as a PROXY for "does it wrap the
library". Cycles 043, 045, this near-miss, and ergon's ledger_id-prefix gate. THE FOURTH BEING
IN ANOTHER ROLE'S CODE IS THE USEFUL PART: the trap is not idiosyncratic to me. The prereg's
self-guard (every finding must diff against a checkable artifact, never a re-reading of my own
prose) is the only reason the findings doc contains no false entry.

TRACK 1: techne/scripts/arsenal_red.py — no cycle in 48 recorded the command behind its
"arsenal red" count. Scope stated in code, invocation emitted beside the number, diff by
FAILING NODE ID not by count. And I am explicitly NOT comparing today's run to cycle 048's:
the historical scope was never recorded and today's collection is wider (4,306 vs ~3,576), so
comparing them would repeat this cycle's own error twice in one cycle.

What I want attacked:
1. Is "the broken loader was accidentally acting as a firewall" a real causal claim, or am I
   dressing up a coincidence? The drop and the leak-guard have no design relationship.
2. Two of three retrospective predictions falsified in the direction of MY RECORD BEING
   BETTER than I predicted. Is a self-audit that clears its author evidence, or evidence that
   the audit's checkable-artifact guard was too narrow to catch the interesting failures?
3. O-1: I skipped the operator's own thesis and never said so. What mechanism catches a
   silently-dropped charter clause, given that nothing in 27 cycles surfaced it and only an
   explicit audit did?
```

## Traps ledger additions

- **A defect measured on one producer's records, quoted as a property of the consumer.** The
  loader was correct for 5 of 7 ledgers. Defence: **enumerate every producer at a seam before
  naming what is broken** — the fix derived from a one-file measurement may be the *wrong* fix,
  not merely an incomplete one.
- **A bug that is load-bearing for safety.** The 100% drop was suppressing a prose-leakage
  path. Defence: before fixing a drop/filter/failure, ask **what is currently NOT happening
  because of it**, and whether anything downstream has come to depend on that silence.
- **Green-because-vacuous tests.** Three dry-run tests passed only because the pool was empty.
  Defence: a test over a collection must assert the collection is **non-empty** first, or it
  cannot distinguish "correct" from "nothing happened."
- **A policy routed by a filename.** `ledger_id.startswith("nearmiss")` decided a *leakage*
  question. Defence: leak gates **allowlist by declared property, never denylist by name**
  (`feedback_handoff_seam_inverted_doctrine`) — and the caller that knows the property states it.
- **Silence as withdrawal.** O-3 was promised, became impossible, and was never retracted.
  Defence: a commitment that becomes structurally impossible must be **explicitly withdrawn in
  writing**; going quiet leaves it live on the record and un-actioned by anyone.
- **A reported number with no recorded invocation.** 48 cycles, three different red counts, no
  command. Defence: **every reported count ships the command that produced it**, and diffs go
  by name, not by count.
