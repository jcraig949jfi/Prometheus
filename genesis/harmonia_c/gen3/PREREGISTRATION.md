# PREREGISTRATION — Harmonia C Gen-3: composition vs. mutation for capability acquisition

**Author:** Harmonia C (M2) · **Frozen:** 2026-09-01, before any measurement.
**Binding.** Anything below may be *reported as violated*; it may not be quietly edited.
Amendments append with a timestamp and a stated reason, and never change a threshold
after seeing the number it gates.

---

## 0. Hypothesis under attack

> **H:** Useful new computational capabilities are more readily accumulated through
> composition, encapsulation, and reuse of previously viable behaviors than through
> undirected local mutation alone.

I am trying to falsify H. H is plausible; it is not established.

### Competing explanations, each of which must be separately excluded

| # | competing explanation | how it is excluded |
|---|---|---|
| X1 | composition wins because it gets a **larger effective mutation radius** per step | E3: measure realized parent-child edit distance per arm; re-run radius-matched |
| X2 | composition wins because it gets **more compute** (longer programs, macro expansion) | compute accounted in BOTH evaluations and executed VM instructions; E3b matches on instructions |
| X3 | composition wins because the **task decomposition was built to match it** | three worlds with different structural demands; W1 is declared composition-favourable *in advance* and is a positive control, not evidence |
| X4 | composition wins because of **brute-force expressivity** (bigger programs) | length budget identical across arms; expressed length reported |
| X5 | the "new capability" is **unseen syntax**, not competence | capability defined by exact match against a reference function on HELD-OUT probes |
| X6 | the capability **already existed in an ancestor** | E5 ancestor-comparison ablation, mandatory on every crossing |
| X7 | duplicate/equivalent programs counted as **distinct discoveries** | canonicalisation by behavioral signature before counting |
| X8 | **human interpretation** contaminated promotion | Court is deterministic code; no LLM in the promotion path; interpretation happens only AFTER promotion (E7) |

---

## 1. Arena (frozen)

**SlotVM.** 16 registers over Z_256. Straight-line programs (no loops, no branches), so
every program is a total deterministic function and exact equality is decidable.

- `R[0..3]` INPUT (written before execution)
- `R[4..9]` SCRATCH (zeroed before execution)
- `R[10..15]` OUTPUT (zeroed before execution; read after)

**Instruction set (12 opcodes, frozen).** Each instruction is `(op, a, b)`.

```
0 ADD  a b : R[a] = R[a] + R[b]        6 NOT  a .  : R[a] = ~R[a]
1 SUB  a b : R[a] = R[a] - R[b]        7 SHL  a k  : R[a] = R[a] << (k&7)
2 MUL  a b : R[a] = R[a] * R[b]        8 SHR  a k  : R[a] = R[a] >> (k&7)
3 XOR  a b : R[a] = R[a] ^ R[b]        9 MOV  a b  : R[a] = R[b]
4 AND  a b : R[a] = R[a] & R[b]       10 SETC a k  : R[a] = k * 17
5 OR   a b : R[a] = R[a] | R[b]       11 SWAP a b  : R[a],R[b] = R[b],R[a]
```

All arithmetic mod 256. Writes to `R[0..3]` are permitted (inputs are not protected).

**Program length:** identical cap for every arm, `L_MAX = 48` expressed instructions.
Programs longer than `L_MAX` after any operator are truncated; truncation is recorded.

**Cost model (compute accounting):**
- `evals` — number of candidate evaluations (the budget that is matched across arms).
- `vm_instructions` — expressed instructions actually executed x probes. Reported for
  every arm. Macro expansion (arm D) inflates this and MUST be reported.

## 2. Worlds (three, different structural demands)

Each world declares a battery of capability slots. Slot `k` maps to output register
`10+k`. A world's reference functions are fixed integer functions of `(x0,x1,x2,x3)`.

- **W1 PIPELINE — declared composition-FAVOURABLE (positive control, not evidence).**
  Slots: `A = f(x)`, `B = g(x)`, `T = g(f(x))`. A and B are separately reachable; T is
  their composition. If composition does not win here, the arms are broken.
- **W2 ENTANGLED — no viable 2-way split.** The target's intermediates are consumed
  twice with different transforms, so no proper subprogram is itself a battery
  capability. Composition has nothing useful to compose.
- **W3 INTERFERENCE — composition must be allowed to lose.** Two capabilities that
  both require the same scratch registers; the goal is holding BOTH at once. Naive
  concatenation destroys one. Predicts arm C loses to arm E (compose+refine).

**Pre-registered directional predictions (so the result can embarrass me):**
`W1: C,D,E > A`. `W2: no arm separates from B`. `W3: C < E, and C may lose to A.`
A campaign in which all three fire is *weak* evidence for H — it is exactly what a
well-built arena is supposed to produce. Only W2/W3 outcomes can move H.

## 3. Capability — frozen BEFORE search

Candidate `P` **holds capability k** in world `W` iff:

```
for every probe x in HELDOUT(W):   run(P, x)[10+k]  ==  f_k(x)     (exact, all 64 probes)
```

- `TRAIN` probes (16) drive fitness during search. `HELDOUT` probes (64) are drawn from
  a disjoint RNG stream and are **never** visible to any arm.
