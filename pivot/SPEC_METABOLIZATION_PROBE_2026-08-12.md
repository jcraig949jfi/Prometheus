# Metabolization Probe — Requirements & Design

**Doc type:** Requirements + design spec (executable — build against this, don't re-derive).
**Version:** v2.0 (2026-08-13) — incorporates James's full peer review verbatim-in-substance:
four mandatory changes (causal cutoff R14; F-answer/F-oracle split; transfer-distance
stratification; bounded-null verdict language) plus the recommended additions (F-generic
control replacing F-format; whole-vs-retrieved as first-class arms with the four-quantity
decomposition; Tier A demoted to harness qualification only; R7 marginal-balance upgrade;
negative-transfer and behavioral metrics; single-primary-endpoint statistics; the diagnostic
matrix replacing the three-path table; narrowed purpose claim). v1.x audit history preserved
in git (v1.0 → Aporia audit → v1.1 → v1.2 → freeze → James review → v2.0).
**Status:** v2.0-FINAL, RE-FROZEN. Further changes belong in the preregistration, which is
the binding instrument. Sign-offs per §4.1.
**Authority:** James, 2026-08-12/13 — "Priority #1." Constitutional context: the heredity rule
(*no new architecture until one failure produces one verified improvement*) and the
two-control rule (*every meter ships a positive control and a cheat control or its output is
inadmissible*).

---

## 1. Purpose (narrowed per review §15)

> **Does Prometheus's actual accumulated failure residue improve the next attempt, compared
> with equally plausible but irrelevant residue — and over what transfer distance?**

This tests a **necessary subclaim** of the founding thesis: *prior falsification residue
contains information capable of improving subsequent problem solving.* It does NOT test that a
geometrically meaningful kill field exists, that any gradient is navigable at scale, or that
learning from it compounds. Those are the successor experiments:

- **M1 (this probe):** does residue carry transferable information, and over what radius?
- **M2:** can the system retrieve the right residue? (partially internal to this probe via the
  whole-vs-retrieved decomposition)
- **M3:** does residue redirect search toward productive regions? (behavioral metrics here are
  the pilot)
- **M4:** does repeated consumption compound? Only after M4 does the word "metabolism" get
  used literally.

The center of gravity is **F-prom versus F-null** — not F-prom versus F0.

## 2. Canonical nomenclature (binding — supersedes v1.x and all prior labels)

**Arms** (all token-budget-matched):

| Arm | Contents given to the solver alongside the problem | Role |
|---|---|---|
| **F0** | Nothing — problem only | Baseline |
| **F-null** | Adversarially matched but *mismatched* residue — wrong problems, same surface statistics | Identity control: does correct residue identity matter? |
| **F-generic** | High-quality generic failure-reasoning advice (verify assumptions; test boundary cases; isolate first failing transformation; distinguish representational from solver failure; search counterexamples; inspect invariants; …) — authored without access to target, residue, or answer; token-matched | Specificity control: is Prometheus better than a sophisticated "think harder" prompt? **Replaces v1.x F-format**, which was too weak |
| **F-prom-retrieved** | Prometheus's actual residue for the task, per-problem retrieved packets (§4.4) | The deployable condition |
| **F-prom-whole** | Maximum available Prometheus residue — the full 3,311-class signature_index in context plus task extracts | The existence condition (does useful information exist at all, retrieval aside?) |
| **F-oracle** | Ground-truth **failure diagnosis** — what went wrong and why — WITHOUT solution information | Ceiling: value of perfect failure knowledge |
| **F-answer** | Packet literally containing sufficient solution information | **Instrumentation positive control ONLY.** Tests that the solver reads and uses packet payload. Never participates in substantive comparisons |
| **F-shuffle** *(optional; preregistration decides feasibility)* | Correct task's residue with within-record correspondence scrambled (diagnosis ↔ approach ↔ falsifier ↔ margin ↔ break location) | Structure control: F-prom > F-shuffle ⇒ relational structure carries signal; F-shuffle ≈ F-prom > F-null ⇒ the signal is bag-of-clues/topic conditioning |

**The reading ladder** (each rung a different engineering question):
F-answer (can it consume explicit info?) → F-oracle (value of perfect failure knowledge) →
F-prom-whole (does Prometheus possess useful information?) → F-prom-retrieved (can Prometheus
navigate to it?) → F-generic (is it better than generic advice?) → F-null (does identity
matter?) → F0.

**Primary quantities:**
- `Δ_carry = F-prom-retrieved − F-null` *(primary endpoint, §4.6)*
- **Decomposition (per review §7):** residue existence `= F-prom-whole − F-null`; retrieval
  efficiency `= F-prom-retrieved − F-null`; retrieval loss `= F-prom-whole −
  F-prom-retrieved`; oracle gap `= F-oracle − F-prom-whole`; specificity margin
  `= F-prom-retrieved − F-generic`.
- `Q_residue = (F-prom-retrieved − F-null) / (F-oracle − F-null)` — **reported only when the
  preregistered lower confidence bound of (F-oracle − F-null) exceeds the minimum
  meaningful-effect threshold; otherwise reported as `Q_residue = UNIDENTIFIABLE`** (review
  §5: never force a ratio out of noise).

**Transfer-distance ladder (mandatory stratification, per review §1).** Every task is tagged
with its distance from the residue's originating failures:

| D | Test | A win means |
|---|---|---|
| **D0** | Same problem, retry | Residue supports correction |
| **D1** | Same family, changed parameters | Residue generalizes locally |
| **D2** | Different instance, same failure mechanism | Failure abstraction transfers |
| **D3** | Different surface form, same latent obstruction | Genuine reusable failure knowledge |

D4 (cross-domain) is explicitly out of scope for this probe. **All headline quantities are
reported per-distance (D0–D3), not only pooled.** A profile like "D0 strong → D3 zero" is a
first-class result — the first empirical measurement of the residue's transfer radius — not a
partial failure.

## 3. Requirements

**R1 — Non-model ground truth.** Every task's gold label is computed, enumerated, or
kernel-checked. No LLM-judged labels anywhere.

**R2 — Preregistration before first arm.** `pivot/PREREG_METABOLIZATION_PROBE_v1.md` commits
BEFORE any arm executes: final task-set manifest (hashes) plus the R13 replenishment procedure
and hashed source pool (replenishment is a preregistered branch, never an amendment); solver
identities (model_id + version + date, pinned); arm-packet construction procedures; the
transfer-distance tagging procedure; metrics; the full statistical plan (R15); decision
thresholds; kill conditions; named executor per component. Signatories: Ergon (driver), Charon
(kill authority), Harmonia B (meter integrity).

**R3 — Two instrumentation controls, demonstrated before arms run** *(amended: F-answer split
from F-oracle per review §4)*:
- *Payload-consumption control:* **F-answer** must yield F-answer ≫ F0. If the solver cannot
  exploit a packet that literally contains the solution, the packet pipeline or solver is
  broken; running arms is inadmissible. F-answer appears in no substantive comparison.
- *Cheat control (payload-reading null):* packets with content REDACTED but format/structure
  intact must NOT beat F0. If they do, the packet format leaks; rebuild the spec.

**R4 — Grader headroom.** ≥25pp demonstrated between the strongest solver's F0 baseline and
the instrument ceiling on the chosen task set, else add harder probes before reading anything.

**R5 — Instrument fixes land first.** `valid=None` patch merged; z3 present on executing
hosts; `prometheus_math` importable where its primitives are used.

**R6 — F-prom packets honestly assembled.** Packets contain what the substrate ACTUALLY
recorded — incomplete, correlated, verbose, null-heavy, partially wrong, often missing break
location — with no hand-enrichment. Where the substrate recorded nothing useful, the packet
says so; that sparsity is the measurement. Assembly code committed and deterministic.

**R7 — F-null adversarially constructed, with two-layer verification** *(amended per review
§9)*: (a) **predefined marginal-balance tests** on: token count, records per packet,
field-null rates, signature count, kill-label distribution, numerical-token density,
object-family frequency, timestamp distribution, payload length, vocabulary diversity,
source-type distribution — each within preregistered tolerance; AND (b) the **blinded
classifier test** (≤55% on surface features) as catch-all. Charon owns both.

**R8 — Raw-model solvers.** Raw API or local models only — never tool-enabled harness
sessions. Temperature, system prompt, token budgets pinned; fixed seeds where the API permits.

**R9 — Executor-tagged results.** Every number carries executor, time, host, model version.
Typed JSONL result objects (one row per task × arm × attempt × distance-tag), committed.

**R10 — Independent re-computation.** A second, different agent re-executes the headline
computation from committed result objects before any verdict enters doctrine.

**R11 — Budget accounting.** Tier A zero API spend. Tier B logged per arm; halt (not degrade)
on exhaustion; half-run arms discarded, never averaged.

**R12 — Single owner.** Ergon. Supporting contracts are bounded deliverables. Succession is
explicit, never ambient.

**R13 — Per-item contamination probe with power floor.** Each task posed cold to each solver
(no residue, minimal budget); items answered reliably are stratified out of primary analysis
and reported separately (contamination lifts F0, compresses arms, fakes a null). Minimum
post-stratification N tied to the preregistered power calculation; below it, replenish from
the preregistered pool BEFORE arms run. An underpowered Δ_carry ≈ 0 must be impossible to
mistake for a no-carry verdict.

**R14 — Causal/provenance cutoff (NEW — mandatory, per review §2; the firewall).** For every
evaluated task T, define provenance cutoff τ(T). **F-prom packets may contain only residue
generated strictly before T's held-out attempt and before any record derived from T's gold
outcome.** Enforcement is mechanical, from provenance IDs and ledger append-order — NOT from
wall-clock timestamps alone (M3's CMOS reset makes clock-derived times unreliable for
affected windows; ledger ordering and record IDs are the honest clock). The assembler carries
the executable assertion `packet_max_provenance < target_attempt_provenance` and fails loud on
violation. Without this, "residue for that problem" can smuggle later knowledge about the
problem into the packet, and the entire experiment measures leakage.

**R15 — Statistical plan (NEW — mandatory, per review §13).** ONE primary endpoint: **paired
task-level F-prom-retrieved vs F-null success on the pooled preregistered Tier-B manifest.**
Everything else — per-distance strata, decomposition quantities, per-class breakdowns,
behavioral metrics, model-specific results — is secondary/exploratory and labeled so. The
preregistration fixes: exact test; treatment of multiple attempts; model pooling policy;
confidence intervals; multiple-comparison handling; missing-API-response handling; ties; task
exclusions; and a **minimum practical effect size** — statistical significance alone does not
define usefulness (a +0.7pp lift over 494 tasks may be significant and strategically
meaningless).

## 4. Design

### 4.1 Roles & contracts *(unchanged from v1.2 except as noted)*

| Seat | Contract |
|---|---|
| **Ergon** (DRIVER) | Experiment end-to-end: preregistration, harness (extending `routing_eval.py`), transfer-distance tagging, solver runs, result objects, verdict draft |
| **Techne** | F-prom packet assembly (retrieved + whole variants) with the R14 firewall built into the assembler; honesty note per R6 |
| **Harmonia B** | Meter integrity: R3 both controls, R4 headroom, preregistration co-sign |
| **Harmonia A** | Grading-oracle wiring; `valid=None` patch |
| **Charon** | F-null construction + R7 both layers; F-generic authoring (it is failure-advice authorship — the falsifier's craft — with no target access); kill authority: adjudicates verdict against preregistration; runs nothing else |
| **Apollo** | Tier A wall corpus + per-wall F-oracle diagnoses; behavioral-metric schema (its dispatch_audit is the in-loop precedent) |
| **Hephaestus** | SUPPLIER ONLY (conflict on record): forge-ledger residue extracts; this spec. No grading, no verdict |
| **James** | Tier B procurement; reads the adjudicated verdict |

### 4.2 Tier A — HARNESS QUALIFICATION ONLY *(demoted per review §8; supersedes v1.1's
"directional Δ_carry" rationale)*

Substrate: Apollo's ablation-induced walls (≥20, ≥4 failure classes) — chosen because
F-oracle is exact by construction. **But constructed failures are idealized** ("no operator
writes slot `counts`" is cleaner diagnostic information than real residue ever is), so:

> **Tier A's only permitted verdict is `HARNESS_ADMISSIBLE` / `HARNESS_NOT_ADMISSIBLE`.**
> Tier A's Δ_carry and Q_residue MUST NOT be interpreted or quoted as evidence for or against
> the Prometheus thesis. Synthetic success is not a victory lap.

Tier A runs all arms mechanically (pipeline exercise), on local Qwen2.5-Math-1.5B (M1, raw)
and/or `gemini-3.6-flash` (free tier). **Exit criteria:** R3 both controls pass; R7 both
layers pass; R13 stratification executed; R14 assertion demonstrably fails-loud on a planted
violation; typed results flow end-to-end; F-answer ≫ F0 and F-oracle > F0 at preregistered
significance on the wall corpus. Then Tier B is a solver-swap plus task-set swap.

### 4.3 Tier B — the decisive run (gated on API procurement)

Task sets (final manifest in preregistration): the 494-item computed-gold OOD set;
`prometheus_math` op instances (post-unbrick); optional Lean-checkable claims. Every task
transfer-distance-tagged D0–D3 against its residue provenance. **F-prom-whole and
F-prom-retrieved are both first-class arms** (no longer "variants"): the decomposition
quantities in §2 are computed and reported as the experiment's structural output. Solvers:
≥2 frontier models from different families, raw API, pinned. Charon's navigability pre-test
(kill_vector slice + right-axis null on the 0.725-bit MI) runs alongside as the geometry-side
companion, same preregistration.

### 4.4 Residue packet spec *(v1.2 content + R14 firewall)*

Per task, deterministically assembled, provenance-stamped, R14-filtered: nearest kill
signatures; prior failed approaches for adjacent problems **whose provenance precedes τ(T)**;
void structure around the task; stored margins/falsifier IDs/kill_pattern strings as-is
(33.6%-null warts included, per R6); packet header with assembly version, source record IDs,
provenance bounds, token count. EXCLUDED: hand-written content, out-of-substrate content,
answer-naming text, any record at-or-after τ(T).

### 4.5 Verdict: the diagnostic matrix *(replaces the three-path table per review §14; the
dossier's three futures map onto rows as noted)*

*Authorship note: this spec's author is the declared-conflicted supplier. The v2.0 verdict
structure and thresholds originate from James's review; co-signers still independently
confirm thresholds in the preregistration.*

| F-oracle | F-prom-whole | F-prom-retrieved | Diagnosis | Next move |
|---|---|---|---|---|
| ✗ (≈F0) | — | — | Solver/task/headroom failure (or contamination — check R13 strata) | Re-level tasks or swap solver; NOT a residue verdict |
| ✓ | ✗ | ✗ | **Recorded residue lacks usable information** — bounded: *no detectable carry under tested models, tasks, packetization, context budgets* — never "exhaust at any capacity" | Provenance engineering (margin-space vectors, break-step records, verified-trace factory); re-probe (dossier Path β/γ boundary) |
| ✓ | ✓ | ✗ | **Retrieval/navigation failure** — information exists, Prometheus can't find it | Build the retriever/index (M2); the residue is vindicated (Path β, retrieval flavor) |
| ✓ | ✓ | ✓ weak | Residue useful, low quality; report per-distance radius | Enrich records; distill what carries (Path β) |
| ✓ | ✓ | ✓ strong | **Carry demonstrated** — with transfer radius D0–D3 profile as the headline | Path α: distillation, process-reward training, forge pointed at failure clusters |
| ✓ | harmful | harmful | **Negative transfer** — residue misleads | Audit misleading-record classes; this is a first-class finding, not noise |

Additional bounded-null sublabels where applicable (review §6): *representation null* (oracle
works, Prometheus's encoding doesn't), *consumption null* (tested models can't exploit what's
there), *retrieval null*, *residue null* — only the last approaches "functionally exhausted
**under the tested regime**."

### 4.6 Metrics *(amended)*

**Primary (R15):** paired task-level F-prom-retrieved vs F-null, pooled Tier-B manifest.
**Secondary, mandatory:** per-distance (D0–D3) profiles of all ladder quantities; the §2
decomposition; per-failure-class breakdowns; **negative transfer** (review §11): per arm,
solved→unsolved vs baseline, unsolved→solved, answer-changed, failure-class-changed,
attempts±; `harm_rate = P(arm breaks an F0 success)` — a substrate that fixes 8 and breaks 7
is not navigation. **Behavioral (review §12, where machine-checkable):** chosen operator;
first invalid transformation; falsifier invoked; attempts count; **repeated-dead-approach
rate** (did the solver retry an approach its packet said was killed?); tokens-to-valid.
"Accuracy +3pp with repeated-dead-approaches −31%" is a more Prometheus-native result than
the accuracy number alone — this is the KillVector ambition at experiment scale, no grand
architecture required.

### 4.7 Reporting

One typed result file per tier; one verdict doc co-signed per §4.1 leading with: the primary
endpoint, the D0–D3 profile, the decomposition ladder, harm rate, and the diagnostic-matrix
row — numbers before narrative. Example of the report shape the program wants (review): "D0
+18 / D1 +11 / D2 +5 / D3 +0; oracle ceiling +23; whole +10; retrieved +6; generic +2; null
+0.4; harm 1.8%; repeated-dead −31%." A result of that shape names what Prometheus IS — e.g.
*a failure-memory system with a measurable transfer radius* — which is worth more than any
single Δ.

## 5. Preconditions gate *(unchanged from v1.2)* — A. `valid=None` + z3; B. snappy/cypari
unbrick; C. kill_vector slice OR whole-index primary, resolved in preregistration; D. headroom
demonstrated; E. API procurement (Tier B) with the 7-day escalation mechanic after Tier A
exit; F. backups of fire+sci and the F: corpus before Tier B prices data that has no second
copy.

## 6. Schedule *(owner-sessions)* — 1. Preregistration (Ergon) + co-signs; 2. Pit-stop items
+ packet assembler (with R14) + F-null/F-generic construction + controls, parallel; 3. Tier A
+ HARNESS_ADMISSIBLE check; 4. Procurement (anytime; escalates per 5E); 5. Tier B +
navigability companion + R10 re-computation + adjudication.

## 7. Kill conditions for the probe itself *(v1.2 +1)* — Tier A fails R3 after one
re-leveling → STOP, redesign. Cheat control fails twice after rebuild → escalate with failure
analysis. R7 classifier beats 55% after two F-null rebuilds → experiment as designed not
runnable; say so. **NEW:** R14 assertion cannot be enforced mechanically for a task class
(provenance too coarse) → that class is EXCLUDED, listed, and its exclusion reported — never
waved through.

## 8. Out of scope

No training runs. No new architecture (heredity rule). No LLM-judged gold. No semantic-router
gates in grading. No hand-enriched packets. No headroom failure read as residue verdict. No
Tier A number quoted as thesis evidence. No "at any capacity" claims — all nulls are bounded
to the tested regime. No verdicts without executor identity and independent re-computation.
D4 cross-domain transfer excluded from this probe.

## 9. Open items for the preregistration to fix

Task-set sizes and per-distance quotas; solver list (procurement-dependent); F-shuffle
feasibility; M0 unrepresentables in Tier A; packet token ceiling; exact test + minimum
practical effect size (R15); whole-vs-retrieved reporting order; F-generic text finalization
(Charon) and its token-matching tolerance.

## 10. How this spec is falsified

If Tier A passes, Tier B runs, and the fleet cannot agree which diagnostic-matrix row the
result lands in against the preregistered thresholds, this spec failed at its one job —
making the outcome unarguable in advance. The failure analysis goes in the postmortem, not a
v3 of the experiment.

---
*v2.0: the review's core gift is the transfer-distance ladder — it converts a pass/fail bet
into a measurement of the residue's radius, which is a property Prometheus can own regardless
of verdict. Spec re-frozen; the preregistration is the binding instrument. — Hephaestus
(drafting), James (review of record), 2026-08-13.*
