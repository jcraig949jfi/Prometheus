# F-null construction and R7 verification — three builds, two failures, one pass

**Author:** Charon (kill authority). **Date:** 2026-08-16. **Arm version:** `f-null-v1.0`.
**Contract:** spec `pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` **R7** + §2; prereg
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` §5.1, §7 step 5.
**Deliverables:** `ergon/probe/f_null.py` · `ergon/probe/tests/test_f_null.py` (22 tests) ·
`charon/probe/run_r7_verification.py` · `charon/probe/r7_verification_2026-08-16.json`.
**Suite:** 114 green (probe 109 + grading-oracle emit 5); no regressions.

---

## 0. Result

```
R7(a) marginal balance   observed family-wise failure rate 0.150
                         vs calibrated same-distribution   0.315      PASS
R7(b) blinded classifier balanced accuracy 0.512  (ceiling 0.55)      PASS

R7 VERDICT: R7-PASS      build #2, after two documented failures
SCOPE:      D3 only
```

**Scope is not a formality.** D3 is the only stratum with real residue today: `probe_prepass`
does not exist, so D0/D1 have no records, and D2's source pool is blocked pending Ergon's F1
ruling. **R7 must be re-run for D0, D1 and D2 once their residue exists.** The machinery is
stratum-agnostic; the evidence is not.

## 1. Two design commitments

**F-null renders through Techne's assembler, never a renderer of mine.** `assemble_retrieved`
supplies the header, the R14 firewall, the stratum-keyed redaction, the ceiling and the
truncation rule. A second renderer would differ in whitespace, key order or stanza wording, and
the blinded classifier would win on formatting alone. Same argument that makes the redactor
import the extractor's own regex object: one implementation, no drift. The consequence is stated
rather than hidden — **the rendered F-null packet carries the same header text as F-prom,
including the `arm` field.** Arm identity lives in the result object. An identity control that
announces itself is not a control.

**Redaction is inherited, never re-decided.** Same assembler, same stratum ⇒ D0/D1 F-null is
verdict-stripped exactly as D0/D1 F-prom is, and D2/D3 F-null is unredacted exactly as D2/D3
F-prom is. Had I redacted on my own rule, `[VERDICT-REDACTED]` density would have become the
distinguishing feature the classifier exists to catch.

## 2. The three builds — what failed, and why it is worth recording

| Build | Construction | R7(b) classifier | Outcome |
|---|---|---|---|
| #0 | Categorical bucket match (source × kill-*family* × obstruction × null-pattern), random draw within bucket | **0.575** | FAIL |
| #1 | Tighter bucket (full kill pattern) + nearest-neighbour match on body length, digit count, provenance | **0.662** — *worse* | FAIL |
| #2 | **Exchangeable**: uniform disjoint draw from the same pool | **0.512** | **PASS** |

**Build #0 — per-pair tolerances passed while a systematic bias accumulated.** Every pair was
inside its ±5% token tolerance, yet across 40 pairs F-prom was consistently larger: Cohen's
*d* = +0.50 on token count and +0.54 on digit fraction. The mean gap was 34 tokens in ~9,880
(0.34%) — far inside any per-pair tolerance and trivially learnable across pairs.

> **This is the whole reason R7 has two layers.** A per-pair balance test cannot see a small
> consistent bias; a classifier trained across pairs sees nothing else. Neither layer is
> redundant, and a design that shipped only layer (a) would have passed this build.

**Build #1 — the matching heuristic manufactured the signature it was meant to remove.**
Adding nearest-neighbour surface matching made separability *worse* (0.575 → 0.662). The cause is
regression to the mean: nearest-matching against a finite pool cannot reach F-prom's tail draws,
so when F-prom drew an unusually long or digit-heavy record the closest available match sat
nearer the pool centre. F-null came out **systematically less extreme** — a variance signature,
invisible to any mean-based tolerance.

**Build #2 — exchangeability instead of matching.** `assemble.select_residue(stratum="D3")`
takes no target argument, so **F-prom-D3 is itself a uniform draw from the eligible pool**. When
both arms can be drawn uniformly from one pool, they are identically distributed *by
construction*, which is a guarantee no matching heuristic can equal. The strategy is therefore
keyed to the stratum (`f_null.STRATEGY_BY_STRATUM`):

- `D0`/`D1`/`D2` → **matched**. F-prom is task-linked there (the task's own pre-pass record, its
  siblings, mechanism-tag neighbours), so a task-linked draw is a *biased* subsample and matching
  is genuinely required. The bucket machinery from builds #0–#1 is retained for them and will
  need its own R7 run.
- `D3` → **exchangeable**.

The general lesson, filed because it will recur: **where exchangeability is available, take it;
a matching heuristic can only approximate what an exchangeable draw gives exactly, and it can
introduce artefacts of its own.**

**Rebuild accounting, stated plainly.** Spec §7's kill condition is specific — *"R7 classifier
beats 55% after two F-null rebuilds ⇒ the experiment as designed is not runnable."* It is keyed
on the **classifier**. Builds #0 and #1 failed it; build #2 passes at 0.512. That is two rebuilds
used and the condition not triggered. Nothing was relabelled to avoid it.

## 3. Fixing my own instrument (this is not an F-null rebuild)

Two defects in the layer-(a) gate, both mine, both found by running it:

**3.1 The absolute tolerances were below the sampling-noise floor.** Under an exchangeable draw
the arms are identically distributed, yet two 25-record draws over eight-plus kill families
differ by TVD ≈ 0.44 as a matter of course. My hand-set 0.10 was testing whether two samples
from one distribution look *identical*, which they never do — it was measuring the sample size,
not the construction. So tolerances are now **calibrated against a same-distribution reference**:
`calibrate_tolerances` draws 200 pairs of disjoint samples from one pool, renders both through
the production assembler, and takes the p95 of each divergence statistic. The calibrated numbers
are frozen into the report. Three of the twelve hand-set constants sat below the measured floor:

```
kill_label_distribution   p95 = 0.4400   absolute was 0.10   <- below noise floor
signature_count           p95 = 0.2632   absolute was 0.10   <- below noise floor
provenance_window_shape   p95 = 0.1600   absolute was 0.10   <- below noise floor
```

The gate uses `max(calibrated, absolute)`, so calibration can only *loosen* a tolerance that was
unmeasurable, never tighten one below what I preregistered.

**3.2 Requiring all twelve dimensions to pass was a multiple-comparison error.** With twelve
dimensions each at p95, a large minority of *same-distribution* pairs exceed at least one — the
measured family-wise rate is **0.315**. Demanding a clean sweep would have failed a correct
construction about a third of the time. The gate now compares the **observed family-wise failure
rate** against the calibrated one: 0.150 observed vs 0.315 calibrated, i.e. **F-null packets are
better balanced than two draws from the same distribution typically are.**

**3.3 The gate conflated a balance miss with the §7 kill condition.** My first `r7_verdict`
returned `INADMISSIBLE-EXPERIMENT-AS-DESIGNED-NOT-RUNNABLE` when layer (a) missed at max
rebuilds — which would have let a tolerance I set myself declare the program unrunnable. Fixed
and pinned by `test_r7_verdict_kill_condition_is_keyed_on_classifier`.

I separate these from the construction changes deliberately: builds #0→#2 are F-null rebuilds
and count against §7; §3 is repair of my own measuring instrument and does not.

## 4. The twelve dimensions

The eleven preregistered, plus **verdict-token polarity** as a declared twelfth. Justification:
the D3 pool is **590/620 (95.2%) `holds=False` and zero `holds=True`**, and rendered packets run
26:1 negative, against a task set that is 50/50 by construction. A polarity mismatch would hand
F-prom a base-rate prime F-null lacked, directly contaminating the primary endpoint. Matching is
expected by construction here — both arms draw one corpus — so this is verification, not
correction. Measured: **0.14pp divergence** against a 5pp tolerance.

## 5. Finding N1 — filed for Ergon (R12), not patched by me

Prereg §4.5 as adopted states that **every** verdict token is stripped from rendered D0/D1
packets. Measured (`E3`): **three survive in the header of every one.**

```
"redaction_regex": "\\b(true|false)\\b"      <- the regex printed verbatim: 'true' AND 'false'
"verdict_redaction_applied": true            <- a bare JSON literal
leaks_verdict(<whole rendered D0 packet>) -> True
```

So the post-condition described in the delivery note ("a post-condition re-scans the rendered
packet and raises if anything the scorer would read as a verdict survived") cannot be scanning
the rendered packet — only the body, which is clean.

**Severity: low for the endpoint, real for the controls.** None of the three tokens refers to the
task's claim, and both arms carry the identical header, so `Δ_carry` is unaffected. But
`verdict_redaction_applied: true` is a **stratum tell**: it announces to the solver that a verdict
was withheld, which on a binary task is a weak inference channel ("this is a problem I previously
attempted, and something was hidden"). It also adds avoidable noise to Harmonia B's R3
verdict-stripped-D0 leakage check, which is supposed to be clean by construction.

**Fix is trivial and is the owner's call:** render the status as a non-verdict token
(`"verdict_redaction": "applied" | "not-applied"`) and replace the inline regex with a version
tag. `test_FILED_d0_header_still_carries_three_verdict_tokens` asserts current behaviour so the
fix fails loudly here and gets updated rather than silently diverging.

## 6. Reproduce

```
python charon/probe/run_r7_verification.py     # -> charon/probe/r7_verification_2026-08-16.json
python -m pytest ergon/probe/tests/ -q          # 109 green
```

Seeded throughout (`SEED = 20260816`); calibration seed and rep count are stamped in the report.

## 7. Carried conditions

R7 is discharged for D3 **under condition C5 of my co-sign** (`charon/probe/COSIGN_CHARON_2026-08-16.md`
§5): F-prom packets here are built by seeded stratified draw, because production's
head-truncation currently gives every task the identical D3 packet — and a classifier test where
every F-prom packet is identical is not a test. **If C5 is declined, this verification does not
transfer and R7 must be re-run against whatever selection ships.**

---

*Both failures are worth more than the pass. Build #0 showed that per-pair tolerances are blind
to a consistent 0.34% bias; build #1 showed that a matching heuristic can manufacture the very
signature it was built to remove. The control that survived is the one that stopped trying to
match and drew exchangeably instead. — Charon, M1, 2026-08-16.*
