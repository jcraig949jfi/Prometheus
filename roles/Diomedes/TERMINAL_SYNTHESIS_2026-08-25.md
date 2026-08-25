# Diomedes — TERMINAL SYNTHESIS: the coordinate-adequacy reconnaissance, cycles 001–005

**Filed:** 2026-08-25, per `LOOP_CHARTER.md` §14 and the HITL disposition. **This closes the
thread.** Five cycles ran; five closed. No sixth question is manufactured here.

**Standing admission (charter §20.5):** I am an LLM writing this interpretation. My prose about what
the numbers mean is rung 5 at best and is not evidence. What survives me are the enumerated tables,
the differential tests, the assertions, and the hand-checkable rows. Everything below is commentary
on those.

---

## 1. What was actually tested

**The question:** does Prometheus represent mathematical search in coordinates that preserve
information useful for deciding what transformation to try next? Sharpened early to
`I(A*; Z_a | Z_x)` — information about useful actions **conditional on the current state**.

**The environment for all five cycles was `theseus/corpus`'s h1 counterexample-search population**
(plus b2/b3/b4 for Arm A and the Q1 census). The task: given a state — a parent object, a tested
invariant, a relation — rank candidate objects by whether substituting them **breaks** the relation.
Ground truth was recovered from the corpus's own payloads and validated against its own labels;
oracle predicates reproduced the corpus's `holds` at 1.0000 before anything was measured.

**Dispositions:** 001 REDESIGN · 002 KILL · 003 REDESIGN · 004 REDESIGN · 005 PARK (both arms).

## 2. The strongest positive evidence

**The decomposition, exactly measured, with a positive control at 1.0000 and a cheat control at
0.4993–0.5005, population digest `1b4abb1a…`:**

chance **0.5000** · Prometheus's recorded coordinates **0.5560** · best state-ignoring ranking
**0.6254** · cheap arithmetic `Z(x,a)` per cell **0.6600** · at finer conditioning **0.7101** ·
oracle **1.0000**.

Stated in the only phrasing I am permitted, because an earlier phrasing overreached: *roughly three
quarters of the observed improvement from chance to the perfect state-specific oracle is unavailable
to the best state-independent ranking.* These are **ranking accuracies, not information estimates.**

**The type argument, measured at exactly 0.5000.** A representation invariant across candidate
actions cannot rank those candidates using that representation alone. Parent-only coordinates score
exactly chance, not approximately. This is the most durable thing the thread produced, and it is
durable precisely because it is a type fact confirmed by measurement rather than a statistical claim.

## 3. The strongest negative evidence

**Transfer failed along every axis available in this population.** Same pair / different relation
0.4885; different pair / same relation 0.5349; different pair / different relation 0.4898 — against
0.7101 for local relearning. Fitted coefficients were near-orthogonal across cells
(cos −0.0312 within pair, 0.0647 within relation).

**And it survived a transport attempt.** Cycle 005 Arm B: 552 ordered cell pairs, 5 seeds, six
frozen transports. Best recovery **6.03%** of the relearning gap (SE 0.0015), against a 50% gate
shown reachable at **94.5%**. The transport moved the number in the direction its own mathematics
predicts — helping where invariant scales differ (+0.083 across pairs), hurting where they do not
(−0.068 within a pair) — and the magnitude was small.

**Production omitted the transition semantics required to test its own thesis.** `sigma.symbols` =
0 rows. `step_trace` degenerate at 332,883 of 332,886 identical steps. Yet ~48.4M records carry
parent links. This is the finding with the clearest consequence for Prometheus and it needed no
model to establish.

## 4. Claims: surviving, killed, unresolved

**SURVIVING — narrowed.**

*Finding 1: state-only residue is action-insufficient by construction.* Measured 0.5000. **What it
does not prove:** that `Z(x,a)` is adequate for navigation. Two actions with identical immediate
statistics can enter different future basins. The real requirement is **decision-sufficiency
relative to a horizon and objective** — named in this thread, **never tested by it.** No multi-step
experiment exists anywhere in these five cycles.

