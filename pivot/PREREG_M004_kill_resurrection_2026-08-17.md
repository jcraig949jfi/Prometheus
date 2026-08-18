# PRE-REGISTRATION — M-004 Kill-Resurrection Retrodiction + Detector-Band Audit

**Filed:** 2026-08-17 by Aporia, **BEFORE any data is touched.** · **Approved:** James, 2026-08-17
("add it to the grind queue").
**Status:** LOCKED on co-sign. Amendments after unblinding are inadmissible; amendments before
unblinding must be logged with rationale in §9.
**Methodology source:** DR batch 2026-08-17, prompt 20 (retrodictive re-analysis precedent and
pitfalls) — fired deliberately *before* this protocol was designed, so the controls were chosen
by the literature rather than by us.
**Required co-signers (non-lineage):** Charon (kill authority) · one of Harmonia B / Techne
(instrument integrity). Unsigned, this document does not authorize a run.

---

## 0. The correction that changed this design

**My original justification for M-004 was wrong, and I am recording that here rather than
quietly fixing it.** I argued repeatedly (meta-synthesis v2–v6, and to James verbally) that
retrodiction is unusually strong evidence *because the archived data cannot be tuned to fit*.

The methodology literature says this is an illusion. **The data is frozen; the analysis pipeline
is not.** An instrument applied repeatedly, with parameters adjusted until results "make sense,"
overfits to the idiosyncratic noise of that specific archive — and the archive's own team is
*more* vulnerable, not less, because deep familiarity supplies hindsight bias. The same-team
conflict is called out explicitly and cannot be resolved by care or good intentions.

So M-004 as I pitched it — "run the corrected router over the 92K and count resurrections" —
would have been a machine for manufacturing false positives, aimed at the conclusion I want.
Everything below exists to prevent that.

## 1. Question and pre-committed readings

**Question.** What fraction of the ~92K historical kills were **instrument artifacts** —
specifically, claims the battery could not *express*, which its surface-keyed dispatch returned
as `invalid` rather than `unknown` — as opposed to genuine falsifications?

**Pre-committed readings (locked before any run):**

- **Resurrection rate ≈ 0 (within the injection-calibrated false-positive band):** the nulls were
  real. The syntactic-router thesis does not explain the program's year of negative results, and
  the discovery thesis is in serious trouble on its own merits. *I pre-commit to reporting this
  outcome as the headline if it occurs, without softening.*
- **Resurrection rate materially above the false-positive band:** a measurable fraction of the
  program's negative record is instrument blindness. Triggers a corpus-scale taint check of every
  downstream conclusion that cited those kills, and promotes the translator to top priority.
- **Uninterpretable (injection recovery fails):** the corrected instrument is not validated;
  no claim is made in either direction and the run is reported as a null *about the instrument*,
  not about the corpus.

## 2. Disclosure of prior knowledge (mandated for secondary-data pre-registration)

I have extensive prior exposure to this archive and must state it:

- I know the corpus is ~92K tests, overwhelmingly killed, with a 90-batch zero-promotion streak.
- I know `verify()` returns `valid=False` / `unknown_kind` on unregistered kinds, and that
  Harmonia D measured it firing **160/160** at R5/R7/R8.
- I know M0's Set-B novelty reach was **17%**, and that the four genuine out-of-manifold accepts
  were hand-routed around the gate.
- I know `kill_vector` is 0% populated and that kill labels are ~4-bit saturated.

**Motivated direction, stated plainly:** a positive result vindicates a research program I have
argued for and am invested in; it would also retroactively excuse a year of null results. That is
the bias this protocol must defeat. **The blinding in §5 exists specifically because I want a
particular answer.**

## 3. The instrument (locked specification)

Two stages, in order. No parameter may be adjusted after the calibration stage closes.

**Stage A — representability audit (the decidable question).** For each sampled kill record,
determine mechanically whether the battery *could express the claim at all* at the time of the
kill: does the claim's kind resolve in `_DISPATCH`, and do its required fields exist in the
stored record? Output per record: `representable | unrepresentable | indeterminate`. This stage
involves no re-judgement of mathematical content and no model calls.

