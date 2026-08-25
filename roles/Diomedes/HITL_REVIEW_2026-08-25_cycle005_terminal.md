# Diomedes — external review packet: coordinate adequacy, cycles 001–005

**Filed:** 2026-08-25, at thread close. **Charter:** `LOOP_CHARTER.md` §16.
**Written for a reviewer with zero repository access and zero prior context.** Everything needed to
find the mistake is in this document. The text block handed to reviewers is §1–§12 verbatim.

**Purpose:** this thread has closed itself with disposition PARK. The review is not asked to confirm
that. It is asked to find what is wrong with it.

---

## 1. What Prometheus is, minimally

A research substrate that generates and tests conjectured relations between mathematical objects
drawn from catalogs — knots (invariants: crossing number, determinant, signature) and elliptic
curves (invariants: rank, conductor, Tamagawa product). A generator proposes a relation between an
invariant of object A and an invariant of object B; the relation is checked exactly by integer
arithmetic; the result is logged. The corpus holds ~10^8 such records.

**The seat writing this** is responsible for one question only: *does Prometheus represent
mathematical search in coordinates that preserve information useful for deciding what transformation
to try next?* Not "is the mathematics correct" — "is the recorded representation adequate to choose
an action."

## 2. The precise question

Formally, whether the recorded representation carries `I(A*; Z_a | Z_x)` — information about which
**action** is useful, **conditional on the current state**.

Operationalised as a ranking task, exactly:

- **State `x`** = (a parent object, a tested invariant, a relation).
- **Candidate actions `a`** = up to 100 candidate objects that could be substituted.
- **Oracle label** = does substituting this candidate **break** the relation? Computed exactly by
  integer arithmetic, not modelled.
- **Metric** = per-state tie-averaged rank AUC over the candidate set, averaged over states.
- **Relations** = exactly two: `abs_diff_le_3` (|v_a − v_b| ≤ 3) and `equal_mod_2` ((v_a − v_b) even).
  These two were frozen because their predicates reproduced the corpus's own `holds` labels at
  1.0000 in pre-flight.

**Admissibility rule enforced in code:** no ranking arm except the oracle may read the candidate's
**tested** invariant value. Features are built from *companion* invariants — a different axis.

## 3. The decomposition (cycles 001–003)

Positive control (oracle) 1.0000. Cheat control (labels shuffled within state) 0.4993–0.5005.
Population digest `1b4abb1a…`, 5 seeds.

- chance — **0.5000**
- Prometheus's own recorded coordinates — **0.5560**
- best state-**ignoring** ranking (best fixed ordering of candidates, no state information) — **0.6254**
- cheap arithmetic features `Z(x,a)` fit per cell — **0.6600**
- same, at finer conditioning — **0.7101**
- state-specific oracle — **1.0000**
- parent-only representation `f(Z(x))` — **exactly 0.5000**

**Phrasing used deliberately:** *roughly three quarters of the observed improvement from chance to
the perfect state-specific oracle is unavailable to the best state-independent ranking.* These are
**ranking accuracies, not information estimates.** An earlier phrasing ("75% of the information") was
wrong and was retracted.

**The 0.5000 is a type fact, not a statistical one:** a representation invariant across candidates
cannot rank those candidates. It comes out exactly, not approximately.

## 4. The transfer failure (cycle 004)

A **cell** = (invariant pair, relation). 12 invariant pairs carrying both relations ⇒ 24 cells.
Train on one cell, evaluate on another:

- **A** same pair, same relation (local relearning) — **0.7101**
- **B** same pair, different relation — **0.4885**
- **C** different pair, same relation — **0.5349**
- **D** different pair, different relation — **0.4898**

Fitted coefficients were near-orthogonal across cells: cosine **−0.0312** within pair across
relations, **+0.0647** within relation across pairs. Object-level break-rate controls sat at
0.5574–0.5653 in every cell, i.e. the local signal is not object memorisation.

**Transfer failed on both available axes.** That is the negative result the rest of the thread tried
to explain.

## 5. The two questions cycle 005 was built to answer

- **Q1 — oracle form.** The oracle in §2 is cheap arithmetic over catalog values. Is the
  decomposition an artifact of that, i.e. would arithmetic features recover it under an oracle whose
  answer is not transparently encoded in them?
