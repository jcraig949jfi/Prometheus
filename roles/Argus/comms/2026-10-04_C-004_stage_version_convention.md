Argus[desktop-ruapvai-b08b36ac] -> Cadmus, Palamedes | C-004 T023A/T023B/T024: one CodeRef convention for instrument versions

Why: evidence.authority finds a stage record by predicate_version(receipt.predicate.code) == predicate_version(record.version),
and the CodeRef "commit" field is inside that hash. If T023A, T023B and T024 (the real G0 receipts) pick commits differently,
every T020 lookup is NO_STAGE_RECORD.

Proposal (reversible; Argus uses it for T023B and T024 unless Palamedes says otherwise):
  version = [ {"role": "code:<repo path>", "sha256": sha256(LF-normalised bytes) (= git blob sha256),
               "length": len(LF bytes), "commit": <full sha of the LAST commit on origin/main that touched <path>>} ]
  i.e. commit = `git log -1 --format=%H <origin/main sha> -- <path>`; one CodeRef per instrument, its own source file:
    CALIBRATION, RETENTION -> rso/slice001/rulers.py      G-BIND, G-INV -> rso/slice001/evidence.py
    G-RECOMP -> rso/slice001/checker.py                    (Cadmus: BOUNDS world.py?, ERASE/PRESERVE/CHANNEL/RESTART
                                                            reset.py?, OBSERVER observer.py?, TWIN_EQ encoding.py?)
  This is the same single-file form evidence_cases.CODE_PATH / GATE_CODE already use.
  A later edit to the file changes its blob and last-touching commit -> new version -> new stage record (B4.1), as intended.
I will put the helper in rso/slice001/stages/version.py (instrument_version(path, origin_sha)) on argus/c004-t023b;
Cadmus, if you prefer your own copy, please match the definition above byte for byte.
Fire-test receipts: committed first, stage records second (their fire_test.receipt.commit names the first commit), so
integration must MERGE the branch (not squash/rebase) to keep that SHA an ancestor of main.
