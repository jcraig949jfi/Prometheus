"""Tasks: cycle 8's accessibility topology, carried into the byte substrate.

WHAT A TASK IS HERE. A task is NOT a fitness function that copies organisms. Competence
gates INTERACTION OPPORTUNITY, resources, or metabolism, depending on the pressure
factor; reproduction remains whatever the reproduction-physics factor says it is. That
separation is the campaign's core principle, so it is enforced structurally: task
evaluation runs in a scratch arena with the world ops DISABLED, so an organism cannot
produce a descendant while being scored, and cannot touch the soup it came from.

THE TASK FAMILY. Cycle 8's conditional transform, in bytes: an organism is shown a value
and a regime and must answer v under regime 0 and T(v) under regime 1. Cycle 8 measured
why that is unreachable from an identity plateau; every knob that measurement identified
is a factor here:

  read_order  ANSWER_BEFORE_READ  the value arrives first, so 'echo the first byte' scores
                                  .5 without ever reading the regime - the moat that made
                                  the conditional 4 edits away across a valley of zero.
              FORCED_READ         the answer in BOTH regimes depends on a key byte that
                                  only exists in the input, so the plateau scores ~0 and
                                  the first step toward reading is itself rewarded.
  constants   ATOMIC              T is XOR K for an awkward K: the witness needs that exact
                                  literal byte, which uniform mutation supplies at 1/256
                                  per draw (and cycle 8's 32-bit version at 2^-32).
              INCREMENTAL         T is INC-reachable (ADD 1, or XOR 1): expressible with no
                                  literal at all, or one INC away from a byte already held.
  edits       ONE_EDIT            the ancestor already reads both inputs, so the conditional
                                  is one instruction away.
              MULTI_EDIT          the ancestor reads nothing; the read must be built first.
  bridge      NEUTRAL_BRIDGE      partial credit for echoing the right base answer, so the
                                  intermediate is not lethal.
              VALLEY              all-or-nothing, the cycle 8 condition.

HELD-OUT EPISODES. Episodes are redrawn from a fresh seed every evaluation, and a
held-out set from a disjoint seed stream scores the same organism. An organism that
scores high on one and at chance on the other is exploiting deterministic inputs, which
anticheat.py flags rather than silently patching.

Computational scope: integer programs on a bounded virtual machine.
"""
from __future__ import annotations

import random

import z8

VMAX = 256

# transform levels: name -> (constant, kind)
TRANSFORMS = {
    "XOR1": (0x01, "INCREMENTAL"),
    "ADD1": (0x01, "INCREMENTAL"),
    "XOR15": (0x0F, "ATOMIC"),
    "XOR5A": (0x5A, "ATOMIC"),
    "ADD37": (0x25, "ATOMIC"),
}

READ_ORDERS = ("ANSWER_BEFORE_READ", "FORCED_READ")
BRIDGES = ("VALLEY", "NEUTRAL_BRIDGE")


class TaskSpec:
    __slots__ = ("transform", "read_order", "bridge", "n_episodes", "budget", "neutral",
                 "output_gate", "cue_cost")

    def __init__(self, transform="XOR1", read_order="ANSWER_BEFORE_READ", bridge="VALLEY",
                 n_episodes=8, budget=120, neutral=False,
                 output_gate="UNRESTRICTED", cue_cost="VM"):
        self.transform = transform
        self.read_order = read_order
        self.bridge = bridge
        self.n_episodes = n_episodes
        self.budget = budget
        self.neutral = neutral
        # H1 intervention. NEITHER of these changes the task. `episodes()` produces the
        # same inputs and the same expected answers whatever they are set to, which is
        # the whole point: the predecessor's read_order factor could not serve as an
        # intervention because FORCED_READ sets base = v XOR key and passes a
        # three-element input vector, so its two arms score different targets.
        #   output_gate  UNRESTRICTED  OUT always emits.
        #                GATED         OUT is discarded until the regime cue is consumed.
        #   cue_cost     VM            the organism must execute IN to consume the cue.
        #                FREE          the world delivers the cue without instruction cost.
        self.output_gate = output_gate
        self.cue_cost = cue_cost

    def as_dict(self):
        return {"transform": self.transform, "read_order": self.read_order, "bridge": self.bridge,
                "n_episodes": self.n_episodes, "budget": self.budget, "neutral": self.neutral,
                "output_gate": self.output_gate, "cue_cost": self.cue_cost,
                "constant_kind": TRANSFORMS[self.transform][1]}

    def cue_index(self):
        """Position of the regime cue in the input vector. It is always last."""
        return 2 if self.read_order == "FORCED_READ" else 1


