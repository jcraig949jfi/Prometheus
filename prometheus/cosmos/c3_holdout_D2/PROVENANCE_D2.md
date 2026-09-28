# Holdout D2 (C3) -- provenance

Author: Nestor (build delegate), 2026-09-28, under the operator directive relayed by Nestor (fresh opaque hidden
set because holdout D's sealed spec is plaintext on main). Machine: **M1 (SKULLPORT)**. Worktree
F:/Prometheus-worktrees/nestor-d-merge at 7c018d92b (= origin/main at start). Python 3.12.10 (MSC v.1943, AMD64),
numpy 2.2.6, cryptography 48.0.0 (AES-256-GCM), scipy only via the reference certificate.

## Inputs read (complete list)
- roles/Cosmos/c3/D_CONTRACT.md (s1-s7). S1_PREREG_P1P2_GATE.md was permitted but not needed.
- prometheus/cosmos/c3/{system,task,certify,probe}.py
- prometheus/cosmos/c3_holdout_D/{__init__,medium,seal,selftest}.py, PROVENANCE.md, SELFTEST.json, .gitattributes;
  sealed_spec_D.json (its header was viewed; the file is read by `draw.exposed_d_worlds()` only to REJECT
  exposed worlds from D2).
Not opened: any other roles/Cosmos file, any Cosmos branch, anything on M2. Nothing under c3_holdout_D/ was edited.

## Borrowed code / concepts
| item | source | how used |
|---|---|---|
| family, knobs, lattice, `draw_worlds`, `intervene`, `CONTROL_HISTORY_FREE` | c3_holdout_D/medium.py (imported UNCHANGED) | D2 hidden set + intervention + public controls |
| nonce -> `default_rng(int(nonce,16) mod 2^128)`, source sha LF convention, broker env guard | c3_holdout_D/seal.py | draw.py (plus rejection of exposed-D worlds) |
| DEMO world, history-free control | c3_holdout_D/selftest.py | public throwaway worlds in selftest_D2.py |
| `certify` (P1/P2 v3) | prometheus/cosmos/c3/certify.py | runner certification (unchanged, default sizes on the real run) |
| `System`, `rollout`, `batch`, `Task` | prometheus/cosmos/c3/{system,task}.py | stub interface; selftest dummy predictor |
| AES-GCM (AEAD), salted hash commitment, HMAC world tags, append-only hash chain | standard cryptographic constructions via `cryptography` / hashlib / hmac | sealbox.py, runner.py |

## Files
- `__init__.py` package docstring (no guard: verify_reveal/sealbox usable by a checker; family-loading modules guard)
- `sealbox.py` cipher, commitment, canonical JSON, spec_id
- `draw.py` once-only fresh draw -> secrets dir (plaintext, salt, key) + `hidden_D2.enc` + `MANIFEST_D2.json`
- `runner.py` across-the-firewall runner (hash-pinned package, predictions-before-certificates gate, receipts)
- `verify_reveal.py` reveal checker; `firewall_check.py` key-holder leak scan (booleans/counts)
- `selftest_D2.py` controls-only selftest -> `SELFTEST_D2.json`; `FIREWALL.md`; `.gitattributes`

## Order of events (2026-09-28)
1. Selftest on throwaway material: pass. 2. `draw.py` run ONCE (draw_utc in the manifest). 3. Selftest again
(also checks the real manifest/ciphertext publicly): pass; `verify_reveal` on the real secrets (booleans only): all
true. 4. `firewall_check` over the worktree + HEAD/origin/main trees. No hidden world was certified, no prediction
package was run against the hidden set, nothing was committed or pushed.
