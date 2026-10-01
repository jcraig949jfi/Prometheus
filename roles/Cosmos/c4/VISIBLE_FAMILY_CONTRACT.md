# C4 visible world family -- contract for a NON-COSMOS author

Issued by Cosmos, 2026-09-30, under the operator's C4 review (roles/Cosmos/prompts/2026-09-30_operator_c4_review/
s8).

This is NOT a holdout. Your family will be fully visible once it is written, and Cosmos will use it for
C4 development. Its purpose is AUTHORSHIP INDEPENDENCE: a world family designed by someone other than
Cosmos, before any C4 law search.

This file deliberately contains no candidate coordinate, no expected equation, no expected boundary and
no preferred mechanism. Please do not ask Cosmos for any of these. Please also do not read
roles/Cosmos/c3*, roles/Cosmos/c4/ (other than this file) or roles/Cosmos/research/ before your family is
committed. This is not a secrecy rule. It keeps your design independent of Cosmos's.

## 1. The functional task (the only thing your world must share with the other families)
An episode has T = k+2 steps.
- At t = 0 the system observes a CUE (one of V symbols).
- For t = 1..k it observes DISTRACTORS drawn independently of the cue.
- At t = k+1 it observes a QUERY symbol and must answer. J = 1 iff the answer equals the cue.
prometheus/cosmos/c3/task.py implements this (public). Your world may use any V >= 2 and must support
every k in {2, 4, 8}.
There is no reward economy: nothing is priced, and J is the only outcome.
Your world may make the task easy, hard or impossible in different parts of its parameter space. That is
expected and fine.

## 2. Execution API (implement prometheus/cosmos/c3/system.py `System`, batched over episodes)
  init(E) -> state            dict of arrays, axis 0 = episode. This is the WHOLE causal state: every
                              variable that can influence the future, including any environment the
                              system writes to.
  noise(n, rng) -> dict       every random draw of one step for n episodes. ALL randomness must come
                              through here (no internal RNG).
  step(state, obs_t, noise)   one step; obs_t (E,) int
  readout_features(state)     what the system's own policy sees when it answers (the harness trains a
                              readout on it)
  full_state(state)           the whole causal state as a numeric (E, D) array
Exchanging rows of every array in `state` between two episodes must give a valid state.
The system must accept ANY input symbol sequence, not only task-shaped ones.

## 3. Native measurements (your declarations; nothing universal)
Declare every native parameter with its UNITS, its PHYSICAL MEANING in plain words and its RANGE. If
your system has a natural notion of energy, maintenance or computational cost per step, you may expose
it as a declared native measurement.
Do NOT declare any cross-substrate coordinate, any "memory" or "universal" variable, or where you expect
any boundary to lie.

## 4. Knobs and world grammar
- Expose the native parameters as knobs over the declared ranges.
- A world = (your family, knob values, k, V).
- Provide a function that builds a world at any knob setting in range.
- Declare the NATURAL distribution over your knobs: the range or lattice you consider the family's
  ordinary operating space. Cosmos samples from it uniformly.

## 5. Reproducibility
- The world is deterministic given (world, seed). Replaying the same world and seed gives identical
  arrays.
- Provide a controls-only selftest that returns booleans:
  - replay identical;
  - interchange round trip (swap twice = identity);
  - noise(n, rng) is the only randomness (re-running with a fixed rng gives identical output);
  - a history-free control setting exists and is declared.
- Record the Python/numpy versions, your source sha256 and the machine you worked on.
- Add a PROVENANCE note beside your module listing every borrowed concept or code.

## 6. Delivery
- Commit your module under prometheus/cosmos/c4/families/<your_family>/ with its selftest, the
  native declarations (a JSON or MD file) and the PROVENANCE note.
- Push it, then tell Cosmos on comms: commit id, module path, declared natural distribution.
Mechanical alienness is welcome. Agreement with Cosmos is not a goal.
