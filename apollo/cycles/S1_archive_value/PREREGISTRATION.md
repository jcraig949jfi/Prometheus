# S1 — ARCHIVE VALUE TEST — PREREGISTRATION (v0.2 DRAFT — NOT YET FROZEN)

> **STATUS 2026-09-01: NOT FROZEN.** The pilot (see `PILOT_FINDING.md`) validated the
> harness but showed this document's PRIMARY endpoint operationalization (transfer_rate
> at tau=75th-pct-random) is DEGENERATE at feasible budgets: the source search produces
> no functional organisms (best passes 1-2/12 cases), so tau collapses to the floor and
> every member reads as "useful." The endpoint is being re-anchored on a solvability
> calibration BEFORE freezing. The kill threshold and controls below stand; only the
> endpoint's operationalization changes. No scored cell has been run.


> **Apollo (M2), 2026-09-01.** Written and committed BEFORE the campaign runs, per
> falsification-first doctrine and the HITL review of 2026-09-01. This is the ONE
> serious substrate-miner falsification campaign Apollo was authorised to run. It is
> designed to be able to KILL the substrate-miner role, not to confirm it.
> **Foundry pin at freeze: `50b5c232...`.** If the host release changes mid-campaign
> the client refuses to run (pin mismatch) and the campaign resumes under a re-declared
> pin — the pin is recorded per burst so a release boundary is auditable, never silent.

---

## 1. The proposition under test

Gen-1's proposition ("evolutionary composition autonomously widens reasoning
capability") remains falsified and is NOT retested here. S1 tests the weaker Gen-2
proposition:

> **Quality-diversity search (MAP-Elites) produces a more useful population of
> transferable and behaviourally distinct structures than matched random search, under
> equal evaluation budget.**

"Useful" is defined operationally in §5. The archive itself is on trial — coverage is
NOT assumed to be a good. A MAP-Elites run that fills niches whose members neither
transfer nor improve downstream is **decorative ecology**, and S1 must be able to say so.

## 2. Primary endpoint (declared primary before results)

