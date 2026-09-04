# Proteus maintenance record — pre-T1 hardening pass, 2026-09-04

Formal Proteus-side record of the defects exposed by Harmonia's first end-to-end integration and
by the parallel Mnemosyne seam review, plus two further defects that this pass's own verification
found in my earlier remediation.

**Scope discipline.** No published V0.6 scientific result was altered. The first specimen was not
reinterpreted. Campaign 1 was not unblocked. Frozen organism semantics were not changed. Nothing
under `proteus/foundry/` was modified, and the audit stamp still reads FRESH on its original tree
digest `3ae4ee8b773e0fcf`.

## What Harmonia's integration established about the Proteus surface

Her packet's section 23 records **"Changes outside Harmonia code: NONE"** — the consumer surface
needed no modification to carry a specimen end to end. Independently confirmed by her run:

- `blob_hash == "sha256:" + organism_id` for all 64 specimens, so the seam is self-verifying and
  needs no mapping table in either direction.
- Intrinsic/extrinsic separation demonstrated rather than asserted: the same specimen in two
  worlds produced an identical `blob_hash` and a different `artifact_id`.
- Determinism held in a third party's hands: full-run replay identical, and checkpoint-plus-RNG
  continuation reproduced ticks 8–15 of an unbroken run exactly.
- The `source_qualification` block propagated; USE A only, Campaign 1 blocked.
- The specimen drawn was a silent budget-burner and was recorded as a valid outcome with no
  claim attached. Had the population been filtered for "interesting" organisms, that first draw
  would not have existed.

## Defects

### D1 — a living document denied the registry it sits beside
`roles/Proteus/CONSUMER_SURFACE_V0_6.md` stated in bold that no registry, dictionary or catalog
exists. True when written on 2026-09-03; false roughly seven hours later when
`PLAYER_REGISTRY.json` was committed under the integration directive. Never amended.
**Found by a sibling seat, not by Proteus.** Status: FIXED (see D7 — the first fix was partial).

### D2 — a quarantine claim broader than its enforcement
`proteus/contracts/SFE_INTEGRATION.md` asserted the quarantine audit forbids any network import
in `proteus/`. It does not: `quarantine.py` scopes its allowlist to `proteus/foundry` only, so
`proteus/integration` — the package Harmonia binds to — was unenforced. The property held in fact
and was guaranteed by nobody. Status: FIXED (wording corrected; enforcement added package-wide by
`proteus/tests/test_package_import_hygiene.py`, which imports quarantine's own
`FORBIDDEN_ANYWHERE` so there is no second source of truth).

### D3 — `random` imported in V0.6 analysis code
Closing D2 immediately surfaced it: `proteus/v0_6/equilibrium.py` imports the stdlib `random` and
calls `random.Random(seed)` inside `stationary_empirical()`. Proteus policy is that `random` is
used nowhere — `SplitMix64` exists precisely so bit-exact replay does not depend on its float and
choice paths.

**Blast radius, measured rather than assumed.** `stationary_empirical` is called from exactly two
places, both in `v0_6/run_full.py`: the empirical-occupancy cross-check and the matched-trajectory
arm. Both were reported in the V0.6 final packet as **non-adjudicated** — the empirical arm is an
external check by preregistration, and the trajectory arm was explicitly discounted in section M
as under-converged. The numerical replay contract calls `stationary_power` and never
`stationary_empirical`, so the cross-runtime byte-identity result is unaffected. **No adjudicated
V0.6 number depends on this import.**

Status: **NOT FIXED, DELIBERATELY.** Replacing it with `SplitMix64` would change two published
numbers, which this pass is forbidden to do. Instead the blast radius is now pinned by gate G1,
which fails if `random` is used anywhere outside that one function.

### D4 — published hashes did not reproduce on a consumer's checkout
Harmonia's F2: the readiness packet hashed `0bf104bb…` on her working copy against the published
`5059f44c…`. She diagnosed it correctly as CRLF conversion and moved on; she should not have had
to. Status: FIXED via `proteus/.gitattributes` and `roles/Proteus/.gitattributes` pinning
`eol=lf`.