- **Q2 — chart mismatch vs intrinsic locality.** Does the §4 anti-transfer survive a serious attempt
  at **mathematically natural coordinate transport**? If a low-complexity map restores the ordering,
  "navigation knowledge is local" was premature.

**Both were pre-registered and committed before measurement**, including the decision thresholds and
the interpretation of every branch.

## 6. Q1 — answered "unresolvable in this corpus", by measurement

Arm A used operator commutation (`f(g(v)) == g(f(v))` over 6 recovered integer operators × 101
values), fully enumerated — 3,276 of 3,636 cells; the 360 absent all involve one operator whose table
range does not overlap the others, and were deliberately **not** filled rather than extrapolated.

- marginal ceiling (rank ignoring everything) 0.7892
- **f-conditional ceiling** (knowing which operators, not the value `v`) — **0.9735**
- oracle 1.0000 ⇒ **conditional headroom 0.0265**

Against h1's headroom of 0.3746, that is **fourteen times smaller**. Commutation is ~97% determined
by *which operators are involved*, regardless of `v`. **The arm was underpowered by landscape, not by
sample size** — no amount of data would help. Disposition PARK, Q1 unresolved.

A census then enumerated the remaining candidate populations exactly, rather than asserting them:

- b3 self-inverse `f(f(v))==v` — ceiling 0.9988, **headroom 0.0012**
- b4 fixed point `f(v)==v` — ceiling 0.9989, **headroom 0.0011**
- b5 — 2 candidate actions total, 1.4% negative class · c4 — 18,976/18,976 single-class ·
  b1 — 1,340/1,340 single-class · c5 — single-class on its primary outcome and the same arithmetic
  oracle family as h1 · g5 — absent, n = 0

Enumerations were checked against the corpus's own logged labels: b3 matches exactly (260/346);
b4 matches at exactly 2× (160/446 vs 320/892 — the corpus stores each cell twice).

**No population in this corpus carries both a non-arithmetic oracle and conditional headroom above
0.05.** Q1 is not answerable here.

## 7. Q2 — the transport experiment (the main new result)

**Design.** For every ordered pair of the 24 cells (552 per seed, 5 seeds, ~38,000 states/seed),
compare three things — the decisive comparison being 2 vs 3:

1. **raw transfer** — model from cell i applied to cell j
2. **coordinate transport** — `f_i(T(x,a))` for each `T` in a family **frozen before measurement**
3. **local relearning** — model fit on cell j from scratch

`recovery(T) = (transfer_T − transfer_raw) / (relearn − transfer_raw)`.

**The frozen family** (no member added, tuned, or removed after freezing): T0 identity · T1 sign flip ·
T2 threshold normalisation · T3 modulus alignment · T4 quantile standardisation · T5 = T2∘T4. Each
`T` is applied **two-sided** — to the source at fit time and the target at evaluation time, each
using its own side's parameters — and uses **no target labels**, so it is a transport and not
relearning.

**Results.** Local relearning **0.7392** · raw transfer **0.5068** · headroom **0.2325**.

- T0 identity — 0.5068 — recovery **0.0000**
- T1 sign flip — 0.4932 — recovery **−0.0582** (SE 0.0032)
- T2 threshold normalisation — 0.5115 — recovery **+0.0204** (SE 0.0011)
- T3 modulus alignment — 0.5068 — recovery **0.0000**
- T4 quantile standardisation — 0.5194 — recovery **+0.0543** (SE 0.0022)
- T5 = T2∘T4 — 0.5208 — recovery **+0.0603** (SE 0.0015)

Pre-registered gates: ≥50% ⇒ chart mismatch (locality withdrawn); 25–50% ⇒ mixed; <25% ⇒ locality
survives. **Best is 6.03%**, roughly 127 SE below the 25% line.

**The gate was shown reachable, not assumed.** Relearning measured *within* each chart: T4 **0.7265**
vs 0.7392 raw. The T4 chart costs only 0.0127 of local learnability, so a transport working as well
as local relearning would have scored **≈94.5% recovery**. The decision was eligible to go the other
way.

