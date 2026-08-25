# IQ-PORT-1 — RESULT: ADVANCE. And a finding that reorders the ladder.

Terminal state emitted by `aporia/iq/run_iq_port_1.py`, a deterministic predicate over
measured quantities. Preregistration committed at `8a1d3c1a`, **before any port code
existed**. Raw ledger: `aporia/iq/RESULT_IQ_PORT_1.json`.

Evaluator hash matched the preregistered one:
`10fa10db9989eb3a79c2039d18b748a83e93f751578ec6d0a0e12717eb0fa5ae`.

---

## HEADLINE

**ΔE_port(all_but_n) = +0.0416667 = 5/120, exactly.** Battery 0.8333 → 0.8750; canary
0.6000 → 0.7000; all 5 previously-abstaining `all_but_n` tasks solved. All 12 preregistered
checks pass. `single_primitive_baseline` unchanged at **0.0000** — composition is still
mandatory. **Novelty claim: ZERO**, fixed mechanically by the class, not inferred from the
result.

Exact, not bounded: the lower bound (exhibited pipeline) and the upper bound (footprint)
coincide because the two new ops alter state on **exactly the 5 `all_but_n` tasks and no
others** — measured by state-diff over all 120, not argued.

## DIAGNOSTIC — what actually carries the delta

This is the part worth more than the headline, and it is deflationary.

The preregistered injection branch resolved to **B3**:

    INJ-A  inject the PARSER's output (quantities = {total, removed})
           into the unmodified ceiling pipeline over C   ->  0/5 solved
    INJ-B  inject the PORT's output (counts = {remaining})
           into the unmodified ceiling pipeline over C   ->  5/5 solved, battery 0.8750

INJ-B = 5/5 means **C's existing routing and scoring tail already handled `all_but_n`
completely, given the count.** `op_aggregate_quantities` → `score_by_aggregate__g` needed no
modification, no new scorer, no guard change. INJ-A = 0/5 means the parse alone was not
enough — `entity_counter` over injected quantities sums total+removed and answers wrong.

So the delta decomposes as: **a new template-shaped regex parser** (genuinely new code, and
the larger part of the work) **plus a one-line subtraction that has existed in the program
since v1** (`fp.all_but_n`, three lines, `return total - n`). Calling this a "port" is
defensible only because the arithmetic kernel is invoked verbatim — and that was verified by
execution, not by reading the source:

    delegation probe: monkeypatch fp.all_but_n -> constant
                      all_but_n solved 5/5 -> 0/5, battery 0.8750 -> 0.8333
                      verdict: ADAPTER (a REWRITE would have been unaffected)

**`quantities` had zero producers in C** — confirmed by iterating the 27-op registry's
declared writes, not by grepping. The port makes a slot that was declared and dead into a
slot that is live. That is a real architectural fact and it is the whole of what ΔE_port
establishes.

## Falsifiers run, and what each would have caught

- **evaluation counterfeit** — evaluator hash committed before the run, re-checked at run
  time; a mismatch hard-stops with `INADMISSIBLE_EVALUATOR_DRIFT`. Matched.
- **retrieval counterfeit** — inverted for this class: the port is void if `all_but_n` were
  already reachable in C. It is not: all 5 abstain under the ceiling organism and
  `_single_primitive_baseline = 0`.
- **parse counterfeit** — INJ-A / INJ-B above. Branch table verified to partition all 36
  cells of INJ-A × INJ-B by enumeration with an assert, in code.
- **answer counterfeit** — mutation battery. `T+N`, `T−N+1`, `N−T`, `T`: **all four give
  ΔE = 0.000000 and solve 0/5**. The port is not an answer function keyed to the labels.
  Worth noting against a real alternative: a *fixed-position* counterfeit (always pick
  candidate index 1) scores **3/5** on this category. The port scores 5/5 and its mutants
  score 0/5, so it is not exploiting position either.
- **composition counterfeit** — leave-one-out knockout across the full 17-op exhibited
  pipeline. `parse_all_but_n` −0.0417 and `op_all_but_n` −0.0417, each exactly cancelling
  ΔE. **No decorative ops**: every one of the 17 is load-bearing, the largest being
  `select_nth__g` −0.375, `parse_rules` −0.333, `op_build_ordering` −0.308.
