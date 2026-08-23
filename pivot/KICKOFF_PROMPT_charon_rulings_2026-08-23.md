# Kickoff — Charon (kill authority): four rulings the probe is blocked on

**For:** Charon (M1) · **cc:** Harmonia B (independent, M2) · **From:** James (HITL)
**Date:** 2026-08-23 · **Prepared by:** Ergon (driver) — I am a conflicted party on items 2–4;
treat my recommendations as testimony, not as findings.

---

## 0. One-paragraph state

The free-host decisive campaign ran its full P1 pre-pass and **halted itself rather than
advance**. Everything below is $0 — the free lane turns out to serve **>1,000 long calls/day**
on `deepseek-v4-flash` (the "~40/day" figure the fleet planned against was nemotron's, and was
wrong by 25×). Nothing here is blocked on money. It is blocked on **four rulings that are
yours**, and on an exit review only you and Harmonia B can perform.

## 1. Exit review #3 — the P4 gate (chartered; prompt already written)

`pivot/KICKOFF_PROMPT_exit_review_3_charon_2026-08-21.md`, charter item R2-1. Single invariant:
*treatment identity must be computationally unavailable after semantic content is removed.*
Harmonia B runs it independently on M2; **do not read her artifacts dated after 2026-08-19 until
yours is committed.**

The pipeline is materially different from when that prompt was written — the campaign now
enforces a truncation gate, a three-valued band verdict, durable appends, and a transport floor,
and `ergon/probe/campaign.py` has an end-to-end dry-run test. **Re-read the code, not the
prompt's description of it.**

**If both #3 reviews PASS**, you create `ergon/probe/ledgers/campaign/RE_REVIEW_SIGNOFF`. That
file is the only thing gating P4 (the decisive arms). Not on your PASS alone.

## 2. Co-sign the A4 interpretation amendment

`pivot/PREREG_METABOLIZATION_PROBE_v1.md` §6.3. Charter R2-2 requires it to land **before** Tier
B. I co-signed on 2026-08-21 **with a provenance correction**: two passages are *not* charter-
verbatim (a scoping parenthetical and a sentence bounding heredity/transfer claims). Both are
strict tightenings sourced to already-adjudicated text in the same document, and I adopted them
as tightenings with sources named rather than as charter text. **Check that correction and
either countersign or refuse it.** P4 is gated on your co-sign in addition to the sign-off above.

## 3. THE RUNG RULING — route (a) or (b)

Full evidence: `ergon/probe/ESCALATION_P1_BAND_2026-08-21.md` (pre-filed at n=395 *before* the
data existed, commit `70459647`; the prediction held).

```
                       raw point   manifest 95%        straddles  n_req   movable   verdict
M20  free  n=620        0.5823    [0.5434, 0.6211]      YES       2969    0.3468   UNDECIDED-UNDERPOWERED
M30  free  n=200        0.5000    [0.4307, 0.5693]      no          97    0.3950   LEVELED
M30  paid  n=200        0.5000                                                     (comparator; hosts never pooled)
```

- **M20 cannot be decided by this manifest** — it needs n≈2969, 4.8× what we have. It fails on
  decidability alone; its dispersion term passes.
- **M30 levels cleanly on the free host**, dead centre, decidable at n≈97. Free M30 equals paid
  M30 **exactly**, so the host delta at this rung is **zero**.

I did **not** advance to M30 myself: my own committed rule says the rung advance is yours because
sweep-until-in-band inflates false-accept 3.9× (HB-R2). I only *measured* it, which executes your
own "measure all pre-declared rungs" ruling (§3.1 ruling 2). **The selection is the ask.**

**My recommendation, offered as a conflicted party:** route (b), M30. But see item 4 first,
because it may make this ruling moot.

## 4. THE RULING THAT MAY OUTRANK ALL OF THE ABOVE

**Is the Tier B post-screen band read reachable in principle on this family?**

HB-R1: at one family the lenient screen is a diagnostic and the band is read raw; **at Tier B
(≥2 families) the band is read post-screen.** Post-screen numbers:

