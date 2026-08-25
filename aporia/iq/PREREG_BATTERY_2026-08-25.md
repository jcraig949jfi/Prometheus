# PREREGISTRATION — BATTERY: the counterfeit taxonomy as machine-enforced gates

**Written 2026-08-25 before any code exists.** Ladder step 5. Doctrine §2 requires that *"a claim
whose class has an unrun mandatory falsifier is inadmissible"* — as **machine-enforced gates, not
a checklist.** This rung builds the machine.

---

## 1. Why BATTERY now rather than SELECTOR

SELECTOR is the arc's decisive experiment and it is not blocked by anything technical. BATTERY
goes first for one reason, stated so it can be judged: **SELECTOR is exactly the kind of
experiment this arc has repeatedly gotten wrong at the instrument level**, and it is expensive
enough that a silent instrument defect would cost the whole rung.

The evidence that the defects are systematic rather than incidental — all from this arc, all
mine:

    threshold below the attainable floor   TRANSFER-1: a <0.10 bar under a 1/k floor of 0.25,
                                           written one pass after logging P138 as a lesson
    vacuous reading                        THREE times: the check_transitivity footprint,
                                           the first scorer audit, and C2/C5 this rung
    probe perturbs what it measures        CEILING-ABSTAIN v1: removed the matched candidate,
                                           reported the proven ceiling collapsing by 24 tasks
    branch gloss falsified                 TRANSFER-1: the REDESIGN branch fired for a cause
                                           its own preregistration named wrongly
    mutation battery incomplete            IQ-PORT-1: four mutants, and the one that mattered
                                           (return-N) was not among them

Every one was caught, but each was caught **by me noticing**, which is exactly the mechanism
doctrine §2 says cannot be relied on for the next one. That is the case for mechanising now.

## 2. What the gate is

A deterministic function over a **recorded claim object** — never over prose, never over model
judgement:

    adjudicate(claim) -> ADMISSIBLE | INADMISSIBLE(reasons[])

`claim` carries: `intervention_class`, the falsifiers actually run with their outcomes, the
thresholds used, the attainable range of each statistic, and the readings. The gate returns
INADMISSIBLE with a machine-readable reason list. **No natural-language field is ever parsed for
meaning.**

### Gates, each with the input that trips it

    G-CLASS      class not in {PORT_EXISTING_CAPABILITY, SYNTH, DISCOVER, INSTRUMENT}
                 -> trips on an unlabelled or novel class
    G-MANDATORY  a falsifier mandatory for the claimed class is absent or unrun
                 -> trips on IQ-PORT-1 with its state injections removed
    G-FLOOR      a threshold placed below the statistic's attainable floor
                 -> trips on TRANSFER-1's <0.10 bar against a 1/k floor of 0.25
    G-VACUOUS    a predicate whose reading could not have come out otherwise
                 (attainable range degenerate, or n = 0 on the branch it reads)
                 -> trips on the check_transitivity footprint of 0 and on C2/C5
    G-INERT      a null result with no positive control establishing the instrument moves
                 -> trips on CEILING-ABSTAIN's zero-loss reading BEFORE its positive control
    G-PERTURB    a probe declared to modify the quantity it tests
                 -> trips on CEILING-ABSTAIN v1's removal discriminator
    G-BRANCH     branch table not asserted to partition its outcome space
                 -> trips on any rung without the enumeration assert

## 3. Predicted readings, each with its failing input

    B1  the six rungs of this arc, AS ACTUALLY RUN, are ADMISSIBLE.
        FAILS IF: any is inadmissible. That would mean either the gate is miscalibrated or a
        shipped rung has an unrun mandatory falsifier — and I would report which, not retune
        the gate to pass my own work.

    B2  the same six rungs, with one required falsifier REMOVED from each, are INADMISSIBLE.
        This is the negative control and it is what makes B1 non-vacuous.
        FAILS IF: any ablated claim still passes. The gate would be discriminating nothing.

    B3  the four historical defects listed in §1 are each caught by their named gate when
        replayed as claim objects.
        FAILS IF: a defect I know about slips through. The gate would be a checklist of things
        I already fixed rather than a detector.

    B4  the adjudication is a pure function: same claim object in, same verdict out, with no
        model call and no free-text parsing anywhere in the path.
        FAILS IF: any gate reads a prose field for meaning.

**Attainable range, computed before any threshold.** The gate is binary per claim over N claims,
so the reading lives in [0, N] admissible. **B1 and B2 together require BOTH endpoints to occur**
— all-admissible on the real claims and all-inadmissible on the ablated ones. A gate that returns
one value on every input is reported as VACUOUS, whichever value it is.

## 4. Terminal states — asserted to partition over B1 x B2

    ADVANCE   B1 and B2 both hold. The gate admits the arc's real work and rejects it when a
              mandatory falsifier is removed. It becomes a standing precondition on every
              future claim, including SELECTOR's.
    REDESIGN  B1 holds, B2 fails. The gate passes everything; it discriminates nothing and is
              a checklist wearing a gate's clothes.
    PARK      B1 fails. Either a shipped rung has an unrun mandatory falsifier, or the gate is
              miscalibrated. Report WHICH, and do not retune the gate to pass my own work
              without saying so.

## 5. The trap this rung must not fall into, named in advance

**I am writing the gate and choosing the claims it is tested on.** A gate authored against the
defects I already found, then validated on the rungs I already fixed, is a fit statistic and not
a capability estimate — the exact failure recorded in
`feedback_promotion_requires_independent_failure_mode`.

So: B3 is explicitly a **fit** check and is labelled as such in the result, never quoted as
evidence the gate catches unseen defects. **The only real test is prospective** — the gate binds
SELECTOR before SELECTOR runs, and its value is decided there, not here.

## 6. Scope

- Adjudication over recorded claim objects only. The gate does not read source, run experiments,
  or judge prose.
- `C` untouched; `apollo/src/` untouched; the 120-task battery unmodified.
- The claim objects for the six rungs are transcribed from their committed RESULT json files, so
  the inputs are the shipped evidence rather than a retelling.

## 7. Cost-to-falsify

Rows B1–B4 written to `aporia/iq/COST_TO_FALSIFY.jsonl` with `outcome: null` before any code.
Cumulative: 23/27.
