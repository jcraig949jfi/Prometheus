# PROPOSAL T2 (control)

**Designer:** Prometheus research design seat · **Date:** 2026-09-02 · **Status:** SPECIFICATION (not executed)
**Instrument:** the Ergon probe band — `ergon/probe/` task families scored by exact-match extracted
integer vs computed gold (`task_gen_v3.py`, `extract.py`, `task_controls.py`).

This is the **control leg** of the T-series: it measures the FREE-vs-PAID host gap that any
cross-host capability claim silently assumes is zero (or silently assumes is large — the +14pp
version of this claim reached a binding prereg before being withdrawn). Its expected outcome,
from prior reads, is a small-or-null delta; the point of running it is to convert that
expectation into a bounded, preregistered number with a decidable verdict.

## Hypothesis

**H1 (directional, what the experiment tests):** paid-tier serving of the same model family
(`deepseek:deepseek-v4-flash`, DeepSeek direct, funded) yields exact-match accuracy on the
probe band higher than free-tier serving (`nvidia:deepseek-v4-flash`, free NVIDIA lane) by at
least the smallest gap that could matter on this instrument: **Δ = acc(paid) − acc(free) ≥
+4.0pp** at the primary rung. 4.0pp is not arbitrary: it is the sized magnitude of the probe's
own method-priming confound (`ergon/probe/FINDING_heuristic_floor_2026-08-24.md`, §2) — a tier
gap smaller than an already-documented within-family confound cannot bear interpretive weight.

**H0 (practical equivalence):** |Δ| < 4.0pp — the tiers are interchangeable at the resolution
the probe operates at, and the no-pooling rule (R9) stands on version-pinning principle rather
than on a measured capability gap.

**Scope discipline (declared up front):** "FREE tier vs PAID tier" here means *the same model
family served on a free host vs a paid host*. This isolates the serving-tier variable
(quantization, served checkpoint, sampling defaults, truncation behavior) while holding the
weights family fixed. It is explicitly NOT a claim about "free models vs paid models" as
populations — that comparison confounds tier with model identity and is out of scope.

**Framing falsifier on the word "reasoning":** the family's attainable-without-reasoning floor
is 0.5225 (coprime-to-30 heuristic, fresh-seed, `FINDING_heuristic_floor_2026-08-24.md`), and
both hosts' prior M30 reads sit at or below it (paid 0.500, free 0.510). If both hosts again
read ≤ 0.5225 at the primary rung, the verdict is stamped **BELOW-HEURISTIC-FLOOR** and the
measured Δ is reported as a *serving-fidelity* delta, not a *reasoning-capability* delta. The
gap is real either way; what it is a gap *in* depends on this stamp.

## Design

**Task family:** `nearmiss_mix` (adversarial primality near-misses, `task_gen_v3.py`): "of
these five numbers, how many are prime?", balanced answer range {1,2,3,4}, **chance floor
0.25**, band [0.35, 0.60], gold computed by deterministic Miller–Rabin (never judged).

**Rungs (pre-declared, all three fixed before any call):**
- **M30 — primary.** Both hosts previously read in-band here (paid 0.500 n=200; free 0.510
  n=200, LEVELED, `ergon/probe/ledgers/coldband_m30_free/bandread.json`), so the cell has
  headroom in both directions and neither host is floor- or ceiling-compressed.
- **M20, M40 — secondary**, spanning the band (paid M20 0.640; paid M40 0.35 at n=40), to
  test whether any tier gap is uniform across difficulty or a rung×host interaction.

**Manifests:** one fresh manifest per rung, generated at a **preregistered seed committed
with this proposal before the first API call** (proposed: 20260902), sha256-pinned
(`manifest_sha256`, `generator_sha256`) and committed in the same commit as this spec.
Fresh seeds, not the pinned campaign manifests — block A (`e6b1e001bf79e3ef`) is pinned
precisely so it cannot be reused for side experiments, and the heuristic floor was shown to
generalize across seeds, so fresh seeds cost nothing.

