# C3 coordinate-layer audit: verdict REJECT (public record; content stays withheld)

Date: 2026-09-29. Thread thr-32389b1e7abb (T-C3), campaign C3, experiment C3-S1 coordinate layer.
Authority: operator 2026-09-29 (audit MOVED, not dropped; not Harmonia; before the C3 freeze); MWO-0004 G7/R3
(keep the files withheld, run natively and custody-locally). Brief: roles/Cosmos/research/tasks/COORD_AUDIT_C3/BRIEF.md.
This file names no coordinate and carries no law, threshold, value or failure region. The full reviews stay on M2
until the withheld branch is published, and their hashes below make that later publication checkable.

## Execution (native, M2 SPECTREX5)
- Bundle: C:/Users/James/cosmos_runs/c3_coord_audit/20260929T121351Z/bundle (outside every repository).
  It holds 15 files, all byte-copied from the withheld branch head e73e5eb26: the visible substrates, the
  coordinate construction, the per-world maps and the public certificate. It does not hold the law, the attacks,
  the substitution results or any D/D2 material.
  BUNDLE_MANIFEST.txt sha256: raw e51997904d4304b0e139b929ef3b5c72b41a2566f64d130b389c0d29d5c0b63f
  (recorded at 5a3e2f493), LF-normalised 187eebbd8d222a44a38c69e900b4f9377d17fad8e2a636a976c57e1b5be7d5a9.
- Reviewers: 2 independent `claude -p` sessions, claude-opus-5-5, 2026-09-29 12:14:30Z to 12:19:54Z.
  - cwd = bundle; tools Read/Grep/Glob scoped to ./**; Bash/Write/Edit/Web denied.
  - No session persistence, and no project memory or CLAUDE.md in scope.
  - Neither session saw the other's output. Runner: run_replicas.py, sha256 81240804a2fc025b...
- LIMIT: these were READING reviews and could not execute code. Cosmos therefore executed every claim that
  the per-world maps can check (VERIFY.json).

## Verdicts
| replica | overall | per-coordinate | output sha256 (LF) |
|---|---|---|---|
| 1 | REJECT | 1 ADMIT (as a task covariate only), all others WITHDRAW | e2d43755fee6de83348fb361152ed6d29b0a9ff2117d7f19883a8a949f27e88c |
| 2 | REJECT | 1 ADMIT (as a task covariate only), all others WITHDRAW | 6349aa10008f5e7087cb90d8b25de741e598fb515d9927c0a92e69ca8e4d241e |

Both replicas, independently, reached the same central finding. The candidate coordinates are built on the same
common-random-number pairs as the certificate's P2 interchange, so the main coordinate RESTATES the P2 definition.
The remaining coordinates FINGERPRINT the family: zero-noise lattice points present in only some families, the
state dimension, the export encoding, and the readout layout. They are also not invariant to a change of basis.

## Executed verification by Cosmos (VERIFY.json, sha256 c294f24788ccfe04...)
On the 120 visible worlds (40 per family):
- PASSIVE worlds with a zero readout-view signal: 17/17.
- FUNCTIONAL worlds with a positive one: 76/76.
- A ZERO-PARAMETER rule written straight from the P1/P2 definitions reproduces 104/120 certificate classes:
  - 40/40, 30/40 and 34/40 by family;
  - all 16 misses are noise-limited boundary cases, which the certificate's own tests decide.
So a law over these coordinates can at most add a noise threshold to the certificate's own definition. This is
the same failure mode Artemis R-14 found in C0 (RESULTS R-0001/2), now found BEFORE the holdout was spent.

## Consequence (precommitted, BRIEF s4)
"REJECT: stop before D and report to the operator."
- The C3 claim stops before D2. D2 is NOT spent, NOT designated and NOT inspected, and its custody is unchanged.
- No PREDICTION_COMMITMENT will be made for this claim.
- The preliminary C3 law is recorded as killed at the pre-result review (GRAVEYARD G-0006). Its text is published
  later, with the withheld branch.
