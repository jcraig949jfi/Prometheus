# Diomedes cycle 003 — PRE-REGISTRATION: was cycle 002's KILL about coordinates, or about transfer?

**Filed:** 2026-08-24, **before any outcome measurement.** **Charter:** `LOOP_CHARTER.md`.
**Predecessor:** cycle 002 (`2780e5b5`), disposition KILL.
**Scope:** no new features, no new corpus, no learned representation beyond the same logistic
scorer. Only the **split** changes. Uses the identity-proved harvest cache (digest `1b4abb1a…`).

---

## 1. The question

Cycle 002 killed *"a global relational model over `Z(x,a)` transfers across held-out invariant
pairs"* (PHI_REL 0.5444 vs ceiling 0.6254). But its pre-registered per-feature table showed the
**single most informative feature in the experiment was relational** — `parity_match_0`,
|AUC − 0.5| = 0.0655, pointing the direction the mechanism predicts — and the model scored *below
its own best input*.

Two explanations remain, and they imply opposite next moves:

- **E1 — TRANSFER FAILURE (H4).** Relational coordinates do carry state-conditional information, but
  the companion↔tested relationship differs per invariant pair, so a global coefficient learned on
  some pairs is wrong on others. Cycle 002 measured a transfer limit and mislabelled it a coordinate
  limit.
- **E2 — GENUINE COORDINATE INADEQUACY (H3).** Relational coordinates do not carry the conditional
  signal even locally; the per-feature |d| is a marginal artifact. Learned transition representations
  become defensible.

> **Cycle 003 asks only: does the same frozen feature family recover materially more signal when
> trained and evaluated within the same invariant pair?**

## 2. Arms

Identical feature family, identical scorer, identical seeds. Only the split differs.

- **T3_ACROSS** — train on 60% of invariant pairs, evaluate on held-out pairs. *Replicates cycle 002;
  must reproduce 0.5444 ± its SE or the harness has drifted.*
- **T2_WITHIN** — for each invariant pair, train on 60% of that pair's **states**, evaluate on the
  remaining 40% of that pair's states. The discriminating arm.
- **T0_INSAMPLE** — train and evaluate on the same states. Upper bound on what the family can express
  at all; not evidence of anything except expressivity.
- **B1_T2 (mandatory control)** — the candidate break-rate alone under the T2_WITHIN split.
  **Rationale:** the same objects recur across states within a pair, so a T2 gain could be *object
  memorization* rather than relational transfer. If B1 rises by a comparable margin, the T2 gain is
  object-level and E1 is **not** supported.
- **ORACLE / SHUFFLE / RANDOM** — the standing controls, required as before.

## 3. Direct mechanism test (the smoking gun, cheaper than the AUC comparison)

For each invariant pair with ≥ 200 states, fit the relational model and record its coefficient
vector. Then report **mean pairwise cosine similarity** between per-pair coefficient vectors.

- cosine ≈ +1 → the relationship is the same everywhere; E1 is false and the T3 failure needs
  another explanation.
- cosine ≈ 0 or < 0 → the learned relationship genuinely differs, or inverts, per invariant pair.
  That is E1's mechanism observed directly rather than inferred from a score gap.

Also report, per feature, the fraction of pairs in which its coefficient sign agrees with the modal
sign.

## 4. Pre-registered decision bands

Let Δ = mean(T2_WITHIN) − mean(T3_ACROSS), with 3·SE intervals.

- **TRANSFER-FAILURE-CONFIRMED** — Δ > 0.03, T2 lower bound above T3 upper bound, **and** the
  B1_T2 control rises by < half of Δ. ⇒ cycle 002's KILL was about transfer (H4), not coordinates
  (H3). Disposition **REDESIGN** — the instrument (a global model) was inadequate to the question.
- **COORDINATES-INADEQUATE-CONFIRMED** — the T2 and T3 intervals overlap, or Δ ≤ 0.01.
  ⇒ relational coordinates do not carry it even locally. Cycle 002's KILL stands at full breadth and
  learned transition representations become defensible **for the first time**. Disposition **ADVANCE**
  (of the claim that something richer is required — the next hypothesis earns testing).
- **OBJECT-MEMORIZATION** — Δ > 0.03 but B1_T2 rises by ≥ half of Δ. ⇒ the within-pair gain is
  object-level recurrence, not relational structure. Disposition **KILL** of E1.
- **AMBIGUOUS-NEEDS-POWER** — 0.01 < Δ ≤ 0.03 with overlapping intervals. Report the n required;
  force no branch.

## 5. Known confounds, declared before measuring

1. **Object recurrence within a pair** — addressed by the B1_T2 control (§2).
2. **T2 has fewer training states per model** than T3 has training rows, so T2 could underperform for
   sample-size reasons alone. This biases *against* E1, making a positive result conservative. Report
   per-pair training n.
3. **Pairs with few states** are excluded at ≥ 200 to keep per-pair fits meaningful; that exclusion is
   frozen here, not tuned.
4. **T0_INSAMPLE is not evidence.** It is reported to bound expressivity and must not be cited as a
   result.

## 6. Prediction (recorded so it can be wrong)

I expect **TRANSFER-FAILURE-CONFIRMED**: T2_WITHIN in **0.58–0.65**, Δ ≈ 0.04–0.10, mean pairwise
coefficient cosine **near zero or negative**, and B1_T2 rising only slightly. My cycle-002 prediction
was wrong on three of four clauses, so this one deserves discounting — and the B1_T2 control exists
precisely because the result I expect is also the result my charter-aligned bias would most like.

## 7. Deliverables

`CYCLE_003_RESULT_*.md`, CAR-003, `cycle003_run.py` + `cycle003_result.json`, in one commit.

*— Diomedes, cycle 003 pre-registration, 2026-08-24. Frozen before measurement.*
