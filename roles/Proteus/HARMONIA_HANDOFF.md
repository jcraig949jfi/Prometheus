# Proteus players — a consumer's guide for Harmonia

You do not need to read anything about Proteus V0 through V0.6 to use this. The short version is
below; the caveats in section 9 are the only part you must not skip.

**Runtime:** CPython 3.11 or 3.12. Standard library only — no dependencies, no network, no model,
no API key, no GPU.

**Install:** there is no install. Put the repository root on `PYTHONPATH` and import. No `cwd`
assumption, no hidden fixture, no import trick.

```bash
export PYTHONPATH=/path/to/Prometheus      # Windows: set PYTHONPATH=F:\Prometheus
python -c "from proteus.integration import registry; print(len(registry.load_default()['entries']))"
```

---

## 1. What a player is

A player **is a data object** — a bounded tape-machine manifest:

```python
{"schema_version": "proteus.player_manifest.v0",
 "n_regs": 8, "tape_words": 256,
 "genome": [1274839201, ...],      # 32-bit words, 4 words per instruction
 "code_writable": False, "persist": "tape",
 "tick_budget": 256, "out_cap": 4}
```

It is data, not code. Every 4-word group is an instruction with `op = word mod 25`, so **every
word sequence is a valid program** — there is no parse failure and no such thing as a malformed
genome. No field carries a string a player can read. Players contain no natural language, no
model, and no knowledge that worlds exist.

`organism_id` is `sha256` of the canonical JSON of that manifest. Identical manifest, identical
id, forever, on any machine.

## 2. How to get players

The frozen starter menagerie is committed: **64 specimens**, at
`proteus/integration/PLAYER_REGISTRY.json`.

```python
from proteus.integration import registry as R

reg = R.load_default()             # validates on load; raises RegistryError if anything is off
ids = R.enumerate_ids(reg)         # 64 organism ids, in registry order
```

`load` and `load_default` **fail closed**: an unknown schema version, a missing or unexpected
field, a manifest that does not match its id, or a tampered `registry_id` all raise
`RegistryError` rather than returning something usable.

## 3. How to inspect one before you schedule it

```python
entry = R.get_entry(reg, oid)               # everything below, in one object
manifest = R.get_manifest(reg, oid)         # the player itself
env = R.get_resource_envelope(reg, oid)     # hard bounds, before you commit resources
```

The resource envelope is what a scheduler needs and nothing more:

`n_regs`, `tape_words`, `genome_words`, `genome_instructions`, `code_writable`, `persist`,
`tick_budget`, `out_cap`, `max_state_footprint_words`, `persistent_state_words`,
`max_ops_per_tick`, `max_output_values_per_channel_per_tick`.

These are hard bounds read off the manifest — not estimates, not a ranking. `tick_budget` is a
ceiling you can lower and **cannot raise**: passing a larger `budget` to `run_tick` is silently
clamped, and there is a test for that.

## 4. How to run one

```python
from proteus.foundry.vm import Player, Meter, validate_manifest
from proteus.foundry.prng import SplitMix64

validate_manifest(manifest)          # authoritative; raises ManifestError
p  = Player(manifest)
st = p.fresh_state()                 # {tape, regs, ip, ticks}
rng = SplitMix64(my_seed)            # YOU seed it. The player can never seed its own randomness.
m  = Meter()                         # optional resource accounting

outputs, status = p.run_tick(st, inputs, n_out, rng, meter=m, budget=None)
```

- `inputs` — a list of channels, each a list of 32-bit ints. May be empty. The count may change
  every tick.
- `n_out` — how many output channels you want this tick. May change every tick.
- `outputs` — `n_out` lists, each at most `out_cap` values. Overflow is dropped **and counted**
  in `Meter.out_dropped`; it is not an error.
- `status` — `"halt"`, `"yield"`, or `"budget"`. A status is an outcome, never an exception.

The player addresses channels by `register value mod channel count`, so a genome written against
two channels runs unchanged against seven. **Whether it does anything useful there is your
question, not the ABI's.** This is deliberate: worlds may become high-dimensional, partially
observable, warped, damaged or adversarial, and the player contract should not need to change.

## 5. Checkpoint, restore, replay

```python
from proteus.foundry.lineage import checkpoint, restore

snap = checkpoint(oid, st, encounter_id, tick)   # content-addressed snapshot
st2  = restore(snap)                             # exact state back
```

`restore` refuses a checkpoint taken under a different `runtime_hash` — it raises rather than
silently giving you a state the current interpreter would interpret differently.

**Deterministic replay guarantee.** Same manifest + same runtime + same seed + same per-tick
inputs ⇒ identical outputs, identical statuses, identical final state, identical op counts. If
you also restore the RNG to the same point, continuing from a checkpoint reproduces the unbroken
run's remaining ticks exactly. Both are verified in the smoke harness across eight structurally
different specimens.

What determinism does **not** cover: wall-clock and CPU fields in `Meter` are timings and will
differ between runs. Everything else is exact.

## 6. Provenance — how to verify what generated a player

```python
entry["identity"]     # manifest_schema_version, runtime_hash, grammar_hash,
                      # grammar_version, affordance_hash
entry["provenance"]   # source, foundry_identity, population_seed,
                      # index_in_population, derivation, generation_manifest_id
```