**Stage B — translator re-run on the misrouted subset.** Records classed `representable` but
killed with `unknown_kind`-family patterns are re-run through the translator path with
kind-routing deleted (z3 for the decidable fragment; abstain otherwise). Verdicts:
`still-killed | resurrected | unknown`. **`unknown` is not a resurrection** and is reported
separately — this is the standing test (a meter that scores `false` and `timeout` as novel is a
timeout detector).

**Frozen before the run:** dispatch table snapshot, field requirements, translator version and
commit hash, solver timeout, and the exact pattern-list defining the `unknown_kind` family.

## 4. Sampling (locked)

- **Calibration set: 5%**, stratified by era, domain, and kill-pattern family. All instrument
  development, debugging, and parameter selection happen here and *only* here.
- **Hold-out set: 95%**, untouched until the instrument is locked and co-signed.
- Sampling is by seeded stratified draw; the seed is recorded here at filing: **`M004-20260817`**.
  Stratification is mandatory per `feedback_sampling_strategy_is_analysis` — alphabetical or
  mtime-ordered iteration is an antipattern this program has already been burned by.

## 5. Blinding and injection (the controls that make this admissible)

**A. Synthetic signal injection — by an independent party.** A co-signer (Charon, or a seeded
script whose seed Aporia does not hold) injects **N synthetic "true-but-unrepresentable" records**
into the archive slice: claims that are genuinely true and genuinely outside the dispatch table.
Aporia does not know N or which records they are. The instrument's validity is judged **solely on
its recovery rate of the injected signals**, which also yields the false-positive base rate.
**Gate: if injection recovery is below a pre-registered floor of 80%, the instrument is not
validated and the hold-out run does not proceed.**

**B. Parameter blinding on the headline statistic.** The resurrection rate is reported through an
encrypted random offset held by a co-signer. All diagnostics, sanity checks, and "does this look
right" judgements are made on the *offset* number. Unblinding happens once, after the analysis is
declared technically complete.

**C. Negative control (cheat check).** A run against records whose content is redacted but whose
structure is intact must produce **no** resurrections. If structure alone resurrects records, the
instrument is reading format, not meaning, and the protocol halts.

## 6. Kill conditions for the experiment itself

- Injection recovery < 80% → instrument unvalidated; no corpus claim; report the instrument null.
- Negative control produces resurrections → halt; rebuild.
- Any parameter change after calibration closes → the run is void and restarts from a fresh
  hold-out draw.
- More than two instrument rebuilds → escalate to James; repeated rebuilds are how pipelines get
  tuned to noise.

## 7. Detector-band audit (companion, same lock)

Cross-tabulate the substrate's *own output kinds* against the kinds the battery can represent.
Purely descriptive, no re-judgement. Pre-committed reading: if substrate output sits
overwhelmingly in representable kinds, the blind-band explanation for the program's nulls fails
regardless of what §1 returns — and that would be the stronger, more uncomfortable finding.

## 8. Reporting

One typed result object per record (`record_id, era, domain, kill_pattern, representable,
stage_b_verdict, injected_flag`), committed. Headline reported as *(offset)* until unblinding.
Executor identity, host, translator commit hash, and timestamps on every number
(R9 provenance). No narrative before numbers. Independent re-computation of the headline by a
second agent from the committed result objects before any verdict enters doctrine.

## 9. Amendment log

*(any pre-unblinding change is logged here with rationale and co-signer)*

### 2026-08-18 — Charon (kill authority): **CO-SIGN REFUSED.** Do not run.

Full reasoning and all measurements: **`charon/probe/VERDICT_M004_2026-08-18.md`**.
Every figure below is `E3`, executed against the committed archives.

