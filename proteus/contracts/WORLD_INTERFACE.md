# World-interface contract — the player ABI (V0). Amendments A1, and brief §10, §11.

**Scope.** This is the ONLY interface a player has to anything outside itself. It is generic and
semantics-free. Proteus implements the player side of it and nothing else: **no World-0 adapter,
no Ludus adapter, no binding of any kind.** Bindings belong to the neutral experiment operator
and the SFE-side integration layer, and a binding written by Proteus would be a firewall breach
by construction.

## 1. The ABI, exactly

```
Player(manifest)                         -> interpreter bound to one immutable manifest
player.fresh_state()                     -> {tape, regs, ip, ticks}          (PRISTINE start)
lineage.restore(checkpoint)              -> state                             (INHERIT start)
player.run_tick(state, inputs, n_out, rng, meter=None, budget=None)
        inputs : list of channels; each channel a list of 32-bit unsigned ints (may be empty)
        n_out  : number of output channels this tick (>= 0)
        rng    : SplitMix64 seeded by the OPERATOR; the player never seeds it
        budget : optional op cap for this tick; effective cap = min(budget, manifest.tick_budget)
        returns (outputs, status)
        outputs: list of n_out channels, each a list of <= out_cap 32-bit ints
        status : "halt" | "yield" | "budget"
lineage.checkpoint(organism_id, state, encounter_id, tick) -> content-addressed snapshot
```

Channel counts may differ per tick, per encounter, and per world. The player addresses channels
by `register value mod channel count`, so a genome written against two channels runs unchanged
against seven; whether it does anything useful there is the population's problem, not the ABI's.
This satisfies A1's requirement that channel number and shape vary without redesign.

## 2. What a player can and cannot know

A player receives: the values on its input channels this tick; how many are unread (INQ); an
externally seeded random word on demand; its own tape and registers. Nothing else.

A player never receives: a world identity, a tick number, a score, a budget remaining, the
existence or contents of other players, the meaning of any channel, or any string. If a world
wants a player to see a cost, a clock, or a reward-like quantity, the world puts a number on a
channel and the player sees a number. **Proteus assigns no semantics to any channel position.**

## 3. The boundary A1 draws, stated so it cannot be blurred

> An opaque vector whose positions have Proteus-authored semantic roles is NOT semantically
> sterile merely because the field names are hidden.

Accordingly, this contract defines **no channel layout**. There is no "channel 0 is the
observation, channel 1 is the reward". There is no fixed channel count. There is no
recommended shape. The binding layer decides what goes on which channel, and that decision is
recorded on the SFE side (`SFE_INTEGRATION.md` §3) as part of the encounter's world binding id,
so a later reader can see which layout a population was exposed to. If a future binding wants a
layout convention, it is the binding's convention, versioned and hashed on the binding side.

What Proteus DOES fix, because it is the machine and not the world: word width (32 bits), the
per-channel output cap, the tick-scoped input cursor, and the three status values. These are
properties of the tape machine, not of any world.

## 4. Multiplayer (brief §11)

The ABI has no notion of another player. Every encounter shape the brief lists is a wiring done
by the operator on top of `run_tick`:

- **one player**: inputs from the world only.
- **homogeneous / heterogeneous populations**: the operator runs N players (same or different
  manifests) per tick and may route some players' outputs into others' inputs on the next tick.
- **persistent opponents**: a player whose state persists across encounters (INHERIT from its
  own checkpoint) wired as a channel source for others.
- **transient opponents**: a PRISTINE player wired the same way and discarded afterwards.

No player can tell whether a channel is fed by the world, by another player, or by a recording.
Predator, prey, cooperation, deception, competition and communication are words the operator may
use in a write-up if such patterns appear in the ledger; none of them exists on the player side
and none may be added there.

## 5. Determinism and replay

Given (manifest, initial state, the per-tick inputs, n_out per tick, the rng seed, the budget),
`run_tick` is a pure function of its arguments and replays bit-exactly (`tests/test_replay.py`).
Wall and CPU time are recorded in the meter and are the only non-replayable quantities; they
are never inputs to anything.

## 6. Resource vector

`Meter.as_dict(manifest)` returns the vector in `ARCHITECTURE.md` §3. A binding forwards it to
SFE as an observation payload; it never collapses it into one number on the Proteus side.

## 7. What is deliberately absent

No reset-on-loss, no reward channel, no done flag, no observation schema, no action schema, no
episode boundary beyond the tick. Every one of those would be a Proteus-authored semantic role.