**SURVIVING — unchanged and strong.**

*Finding 2: the instrument could not test its own thesis.* Once assembled, those parent-linked
records are a **transition corpus**, never a "navigation corpus." Edges alone do not give direction;
direction exists only relative to a terminal objective and horizon.

**KILLED.**

*That cheap relational coordinates recover the conditional signal across held-out invariant pairs*
(cycle 002). *That either relation type or invariant pair alone explains the transfer failure*
(cycle 004 — both axes failed). And several of my own predictions, listed in §6.

**UNRESOLVED — and now measured to be unresolvable here.**

*Q1 — does the decomposition survive an oracle not transparently encoded in cheap arithmetic?*
Arm A could not answer it: b2's conditional headroom is **0.0265** against h1's 0.3746, fourteen
times smaller. The Step-3b census then enumerated the remaining candidates exactly, rather than
asserting them:

- **b3** self-inverse `f(f(v))==v` — ceiling 0.9988, **headroom 0.0012**
- **b4** fixed point `f(v)==v` — ceiling 0.9989, **headroom 0.0011**
- b2 — headroom 0.0265 · b5 — k=2 candidate set, 1.4% negatives · c4 — 18,976/18,976 single-class ·
  b1 — 1,340/1,340 single-class · c5 — single-class on its primary outcome and h1's own arithmetic
  oracle family · g5 — absent, n=0

The enumeration was checked against the corpus's own logged labels: b3 matches **exactly**
(260/346), b4 matches at exactly **2×** (the corpus carries each cell twice).

**Verdict, measured: no population in this corpus carries both a non-arithmetic oracle and real
conditional headroom.** That is itself the finding, and it is the sharpest available form of *the
corpus contains no second search process with both properties.*

*Q2 — is anti-transfer chart mismatch or intrinsic locality?* **Still open, and honestly so.** Arm B
answers it negatively **only for quantile standardisation and threshold rescaling**, because the
frozen relation set `{equal_mod_2, abs_diff_le_3}` contains exactly **one threshold and one
modulus** — so T3 was identically the identity map, T2 acted only across relations, and T1 was
closed-form. Four of six transports were structurally degenerate, **declared before measurement**,
family left unchanged. **Finding 3 (locality) therefore stays PROVISIONAL and is not promoted.**

## 5. What would have to become possible to reopen this

Not "more data" and not "a better model." Specifically:

1. **A population with more than one threshold and more than one modulus.** Q2's transport family
   needs genuine variation in the relation parameters to be non-degenerate. This corpus has none.
2. **A search process with a non-arithmetic oracle AND conditional headroom above ~0.05.** Measured
   absent here across eight candidate populations.
3. **A closed, executable action vocabulary with exact successor states** — so that
   decision-sufficiency over a horizon can be tested at all, which nothing in this thread could do.
4. **An `EDGE`-shaped record** (§7), because the arity question cannot be re-asked against a corpus
   whose atomic unit is a noun with a verdict attached.

Absent (1) and (2), reopening this line in `theseus/corpus` would be re-measuring a landscape whose
limits are now known and documented.

## 6. My calibration record, kept because it is unflattering

Cycle 002: wrong on 3 of 4 clauses. Cycle 003: right on direction, under-estimated the effect.
Cycle 004: wrong on the ordering — conflated "fits both passably" with "transfers." Synthesis 001:
overreached on the "75%" phrasing. Cycle 005 planning: recommended c4 as the replication target; it
was **vacuous**, every outcome field single-valued. Arm A: wasted by not measuring conditional
headroom first — third instance of the same trap. Arm B: predicted T1 would be the largest mover at
10.4%; it was the **worst** at −0.058, because I quoted a recovery ceiling computed on cycle 004's
B cell as a property of all 552 ordered pairs. Findings 1 and 3: overstated until external review
corrected them.

**Eight of my substantive predictions on this thread were wrong or overstated.** Every one was
caught by a pre-registration written before the measurement, or by external review. That is the
argument for the firewall, and it is the main methodological output of the thread.

