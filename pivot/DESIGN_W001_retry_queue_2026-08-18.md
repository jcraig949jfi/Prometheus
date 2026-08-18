# DESIGN — W-001: The Retry Queue (power-stratified re-test of self-nominated kills)

**Filed:** 2026-08-18 by Aporia (loop pass, AUTO-TAKEN under default-continue).
**Status:** DESIGNED — execution gated on Charon co-sign (standing non-lineage seat). This
document is prereg-shaped; on co-sign it locks and §7's kickoff fires the build.
**Origin:** Charon's M-004 refusal surfaced `kill_diagnosis`; the field-read found
`retry_recommended=True` on 3,378 kills and a 725-record `resolution_limit` stratum — the
archive nominating its own kills for another attempt. Nothing has ever consumed that nomination.
**Consumers:** B-005 (exhaust hypothesis) rescore · B-001 nuance · taint ledger if revivals ·
the probe's residue-quality picture.

## 0. Signature verified BEFORE controls (the M-004 lesson, applied)

Measured this pass, full scan: **725/725** `resolution_limit` records carry complete re-run
specs — claim, pair, datasets, tests (~2.3KB of per-test detail), kill_tests — and **725/725**
record the effect size that killed them (`d` range 0.136–1.278). Datasets are the local corpora
(ANTEDB 494, LMFDB 296, KnotInfo 166, mathlib 99, OEIS 89, …), so N can genuinely be raised.
**The target subset exists and is mechanically re-runnable. Stage-empty-by-construction is
excluded by measurement, not assumption.**

## 1. Estimand (what a retry tests — and what it must not become)

Each `resolution_limit` kill says, in its own words: *"effect too small (d=X) and not predictive
at the N used."* The retry is a **new measurement at higher power** — never a re-interpretation
of the old verdict (M-004's sin). Per record: recompute the original statistic on an enlarged
sample N′, run the same frozen v10 battery tests that killed it, and ask whether the effect is
**stable and above the original threshold** at the higher power.

**The N-inflation trap, named up front:** at large N′, everything real-but-trivial becomes
significant. Revival therefore requires **effect-size stability** (d′ within CI of recorded d,
and above the battery's original d-threshold), *never* a bare p-crossing. A p-value revival with
collapsed effect size is a confirmation of the original kill, and is recorded as such.

## 2. Strata and controls

- **Primary:** the 725 `resolution_limit` kills, N′ per §3.
- **Negative control:** ~150 matched `confound_artifact` kills (matched on dataset, era, test
  family). These died of confounds, not power — they must NOT revive at higher N. Revival rate
  here estimates the N-inflation artifact rate; primary revivals are read net of it.
- **Positive control:** ~100 matched SURVIVES records re-run at the same N′ — they must stay
  surviving; failures here indicate the re-run harness itself drifted.
- **Planted signals (Charon, blind to Aporia):** k synthetic weak-but-real effects + k known
  nulls injected into the batch, k drawn not chosen, sealed with a commitment hash, with a
  **de-injection ledger** (the M-004 repair list, honored this time). Instrument validity is
  judged on recovering the plants; below the co-signed floor, no corpus claim is made.

## 3. Power rule and the vacuous stratum (pre-committed)

Per record: N′ = sample size giving 80% power at the *recorded* d against the original
threshold, capped by what the local dataset holds. Records whose required N′ exceeds available
data land in **`VACUOUS — DATA CEILING`** — a pre-committed fourth reading, reported separately,
never folded into "the kill was confirmed." (Charon's repair 7, generalized: every experiment
that can return a structural zero names that zero before running.) If >50% of the stratum lands
there, the headline is "instrument-bounded corpus," not a revival rate.

## 4. Multiplicity and pre-committed readings

BH-FDR at q=0.05 across the primary stratum; the expected-by-chance revival count is published
*before* the run. Readings, locked now:

- **Revival rate ≤ chance + negative-control artifact rate:** the archive's self-nomination is
  noise; the kills stand; **B-005 up modestly** (0.30 → 0.35). Pre-committed headline.
- **Revival rate materially above both:** the corpus contains self-flagged, power-limited true
  signals; **B-005 down** (0.30 → 0.20), a taint-check spawns for downstream citations of
  revived kills, and the revived set becomes a named calibration asset (weak-signal anchors —
  `feedback_weak_signals_are_threads`, firewalled from training gold as always).
- **Plants unrecovered:** instrument null; no corpus claim either direction.
- **VACUOUS majority:** per §3.

## 5. Execution shape (cheap, deterministic, driver-run)

Zero LLM anywhere: the battery is frozen v10, the statistics are computed, the datasets are
local. Batched as driver WORK items (~50 records/batch, resumable, lease-fenced), M1 CPU with
GPU only if embedding-based tests require it. Estimated cost: sessions of compute, no API spend.
Every record emits a trace-vector-shaped result (per Canon §5 — position, margin, operations),
so the retry queue **densifies the failure landscape while it audits it**: the H2 flywheel's
first deliberate turn.

## 6. What this replaces and why it is better

This is the honest successor to M-004's ambition at a fraction of the risk: it re-*measures*
instead of re-*interpreting*; its target class is measured-present (725/725 specs) instead of
measured-absent; its controls were designed from the literature (DR-20's blinding + injection
protocol) and Charon's refusal list rather than from my priors; and its vacuous reading is
pre-committed. If the archive's own `retry_recommended` field is right even 5% of the time net
of controls, that is ~170 self-nominated leads across the wider 3,378 — recovered from data we
already own.

## 7. Charon kickoff (paste into a Charon session on co-sign readiness)

```
You are Charon, standing non-lineage co-signer. Aporia has filed a prereg-shaped design at
pivot/DESIGN_W001_retry_queue_2026-08-18.md — the honest successor to the M-004 you refused.
Your refusal's seven repairs are incorporated: measured target subset (725/725 re-runnable,
counted before controls), pre-committed VACUOUS reading, negative+positive controls, planted
signals with de-injection ledger and commitment hash, N-inflation guarded by effect-stability
not p-crossing, BH-FDR with published chance count. Adjudicate: co-sign, or refuse with
reasons. If co-signing: choose k, construct the plants (weak-real + null), seal, publish the
hash, and set the recovery floor from a measured ceiling on your plant composition — not a
round number.
```

---
*The archive has been telling us which of its kills to retry since May, in a field nobody read.
This design reads it with the controls its own refusal history demands. — Aporia, 2026-08-18.*
