# Data loss event — 2026-08-22 ~08:33

Written immediately after discovery, before any restoration, so the record is not
reconstructed from memory later.

## What happened

Between two consecutive tool calls in iteration 10, every file in
`charon/ceiling_v0/` was deleted except `runs/*.log`, `__pycache__/`, and the
directories themselves. Directory mtime is 08:33.

The preceding operation was a single-file read-modify-write of `sufficiency.py`
(`pathlib.read_text` -> `str.replace` -> `write_text`). That cannot delete
sibling files, and it failed with `FileNotFoundError` on the READ, meaning the
file was already gone when it ran. I did not issue a delete, and no tool call in
this session removed anything other than five scratch run directories in
iteration 5 (`_chk`, `_det_a`, `_det_b`, `smoke`, `base01`), all named
explicitly. Cause is therefore external to this session and unidentified.

## Lost and NOT recoverable

- **`runs/emission01/` transcripts.** The raw model outputs from the only usable
  lane window. Iteration 9's relevance finding — that 38 of 38 claims targeted
  patterns occurring in held-out queries, mean ~12 occurrences — was derived by
  re-parsing these. The claim TEXTS are gone. That specific result cannot be
  re-derived from anything that survives, and the lane is down, so it cannot be
  re-measured either.
- `runs/emission01/emission.jsonl` (structured per-turn records).
- All artifact stores (`store_seed*_*.json`) from every run.

## Lost but EXACTLY reproducible

Every deterministic result. The pipeline is byte-reproducible by construction and
there is a guard test asserting it (`test_pipeline_determinism`: same seeds in,
identical records and stores out). Re-running restores these bit-for-bit:

- `runs/base20/`, `runs/b2_base20/`, `runs/b2_ign/`, `runs/b2_p3d2/`
- 20-universe baselines, ablations, funnel, verifier sweep, bias sensitivity
- `sufficiency.py` sweeps

## Survived

- **`runs/emission01.log`** — all 48 per-turn emission lines, i.e. the complete
  headline model result (C0 1/12 turns, C1 15/15, C1N 14/14, truth counts). The
  irreplaceable measurement survives in printed form even though its source data
  does not.
- `runs/free_overnight.log`, `free_overnight_p2.log`, `c1_run.log`,
  `c1_pilot.log`, `emission02.log`.
- `__pycache__/*.pyc` for 11 modules: arms, baselines, c4, calibrate, lanes,
  metrics, policy, prompts, reasoner, substrate, universe. Compiled 3.12 bytecode,
  so structure and constants are recoverable even where source is not.
- The published report artifact (external), holding the 20-universe numbers.

## Not in pycache, must be rewritten

`run.py`, `ablations.py`, `analyze.py`, `build4.py`, `emission.py`,
`sufficiency.py`, `tests/test_all.py`, and every markdown file including both
pre-registered SPECs and the iteration log.

## The actual lesson

**Nine iterations of work were never committed to version control.** That is why
there is no recovery path. The experiment carried elaborate internal safeguards —
pre-registration hashing, provenance on every memo entry, validity flags,
leakage scans, 79 guard tests — and none of them protect against the working tree
disappearing. Durability was the one failure mode with no guard on it.

First action on restoration: `git add` and commit, before writing anything else.

## Integrity note

The pre-registered SPEC files are gone. Their content is reconstructible from
this session's record, but a reconstructed pre-registration is weaker evidence
than a hashed one, and I will not claim otherwise.

I initially wrote here that the surviving logs still carry the original
`spec_md_sha256_16` values so a restoration could be checked against them. That
is **false** and I am correcting it in place rather than deleting it. The
manifests lived in `runs/*/manifest.json`, inside the deleted run directories;
the surviving `.log` files contain only printed progress lines. Grepping them for
`spec_md_sha256_16` and `code_sha256_16` returns nothing.

So there is **no surviving hash of either SPEC**. A restored SPEC is a
reconstruction attested only by this session's transcript, and every restored
file will say so at the top. Pre-registration integrity for Builds 1 and 2 is
permanently downgraded from cryptographically checkable to
testimony — which, given that pre-registration is the entire defence against
post-hoc goalpost-moving, is the most damaging part of this loss. It matters more
than the deleted code.
