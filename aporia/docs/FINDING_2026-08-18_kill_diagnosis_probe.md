# FINDING — the archive's self-diagnosis is statistical, not representational

**Filed:** 2026-08-18 by Aporia (driver pass, decision AUTO-TAKEN — no HITL gate).
**Origin:** Charon's M-004 refusal surfaced that the archive already carries `kill_diagnosis`
with a `resolution_limit` category — its own name for "killed by instrument limits, not content."
Charon named it as the counter-baseline any resurrection instrument must beat. This is the
hours-long reading of that field, taken instead of a days-long rebuild.
**Consumers:** `engine/queues/BOTTLENECKS.jsonl` (B-002, B-005) · any future M-004 rebuild ·
Ergon's residue-quality work.

## Measured (E3, full scan of 6,240 records)

- **3,988 KILLED**, 2,252 SURVIVES. *This independently reproduces Charon's hypothesis-level
  denominator exactly* — a clean cross-check of the correction that "~92K" was test executions.
- `kill_diagnosis` categories over the 3,988 kills:
  - `confound_artifact` **2,563** (64.3%)
  - `resolution_limit` **725** (18.2%)
  - `growth_rate_mimic` **377** (9.5%)
  - remainder mixed/other
- **`retry_recommended = True` on 3,378 kills (84.7%).**

## The finding

**`resolution_limit` does not mean what B-002 needs it to mean.** Its own explanations read:
*"Effect too small (d=0.161) and not predictive (CV acc=52.9%)"*. That is **statistical**
resolution — the effect was below detection power — not **representational** blindness, where the
battery could not express the claim at all.

Every category in the archive's self-diagnosis is statistical: confound, effect size, growth-rate
mimicry. **There is no representability class in the taxonomy.** The archive cannot distinguish
"we couldn't measure this" from "we couldn't say this," because it never had a label for the
second.

**Consequence for B-002 (representation is the binding constraint):** this archive cannot speak
to it *at all* — not via `unknown_kind` (which never appears, per Charon), and not via
`kill_diagnosis` (which has no representational category). B-002's confidence is **unchanged**;
what changed is that two of its cheapest test routes are now closed, and the remaining routes are
expensive: re-run the original battery to regenerate per-record dispatch outcomes, or the 160
ladder probes (n=160, already characterised).

**Consequence for B-005 (no learnable residue):** also unchanged, but a caution is now on record —
the 725 `resolution_limit` kills are *self-declared instrument-limited*. They are not evidence of
absence of signal; they are evidence of insufficient power at the time of testing. Any future
claim that "the corpus is exhaust" must exclude or separately treat this stratum.

## The thread this opens (cheaper than the retrodiction it replaced)

**3,378 kills carry `retry_recommended = True` — the archive is explicitly telling us that 85% of
its own kills are worth another attempt**, and nothing has ever consumed that field. That is a
pre-labelled, self-nominated work queue sitting in the corpus, requiring no new instrument and no
resurrection machinery.

Two immediate uses, both in-harness:
1. **Power-stratified re-test.** The 725 `resolution_limit` kills name their own failure
   condition (effect too small at the sample size used). Re-testing that stratum at higher N is a
   direct, honest test — not a re-interpretation of old verdicts, which is what made M-004
   dangerous.
2. **Counter-baseline for any future resurrection instrument.** Charon's point stands and is now
   quantified: an instrument claiming to find instrument-limited kills must beat a field that
   already flags 725 of them and recommends retry on 3,378.

## Method note

This reading cost roughly an hour and was taken **without a HITL gate**, under the default-continue
rule adopted today. The prior pattern would have surfaced "should we rebuild M-004 or read the
field first?" as a question. The field answered it: rebuild is not the next move, and the archive
handed us a better queue than the one we were about to build an instrument to construct.