For a source population P (a MAP-Elites archive or a matched random population) trained
on world W_s, and a held-out target world W_t of a DIFFERENT family, over the DISTINCT
members of P (deduplicated by `genotype_addr`, so a population's raw size and its
duplicate rate cannot inflate it):

    transfer_rate(P, W_t) = ( # distinct members with fitness >= tau_t on W_t ) / |P_distinct|

This is P(useful on W_t | member drawn from P) — the reviewer's primary quantity — and
is size-invariant, so a MAP-Elites archive (~15 members) and a random population (~300
evaluations) are compared on equal footing. **tau_t is the 75th-percentile fitness of
the DISTINCT random population on W_t** (a per-target, per-run relative bar set from the
RANDOM source so MAP-Elites cannot game it). The primary comparison is

    ENRICHMENT = mean_pairs transfer_rate(map_elites_archive) / mean_pairs transfer_rate(random)

pooled across all cross-family (W_s, W_t) pairs and seeds. Both the rate and tau are
defined structurally here before any number exists.

## 3. Secondary endpoints (all recorded, none primary)

- **held-out fitness**: best/mean fitness of P on W_t (continuous, alongside the count).
- **behavioural coverage**: archive cells occupied / total; and behavioural entropy over
  the engine's behaviour descriptor.
- **duplicate rate**: fraction of P whose members share a `genotype_addr` or an
  evaluation `result_hash` (inflation guard — the charter's "report the canonical core,
  not the cell count").
- **boundary-pair yield**: count of (parent, child) pairs one mutation apart whose
  behaviour/fitness differs across a declared threshold (a sharp-boundary specimen —
  charter §3). Parent links come from `ARTIFACT_MUTATED.parent_ids`.
- **motif recurrence**: byte-level n-gram substructures over `genotype_b64` that recur
  across independent runs/worlds (frequency ONLY, not importance — §7 caveat).
- **adaptation distance**: mutations to recovery when a transferred member is allowed a
  tightly-bounded (<=50-eval) local search on W_t. Reported, not primary.

## 4. Design

- **World families (independently-constructed construction semantics):**
  - F1 AFFINE:      f(x)=a*x+b
  - F2 PIECEWISE:   f(x)=|x|+c ; f(x)=max(x,k)
  - F3 MODULAR:     f(x)=((x mod m)+m) mod m
  - F4 QUADRATIC:   f(x)=x*x + c ; f(x)=x*x - x
  - **3 instances per family x 3 live families used for the scored campaign = 9 live
    worlds** (F1,F2,F3 scored; F4 held in reserve for a replication tie-break only).
- **Dead-world control (§6a):** DEAD-RANDOM — outputs are a fixed random permutation of
  the input domain, i.e. NO consistent function. Target is unreachable by any engine.
- **Drivers:** `random` (mandatory baseline) vs `map_elites`.
- **Matched:** identical `budget` (300 evaluations), identical seed set
  {20260901, 4242, 7}, identical engine (`stackvm-v1`, deterministic → clean replay),
  identical task per (world) across drivers.
- **No repair during the campaign.** No primitive additions, no evaluator changes, no
  budget rescue because a run looks poor, no ontology churn. Nulls are recorded.
- **Populations preserved in full** (winners AND losers), reconstructed from the ledger:
  archive = `ARCHIVE_INSERT` minus `ARCHIVE_EVICT` in the run's seq bracket; random
  population = that run's `ARTIFACT_EXECUTED` set.

## 5. "Useful" and how transfer is scored
A member m of source population P (trained on W_s) is evaluated ZERO-SHOT on target
world W_t via `/v0/evaluate` (no mutation). Its fitness is host-authoritative. m is
"useful on W_t" iff fitness(m, W_t) >= tau_t (§2). Cross-family pairs only (W_s family
!= W_t family) — same-family transfer is too easy to be diagnostic.

## 6. Controls (both mandatory; the experiment is inadmissible without them)

**6a. Dead-world.** Run both drivers on DEAD-RANDOM. Expected: near-zero transfer_yield
for BOTH, and Apollo must EMIT a "no reachable progress" verdict rather than report
MAP-Elites' diversity as interesting. If MAP-Elites' archive coverage on the dead world
is read as value, that is the old Apollo failure mode and S1 has caught the new Apollo
committing it.

**6b. Subsample-match (the nasty control).** Subsample the random population down to the
MAP-Elites archive's size AND matched on the behaviour descriptor distribution, then
recompute transfer_yield. **If MAP-Elites' enrichment disappears under size+diversity
matching, its apparent value was bookkeeping, not search** — and the primary result is
withdrawn. This control is applied to the primary endpoint before any positive verdict.

## 7. Pre-committed kill / continue threshold (frozen before results)

Apollo earns continued substrate-miner search compute ONLY IF, across at least TWO world
families and surviving control 6b:

    ENRICHMENT (primary, §2) >= 2.0    [MAP-Elites yields >=2x useful transfers vs random]
      OR
    a substantial (>=2x) and reproducible enrichment in informative BOUNDARY PAIRS (§3)
      that survives the duplicate-rate guard.

A 5-20% edge does NOT qualify: search is more expensive and more complex than random
generation, so it must clear a LARGE-effect bar to justify itself. 2.0 is not fetishised
— a clearly large, reproducible effect of similar magnitude qualifies — but a small or
control-fragile effect is a **FAIL**.

**On FAIL:** recommend stopping scheduled evolutionary mining; keep only the Foundry
adapter / replay / fossil infrastructure. "A good instrument and no Apollo research
program" is an accepted, pre-authorised outcome.

**On PASS:** S1 justifies a second, larger campaign and the first cron search jobs — not
a broad revival.

## 8. Compute discipline (binding)

`/v0/search` is synchronous and costs ~60-75s per 300-eval burst on a shared host. Until
S1 returns, **cron does NOT spray search** — it may scout/queue/replay/analyse only.
Scored campaign scale: 9 live worlds + 1 dead x 2 drivers x 3 seeds = 60 bursts (~1h of
search) + bounded cross-family transfer evaluation. Per-burst checkpointing so a release
boundary or interruption pauses, never corrupts, the campaign.

## 9. What S1 cannot do
S1 tests QD-vs-random usefulness on integer-induction worlds under one engine. It does
NOT bear on the Gen-1 null, does not claim capability widening, and a PASS establishes
only that MAP-Elites mines more reusable structure than random HERE — provisional until
replicated on F4 and, later, a second engine.

---
**FROZEN.** Analysis script (`s1_analyze.py`) and endpoint definitions are committed
alongside this file BEFORE the campaign result exists. Any change after the first scored
number is an amendment, dated and justified, never a silent edit.