To reproduce a specimen from scratch: pin those hashes, re-run the generator with the recorded
foundry manifest on a listed runtime, and check `organism_id == sha256(canonical_json(manifest))`.
`python proteus/integration/run_determinism_check.py` does this and prints the digests; it has
been confirmed byte-identical on 3.11.9 and 3.12.10.

## 7. Intrinsic vs extrinsic — where your observations go

This matters more than it looks.

- **Intrinsic** (Proteus owns): genome, manifest, runtime identity, lineage, provenance. Fixed at
  generation. Determines `organism_id` and `entry_id`.
- **Extrinsic** (you own): behaviour, encounters, phenotype, scores, failures, novelty,
  discovered capabilities.

`entry_id` is computed over the intrinsic part **only**. You may write whatever you like into
`entry["extrinsic"]` — it is the one open namespace — and neither `organism_id` nor `entry_id`
will change. There is a test asserting exactly that.

Every specimen ships with `extrinsic.phenotype == "UNKNOWN"`, and Proteus never writes any other
value. **UNKNOWN is a permanent, legitimate state.** It records that no observation has been
made. The registry deliberately has no `generate → score → classify → delete` lifecycle, so an
organism with no demonstrated use is not a candidate for deletion.

## 8. What the starter population contains

64 specimens spanning all 7 tape sizes (16–1024 words), 1–64 genome instructions, all 4 persist
policies, both `code_writable` values, and all 4 tick budgets.

Under a fixed synthetic fixture, first-tick outcomes were **13 halt, 7 yield, 44 budget**, and
**54 silent / 10 emitting**. Those counts are recorded in
`proteus/integration/ABI_LIVENESS_OBSERVATIONS.json` as extrinsic observation.

**No specimen was filtered on any of that.** The population is `generate(manifest)` in generator
order; the only rejection rule is manifest validity, which rejected zero. Organisms that halt
immediately, emit nothing, or burn their whole budget are all present on purpose — removing them
would be exactly the semantic selection pressure Proteus exists to avoid.

## 9. Caveats you must not skip

Read `reg["source_qualification"]`. It travels with every registry so you never have to
reconstruct this from history:

```
deterministic_generation   QUALIFIED
semantic_quarantine        QUALIFIED
mutation_neutrality        NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT
mutation_current_source    FULL_SPACE_CURRENT_SOURCE_UNRESOLVED
operational_significance   NOT_YET_ADJUDICATED
permitted_use              USE_A_FROZEN_SPECIMEN_SOURCE
prohibited_use             USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR
```

In plain terms: **these 64 frozen specimens are safe to enumerate, instantiate, run, checkpoint
and replay.** What is *not* established is that the **mutation machinery** which would breed new
generations is neutral. It measurably is not: it carries an authored probability current, with
entropy production 1.4e-02 nats per mutation step and 11.3% of two-way probability flux appearing
as net imbalance, reproduced across two independent measurements.

Consequences for you:

- Do **not** interpret a mutated population as unbiased evolution.
- Do **not** assume structural states are sampled neutrally, and do not build a population
  comparison that quietly relies on it.
- Whether that current would actually bias a real campaign is **not yet adjudicated** — it is
  neither established nor ruled out.

Evidence, if you ever need it: `roles/Proteus/PROTEUS_V0_6_FINAL_EXTERNAL_REVIEW_PACKET.txt`.

## 10. What Proteus deliberately does NOT provide

- **No world adapter and no binding of any kind.** Proteus implements the player side only.
  Binding a world to the ABI is yours. A binding written by Proteus would breach the firewall
  that keeps players semantically sterile.
  The other side of that binding is documented at
  [`integration/HARMONIA_FIRST_INTEGRATION.md`](../../integration/HARMONIA_FIRST_INTEGRATION.md)
  (maintainer: Daedalus) — the live SFE endpoint, the artifact request contract an adapter must
  satisfy, and a runnable verification battery. Note in particular that `organism_id` is the
  sha256 of the canonical manifest (§1 above), so posting that exact serialization makes SFE's
  content address equal it — one assertion then proves a specimen crossed unaltered.
- **No player types, families, taxonomy, tags or quality scores.** The registry makes specimens
  addressable; it does not say what any of them is *for*. A test scans the registry for that
  vocabulary and fails if it ever appears.
- **No ranking, selection, or notion of a good player.** That is the arena's discovery.
- **No packaging beyond `PYTHONPATH`.** Deliberate: adding a dependency would cost the
  standard-library-only property, which is worth more than the convenience.
- **No evolutionary campaign.** Breeding is USE B and is not qualified.

## 11. Commands

```bash
python -m pytest proteus/tests -q                      # 96 tests
python proteus/integration/run_build_menagerie.py      # rebuild the registry (deterministic)
python proteus/integration/run_smoke.py                # consumer smoke harness, A-K + error paths
python proteus/integration/run_determinism_check.py    # cross-runtime identity check
python proteus/audits/audit_identity.py verify         # audit stamp freshness
python proteus/audits/quarantine.py                    # semantic quarantine
```