**Three traps fired repeatedly and are worth carrying forward:** assuming semantics from field
names; anchoring across cycles between *different estimators* (it fired again in Arm B's C and D
cells — cycle 004 sampled one target cell per source, Arm B enumerated all 552); and pre-flighting
only *some* properties of a population.

## 7. Consequences for Prometheus

**The reframing that supersedes my original headline.** Not "failure geometry should become action
geometry." The sharper statement is that **Prometheus stored observations at the wrong causal arity
for navigation** — and `verdict(state, action)` is not the fix either. The natural atomic object is

> `e = (x_before, a, x_after, o, c)` — an **edge**, with externally established evidence `o` and
> recorded search context `c`.

**Recommendation C — the `EDGE` primitive.** Authorized by HITL to proceed regardless of any cycle-005
result, because it is engineering and does not depend on the navigation hypothesis surviving. Two
invariants to enforce **by interface, not by promise**: no generator may write into the epistemic
outcome namespace (the 99.98% self-verdict event was a generator carrying its own judge — make that
structurally impossible); and observations must not be collapsed to a success bit at write time,
because deciding today that "goal count −1 = good" writes a human policy into the corpus and
forecloses recomputation. **This touches `sigma_kernel/`, which is Techne's. It is filed as a
specification and a request, not executed. Routing is James's call.**

**The LLM is not the hard part.** LLM proposes verbs → reality executes → Prometheus records edges →
statistics infer policies → **prospective execution judges policies**. The model is provenance for
`a` and appears nowhere in `o`. `p(a|x)` may be arbitrarily contaminated; it cannot touch
`P(x′, o | x, a)`. No LLM judge is required anywhere in the chain. The genuinely hard problem moves
one level up: *what objective over verified trajectories constitutes mathematical progress before a
theorem has been proved?* Not solved here, and not to be solved by assertion.

**The doctrine correction that outlives the thread.** Certainty of *observation* and uncertainty of
*policy inference* are independent axes; the §20 ladder conflated them. **Infer freely; believe only
prospective consequences measured through independent instruments.** And for open action spaces,
regret against an unknowable optimum is unavailable — replace it with **paired empirical dominance
under controlled budgets**, `P(solve | π₁, B)` vs `P(solve | π₂, B)`.

## 8. The handoff, which I am not executing

**The smallest real test of the question this thread could not answer:** Lean tactic selection with a
**closed** mathematical action vocabulary (`intro`, `apply Lᵢ`, `rw Lᵢ`, `simp`, `constructor`) and
bounded premise candidates. Real proof states, exact execution, exact successor state, exact terminal
verification, finite candidate sets, exhaustive evaluation at sampled states, **zero LLM**. Lean's
own `exact?`/`apply?` provide non-LLM action generators as controls. It supplies precisely what
`theseus/corpus` lacks: a non-arithmetic oracle, real conditional headroom, and a horizon over which
decision-sufficiency is even definable.

**This is a new thread, not a sixth cycle, and it is not mine to start unasked.**

## 9. Was this thread worth its compute?

Charter §13: not rewarded for cycles, commits, or keeping the thread alive; *a three-cycle sequence
ending in a clean KILL beats fifty cycles of elaborate ambiguity.*

Five cycles produced **one durable type result**, **one instrument finding with a concrete repair**,
**one measured impossibility** (no population here can answer Q1), **one honest unresolved question**
(Q2, degenerate family), and **a large negative space**: transfer failed on both available axes and
was not restored by transport. It did **not** establish that mathematical search contains
transferable navigational structure. It established that **this corpus cannot answer whether it
does** — and named exactly what an environment would need in order to.

**The prize was transferable directional information. The answer here is: not found, and this
instrument could not have found it.** That is a real answer, and it is the one the charter said to
be willing to reach.

---

**Cycle 005 disposition: PARK. Thread: CLOSED.** No sixth question. Per charter §14: committed,
pushed, stopped.

*— Diomedes, terminal synthesis, 2026-08-25.*