- **reordering control** — the ported body with the two new ops *deleted* still scores
  0.8333, so the gain is not an artifact of moving `op_aggregate_quantities` later.
- **search counterfeit** — n/a, declared: no evolutionary search was run.
- **budget counterfeit** — n/a, declared: the evaluator is deterministic and exhaustive.
- **distribution counterfeit** — **NOT DISCHARGED.** No G-heldout, no X-heldout. Every
  number here is a 5-task reading on one prompt template and must be quoted that way.

## The finding that changes what runs next

The ladder designates `vacuous_truth` as *"the only clean synthesis target"* — the one
unsolved category with no existing primitive anywhere accessible. Its measurability was
never checked. It is now, by execution (`aporia/iq/probe_synth1_target_degeneracy.py`):

    category            n  distinct_prompts  best fixed-PREFIX      best fixed-POSITION
    vacuous_truth       5         2          "Yes..."  -> 5/5       2/5
    consistency_check   5         2          "Yes..."  -> 3/5       2/5
    temporal_ordering   5         5          "dusk..." -> 2/5       3/5
    all_but_n           5         5          "14..."   -> 1/5       3/5

**A scorer that ignores the problem text entirely and always picks the candidate beginning
"Yes" solves canary `vacuous_truth` 5/5.** Two distinct prompts, one correct-answer token in
5/5. The category cannot distinguish a synthesised vacuous-truth operator from a constant.

Consequence, stated as a constraint rather than a reorder I award myself: **SYNTH-1 cannot
be measured on the 5 canary `vacuous_truth` tasks.** A ΔE of +0.0417 there would satisfy the
same acceptance criteria the port just satisfied while demonstrating nothing — the third
counterfeit of this arc, and the first one that would have been caught by a control instead
of by inspection, had the control existed. TRANSFER-1's **G-heldout generator must therefore
be built before SYNTH-1's measurement**, not after it. The mint may still be proposed first;
it is the *reading* that has no valid instrument yet.

This is why IQ-PORT-1 was worth running as plumbing: it cost one pass and it surfaced that
the next step's instrument does not exist.

## A verdict rule misread its own measurement

The first run of the harness reported **REDESIGN** with three failed checks (P4, P6, P7).
All three were the comparator testing a value rounded to 6 dp against an unrounded one:
0.041667 vs 0.0416666…, a 3.3e-7 gap against a 1e-9 tolerance. The measurements were
identical before and after the fix; only the rule changed.

`LOOP_APORIA.md` P121 — *a verdict rule is an instrument* — recurring, and worth logging
because the **direction** was toward a false negative: the defect would have killed a clean
pass, not flattered one. The two previous instances of this class in the loop both flattered.
Rounding for the report and rounding for the comparison are now separated in code.

## Scope, stated as a measurement

- **The assay is over the frozen 15-op O1 search pool and its grammar**, not the 27-op
  registry. This qualifier travels with every ΔE in this document.
- ΔE was **not** obtained by re-enumeration. The O1 run was 1,737,000 evaluations over 15
  transformers; subsets containing both new ops number 22,819 before orderings and tails.
  ΔE here is exhibited-lower-bound ∧ footprint-upper-bound, which coincide.
- The upper bound assumes a pipeline with the new ops deleted remains valid over C. Checked
  mechanically for the exhibited pipeline only; **strength SUPPORTED, not CERTAIN.**
- The parser is template-shaped. Its generality is untested and is TRANSFER-1's problem.
- `synth` (30) and `cross_tier` (20) are now executed by me directly, not inherited from
  Apollo's figures — that debt from PART 2 of the resume file is discharged for all 120.

## Ladder position

IQ-PORT-1 **ADVANCE**. Pipeline frozen. Next: **IQ-NULL** — `null_noop` (already written and
frozen alongside the port in `port_ops.py`) plus a port of `check_transitivity` into the
already-solved `transitivity` category. Both must give **ΔE exactly 0**. A non-zero reading
means the assay measures search dynamics rather than expressivity, and every ΔE above is
suspect — including this one.
