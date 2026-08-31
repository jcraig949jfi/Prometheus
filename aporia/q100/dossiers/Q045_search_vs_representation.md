# Dossier — Q045: distinguishing search failure from representation failure

**Pass 2 of the Q100 loop.** 2026-08-31, Aporia. Measured, not surveyed.

**The question (L1-045, verbatim):** *Can an artificial system distinguish a failure caused by
insufficient search from one caused by an inadequate representation?*

    T1  matched search-limited vs primitive-missing problems;  PASS >= 90% diagnosis
    T2  allow compute increase or primitive addition;          PASS within 1.2x oracle cost
    T3  scale both difficulty axes independently;              PASS diagnosis stays calibrated

---

## 1. TRIAGE — why this one is worth the microscope

Three independent routes converged on Q045 this week, and only one of them is corpus gravity:

- I triaged it Tier B from the substrate side, noting D-4's viable-only oracle as a candidate
  instrument, **before** any synthesis was supplied.
- ChatGPT's synthesis of L1 called it *"secretly one of the most important questions in the
  set"* and placed it on the `∃g ∈ G(A): g(x)=y` boundary.
- It is the operational form of Amendment 1's three levels: Level 0/1 fix search cost, only
  Level 2 fixes reachability. **Which failure you have determines which level you need.**

It also passes the loop's reachability precondition cleanly: all three tests have real bands, and
the conjunction screen finds nothing (T2 is a disjunction — compute *or* primitive).

## 2. WHAT WE ALREADY HAVE, AND ITS LIMIT

D-4's per-episode viable-only oracle separates the two on real substrates:

    substrate    achieved far   oracle far-reach   attribution
    S1_REG       0.00-0.02      0.41               SEARCH weakness at this budget
    S2_STACK     0.15           0.50               substantial navigation regret
    S4_MEM       0.53           0.73               moderate regret
    S3_REWRITE   0.00           0.00               TOPOLOGY failure, not search

**Two limits.** It attributes per *substrate*, not per *problem*, so it cannot supply the
matched-pair labels T1 needs. And it is a **lower bound** — it traverses only edges actually
observed during the run, so "oracle says 0.00" means "no observed path", not "no path".

## 3. THE EXACT INSTRUMENT — leave-one-out over the TINYPROG closure

`build_closure()` returns `minsize[(type, signature)]`: the minimal program size for every
extensionally distinct behaviour reachable within a depth bound, by bottom-up enumeration with
deduplication. That converts the oracle from an estimate into a **certificate**.

Ground truth by construction:

    build closure of full C at depth K            -> reachable_full
    build closure of C \ {p} at depth K           -> reachable_ablated
    targets in reachable_full but NOT ablated     -> REPRESENTATION failure, certified
    targets in ablated but missed by navigator    -> SEARCH failure, certified

This is IQ-PORT-1's leave-one-out knockout pointed at a new question.

**Viability, measured (depth 5, 3,502 type-V signatures):** every one of the ten primitives
creates a usable representation-failure class when removed.

    removed   V-sigs remaining   lost   lost %
    p05             1,366        2,136   61.0%
    p00             1,489        2,013   57.5%
    p01             1,937        1,565   44.7%
    p02             2,004        1,498   42.8%
    p04             2,052        1,450   41.4%
    p06             2,448        1,054   30.1%
    p08             2,520          982   28.0%
    p07             2,833          669   19.1%
    p09             2,846          656   18.7%
    p03             2,887          615   17.6%

A testbed exists, it is large, and it comes with exact labels. **That is more than Q045 has had
anywhere.**

## 4. THE MICROSCOPE FINDING — the label is budget-relative, and it leaks

"Not reachable within depth K" is not "not reachable". A deeper composition of the *impoverished*
set may reach the same extensional behaviour — in which case the label was never about
representation at all. It was about depth, which is search.

Measured directly. Label at depth 5 with `p05` removed (2,136 targets), then enumerate the same
impoverished set deeper:

    enumerate C\{p05} to    candidates   recovered   contamination   still unreachable
    depth 6                     20,295          39            1.8%              98.2%
    depth 7                     83,549          71            3.3%              96.7%
    depth 8                    333,667         140            6.6%              93.4%