def spec_from_cell(cell, n_episodes=8, budget=140):
    """The one place a grammar cell becomes a task. Both the engine and the post-run
    assays call this, so a task cannot mean one thing while it runs and another when it
    is assayed."""
    return TaskSpec(transform=("XOR1" if cell["task_transform"] == "NEUTRAL" else cell["task_transform"]),
                    read_order=cell["read_order"], bridge=cell["bridge"],
                    n_episodes=n_episodes, budget=budget,
                    neutral=(cell["task_transform"] == "NEUTRAL"))


def apply_transform(name, v):
    k, _ = TRANSFORMS[name]
    if name.startswith("XOR"):
        return (v ^ k) & 0xFF
    return (v + k) & 0xFF


def episodes(spec, seed, n=None):
    """n episodes as (inputs, expected, base_answer). base_answer is the regime-0 answer,
    used only by the NEUTRAL_BRIDGE partial credit."""
    rng = random.Random(seed)
    n = n or spec.n_episodes
    out = []
    for _ in range(n):
        v = rng.randrange(VMAX)
        r = rng.randrange(2)
        if spec.read_order == "FORCED_READ":
            key = rng.randrange(1, VMAX)
            base = (v ^ key) & 0xFF
            inputs = [v, key, r]
        else:
            base = v
            inputs = [v, r]
        exp = base if r == 0 else apply_transform(spec.transform, base)
        out.append((inputs, exp, base))
    return out


def score(mem_bytes, spec, eps, ops_enabled=0x00, arena_bits=9):
    """Run the organism's bytes on each episode in a fresh scratch arena.

    World ops are disabled by default: scoring cannot birth anything. Returns
    (score, telemetry) where telemetry carries the answer-before-read probe.
    """
    size = 1 << arena_bits
    n = len(mem_bytes)
    if n == 0 or n > size:
        return 0.0, {"reads_at_answer": -1, "answered": 0.0, "halted": 0.0, "ops": 0}
    correct = 0.0
    reads_at_answer = []
    answered = 0
    halted = 0
    ops = 0
    for inputs, exp, base in eps:
        mem = bytearray(size)
        mem[0:n] = mem_bytes
        # H1. The gate suppresses OUT until the cue has been consumed; FREE cue cost
        # pre-advances the input cursor past the cue and credits the read, so the
        # organism receives the cue without spending instructions on it. Under FREE the
        # gate is therefore already satisfied at entry, which is exactly the contrast
        # the design needs: gating with and without an execution price attached.
        ci = spec.cue_index()
        gate = (ci + 1) if spec.output_gate == "GATED" else 0
        ctx = z8.Ctx(mem, 0, n, policy=z8.OWN, inputs=inputs, out_gate_reads=gate)
        if spec.cue_cost == "FREE":
            # The world hands the cue over: its value is waiting in register C and the
            # read is credited, so the gate is already satisfied and no instructions
            # were spent. The input CURSOR is deliberately left at 0 - the organism can
            # still read v and the cue normally - so FREE removes the price of consuming
            # the cue without removing any information the VM arm has.
            ctx.regs = [0] * 8
            ctx.regs[1] = inputs[ci] & 0xFF if ci < len(inputs) else 0
            ctx.in_reads = ci + 1
        z8.run(ctx, 0, spec.budget, ops_enabled=ops_enabled)
        ops += ctx.ops
        halted += 1 if ctx.halted else 0
        if ctx.outputs:
            answered += 1
            a = ctx.outputs[0]
            if a == exp:
                correct += 1.0
            elif spec.bridge == "NEUTRAL_BRIDGE" and a == base:
                correct += 0.5           # the read-and-echo intermediate is not lethal
            reads_at_answer.append(ctx.in_reads_at_first_out)
    k = len(eps)
    tel = {"reads_at_answer": (sum(reads_at_answer) / len(reads_at_answer)) if reads_at_answer else -1,
           "answered": answered / k, "halted": halted / k, "ops": ops / k}
    return correct / k, tel


