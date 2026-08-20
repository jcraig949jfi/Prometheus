# Two retrodictions — kill-resurrection and the repair ledger

**Author:** Harmonia_M2_C · **Date:** 2026-08-19 · **Station:** M2
**Assigned by:** James. Reassigned from Aporia deliberately: a base-rate question over an
archive is this seat's method, and **Harmonia A is conflicted** — the router thesis is A's
own, so a finding either way from A is worth less than the same finding from here.
**Pre-registration (binding, written before measurement):**
`D:\Prometheus\harmonia\experiments\kill_resurrection_prereg_20260819.md`
**Source of the ask:** `D:\Prometheus\aporia\docs\META_SYNTHESIS_2026-08-12_v1.md` §5,
v4 — re-keyed on **representability** after Harmonia D killed the entails-closure version.
**Thing under test:** `D:\Prometheus\roles\Harmonia\REVIEW_20260812_syntactic_router.md` (A).

**Artifacts shipped:**

| artifact | what it does |
|---|---|
| `D:\Prometheus\harmonia\diagnostics\kill_resurrection_audit.py` | re-evaluates every killed record independently; `_kill_resurrection.json` |
| `D:\Prometheus\harmonia\diagnostics\shadow_catalog_chance_floor.py` | random-pairing null over the survivor population |
| `D:\Prometheus\harmonia\experiments\kill_resurrection_prereg_20260819.md` | the binding pre-commitment |

**Evidence levels:** E1 read source · E3 executed this session.

---

## HEADLINE

> **Retrodiction 1: 0 of 92 historical kills resurrect. 176 of 176 records are
> representable. The router thesis does not explain the program's nulls.**
>
> **And the survivors are worse news than the kills.** 84/84 non-promoted records that
> passed the content check re-evaluate TRUE — but at **45.9% observed against a 46.1%
> random-pairing null.** The survivor population sits exactly on its chance floor. The
> Metabolization Probe is not pricing a mislabeled asset. It is pricing a **correctly
> labeled, chance-level one.**
>
> **Retrodiction 2: capability restored, consumption zero — Hephaestus's inference holds
> as a typed table.** With a mechanism the archaeology did not name: **repairs are
> station-local and do not propagate.** The snappy/z3 repair landed on M1 on 08-13 and
> **M2 is still at 29/222 modules today**, seven days later.

---

## 1. Retrodiction 1 — kill-resurrection, keyed on representability

### 1.1 The reference class, and what is NOT in it

Per my standing rule (`feedback_base_rate_null_for_pattern_claims`): define the reference
class and clean the denominator *before* inferring anything.

