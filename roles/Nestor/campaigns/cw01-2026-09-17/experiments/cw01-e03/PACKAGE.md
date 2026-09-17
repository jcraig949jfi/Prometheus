# cw01-e03 — ENGINEERING LEDGER (XIII)

Experiment 3 of 10. Disposition **COMPLETE**. RECONCILE 17:55 → IX discharged ~18:12, ≈17 min of a
24 h timebox. Science cost: 74.3 s for 4 replicates × 3 arms × 60 generations × 64 organisms.

---

## THE SCIENCE

**Coalitions evolved, and they are conditional rather than merely cheap.**

| | treatment | non-conditional control | activate-all |
|---|---|---|---|
| score | 1.4730–1.6029 | 0.9601–1.3314 | 0.6588–0.6632 |

- sparsity **0.243** (≈3.9 of 16 affordances)
- conditionality **MI 1.583 bits**, excess **+1.194** over its shuffled null, significant **4/4**
- scrambling the hidden structure at *identical cost* costs **−37.6% to −61.0%**, collapses **4/4**
- ancestor-relative **+159.6%**

The control that carries the claim: the **non-conditional evolved arm has MI 0.0000 with exactly one
distinct activation pattern** — maximally sparse, completely blind. The estimator calls it blind while
calling treatment conditional. That is the sparsity-vs-coalition distinction the pre-registration named
as decisive, demonstrated on evolved populations rather than argued.

Interpretive limits stand: MI is biased upward at this sample size (≈0.14 bits on independent data), so
only the excess over the null is evidence; and this is an 82-parameter linear activation policy, not a
rich program.

---

## STARTUP

**Reused unchanged: four components** — `lib/seeds.py`, `lib/localrun.py`, `lib/residue.py`,
`lib/lineage.py`. (e01 reused 0, e02 reused 3, e03 reused 4.)

**Created:** `world_e03.py`, `execute_e03.py`, `WORLD.json`, plus two new shared components —
`lib/infometrics.py` (MI with a shuffled null) and `lib/learnability.py` (the new standing gate).

**e03 is the first experiment to clear a learnability gate before spending any budget.** ROUTER 1.9011
vs STATIC_SPARSE 0.9854 (+92.93%) vs ACTIVATE_ALL 0.6606, with `BAD_ROUTER` as the informative control:
precision 0.915 but coverage 0.199 — *more precise and worse*, proving precision alone is not the
objective.

**Failed qualification:**

| Defect | What |
|---|---|
| **D029** (critical) | The world's latent facts — hidden structure **and** class feature centres — were redrawn every episode. Class-0 centroid spread **1.955** across episodes; conditional routing was unlearnable **in principle**. Fixed to attempt-stable (spread → 0.241). |
| **D031** (critical) | The backend gate was passed by **assertion**, not measurement. |

---

## EXECUTION

**726 rows** emitted (4 × 3 × 60 generations + 6), against e02's 6. The D026 fix works: the
trajectories are durable evidence rather than something a re-run has to regenerate.

Structural fix that finally worked: **arms are genome transformations applied up front**, and
activation is **deterministic**. e02 hit RNG-desynchronised arms twice (D019, D021) because
`flag and prng.random()` short-circuits; *guarding* that pattern failed, *removing* it did not. Q10
now passes by construction — treatment and control identical on info (308.79576632907015) and cost
(600.0) with weights zeroed.

---

## TEARDOWN

Clean. In-process, 0 owned runtime resources, `pm:cw01:*` empty, 0 live consumers, 0 matched processes,
all r8 science keys intact.

---

## PORTABILITY

Unchanged: **git worktree + `PM_TAG`**, no GPU, no Redis, no container. M1 QUALIFIED; M2 / cloud CPU
LIKELY but untested and therefore not claimed; Podman UNQUALIFIED; Docker-in-WSL LIKELY.

Note for IX: e03 holds **no substrate-backed organism-visible state**, so a Redis swap would have tested
nothing. IX was discharged against a second *implementation* instead — 288 comparisons, worst divergence
**0.000e+00**.

---

## COMPRESSION

**Landed:** `lib/infometrics.py` and `lib/learnability.py`. Six shared components now exist, and e03
consumed four of them without modification.

**`learnability.py` is the important one.** Five defects across three experiments shared one shape —
*the instrument could not have shown the effect even if it existed* (D009 mechanism never fired, D010
arms never matched, D019 arms desynchronised, D025 detector blind where the signal was, D029 latent
facts redrawn). Each was caught only because I happened to look. It is now a gate that fails closed, and
it correctly rejects a 100% advantage with a dead mechanism.

---

## THE HONEST HEADLINE

**The predicted cost curve finally appeared: 8 → 12 → 3 defects.** e03 cost a fraction of its
predecessors, and reuse is visibly why.

Two qualifications belong with that number. First, e03 inherited six components and a learnability gate
that e01 and e02 had to earn the hard way — the curve measures accumulated machinery, not growing care.
Second, **D031 is a new failure mode**: I recorded `ran=True, passed=True` for a check whose entire
content was an assertion, and `lineage.decide` cited it faithfully. The machinery correctly refuses to
reach a branch whose tests did not run — but it trusts what the caller records against them. A gate is
only as honest as its inputs, and no amount of gate-building fixes that.

So the failure modes are still mutating even as the count falls. The rule this experiment adds:
**never record `ran=True` for a check that performed no comparison.**