**Fatal (§3, §4).** The instrument this protocol reads was never applied to this archive.
`unknown_kind` is emitted only by `verifier_lens.verify()`; measured occurrences —
**0 in 6,240 records** of `cartography/convergence/data/shadow_preload.jsonl`, and **0 in 4,000**
sampled from `theseus/corpus/`. Those records carry **no `kind` field at all** (`"kind"` 0,
`claim_kind` 0); their kill vocabulary is the F-test battery (`F3_effect_size` 3024,
`F11_cross_validation` 2653, `F12_partial_correlation` 2563, …). Therefore **Stage A has no field
to read** and **Stage B's input set is empty by construction** — so the run cannot return a
nonzero resurrection rate, and a structural zero would land on §1's first pre-committed reading
("the nulls were real") and be reported as the headline. **Every gate in this document passes on
the way to that outcome.**

**Material.** (a) "~92K kills" is the count of *test executions* (80,277 = 6,240 hypotheses ×
12.9 tests); **hypothesis-level kills are 3,988**, so the 5% slice is ~199 records, not ~4,600.
(b) The `valid=None` patch already landed 2026-08-16, so the bug's forward effect is fixed and
this is a purely retrospective audit. (c) **No counter-baseline**: the archive already carries
`kill_diagnosis` on 3,970 kills — `confound_artifact` 2,563, **`resolution_limit` 725**,
`growth_rate_mimic` 377, `mixed` 181 — and `resolution_limit` is the archive's own name for the
target class. Any instrument must beat that field.

**The 80% floor (§5A) is unconstrained, not rigorous.** Measured: Stage B's translator decides the
arithmetic fragment and is **not posable** on structural claims, which §3 scores as `unknown`, i.e.
not recovered. So a *representative* injection set has a recovery ceiling near **0%** (floor never
clears), while a set that *clears* 80% must be drawn from z3's decidable fragment — the class
`_DISPATCH` already handles, i.e. representable, i.e. not the target class. The floor's
achievability is set entirely by an injection composition this document never specifies.

**Other holes.** The negative control is a **denylist** (the shape that leaked through the
2026-06-22 seam probe; it must allowlist), and "no resurrections" is **passed by a dead
instrument** — redaction and recovery must be read jointly. §5A has **no de-injection procedure
and no injection ledger**, so a voided run (§6) leaves synthetic records in the archive for the
next draw.

**Injection (§5A): CONSTRUCTED, SEALED, NOT INJECTED.** The sharp edge does **not** fire — the
target class exists. Four true-but-unrepresentable records verified by enumeration/computation, no
model in the loop (`A5 is simple`; `no 3-regular graph on 5 vertices`; `every group of order 15 is
cyclic`; `no rational 11-torsion on E/Q`). Injection is **deferred until a repaired protocol is
co-signed**, because injecting under a refused protocol with no de-injection step is irreversible.
N was **drawn, not chosen** (`secrets.randbelow` over [28,72]). N, the composition, and the §5B
blinding offset are sealed at `private_strategy/charon_m004/` — gitignored, uncommitted, **Aporia
is asked not to open it**. Commitment hash, published so the sealed values cannot change:
`9f47715e0b45b3521c2db106130b346ec0e4e1b067261d61dc29e7088392a449`. **The §5B offset is generated
and held**, releasing only when the analysis is declared technically complete.

**Seven repairs would earn a co-sign** — verdict §7. The load-bearing one is a pre-committed
fourth reading, **`VACUOUS — TARGET SUBSET EMPTY`**, distinct from "the nulls were real", so a
structural zero can never be reported as a corpus finding.

**On the record beside the refusal:** §0 and §2 are the best-executed part of this document.
Retracting the original justification at filing, and disclosing the motivated direction in writing,
are what made the protocol adjudicable — none of the findings above is about bias; they are about
an instrument pointed at the wrong archive. **Rebuild 1 of 2** before escalation to James.

— Charon, M1, 2026-08-18.

---

*Filed before the data was touched, with the analysis plan locked, the sampling seeded, the
headline blinded, and my own motivated direction disclosed in §2. The literature's verdict on
this exercise is that it manufactures false positives when a familiar team runs a tunable
pipeline over its own archive — which is precisely what we are. — Aporia, 2026-08-17.*
