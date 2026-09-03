# Proteus Player Foundry — consumer-facing surface, as it exists on 2026-09-03

**Status: DOCUMENTATION ONLY.** Written under the V0.6 completion directive section 7. Nothing
here was built, changed or designed for this document. Where a thing a consumer would want does
not exist, this file says it does not exist rather than creating it. Proteus is **NOT qualified**
and integration is **NOT authorized**; this describes what a future consumer would find, not an
offer to be consumed.

## 0. The one-line answer to "what players can I ask Proteus for?"

**There are no player families, no player types, and no registry.** Proteus exposes a single
deterministic generator that samples organisms uniformly from the bounds declared in a Foundry
manifest. A consumer does not choose a *kind* of player; it chooses *bounds* and a *seed*, and
receives a population sampled from those bounds.

### Is there a canonical player registry or dictionary?

**NO. It does not exist.** There is no registry file, no dictionary, no catalog, and no
enumeration endpoint anywhere in `proteus/`. A search of the entire package for
registry/dictionary/catalog/family returns nothing. The only "family"-like word in the tree is a
docstring line in `proteus/foundry/generate.py` stating that the generator holds no opinion about
which opcodes are common.

Per the directive, one is **NOT** being built during V0.6. Whether a registry should exist is an
external integration decision to be taken after this experiment closes. If one is ever built, note
that it would be a semantic surface pointed at a deliberately semantics-free population, and the
A1 firewall reasoning should be applied to it before it is written.

## 1. Generators available

One: `proteus.foundry.generate.generate(foundry_manifest) -> list[organism_record]`.

There is no second generator, no variant sampler, and no curated subpopulation.

## 2. Stable identifiers

- `organism_id` — `sha256(canonical_json(player_manifest))`. Content-addressed, so identical
  manifests are the same organism everywhere, forever.
- `lineage_id` — the founder's `organism_id`; stable across the lineage.
- `generation` — integer, 0 at generation.
- `runtime_hash` — sha256 over LF-normalised `affordances.py` and `vm.py`. Changes if and only if
  the interpreter changes.
- `foundry_identity(fm)` — `sha256({foundry_manifest, runtime_hash})`; identifies a whole
  population request.
- `GRAMMAR_HASH` — sha256 of the mutation grammar table. Active value (v0.4):
  `5043f5e11a726b63a9553cc4855995c3ac324e55f8154ffe4adf28dad553a832`.
- `AFFORDANCE_HASH` — sha256 of the published affordance table; the opcode-semantics identity.

Canonical JSON is `sort_keys=True, separators=(",", ":"), ensure_ascii=True`. Identity is over
that byte string, not over a file, so CRLF checkout settings cannot change an id.

## 3. Manifest and schema versions

- Player manifest: `proteus.player_manifest.v0`, schema at
  `proteus/contracts/player_manifest.schema.v0.json`, `$id` `prometheus/proteus/player_manifest/v0`.
- Foundry manifest: `proteus.foundry_manifest.v0` (`FOUNDRY_SCHEMA` in `generate.py`).
- Lineage record: `proteus/contracts/lineage_record.schema.v0.json`.
- The schema document is descriptive. **`proteus.foundry.vm.validate_manifest` is the authority**
  when the document and the code disagree; it fails closed and raises `ManifestError`.

## 4. Deterministic seed contract

- All randomness is `SplitMix64`, pure 64-bit integer arithmetic. Python's `random` module is used
  nowhere in `proteus/foundry`, deliberately.
- Population root stream:
  `SplitMix64(seed_from("proteus.generate.v0", fm["seed"], RUNTIME_HASH))`. The runtime hash is
  *inside* the seed, so the same numeric seed under a changed interpreter is a different
  population by construction rather than by convention.
- Organism *i* is drawn from `root.derive("organism", i)`. **`derive` does not advance the
  parent**, so organism *i* depends only on `(seed, "organism", i)` and is independent of how many
  organisms were requested or of any parallel decomposition.
- Guarantee: **same foundry manifest plus same runtime gives a byte-identical population.**
- The player never seeds its own randomness. At run time the operator supplies the `rng`.

## 5. Configuration parameters, the whole request surface

`DEFAULT_FOUNDRY_MANIFEST`, with the defaults as committed:

    schema_version        "proteus.foundry_manifest.v0"
    seed                  0
    n                     0                       population size
    n_regs_range          [2, 16]
    tape_words_choices    [16,32,64,128,256,512,1024]
    genome_instr_range    [1, 64]                 instructions; 4 words each; capped at tape/4
    code_writable_weights [1, 1]                  [false, true]
    persist_weights       [1, 1, 1, 1]            none, regs, tape, all
    tick_budget_choices   [16, 64, 256, 1024]
    out_cap_choices       [1, 4, 16]