**Sample sizes (fixed-n, no sequential extension):**
- M30: **n = 1,600 paired items** (each item sent to both hosts), one scoring rep per host.
- M20, M40: **n = 400 paired items each**, one scoring rep per host.
- Dispersion diagnostic: rep-2 on a 200-item random subsample of the M30 manifest, both
  hosts (movable-share diagnostic only; never enters the primary statistic).
- Totals: 2,600 paid calls ≈ **$8.3** at the measured $3.2/1,000-call burn (paid v4-flash,
  reasoning outputs 800–3,900 tokens); 2,600 free calls ≈ 2 days at the observed
  ≥1,500 calls/day floor, 2.0s spacing, yielding to `campaign.lock`.

**Collection protocol:** identical prompt bytes to both hosts; `max_tokens = 16384` (the
8192 cap truncation-confounded P1); `timeout = 420s`; retries 0; append-only fsynced JSONL
ledgers recording per row: uid, rep, status, error_type, latency_s, completion_tokens,
extracted_int, attempt_text (4,000-char cap), ts_utc, host, executor, **and the served
`model_id` string** — the served checkpoint is part of the experimental unit. The two hosts'
legs for a given rung are collected **interleaved within a shared 7-calendar-day window** so
version drift cannot masquerade as a tier effect.

**Scoring:** exact match of `extract_numeric(text).value` against `gold_int`, rep-1 only.
Truncated and parse-failed rows score wrong in the primary read (identical rule both hosts),
with a mandatory sensitivity read conditioning on rows OK-and-parsed on **both** hosts.

**Primary statistic:** per-item paired difference at M30. Point estimate
Δ̂ = (b − c)/n where b = items paid-right/free-wrong, c = free-right/paid-wrong; exact
McNemar test on (b, c); 95% CI on Δ by Newcombe's paired method; TOST at 90% CI against the
±4.0pp margin. Empirical between-host discordance π̂_d = (b+c)/n is stamped in the read.

**Power / decidability (computed before choosing the thresholds, per the gate-vs-SE rule):**
planning π_d = 0.45 (conservative; within-host rep-to-rep movable share measured 0.385–0.415).
At n = 1,600: paired SE = √(π_d/n) = **1.68pp**; the 4.0pp margin is 2.4× the SE.
- Superiority MDE ≈ **4.6pp** (80% power, α = 0.05 two-sided).
- Equivalence at ±4.0pp is concludable whenever |true Δ| ≲ 1.2pp (90% CI half-width 2.76pp).
- **Both verdicts are therefore reachable** (gate-reachability check passed on paper); the
  region Δ ∈ (~1.2pp, ~4.6pp) is preregistered as **UNDECIDED** and must be reported as
  UNDECIDED with its interval — never quoted as a bare point estimate (the +14pp incident
  began as exactly such a quote).
- If observed π̂_d > 0.45, recompute n_required for the same half-widths and stamp
  **UNDERPOWERED-BY-DISPERSION** instead of forcing a verdict.

Secondary rungs are read with Bonferroni k = 2 (α = 0.025 each); at n = 400 they are
screening-resolution (paired SE ≈ 3.4pp) and support only sign/interaction checks, never a
headline delta.

## Controls

1. **Item-level pairing.** Same sha-pinned manifest, same prompt bytes, to both hosts —
   removes item-sampling variance from the tier contrast entirely. No cross-host pooling into
   any band statistic (R9 stands regardless of outcome).
2. **Well-posedness (C1, non-LLM, $0):** the deterministic solver
   (`task_controls.py::deterministic_solver`) must recover gold from prompt text at
   **1.0000** on every manifest before any API call is made. Anything less invalidates the
   manifest, not the hosts.
3. **Heuristic floor stamped beside every read:** coprime-to-30 count, re-scored on each
   fresh manifest (expected ≈ 0.52). Chance floor 0.25 stamped likewise.