**The distinction is real: 93.4% of the class survives a 26x increase in enumeration.** But the
label leaks, and **the leak roughly doubles per level** (1.8 → 3.3 → 6.6). Extrapolated, a
depth-5 label carries perhaps 25% contamination when checked against depth 11.

**So the search/representation distinction is not a property of the target. It is a property of
the (target, budget) pair, and the honest object is a trichotomy, not a dichotomy:**

    (a) reachable by the impoverished set within the navigator's budget   -> SEARCH failure
    (b) reachable by it only at greater depth                             -> DEPTH failure  (6.6%)
    (c) not reachable by it at any enumerated depth                       -> REPRESENTATION (93.4%)

Case (b) is where every confusion in this question lives, and it is the case Amendment 1 speaks
to: a macro over existing primitives **helps case (b) and cannot touch case (c)**, because
`G(C ∪ {M}) = G(C)`. Only a Level 2 extension moves case (c).

## 5. THE DEFECT IN Q045's OWN TEST — a new screen

T1 demands **≥90% diagnosis accuracy**. The measured ground-truth label instability is **6.6%** at
the depths tested.

**The PASS threshold sits 3.4 points above the noise floor of the labels it is scored against.**

That is `feedback_gate_must_exceed_measurement_error` in a form the loop has not screened for:
not threshold-versus-statistic-range (the reachability screen), and not threshold-versus-
conjunction (the L4 screen), but **threshold versus the error rate of the ground truth itself.**
A diagnostic scoring 91% against labels that are 6.6% wrong has not been shown to beat the
labelling procedure.

**Third screen, added to the loop:** for any test scored against constructed ground truth,
measure the ground truth's own instability first, and require the PASS threshold to clear chance
by at least 2x that instability.

**Fix for Q045 specifically:** label at depth K, verify at depth K+3, report the contamination
rate beside every classification, and either restrict the task population to case (c) targets
that survive the deeper check, or score the diagnostic on the trichotomy rather than the
dichotomy.

## 6. PREREQUISITES

**Satisfied.** The world (TINYPROG, WORLD_ADMISSIBLE on five unused seeds). The certificate
(`build_closure`, exact minimal size per behaviour). The ablation harness (leave-one-out,
precedent in IQ-PORT-1's 17-op knockout). Cost separation (`C_execution = 6.0 × C_search` on
record). A measured testbed with ten choices of removed primitive.

**Not satisfied.** (i) No diagnostic procedure exists yet — the instrument that produces ground
truth is not the thing under test; the thing under test is a procedure that sees only the
navigator's trace. (ii) T2's "primitive addition" arm requires a **Level 2** primitive to be
meaningful, and no Level 2 mechanism exists here or in the surveyed literature. (iii) T3's
"scale both axes" needs the contamination curve extended past depth 8 to know how far the labels
hold.

## 7. LANGUAGE-FREE FORMULATION — class NATIVE

Nothing in this needs language. Targets are extensional signatures over a fixed probe set;
primitives are anonymous and position-indexed; the diagnosis is a function of search traces and
behavioural fingerprints. The scoring criterion — the place where language normally re-enters —
is enumeration membership, which is a fact about a closure and not a judgement.

**The one human choice left, stated:** the primitive set and the probe inputs. Both are designed.
Q045's answer is therefore relative to a designed algebra, exactly as BIGANN's label-free result
remained relative to a chosen metric and corpus.

## 8. VERDICT

**ANSWERABLE, and closer to answerable here than anywhere in the surveyed literature** — but not
as written. The dichotomy in the question is a trichotomy in the measurement, and the T1
threshold is inside the ground-truth noise. Repair the test as in §5 and the experiment is
runnable on machinery that already exists and costs seconds per closure.

**Recommended next action:** preregister Q045-A — build the trichotomy labels at depth 5 verified
to depth 8, restrict to the 93.4% stable class, and ask whether a trace-only diagnostic beats the
base rate. This is a smaller and better-posed rung than A3, and it feeds A3 directly, because A3
cannot interpret its own result without knowing which failure it is looking at.
