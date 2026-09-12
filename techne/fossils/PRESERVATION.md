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

## Host-local now (bodies)
The bodies themselves live under `<vault>/fossils/<id>/upstream/` (default
`<canonical checkout>/vault/fossils`, `$TECHNE_FOSSIL_VAULT` overridable) and are gitignored.
They survive on this host. They do NOT survive the host dying.

## The gap, and whose call it is
Full immutable preservation -- a specimen reconstructible if its upstream repository, an
academic website, or a package registry disappears -- needs an off-host immutable store keyed
by the recorded hashes. The operator's convention for large data is the Z: share; wiring the
vault to push bodies there (or to object storage) with the tree hash as the key is an operator
decision, not Techne's to make unilaterally, and large bodies must NOT go into git. Until then
the guarantee is "reconstructible from the recorded origin + verifiable by hash", which is
strong for still-live origins and weak for the day an origin vanishes. That day is the reason
this file names the gap rather than hiding it.
