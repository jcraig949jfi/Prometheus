# PREREGISTRATION — SELECTOR: does ΔE deserve promotion from microscope to compass?

**Written 2026-08-25 before any code exists.** Ladder step 6 — **the arc is judged here**, not on
whether `vacuous_truth` moves five tasks. Doctrine §6 and §9.

**This preregistration is itself submitted to `aporia/iq/battery.py` and must adjudicate
ADMISSIBLE before the experiment runs.** That is the gate's first prospective test.

---

## 1. The question

> Does this representation merely describe what already worked, or does it tell the system what
> capability to acquire next?

`E` as a **microscope** is established: it diagnoses expressivity, and IQ-NULL showed it measures
expressivity rather than search dynamics. `E` as a **compass** — a selector that ranks which
abstraction to acquire — is unestablished and is what this rung tests.

## 2. Design, per doctrine §6

**Freeze the candidate pool first**, so every selector receives an identical pool. Candidates are
adaptations of the 25 `forge_primitives` functions plus the two port ops, fixed by hash before
any score is computed.

Five selectors, at **identical insertion count** and **identical downstream compute**:

    S_C        rank by compression
    S_R        rank by reachability (ΔE)
    S_C+R      combined
    S_random   control
    S_oracle   hindsight on held-out benefit — not deployable, establishes headroom

**Dependent variable: marginal held-out reachability PER LIBRARY SLOT and PER UNIT DOWNSTREAM
COMPUTE.** Not final solve rate — otherwise `S_R` wins by selecting large expensive primitives,
which is a measurement artifact rather than a capability.

Quadrants, and the one that must not be over-read: high-C/high-R ideal reusable abstraction ·
high-C/low-R compression decoy · low-C/low-R junk · **low-C/high-R = "reachability-only
candidate", NOT gold until confirmed on held-out transfer.**

## 3. MANDATORY PRE-FLIGHT — and I expect it may kill the rung

The design above assumes the DV can vary. **On this substrate that is doubtful, and the check
must run before the comparison, not after.**

Lexis measured `ΔS = 0.00%`: all 20 unreached tasks lie outside the operator closure, so no
macro, guard or search over existing operators reaches any of them. If most frozen candidates
therefore score `ΔE = 0`, every selector is ranking a near-constant vector and **no selector can
beat another for reasons that have anything to do with selection.**

    PF1  compute ΔE for every candidate in the frozen pool.
    PF2  compute the attainable range and variance of the DV.
    PF3  GATE: if fewer than THREE candidates have ΔE > 0, the selector comparison is
         **VACUOUS** and is reported as VACUOUS — never as "no selector beat random".

**This is the P138 check applied before the expensive step rather than after it.** A null from a
comparison whose DV cannot vary is a non-measurement wearing a result's clothes, and this arc has
produced that exact artifact three times.

**Failing input for PF3:** three or more candidates with distinct positive ΔE. Then the DV varies
and the comparison is meaningful.

## 4. Predicted readings

    P1  PF3 FAILS — fewer than three candidates move ΔE at all, because the forge library was
        already shown to intersect Apollo v1 25-of-25 and the unreached categories need
        vocabulary that library does not contain.
        **I expect the rung to terminate VACUOUS at pre-flight**, and I am stating that in
        advance so a vacuous outcome cannot later be presented as a kill of ΔE-as-selector.
    P2  IF PF3 passes: S_R beats S_random on marginal held-out reachability per slot.
        FAILS IF it does not — and that failure is the preregistered KILL below.
    P3  S_oracle exceeds every deployable selector, establishing non-zero headroom. If it does
        not, the DV is saturated and the comparison is uninformative regardless of PF3.

## 5. The preregistered KILL, stated before any number exists

> **If R-ranking cannot beat compression or random under frozen candidates and equal resources,
> the claim that ΔE deserves promotion to abstraction SELECTOR is KILLED.**
>
> **This does NOT kill the expressivity assay as a diagnostic instrument.** That distinction is
> the difference between *E is a microscope* and *E is a compass*, and it is the whole point of
> the rung.

A VACUOUS pre-flight is **not** a kill and may not be reported as one. It is a statement about
the substrate's headroom, not about ΔE's ranking power.

## 6. Terminal states — partition over PF3 × P2

    VACUOUS   PF3 fails. The DV cannot vary; report the ΔE distribution and stop. Neither a
              kill nor a confirmation.
    KILL      PF3 passes, P2 fails. ΔE does not deserve selector promotion; the assay survives
              as a diagnostic.
    ADVANCE   PF3 passes, P2 holds. ΔE ranks better than random under frozen candidates and
              equal resources — the first evidence for compass, still short of transfer.

## 7. Scope

- `C` untouched, `apollo/src/` untouched, 120-task battery unmodified.
- Any mutant-style reading uses the **abstain pool** from `run_ceiling_abstain.py`, because the
  1/k guessing floor corrupts mutation readings even though it is inert for capability.
- Single seed; no intervals quoted.
- This rung ranks candidates for a **frozen** pool on **this** battery. It says nothing about
  selection over an open-ended candidate space.

## 8. Cost-to-falsify

Rows PF3, P1, P2, P3 written to `aporia/iq/COST_TO_FALSIFY.jsonl` with `outcome: null` before
any code. Cumulative: 27/31.