```
                raw       post-screen    floor
M20  n=620     0.5823       0.2684        0.35     FAILS
M30  n=200     0.5000       0.3007        0.35     FAILS
```

**Neither rung meets the Tier B floor.** M30 gives a clean `LEVELED` at Tier A and still would
not level at Tier B. The screen removes both-right items, so

```
post-screen acc = (rep1-right AND rep2-wrong) / (discordant + both-wrong)
```

which clears 0.35 only when the task set is dominated by *unstable* items rather than
*consistently failed* ones.

**Correction to my own analysis, so you do not inherit it:** I argued a harder rung would push
post-screen *further under* the floor. It did not — 0.2684 → 0.3007, upward. The ratio
`D/(D+W)` fell as I said (0.607 → 0.552), but the share of discordant items with rep-1 correct
(44% at M20, 54% at M30) swamps the structural term at these sample sizes. **My mechanism was
real; my direction was wrong.** Do not lean on it for direction — only for the existence of the
tension.

What survives is the fact, not the model: **two rungs, both failing the same floor, one of them
otherwise perfect.** If the Tier B post-screen band is not reachable on this family, then no rung
choice fixes it and the defect is in the **design** — the band (HB-R2) and the screen (HB-R1)
were specified against different populations without anyone checking that a common solution
exists. That is charter **R2-1** territory: *re-pose the experiment, do not patch it.* Item 3
becomes moot in that case, which is why this one is listed after it but should be ruled first.

## 5. R2-6 — the transfer comparator (the D2/D3 blocker; yours)

D2/D3 asks the North Star question: does the year of accumulated residue carry anything? It is
**data-feasible and free**, and blocked only on R2-6 — what plays F-null's role where a
task-specific null cannot exist.

Groundwork is done and is counts, not design:
`ergon/probe/CORPUS_CHARACTERIZATION_FOR_R2-6_2026-08-22.md`. Full 165-batch scan,
**132,312,039 REJECTED records, 43 cells, 131,649 patterns**. The load-bearing findings:

- **68% of the corpus (89.9M records) sits in cells whose ENTIRE failure vocabulary is ≤8
  patterns (≤3 bits); 12.6% in cells with exactly ONE pattern (0 bits).** The designated
  failure signature is nearly empty for most of the corpus.
- `a1` and `f1` have **identical** vocabularies (Jaccard 1.0000), so the cross-generator null I
  proposed is cosmetic at the signature level.
- But `canonical_claim_text` and `claim_payload` are **100% populated** (`step_trace` 17.2%).
  The *record* is not 2 bits; the *designated signature* is.

**Health warning on that document:** an earlier 6-batch sample in the same file reached the
opposite conclusion and is marked withdrawn — a contiguous head-of-file window saw few
generators and missed `f1` entirely. **Cite full-scan numbers only (§3d).**

This largely pre-answers the verdict-level arm of **R2-5** (mine, ordered after Tier B): a D2/D3
keyed on `kill_pattern` retrieves a near-constant. I have recorded that and not acted on it.

## 6. What is running while you rule

- **Campaign** — halted at P1, makes **zero API calls** per firing while held.
- **M30 cold-band** — complete, LEVELED, committed.
- **Second family (C7)** — `nemotron-super-49b-v1` at **380/400** rows, finishing on its own.
- Nothing needs babysitting; nothing is spending money.

## 7. Order I would take them in

1. **Item 4** (post-screen reachability) — may moot item 3.
2. **Item 1** (exit review #3) — the only P4 gate, and independent of everything else.
3. **Item 3** (rung) if item 4 leaves it live · **Item 2** (co-sign) — cheap, ~15 lines.
4. **Item 5** (R2-6) — the biggest prize, and the only one pointed at the North Star.

*Ergon is the driver and a conflicted party on 2–4. Every number above is regenerable from a
committed command; where I have been wrong this week I have marked it in place rather than
quietly restating it.*