**The 92K/394K corpus is ABSENT on this host** — `D:\Prometheus\theseus\corpus\` contains
only `.gitkeep` (E3). Population-level verdict shares survive in
`D:\Prometheus\theseus\corpus_health_report.md` (394,623 unique records, 2026-05-18):
REJECTED 255,375 (64.7%) · SHADOW_CATALOG 125,222 (31.7%) · INCONCLUSIVE 14,026 (3.6%).

The only per-record sample on this station is
`D:\Prometheus\pivot\promoted_triage_sample.jsonl` — **176 records across 4 strata.**

**KILL := verdict == REJECTED (92 records).** SHADOW_CATALOG is *not* a kill: it is a
content-PASS that was never promoted, which is a different failure and is reported
separately in §1.4. Conflating them would have inflated the denominator by 91%.

Only `S3_random` supports unbiased extrapolation, so it is reported separately throughout.

### 1.2 The decisive structural fact (E1)

`D:\Prometheus\theseus\generators\a1_catalog_cross_product.py:183`:

```python
Verdict.SHADOW_CATALOG.value if holds else Verdict.REJECTED.value
```

**The verdict is content-determined at emit time.** REJECTED *means* the relation was
evaluated on the stored operands and violated. **43 of 48 generators** contain the same
verdict-on-predicate construction (E3, grep). A kill in this substrate is not a dispatch
outcome — it is the result of running the predicate.

That is already most of the answer, and I declared it as my prior in the prereg §6 before
measuring, precisely so the confirmation would not look like a discovery.

### 1.3 The measurement (E3)

Every record's assertion was re-derived **independently** — relation semantics written from
the relation NAME, never reading the stored `holds` flag as input.

| | n | CONTENT_FAILURE | ROUTING_ARTIFACT | UNREPRESENTABLE |
|---|---:|---:|---:|---:|
| all kills (pooled) | 92 | **92 (100%)** | **0 (0%)** | 0 |
| S3_random only | 30 | **30 (100%)** | **0 (0%)** | 0 |
| S1_high_freq_template | 7 | 7 | 0 | 0 |
| S2_top_diverse_gens | 30 | 30 | 0 | 0 |
| S5_verifier_weird | 25 | 25 | 0 | 0 |

**Resurrection rate: 0/92 pooled (95% upper bound 3.3% by rule of three), 0/30 on the
unbiased stratum (upper bound 10.0%).** A zero on a finite sample is a ceiling, not a
certainty, and is reported as such.

**Representability: 176/176.** Every claim kind — `invariant_equality`, `mutation`,
`kill_neighborhood`, `symmetry_transform`, `bridge_extension` — is fully expressible from
stored fields. The "blind band" is empty in this corpus. Nothing was scored `novel` for
being undecidable, which is D's standing test on any meter of this shape.

**Fidelity control: 0 disagreements across all 176 records.** My independent re-derivation
reproduces the substrate's own flag exactly, across 5 claim kinds and 5 relation families.
The substrate's content evaluation is correct.

### 1.4 The survivors — and the finding that actually matters

84/84 SHADOW_CATALOG records re-evaluate TRUE. So the non-promoted survivor population
consists of **genuinely true claims that were never promoted**. That is the population the
Metabolization Probe is pricing, so the operative question is whether they are true because
they carry signal, or true by coincidence.

Random-pairing null (permute right operands, preserve both marginals, 2000 permutations,
seed 20260819) — the null `theseus/scoring/content_aware_promote.py` implements:

| relation | n | observed | null mean | null 95% hi | verdict |
|---|---:|---:|---:|---:|---|
| equal_mod_2 | 58 | 53.4% | 53.2% | 63.8% | **AT CHANCE** |
| abs_diff_le_3 | 47 | 29.8% | 35.4% | 44.7% | **AT CHANCE** |
| abs_diff_le_2 | 18 | 33.3% | 48.5% | 61.1% | **AT CHANCE** |
| abs_diff_le_1 | 8 | 87.5% | 56.4% | 75.0% | above null *(n=8; noise)* |
| abs_diff_le_0 | 4 | 100.0% | 37.0% | 100.0% | AT CHANCE |
| **POOLED** | **135** | **45.9%** | **46.1%** | | **AT CHANCE** |

The substrate's own census corroborates from the population side: `equal_mod_2` 67.2%
categorical, `abs_diff_le_*` 67.0%, `divides` 50.7% — and `equal`, **the only relation hard
to satisfy by chance, holds 2.4% of the time.** The yield is concentrated in exactly the
relations a coin could pass.

**Reading: the zero-promotion streak is the gate behaving correctly.** Promoting the
survivors would have been the error.

### 1.5 Verdict against the pre-committed readings

The prereg pre-committed both branches. **"Resurrects nothing" fires:**

> the router thesis is dead for this corpus, the nulls were real, and the program should
> face that rather than repair around it.

I hold to it. Scope, stated precisely: this kills the router explanation **for the Theseus
substrate's 255K REJECTED population**, which is the corpus the retrodiction was aimed at
and the one the Metabolization Probe prices. It does **not** touch A's §2 (`verify()`
`unknown_kind` certifying true claims WRONG) — that is a different instrument, it is E3, and
it stands. A's §6 (the self-inflicted regex import screen) stands. What dies is the
*generalization* from those instances to "the program's 92K nulls are partly
instrument-blindness."

### 1.6 What this costs the Metabolization Probe

The probe is pricing the residue corpus. This audit says the residue is not mislabeled — it
is **correctly labeled and chance-level**. A metabolization lane that mines this corpus for
signal is mining a coin. That does not kill the probe: metabolizing *failure clusters* is
what produced the only capability climb in program history (Hephaestus D2). It means the
probe should price **failure structure**, not survivor claims.

---

## 2. Retrodiction 2 — the repair ledger

Hephaestus answered this by inference from git archaeology (`META_ASSESSMENT_2026-08-12`
D2): repairs restored *capability* but **no repair has ever been followed by a consumer
consuming.** Here it is as a typed table, with the prediction column the ask specified.

| # | repair | date | commit | preregistered prediction of output? | capability restored? | consumer consumed? |
|---|---|---|---|---|---|---|
| 1 | Ergon seam-fidelity fix (handoff inverted the doctrine; stranded 89% of corpus) | 06-15 | `db4b2cac` | partial — adversarial verdict filed 06-17 (`81c72c81`) | claimed | **NO** — 08-19 `6e1b6ff9` found 14 phantom batches, corpus "verifiably empty" |
| 2 | seam allowlist rebuild (leak gate denylist → structural allowlist) | 06-22 | `6439311a` | **none found** | claimed | **NO** evidence found |
| 3 | promotion replay audit (gate is shape-only; count is a formula fossil) | 06-23 | `b092b86a` | **YES** — Charon predicted replay would misread as exoneration; **prediction HELD** | audit produced its finding | **NO** — gate still does not content-gate (E3, §2.1) |
| 4 | `object_zeros` NULL `object_id` repair (98.8% of rows) | 06-23 | `6f06e1b8` | none found | **NOT CHECKABLE on M2** | **NOT CHECKABLE** |
| 5 | `.176` → `.202` DB repoint | 06-24 | `983fd077` | "today's sessions can query" | **NOT CHECKABLE on M2** | **NOT CHECKABLE** |
| 6 | DuckDB retirement + corrupt-table drop | 06-24 | `59d0ac66`, `fa8f625a` | none found | **NOT CHECKABLE on M2** | **NOT CHECKABLE** |
| 7 | `snappy` + `z3` install (my 08-12 finding) | 08-13 | `f405b683` | **YES** — "Spec R5 precondition B discharged" | **YES on M1** (199/200); **NO on M2** (29/222, E3 today) | **NOT YET** — "no arm has executed and none will until the prereg carries three signatures" |
| 8 | `valid=None` abstention patch | 08-16 | `494ee2e2` | **YES** — remove 160/160 `unknown_kind` pollution at R5/R7/R8 | **YES** (E3: `verifier_lens` abstains, with the pollution cited in-source) | **pending** — no re-run artifact found |

**The claim holds.** Of 8 completed repairs: 3 carried an explicit preregistered prediction,
and in all 3 the prediction about *capability* was correct. **Zero have been followed by a
consumer consuming.** Where the ledger says NOT CHECKABLE it says so rather than scoring a
convenient zero — 3 of 8 rows cannot be closed from this station at all.

### 2.1 The correction A's review needs (E3)

A's §1 first row states the Theseus content check "exists and is **not wired into the
gate**." That is *substantially* right and *framed* wrong, and the framing carries the
thesis. `D:\Prometheus\theseus\daemon.py:432` **does call** `maybe_promote_by_f2` — in
**observation mode**, with this comment:

> *"F2 observation-mode tally — counts what content-aware filter would promote, without
> changing actual promotion behavior... every refactor needs measured counterfactual utility
> before being treated as residue. F1 vs F2 promote-count delta IS that measurement."*

That is not a semantic check excluded by a syntactic router. It is a **staged rollout with a
documented graduation criterion**, citing an amendment rule. A read exclusion as
architectural disposition; the source says measurement protocol.

And the two retrodictions meet here: the counterfactual F2 was installed to measure is
exactly what §1.4 computed independently — at a 46.1% chance floor, F2 promotes noise. **The
check never graduated because the measurement it was waiting on came back null.** The gate
was right, and A's strongest single row is the weakest one in the thesis.

### 2.2 The mechanism the archaeology did not name

Row 7 is the sharpest, and it is my own finding from 7 days ago. `pip install snappy` was
approved and landed **on M1**: `prometheus_math` imports 199/200 there. On **M2, measured
today: 29/222, same three doors — `cypari`, `snappy`, `knot_floer_homology`.**

So the ledger's answer is not only "no consumer consumed." It is that **a repair is
station-local and does not propagate**, and the station where the finding was *made* is
still broken. Under ruling R1 (math is the calibration standard), M2 cannot currently run
the calibration standard at all.

**This is the cheapest open item in the program and it is one command:**
`pip install snappy` on M2 (pulls `cypari`, `knot_floer_homology`; verified by dry-run
resolution on py3.14/Windows). I have not run it — installing into the global interpreter is
a host change and James's call, and it was James-approved on M1, not here.

---

## 3. Weaknesses

- **n=176 on a 394,623-record population, and the corpus is absent from this host.** The
  0/92 is a sample result. Its honest ceiling is 3.3% pooled / 10.0% on the unbiased
  stratum — not "zero". Re-running against the full corpus on the station that holds it
  would tighten this by three orders of magnitude and is the obvious follow-up.
- **The sample is Techne's, drawn for a different purpose** (promote-filter triage, 05-30).
  Its strata are purposive and its inclusion probabilities are unknown; I could not verify
  it is representative of the 255K REJECTED population, only that S3_random is internally
  unbiased.
- **My first revision manufactured a phantom finding.** It scored 13 records as substrate
  false-passes; all 13 were my own operand-selection error (I evaluated raw operands for
  `symmetry_transform`, whose assertion is reflection *invariance*, and the kill-pair for
  `kill_neighborhood`, whose assertion is `epsilon <= 2.0`). Corrected, disagreements went
  13 → 0. Had I published the first run, I would have reported a 15.5% false-pass rate that
  does not exist. The audit now documents each kind's assertion in-source.
- **kill_pattern strings could be post-hoc narration** rather than the gate's actual
  decision. My agreement with them proves bookkeeping consistency, not gate correctness.
  The independent re-derivation partly mitigates this — I computed the predicate myself —
  but I cannot prove the stored operands are what the gate saw.
- **Repair-ledger rows 4–6 are unclosable from M2** (no PostgreSQL on this station), and
  rows 2 and 4–6 have no prereg I could find — absence of evidence in a repo this size is
  weak evidence of absence.
- **Declared conflict:** I am the seat that killed A's dispositional claim with a base rate
  in `REVIEW_20260812_harmonia_C.md` §3. That is a standing prior in the anti-router
  direction, and this result confirms it. Weight accordingly — the informative outcome
  would have been a non-zero resurrection rate, and I did not get one.

---

*The retrodiction was aimed at the possibility that a year of nulls was instrument
blindness. It is not: the kills were real, the substrate evaluated its own content
correctly on 176/176 records, and the survivors it declined to promote sit on their chance
floor. The program does not need to repair around its nulls. It needs to face that the
substrate was asking questions a coin could answer.*

— Harmonia C, 2026-08-19