- `PERTURB` probes (64) are drawn from a *different input distribution* (structured:
  low-entropy, byte-aligned, and adversarial constants) and are reported separately.
- **TRANSFER** = the same reference functions evaluated after a fixed permutation of the
  input registers, with the candidate given permuted inputs. A capability that survives
  transfer is reported separately; transfer failure is NOT a promotion blocker but IS
  recorded.
- A previously-unseen output hash is **NOT** a capability. Novel output != capability.

**Capability set** `K(P)` = set of slots held on HELDOUT. Accumulation is measured on
`K`, not on fitness.

## 4. Arms (frozen; they differ ONLY in the variation operator)

Every arm uses the identical search loop, identical initial population, identical
selection, identical archive-write rule, identical budget and identical RNG discipline.

| arm | operator |
|---|---|
| **A LOCAL** | point mutation: change one instruction's op OR one operand |
| **B STRUCT** | segment mutation: insert / delete / duplicate / move a contiguous block |
| **C COMPOSE** | child = graft of two *distinct viable archive members*; no follow-up mutation |
| **D ENCAPS** | archive members become callable macros; child mutates over the macro-extended alphabet (a `CALL m` expands to the macro body at execution) |
| **E COMP+REF** | arm C, then one arm-A mutation |
| **F RANDOM** | uniform random program of matched expressed length (control) |

**Fairness rules, frozen:**
1. All arms are seeded from the **same** initial population and **same** archive state.
2. All arms **write** to the archive under the same rule. Only C/D/E **read** it.
3. When the archive holds fewer than 2 distinct viable behaviors, C/D/E fall back to
   arm B. **The fallback rate is recorded and reported**; a composition arm that is
   mostly fallback is reported as such.
4. Budget is matched on `evals`. `vm_instructions` is reported and, in E3b, matched.

## 5. Kill conditions (each one stops or redirects the campaign)

- **K1 (E1, arena):** if arm F (random search) acquires the W1 `T` capability in
  `>= 20%` of seeds, the arena is too easy and **no arm comparison is reported**.
- **K2 (E1, leakage):** if a constant-output program, or a program that ignores the
  inputs, holds any capability on HELDOUT, the capability definition leaks and E2+ do
  not run until it is repaired.
- **K3 (E2):** if no arm acquires any capability in any world, the campaign reports
  `NO_CUMULATIVE_CAPABILITY_ACQUISITION_OBSERVED` and E4-E8 are skipped as unreachable.
- **K4 (E3):** if the composition advantage in W1 vanishes under radius matching, the
  headline verdict becomes `COMPOSITION_ADVANTAGE_EXPLAINED_BY_MUTATION_RADIUS`.
- **K5 (E5):** a promoted composition whose capability is present in an ancestor, or
  survives removal of a composed part, is **not** a compositional acquisition. If the
  majority of crossings fail ablation, `APPARENT_NOVELTY_REDUCES_TO_KNOWN_OPERATIONS`.
- **K6 (E8):** a candidate that fails exact replay from its frozen ancestry record is
  struck from all counts, and the count is reported before and after.

## 6. The eight experiments (no ninth)

| # | name | depends on | kill |
|---|---|---|---|
| E1 | arena admissibility + leakage controls | — | K1, K2 |
| E2 | six-arm discovery head-to-head, 3 worlds x N seeds | E1 | K3 |
| E3 | mutation-radius and compute confound (X1, X2) | E2 | K4 |
| E4 | accumulation and retention (capability sets along ancestry) | E2 | — |
| E5 | causal ablation of every successful composition (MANDATORY) | E2 | K5 |
| E6 | interference boundary — when composition hurts | E2 | — |
| E7 | ontology-blind lane + post-hoc compression | E2 | — |
| E8 | Novelty Court over all promoted candidates | E2..E7 | K6 |

**Skipping rule:** if a prerequisite fails, dependent experiments are reported as
SKIPPED with the reason. They are not replaced with something easier.

**No-rescue rule:** no world, reference function, budget, or threshold may be changed
after seeing a result. If the arena turns out to be badly designed, that is a REPORTED
FINDING, not a licence to redesign and re-run.

## 7. Statistical reporting

- Every rate reported with an exact binomial 95% CI (Clopper-Pearson), never a naked
  point estimate.
- Between-arm comparison by two-sided Fisher exact test on seed-level success counts.
- `n_seeds` is fixed at 12 per (arm, world) before any run. No optional stopping.
- Seeds are `20260901 + i`. The same seed gives the same initial population across arms.

## 8. Declared conflicts and priors

- My prior, stated before measurement: **composition is a search operator, not a
  capability source.** Apollo's 2026-08-19 type-bridge cycle ruled crossover
  `search_operator` on this program's own evidence. A result confirming my prior is the
  *least* informative outcome and gets the extra attack (per
  `feedback_positive_results_are_provisional`, a lane-favouring result needs 3
  independent falsification families).
- I retracted my own last filed claim on 2026-08-31 for reading a ceiling as a floor.
  Every threshold in this document is therefore written with its direction stated
  explicitly, and E1 exists to measure the chance floor rather than assume it.

— Harmonia C, M2, frozen 2026-09-01