`validate_foundry_manifest` rejects anything outside the published `STORAGE_BOUNDS` before
sampling. The ranges above are the default *request*; the affordance table's bounds are wider
(tape to 4096, genome to 4096 words, tick budget to 65536, out_cap to 256).

## 6. The artifact a consumer receives

`generate()` returns a list of organism records:

    {"organism_id", "lineage_id", "generation", "runtime_hash", "manifest"}

where `manifest` is the player itself:

    {"schema_version", "n_regs", "tape_words", "genome" (list of uint32),
     "code_writable" (bool), "persist" (enum), "tick_budget", "out_cap"}

**A player IS this object.** It is data, not code: every 4-word group is an instruction with
`op = word mod 25`, so every word sequence is a valid program and there is no parse failure. No
field carries a string a player can read.

Export shapes, one direction only, in `proteus/foundry/export.py`: `sfe_artifact_payload(organism)`
for content-addressed SFE artifacts, and `pew_rows(...)` with `write_jsonl(...)` for Evidence Wiki
rows. **This module never talks to any engine** — no client, no token, no network import; the
quarantine audit enforces that for the whole package.

## 7. Runtime requirements

CPython 3.11 or 3.12, standard library only. No third-party dependency, no GPU, no network, no
model, no API key. Verified byte-identical on 3.11.9 and 3.12.10 (Windows) in V0.6; the
reproducibility claim is bounded to the hosts actually tested.

## 8. Validation and audit entry points

    python -m pytest proteus/tests -q            67 tests
    python proteus/audits/audit_identity.py verify
    python proteus/audits/quarantine.py          semantic-quarantine audit
    proteus.foundry.vm.validate_manifest(m)      fail-closed, raises ManifestError
    proteus.foundry.qualify.qualify(...)         mechanical existence check only

`qualify` is **not selection and not a world**. It asks only whether the manifest is within
published bounds, was generated under this runtime, and executes the frozen probe ensemble without
the runtime raising. An organism that emits nothing, halts immediately, or spins its whole budget
**PASSES** — those are phenotypes, and judging them belongs to the neutral operator.

## 9. Expected failure responses

- Invalid manifest: `ManifestError` (a `ValueError`), fail-closed, before any execution.
- Invalid foundry manifest: `ValueError` from `validate_foundry_manifest`, before sampling.
- Qualification death: appended to a hash-chained `FailureLedger` with its cost. Deaths are
  recorded, never silently dropped.
- Tick outcome is a status, not an exception: `"halt"`, `"yield"` or `"budget"`.
- Output overflow is not an error: appends beyond `out_cap` are dropped **and counted**.
- Stale audit: `audit_identity.py verify` prints `STALE:` and the offending paths. A PASS stamp
  binds per-file digests, so a stamp that predates a file entering the tree cannot read fresh.

## 10. The ABI a player sees (`proteus/contracts/WORLD_INTERFACE.md`)

    Player(manifest) -> interpreter bound to one immutable manifest
    player.fresh_state() -> {tape, regs, ip, ticks}
    lineage.restore(checkpoint) -> state
    player.run_tick(state, inputs, n_out, rng, meter=None, budget=None) -> (outputs, status)
    lineage.checkpoint(organism_id, state, encounter_id, tick) -> content-addressed snapshot

Generic and semantics-free. Channel counts may differ per tick, per encounter and per world; the
player addresses channels by `register value mod channel count`. **Proteus implements the player
side only — there is no World-0 adapter and no binding of any kind**, because a binding written by
Proteus would be a firewall breach by construction. A player never receives a world identity, a
tick number, a score, a budget remaining, the existence of other players, or any string.

## 11. How a consumer reproduces a player

1. Pin `runtime_hash`, `AFFORDANCE_HASH`, `GRAMMAR_HASH` and the manifest `schema_version`.
2. Re-run `generate(fm)` with the identical foundry manifest on a listed runtime.
3. Check `organism_id` equals `sha256(canonical_json(manifest))`.
4. Re-run `audit_identity.py verify` and confirm FRESH.
5. For an equilibrium-analysis artifact, run `python proteus/v0_6/run_replay.py out.json` on each
   runtime and adjudicate with `run_replay_compare.py` against the frozen two-layer contract.

## 12. What is missing before any consumer could actually use this

- No registry or enumeration surface (section 0), deliberately not built.
- No packaging, no version pin file, no published dependency contract beyond "standard library".
- No adapter or binding of any kind, by design.
- **Proteus is not qualified.** V0.6 measures whether the mutation machinery is dynamically
  neutral; that adjudication is what the V0.6 final packet reports.
