# Proteus Player Foundry — Architecture (V0)

**Status:** built 2026-09-02 under the V0 brief and the external review addendum. Foundry-local
tests only. No world touched, no campaign launched. Pure standard-library Python; no third-party
dependency anywhere in `proteus/`.

**One sentence.** A player is a content-addressed manifest — a bounded tape of 32-bit words plus
six integer/enum limits — executed by a frozen interpreter whose 25 primitives fall into nine
published classes; populations are sampled deterministically from compact Foundry manifests;
descent applies one of thirteen syntactic operators; every organism, descent, checkpoint,
encounter and death has an immutable identity; and the only two things ever measured inside the
Foundry are whether two organisms produce the same transcript on external noise and which
primitive classes that transcript depends on.

## 1. Frozen vs. evolvable

The design principle (brief §17): freeze the machinery that lets us determine whether evolution
occurred; do not freeze our conception of what a good organism looks like.

| Frozen (changing it is a new runtime identity) | Evolvable (axes the population varies on) |
|---|---|
| affordance table (`affordances.py`, hash `f1607ee8…`) | genome contents (any word sequence is a valid program) |
| instruction format: 4 words, `op = word mod 25` | genome length, 1..1024 instructions |
| tape/register/budget bounds (`STORAGE_BOUNDS`) | `tape_words`, `n_regs`, `tick_budget`, `out_cap` within bounds |
| persist-policy semantics | which persist policy (`none/regs/tape/all`) |
| protected-region semantics of `ST` | whether the genome region is writable (self-modification) |
| the mutation grammar and its weights (`grammar.py`, hash `da7e2ccb…`) | everything the operators touch |
| probe ensemble (derived from the addendum hash) | — (not a selection target) |

Nothing in the frozen column names a cognitive function. The `(M, T, C, Π)` lens of brief §2 is
not present in the code at all: in a single-address-space machine, "machinery", "representation",
"control" and "plasticity" are all patterns of words on the tape, and whether an organism has any
of them is a fact about the organism, not a slot in the runtime.

## 2. Components

```
proteus/foundry/
  affordances.py   the table; publish() writes contracts/affordance_table.v0.json
  vm.py            Player (interpreter), Meter (resource vector), validate_manifest (fail-closed)
  prng.py          splitmix64 with hierarchical derive(); no `random`
  identity.py      RUNTIME_HASH = sha256(LF-normalised vm.py + affordances.py + affordance hash)
  generate.py      Foundry manifest -> generation-0 population, bit-identical under a seed
  grammar.py       13 operators, frozen weights, GRAMMAR_HASH, static_reachable()
  lineage.py       descend(), checkpoint(), restore()
  probes.py        the frozen ensemble; run_ensemble() -> (transcript, class id)
  signatures.py    transcript class + knockout vector
  qualify.py       Foundry-local qualification with a hash-chained failure ledger
  export.py        SFE artifact payload shape, encounter identity, PEW JSONL rows (one-way)
proteus/audits/quarantine.py    string-layer audit (mechanical) + ontology table (review)
proteus/contracts/              ABI, multiplayer, SFE, PEW contracts; JSON schemas; the table
proteus/tests/                  replay, mutation, failure
proteus/v0/                     preregistrations, runners, results, rows, campaign proposal
```

## 3. The player

**State** `{tape, regs, ip, ticks}`. The genome is copied to `tape[0:len]`; the rest is zero
(NOP). Execution fetches `(op, a, b, c)` at `tape[ip..ip+4]`, `ip` advancing by 4 modulo
`tape_words`, so control falls off the genome into NOPs and wraps to 0. Jumps are relative, in
instructions, signed, modulo the tape.

**Tick.** The operator supplies input channels (lists of words), an output channel count, an
externally seeded random stream, and optionally a lower op budget. The player runs until `HALT`
(ip resets), `YIELD` (ip persists) or budget exhaustion (ip resets), returning the outputs and
the status. Input cursors are tick-scoped. At the next tick boundary the persist policy decides
what survives: `none` resets tape and registers to the genome, `regs` keeps registers, `tape`
keeps the tape, `all` keeps both.

**Self-modification.** `ST` into the genome region writes if `code_writable`, else is ignored.
Whether an organism rewrites itself is therefore an axis, and the meter counts such writes as the
declared proxy for "adaptation expenditure". No other plasticity mechanism exists; if plasticity
matters, it must be assembled from writes.

**Resources** are a vector (`Meter.as_dict`): ops, ops by class, code-region writes, branches
taken, channel reads/writes/drops, random draws, wall and CPU seconds, GPU `unavailable`, ticks,
budget-exhausted ticks, footprint words, persistent-state words. There is no fitness field and
the two brief-mandated quantities that are not mechanically separable in this machine (search
and adaptation expenditure) are reported as named proxies.

## 4. Identity and immutability

- `organism_id = sha256(canonical manifest)`; `lineage_id` = the root's id; generation counts descents.
- `record_id = sha256(lineage record)`; records carry parent ids, mutation seed, exact operators
  with arguments, pre/post hashes, state-inheritance policy, resource budget, runtime and grammar
  hashes. Records are appended, never edited.
- `checkpoint_id = sha256(organism, encounter, tick, state)`; `restore()` refuses any checkpoint
  taken under a different runtime hash.
- `encounter_identity(organisms, world_binding, seed, checkpoints)` is the id SFE observations
  bind to (A9). Proteus mints it and nothing else about an encounter.
- The failure ledger is hash-chained; a death is a row with its cost, not a dropped candidate.
- The runtime hash is computed over LF-normalised source so a CRLF checkout does not fork identity.

## 5. What the Foundry measures, and what it refuses to

Measured: `probe_transcript_equivalence` and the knockout-sensitivity vector, both on frozen noise
derived from a public hash, under a fixed budget. Preserved: the genotype-to-class map with
lineage and ancestry (A7). Refused: any score, any ranking, any label of interest. The word
"fitness" does not occur in the runtime, the meter, or the exports.

## 6. Known limits, declared

- **Static reachability is approximate under self-modification.** `unreachable_removal` uses the
  initial tape; a writable genome may reach code the analysis calls dead. The operator records
  `approx: true` when `code_writable`.
- **Opcode prior.** `op = word mod 25` gives opcode 0..6 a relative frequency of
  (1 + 2^-32·…) — negligible but non-zero — over 7..24 because 2^32 mod 25 ≠ 0. Published here so
  it is not discovered later.
- **Uniform initialisation** produces many organisms that halt or spin before emitting anything.
  That is a fact about the initial distribution, not a defect; V0 does not shape it (A8).
- **The ensemble is small** (4 probes). Transcript equivalence on 4 probes is coarser than on 40;
  the ensemble size is part of the frozen configuration identity and is not tuned after the fact.
- **No multiplayer semantics in the runtime.** Other players are channels the operator wires
  (`contracts/WORLD_INTERFACE.md` §4). Nothing in the player knows a channel is another player.