**Transport acted in the direction its own premise predicts.** By pair type, T4: **−0.068** on same-pair
(same invariants, so no scale mismatch to correct — rescaling only loses), **+0.083** on
different-pair/same-relation, **+0.045** on different-pair/different-relation. A structural pre-flight
had measured median feature-scale ratios across cells of up to **2587×**, which is exactly where T4
helped.

## 8. The limitation, declared before the numbers existed

The frozen relation set contains **exactly one threshold (3) and exactly one modulus (2)**. It follows
by inspection — and was written down and committed **before** measuring — that:

- **T3 is identically the identity map** (there is no second modulus to align to). Asserted in code
  and confirmed: T3 equalled T0 to the last digit on every pair and every seed.
- **T2 is the identity between two same-relation cells** and acts only across relations.
- **T1 is closed form**: `AUC → 1 − AUC`.
- **T0 is definitional.**

So the family reduced on this population to **one substantive transport (T4) plus one
relation-rescale (T2/T5)**. Consequently the locality claim is **not promoted** — a null about
quantile standardisation and threshold rescaling is not a null about coordinate transport in general.

## 9. Controls and integrity checks (all passed)

- Population digest `1b4abb1a…` verified before every run.
- **Builder differential:** the feature builder used here must reproduce the frozen one from earlier
  cycles. **60,640,200 feature values per seed** streamed into a SHA-256; identical on all 5 seeds.
- **Metric differential:** the vectorised AUC vs the original implementation — max absolute
  difference **exactly 0.0**.
- Perfect predictor **1.0** · constant predictor **0.5** · monotone-transform invariance **0.0** ·
  labels permuted within state → **0.5051**.
- Sign-flip identity and the linear-score/probability-score ranking identity — both **exactly 0.0**.
- Headroom floor rechecked per seed (lowest 0.2305).
- **20 hand-checkable rows** published at exact float64 precision, with a self-check that the
  arithmetic closes (it does, to relative 1.3e-16).

**Two defects of the runner, declared and repaired with identity proofs rather than assertions.**
(i) The first implementation exhausted 16.5 GB and was killed; the rewrite changed storage layout
only, and one seed's numbers from the first run were recorded beforehand and re-asserted against the
rewrite — worst drift 4.69e-05 against a 4-decimal rounding floor. (ii) The first hand-check emission
rounded to 6 dp and did **not** close on features of magnitude ~3200, so those rows were not in fact
hand-checkable; re-emitted at exact precision. The first repair used an *absolute* tolerance on a
score of magnitude 3200 — the wrong unit — and was corrected to a relative one.

## 10. Competing interpretations, stated without preference

**Interpretation 1 — conditional structure is real and the policy is local.** Within a cell there is
substantial state-conditional signal (0.7392 vs a 0.6254 state-independent ceiling); it does not
transfer, and two natural charts do not restore it.

**Interpretation 2 — there is no navigational content to transport, and the whole decomposition is
task construction.** The oracle asks whether |companion-derived quantity − target| falls in a band,
and the features include distances to the target computed on companion invariants. Within-cell
learnability may be a per-cell base rate plus a per-cell scale, and "anti-transfer" may be nothing
more than the fact that different invariant pairs have different units and different label
prevalences. On this reading Q2 was never a real question and 6% is exactly what one should expect.

**Interpretation 3 — the transport family was too weak to answer Q2, so Q2 is untouched.** T4 is a
*marginal, per-feature* monotone transform. If the mismatch lives in the joint distribution —
covariance structure, feature interactions — then a distribution-alignment map fitted on the target's
**unlabeled features** (covariance alignment, or an optimal-transport map) is still label-free and
arguably still "mathematically natural", and might recover far more. The pre-registration's
disqualifier was "a `T` that requires fitting to the target cell is not a transport", which is
ambiguous about unlabeled target features, and I did not resolve that ambiguity in advance.

**Interpretation 4 — the cell partition manufactures the failure.** 24 cells were treated as 24
separate prediction problems. A single model trained across all cells with cell-identity features was
never run. If that pooled model performs near 0.71, "locality" is an artifact of refusing to pool.

## 11. My own view, stated separately so it can be discounted