4. **Transport floor 0.95** per (host × rung) cell — a dead lane scores every row wrong and
   would emit a confident tier gap in whichever direction the dead lane sits. Direction of
   this confound: pushes *toward* H1 if the free lane degrades, so it is gated, not reported.
5. **Truncation gate 2.0%** per cell at 16,384 tokens (rep-1), per `chain_run.TRUNCATION_GATE`.
   Direction: truncation drags the truncated host down artifactually (the truncation-flatters-
   a-gate defect, inverted); hence gated per host, not differenced away.
6. **Scoring-symmetry control:** |parse-fail rate(paid) − parse-fail rate(free)| must be
   ≤ 2.0pp, else the cell is SCORING-CONFOUNDED; and the primary read must agree in sign with
   the both-hosts-parsed sensitivity read or the verdict is withheld.
7. **Serving-config drift control:** per-host `model_id` must be constant within a cell (any
   mid-cell change → WINDOW-BROKEN for that cell); median completion_tokens per host reported,
   and a >2× ratio flags a sampling-default confound in the read (reported, not gated —
   token-budget differences are part of what "tier" means).
8. **Time control:** shared 7-day collection window per rung, interleaved; timestamps on
   every row.
9. **No mid-run accuracy reads:** the collection code writes rows and never computes
   accuracy; the read function runs once, at coverage completion (structural guard against
   informal sequential stopping).

## Preregistered falsifiers (each with an explicit numeric threshold)

- **F1 (equivalence kills H1):** the 90% TOST CI of paired Δ_M30 lies entirely within
  **±4.0pp** → H1 falsified; tiers practically equivalent at probe resolution; record as the
  T-series control anchor.
- **F2 (sign kills H1):** Δ̂_M30 ≤ 0 **and** the 95% CI upper bound < **+4.0pp** → H1
  falsified with direction information (free ≥ paid).
- **F3 (interaction kills the "tier effect" reading):** Δ_M20 and Δ_M40 have opposite signs
  and **each** 95% CI excludes 0 → any M30 result is reported as a host×rung interaction,
  not a tier effect; H1 as stated is falsified.
- **F4 (floor sanity, instrument falsifier):** either host's cell accuracy
  < 0.25 + 2·SE (= **0.2716** at n = 1,600; **0.2933** at n = 400) → the cell is treated as a
  transport/extraction defect (INVALID), never as "low capability".
- **F5 (framing falsifier):** both hosts ≤ **0.5225** at M30 → BELOW-HEURISTIC-FLOOR stamp;
  the result may not be described as a reasoning-capability gap in any downstream document.
- **F6 (admissibility, per cell):** transport_ok < **0.95**, or truncation_rate > **0.02**, or
  deterministic-solver agreement < **1.0000**, or parse-fail differential > **0.02** → the
  affected cell emits no number at all (INVALID-TRANSPORT / TRUNCATION-CONFOUNDED /
  MANIFEST-INVALID / SCORING-CONFOUNDED respectively).
- **F7 (dispersion honesty):** observed π̂_d > **0.45** at M30 → UNDERPOWERED-BY-DISPERSION;
  the recomputed n_required is stamped and no equivalence or superiority verdict is issued
  at n = 1,600.

## Stopping rule

- **Fixed-n design.** Collection stops when every (rep, uid, host) cell in the preregistered
  manifests is filled — 2,600 rows per host + 400 rep-2 rows. No extension, no early success
  declaration, no interim accuracy computation.
- **Quota walls (HTTP 429/402):** pause-and-resume against the append-only ledger (the
  coldband pattern); a wall never restarts or reseeds anything.
- **Windows:** each rung's two host-legs must both complete within a shared **7-calendar-day
  window**; the whole experiment within **14 calendar days** of the first call. A rung whose
  window breaks is stamped WINDOW-BROKEN and reported descriptively only. At day 14, any cell
  below **90% coverage** is stamped ABANDONED-INCOMPLETE; its rows are committed (rows ship
  in the same commit as any verdict — no verdict without rows), but it emits no verdict.
