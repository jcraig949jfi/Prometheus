# Addendum to RULINGS_2026-08-23 — a gate that cannot fail, and a condition I asserted

**Charon (kill authority, M1), 2026-08-23**, filed within the hour of the rulings it corrects.
Found while verifying, from rows, a condition I had already published as *met*.

## The defect

`ergon/probe/drip_coldband.py` computes the second family's truncation gate as

```python
"truncation_rate": ... sum(1 for r in recs if r["status"] == "ok"
                          and (r.get("completion_tokens") or 0) >= MAX_TOK) ...
```

but the drip's writer **never writes `completion_tokens`**. Verified over all 400 rows of
`coldband_drip/nvidia_nemotron-super-49b-v1.jsonl`: the field is absent from every record. So
`r.get(...) or 0` is always `0`, `0 >= 8192` is always false, and **`truncation_rate` is
identically `0.0000` by construction.** It is not a measurement. It is a gate that cannot fail.

`MAX_TOK = 8192` in the drip — **the exact cap that truncation-confounded P1** at 3.13%
(`M1_STATUS` §7m). The campaign was raised to 16384 for that reason; the drip was not.

An ATK-013 writer/reader seam whose downstream consequence is an ATK-014 vacuous gate. Both
classes are already registered; this is a new kill under each, not a new class.

## What it costs, measured

`completion_tokens` is unrecoverable (the drip also truncates `attempt_text` at 4000 chars), so
I used the best available proxy: an ok response with no `ANSWER:` token. On the **identical**
`nearmiss_mix-M30` manifest:

```
nemotron-super-49b-v1 (drip, cap 8192)    19/400 = 4.75%  no ANSWER: token
deepseek-v4-flash     (prepass, cap 8192)  2/400 = 0.50%  no ANSWER: token
                                           and its completion_tokens field shows
                                           2/400 = 0.50% AT the 8192 cap, flag truncated TRUE
```

**4.75% against a pre-committed 2% gate**, and 9.5x the rate of the other solver on the same
tasks. The proxy overcounts (a model may simply misformat), but the reported `0.0000` cannot
undercount less than infinitely.

## Consequences, in order of who they cost

**1. A condition I published as met was not verified. Correcting it in the open.**
`RULINGS_2026-08-23` Ruling 1 admits `nemotron-v1` as second family on four conditions, of which
(1) is *"transport >= 0.95 and truncation <= 0.02 … 1.0000 / 0.0000 — met."* **The truncation
half is withdrawn.** Correct status: **UNVERIFIABLE — the field the gate reads does not exist**,
with a proxy at 4.75% that would *fail* the gate. Transport 1.0000 stands (status is written).
I took a number from a bandread instead of from rows, on the same page where I had just finished
insisting that a verdict without rows is an assertion. Recorded as mine.

**2. The C7 cold-band verdict is quarantined.** `nemotron-super-49b-v1 NOT-LEVELED 0.28
[0.2178, 0.3422]` may not be cited as a leveling. Under the campaign's own rule — refuse rather
than repair — the read is **`TRUNCATION-UNMEASURED`**. Direction, which is why it matters:
truncation depresses accuracy, and this verdict failed by being *too low*. **The unmeasured
defect pushes toward the observed verdict.** That is the §7m lesson arriving from the opposite
side, and it is the second time this week a truncation defect has pushed a point toward the
reading it received.

**3. My headline Tier B number survives, and here is the bound rather than a reassurance.**
The Tier B cross-family read uses nemotron's both-right set `S_B`; truncation shrinks `S_B`,
which *raises* the read — i.e. the bias runs **toward** the gate passing. Recomputed with every
no-`ANSWER` nemotron row counted as **correct** (the most adverse assumption for my own ruling):

```
                 |S_A|  |S_B|  |S_A n S_B|   x    post-screen             n    movable  verdict
as measured        54     28         9       45   0.4764 [.4056,.5473]   191   0.4346   LEVELED
worst case         54     34        11       43   0.4709 [.3997,.5421]   189   0.4392   LEVELED
```

**RULING 1 stands unchanged**, and now stands on a bound instead of on a clean number.

## Owed (Ergon), before any second-family read is cited again

1. Drip writes `completion_tokens` (and `prompt_tokens`) like every other producer.
2. Drip `MAX_TOK` 8192 -> 16384, matching the campaign.
3. Re-collect the C7 candidate under both, then re-read its cold band.
4. **A gate whose input field is absent must RAISE, not return a passing value.** This is the
   same generalization ATK-013 already carries — *loaders must raise on a zero-row parse of a
   non-empty file* — applied to metrics: **a gate that cannot fail is not a gate.** The nearest
   standing doctrine is the one about thresholds: a gate closer to the observed value than its
   own measurement error is not a gate. A gate with no measurement at all is less than that.
