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

---

## 9. ADDENDUM — does the unreachable class dissolve with scale? Measured to depth 10.

**Operator intuition, 2026-08-31:** *"a 5 node graph, navigating a solution is impossible but a
1000 node graph has many solutions"* — unreachability as an artifact of a small explored
structure, evaporating as the structure grows.

**Competing hypothesis:** `C \ {p}` generates a PROPER SUBALGEBRA. Then no depth recovers the
missing behaviours and the recovery curve hits a floor rather than going to zero.

These differ at the limit, so the limit was pushed. p05 removed, class labelled at depth 5
(2,136 targets), enumerating the same impoverished set deeper:

    depth   candidates    V-sigs    recovered   cum %   new
      6         20,295     5,002           39    1.8%    39
      7         83,549    17,768           71    3.3%    32
      8        333,667    61,230          140    6.6%    69
      9      1,296,241   204,506          199    9.3%    59
     10      4,911,333   663,527          223   10.4%    24

**Still unreachable after depth 10: 1,913 = 89.6%.**

The decisive statistic is marginal yield, not cumulative recovery:

    depth   new   marginal candidates   recoveries per million
      6      39                20,295                  1,921.7
      7      32                63,254                    505.9
      8      69               250,118                    275.9
      9      59               962,574                     61.3
     10      24             3,615,092                      6.6

**The reachable graph grew 133x and the search grew 242x, while marginal yield collapsed 291x.**
New recoveries peaked at depth 8 and are falling while each level costs about 4x more. That is
the signature of a floor, not of a threshold being approached.

### The intuition is right about the mechanism and wrong at the limit

**Right:** 10.4% of the class *was* a small-structure artifact — those depth-5 labels were simply
wrong, which is exactly the failure mode the analogy names. It is real and now quantified.

**Wrong at the limit:** 89.6% did not move, and marginal return is collapsing toward zero. The
residue behaves like a genuine representation boundary that no search budget crosses.

### Why the two look identical at small scale and diverge at large scale

Different mathematical objects wearing the same clothes.

- **Random-graph connectivity** is a *probabilistic* threshold. Adding nodes adds edges by
  chance, a giant component almost surely appears, and as n grows the probability of a path goes
  to one. **Size fixes it.**
- **A generated subalgebra** is *closed under its generators*. `G(C \ {p})` contains exactly what
  the nine primitives generate and never anything else, at any depth. **Size does not fix it —
  only a new generator does.**

At small scale both produce "no path found", which is why the analogy feels tight. They separate
only when the budget is pushed and marginal yield is watched: percolation accelerates toward
connection, a subalgebra decelerates toward a floor. This decelerated.

This is the operational content of Amendment 1. The 89.6% residue is exactly the population on
which `G(C ∪ {M}) = G(C)` bites — no macro built from the nine can reach it, because a macro is
already an element of the closure that excludes it. Only a **Level 2** primitive can.

### What this changes above

- §4's trichotomy stands, measured to depth 10: **search failure / depth failure (10.4%) /
  representation failure (89.6%)**.
- §5's label-noise screen tightens rather than loosens. Ground-truth instability is **10.4% at
  depth 10**, so Q045's ≥90% PASS threshold now sits *below* the label noise floor rather than
  3.4 points above it. **As written, T1 cannot be passed by any diagnostic on this population.**
- The §5 fix is unchanged but now mandatory: restrict scoring to the stable residue, or score
  the trichotomy.
- Reproducible at `aporia/q100/probes/q45_asymptote.py`.

### Honest limits

One removed primitive, one world, one probe set. A proper-subalgebra claim would be *proved* by
exhibiting an invariant preserved by all nine primitives and violated by p05; no such invariant
has been constructed, so the algebraic reading is **supported by a collapsing marginal-yield
curve, not established** — the floor could still be a very slow decay. The cheap next check is
the same sweep on a second removed primitive: if the yield collapse replicates across primitives
with different loss fractions, the subalgebra reading strengthens considerably.

---

## 10. ADDENDUM 2 — where the world actually varies, and the certificate that falls out

**Operator, 2026-08-31:** *"the world can vary vastly despite being made of similar parts."*

Correct — and the measurement localises *where*. It is not where I expected.

### 10.1 Varying the ring and the width barely moves anything

Same ten primitive KINDS throughout; only the ring and vector width change. Label at depth 5
with elementwise-multiply removed, verify at depth 8.

    world     field?   full V    lost   lost%   recovered@8   FLOOR
    Z5^4        yes     4,438   3,018   68.0%          3.7%   96.3%
    Z6^4         no     3,502   2,136   61.0%          6.6%   93.4%
    Z7^4        yes     4,847   3,206   66.1%          4.5%   95.5%
    Z8^4         no     3,712   2,407   64.8%          4.2%   95.8%
    Z9^4         no     4,850   3,109   64.1%          2.4%   97.6%
    Z6^3         no     3,183   1,965   61.7%          3.9%   96.1%
    Z6^5         no     3,637   2,295   63.1%          1.8%   98.2%
    Z7^3        yes     4,627   3,076   66.5%          4.5%   95.5%

    FLOOR spread 4.8pp (93.4-98.2).   mean prime 95.8% vs composite 96.2%.

