# W2-7 implementation sketches against the campaign world (not applied; no world run)

These are the edits a future bounded in-world test would make. All are source injections in the `run_dc.dense_z8()`
style: read the campaign file as text, assert the anchor occurs exactly once, replace, then exec into a fresh module.
VM-level variants need no world edit, because `world.z8` is a module global (`world.z8 = alien_vm.build(NAME)`). The
world's P-11 call (`p11.assay(z8, ...)`) then inherits the VM, so ruler and world share the same physics.

**Layout-level variants must edit both `world.Runner._pair_interact` and `p11.interact`.** The P-11 ruler re-executes
every candidate event. If only the world is edited, the ruler certifies events under stock physics, so it measures a
different world from the one that produced them. The per-interaction draw (r, side order, registers) must be stored
in `st0` / `kw` and replayed inside `p11.interact`.

## VM level (`world.z8 = alien_vm.build(NAME)`; P-11 inherits it)

| variant | z8.py anchor (exactly once) | replacement |
|---|---|---|
| NOBLOCK | LDIR branch after its ops-mask gate | `_HITS[0] += 1; continue` (the op is a same-length no-op; ED B0 still consumes 2 bytes, E5 1) |
| EXPLEN | `if n == 0:\n n = 0x10000` | `if n == 0: _HITS[0] += 1` (zero count copies zero bytes; HL/DE/BC/Z updated as before) |
| NOWRAP | `rd` (data path only) and `wr` | data address `a = addr & 0xFFFF`; `a >= size` reads 0, and the write is dropped (counted in `writes_blocked`); code fetch still wraps |
| HARV_HALT | `pc = pc & mask ...; op = mem[pc]` | if pc is outside `[base, base+len)`: stop, as HALT does |
| HARV_WRAP | same anchor | `pc = base + (pc - base) % len` |
| BLOCK_OWN | `wr(dst, v)` inside the LDIR loop | write only if `dst` is in the executing context's own half; otherwise blocked |
| AOFF | `__slots__`, `__init__`, `rd`/`wr` data path, `JP` target, `SELF` result | `eff = addr + ctx.aoff`; `JP n -> n + aoff`; `SELF -> HL = base - aoff` |
| SELFCOPY | the dense alias map, plus a branch before LDIR | E5/E7 map to an unreadable op2 (0x1F5). That branch copies own `[base, base+len)` to `[base+len, ...)`, one step per byte, with copy mutation as in LDIR, and leaves the registers untouched |

`alien_vm.py` in this folder is the working implementation of every row. `selftest.py` T2 shows each variant is
bit-identical to the dense VM on every execution where `_HITS == 0`.

## Layout level (world and P-11 together)

```python
# world.Runner._pair_interact, after `ga, gb = ...`:
#   RING192    tape = bytearray(192)    (instead of _pow2(2 * n)). P-11 already receives tape_len=len(tape) from kw.
#              ONE-LINE world edit; p11.interact needs none.
#   ROTATE     r = self.rng.randrange(128); every ctx gets ctx.aoff = -r (AOFF vm); st0 += (r,);
#              p11.interact(..., r) sets ctx.aoff = -r for both the main run and the donor-disabled control.
#   RELADDR    ctx.aoff = start (AOFF vm), in world and p11.interact alike.
#   SIDERAND   order = [(0, 0, a), (1, n, b)]; if self.rng.random() < .5: order.reverse(); store the swap
#              bit in st0 and replay it in p11.interact.
#   REGRAND    before each ctx: org.regs = [rng.randrange(256) for _ in range(8)]; org.fz, org.fc = rng bits;
#              st0 is captured AFTER this assignment, so P-11 replays the same random entry state.
# Newborn-register rule (world only; the static screen cannot see it):
#   VE-RAND    in the birth branch (`org.pid, org.anc, org.oid = ...`): org.regs = random 8 bytes, flags random.
#   VE-RESET   at the top of _pair_interact: a.regs = b.regs = None; a.fz = a.fc = b.fz = b.fc = 0.
#              Its static screen is IDENTICAL to stock, because the screen already uses fresh state.
```

For the ATOMIC runner (`run_ds.runner_cls`), `_pair_interact` calls `super()._pair_interact`, so the world edit is
inherited and no second edit is needed.
