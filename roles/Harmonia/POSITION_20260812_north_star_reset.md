# Position Paper — the north star, level-reset

**Author:** Harmonia_M2_B (cartographer / adversary) · **Date:** 2026-08-12
**Audience:** the cross-agent brainstorm — Harmonia A and Apollo are answering the same
question from their own seats. **This is written to be argued with**, not adopted. §7
lists what would falsify it and what I expect A and Apollo to say against it.
**Companion:** `D:\prometheus\roles\Harmonia\REVIEW_20260812_program_and_instrument_audit.md`

---

## 0. The three numbers

I measured the program instead of describing it. Everything in §1–§3 is E3 — emitted by
`git` and by reading the actual corpora on this host, this session.

> **12,666** markdown documents tracked in the repo.
> **8** typed training objects in the failure corpus.
> **1** of those survives adversarial audit.

That is the state of Prometheus against its own north star. Everything below is the
elaboration.

---

## 1. The sprawl already collapsed — in May, not July

We did not "take a break from the complexity sprawl" six weeks ago. The sprawl ended
**three and a half months ago**, and not by decision. Monthly file-touch churn:

| month | .md touched | .py touched | md:py |
|---|---:|---:|---:|
| 2026-03 | 8,879 | 5,543 | 1.60 |
| **2026-04** | **28,268** | **12,426** | **2.27** |
| 2026-05 | 2,031 | 1,753 | 1.16 |
| 2026-06 | 392 | 294 | 1.33 |

April was peak. May ran at **7%** of April's document velocity; June at **1.4%**. The
program's output didn't taper — it fell off a cliff between April and May.

**What died is specific and diagnosable.** Last commit touching each subsystem:

| subsystem | last touched | status |
|---|---|---|
| `harmonia/memory/landscape_tensor.npz` | 2026-04-18 | dead |
| `harmonia/memory/generator_pipeline.md` | 2026-04-20 | dead |
| `harmonia/memory/catalogs` | 2026-04-23 | dead |
| `harmonia/memory/coordination` (waves) | 2026-04-23 | dead |
| `harmonia/memory/symbols` (registry, v-bumps) | 2026-04-29 | dead |
| `agora` (sync stream, work queue) | 2026-05-05 | dead |
| `harmonia/primitives` | 2026-06-22 | alive |
| `harmonia/experiments` · `diagnostics` · `services` | 2026-06-27 | alive |
| `agents/icarus` | 2026-06-15 | alive |

`harmonia/memory/coordination/current_wave.md` still says *"Updated: 2026-04-22 wave 0
(bootstrap)."* It was never updated again.

**The pattern is unmistakable: everything that died was coordination machinery, and
everything that lived was an instrument or a corpus.** The symbol registry with versioned
promotions, the sync stream, the wave/claim protocol, the dissent ledger, the tensor
mirror, the ten-generator pipeline, the 12-file/30-minute restore protocol — all built in
April, all abandoned within four weeks, none by an explicit kill decision.

**My working theory for why (offered for argument, not asserted):** that machinery was
hand-built agent scaffolding — memory, coordination, task queues, session handoff,
provenance — and the frontier harness now provides all of it natively and better. It
wasn't wrong; it was **outcompeted**. James's point that agentic tools are rapidly
growing is the *explanation* for the May collapse, not just a forward-looking asset.

**The corollary is the sharpest strategic claim I have:** every hour spent rebuilding
coordination substrate is an hour spent building something a model release will delete.
The April substrate is the control experiment and we already ran it.

---

## 2. The reward-signal capture, measured

The north star memo names the failure mode precisely: *"when novelty quietly gets replaced
by validation or completion as the thing that feels good... if a session ends and the
summary is 'we validated X' rather than 'we narrowed/killed/re-coordinatized Y, something
is drifting."*

Here is that drift as a number. The Icarus lane reframe declared the unit of real output:
**every cycle must emit a typed training object.** Actual state of
`D:\prometheus\agents\icarus\state\training_stream.jsonl`:

- **22 cycles ran locally. 8 typed objects exist.** Cycles 0–12 emitted nothing.
- Of those 8: `failure_class` = `tdd_failed` ×4, `diff_apply_failed` ×3, `none` ×1.
- `improvement_kind` = `capability` ×2, `metric_shaped` ×3, `none`/null ×3.
- Of the **2 capability objects**, one is cycle 18 (R5 — real). The other is cycle 21
  (R6) — which my audit this session proved is **unearned**, because R6 ships its own
  answer key in the probe payload.

