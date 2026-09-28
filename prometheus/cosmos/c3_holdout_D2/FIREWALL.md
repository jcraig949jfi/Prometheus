# Holdout D2 -- firewall

D2 is the opaque successor of holdout D. Holdout D's original hidden set (`prometheus/cosmos/c3_holdout_D/sealed_spec_D.json`)
is plaintext on main and is therefore EXPOSED: it must never be used as a blind set again. D2 draws a fresh set of
128 worlds + 128 run seeds from the SAME, UNCHANGED family code (`c3_holdout_D/medium.py`, sha256-LF
`09559e69...cde4`) with a new CSPRNG nonce, and publishes only ciphertext and commitments.

## What is public (in the repo, this directory)
| file | content |
|---|---|
| `MANIFEST_D2.json` | family/version, medium.py sha256, n_worlds, cipher, IV (public), sha256(ciphertext), salted commitment, versions, draw time, spec_id. No secret. |
| `hidden_D2.enc` | AES-256-GCM ciphertext+tag of the canonical plaintext bytes. Useless without the key. |
| `sealbox.py`, `draw.py`, `runner.py`, `verify_reveal.py`, `firewall_check.py`, `selftest_D2.py` | code only |
| `SELFTEST_D2.json` | booleans only (throwaway material; never the hidden set) |

Public commitments: `commitment = sha256(salt || plaintext_bytes)` (salt 32 random bytes) and, separately,
`ciphertext_sha256 = sha256(hidden_D2.enc)`. `spec_id = sha256(canonical manifest minus spec_id)`. The AES-GCM
AAD binds the ciphertext to the medium.py source hash.

## What is secret (never in any repo, never on M2, never sent to Cosmos)
| item | where | who can reach it |
|---|---|---|
| plaintext hidden set (worlds, run seeds, nonce) | host **M1 (SKULLPORT)**, a directory under the operator's Windows user profile that is outside every git repository (path class: `C:/Users/<operator>/nestor_secrets/holdout_D2/`) | the operator account on M1 (Nestor seats run as that account) |
| commitment salt (32 B) | same directory | same |
| AES-256 key (32 B) | same directory | same |
| runner receipts (default) | M1, `C:/Users/<operator>/nestor_receipts/holdout_D2/run_*` (outside git; results only, no knobs/seeds/key) | same; released by Nestor when the operator decides |

Decryption happens only inside `runner.py` / `verify_reveal.py` in memory on M1; nothing writes the plaintext
anywhere else. Reveal (after the evaluation is closed) = publishing plaintext + salt + key, checked with
`verify_reveal.py`.

## Threat model
- **Adversary**: Cosmos on M2 (and anything Cosmos can run), able to read everything on main, every pushed branch,
  and everything on M2. Cosmos's legitimate channel is one frozen, hashed prediction package handed to Nestor.
- **Assets**: world knobs, run seeds, nonce (which regenerates both), salt (would let a guessed plaintext be confirmed),
  key.
- **Defences**: (1) secrets live only on M1 outside git -> no push/pull/branch can carry them; (2) ciphertext is
  AES-256-GCM, key 256-bit random; (3) commitment is salted, so the lattice (~10^7 points per world) cannot be
  brute-forced against it; (4) receipts carry no knob, seed or key; worlds are named by index and
  `world_tag = HMAC-SHA256(key, world||seed)`, verifiable only after reveal; (5) the predictor runs in a separate
  process that never holds the key/plaintext, sees only the System interface over a pickle-free pipe (JSON +
  `.npy` with `allow_pickle=False`), and error replies carry exception type names only; (6) the runner refuses a
  package whose sha256 differs from the one Cosmos committed to, and cannot certify a world until every world has
  a recorded prediction and a seal record commits to them all (re-verified on disk before each certification).
- **Residual risks (declared)**:
  - The System interface itself reveals physics to the predictor (state shape reveals L and V; readout dim reveals
    w_patch*V; probing step() can estimate v, D, decay...). That is the contract's design (s3), not a leak.
  - The predictor is Python code running as the operator account on M1: a malicious package could read files
    (including the key directory). Mitigations: the package is frozen + hashed (so it can be read before running),
    and an AST audit refuses filesystem/process/network/introspection imports and calls; the audit is a heuristic,
    NOT a sandbox. **Nestor should read the package source before running it** and never use `--allow-flagged`
    without reading the flags. A stronger option (Nestor's call): run the package under a separate low-privilege
    Windows account with no read access to `nestor_secrets`.
  - A predictor with oracle access could run the reference certificate itself through the interface. Usage
    (calls, episode-steps) is recorded per world; `--max-episode-steps` caps it if the adjudication rules want that.
  - Anyone with the operator account on M1 can read the secrets.

## Execution across the firewall
1. Cosmos posts `sha256(package.zip)` and hands over `package.zip` (format in `runner.py` docstring).
2. Nestor on M1: `COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.runner --package package.zip
   --package-sha256 <sha> --key <secrets>/hidden_D2.key.hex --phase predict` -> prints the chain head after all
   128 predictions are recorded and sealed. Post that head (it fixes every prediction) before certifying.
3. `... --phase certify --out <same run dir>` -> certify.py on each world + the package's intervention; RESULT.json
   and the chain head. `--verify-receipts <run>/receipts.jsonl` re-verifies the chain.

## Independent checker checklist
Anyone (no secrets needed):
- [ ] `sha256(hidden_D2.enc)` equals `MANIFEST_D2.json.ciphertext_sha256`; `spec_id` recomputes
      (`sealbox.manifest_spec_id`); `family_src_sha256` equals sha256-LF of `c3_holdout_D/medium.py` on main.
- [ ] `git log --all --stat -- prometheus/cosmos/c3_holdout_D2` shows no `*.plain.json`, `*.key*`, `*.salt*` file ever.
- [ ] `git grep -n -i -E "nestor_secrets|hidden_D2\.(key|salt|plain)" $(git rev-list --all)` returns only
      code/docs references to the file NAMES, never contents (key/salt files are 64 hex chars on one line).
- [ ] `c3_holdout_D/` is byte-identical to its sealed commit (`git diff a56ef7787 -- prometheus/cosmos/c3_holdout_D`
      shows nothing).
- [ ] `COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_D2` -> `selftest_pass: true`.
Key holder on M1 (prints booleans/counts only; never prints secrets):
- [ ] `python -m prometheus.cosmos.c3_holdout_D2.firewall_check --scan <every worktree/checkout> --git-ref HEAD origin/main`
      -> `all_clean: true` (searches for key/salt/nonce hex, every hidden world's canonical JSON, the plaintext's
      sha256 as a file hash, and clusters of hidden run seeds; also greps the committed trees of the refs).
- [ ] `git -C <secrets dir> rev-parse` fails (not a repo); `hostname` is SKULLPORT (M1), not M2.
- [ ] The secrets directory is not synced (OneDrive/Dropbox) and holds exactly the three files.
After reveal: `python -m prometheus.cosmos.c3_holdout_D2.verify_reveal --plaintext .. --salt .. --key ..` -> all true
(with `COSMOS_BROKER=1` it also re-derives every world and seed from the nonce).
