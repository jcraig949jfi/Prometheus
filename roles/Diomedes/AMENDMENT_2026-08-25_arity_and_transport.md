# Diomedes — Amendment, 2026-08-25: causal arity, decision-sufficiency, and the transport question

**Trigger:** HITL review of `STATUS_2026-08-25.md`. **Scope:** narrows two of three findings,
corrects the charter §20 ladder, and adds two mandatory controls to cycle 005. No measurement
changes. **All corrections adopted.**

---

## 1. The reframing that supersedes my headline

I framed the thread as *failure geometry should become action geometry*. The sharper statement:

> **Prometheus has been storing observations at the wrong causal arity for navigation.**

And crucially, **upgrading the schema to `verdict(state, action)` is not sufficient either.** The
natural atomic object is

> **`e_t = (x_t, a_t, x_{t+1}, o_t, c_t)`**

where `o_t` is externally established outcome/evidence and `c_t` records the **search context** —
resources, available actions, objective, verifier, parent trajectory. **That is an edge, not a richer
failure record.**

The productive question is therefore not *"what should a failure record contain?"* but *"what is the
minimal experimentally grounded transition record from which competing navigation hypotheses can
later be tested?"*

## 2. FINDING 1 — KEEP, but narrowed (my type argument was oversold)

**What it proves:** a representation invariant across candidate actions cannot rank those candidates
using that representation alone. Measured at exactly 0.5000. That stands.

**What it does NOT prove:** that `Z(x,a)` is the *minimum adequate object for navigation*. `Z(x,a)`
can rank immediate actions while remaining catastrophically inadequate for multi-step search —
**two actions with identical immediate statistics can lead into radically different future basins.**

**The corrected requirement:** not action-sufficiency but **decision-sufficiency relative to a
horizon and an objective.** My result is therefore closer to an **edge-representation result than a
policy result**, which is also where Local Optima Networks sit: the useful object is a directed
transition graph between regions, not a per-action score.

Every prior statement of the form "the minimum adequate object is `Z(x,a)`" is hereby narrowed to:
*state-only residue is **action-insufficient by construction**; adequacy for navigation is a further,
unestablished question.*

## 3. FINDING 3 — demoted to PROVISIONAL

I claimed navigation knowledge is local. Near-orthogonal fitted coefficients and below-chance
transport establish **failure of the tested representation and model family under the tested axes**.
They do **not** distinguish:

- an **intrinsically local policy**, from
- a **globally transportable law expressed in the wrong coordinates** — chart mismatch.

**That distinction becomes the last reconnaissance question**, and it is now a mandatory cycle-005
control (§6.2).

## 4. FINDING 2 — KEEP, unchanged and strongly

Production omitted the very transition semantics required to test the intended thesis.
`sigma.symbols` = 0 rows; `step_trace` degenerate; ~48.4M parent-linked records unassembled.

**One naming correction:** once assembled, those records are a **transition corpus**, not a
"navigation corpus." **Edges alone do not give direction — direction appears only relative to a
terminal objective and horizon.** Whether navigational structure exists in them is a separate
empirical question and must not be smuggled in by the name.

## 5. Charter §20 ladder — corrected (two axes, not one)

My ladder read *exhaustive > symbolic > combinatorial > deterministic > fitted*, which implies
fitted inference is always epistemically inferior. That conflates two independent axes:

- **epistemic certainty of observation** — did this transition actually occur, as verified?
- **uncertainty of policy inference** — what does this imply about what to do next?

**You can have exact observations feeding statistical inference without epistemic contamination.**
Discrete analysis breaks precisely at the boundary from *facts about observed transitions* to
*counterfactuals about unobserved ones*: `(x,a) → x'` that you executed can stay exact;
`Q(x,a) = what would eventually happen` cannot, absent exploration or modelling.

**Adopted architecture, replacing the single ladder:**

> untrusted heuristic search → **trusted transition observations** → untrusted statistical policy
> inference → prospective trial → **trusted terminal verification**

**Adopted doctrine, replacing "prefer rung 1":**

> **Infer freely; believe only prospective consequences measured through independent instruments.**

This is less restrictive than §20 as written and preserves the epistemic firewall. §20's ladder is
retained as guidance for the *observation* axis only.

## 6. Two mandatory controls added to cycle 005

### 6.1 Generator-leakage test — the mistake most worth finding

The devastating alternative explanation for the entire thread:

> the "conditional signal" is mostly **reconstruction of the benchmark generator**, not navigation
> signal.

Changing the oracle predicate is necessary but **may not be sufficient**. The required check: does
the candidate generator, the state representation, or the cell definition contain any variable
**structurally downstream of whatever produced the correct action**? The target property is

