"""NPE register-reset world axis (operator ruling ARC3, 2026-09-28).

CARRIED is the DEFAULT NPE world: organisms keep their registers across executions (and a replication event leaves the
overwritten organism's registers in place). Every other policy is an explicit, declared experimental/environmental
condition applied to BOTH organisms immediately before every pair interaction:

    CARRIED        no change (identity; the default world; historical results were produced here)
    ZERO           registers = None (z8 treats None as all zeros), flags 0
    CONST:<hex>    all 8 register bytes = <hex byte> (e.g. CONST:5A), flags 0
    RANDOM         all 8 register bytes and both flags drawn uniformly from a per-run RNG (never the world's RNG)
    PATTERN:<16hex> the 8 register bytes given explicitly (B C D E H L (HL) A), flags 0
    SCHEDULE       ZERO applied with probability p(epoch) given by a callable, else CARRIED (gradual withdrawal of the zero
                   scaffold; use with_schedule(), the draw comes from a per-run RNG, never the world's)

Historical results are NOT rewritten: earlier experiments' runners stay as they were (e.g. W1 X-DD-STATELESS = ZERO,
P2 X-P2-REGSTATE = CARRIED/ZERO/CONST:5A/RANDOM); this module only makes the axis explicit for new work.

    from reset_axis import with_reset, selftest
    Runner = with_reset(run_ds.runner_cls(world), "CONST:5A", prng=random.Random(seed))
"""
from __future__ import annotations

import random


def parse(policy: str):
    p = policy.upper()
    if p in ("CARRIED", "ZERO", "RANDOM"):
        return p, None
    if p.startswith("CONST:"):
        return "CONST", int(p.split(":", 1)[1], 16) & 0xFF
    if p.startswith("PATTERN:"):
        h = p.split(":", 1)[1]
        assert len(h) == 16, "PATTERN needs 8 bytes (16 hex digits)"
        return "PATTERN", [int(h[i:i + 2], 16) for i in range(0, 16, 2)]
    raise ValueError("unknown reset policy %r" % policy)


def vector(policy: str, prng: random.Random | None):
    """The (regs, fz, fc) an organism enters an interaction with under `policy` (None for CARRIED)."""
    kind, arg = parse(policy)
    if kind == "CARRIED":
        return None
    if kind == "ZERO":
        return (None, 0, 0)
    if kind == "CONST":
        return ([arg] * 8, 0, 0)
    if kind == "PATTERN":
        return (list(arg), 0, 0)
    assert prng is not None, "RANDOM needs a per-run RNG separate from the world's"
    return ([prng.randrange(256) for _ in range(8)], prng.randrange(2), prng.randrange(2))


def with_reset(base_cls, policy: str, prng: random.Random | None = None):
    """Subclass `base_cls` (a world.Runner or an ATOMIC runner) so every pair interaction applies `policy`."""
    kind, _ = parse(policy)
    if kind == "CARRIED":
        return base_cls

    class Reset(base_cls):
        reset_policy = policy

        def _pair_interact(self, i, a, b):
            for o in (a, b):
                o.regs, o.fz, o.fc = vector(policy, prng)
            return super()._pair_interact(i, a, b)
    Reset.__name__ = "Reset_" + kind
    return Reset


def selftest(world, base_cls, cell: dict, tier: str) -> tuple[bool, dict]:
    """Fail/pass: under each policy, the register vector z8.run first sees in an interaction equals the policy's vector
    (CARRIED: the organism's own carried vector)."""
    out = {}
    for pol in ("CARRIED", "ZERO", "CONST:5A", "PATTERN:0102030405060708", "RANDOM"):
        prng = random.Random(1)
        r = with_reset(base_cls, pol, prng)(dict(cell), 1, tier=tier)
        r.t["epochs"] = 0
        r.run()
        x, y = [o for o in r.orgs if o.alive][:2]
        x.regs, x.fz, x.fc = [7] * 8, 1, 1
        seen = []
        orig = world.z8.run

        def spy(ctx, pc, budget, ops_enabled=0xFF):
            seen.append([0] * 8 if ctx.regs is None else list(ctx.regs))
            return orig(ctx, pc, budget, ops_enabled)
        world.z8.run = spy
        try:
            r._pair_interact(0, x, y)
        finally:
            world.z8.run = orig
        v = seen[0]
        expect = {"CARRIED": [7] * 8, "ZERO": [0] * 8, "CONST:5A": [0x5A] * 8,
                  "PATTERN:0102030405060708": [1, 2, 3, 4, 5, 6, 7, 8]}.get(pol)
        out[pol] = (v == expect) if expect is not None else (v not in ([7] * 8, [0] * 8, [0x5A] * 8))
    return all(out.values()), out


def with_schedule(base_cls, p_of_epoch, prng: random.Random):
    """ZERO reset with probability p_of_epoch(epoch) per organism per interaction; otherwise the carried state is kept."""

    class Sched(base_cls):
        reset_policy = "SCHEDULE"

        def _pair_interact(self, i, a, b):
            p = p_of_epoch(self.epoch)
            for o in (a, b):
                if prng.random() < p:
                    o.regs, o.fz, o.fc = None, 0, 0
            return super()._pair_interact(i, a, b)
    return Sched
