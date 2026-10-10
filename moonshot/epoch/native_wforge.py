"""The native wforge epoch runtime, moonshot.native.wforge v1 (C-012-T007; design v0.3 s8: primary substrate).

An epoch advances ONE wforge Encounter -- the world wforge's grammar expands from a genome -- by ticks_per_epoch ticks
under a fixed deterministic policy, from a checkpoint that captures the Encounter's ENTIRE state (registers, charge,
liveness, pending writes, observation history, counters and both xorshift streams) to the next one. Chained epochs
therefore equal one monolithic run of the same world tick for tick (tested), which is what R-RUNTIME asks of a native
checkpoint. wforge's own running trace hash is not carried: Moonshot's TRACE (one canonical line per tick: tick,
registers, charge, liveness, pending writes) and the R-EP lineage are the record.

Spec params (all canonical): genome (wforge payload), world_id (must be the genome's), episode_seed, ticks_per_epoch,
policy {"name": "affordable-seeded", "version": 1, "seed"}, wforge_world_sha256 (the wforge implementation the epoch
ran: world.py + genome.py, LF-normalised; a different implementation is REFUSED, so a repaired wforge is a different
spec and a different work identity).

Policy affordable-seeded v1: for each live slot, wforge's own stream function keyed by (policy seed, world id, episode
seed, tick, slot) draws: on one tick in four, an action of magnitude 1..3 on one channel, else abstention; if the
action's cost exceeds the slot's charge, the slot abstains. Frugal by design, so a world lives long enough for its
epochs to carry ticks (a policy acting on every channel every tick drained every surveyed world within ~10 ticks).
It is stateless, and it never issues an unaffordable action -- wforge's F09 path (unaffordable actions
queue unpaid writes) is never exercised, so these epochs do not depend on that defect. It is plumbing, not an
organism: no survival search runs on it (OP-NF2).
"""
import hashlib
import sys
from pathlib import Path

from .canonical import canonical_bytes, parse_canonical

NATIVE_WFORGE_V1 = {"name": "moonshot.native.wforge", "version": 1}
POLICY_NAME, POLICY_VERSION = "affordable-seeded", 1
CHECKPOINT_SCHEMA = "moonshot.native.wforge.checkpoint.v1"
_WFORGE = Path(__file__).resolve().parents[2] / "SerendipityFoundry" / "worldfoundry"
_PARAMS = ("episode_seed", "genome", "policy", "ticks_per_epoch", "wforge_world_sha256", "world_id")
_LISTS = ("regs", "charge", "alive", "yield_events", "actions_used", "abstained")


def _wforge():
    if str(_WFORGE) not in sys.path:
        sys.path.insert(0, str(_WFORGE))
    from wforge import genome as G
    from wforge import world as W
    return G, W


def world_sha256():
    """sha256 over wforge's world.py then genome.py, each LF-normalised (identical on every OS)."""
    h = hashlib.sha256()
    for name in ("world.py", "genome.py"):
        raw = (_WFORGE / "wforge" / name).read_bytes().replace(b"\r\n", b"\n")
        h.update(name.encode() + b"\x00" + str(len(raw)).encode() + b"\x00" + raw)
    return h.hexdigest()


def genome_from(payload):
    G, _ = _wforge()
    return G.WorldGenome(grammar_version=payload["grammar_version"], generation_seed=payload["generation_seed"],
                         parent_ids=tuple(payload.get("parent_ids") or ()),
                         mutation_history=tuple(G.MutationOp(**m) for m in payload.get("mutation_history") or ()))


def genesis_params(genome, *, episode_seed, ticks_per_epoch, policy_seed):
    return {"genome": genome.payload(), "world_id": genome.world_id, "episode_seed": episode_seed,
            "ticks_per_epoch": ticks_per_epoch,
            "policy": {"name": POLICY_NAME, "version": POLICY_VERSION, "seed": policy_seed},
            "wforge_world_sha256": world_sha256()}


def _check(p):
    if not isinstance(p, dict) or sorted(p) != list(_PARAMS):
        raise ValueError("native wforge params must be exactly {}".format(_PARAMS))
    if p["wforge_world_sha256"] != world_sha256():
        raise ValueError("this wforge ({}) is not the implementation the spec names ({})".format(
            world_sha256()[:12], str(p["wforge_world_sha256"])[:12]))
    if genome_from(p["genome"]).world_id != p["world_id"]:
        raise ValueError("world_id is not the genome's")
    t = p["ticks_per_epoch"]
    if isinstance(t, bool) or not isinstance(t, int) or t < 1:
        raise ValueError("ticks_per_epoch must be a positive integer")
    pol = p["policy"]
    if not isinstance(pol, dict) or sorted(pol) != ["name", "seed", "version"] or \
            (pol["name"], pol["version"]) != (POLICY_NAME, POLICY_VERSION) or not isinstance(pol["seed"], int):
        raise ValueError("unknown policy {}".format(pol))
    return p


