"""A1 (INDUSTRY) baseline: Berkeley ABC wrapper with exact truth-table round-trip verification.

Converts any multi-output Boolean task (n_inputs, targets) to exact .pla, invokes
Berkeley ABC (`strash; dc2; resyn2; resyn2; dc2; resyn2; strash; write_bench`),
parses the resulting AIG back into `XAGCircuit`, verifies 100% truth-table equivalence,
and reports BOTH:
  - `abc_aig_gates`: exact ABC AIG node count (pure AND + free inversions)
  - `abc_xag_gates`: gate count after exact sound local 3-AND -> 1-XOR folding
                     so ABC gets full credit on XOR-heavy targets.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from comp_sprint.circuit import Gate, StrashBuilder, XAGCircuit, full_mask, verify_truth_tables

_SCRATCH_ABC = (
    Path(os.environ.get("USERPROFILE", r"C:\Users\jcrai"))
    / ".gemini" / "antigravity-cli" / "brain"
    / "1173311b-e2f8-4758-88bf-00243a26d849" / "scratch" / "abc_build" / "abc.exe"
)


def find_abc_binary(explicit: Optional[Path] = None) -> Path:
    candidates: List[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit))
    env_p = os.environ.get("PROMETHEUS_ABC_BIN")
    if env_p:
        candidates.append(Path(env_p))
    candidates.append(Path(__file__).resolve().parent / "bin" / "abc.exe")
    candidates.append(_SCRATCH_ABC)
    for name in ("abc", "abc.exe", "yosys-abc", "yosys-abc.exe"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    raise FileNotFoundError(
        "Berkeley ABC binary not found. Checked comp_sprint/bin/abc.exe, scratch/abc_build/abc.exe, and PATH."
    )


def write_pla(path: Path, n_inputs: int, targets: Sequence[int]) -> None:
    n_outs = len(targets)
    n_rows = 1 << n_inputs
    lines = [
        f".i {n_inputs}",
        f".o {n_outs}",
        ".ilb " + " ".join(f"x{i}" for i in range(n_inputs)),
        ".ob " + " ".join(f"y{h}" for h in range(n_outs)),
        f".p {n_rows}",
    ]
    for r in range(n_rows):
        in_bits = "".join(str((r >> i) & 1) for i in range(n_inputs))
        out_bits = "".join(str((targets[h] >> r) & 1) for h in range(n_outs))
        lines.append(f"{in_bits} {out_bits}")
    lines.append(".e")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


_ASSIGN_RE = re.compile(r"^\s*([A-Za-z0-9_.\[\]]+)\s*=\s*([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*$")
_LUT_RE = re.compile(r"^\s*([A-Za-z0-9_.\[\]]+)\s*=\s*LUT\s+0x([0-9a-fA-F]+)\s*\(([^)]*)\)\s*$")
_IO_RE = re.compile(r"^\s*(INPUT|OUTPUT)\s*\(\s*([A-Za-z0-9_.\[\]]+)\s*\)\s*$")


def _lut2_to_gate(builder: StrashBuilder, lut_hex: int, a: Tuple[int, bool], b: Tuple[int, bool]) -> Tuple[int, bool]:
    """Decode ABC 2-input LUT hex (bit index = (b << 1) | a: a is LSB, b is MSB) into 0 or 1 XAG gate."""
    h = lut_hex & 0xF
    if h == 0x0:
        return (-1, False)
    if h == 0xF:
        return (-1, True)
    if h == 0xA:  # a (bits 1,3 -> a=1)
        return a
    if h == 0x5:  # ~a
        return (a[0], not a[1])
    if h == 0xC:  # b (bits 2,3 -> b=1)
        return b
    if h == 0x3:  # ~b
        return (b[0], not b[1])
    # XOR / XNOR
    if h == 0x6:
        return builder.add_gate("XOR", a[0], a[1], b[0], b[1])
    if h == 0x9:
        n, i = builder.add_gate("XOR", a[0], a[1], b[0], b[1])
        return (n, not i)
    # 4 weight-1 AND polarities (and their 4 weight-3 negations)
    neg = False
    if bin(h).count("1") == 3:
        h ^= 0xF
        neg = True
    # Now h in {0x8 (a&b), 0x2 (a&~b), 0x4 (~a&b), 0x1 (~a&~b)}
    a_inv = a[1] ^ (h in (0x1, 0x4))
    b_inv = b[1] ^ (h in (0x1, 0x2))
    n, i = builder.add_gate("AND", a[0], a_inv, b[0], b_inv)
    return (n, i ^ neg)


def parse_bench_to_xag(bench_text: str, n_inputs: int, n_outputs: int) -> XAGCircuit:
    """Parse Berkeley ABC .bench netlist (standard gates or 1/2-input LUTs) into XAGCircuit."""
    builder = StrashBuilder(n_inputs)
    wires: Dict[str, Tuple[int, bool]] = {f"x{i}": (i, False) for i in range(n_inputs)}
    out_names: List[str] = []

    for raw in bench_text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m_io = _IO_RE.match(line)
        if m_io:
            kind, name = m_io.group(1), m_io.group(2)
            if kind == "INPUT":
                if name not in wires:
                    raise ValueError(f"Unexpected INPUT {name!r} in bench")
            else:
                out_names.append(name)
            continue

        m_lut = _LUT_RE.match(line)
        if m_lut:
            lhs = m_lut.group(1)
            hval = int(m_lut.group(2), 16)
            args = [a.strip() for a in m_lut.group(3).split(",") if a.strip()]
            if len(args) == 0:
                wires[lhs] = (-1, bool(hval & 1))
            elif len(args) == 1:
                w = wires[args[0]]
                if hval == 0:
                    wires[lhs] = (-1, False)
                elif hval == 3:
                    wires[lhs] = (-1, True)
                elif hval == 2:
                    wires[lhs] = w
                elif hval == 1:
                    wires[lhs] = (w[0], not w[1])
                else:
                    raise ValueError(f"Invalid 1-input LUT 0x{hval:x}")
            elif len(args) == 2:
                wires[lhs] = _lut2_to_gate(builder, hval, wires[args[0]], wires[args[1]])
            else:
                raise ValueError(f"Expected <=2-input LUT after strash, got {len(args)}: {line!r}")
            continue

        # Handle constant lines like `y0 = vdd` or `y0 = gnd`
        if "=" in line and "(" not in line:
            lhs, rhs = [s.strip() for s in line.split("=", 1)]
            rl = rhs.lower()
            if rl in ("gnd", "0", "false"):
                wires[lhs] = (-1, False)
            elif rl in ("vdd", "1", "true"):
                wires[lhs] = (-1, True)
            else:
                wires[lhs] = wires[rhs]
            continue

        m_as = _ASSIGN_RE.match(line)
        if not m_as:
            raise ValueError(f"Unrecognized bench line: {line!r}")
        lhs, op_raw, args_raw = m_as.group(1), m_as.group(2).upper(), m_as.group(3)
        args = [a.strip() for a in args_raw.split(",") if a.strip()]

        if op_raw == "BUFF" or op_raw == "BUF":
            wires[lhs] = wires[args[0]]
        elif op_raw == "NOT":
            n, inv = wires[args[0]]
            wires[lhs] = (n, not inv)
        elif op_raw in ("AND", "NAND", "OR", "NOR", "XOR", "XNOR"):
            # Fold n-ary gates left-to-right
            cur_n, cur_i = wires[args[0]]
            for a_name in args[1:]:
                rn, ri = wires[a_name]
                if op_raw in ("AND", "NAND"):
                    cur_n, cur_i = builder.add_gate("AND", cur_n, cur_i, rn, ri)
                elif op_raw in ("OR", "NOR"):
                    # a | b = ~(~a & ~b)
                    cur_n, cur_i = builder.add_gate("AND", cur_n, not cur_i, rn, not ri)
                    cur_i = not cur_i
                else:
                    cur_n, cur_i = builder.add_gate("XOR", cur_n, cur_i, rn, ri)
            if op_raw in ("NAND", "NOR", "XNOR"):
                cur_i = not cur_i
            wires[lhs] = (cur_n, cur_i)
        else:
            raise ValueError(f"Unsupported bench op {op_raw!r} on line: {line!r}")

    # Match outputs in canonical order y0 .. y_{n_outputs-1}
    expected_outs = [f"y{h}" for h in range(n_outputs)]
    ordered = expected_outs if all(n in wires for n in expected_outs) else out_names
    if len(ordered) != n_outputs:
        raise ValueError(f"Expected {n_outputs} outputs, found {len(ordered)}: {ordered}")
    return builder.build([wires[n] for n in ordered], prune_dead=True)


def fold_aig_xors(circ: XAGCircuit) -> XAGCircuit:
    """Sound exact AIG -> XAG XOR pattern folding:
    Detects `AND(~AND(a, b), ~AND(~a, ~b))` == `a ^ b` and `AND(~AND(a, ~b), ~AND(~a, b))` == `~(a ^ b)`.
    Guaranteed truth-table identical; gives ABC full credit in XAG gate counts.
    """
    n_in = circ.n_inputs
    # Map each gate node_id -> Gate
    gmap: Dict[int, Gate] = {n_in + i: g for i, g in enumerate(circ.gates)}

    builder = StrashBuilder(n_in)
    node_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
    for i in range(n_in):
        node_map[i] = (i, False)

    for idx, g in enumerate(circ.gates):
        nid = n_in + idx
        folded: Optional[Tuple[int, bool]] = None
        if g.op == "AND" and g.left_inv and g.right_inv:
            gl = gmap.get(g.left)
            gr = gmap.get(g.right)
            if gl is not None and gr is not None and gl.op == "AND" and gr.op == "AND":
                # Check if gl and gr share the exact same two underlying fanin nodes with opposite polarities
                l_pair = ((gl.left, gl.left_inv), (gl.right, gl.right_inv))
                r_pair = ((gr.left, gr.left_inv), (gr.right, gr.right_inv))
                if gl.left == gr.left and gl.right == gr.right:
                    if gl.left_inv != gr.left_inv and gl.right_inv != gr.right_inv:
                        # ~( (a^p)&(b^q) ) & ~( (a^!p)&(b^!q) ) == (a^p) ^ (b^q) ^ 1?
                        # Exact check:
                        #   if p==q: ~(a&b) & ~(~a&~b) = a ^ b (no inv)
                        #   if p!=q: ~(~a&b) & ~(a&~b) = ~(a ^ b) (inv=True)
                        an, ai = node_map[gl.left]
                        bn, bi = node_map[gl.right]
                        xn, xi = builder.add_gate("XOR", an, ai, bn, bi)
                        extra_inv = gl.left_inv != gl.right_inv
                        folded = (xn, xi ^ extra_inv)
                elif gl.left == gr.right and gl.right == gr.left:
                    if gl.left_inv != gr.right_inv and gl.right_inv != gr.left_inv:
                        an, ai = node_map[gl.left]
                        bn, bi = node_map[gl.right]
                        xn, xi = builder.add_gate("XOR", an, ai, bn, bi)
                        extra_inv = gl.left_inv != gl.right_inv
                        folded = (xn, xi ^ extra_inv)
        if folded is not None:
            node_map[nid] = folded
        else:
            ln, li = node_map[g.left]
            rn, ri = node_map[g.right]
            node_map[nid] = builder.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)

    outs = []
    for onode, oinv in circ.outputs:
        mn, mi = node_map[onode]
        outs.append((mn, mi ^ oinv))
    res = builder.build(outs, prune_dead=True)
    assert res.truth_tables() == circ.truth_tables(), "XOR folding broke truth table!"
    return res


# Exact expansion of Berkeley ABC's official `resyn2` alias from abc.rc (no abc.rc dependency).
_RESYN2 = "balance; rewrite; refactor; balance; rewrite; rewrite -z; balance; refactor -z; rewrite -z; balance"
DEFAULT_ABC_RECIPE = f"strash; dc2; {_RESYN2}; dc2; {_RESYN2}; dc2; strash"


def synthesize_with_abc(
    n_inputs: int,
    targets: Sequence[int],
    abc_bin: Optional[Path] = None,
    recipe: str = DEFAULT_ABC_RECIPE,
    meter: Optional[object] = None,
    phase: str = "industry_abc",
) -> Dict[str, object]:
    """Run Berkeley ABC on (n_inputs, targets) and return verified AIG & XAG circuits."""
    exe = find_abc_binary(abc_bin)
    mask = full_mask(n_inputs)
    clean_targets = tuple(t & mask for t in targets)

    with tempfile.TemporaryDirectory(prefix="prom_abc_") as td:
        tdir = Path(td)
        pla_p = tdir / "in.pla"
        bench_p = tdir / "out.bench"
        write_pla(pla_p, n_inputs, clean_targets)

        cmd_str = f'read_pla "{pla_p.as_posix()}"; {recipe}; write_bench "{bench_p.as_posix()}"'
        t0 = time.perf_counter()
        proc = subprocess.run(
            [str(exe), "-c", cmd_str],
            capture_output=True,
            text=True,
            timeout=60,
        )
        dt = time.perf_counter() - t0
        if meter is not None:
            meter.charge_cpu(dt, phase=phase)
        if proc.returncode != 0 or not bench_p.exists():
            raise RuntimeError(
                f"ABC failed (rc={proc.returncode}): stdout={proc.stdout[-300:]} stderr={proc.stderr[-300:]}"
            )
        bench_text = bench_p.read_text(encoding="ascii")

    aig = parse_bench_to_xag(bench_text, n_inputs, len(clean_targets))
    assert verify_truth_tables(aig, clean_targets, meter=meter, phase=phase), "ABC AIG failed exact verification!"
    xag = fold_aig_xors(aig)
    assert verify_truth_tables(xag, clean_targets, meter=meter, phase=phase), "ABC XAG failed exact verification!"
    return {
        "aig": aig,
        "xag": xag,
        "aig_gates": aig.gate_count(),
        "xag_gates": xag.gate_count(),
        "wall_seconds": dt,
    }