> state/action features ⟂ oracle-construction internals, **except** through the mathematical
> relationship navigation is supposed to exploit.

### 6.2 Coordinate-transport control — separates chart mismatch from intrinsic locality

For cells `c_i`, `c_j`, compare three things, and **the decisive comparison is 2 versus 3**:

1. **raw transfer** — `f_i → c_j` (this is what cycles 003–004 measured)
2. **coordinate transport** — a cheap, **mathematically natural** `T_ij` on features/actions, then
   `f_i(T_ij(x,a))`. Natural means derived from the operators' own structure, **not** an arbitrary
   learned embedding.
3. **local relearning** — fit `f_j` from scratch

If a low-complexity `T_ij` repeatedly restores most of the within-cell ordering, **"policies are
fundamentally local" was premature — it was chart mismatch.** If transport still fails after
mathematically motivated transformations, the local interpretation becomes substantially stronger.

## 7. Cycle 005 is terminal only if it resolves both

Adopted: cycle 005 becomes the thread's terminus **only** if it answers

1. does the decomposition survive an oracle whose answer is **not transparently encoded** in the
   cheap features (§6.1)?
2. does anti-transfer survive a serious attempt at **mathematically natural coordinate transport**
   (§6.2)?

If either fails, the grand interpretation shrinks drastically. If both survive, stop — that is
enough to justify rebuilding the instrument.

## 8. Recommendation C — instrument repair, independent of any result

**Authorized by HITL to proceed regardless of cycle 005.** This is engineering, not research, and it
does **not** depend on the navigation hypothesis surviving.

**Proposed canonical primitive**, superseding the framing that CLAIM is fundamental:

> **`EDGE(x_before, a, x_after, observations, provenance, context)`**

with `CLAIM` / `FALSIFY` / verdicts treated as **interpretations layered on edges**, not as the
fundamental learning record. If the north star is the verbs of mathematics, a corpus whose atomic
unit is a noun with a verdict attached was architecturally mismatched from the beginning.
**The verb is the edge.**

**Two schema invariants to enforce by interface, not by promise:**

1. **No generator may write fields in the epistemic outcome namespace.** The 99.98% self-verdict
   event was a generator carrying its own judge; make that structurally impossible.
2. **Do not reduce observations to a success bit at write time.** Preserve raw verifier-grounded
   events — `compiled?`, `typechecked?`, `goal_count_before/after`, `proof_closed?`,
   `counterexample_found?`, `expression_size_delta`, `new_subgoals`, `timeout`, `resource_cost`.
   Deciding today that "goal count −1 = good" silently writes a **human policy** into the corpus and
   forecloses recomputation under later policy definitions.

**Coordination note:** this touches `sigma_kernel/`, which is Techne's. Filed here as a specification
and a request, not executed unilaterally — charter §15 reserves program-level instrumentation change
for HITL and the owning seat.

## 9. What anchors a policy — corrected

**There is no compiler for "right move."** A verifier establishes facts about trajectories; "right
move" exists only relative to a utility functional over trajectories. `U(τ) = 1` if a valid proof is
reached within budget is externally grounded; `Q^π(x,a) = E[U(τ) | x,a,π]` is an **estimate, not a
truth**, and demanding that it carry the epistemic status of a verified event is impossible outside
exhaustive spaces.

**The clean anchor:** *this action produced this externally verified transition, and this subsequent
trajectory achieved this externally verified terminal objective under this explicitly recorded
budget.*

**And for open action spaces**, regret against an unknowable optimum is unavailable. Replace it with
**paired empirical dominance under controlled proposal budgets**: `P(solve | π₁, B)` vs
`P(solve | π₂, B)`. One does not need to know that `a` was globally best — only whether learned
navigation causes **more externally certified endpoints** than the control.

## 10. The LLM is not the hard part

Adopted architecture:

> LLM proposes verbs → reality executes verbs → Prometheus records edges → statistics infer policies
> → **prospective execution judges policies**

The LLM appears as **provenance for `a` and nowhere inside `o`**. It may emit the operator, its
arguments, a rationale, even its own ranking — all of which are **features of the proposal, not
evidence**. `p(a|x)` may be as contaminated as it likes; it cannot contaminate `P(x', o | x, a)`.
No LLM judge is required anywhere in the chain.

**The genuinely hard problem moves one level up:** *what objective over verified trajectories
constitutes mathematical progress before a theorem has been proved?* Not to be solved now. First
determine whether the edge representation carries transferable direction at all in a small **real**
mathematical environment.

*— Diomedes, amendment 2026-08-25. Findings 1 and 3 narrowed; finding 2 unchanged.*