def _fresh(p):
    _, W = _wforge()
    return W.Encounter(W.expand(genome_from(p["genome"])), p["world_id"], p["episode_seed"])


def capture(enc):
    """The Encounter's entire state as a canonical object."""
    return {"schema": CHECKPOINT_SCHEMA, "world_id": enc.world_id, "episode_seed": enc.seed, "tick": enc.tick,
            "regs": list(enc.regs), "charge": list(enc.charge), "alive": list(enc.alive),
            "pending": [list(x) for x in enc.pending], "history": [list(h) for h in enc.history],
            "yield_events": list(enc.yield_events), "actions_used": list(enc.actions_used),
            "abstained": list(enc.abstained), "s_stoch": enc._s_stoch.s, "s_corrupt": [x.s for x in enc._s_corrupt]}


def state_of(obj):
    """A comparable form of a captured state."""
    return canonical_bytes(obj)


def initial_checkpoint(p):
    return canonical_bytes(capture(_fresh(_check(p))))


def restore(p, checkpoint):
    """An Encounter in exactly the state the checkpoint captured; a checkpoint of another world is refused."""
    try:
        o = parse_canonical(checkpoint)
    except Exception as e:
        raise ValueError("checkpoint is not canonical: {}".format(e))
    if not isinstance(o, dict) or o.get("schema") != CHECKPOINT_SCHEMA:
        raise ValueError("not a native wforge checkpoint")
    if (o.get("world_id"), o.get("episode_seed")) != (p["world_id"], p["episode_seed"]):
        raise ValueError("checkpoint of world {} episode {}, spec names {} episode {}".format(
            o.get("world_id"), o.get("episode_seed"), p["world_id"], p["episode_seed"]))
    enc = _fresh(p)
    m = enc.m
    shapes = {"regs": m.n_regs, "charge": m.n_slots, "alive": m.n_slots, "yield_events": m.n_slots,
              "actions_used": m.n_slots, "abstained": m.n_slots}
    for k in _LISTS:
        if not isinstance(o.get(k), list) or len(o[k]) != shapes[k]:
            raise ValueError("checkpoint field {} has the wrong shape".format(k))
        setattr(enc, k, list(o[k]))
    if len(o.get("s_corrupt") or []) != m.n_slots:
        raise ValueError("checkpoint s_corrupt has the wrong shape")
    enc.tick = o["tick"]
    enc.pending = [tuple(x) for x in o["pending"]]
    enc.history = [list(h) for h in o["history"]]
    enc._s_stoch.s = o["s_stoch"]
    for x, s in zip(enc._s_corrupt, o["s_corrupt"]):
        x.s = s
    return enc


def policy_actions(p, mech, enc):
    _, W = _wforge()
    out = []
    for s in range(mech.n_slots):
        r = W.stream("moonshot.policy.affordable-seeded.v1", p["policy"]["seed"], p["world_id"], p["episode_seed"],
                     enc.tick, s)
        a = [0] * mech.act_width
        if r.below(4) == 0:
            a[r.below(mech.act_width)] = 1 + r.below(3)
        if not enc.alive[s] or sum(a) * mech.act_cost > enc.charge[s]:
            a = [0] * mech.act_width                                      # abstain: never an unaffordable action
        out.append(a)
    return out


def trace_line(enc):
    """One canonical line per tick. It includes every slot's observation, so the observation history and the
    corruption streams -- which only observe() reads -- are part of what checkpoint conformance checks (the
    observation is read once per slot per tick, a fixed consumption pattern)."""
    obs = [enc.observe(s) for s in range(enc.m.n_slots)]
    return canonical_bytes({"tick": enc.tick, "regs": list(enc.regs), "charge": list(enc.charge),
                            "alive": list(enc.alive), "pending": len(enc.pending), "obs": obs}) + b"\n"


def run_native_wforge_v1(input_checkpoint, spec):
    """(input checkpoint, spec) -> (trace, output checkpoint). Refusals raise ValueError."""
    p = _check(spec.get("params"))
    enc = restore(p, input_checkpoint)
    mech = enc.m
    lines = []
    for _ in range(p["ticks_per_epoch"]):
        if enc.tick >= mech.horizon or not any(enc.alive):
            break                                                       # a finished world stays finished
        enc.step(policy_actions(p, mech, enc))
        lines.append(trace_line(enc))
    return b"".join(lines), canonical_bytes(capture(enc))
