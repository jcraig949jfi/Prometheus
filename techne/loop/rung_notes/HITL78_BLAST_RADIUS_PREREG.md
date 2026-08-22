# Pre-registration: does HITL #78 have a measurable effect on live output?

Written cycle 042 **before measuring the outcome**, per round-12 review:

> Cycle 042 becomes a real test only if HITL #78 has a predeclared consequence that can be
> measured against live behavior. PASS as real-substrate science: #78 makes a predeclared,
> quantitative prediction about live outputs and that prediction is tested. FAIL back into
> diagnosis: #78 is merely located, characterized, or given another instrument.

## What I already knew when I wrote this (disclosed, not pretended away)

- `loader_drop_rate()` on `ergon/probe/ledgers/campaign/campaign_log.jsonl`: **956 rows on disk,
  0 accepted by the shipping `load_prepass`, 625 accepted by the audit shim.** Fifteen cycles.
- `load_prepass` has six non-test call sites: `campaign.py:312`, `pilot_d0.py:49`,
  `r3_live.py:38`, `r3_supplement.py:38`, `run_r7_d0d1.py:43`, `static_leakage_d0.py:21`.
- `campaign.py:312` reads `p1_prepass.jsonl` — **a different file from the one I have been
  measuring.** I have NOT yet checked which file the other five read. That check is the outcome
  and is deliberately deferred until after this document is committed.

## The predeclared prediction

**If #78 matters**, then replaying the same live ledger through two observational conditions —

    AS-RUNNING        ergon.probe.assemble.load_prepass       (what production does today)
    COUNTERFACTUAL    techne...real_substrate._audit_load_prepass  (the condition #78 implies)

— produces divergent downstream output on a file some consumer actually reads. Concretely:

**Y₁ — selection volume.** `len(select_residue(pool, ...))`.
Prediction: as-running = 0, counterfactual > 0.

**Y₂ — packet content.** token count of `assemble_retrieved(...)`.
Prediction: as-running yields an empty or degenerate packet; counterfactual yields a populated
one. **Δ ≥ 1 record and Δ > 0 tokens.**

**Y₃ — τ coverage.** `tau_from_records(pool)`.
Prediction: as-running = empty mapping; counterfactual = non-empty.

**Y₄ — consumer reach (the gating observable).** The number of the six non-test call sites whose
ledger path resolves to a file on which `load_prepass` currently drops 100%.
Prediction, stated as a range because I genuinely do not know: **at least 1 of 6.**

## Decision rule, fixed in advance

- **BLAST RADIUS CONFIRMED** iff Y₄ ≥ 1 *and* Y₁/Y₂/Y₃ diverge on that consumer's actual file.
  Then #78 is a live defect with measured downstream consequence, and the size of Y₂ is its cost.
- **BLAST RADIUS NULL** iff Y₄ = 0 — no consumer reads a file where the loader drops everything.
  Then **#78 exists but has no measurable effect on this live run**, fifteen cycles of escalation
  were aimed at a file nothing consumes, and that is the finding. It is reported as prominently
  as a positive result would have been.
- **PARTIAL** iff Y₄ ≥ 1 but the affected consumers are themselves not run (dead scripts). Then
  the exposure is latent, and prevalence-vs-exposure applies exactly as round-11 review framed it
  for the defect class: the defect is real, the live risk is not.

## Constraint accepted

> No new general-purpose instrument in cycle 042 unless required to answer the predeclared live
> question.

Nothing general-purpose gets built here. The replay uses functions that already exist —
`load_prepass`, `_audit_load_prepass` (cycle 025), `select_residue`, `assemble_retrieved`,
`tau_from_records`. Read-only throughout; ergon is not patched.

## What would make me wrong

If as-running and counterfactual produce the *same* downstream output despite the 956-to-0 drop,
then something downstream is compensating and my model of the pipeline is wrong. That would be
the most interesting outcome of the three and it is why Y₁–Y₃ are measured rather than assumed
from the record counts.