**A prediction of mine failed here and is recorded as such.** I expected the field/ring
distinction to be the sharp lever — Z5 and Z7 have every nonzero element invertible, Z6/Z8/Z9
have zero divisors, a categorical algebraic difference from a one-character change. It made
**0.4 percentage points** of difference, inside the spread. The floor is invariant to the
arithmetic.

**And this strengthens §9 rather than weakening it:** the 89.6% floor was not a Z6 artifact. It
replicates at 93-98% across eight worlds.

### 10.2 Varying the operator inventory moves everything

Z6^4 throughout; remove each primitive in turn.

    removed   kind               lost   lost%   recovered@8   FLOOR
    p00       rotate            2,013   57.5%          0.8%   99.2%
    p05       vec multiply      2,136   61.0%          6.6%   93.4%
    p01       reverse           1,565   44.7%          6.8%   93.2%
    p06       sum->scalar       1,054   30.1%         17.7%   82.3%
    p02       increment         1,498   42.8%         26.2%   73.8%
    p04       vec add           1,450   41.4%         29.0%   71.0%
    p07       product->scalar     669   19.1%         40.7%   59.3%
    p08       scalar add          982   28.0%         69.7%   30.3%
    p09       scalar multiply     656   18.7%         72.6%   27.4%
    p03       double              615   17.6%         95.8%    4.2%

    FLOOR spread 94.9pp (4.2-99.2), against 4.8pp for ring and width.

**Twenty times the variation, from the same-sized parameter change.** The operator inventory is
the world; the arithmetic is decoration.

### 10.3 The variation is signal, not noise — and it is the missing certificate

The floor is not scattered. It tracks whether the removed primitive was **definable from the
rest**:

- **`double` reads 4.2%.** `dbl(v) = 2v` and `vadd(v,v) = v+v = 2v` — identical by inspection of
  `world3.py`. It is a composition wearing a primitive's name, and the instrument says so.
- **`rotate` reads 99.2%.** Every other primitive is coordinate-wise or global; only `reverse`
  also moves data between positions, and reverse alone generates an involution, not the cyclic
  group. Rotation is structurally irreplaceable, and the instrument says that too.

**So the leave-one-out floor is an operational non-redundancy certificate:**

    floor ~ 0   the primitive is reproducible from the others   -> Level 0, a named composition
    floor ~ 1   the primitive is a genuine generator            -> irreplaceable at any depth

**This is the test Q060's T2 demands and that the entire library-learning literature has never
executed** (`Q047_Q060_Q100_operator_invention.md`: novelty is asserted or replaced by a
compression proxy in DreamCoder, Stitch, babble, LILO and ShapeCoder). It now arrives with a
**positive control** — `double`, known-definable, reads 4.2% — and a **negative control** —
`rotate`, structurally unique, reads 99.2%. Both recovered facts we already knew, which is what
licenses using it on facts we do not.

### 10.4 The limit, stated precisely

`double` reads 4.2% rather than 0% because the enumerator counts **tree size**: `dbl(f(x))` costs
`size(f)+1` while `vadd(f(x),f(x))` costs `2·size(f)+1`, since a shared subterm is paid for
twice. So the floor conflates *"not definable"* with *"definable only at much greater tree
cost."* It is a **cost-sensitive** non-redundancy measure, not a pure definability measure. For
`rotate` this does not matter — no definition exists at any cost. For borderline primitives it
does, and any use of this certificate must report the size convention alongside the number.

### 10.5 What this settles for the operator's claim

**Worlds made of similar parts do vary vastly — but along the operator axis, not the arithmetic
axis, and by a factor of twenty.** Two consequences:

1. **Q045's experiment is portable across rings and widths** (floor stable to 4.8pp) and
   **must be stratified by removed primitive** (floor varies 94.9pp). Sampling one removal and
   generalising would be exactly the prefix-sampling error this programme has committed before.
2. **The ground-truth label noise is primitive-specific.** §9 quoted 10.4% from `p05`. For `p03`
   it is **95.8%** — labels there are almost entirely wrong. Any Q045 task population built by
   removing a low-floor primitive is measuring depth, not representation, and would produce a
   diagnostic that appears to work while classifying nothing.

Reproducible at `aporia/q100/probes/q45_world_variation.py` and `q45_per_primitive_floor.py`.
