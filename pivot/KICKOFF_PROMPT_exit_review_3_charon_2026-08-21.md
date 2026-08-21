# Kickoff — Charon: Tier-A Exit Review #3 (single invariant)

**For:** Charon (kill authority, M1) · **From:** James (HITL) · **Date:** 2026-08-21
**Charter authority:** `pivot/ROUND2_CHARTER_2026-08-20.md` item R2-1.
**Provenance declaration (read first):** this prompt was drafted by Hephaestus, the probe's
**conflicted residue supplier**. The invariant below is chartered text he did not author (it is
the external review's, adopted by James). Treat this prompt as **minimum scope, not ceiling** —
you are the kill authority; attack anything you find, prompted or not. If you believe this
prompt itself steers you away from a defect class, say so in your deliverable.

---

## The single invariant

Both prior exit reviews killed the pilot through **arm-identifying measurement confounds**
(serialization structure; token-length asymmetry). Exit review #3 tests ONE thing:

> **Treatment identity must be computationally unavailable after semantic content is removed.**

Not "hard to detect." Not "classifier accuracy is low." *Unavailable.*

## Independence rule

Harmonia B is running this same invariant independently on M2. **Do not read any Harmonia B
artifact dated after 2026-08-19 until your review is committed.** Your two reviews are only
worth two reviews if they collide with the pipeline from different angles. The prior kills
(serialization; token terciles) are known to both of you — re-verifying they stay fixed is
necessary but scores as regression-testing, not as this review. New non-content features are
where your attention goes.

## What you attack

The pipeline Tier B will actually run — current state, free-host pin:
1. `ergon/probe/campaign.py` — read first; note the phase gates and the M20 manifest + host pin.
2. The packet path: `ergon/probe/schema.py`, `extract.py` (frozen `_VERDICT_TOKEN` regex),
   `assemble.py`, `r3_controls.py`, `task_gen_v3.py`, `chain_run.py`.
3. Rendered packets for every arm (generate them; do not trust descriptions of them).

## Method (machine attack, not reading)

1. **Strip semantic content** from every arm's rendered packets using a stripper YOU write
   (do not reuse the pipeline's own redaction — that would test the pipeline with the
   pipeline). What remains: token counts, message structure/count, field ordering, JSON/text
   framing, whitespace patterns, role structure, metadata, truncation behavior, position of
   key information, any timing/routing traces the ledgers record.
2. **Train arm classifiers** on the residue (anything simple and standard — logistic over
   n-grams/feature vectors is fine; local compute only, $0). Report per-arm-pair accuracy with
   a permutation-null CI, on held-out packets.
3. **Positive control first (mandatory):** plant a deliberate arm-identifying leak into a COPY
   of the packets and confirm your attack catches it. If your attack cannot catch a planted
   leak, your attack is invalid — fix the attack before drawing any conclusion. A meter without
   a positive control is not a meter (constitutional).
4. **Regression check** the two known kills stay dead on the current pipeline (serialization
   split; token-tercile DiD on the free-host M20 packets).

## Verdicts (preregistered here, before you look)

- **PASS** — positive control caught; classifiers at permutation-null on all arm pairs; both
  regressions hold. State it as: *treatment identity computationally unavailable in the tested
  feature set* (list the feature set — the claim is bounded by it).
- **FAIL (defect found)** — any classifier beats the null: name the feature, show the
  reproduction command, type the defect against `attacks/REGISTRY.md` (likely ATK-001/ATK-002,
  or mint a new entry with an EXECUTABLE probe).
- **Stopping rule (charter R2-1, binding):** a **third distinct defect class** means the
  design, not the plumbing, is the problem — **stop; do not propose a patch;** the experiment
  gets re-posed, not improved in place.

## Deliverable + gates you control

1. Commit your review as `charon/probe/TIER_A_EXIT_REVIEW_3_CHARON_2026-08-21.md` (convention
   of your #2 review), with every load-bearing number regenerable by a committed command (E3).
2. **If PASS and Harmonia B's #3 is also PASS:** as kill authority, create
   `ergon/probe/ledgers/campaign/RE_REVIEW_SIGNOFF` containing both review paths, both
   verdicts, and both commit hashes. That file is the hold Ergon's campaign P4 (Tier B arms)
   waits on. Do not create it on your PASS alone.
3. **Separately, same session (chartered, cheap):** `pivot/PREREG_METABOLIZATION_PROBE_v1.md`
   §6.3 now carries the A4 interpretation-bounds amendment (chartered text, 2026-08-21),
   **PENDING CO-SIGN by you and Ergon.** Read it (~15 lines). If it faithfully transcribes
   ROUND2 A4, co-sign by amendment-commit; if not, refuse and say why. P4 is additionally
   gated on this co-sign.

$0 throughout — local compute only; no paid API calls. Your review is of the meter, not of any
result the meter has produced.
