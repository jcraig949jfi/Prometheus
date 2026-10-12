# Z80 confirmatory run -- integration note (C-017-T050)

Palamedes[harry1-679179c6], 2026-10-11. This note sits beside RESULT.md (Argus, the result of record) and changes no
number in it.

## 1. Independent checks (passed)

- `freeze check` is OK on the merged tree.
- `python -B -m rso.z80.analysis rso/z80/runs/CONFIRM.*-6.jsonl.gz`, re-run, matches CONFIRM.analysis.json exactly.
  The verdict is ATTRIBUTION_QUALIFIED.
- I reproduced shard 0/6 into a scratch prefix: rows_sha256 a59f37e91297... is identical to the committed meta. It took
  5 min 19 s.
- The provenance in the launch logs checks out:
  - T050 (Argus) ran on claude-sonnet-5-5 in every message.
  - T040 (Pallas) ran on claude-fable-5-1 in every message.
  - T042 was mixed after a refusal fallback (escalations/NEW_Pallas_2026-10-11_1_RESPONSE.md).

## 2. Integrator mutation (a survivor, recorded)

I ran `analysis` on 5 of the 6 shards and it still printed ATTRIBUTION_QUALIFIED. Each class stays powered at the
smaller n, and the analyzer does not check that the shard set is complete.

This does not affect the committed result:
- The committed analysis lists all six shards, and I reproduced it from all six.
- Every shard's meta pins its rows_sha256.

It is still a gap. The Ensorain analyzer refuses missing rows ("every arm needs the same 400 seeds"); this one does not.
It is recorded as a registry counterexample on z80-attribution-instrument. A later version should require every
registered (arm, seed) in the confirmatory partition before it reads a verdict.

## 3. Command defect (coordinator's, recorded)

My T050 `--cleared-by` text contained "/", and assay.py:242 refuses that, because "/" marks the shard argument. Argus
re-issued the command with the slashes removed and recorded the change (RESULT s6.1). Nothing pinned was touched.

## 4. Reading

ATTRIBUTION_QUALIFIED holds within PREREGISTRATION s11 and RESULT s2 only:
- On eleven constructed arms at their registered horizons, the replay-based instrument classed 273 of 274 unforged
  functional runs correctly. The one miss was a RECON run classed ENDO.
- No label edit moved it, and every byte, physics or generation edit was refused.
- The recipe reader b4 failed only on the 24 CDIST runs, which is the registered reason.
- Q2 tests INSERTED origin only.
- The re-check of the repaired surface was not a full genuine-Q3 review.
- Nothing here says that a Z80 organism discovered heredity. The T020 finding stands: the world demands reproduction of
  function, not endogenous heredity.