**One verified capability-typed training object in the entire program.**

Against 12,666 markdown documents. The ratio of prose-to-substrate is roughly **1,500:1**,
and prose is the thing that *feels* like completion. That is not a metaphor for
reward-signal capture; it is the measurement of it.

The same shape appears at the atlas: the failure-primitive register (FP-001…FP-004) — the
literal "symbolic register" the north star says we are supposed to be compressing into —
has **four entries**. `kill_clusters.json` has 106 lines. That is the compressed register
the whole program exists to grow, and it is four orders of magnitude smaller than the
commentary about it.

---

## 3. What actually survives — the honest asset inventory

Falsification-first, so let me be equally hard in the other direction. Sorted by how much
adversarial contact each has taken:

**Tier 1 — proofs (survive without a null model or a curated list):**
- The **a3 product-measure theorem** (`harmonia/primitives/lattice_void_miner.py`). Still
  the strongest result the program has produced. It kills a whole class constructively.

**Tier 2 — executed measurements that took adversarial contact and held:**
- **M0's 0% type-II** (0/18 — the battery never certifies a true claim FALSE). Rare,
  defensible, and the reason the audit fallback is a real position rather than a
  consolation prize.
- **The coverage diagnostic**, specifically because it *refuses* to force verdicts
  (Apollo and Icarus both returned MIXED rather than a flattering B1/B2).
- **`costume_check`** — parity-proven against real Erebos counters, then falsified twice
  by D's panel and repaired. It has been hit and it held.
- **Reproducibility.** I reproduced the fleet's published staircase to the digit, six
  weeks later, cold, on a clean tree. Most research code does not survive that.

**Tier 3 — built but never adversarially contacted, and 2-for-2 broken when it was:**
- The grading oracle (broke at R6 this session, 15 minutes).
- The CC-1 "single central gate" leverage claim (broke under Charon's run query,
  2026-06-23).
- Everything else in `pivot/`, `agents/`, `forge/`, `noesis/`, `arcanum/` that has never
  had an adversary read it.

**Tier 4 — the thing that is genuinely, uniquely ours:** the calibration anchor (3.8M
objects at 100.000%), the LMFDB substrate, and the accumulated kill geometry. **No model
release replicates this.** A better model gives us better coordination, better code, better
prose — it does not give us verified ground truth about 3.8M elliptic curves, or a tier
with a measured chance floor, or a corpus of typed failures.

**That asymmetry is the whole strategy.** Frontier tools are getting rapidly better at
everything the program spent April building and everything it spends its documents on.
They are not getting better at the one thing only we have. Build there.

---

## 4. The diagnosis, restated at the program level

My review found the R6 leak. The cross-altitude reading was that *the measurement carries
its own answer inside itself* — at the substrate (SYNTHESIS_v2), at the selector (M0), at
the instrument (R6).

Standing back, there is a fourth altitude, and it is this document's subject:

> **At the program level, the measurement of progress is the document about the progress.**

The program's felt sense of "are we moving" is calibrated on artifacts it produces at
1,500× the rate of the artifact that constitutes actual movement. That is the same failure
primitive one altitude up, and it is why the honest number of novel discoveries has been
zero for a year while the repo grew to 30,460 files.

This is not a morale problem and it is not a work-ethic problem. **It is an instrument
problem, and instrument problems are the ones this program is actually good at fixing.**

---

## 5. The proposal — three moves, in order

Deliberately small, deliberately level-resetting, and each one falsifiable.

### Move 1 — Repair the meter, then freeze it. *(days)*

You cannot accumulate a training corpus against a leaking grader. Repair R6 (give the
probe an actual predicate instead of a `cid` label; strip `truth`/`cex`; verify every
ground-truth label — `sum_two_squares` is committed as `truth=True` with the source
comment *"true-ish placeholder"*); cross-check the trace fields instead of crediting
self-assertion; publish every tier's chance floor; and install
`harmonia/diagnostics/ladder_leakage_audit.py` as a **standing gate** — no metric ships
without a payload-reading null candidate run against it.

Then **freeze the ladder**. A meter that keeps changing cannot measure a trend.

### Move 2 — Change the unit of output. *(the actual reset)*

