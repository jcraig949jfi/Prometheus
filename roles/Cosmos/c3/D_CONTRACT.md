# C3 foreign holdout -- contract for the author of a sealed substrate (D; later E)

Currency: 2026-09-24. Issued by Cosmos under the operator's directive
roles/Cosmos/prompts/2026-09-24_c3_external_seats/ (s3, s4, s8, s9, s17, s18). This file contains NO
candidate law, coordinate, threshold, result or expected answer, and must never be edited to add one.

## 1. Functional phenomenon (the only thing your world must share with anyone else's)
An episode has T = k+2 steps. At t = 0 the system observes a CUE (one of V symbols). For t = 1..k it
observes DISTRACTORS drawn independently of the cue. At t = k+1 it observes a QUERY symbol and must
emit an answer; J = 1 iff the answer equals the cue. prometheus/cosmos/c3/task.py implements this
(alphabet, paired batches). Your world may use any V >= 2 and any k in {2, 4, 8} per world, declared.
There is no reward economy: nothing is priced; J is the only outcome.

## 2. What Cosmos will measure (published definitions, roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md)
P1 persistence: history about the cue, absent from the current observation, present in the full causal
state (a held-out conditional cross-entropy difference against a permutation null).
P2 causal utility: paired episodes that share every distractor and noise draw differ only in the cue;
at t = k the full causal states of the two are exchanged; the drop in J is the causal effect.
Classes NONE / PASSIVE / FUNCTIONAL (INDETERMINATE reported). prometheus/cosmos/c3/certify.py is the
reference implementation; calib.py holds the planted calibration systems.

## 3. Execution API (implement prometheus/cosmos/c3/system.py `System`, batched over episodes)
  init(E) -> state            dict of arrays, axis 0 = episode (the WHOLE causal state: every variable
                              that can influence the future, including any world the system writes to)
  noise(n, rng) -> dict       every random draw of one step for n episodes (the harness shares them
                              between paired episodes -- all randomness MUST come through here)
  step(state, obs_t, noise)   one step; obs_t (E,) int
  readout_features(state)     what the system's own policy sees when it answers (the harness trains a
                              logistic readout on it)
  full_state(state)           the whole causal state as a numeric (E, D) array
Exchanging rows of every array in `state` between two episodes must be a valid state (the interchange).

## 4. Native measurement contract (coordinate firewall)
Declare each native parameter with its UNITS and PHYSICAL meaning ("decay rate, 1/step", "energy per
update", "channel capacity, bits"...). Do NOT declare any cross-substrate coordinate, any "memory
pressure"/"universal" variable, or where any boundary should lie. Cosmos, not you, maps native
measurements to candidate coordinates.

## 5. Intervention API
Expose your native parameters as knobs with declared ranges. Cosmos will submit, BEFORE any outcome is
revealed, frozen predictions of the form do(knob: a -> b) -> predicted class / J change. You provide a
function that builds the world at any knob setting in your declared ranges.

## 6. World grammar, sealing, reproducibility
- A world = (your family, knob values, k, V). Provide a lattice or grammar of worlds and a sealed list of
  hidden evaluation worlds (at least 120) drawn from it by a CSPRNG nonce.
- Seal with the broker convention (prometheus/cosmos/holdout/seal.py pattern): your module refuses import
  unless COSMOS_BROKER=1; the sealed spec records worlds, nonce, your source sha256, the Python/numpy
  versions; commit and PUSH the sealed files and post only the sha256 commitment to Cosmos.
- Deterministic given (world, seed); a controls-only selftest (booleans): replay identical; interchange
  round-trip (swap twice = identity); a history-free control world certifies NONE.

## 7. Independence and secrecy
- Design your substrate independently. Mechanical alienness is desirable; agreement with Cosmos is not.
- Work OFF M2 (operator decision 2026-09-24): Cosmos's withheld material exists only as local git objects
  on M2, so an author on another machine cannot see it. Do not access M2 or any Cosmos branch before your
  seal is pushed. Read only published material: prometheus/cosmos/c3/{task,system,probe,certify,calib,
  gate}.py, this file, the P1/P2 gate preregistration and INFO_LEDGER.md.
- Document every borrowed concept or code (a PROVENANCE note beside your module).
- Report the machine you worked on.
- Commit and push the seal BEFORE Cosmos submits any prediction to you.
