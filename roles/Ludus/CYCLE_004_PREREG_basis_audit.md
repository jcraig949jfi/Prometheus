# Cycle 004 — PREREGISTRATION: what is a measured circuit a property of?

**Registered 2026-08-27, BEFORE the partner matrix was computed.** Fossil of the failure that
prompted it: `ludus/fossils/FOSSIL_r0003_2026-08-27.json`, frozen first.

The question is not whether `r0003` survives. It is whether the **rXXXX construct** is a coherent
object at all.

---

## 0. The exact-solver advantage, and why it changes the epistemology here

Every one of the 21 worlds is solved by exact backward induction. `E_ijk` therefore carries **no
measurement error** — it is arithmetic over a finite design, not an estimate. Two consequences that
would not hold on a sampled bench:

- Thresholds below are compared against numbers with **zero** sampling noise. There is no SE to
  compute and no power calculation to do; a difference of 0.0001 is real.
- A variance decomposition over the design is **exact**, not fitted. There is no residual term
  standing in for noise — any residual is genuine higher-order structure.

This is why the audit happens now, on small exactly-solved worlds, rather than later on large
sampled ones. Approximation noise would hide exactly the conceptual defect being hunted.

## 1. The measured object

For circuit `r_i` on axis A, partner `r_j` on the other axis, world `W_k`:

```
E_ijk  =  EV(policy where axis A uses r_i and the other axis uses r_j, in W_k)
          -------------------------------------------------------------------
                          EV(exact optimal play in W_k)
```

Admissible cells only: `W_k` must expose both axes, and `r_i`, `r_j` must act on different axes.

## 2. The competing explanations, stated so they can be separated

- **H1 PRIMITIVE.** `E_ijk ≈ a_i + b_j + c_k`. A circuit has a stable marginal effect; partner and
  world shift the level but not the circuit's identity.
- **H2 PARTNER-CONDITIONAL.** `E_ijk ≈ a_i + b_j + c_k + (ab)_ij`. Circuits exist but their effect
  is conditional on the partner.
- **H3 RELATIONAL.** The `(ab)_ij` interaction dominates the main effect `a_i`. The useful object is
  the **pair**, not the circuit; `r_i` alone names nothing.
- **H4 NOT IDENTIFIABLE.** Two or more behaviourally distinct policies reproduce the same signature,
  so the measurements cannot distinguish the mechanisms they are claimed to represent.
- **H5 CONSTRUCT INVALID.** The measured quantity is an artifact of how the bench builds its
  counterfactual (the optimal-play denominator, the partner convention, the retention ratio itself)
  rather than a property of anything in the world.

## 3. Decision rule — fixed now, computed later

Exact variance decomposition of `E_ijk` over the admissible design, into main effects
(`circuit`, `partner`, `world`), two-way interactions, and the three-way term. Write

```
S_circuit = V_circuit / (V_circuit + V_circuit×partner + V_circuit×world + V_circuit×partner×world)
```

the share of a circuit's own variance that is *marginal* rather than conditional.

- **PRIMITIVE_MODEL_SURVIVES** if `S_circuit >= 0.70` **and** circuit rank order is preserved across
  partners (mean Kendall tau >= 0.80).
- **PRIMITIVES_PARTNER_CONDITIONAL** if `0.30 <= S_circuit < 0.70`, **or** rank order breaks
  (tau < 0.80) while `S_circuit >= 0.30`.
- **RELATIONAL_BASIS_REQUIRED** if `S_circuit < 0.30` **and** `V_circuit×partner >= V_circuit×world`.
- **CONTEXTUAL_BASIS_REQUIRED** if `S_circuit < 0.30` **and** `V_circuit×world > V_circuit×partner`
  — the world, not the partner, is what the circuit is conditional on. *(Added because the outcome
  list offered relational and contextual as distinct possibilities and the decomposition can tell
  them apart; naming it now rather than discovering the need for it afterwards.)*
- **CURRENT_MEASUREMENT_NOT_IDENTIFIABLE** — **overrides all of the above** if the FOUNDRY census
  finds two or more behaviourally distinct policies with identical `E` signatures across every
  admissible cell.
- **CIRCUIT_CONSTRUCT_INVALID** — overrides everything if `E_ijk` proves to be a function of the
  benchmark's counterfactual convention rather than the policy, tested by recomputing `E` under an
  alternative denominator (best-cheap-policy instead of exact-optimal) and checking whether the
  outcome class above changes.

Ties or a boundary case are reported as such, not resolved in the direction that flatters.

## 4. Invariance target — the positive result this cycle is looking for

Not "save the circuits". The target is: **find something that stays fixed when properties known to
be irrelevant are varied.** FOUNDRY supplies the irrelevance by construction — worlds identical
except in one named property. For each circuit, the invariance report records which world properties
can be changed with `|ΔE| < 0.01`, and which cannot.

A circuit with a non-empty invariance set has earned a scope statement. One with an empty invariance
set has not, whatever its mean retention.

## 5. Three levels, kept separate throughout

- **INTERFACE** — what decision is physically offered (STOP, SELECT, …).
- **MECHANISM** — what causal structure makes one action better (ruin, gate, decay, capacity
  scarcity, …).
- **CIRCUIT** — what computation turns state into a decision.

No one-to-one mapping is assumed in either direction. The partner matrix is the first instrument
that can show the mapping is many-to-many, and if it does, that is a finding about the basis rather
than a complication to be tidied away.

## 6. What this cycle may NOT do

- May not add a real game. Twenty-one worlds is the budget; FOUNDRY supplies any new contrast.
- May not rename `r0003` to any English concept — not risk sensitivity, ruin awareness, loss
  aversion, optionality, prudence, or caution. It stays ugly whatever the outcome.
- May not weaken `r0003`'s registered scope to accommodate a result.
- May not report "21-world support" for any circuit. Support is reported in four separate counts:
  development / repair / prospective / untouched.
- May not promote any circuit on world count alone. Promotion requires a qualitatively stronger
  evidence class (see the maturity ladder).

## 7. Pre-registered null expectations

Stated so that being wrong is visible:

1. `S_circuit` for the STOP axis will fall in **[0.30, 0.70)** — partner-conditional. Reason: the
   frozen fossil already shows one circuit swinging 0.0000 → 1.0000 on partner alone, but three of
   four batch-1 worlds were pairing-invariant to four decimals, so neither extreme is expected.
2. The SELECT axis will show a **lower** `S_circuit` than STOP, because `r0011` already reversed
   rank between two worlds sharing an interface.
3. The identifiability census **will** find degenerate cells in the smallest FOUNDRY worlds — worlds
   too small to separate any policies — and those cells must be excluded from the decomposition
   rather than counted as evidence of identifiability.
