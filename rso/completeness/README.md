# rso/completeness -- experiment-completeness contract (C-018-T011, directive Generation 4 s2A)

**Property.** A missing shard never silently turns the experiment into a smaller one. An analyzer calls `verify(manifest,
presented_shards)` BEFORE it reads a verdict; only `COMPLETE` and `COMPLETE_EARLY_STOP` license reading one.

Why: C-017 integration removed one of six confirmatory shards and `rso.z80.analysis` still printed ATTRIBUTION_QUALIFIED,
because it evaluates whatever rows it is handed. The frozen C-017 result is unchanged; this is a NEW analyzer version beside it.

    python -m unittest rso.completeness.tests.test_completeness -v          40 tests, ~0.5 s
    python -m rso.completeness.z80 rso/z80/runs/CONFIRM.*-6.jsonl.gz       verify, then the frozen analyzer; exit 0 / 3 / 4
    python -m rso.completeness.z80 build-manifest [--write]                re-derive the manifest

## Files

| File | What |
|---|---|
| `manifest.py` | the format (sealed JSON), `build`, `seal`, canonical digest. Engine-agnostic. |
| `verify.py` | `verify(manifest, presented, sources, native_digest, pinned_manifest_sha256) -> Result`. Engine-agnostic. |
| `z80.py` | the Z80 wrapper: loader, manifest derivation from PREREGISTRATION s6, `analyse()` = verify then frozen `rso.z80.analysis.verdict`. |
| `manifests/z80_confirm.manifest.json` | the committed Z80 manifest (sha256 `8d0f9caa...5355`, pinned in `z80.PINNED_MANIFEST_SHA256`). |
| `tests/` | the tests; `RED_OUTPUT.txt` is the RED run before the verifier existed. |

## Manifest (one frozen JSON object, sealed by `manifest_sha256` over the rest)

`experiment_id`, `arms[]`, `row_key_fields[]` (how a row is keyed: Z80 uses arm + forgery kind), `seed_field`,
`shards[]` each `{id, seeds[], arm_counts{key:n}, rows, rows_sha256, meta_sha256}`, `sources{path: sha256}` (code that produced
or reads the evidence), `early_stop` (null or a rule, below). Expected execution count per arm = the sum of `arm_counts`.

## Result statuses

| Status | Meaning |
|---|---|
| `COMPLETE` | every shard present, byte-identical to the frozen artifact, in its seed partition, with its row counts; sources match |
| `COMPLETE_EARLY_STOP` | a rule declared in the SEALED manifest fired: every non-skippable shard verified and the trigger observed in verified rows |
| `INCOMPLETE` | nothing contradicts the manifest but required evidence (shards, or supplied source hashes) is absent; `missing` lists it |
| `REFUSED` | presented evidence contradicts the manifest; `findings` lists every kind. Outranks INCOMPLETE; `missing` is still filled |

Finding kinds: `DUPLICATE` (same id twice, identical), `CONFLICTING` (same id twice, different), `UNEXPECTED` (id not in the manifest),
`SUBSTITUTED` (internally consistent but not the frozen bytes: a re-run, a dev shard under a frozen identity), `ALTERED` (rows no
longer match the hash the writer recorded in the shard's own meta, or a meta field differs), `SEED_PARTITION` (a row seed outside
the shard's assignment), `COUNT_MISMATCH`, `SOURCE_MISMATCH`, `MANIFEST_ALTERED`.
SUBSTITUTED vs ALTERED needs `native_digest` (the engine's own rows digest; Z80: `receipt.sha256_hex`). Without it every
byte difference is reported ALTERED.

## Early stop (preregistered vs unplanned)

`early_stop = {rule_id, preregistered_in, skippable[shard ids], trigger{where{field:value}, at_least}}`. Absent shards listed in
`skippable` are excused ONLY when `at_least` verified rows match `where`. Rows from a refused shard are never counted. A
trigger not met leaves the absence unplanned: `INCOMPLETE`, with `early_stop.trigger_met == false` as the record. The rule lives
in the sealed manifest, so adding one after the fact makes a different manifest hash; callers that must not accept that pass
`pinned_manifest_sha256` (the Z80 wrapper does). A seal proves "not edited"; only a pin proves "this is the one".

## Z80 fixture (known-answer)

The manifest is DERIVED from the preregistered design -- `subjects.seeds` (s6), `assay.run`'s shard rule, `CONFIRM_N`, `N_FORGE`,
`FORGERIES` -- not read off the rows; only artifact digests come from the committed shards. Test: `build_manifest()` equals the
committed file, and the six committed shards then verify COMPLETE, i.e. the derivation predicted every shard's seeds and per-arm
counts (58, 58, 61, 62, 61, 60 rows). Fed to the frozen analyzer the complete set gives exactly `CONFIRM.analysis.json`.
Corruptions tested on that fixture: each of the six shards removed (INCOMPLETE, none gives a verdict), each duplicated, a dev-seed
shard under a confirm identity, a re-run with a different rows sha, one row altered in each shard, four meta fields altered, a
dropped row, a shard under a foreign id, a changed frozen source, a re-sealed five-shard manifest, an early stop with and
without its trigger.

## RED first, and how hard the tests bite

`tests/RED_OUTPUT.txt` is the run at commit 28252717e: ImportError, the verifier did not exist (all 40 tests RED by construction).
After implementation, 13 single-line mutants of `verify.py` were applied (ignore missing, duplicates, row hash, meta hash, seed
check, count check, unexpected id, source hash, pin, trigger, seal, sources-absent, excuse-with-findings): 12 killed. The survivor
("early stop excuses `missing` despite findings") is equivalent: a finding already forces REFUSED, so only the cosmetic `missing`
list differs.

## Limits (not claimed)

- Detects an artifact that differs from the frozen one. It cannot tell whether the frozen shards were themselves produced by the
  registered procedure: that is `rso/z80/FROZEN.json` + the `--cleared-by` gate, which `sources`/`meta_sha256` pin.
- `meta_sha256` pins the whole meta including `wall_s` and `host`. Right for committed, frozen shards; a future experiment whose
  re-run legitimately changes those should pin selected fields instead (manifest change, not a verifier change).
- The trigger language is one conjunction of equalities and a count. A richer preregistered stopping rule (sequential test) needs
  its own evaluator; declare it, do not widen this one silently.
- It verifies what is presented; whether the caller then reads only `licenses_verdict` results is the analyzer author's duty.
  `z80.analyse` does.
- Registry: proposal in `roles/Eupalamus/comms/2026-10-12_C-018-T011_INTEGRATION_READY.md` (AUTHOR_TESTED); Palamedes owns rso/registry/.
