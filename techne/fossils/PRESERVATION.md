# Immutable preservation (global-archaeology charter, 2026-09-12)

Re-fetchability is not preservation. What the vault guarantees today, and what is the
operator's call:

## Guaranteed now (in git, cross-machine)
For every specimen, the tracked half under `techne/fossils/specimens/<id>/` carries:
  - `record.json` -- origin (URL / repo+commit), exact version, licence, and the tree hash.
  - `UPSTREAM_HASHES.txt` -- sha256 of every upstream file plus a single TREE_SHA256.
  - `recipe.json`, `receipts/`, `harness/` -- how it was built/run and the evidence it ran.
So a specimen is reconstructible-and-verifiable: re-fetch from the recorded origin, re-hash,
compare TREE_SHA256. `python -m techne.fossils.harvest verify <id>` does exactly this.

Byte-exactness: `vault.git_pin` clones with `core.autocrlf=false core.eol=lf`, so a
git-cloned body is the upstream bytes, not a Windows-converted copy -- the tree hash matches a
Linux re-fetch. (Fixed 2026-09-12 after tinycc's `configure` arrived with CRLF; batch-01/02
git bodies predate the fix and should be re-verified on a Linux fetch before their hashes are
trusted cross-platform -- queued.)

## The preserved body is never executed in (2026-09-12)
`harvest run` stages a disposable copy of the body at `<vault>/<id>/work/` and runs the
recipe there; afterwards it re-hashes the PRESERVED `upstream/` and writes
`tree_sha256_after` and `body_preserved` into the run receipt, so the property is measured
on every run rather than asserted. This rule exists because the census that preceded it
(`harvest verify --all`, `VAULT_INTEGRITY_2026-09-12.json`) found 23 of 57 bodies dirtied by
in-place builds while their run receipts said PASS: 0 files removed, 5 modified (configure
rewrites), the rest build products added under `upstream/tree`. All 23 were put back with
`harvest restore <id>` (added rows deleted; modified rows recovered from the body's own git pin
or by sha256 content from the archive kept beside the tree; anything neither holds is reported
UNRECOVERABLE, never fabricated), each with a tracked restore receipt, and the after-census is
57/57 (`VAULT_INTEGRITY_2026-09-12_after_restore.json`). A recipe may set `"in_place": true`
to opt out; the receipt then says so. Controls: techne/tests/test_fossil_isolation.py.

## Host-local now (bodies)
The bodies themselves live under `<vault>/fossils/<id>/upstream/` (default
`<canonical checkout>/vault/fossils`, `$TECHNE_FOSSIL_VAULT` overridable) and are gitignored.
They survive on this host. They do NOT survive the host dying.

## The mirror mechanism is built; the destination is not (2026-09-12, TECHNE-65)
`python -m techne.fossils.harvest mirror --dest <D> [--dry-run]` copies each VERIFIED body to
`<D>/<tree_sha256>/upstream/` (content-addressed), re-hashes the copy, and writes a tracked receipt
under `techne/fossils/mirror/` with source hash, destination hash, bytes and a per-body status
(COPIED_VERIFIED / ALREADY_PRESENT_VERIFIED / REFUSED_SOURCE_DRIFTED / BODY_MISSING_ON_THIS_HOST /
COPY_DIFFERS_LEFT_AS_PARTIAL). A drifted body is never mirrored; a destination inside the repository
is refused (bodies never enter git). Controls: techne/tests/test_fossil_isolation.py (copy+verify,
idempotence, refusal of drift and of an in-repo destination). It has NOT been run against a real
destination: naming one is the operator's decision. Until then THE VAULT HAS ONE HOST AS ITS
PRESERVATION DEPENDENCY -- 90 bodies, ~1 GB, on this machine only.

## The gap, and whose call it is
Full immutable preservation -- a specimen reconstructible if its upstream repository, an
academic website, or a package registry disappears -- needs an off-host immutable store keyed
by the recorded hashes. The operator's convention for large data is the Z: share; wiring the
vault to push bodies there (or to object storage) with the tree hash as the key is an operator
decision, not Techne's to make unilaterally, and large bodies must NOT go into git. Until then
the guarantee is "reconstructible from the recorded origin + verifiable by hash", which is
strong for still-live origins and weak for the day an origin vanishes. That day is the reason
this file names the gap rather than hiding it.
