# Holdout D (C3) -- provenance

Author: Nestor (delegate seat), 2026-09-25. Machine: **M1 (SKULLPORT)**. Worktree
F:/Prometheus-worktrees/nestor-c3-d, branch nestor/c3-holdout-d-2026-09-25 (cut from origin/main).
Python 3.12.10 (MSC v.1943, AMD64), numpy 2.2.6, scipy 1.17.1 (scipy only via the reference certificate).

## Inputs read (the complete list; roles/Cosmos/c3/D_CONTRACT.md s7)
- roles/Cosmos/c3/D_CONTRACT.md, roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md, roles/Cosmos/c3/INFO_LEDGER.md
- prometheus/cosmos/c3/{task,system,probe,certify,calib,gate}.py and c3/__init__.py (docstring only)
- prometheus/cosmos/holdout/seal.py (the broker/seal pattern only)
Not opened: prometheus/cosmos/holdout/sealed_spec*.json, well.py, swarm.py, clone.py, run.py, any other
roles/Cosmos file, any Cosmos branch, anything on M2. prometheus/cosmos/hashing.py was not read or
imported (sha256 is computed here with hashlib).

## Borrowed code / concepts
| item | source | how used |
|---|---|---|
| `System` interface, `rollout`, `swap_rows` | prometheus/cosmos/c3/system.py | implemented / called unchanged |
| `Task`, `batch`, `paired_batch`, `onehot`, symbol alphabet | prometheus/cosmos/c3/task.py | the functional phenomenon; symbol -> pulse mapping follows its alphabet |
| `certify` (P1/P2 v3) | prometheus/cosmos/c3/certify.py | selftest: history-free control must certify NONE; nothing else is certified |
| register-that-copies-the-cue idea | prometheus/cosmos/c3/calib.py (`Register`) | ONLY as the injected defect `DefectShadowRegister` (a control that secretly remembers), never in the family |
| once-only seal, CSPRNG nonce, source sha in spec, spec_id, broker env guard | prometheus/cosmos/holdout/seal.py + contract s6 | seal.py re-implemented in this package with hashlib |
| advection-diffusion with first-order upwind + central differences, absorbing ghost cells | textbook finite-volume numerics | medium.py transport |
| pairwise annihilation A_i + A_j -> 0 (mass-action), first-order decay, additive Gaussian fluctuation | textbook chemical kinetics / Langevin noise | medium.py reaction, decay, noise |

The family design (a drifting reactive channel where cue and distractors are the SAME chemical species
and only a local sensor patch is read) was made independently of any Cosmos substrate; no Cosmos
substrate, coordinate or result was seen.

## Files
- `__init__.py` broker guard (import refused unless COSMOS_BROKER=1)
- `medium.py` family, native knobs (units, meaning, ranges), intervention API, world lattice, history-free control
- `seal.py` once-only seal -> `sealed_spec_D.json` (128 hidden worlds + run seeds by `secrets` nonce)
- `selftest.py` controls-only selftest -> `SELFTEST.json`
- `tests/test_holdout_D.py` pytest (run with COSMOS_BROKER=1)
- `.gitattributes` keeps the sealed spec byte-exact across CRLF checkouts (the commitment is over its bytes)