- **Spend cap:** **$12** on the paid lane. If projected total spend exceeds the cap at 50%
  paid-leg coverage, the paid leg halts → INCOMPLETE. Free-leg collection always yields to
  `campaign.lock` and never contends with the main campaign.
- **One read.** The read function executes once per rung at coverage completion (or at the
  window boundary for the descriptive stamps above). Verdict, rows, ledger sha256s, and both
  manifests' sha256s are committed together.

## Unit of inference

The **manifest item, paired across hosts**, within one (family × rung × host-pair ×
collection-window × served-model_id) cell. n = number of distinct items (1,600 / 400 / 400)
— **never** number of API calls and never item×rep rows (the SE-on-the-wrong-unit rule:
reps are a dispersion diagnostic, not replication of the unit). SEs and CIs are computed on
per-item paired differences; the discordant-pair count (b + c) is the effective information,
and it is stamped in the read.

Claims license accordingly: the verdict speaks about *deepseek-v4-flash served on the free
NVIDIA host vs the paid DeepSeek host, on this family, at these rungs, in this window* — and
nothing wider. It does not speak about "free tiers" as a population, other model families,
other task families, or other dates (the served checkpoint behind a host alias can change;
that is *why* the window and model_id are inside the unit).

## Prior work bearing on this design (cite repo paths if any; 'none found' is acceptable)

- **`ergon/probe/solver.py` (lines 37–50):** the host/family pinning rule —
  `nvidia:deepseek-v4-flash` and `deepseek:deepseek-v4-flash` are the same FAMILY on
  different HOSTS, never compared as the same solver. This proposal is the experiment that
  rule anticipates.
- **Existing cross-host reads (the priors this control formalizes):**
  `ergon/probe/ledgers/decision_M20_n200.json` (paid M20 0.640, n=200);
  campaign free-host M20 rep-1 0.624 (n=351, truncation-corrected) under
  `ergon/probe/ledgers/campaign/` → corrected delta **+1.6pp**;
  `ergon/probe/ledgers/decision_M30_n200.json` (paid M30 0.500, LEVELED, n=200);
  `ergon/probe/ledgers/coldband_m30_free/bandread.json` (free M30 0.510, LEVELED, n=200,
  2026-09-02) → delta **−1.0pp**. Point estimates straddle zero across rungs; neither was
  collected paired or powered for a delta — that is the gap this design closes.
- **The withdrawn +14pp host delta:** the original claim compared paid n=200 against a free
  n=40 read that was itself UNDECIDED with interval [0.303, 0.697]; corrected 2026-08-21.
  This proposal's UNDECIDED-must-stay-UNDECIDED reporting rule and paired design are the
  direct countermeasures.
- **`ergon/probe/FINDING_heuristic_floor_2026-08-24.md`:** the 0.5225 non-reasoning floor;
  source of the ±4.0pp margin and of falsifier F5.
- **`ergon/probe/task_controls.py`:** the non-LLM control battery (deterministic solver,
  cross-validated surface predictors, heuristic floor) reused verbatim as controls 2–3.
- **`ergon/probe/coldband_m30_free.py`:** the collection/read pattern this spec inherits
  (append-only fsynced ledger, transport floor 0.95, truncation gate 2%, campaign-lock
  yielding, decidability-aware verdicts including n_required recomputation).
- **`ergon/probe/ESCALATION_P1_BAND_2026-08-21.md`** and
  **`ergon/probe/ledgers/axis_paid_M30-M40_n40.json`:** rung selection history, including a
  TRUNCATION-CONFOUNDED sweep at 8,192 tokens — why max_tokens is 16,384 here.
- **`ergon/probe/PREREG_block_B_merge_rule_2026-08-25.md`:** precedent for executable merge
  rules that can refuse; this design's F6 gates follow that pattern (a cell that fails
  admissibility emits no number, not a caveated number).
- Searched `evidence_wiki/` for prior free-vs-paid tier experiments: **none found** beyond
  the ledger reads cited above.
