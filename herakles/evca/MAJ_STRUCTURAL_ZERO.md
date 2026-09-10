# `maj` scores 0.0, and that is the correct reproduction

**Herakles, 2026-09-10.** Fixture: `herakles/evca/maj_structural_zero_fixture.json`.
Cite this file, not a chat message.

`maj` scores 0.0 on the live cs-c3-2 corpus under `stable`, on every IC sample
and every transform. It also scores 0.0 under `at_T`. So does every one of the
40 random rule tables. Read without context that looks like a rule that
failed. It is the opposite.

---

## 1. In C1-e, `maj` reproduced EXACTLY, and it was the strongest cell there

The historical reproduction (`herakles/evca/c1e/REPORT.md`, 17 of 18 cells
reproduced) recorded:

    rule   published   measured   n_ics   decision
    maj        0.000      0.000   10000   REPRODUCED  (N = 149)
    maj        0.000      0.000    4000   REPRODUCED  (N = 599)
    maj        0.000      0.000    2000   REPRODUCED  (N = 999)

Zero correct classifications out of 16000 initial conditions across three
lattice sizes. That was called the strongest single cell in the report,
because it is an exact prediction with no tolerance at all: a proportion test
at p = 0 has zero band width, so the protocol prespecified an exact rule for
it rather than a band.

The one discrepancy in C1-e was `particle2` at N = 149, which stays HELD.
`maj` is not that case.

**So `maj` = 0.0 under `stable` and `at_T` agrees with the published figure.
It is a reproduction, not a failure.**

## 2. Why it is a STRUCTURAL zero rather than a low score

`maj` cannot score above zero under either criterion, for a reason that has
nothing to do with how good it is.

**It does not relax to a uniform configuration.** Undriven, 31 cells, density
0.5, 200 samples, censored at 200 steps:

    rule        median   reached uniform   censored
    maj              2                23        177
    exp              6               200          0
    par             14               200          0
    particle1       12               194          6
    particle2       13               195          5
    GKL             13               200          0

`maj` reaches a uniform lattice in 23 of 200 samples. The other 177 never do.
It is not relaxing quickly; it is settling into a frozen NON-uniform pattern.
A naive median would have called it the fastest of the six, which is the
opposite of what is happening.

Both `stable` and `at_T` ask whether the lattice IS the correct uniform
configuration. A rule that does not reach a uniform configuration cannot
satisfy either, at any horizon, for any initial condition. The zero is
entailed by the dynamics.

## 3. The third criterion separates it from random, where the first two cannot

`cellwise_majority_match`, at the C1-e configuration, 149 cells, 298 steps,
100 initial conditions, seed 20260910:

    rule            mean    sd     frac=1   frac=0
    maj           0.5736  0.0685     0.00     0.00
    exp           0.6500  0.4770     0.65     0.35
    par           0.7300  0.4440     0.73     0.27
    particle1     0.7134  0.4497     0.71     0.28
    particle2     0.7300  0.4440     0.73     0.27
    GKL           0.7900  0.4073     0.79     0.21

    20 random tables    mean 0.4998, range [0.4939, 0.5099]

Three things read off that table.

- **`maj` at 0.5736 is well above the random band**, whose 20 draws span
  0.4939 to 0.5099. Under `at_T` the two are indistinguishable at exactly 0.0.
- **`maj`'s `frac=1` and `frac=0` are both 0.00.** It never reaches a uniform
  configuration in either direction, which is the same fact as section 2
  measured a different way, and it is why its `at_T` is structurally zero.
- **For the other five, mean cell-match equals their `at_T` accuracy exactly**,
  because their per-IC values are all 0 or 1. `exp` 0.6500 = 0.65,
  `par` 0.7300 = 0.73. That identity holds only for rules that always reach a
  uniform configuration, and `maj` is the counterexample that makes it worth
  stating.

## 4. What may and may not be quoted

**May.** That `maj` reproduces its published 0.000 exactly under `at_T`, at
three lattice sizes over 16000 initial conditions. That its zero under
`stable` is structural. That it is separable from a random table under
`cellwise_majority_match` and not under the other two.

**May not.** The cell-match number is NOT comparable to a published P. The
published figures are the fraction of initial conditions classified correctly,
all-or-nothing, which is `at_T`. `maj`'s 0.5736 is not "maj is 57 per cent
right"; it is the mean fraction of CELLS agreeing with the target, and for
`maj` specifically the two quantities are different numbers because it never
reaches uniform.

## 5. Reproduction

    python -c "from herakles.ca_stream import reset_v2 as r; \
               print(r.relaxation_time(<rule_hex>, 31, 0.5, 20260910, 200, 200))"
    python -c "from herakles import evca; \
               ics = evca.make_ics(100, 149, seed=20260910); \
               print(evca.cellwise_majority_match(\
                     evca.decode_table(<rule_hex>), ics, 298))"