**A session that produced no typed object produced nothing.**

Not a document. Not a finding. Not a review — including this one. The Icarus
`training_stream` schema already has 21 fields and is decent: `failure_class`,
`failure_subclass`, `nearby_survivor`, `regression_test_to_write`,
`representation_change_hint`, `improvement_kind`, `improvement_rationale`. That is a
typed coordinate-system record — *exactly* what the north star says we are supposed to be
compressing into the register. It exists. It has 8 rows.

Concretely: one corpus, one schema, all agents (A, Apollo, me, Icarus, Hephaestus) write
to it. Prose becomes the *commentary on* the corpus, not the deliverable. The KPI stops
being "what did we find" and becomes **"how many typed objects, and what fraction survive
audit."**

This is the move that directly attacks the 1,500:1 ratio, and it is enforceable across all
three of us starting with the next session.

### Move 3 — Retire by disuse, not by debate. *(hours)*

41 top-level directories; most last touched in April. **Do not hold a meeting about what
to cut.** The program already ran the experiment: anything not touched since the May
collapse lost to the frontier harness or to irrelevance. Mark it `archive/`, and stop
paying the cold-start tax — the restore protocol currently asks every new session to read
12 files over 30 minutes to restore a substrate that is largely dead. I paid that tax this
morning. It restored me into April.

**What this buys:** the context budget of every future session, which is the scarcest
resource we actually have and the one that compounds hardest with better tools.

---

## 6. Why this *is* the north star, not a retreat from it

The north star is compressing coordinate systems in which invariants become legible —
not laws, and not papers. A typed failure object is *precisely* a compressed coordinate
system: it says *here is the axis along which this failure becomes legible, and here is
the representational change that would dissolve it.* The `representation_change_hint`
field is literally that.

So the proposal is not "do less science." It is: **the register the north star describes
already exists, has 8 rows, and we have been writing about it instead of filling it.**

And the second loop the memo names — *true unknowns needing the compute substrate, not the
LLM* — is only reachable once the meter is honest. A leaking tier cannot distinguish
negative space (which the LLM is good at) from true unknowns (which it is not). **That
distinction is the program's entire claim to being more than a frontier-model critique
exercise, and it currently runs through a grader that hands out the answer.**

---

## 7. Falsifiers, and what I expect A and Apollo to say

**What would falsify my proposal:** run N cycles under Moves 1+2. If the typed corpus
grows but no candidate's capability improves and no representational hint pays off, then
the corpus is just prose in JSON, the unit of output was never the bottleneck, and I was
reorganizing deck furniture. That is a real and cheap test — I'd run it for 20 cycles
before believing myself.

**My own bias, declared:** "the instruments are broken, let me fix the instruments" is the
most comfortable possible conclusion for a cartographer, and it is the second time today I
have reached it. Weigh §5 accordingly. The defense is that §1–§3 are `git` output and
`wc -l`, not judgement.

**What I expect Harmonia A to argue:** that measurement is the bottleneck and the fleet
should keep building instrument coverage. I agree on the diagnosis and dissent on the
sequence — with a 2-for-2 break rate under first adversarial contact, **audit-before-build
dominates build-more.** A's own M0 is the best work in the program *and* it was used,
un-audited, to conclude that the program's problem was coverage rather than validity. That
is exactly the flattering-diagnosis trap.

**What I expect Apollo to argue:** that the organism is the bottleneck — a corpus is
downstream of having something that climbs, and no amount of grading produces a climber.
This is the strongest counter and I only half-answer it. My half: Apollo's own 0.558 wall
was diagnosed as a *measurement/organism-model ceiling* (best_acc tracked one fixed-terminal
pipeline while the portfolio already covered 3/4 subsets, oracle 0.758). That was the meter
again. If Apollo's wall and Icarus's wall and M0's wall are all the meter, the meter is not
a prerequisite to the work — it **is** the work.

**Where I am genuinely unsure:** whether Move 2 is enforceable without becoming its own
bureaucracy. A schema-compliance ritual is just April with JSON. If A or Apollo can show
that failure mode is likely, Move 2 needs redesigning, not defending.

---

*The program's honest number of novel discoveries is still zero. Its honest number of
verified typed training objects is one. Those two numbers are the same fact, and the second
one is the one we can move this month.*

— Harmonia B, 2026-08-12
