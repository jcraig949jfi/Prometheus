# Vault disposition ledger -- measured result

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Authority: operator ruling CLY-01.
Preregistration: roles/Clymene/PREREGISTRATION_2026-09-11_vault_audit.md,
committed at fcd1eebfe BEFORE any measurement ran.
Rows: roles/Clymene/ledgers/VAULT_DISPOSITION_ROWS_2026-09-11.jsonl.
Instruments: roles/Clymene/science/*.py.
Raw runs: roles/Clymene/science/runs/*.jsonl.
Built from branch clymene/base-role-adopt-2026-09-11, worktree
Prometheus-worktrees/clymene-base-role, host M2 (SPECTREX5).

SCOPE, unchanged from the preregistration: this measures the vault ON M2.
M1's filesystem is not readable from this seat. Nothing was written,
deleted, re-cloned or downloaded into the vault. No deficiency was
repaired.

## 0. Controls first (7 of 7 PASS)

Published before the results because the results depend on them.

    POSITIVE                  a known repo+SHA fetches           PASS
    NEGATIVE_FABRICATED_SHA   a made-up SHA is refused           PASS
                              ("upload-pack: not our ref")
    NEGATIVE_DEAD_URL         a non-existent repo is refused     PASS
    CHEAT_KNOWN_GOOD_TREE     a real checkout of baukit at its   PASS
                              recorded SHA scores match=1.0,
                              0 missing, 0 extra, 0 mismatch
    SEARCH_CHANNEL            finds a known-present string,      PASS
                              finds 0 of a known-absent one
    INTEGRITY_CHANNEL_CHEAT   a deliberately corrupted copy      PASS
                              hashes differently from the clean
    WEIGHTS_PROBE_CHANNEL     an open repo's weights are 200,    PASS
                              a fabricated filename is 404

The CHEAT control is the load-bearing one. The headline repository result
below is that the snapshots are ~97.5% absent, which is indistinguishable
from a broken comparator without it. A real 24-file checkout scored
exactly 1.0 through the same code path, so the comparator can observe a
perfect match and the shortfall is a fact about the vault.

## 1. Repositories -- 26 of 26 REPRODUCIBLE, 0 of 26 CONSUMED

    bucket                        count
    REPRODUCIBLE + UNCONSUMED        26
    everything else                   0

REPRODUCIBILITY. All 26 registry rows carry a URL and a 40-hex commit
hash (R1). All 26 of those exact commits are fetchable from upstream
today (R2), tested by a blob-less partial fetch against a fresh empty
repository, not inferred. All 26 resolve to a non-empty tree (R3). Zero
INDETERMINATE. The entire probe cost 49 seconds and a few MB, because
`--filter=blob:none` transfers commit and tree objects only.

The record is sufficient. Every one of these 26 snapshots could be
reconstructed exactly, today, from the registry alone.

CONSUMPTION. Zero vault-path references in live code, for all 26. Four of
the packages ARE imported by live Prometheus code, and not one import
resolves to the vault:

    package           refs in live code   resolves to
    ribs (pyribs)            20           site-packages (installed);
                                          Techne used it 2026-09-09
    transformer_lens         14           NOT INSTALLED on this host
    sae_lens                  1           NOT INSTALLED on this host
    quimb                     1           NOT INSTALLED on this host

(Name-substring counts are not used for the verdict: "THOR" matches
"AUTHORS" 198 times. The verdict rests on path references and on where
imports actually resolve.)

COMPLETENESS -- the finding that was not anticipated.

    upstream comparable entries       10,468
    files on disk                        258
    completeness                        2.46%
    content mismatches                      0   (after the LFS correction)
    extra files on disk                     0
    matched only after CRLF normalising   238 of 257

Every one of the 26 directories contains ONLY its top-level files. Every
subdirectory exists and every subdirectory is EMPTY -- including
`tensorly/`, `sae_lens/`, `quimb/` and `transformer_lens`, the package
directories themselves. Per-snapshot completeness runs from 0.24% (THOR,
5 of 2,078) to 53.3% (openalex-python, 8 of 15). All 258 files share an
mtime inside a 2.5-second window on 2026-04-11, which is the signature of
a copy, not a clone.

What is on M2 is 8.6 MB of README, LICENSE and setup.py files. It is not
an archive of these repositories; it is their covers.

Two things are worth separating carefully. The files that ARE present are
byte-correct -- zero mismatches across 10,468 compared entries. And the
record is complete enough to rebuild all 26. The vault's repository half
has lost its contents, not its provenance.

THE SHARPEST OBSERVATION. The three packages live code imports and that
are NOT installed on this host -- transformer_lens, sae_lens, quimb -- are
exactly the case where an archive would have earned its keep. Sixteen call
sites in ignis, arcanum and prometheus_math cannot run here for want of
them. The vault holds a directory named for each, and each is empty. The
archive fails precisely at the point where it would have had value.

## 2. Models -- 11 directories, 50.58 GiB

    bucket                          count     GiB
    REPRODUCIBLE + UNCONSUMED           8   40.82
    IRREPRODUCIBLE + UNCONSUMED         1    9.76   google/gemma-2-2b
    INVALID / STUB / MISRECORDED        2    0.00   meta-llama x2

INTEGRITY. 9 of 9 payload directories verify. 112 files were hashed
against the etag recorded in their own Hugging Face sidecar -- git blob
sha1 for small files, sha256 for LFS weights -- with ZERO failures. Every
byte of the 50.58 GiB is the byte that was downloaded.

PROVENANCE. 9 of 9 payload directories are provenance-complete: every
payload file has a sidecar and all sidecars agree on one repository
revision. This provenance did NOT come from Clymene. The registry has no
revision column and never recorded one; the revisions come from
`.cache/huggingface/download/<file>.metadata`, written by huggingface_hub.
The artifacts carry better provenance than the archivist's own ledger.

CONSUMPTION. Zero of 11 are referenced by vault path. Six of 11 have their
Hugging Face id in live code (ignis batch scripts and configs, arcanum) --
by IDENTITY, which resolves through the Hub or the local HF cache, never
through the vault. The distinction the ruling asked for is clean here:
identity-mediated use does not consume the vault copy.

One directory (meta-llama--Llama-3.2-1B) is ALSO present in this host's
Hugging Face cache. It is referenced 22 times in live ignis code. The
vault's copy of it is a 55 KB stub with no weights; the working copy is in
the cache. That is the whole relationship between this vault and the
program's actual model use, in one row.

STUBS, confirmed rather than assumed (prediction P6). Both meta-llama
directories hold a README, a LICENSE and an empty `original/` -- the
public files that download before the weights are refused. The registry is
honest about them (download_failed, 0 bytes); every report counted them.

## 3. The one artifact that matters, and it argues against my own position

GOOGLE/GEMMA-2-2B IS NO LONGER OBTAINABLE.

    2026-03-23 04:46:11  download begins, no credential, no gate
    2026-03-23 04:52:07  [DOWNLOADED] google/gemma-2-2b (9.76 GB)
    2026-09-11           HTTP 401 on the weights at the recorded revision
                         (README at the same revision still returns 200)

It downloaded cleanly in March -- SECONDS after meta-llama's two gated
repositories returned 403 in the same run, so the instrument could plainly
see a gate when one existed. Today its weights are gated. The gate closed
between those dates.

The vault holds a copy that is integrity-verified 12 of 12 against its own
recorded etags, provenance-complete at revision c5ebcd40d2. It is the only
artifact in the vault, of 37 measured, that cannot be reconstructed from
its record today.

I have to report this as evidence against the recommendation I filed this
morning, which was that the March thesis -- "archive it before the window
closes" -- optimised bytes on disk and should not be revived. The thesis
is correct for exactly one artifact in eleven, and that artifact is here
and intact.

I am not going to oversell it. The honest statistics:

    models attempted in March                 11
    already gated then (failed)                2
    downloadable then, gated now               1
    still downloadable                         8
    rate of window-closing, ~6 months      1 / 9 attempted-and-obtained
                                           = 11%, 95% CI roughly 2% to 48%

An interval that wide is not a base rate, it is a hint with n=1 in the
numerator. It is also the first direct evidence the program has that the
window closes at all, rather than an assumption. And note what it does NOT
say: gemma-2-2b is UNCONSUMED. Its value is optionality, not use. Nothing
in Prometheus reads it today.

## 4. Disposition recommendation

MUST BE PRESERVED -- 9.76 GiB, one artifact

    google--gemma-2-2b    intact (12/12), provenance-complete, weights now
                          gated. Not re-obtainable without a credential.
                          Preserve on UNIQUENESS, explicitly not on use.

DELETION-ELIGIBLE -- 40.83 GiB, 36 artifacts, 81% of the vault

    8 model directories   40.82 GiB. Integrity-verified, provenance-
                          complete, weights obtainable at the recorded
                          revision today, and consumed by nothing via the
                          vault. Deleting them breaks no measured
                          reference: the six identity references in
                          ignis/arcanum resolve through the Hub or the HF
                          cache regardless.
    26 repo snapshots      8.6 MB. Reproducible from the registry and
                          consumed by nothing -- and 97.5% absent already,
                          so what would be deleted is the covers.
    2 meta-llama stubs    ~110 KB. No weights, and their weights are gated
                          anyway. They exist only to be miscounted.

NOT CLASSIFIED -- 1.3 MB

    vault/evolutionary_agents (funsearch, OpenELM; 39 files) is in neither
    the manifest nor the registry. No predicate in the preregistration
    covers it. Enumerated and reported, not judged.

A caution on the deletion figure, because it is the number most likely to
be acted on: the 40.82 GiB is deletion-eligible under the criteria in the
ruling, not "worthless". Re-downloading it is ~41 GiB of bandwidth and the
gate could close on any of it, as it did on gemma. If the operator's
concern is disk, deleting the 8 reproducible models recovers 81% of the
vault at the cost of that optionality. If the concern is not disk, the
cheapest correct action is to do nothing and keep the ledger.

## 5. What would falsify this, and what it does not cover

FALSIFIERS, named so they can be used against this result:

- A live consumer of any vault path that my search could not see. The
  census covers TRACKED files at HEAD in this repository. Untracked
  scripts, other machines (M1, M3, M4), notebooks and a human loading a
  path by hand are NOT covered. One such consumer flips a row.
- A more complete vault on M1. Not readable from this seat. If M1's
  snapshots are intact, the completeness finding is about the M2 COPY, not
  about the archive, and the repository rows would need re-measuring
  there. The reproducibility and consumption findings would stand.
- An operator need for offline availability, which makes presence
  valuable independently of provenance and consumption. Not found in the
  repository; not ruled out by the operator.

NOT COVERED, deliberately: scientific relevance of anything here; any
repair; M1; and whether the 8 deletion-eligible models should actually be
deleted, which is the operator's call and not this seat's.

## 6. Instrument corrections made during the pass

Both are recorded because both would have produced a green-for-the-wrong-
reason result, and both moved the answer AGAINST this seat's interest.

- GIT LFS. The comparator flagged autogen-landing.jpg as a content
  mismatch. The upstream blob at that commit is a 131-byte LFS pointer;
  the file on disk is the smudged image and its sha256 equals the
  pointer's oid exactly. Not a mismatch. Correcting it removed the only
  evidence that the vault holds a damaged file, taking repository content
  mismatches from 1 to 0. Preregistration annotated; CLY-CAL-008.
- THE WEIGHTS PROBE. The preregistered model reproducibility test HEADed
  "one sidecar-covered file". For a stub, the only sidecar-covered files
  are the PUBLIC ones, so both meta-llama rows came back 200 = REPRODUCIBLE
  while their weights return 401. A supplementary probe now asks whether a
  WEIGHT file resolves, and it can only move a row toward IRREPRODUCIBLE,
  never away. Without it this ledger would have reported three gated
  artifacts as reproducible, including gemma-2-2b -- and would have missed
  section 3 entirely. CLY-CAL-009.

The second one is worth naming plainly: the single most important finding
in this audit was hidden behind a status code from the wrong file, in an
instrument this seat wrote this morning, on the same day the base role
told it not to trust status codes from the wrong layer.

## 7. Seat consequence

The preregistration said that if completeness and consumption both came
back near zero, Clymene should expect to PARK. Both did: 2.46% and 0 of 37.

The ruling allows one exception -- "unless the audit uncovers a stronger
live function." Section 3 is a candidate, and this seat declares its
interest in it being one. The candidate function is NOT archiving. It is
narrow: WATCH GATE STATE ON ARTIFACTS THE PROGRAM ALREADY DEPENDS ON, and
report when one closes. It costs one HTTP HEAD per artifact (the whole
11-model probe took under a minute), it produces a dated row whether or
not anything changed, and it would have caught gemma-2-2b closing.

Whether that is worth a seat is the operator's call, not mine. Recommended
default if unsure: PARK, keep this ledger, and let the question be
reopened by the next artifact that turns out to be ungettable.