def competence(mem_bytes, spec, seed, n=None, held_seed=None):
    """Training score, held-out score (disjoint seed stream) and probes."""
    if spec.neutral:
        return {"comp": 0.0, "held": 0.0, "reads_at_answer": -1, "answered": 0.0, "neutral": True}
    tr = episodes(spec, seed, n)
    s, tel = score(mem_bytes, spec, tr)
    out = {"comp": s, "reads_at_answer": tel["reads_at_answer"], "answered": tel["answered"],
           "halted": tel["halted"], "ops": tel["ops"], "neutral": False}
    if held_seed is not None:
        h, _ = score(mem_bytes, spec, episodes(spec, held_seed, n))
        out["held"] = h
    else:
        out["held"] = s
    return out


# ---------------------------------------------------------------- instruments
# Hand-written programs. These are INSTRUMENTS and positive controls, never evidence of
# what evolution can find. Cycle 8's rule, carried forward verbatim in spirit.

def witness(spec, constant=None):
    """A verified conditional program for this task spec.

    `constant` overrides the transform's immediate byte. That is what makes the one-edit
    ancestor exact: assembling with 0 gives a program that is byte-identical to the
    witness except for a single operand byte, because XOR A,0 and ADD A,0 leave A
    unchanged. The distance from ancestor to witness is then literally one byte, and
    WHICH byte it must become is the atomic-versus-incremental constant factor.
    """
    k = TRANSFORMS[spec.transform][0] if constant is None else constant
    trans = ("XOR A,%d" % k) if spec.transform.startswith("XOR") else ("ADD A,%d" % k)
    if spec.read_order == "FORCED_READ":
        src = """
            IN
            LD B,A
            IN
            XOR B
            LD B,A
            IN
            CP 0
            JRZ emit
            LD A,B
            %s
            OUT
            HALT
        emit:
            LD A,B
            OUT
            HALT
        """ % trans
    else:
        src = """
            IN
            LD B,A
            IN
            CP 0
            JRZ emit
            LD A,B
            %s
            OUT
            HALT
        emit:
            LD A,B
            OUT
            HALT
        """ % trans
    code, _ = z8.asm(src)
    return code


def plateau(spec):
    """The identity plateau: echo the first input byte and stop.

    Under ANSWER_BEFORE_READ it scores .5 while reading exactly one byte - the cycle 8
    organism, in bytes. Under FORCED_READ the same program scores ~0, which is the point
    of that factor level.
    """
    code, _ = z8.asm("""
        IN
        OUT
        HALT
    """)
    return code


def reader_ancestor(spec):
    """The ONE_EDIT ancestor: the witness with its transform constant set to zero.

    It reads every input, branches on the regime, and applies a transform that does
    nothing - so it scores exactly what the plateau scores, while sitting ONE OPERAND
    BYTE from the conditional program. Cycle 8 measured a four-edit valley from the
    plateau; this is the deliberate contrast, and the campaign asks what the rest of the
    physics does to a distance that is already one.
    """
    return witness(spec, constant=0)


def one_edit_distance(spec):
    """(bytes differing, the index and required value of the byte) between ancestor and
    witness. Recorded in every run config so the accessibility claim is checkable."""
    a, w = reader_ancestor(spec), witness(spec)
    if len(a) != len(w):
        return {"differs": -1, "index": None, "needs": None}
    idx = [i for i, (x, y) in enumerate(zip(a, w)) if x != y]
    return {"differs": len(idx), "index": idx[0] if idx else None,
            "needs": w[idx[0]] if idx else None,
            "from": a[idx[0]] if idx else None}