I think Interpretation 2 is the most dangerous and I have not fully excluded it. The object-level
break-rate controls (0.5574–0.5653 vs 0.7101 local) argue against pure base-rate explanation, and the
oracle uses the *tested* invariant while features use *companion* invariants, which argues against
direct encoding — but neither is decisive, and the by-pair-type sign pattern in §7 is equally
consistent with "T4 corrects a units difference that was the only thing separating the cells."

I think Interpretation 3 is the strongest **technical** objection and I would not defend against it.
The honest position is that Q2 was answered for two specific transports and left open in general.

**My prediction record on this thread is poor and is the reason for the pre-registration firewall.**
Cycle 002: wrong on 3 of 4 clauses. Cycle 003: right on direction, under-estimated the size. Cycle
004: wrong on the ordering. An earlier synthesis overreached on the "75%" phrasing. I recommended a
replication target that turned out to have no negative class at all. I wasted Arm A by not measuring
conditional headroom first. In Arm B I predicted the sign flip would be the largest single mover at
10.4% — it was the **worst** at −5.8%, because I quoted a ceiling computed on one subset as a property
of all 552 pairs. **Eight substantive predictions wrong or overstated; every one caught by a
pre-registration written before the measurement, or by external review.**

## 12. What I am asking for

Not encouragement. Specifically:

1. **What is the strongest objection to the §7 result** that is not already listed in §10?
2. **Is there a hidden confound** in the §2 task construction — particularly, can the label be
   partially reconstructed from the companion-invariant features by a route I have not noticed?
3. **Is there a simpler explanation** than any in §10 for: local 0.7392, raw transfer 0.5068,
   transport 0.5208?
4. **Does the inference actually follow?** Given the §8 degeneracy, is "Q2 answered for two
   transports, open in general" the right reading, or is the correct reading "Q2 was not tested"?
5. **Is Interpretation 3 fatal?** Would a label-free distribution-alignment map count as a transport
   under a fair reading of the pre-registration, and should the arm be re-run with one?
6. **What is the cheapest discriminating experiment** between Interpretations 1, 2 and 4? The pooled
   cross-cell model of Interpretation 4 looks cheap to me — is it decisive?
7. **Should this thread be killed rather than parked?** It has produced one type result, one
   instrument finding, one measured impossibility, and a large negative space. It has **not** shown
   that mathematical search contains transferable navigational structure.
8. **Is the proposed successor the right one?** The plan is to abandon this corpus and test the same
   question in a Lean tactic-selection environment: a closed action vocabulary (`intro`, `apply L`,
   `rw L`, `simp`, `constructor`), real proof states, exact execution, exact successor states, exact
   terminal verification, finite candidate sets, exhaustive evaluation at sampled states, and no
   language model anywhere in the measurement. Is that a real test of decision-sufficiency, or does
   it inherit the same defect in new clothes?

**Do not assume Diomedes's interpretation is correct. The purpose of this review is to find the
mistake.**

---

## 13. Disposition and what happens next (not part of the reviewer block)

**Cycle 005: PARK. Thread: CLOSED** by terminal synthesis, not by a terminal cycle — the cycle was
terminal only if *both* questions resolved, and Q1 did not.

**Surviving claims.** (1) State-only residue is action-insufficient by construction, measured exactly
0.5000 — **narrowed**: it does *not* establish decision-sufficiency relative to a horizon and
objective, which this thread named and never tested. (2) Production omitted the transition semantics
required to test its own thesis — one degenerate step-trace table, one empty symbol table, ~48.4M
parent-linked records never assembled. Once assembled those are a **transition corpus**, never a
"navigation corpus": edges alone do not give direction, which exists only relative to a terminal
objective and horizon.

**Not promoted.** Locality remains PROVISIONAL, per §8.

**Handoffs, not executed here.** The `EDGE(x_before, a, x_after, observations, provenance, context)`
primitive with two interface-enforced invariants — no generator may write into the epistemic outcome
namespace, and observations are not collapsed to a success bit at write time — touches another seat's
subsystem and is filed as a specification, not built. The Lean successor is a new thread, not a sixth
cycle.

*— Diomedes, external review packet, 2026-08-25.*
