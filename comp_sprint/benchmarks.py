"""Two-stratum benchmark suite for Track 3B-Boolean (Stratum 1 Structured + Stratum 2 Procedural).

Frozen splits:
  - Stratum 1 (Structured real combinational/arithmetic/crypto targets):
      * dev_structured     : 10 targets (4..6 inputs, 2..6 outputs)
      * holdout_structured : 10 targets (4..6 inputs, 2..6 outputs) -- distinct families
  - Stratum 2 (100% Procedural, ZERO LLM involvement):
      * dev_proc_shared    : 10 random shared-cone 5-6 in, 3-4 out DAGs
      * holdout_proc_shared: 10 random shared-cone 5-6 in, 3-4 out DAGs (disjoint seed)
      * holdout_proc_rand  : 10 pure uniform random 5-in, 3-out truth tables (anti-prior control)

Every task is deterministically generated from pure code + fixed seed and sealed by SHA-256.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple

from comp_sprint.circuit import Gate, StrashBuilder, XAGCircuit, full_mask


@dataclass(frozen=True)
class BenchmarkTask:
    task_id: str
    stratum: str  # "structured" | "proc_shared" | "proc_random"
    split: str    # "dev" | "holdout"
    n_inputs: int
    targets: Tuple[int, ...]
    description: str
    hidden_witness_gates: int | None = None  # Only set for procedural shared-cone; NEVER shown to learner

    @property
    def n_outputs(self) -> int:
        return len(self.targets)

    def public_dict(self) -> Dict[str, object]:
        return {
            "task_id": self.task_id,
            "stratum": self.stratum,
            "split": self.split,
            "n_inputs": self.n_inputs,
            "n_outputs": self.n_outputs,
            "targets_hex": [hex(t) for t in self.targets],
            "description": self.description,
        }

    def sha256(self) -> str:
        raw = json.dumps(self.public_dict(), sort_keys=True, separators=(",", ":")).encode("ascii")
        return hashlib.sha256(raw).hexdigest()


def _from_fn(n_inputs: int, n_outputs: int, fn: Callable[[int], Sequence[int]]) -> Tuple[int, ...]:
    tts = [0] * n_outputs
    for r in range(1 << n_inputs):
        outs = fn(r)
        assert len(outs) == n_outputs
        for h, bit in enumerate(outs):
            if bit & 1:
                tts[h] |= 1 << r
    return tuple(tts)


def _bits(val: int, width: int) -> List[int]:
    return [(val >> i) & 1 for i in range(width)]


# ---------------- Structured Real Combinational / Arithmetic / Crypto Targets ----------------

_PRESENT_SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
_PRINCE_SBOX  = [0xB, 0xF, 0x3, 0x2, 0xA, 0xC, 0x9, 0x1, 0x6, 0x7, 0x8, 0x0, 0xE, 0x5, 0xD, 0x4]
_GIFT_SBOX    = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9, 0x2, 0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]
_SKINNY_SBOX  = [0xC, 0x6, 0x9, 0x0, 0x1, 0xA, 0x2, 0xB, 0x3, 0x8, 0x5, 0xD, 0x4, 0xE, 0x7, 0xF]
_ASCON_SBOX   = [
    0x04, 0x0B, 0x1F, 0x14, 0x1A, 0x15, 0x09, 0x02,
    0x1B, 0x05, 0x08, 0x12, 0x1D, 0x03, 0x06, 0x1C,
    0x1E, 0x13, 0x07, 0x0E, 0x00, 0x0D, 0x11, 0x18,
    0x10, 0x0C, 0x01, 0x19, 0x16, 0x0A, 0x0F, 0x17,
]


def _keccak_chi5(x: int) -> List[int]:
    b = _bits(x, 5)
    return [b[i] ^ ((1 - b[(i + 1) % 5]) & b[(i + 2) % 5]) for i in range(5)]


def _popcount(x: int, n: int, out_w: int) -> List[int]:
    return _bits(bin(x & ((1 << n) - 1)).count("1"), out_w)


def _sort_bits(x: int, n: int) -> List[int]:
    c = bin(x & ((1 << n) - 1)).count("1")
    return [1 if i < c else 0 for i in range(n)]


def _gf16_mul_const(x: int, c: int) -> int:
    # GF(2^4) modulo x^4 + x + 1 (0x13)
    res = 0
    a = x & 0xF
    b = c & 0xF
    for _ in range(4):
        if b & 1:
            res ^= a
        hi = a & 0x8
        a = (a << 1) & 0xF
        if hi:
            a ^= 0x3
        b >>= 1
    return res


def _gf16_inv(x: int) -> int:
    # Multiplicative inverse in GF(2^4) / (x^4 + x + 1), with inv(0)=0
    if x == 0:
        return 0
    for y in range(1, 16):
        if _gf16_mul_const(x, y) == 1:
            return y
    raise RuntimeError("unreachable")


def build_structured_tasks() -> Tuple[List[BenchmarkTask], List[BenchmarkTask]]:
    """Return (dev_structured, holdout_structured), 10 targets each, distinct families."""
    dev = [
        BenchmarkTask(
            "s1_dev_add2", "structured", "dev", 4,
            _from_fn(4, 3, lambda r: _bits((r & 3) + ((r >> 2) & 3), 3)),
            "2-bit unsigned adder a+b",
        ),
        BenchmarkTask(
            "s1_dev_add2_cin", "structured", "dev", 5,
            _from_fn(5, 3, lambda r: _bits((r & 3) + ((r >> 2) & 3) + ((r >> 4) & 1), 3)),
            "2-bit unsigned adder with carry-in",
        ),
        BenchmarkTask(
            "s1_dev_mul2x2", "structured", "dev", 4,
            _from_fn(4, 4, lambda r: _bits((r & 3) * ((r >> 2) & 3), 4)),
            "2x2-bit unsigned multiplier",
        ),
        BenchmarkTask(
            "s1_dev_popcount5", "structured", "dev", 5,
            _from_fn(5, 3, lambda r: _popcount(r, 5, 3)),
            "5-bit population count",
        ),
        BenchmarkTask(
            "s1_dev_sort4", "structured", "dev", 4,
            _from_fn(4, 4, lambda r: _sort_bits(r, 4)),
            "4-bit sorting network (unary popcount)",
        ),
        BenchmarkTask(
            "s1_dev_cmp2", "structured", "dev", 4,
            _from_fn(4, 3, lambda r: [int((r & 3) < ((r >> 2) & 3)), int((r & 3) == ((r >> 2) & 3)), int((r & 3) > ((r >> 2) & 3))]),
            "2-bit magnitude comparator (<, =, >)",
        ),
        BenchmarkTask(
            "s1_dev_sbox_present", "structured", "dev", 4,
            _from_fn(4, 4, lambda r: _bits(_PRESENT_SBOX[r], 4)),
            "PRESENT 4-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_dev_sbox_gift", "structured", "dev", 4,
            _from_fn(4, 4, lambda r: _bits(_GIFT_SBOX[r], 4)),
            "GIFT 4-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_dev_keccak_chi5", "structured", "dev", 5,
            _from_fn(5, 5, _keccak_chi5),
            "Keccak / SHA-3 5-bit chi nonlinear layer",
        ),
        BenchmarkTask(
            "s1_dev_mux4_1bit_plus_par", "structured", "dev", 6,
            _from_fn(6, 2, lambda r: [((r >> ((r >> 4) & 3)) & 1), bin(r & 0xF).count("1") & 1]),
            "4-to-1 mux plus data parity",
        ),
    ]

    holdout = [
        BenchmarkTask(
            "s1_hold_add3", "structured", "holdout", 6,
            _from_fn(6, 4, lambda r: _bits((r & 7) + ((r >> 3) & 7), 4)),
            "3-bit unsigned adder a+b",
        ),
        BenchmarkTask(
            "s1_hold_sub2_bin", "structured", "holdout", 5,
            _from_fn(5, 3, lambda r: _bits(((r & 3) - ((r >> 2) & 3) - ((r >> 4) & 1)) & 7, 3)),
            "2-bit subtractor with borrow-in (2-bit diff + borrow)",
        ),
        BenchmarkTask(
            "s1_hold_mul3x2", "structured", "holdout", 5,
            _from_fn(5, 5, lambda r: _bits((r & 7) * ((r >> 3) & 3), 5)),
            "3x2-bit unsigned multiplier",
        ),
        BenchmarkTask(
            "s1_hold_popcount6", "structured", "holdout", 6,
            _from_fn(6, 3, lambda r: _popcount(r, 6, 3)),
            "6-bit population count",
        ),
        BenchmarkTask(
            "s1_hold_cmp3", "structured", "holdout", 6,
            _from_fn(6, 3, lambda r: [int((r & 7) < ((r >> 3) & 7)), int((r & 7) == ((r >> 3) & 7)), int((r & 7) > ((r >> 3) & 7))]),
            "3-bit magnitude comparator (<, =, >)",
        ),
        BenchmarkTask(
            "s1_hold_sbox_prince", "structured", "holdout", 4,
            _from_fn(4, 4, lambda r: _bits(_PRINCE_SBOX[r], 4)),
            "PRINCE 4-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_hold_sbox_skinny", "structured", "holdout", 4,
            _from_fn(4, 4, lambda r: _bits(_SKINNY_SBOX[r], 4)),
            "SKINNY 4-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_hold_sbox_ascon", "structured", "holdout", 5,
            _from_fn(5, 5, lambda r: _bits(_ASCON_SBOX[r], 5)),
            "ASCON 5-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_hold_gf16_inv", "structured", "holdout", 4,
            _from_fn(4, 4, lambda r: _bits(_gf16_inv(r), 4)),
            "GF(2^4) multiplicative inverse (x^4+x+1)",
        ),
        BenchmarkTask(
            "s1_hold_barrel_rot4", "structured", "holdout", 6,
            _from_fn(6, 4, lambda r: _bits((((r & 0xF) << ((r >> 4) & 3)) | ((r & 0xF) >> (4 - ((r >> 4) & 3)))) & 0xF, 4)),
            "4-bit barrel rotator by 2-bit shift",
        ),
    ]
    return dev, holdout


# ---------------- Procedural Zero-LLM Targets (Stratum 2) ----------------

def _sample_shared_cone_circuit(
    rng: random.Random,
    n_inputs: int,
    n_outputs: int,
    n_shared_core: int,
    n_head_per_out: int,
) -> XAGCircuit:
    """Sample a random multi-output XAG with guaranteed shared intermediate cones.

    Builds `n_shared_core` random gates over primary inputs, then for each output builds
    `n_head_per_out` gates that draw from BOTH the shared core and primary inputs.
    """
    builder = StrashBuilder(n_inputs)
    core_nodes: List[Tuple[int, bool]] = []
    pool: List[Tuple[int, bool]] = [(i, False) for i in range(n_inputs)]

    for _ in range(n_shared_core):
        op = rng.choice(("AND", "AND", "XOR"))
        (n1, i1), (n2, i2) = rng.sample(pool, 2)
        li = i1 ^ rng.choice((False, True))
        ri = i2 ^ rng.choice((False, True))
        node = builder.add_gate(op, n1, li, n2, ri)
        core_nodes.append(node)
        pool.append(node)

    outs: List[Tuple[int, bool]] = []
    for _ in range(n_outputs):
        local_pool = list(pool)
        cur = rng.choice(core_nodes)
        for _ in range(n_head_per_out):
            op = rng.choice(("AND", "AND", "XOR"))
            other = rng.choice([p for p in local_pool if p[0] != cur[0]])
            li = cur[1] ^ rng.choice((False, True))
            ri = other[1] ^ rng.choice((False, True))
            cur = builder.add_gate(op, cur[0], li, other[0], ri)
            local_pool.append(cur)
        outs.append((cur[0], cur[1] ^ rng.choice((False, True))))

    return builder.build(outs, prune_dead=True)


def build_procedural_tasks(
    dev_seed: int = 2026112201,
    holdout_shared_seed: int = 2026112202,
    holdout_rand_seed: int = 2026112203,
) -> Tuple[List[BenchmarkTask], List[BenchmarkTask], List[BenchmarkTask]]:
    """Return (dev_proc_shared[10], holdout_proc_shared[10], holdout_proc_rand[10])."""
    def gen_shared(seed: int, split: str, prefix: str, count: int) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        tasks: List[BenchmarkTask] = []
        idx = 0
        while len(tasks) < count:
            n_in = 5 if (len(tasks) < count // 2) else 6
            n_out = 3 if n_in == 5 else 4
            circ = _sample_shared_cone_circuit(
                rng, n_inputs=n_in, n_outputs=n_out, n_shared_core=9, n_head_per_out=4
            )
            tts = circ.truth_tables()
            mask = full_mask(n_in)
            n_rows = 1 << n_in
            # Reject degenerate, duplicate, constant, or near-constant/single-var outputs
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            # Require balanced-ish non-trivial outputs (Hamming weight between 20% and 80%)
            if any(not (0.20 * n_rows <= t.bit_count() <= 0.80 * n_rows) for t in tts):
                continue
            # Require every output to depend on at least 4 distinct inputs
            in_dep_ok = True
            for t in tts:
                deps = 0
                for v in range(n_in):
                    shift = 1 << v
                    # Check if flipping input v changes any output bit
                    m0 = sum(1 << r for r in range(n_rows) if not (r & shift))
                    if (t & m0) != ((t >> shift) & m0):
                        deps += 1
                if deps < 4:
                    in_dep_ok = False
                    break
            if not in_dep_ok or circ.gate_count() < 15:
                continue
            tasks.append(
                BenchmarkTask(
                    task_id=f"{prefix}_{idx:02d}_n{n_in}m{n_out}",
                    stratum="proc_shared",
                    split=split,
                    n_inputs=n_in,
                    targets=tts,
                    description=f"Procedural shared-cone DAG (seed={seed}, n={n_in}, m={n_out})",
                    hidden_witness_gates=circ.gate_count(),
                )
            )
            idx += 1
        return tasks

    dev_shared = gen_shared(dev_seed, "dev", "s2_dev_shared", 10)
    hold_shared = gen_shared(holdout_shared_seed, "holdout", "s2_hold_shared", 10)

    rng_r = random.Random(holdout_rand_seed)
    hold_rand: List[BenchmarkTask] = []
    for i in range(10):
        n_in = 5
        n_out = 3
        bits = 1 << n_in
        tts = tuple(rng_r.getrandbits(bits) for _ in range(n_out))
        hold_rand.append(
            BenchmarkTask(
                task_id=f"s2_hold_rand_{i:02d}_n{n_in}m{n_out}",
                stratum="proc_random",
                split="holdout",
                n_inputs=n_in,
                targets=tts,
                description=f"Pure uniform random 5-in 3-out truth table (seed={holdout_rand_seed})",
                hidden_witness_gates=None,
            )
        )

    return dev_shared, hold_shared, hold_rand


def build_all_benchmarks() -> Dict[str, List[BenchmarkTask]]:
    dev_s, hold_s = build_structured_tasks()
    dev_p, hold_p, hold_r = build_procedural_tasks()
    return {
        "dev_structured": dev_s,
        "holdout_structured": hold_s,
        "dev_proc_shared": dev_p,
        "holdout_proc_shared": hold_p,
        "holdout_proc_rand": hold_r,
    }


def manifest_sha256(suites: Dict[str, List[BenchmarkTask]]) -> str:
    payload = {
        k: [t.public_dict() for t in v]
        for k, v in sorted(suites.items())
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


# ---------------- Phase 2C Fresh Sealed Benchmark Suite (v2c, Zero Leakage) ----------------

_MIDORI_SB0   = [0xC, 0xA, 0xD, 0x3, 0xE, 0xB, 0xF, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6]
_RECTANGLE_SB = [0x6, 0x5, 0xC, 0xA, 0x1, 0xE, 0x7, 0x9, 0xB, 0x0, 0x3, 0xD, 0x8, 0xF, 0x4, 0x2]
_LBLOCK_S0    = [0xE, 0x9, 0xF, 0x0, 0xD, 0x4, 0xA, 0xB, 0x1, 0x2, 0x8, 0x3, 0x7, 0x6, 0xC, 0x5]
_SERPENT_S0   = [0x3, 0x8, 0xF, 0x1, 0xA, 0x6, 0x5, 0xB, 0xE, 0xD, 0x4, 0x2, 0x7, 0x0, 0x9, 0xC]
_PICCOLO_SB   = [0xE, 0x4, 0xB, 0x2, 0x3, 0x8, 0x0, 0x9, 0x1, 0xA, 0x7, 0xF, 0x6, 0xC, 0x5, 0xD]


def _gf16_cube(x: int) -> int:
    sq = _gf16_mul_const(x, x)
    return _gf16_mul_const(sq, x)


def _sample_alien_cells(motif_seed: int = 2026112300) -> List[XAGCircuit]:
    """Deterministically sample 3 non-human PRNG 3-in/2-out XAG micro-cells (ZERO LLM).

    Each cell has 3 inputs, 2 non-constant, non-linear, distinct outputs with 3..5 primitive
    XAG gates, non-zero AND count, and genuine shared internal gate(s) between its 2 outputs.
    """
    rng = random.Random(motif_seed)
    cells: List[XAGCircuit] = []
    seen_sigs = set()
    # Exclude standard Full Adder (sum=0x96, carry=0xe8) and trivial symmetric copies
    forbidden_tts = {0x96, 0x69, 0xE8, 0x17, 0x00, 0xFF}

    while len(cells) < 3:
        n_in = 3
        n_g = 4 if len(cells) < 2 else 5
        b = StrashBuilder(n_in)
        pool: List[Tuple[int, bool]] = [(i, False) for i in range(n_in)]
        for step in range(n_g):
            # Ensure strong nonlinear mixing (mostly AND + XOR)
            op = "AND" if (step in (0, 2) or rng.random() < 0.65) else "XOR"
            (u, ui), (v, vi) = rng.sample(pool, 2)
            nd = b.add_gate(op, u, ui ^ rng.choice((False, True)), v, vi ^ rng.choice((False, True)))
            pool.append(nd)
        gate_nodes = [p for p in pool if p[0] >= n_in]
        if len(gate_nodes) < 3:
            continue
        outs = [(n, inv ^ rng.choice((False, True))) for n, inv in rng.sample(gate_nodes[-3:], 2)]
        circ = b.build(outs, prune_dead=True)
        if not (3 <= circ.gate_count() <= 5) or circ.and_count() < 2:
            continue
        tts = circ.truth_tables()
        if len(set(tts)) < 2 or any(t in forbidden_tts for t in tts):
            continue
        # Require both outputs to depend on all 3 inputs and have balanced-ish weight (2..6 of 8)
        ok = True
        for t in tts:
            if not (2 <= t.bit_count() <= 6):
                ok = False
                break
            for v in range(3):
                sh = 1 << v
                m0 = sum(1 << r for r in range(8) if not (r & sh))
                if (t & m0) == ((t >> sh) & m0):
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue
        sig = tuple(sorted(min(t, t ^ 0xFF) for t in tts))
        if sig in seen_sigs:
            continue
        seen_sigs.add(sig)
        cells.append(circ)
    return cells


def _sample_compositional_circuit(
    rng: random.Random,
    cells: Sequence[XAGCircuit],
    n_inputs: int,
    n_outputs: int,
) -> XAGCircuit:
    """Build an Order-2 multi-layer circuit by wiring 2..3 instances of hidden PRNG `cells`
    across 2 layers plus small random glue gates (100% procedural, ZERO LLM)."""
    b = StrashBuilder(n_inputs)
    # Active wire pool: start with primary inputs
    wires: List[Tuple[int, bool]] = [(i, False) for i in range(n_inputs)]

    def apply_cell(cell: XAGCircuit, arg_wires: Sequence[Tuple[int, bool]]) -> List[Tuple[int, bool]]:
        cmap: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
        for idx_i, (wn, wi) in enumerate(arg_wires):
            cmap[idx_i] = (wn, wi ^ rng.choice((False, True)))
        for gi, g in enumerate(cell.gates):
            ln, li = cmap[g.left]
            rn, ri = cmap[g.right]
            cmap[cell.n_inputs + gi] = b.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)
        res = []
        for onode, oinv in cell.outputs:
            mn, mi = cmap[onode]
            res.append((mn, mi ^ oinv))
        return res

    # Layer 1: apply 2 disjoint/overlapping cell instances to primary inputs (reduces 5-6 wires -> 3-4!)
    perm_in = list(range(n_inputs))
    rng.shuffle(perm_in)
    c1 = rng.choice(cells)
    args1 = [wires[perm_in[0]], wires[perm_in[1]], wires[perm_in[2]]]
    out1 = apply_cell(c1, args1)

    rem_inputs = [wires[perm_in[j]] for j in range(3, n_inputs)]
    layer1_wires = rem_inputs + out1  # 4 wires if n_in=5, 5 wires if n_in=6

    # Layer 2: apply 1 or 2 more cell instances on top of layer1_wires (Order-2 composition!)
    c2 = rng.choice(cells)
    rng.shuffle(layer1_wires)
    args2 = layer1_wires[:3]
    out2 = apply_cell(c2, args2)
    layer2_wires = layer1_wires[3:] + out2  # 3 wires if n_in=5, 4 wires if n_in=6

    # Optional 3rd cell for 6-input targets to keep rich Order-2 depth
    if n_inputs >= 6 and len(layer2_wires) >= 3:
        c3 = rng.choice(cells)
        rng.shuffle(layer2_wires)
        out3 = apply_cell(c3, layer2_wires[:3])
        layer2_wires = layer2_wires[3:] + out3

    # Build n_outputs from layer2_wires + 1..2 light shared glue gates (preserving compositional bottleneck!)
    glue_pool = list(layer2_wires)
    for _ in range(2):
        if len(glue_pool) >= 2:
            op = rng.choice(("XOR", "AND"))
            (u, ui), (v, vi) = rng.sample(glue_pool, 2)
            glue_pool.append(b.add_gate(op, u, ui ^ rng.choice((False, True)), v, vi ^ rng.choice((False, True))))

    # Ensure every output comes strictly from the compressed layer2/glue bottleneck!
    cand_outs = glue_pool[-max(n_outputs, len(layer2_wires)):]
    if len(cand_outs) < n_outputs:
        cand_outs = glue_pool
    chosen = rng.sample(cand_outs, n_outputs)
    final_outs = [(n, inv ^ rng.choice((False, True))) for n, inv in chosen]
    return b.build(final_outs, prune_dead=True)


def build_benchmarks_v2c() -> Dict[str, List[BenchmarkTask]]:
    """Fresh sealed Phase 2C benchmark manifest (ZERO overlap with Phase 2B holdout!).

    Splits (76 tasks total):
      DEV (36 tasks; partitioned internally into 24 dev_train [0..7] + 12 dev_val [8..11]):
        - dev_structured  (12): 10 original dev_structured + 2 fresh (Serpent S0, Piccolo S-box)
        - dev_proc_shared (12): fresh uniform random shared-cone DAGs (seed=2026112311)
        - dev_proc_comp   (12): 100% procedural alien-motif compositional DAGs (seed=2026112313)
      UNTOUCHED HOLDOUT (40 brand-new tasks across 4 strata):
        - holdout_structured  (10): 10 brand-new arithmetic/crypto tasks never in Phase 2B
        - holdout_proc_shared (10): fresh uniform random shared-cone DAGs (seed=2026112321)
        - holdout_proc_comp   (10): fresh procedural alien-motif DAGs (disjoint seed=2026112323)
        - holdout_proc_rand   (10): fresh uniform random 5-in 3-out truth tables (seed=2026112325)
    """
    dev_s_base, _ = build_structured_tasks()
    dev_s = list(dev_s_base) + [
        BenchmarkTask(
            "s1_v2_dev_sbox_serpent0", "structured", "dev", 4,
            _from_fn(4, 4, lambda r: _bits(_SERPENT_S0[r], 4)),
            "SERPENT S0 4-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_v2_dev_sbox_piccolo", "structured", "dev", 4,
            _from_fn(4, 4, lambda r: _bits(_PICCOLO_SB[r], 4)),
            "PICCOLO 4-bit cryptographic S-box",
        ),
    ]

    hold_s = [
        BenchmarkTask(
            "s1_v2_hold_sub3", "structured", "holdout", 6,
            _from_fn(6, 4, lambda r: _bits(((r & 7) - ((r >> 3) & 7)) & 0xF, 4)),
            "3-bit unsigned subtractor a-b (3-bit diff + borrow)",
        ),
        BenchmarkTask(
            "s1_v2_hold_absdiff3", "structured", "holdout", 6,
            _from_fn(6, 3, lambda r: _bits(abs((r & 7) - ((r >> 3) & 7)), 3)),
            "3-bit unsigned absolute difference |a-b|",
        ),
        BenchmarkTask(
            "s1_v2_hold_max3", "structured", "holdout", 6,
            _from_fn(6, 3, lambda r: _bits(max(r & 7, (r >> 3) & 7), 3)),
            "3-bit unsigned maximum max(a,b)",
        ),
        BenchmarkTask(
            "s1_v2_hold_inc_dec4", "structured", "holdout", 5,
            _from_fn(5, 4, lambda r: _bits((((r & 0xF) + 1) if ((r >> 4) & 1) == 0 else ((r & 0xF) - 1)) & 0xF, 4)),
            "4-bit conditional increment/decrement mod 16",
        ),
        BenchmarkTask(
            "s1_v2_hold_sort5", "structured", "holdout", 5,
            _from_fn(5, 5, lambda r: _sort_bits(r, 5)),
            "5-bit sorting network (unary popcount)",
        ),
        BenchmarkTask(
            "s1_v2_hold_sbox_midori", "structured", "holdout", 4,
            _from_fn(4, 4, lambda r: _bits(_MIDORI_SB0[r], 4)),
            "MIDORI Sb0 4-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_v2_hold_sbox_rect", "structured", "holdout", 4,
            _from_fn(4, 4, lambda r: _bits(_RECTANGLE_SB[r], 4)),
            "RECTANGLE 4-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_v2_hold_sbox_lblock", "structured", "holdout", 4,
            _from_fn(4, 4, lambda r: _bits(_LBLOCK_S0[r], 4)),
            "LBLOCK S0 4-bit cryptographic S-box",
        ),
        BenchmarkTask(
            "s1_v2_hold_gf16_cube", "structured", "holdout", 4,
            _from_fn(4, 4, lambda r: _bits(_gf16_cube(r), 4)),
            "GF(2^4) cube x^3 mod (x^4+x+1)",
        ),
        BenchmarkTask(
            "s1_v2_hold_add3_sat", "structured", "holdout", 6,
            _from_fn(6, 3, lambda r: _bits(min(7, (r & 7) + ((r >> 3) & 7)), 3)),
            "3-bit saturating adder min(7, a+b)",
        ),
    ]

    # Fresh uniform random shared-cone DAGs + random truth tables (disjoint seeds from Phase 2B!)
    dev_sh, hold_sh, hold_rnd = build_procedural_tasks(
        dev_seed=2026112311,
        holdout_shared_seed=2026112321,
        holdout_rand_seed=2026112325,
    )
    # Add 2 more dev_proc_shared tasks to make 12 (8 train + 4 val)
    extra_sh, _, _ = build_procedural_tasks(
        dev_seed=2026112312,
        holdout_shared_seed=2026112399,
        holdout_rand_seed=2026112398,
    )
    dev_proc_shared = list(dev_sh) + [
        BenchmarkTask(
            task_id=f"s2_v2_dev_shared_{10 + i:02d}_n{t.n_inputs}m{t.n_outputs}",
            stratum=t.stratum, split="dev", n_inputs=t.n_inputs, targets=t.targets,
            description=t.description, hidden_witness_gates=t.hidden_witness_gates,
        )
        for i, t in enumerate(extra_sh[:2])
    ]

    # Procedural alien-motif compositional DAGs (ZERO LLM, hidden PRNG cells)
    alien_cells = _sample_alien_cells(motif_seed=2026112300)

    def gen_comp(seed: int, split: str, prefix: str, count: int) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        tasks: List[BenchmarkTask] = []
        idx = 0
        while len(tasks) < count:
            n_in = 5 if (len(tasks) % 2 == 0) else 6
            n_out = 3 if n_in == 5 else 4
            circ = _sample_compositional_circuit(rng, alien_cells, n_inputs=n_in, n_outputs=n_out)
            tts = circ.truth_tables()
            mask = full_mask(n_in)
            n_rows = 1 << n_in
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            if any(not (0.15 * n_rows <= t.bit_count() <= 0.85 * n_rows) for t in tts):
                continue
            # Require at least 4 inputs active on >= 2 outputs
            active_outs = 0
            for t in tts:
                deps = 0
                for v in range(n_in):
                    sh = 1 << v
                    m0 = sum(1 << r for r in range(n_rows) if not (r & sh))
                    if (t & m0) != ((t >> sh) & m0):
                        deps += 1
                if deps >= 4:
                    active_outs += 1
            if active_outs < 2 or circ.gate_count() < 10:
                continue
            tasks.append(
                BenchmarkTask(
                    task_id=f"{prefix}_{idx:02d}_n{n_in}m{n_out}",
                    stratum="proc_comp",
                    split=split,
                    n_inputs=n_in,
                    targets=tts,
                    description=f"Procedural compositional DAG (seed={seed}, n={n_in}, m={n_out})",
                    hidden_witness_gates=circ.gate_count(),
                )
            )
            idx += 1
        return tasks

    dev_comp = gen_comp(2026112313, "dev", "s2_v2_dev_comp", 12)
    hold_comp = gen_comp(2026112323, "holdout", "s2_v2_hold_comp", 10)

    return {
        "dev_structured": dev_s,
        "dev_proc_shared": dev_proc_shared,
        "dev_proc_comp": dev_comp,
        "holdout_structured": hold_s,
        "holdout_proc_shared": hold_sh,
        "holdout_proc_comp": hold_comp,
        "holdout_proc_rand": hold_rnd,
    }