**Player identity was never at risk.** `organism_id` hashes canonical bytes held in memory, never
a file, so CRLF could not affect a specimen id — Harmonia's read-back confirmed 64/64 manifests
re-hash correctly. This defect touched document and artifact hashes only.

### D5 — compiled bytecode committed
`git add -f proteus/integration` swept six `__pycache__/*.pyc` files into the repository. The
`-f` was there to defeat `.gitignore` for run logs the directive required preserving, and it took
the bytecode with it. Status: FIXED (untracked), and gate G4 now fails if it recurs — `.gitignore`
cannot prevent this, because `-f` overrides it and `-f` is intrinsic to the preservation workflow.

### D6 — I reported an orphaned commit SHA to the operator
I cited `8735d85c6` as the carrier of the D1–D3 fixes. That SHA is **not reachable from
origin/main**: my pre-push rebase rewrote it. The real carrier is **`f27c448b8`**. The object
still exists locally, which is exactly why it looked correct.

**This is the second occurrence of this exact failure mode.** The first was `d5185d092`, cited in
the V0.6 interim packet and recorded as F3 in the V0.6 final ledger. I verified reachability for
every SHA inside that packet, then quoted an unverified SHA in chat a day later. The verification
habit was attached to the artifact, not to the act of citing. Status: corrected here; the rule is
now that any SHA quoted anywhere, including conversationally, is checked with
`git merge-base --is-ancestor` first.

### D7 — my own D1 fix was incomplete
The first amendment patched the section-0 sub-heading and left two further denials untouched,
including the **most prominent one**: the one-line answer at the top of the document, which read
"there are no player families, no player types, and no registry." A reader would have hit that
sentence first. Caught by this pass's verification step, not by the original edit. Status: FIXED —
all three occurrences are now marked amended, historical or superseded, and gate G5 fails if an
unqualified denial reappears.

## Regression gates added

All five were verified able to FAIL by reintroducing their defect against synthetic inputs; a
gate that has never fired is unproven.

- **G1** `random` may be used only inside `stationary_empirical()` — pins D3's published blast
  radius.
- **G2** the replay contract never references `stationary_empirical` — protects the byte-identity
  claim.
- **G3** the protected deterministic surface (`foundry/`, `integration/`) admits zero import
  exemptions.
- **G4** no `__pycache__` or `.pyc` tracked under `proteus/` or `roles/Proteus/` — the actual
  control against D5, since `.gitignore` cannot be.
- **G5** the living consumer document cannot carry an unqualified registry denial while the
  registry exists.

## Verification results

    pytest proteus/tests -q                    106 passed
    run_smoke.py                               PASSED, 8 specimens, 11 error paths
    run_determinism_check.py                   registry_id b15e0a7f…, matches committed: True
    audit_identity.py verify                   FRESH, tree 3ae4ee8b773e0fcf (unchanged)
    quarantine.py                              STRING LAYER: PASS
    registry first id                          7743b352… == the specimen Harmonia used
    entry_id                                   88c8818853ccfd46… == her recorded value
    phenotype                                  UNKNOWN
    eol attribute on Proteus artifacts         text: set, eol: lf
    published packet hashes from checkout      MATCH, 0 CRLF lines

## Artifacts

- `proteus/integration/ARCHAEOLOGY_REQUIREMENTS.json` — machine-readable; 8 identities, 10 stable
  hashes, 9 qualification fields, 12 queryable properties, 1 carried defect. Generated from live
  artifacts, so it cannot drift from what it describes.
- `proteus/tests/test_pre_t1_gates.py` — G1–G5.
- `proteus/tests/test_package_import_hygiene.py` — package-wide import enforcement.
- `proteus/.gitattributes`, `roles/Proteus/.gitattributes` — eol pinning.

## Remaining blockers for Harmonia T1/T2

None on the Proteus consumer surface. The standing V0.6 limitations are unchanged and inherited:
`NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`, `FULL_SPACE_CURRENT_SOURCE_UNRESOLVED`,
`OPERATIONAL_SIGNIFICANCE_NOT_YET_ADJUDICATED`. USE A is permitted; USE B and Campaign 1 remain
blocked, and nothing in this pass adjudicates them.
