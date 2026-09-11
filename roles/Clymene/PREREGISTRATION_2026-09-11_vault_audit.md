# Preregistration -- Clymene vault integrity and utility audit (CLY-02/03)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Written and committed BEFORE the measurement runs, in its own commit, so
the order is in git history (base role, doctrine). Nothing below may be
changed after the first result is read; changes are appended as dated
annotations with the reason.

Authority: operator ruling CLY-01, 2026-09-11 -- Clymene is CHARTERED,
the March hoarding mission is RETIRED, and this is a bounded measurement
pass. No acquisition, refresh, clone-into-vault, download, deletion or
mutation of the vault. Measurement first; no repair on this pass.

Built from: branch clymene/base-role-adopt-2026-09-11, worktree
Prometheus-worktrees/clymene-base-role, host M2 (SPECTREX5).

## 0. SCOPE, stated before anything is measured

This audit measures THE VAULT AS IT EXISTS ON M2. The registry's
recorded paths are M1 paths. M1's filesystem is not readable from this
seat (only its Postgres port answers), so every statement below is
scoped to M2 and says so. Whether M1 holds a more complete vault is
UNMEASURED FROM HERE and will be reported as such, not inferred in
either direction.

Eligible population, enumerated before any test (never a prefix):

    repo snapshots on M2      26   (vault/repos/*)
    registry repo rows        26
    model directories on M2   11   (vault/models/*)
    registry model rows       14
    manifest models           20
    registry dataset rows      0
    manifest datasets          8
    other vault directories    1   (vault/evolutionary_agents, 1.3 MB,
                                    not in the manifest or the registry
                                    -- unaccounted, will be reported)

Attainable range for the repo reproducibility test: 0 to 26. Attainable
range for repo consumption: 0 to 26. A result of 0 is a real result and
will be reported with its eligible count beside it.

## 1. Definitions, fixed now

REPRODUCIBLE (repo). The RECORD is sufficient to reconstruct the
artifact from upstream TODAY. Tested, not inferred, in three parts, all
three required:

  R1 IDENTITY COMPLETE. The registry row carries a clone URL and a
     40-hex commit hash.
  R2 UPSTREAM FETCHABLE. That exact commit is fetchable from that URL
     today: `git fetch --depth 1 --filter=blob:none <url> <sha>`
     succeeds against a fresh empty repository. This is a blob-less
     partial fetch: it transfers commit and tree objects only (tens of
     KB), never file contents, and never writes under the vault.
  R3 TREE RESOLVES. `git ls-tree -r <sha>` on the fetched object
     yields a non-empty path -> blob listing.

  Any of R1/R2/R3 failing => IRREPRODUCIBLE, with which one failed
  recorded. R2 failing for a network reason rather than a server
  refusal => INDETERMINATE, retried once, then recorded INDETERMINATE
  (an instrument error is not evidence about the world).

COMPLETENESS (repo), reported separately from reproducibility because
they are different questions. For each snapshot, the fraction of the
upstream tree's comparable entries (blobs; submodule and symlink
entries excluded and counted separately) that are present on disk with
matching content. Content match is the git blob sha1 over the raw bytes
OR over CRLF-normalised bytes -- a Windows checkout with autocrlf
writes CRLF where the blob stores LF, and which of the two matched is
recorded. Extra files on disk and files missing from disk are counted.

CONSUMED (repo or model). A reference from LIVE PROMETHEUS MACHINERY,
not from an inventory. The predicate, fixed now:

  CONSUMED-PATH      a tracked non-documentary file resolves a path
                     under vault/ for this artifact.
  CONSUMED-IDENTITY  a tracked non-documentary file imports the
                     package this snapshot provides, or names the
                     artifact's Hugging Face id, in a way that would
                     load it.
  NOT CONSUMED       only documentary references (.md, report .json,
                     survey output, a stale pipeline spec), or none.

  A reference in .md, in a dossier/survey/report artifact, or in
  pipelines/*.yaml (a spec of a pipeline whose entry point is not in
  the tree) is DOCUMENTARY by definition and does not count. This rule
  is fixed now, before the search, so it cannot be moved to flatter a
  result.

  For CONSUMED-IDENTITY on repos there is a second, decisive question:
  if tracked code imports the package, DOES THE IMPORT RESOLVE TO THE
  VAULT? The vault is not on sys.path. If the package resolves to
  site-packages, the import is real but the VAULT COPY is not consumed,
  and the row is recorded NOT CONSUMED with "satisfied by site-packages
  <version>" as the evidence. This is the distinction the ruling asks
  for between path-based and identity-mediated use.

MODEL classification. Analogous, plus:

  PAYLOAD PRESENT    at least one weight file (*.safetensors, *.bin,
                     *.gguf, *.pt) on disk.
  STUB               no weight file, or registry status
                     download_failed. The two known meta-llama
                     directories are expected here; the test is run on
                     all 11 regardless so the expectation can fail.
  PROVENANCE         the HF snapshot sidecar
                     .cache/huggingface/download/<file>.metadata
                     records a repository commit hash (line 1) and a
                     per-file etag (line 2). A directory is
                     PROVENANCE-COMPLETE if every payload file has a
                     sidecar and all sidecars agree on ONE commit hash.
  INTEGRITY          each sidecar's etag is checked against the file on
                     disk: a 40-hex etag is a git blob sha1, a 64-hex
                     etag is a sha256. This is local, needs no network,
                     and is the strongest available evidence that the
                     payload is intact rather than truncated.
  REPRODUCIBLE       the recorded commit still resolves on the Hub
                     today (HTTP HEAD on the resolve URL for one
                     sidecar-covered file; 200/302 = yes, 401/403 =
                     GATED, 404 = gone). Gated counts as
                     IRREPRODUCIBLE-WITHOUT-CREDENTIAL and is recorded
                     as its own value, not folded into failure.

  NOTE fixed in advance: the registry has NO revision column for
  models. If provenance exists it comes from the ARTIFACT's sidecar,
  not from Clymene's record. That distinction will be reported.

## 2. Classification buckets (the operator's, with the additions named)

    REPRODUCIBLE + CONSUMED
    REPRODUCIBLE + UNCONSUMED
    IRREPRODUCIBLE + CONSUMED
    IRREPRODUCIBLE + UNCONSUMED
    INVALID / STUB / MISRECORDED
    UNKNOWN

INVALID/STUB/MISRECORDED takes precedence over the other five: an
artifact that is a stub, or whose registry row asserts something the
disk contradicts, is classified there even if it would otherwise be
reproducible. UNKNOWN is used only where a test could not be run, with
the reason.

COMPLETENESS is reported as a separate column and never silently folded
into a bucket, because "the record can rebuild it" and "what is on disk
is the thing" are different facts and the ruling asks for the first.

## 3. Controls (all three, run in the same pass, results published)

Given this program's graveyard of instruments that were green for the
wrong reason, and given that a preliminary look suggests the repo
snapshots are grossly incomplete, THE COMPARATOR ITSELF IS THE THING
MOST LIKELY TO BE WRONG. Controls are therefore not optional here.

  POSITIVE  A repository and commit known to be fetchable
            (tensorly @ acc439e9f9662c2b10ccdb53e5e88a0a40090525, a
            blob-less fetch already demonstrated by hand) must return
            R2 = pass. Shows the probe can detect real success.

  NEGATIVE  (a) A syntactically valid but fabricated 40-hex SHA against
            a real URL must return R2 = fail, not pass.
            (b) A non-existent repository URL must return R2 = fail.
            Shows the probe does not hallucinate availability.

  CHEAT     A directory whose contents are KNOWN to equal an upstream
            tree exactly -- produced by a real full checkout of a small
            recorded repository at its recorded SHA, into the scratch
            area and never into the vault -- must return
            match_fraction = 1.0 with 0 missing and 0 extra.
            This is success deliberately injected. WITHOUT IT, a
            headline finding of "the snapshots are almost entirely
            missing" is indistinguishable from a bug in the comparator,
            and would be exactly the kind of result this program has
            been burned by. If the cheat control does not return 1.0,
            THE COMPLETENESS RESULT IS WITHDRAWN and reported as an
            instrument failure instead of a fact about the vault.

  A fourth check on the consumption search: it is run once for a string
  known to be present in tracked files and once for a string known to
  be absent, and both must come back correctly before any consumption
  row is recorded.

## 4. Predictions, written so they can lose

Recorded now so that a comfortable result cannot be claimed as
anticipated and an uncomfortable one cannot be explained away.

  P1  Most or all 26 registry rows carry a URL and a 40-hex SHA
      (R1 passes broadly). CONFIDENT.
  P2  Most of those commits are still fetchable upstream today
      (R2 passes broadly), because six months is short for a
      well-known repository. MODERATE. Falsified if more than a
      quarter fail.
  P3  Completeness on M2 is very low for every snapshot. This is the
      prediction most likely to be an artifact of my own instrument
      and is the reason the cheat control exists. If the cheat control
      passes and completeness is still near zero, it is a fact.
  P4  Consumption is ZERO or near zero for repositories, and any
      import of these packages is satisfied by site-packages rather
      than the vault. CONFIDENT, and it is the prediction least
      favourable to this seat's continued existence.
  P5  At least one model is BOTH in the vault and in this host's
      Hugging Face cache, making the vault copy redundant. MODERATE.
  P6  The two meta-llama directories are stubs. NEAR-CERTAIN; it is
      here so that the test is run rather than assumed.

If P4 holds and P3 holds, the honest conclusion is that the repository
half of the vault is neither a working archive nor a consumed one, and
this seat should expect to PARK after recording it. That outcome is
written here, in advance, so that reaching it is not a surprise and
avoiding it is not a motive.

## 5. Conflict of interest

This seat is auditing its own historical output and recommending its
own disposition. The predicates above were chosen because they can
return a verdict against the seat, and the two that most likely will
(P3, P4) are named as such. No predicate may be relaxed after a result
is seen; an appended annotation with a reason is the only permitted
change.

## 6. What is NOT measured on this pass

- Whether M1 holds a more complete vault. Not readable from here.
- Scientific relevance of any repository or model. Out of lane.
- Any repair, re-clone, re-download, prune or delete. Forbidden by the
  ruling and by this preregistration.
- vault/evolutionary_agents (1.3 MB): enumerated and reported as
  unaccounted-for, not classified, because it is in neither the
  manifest nor the registry and no predicate above covers it.
