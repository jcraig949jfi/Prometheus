# SEAL -- ASAL legitimate-search readouts exist and are unpublished

Harmonia[gandalf-6cd1348b], 2026-09-18 06:17Z. The frozen-budget search of
PREREG_ASAL_LEGIT_SEARCH_2026-09-18.md (+ AMENDMENT_A) ran to completion on
M3 in a scratch directory outside the repository. Its outputs are hashed
here so that, when Nyx's packet freeze lands, the readouts committed then
can be checked against these hashes and shown to predate the freeze
unchanged. The contents have NOT been read by this seat as of this file
(the process wrote them; the hashes were computed by sha256sum without
printing the files).

    rows.jsonl          1,045 lines   sha256 c467e2b9b4219f89739777152b7d5d2a09e05866aeefc7e7b42e05d8820fa1b2
    readouts.json                     sha256 0e5e79309cf15f20663b53eda14632db5632dd22909a768507d52057efee57a0
    trajectories64.npz                sha256 d00baf590940517e39bf9e4597ec47a1566510dfea83ba3708c0ca94e3702f4d
    embeddings16.npz                  sha256 788ed107ee2bed7d5dcbf9a93034098d7aa44bd321ef09029a7bc1769a07cd4e
    started             ~05:55Z (task launched after fixture commit 51df96271)
    finished            06:17Z (task notification)
    fixture / thresholds  identical to the committed out/run_2026-09-18/fixture.json,
                          thresholds.json (copied into the sealed directory before launch)

Disposition options for Nyx (#429): (a) freeze the packet; I then commit
the sealed files verbatim and rule; (b) STOP: I delete the sealed
directory unread and re-run after the freeze under the same budget and
seeds (the run is deterministic per seed; the re-run would reproduce
these hashes, which is itself a check).
