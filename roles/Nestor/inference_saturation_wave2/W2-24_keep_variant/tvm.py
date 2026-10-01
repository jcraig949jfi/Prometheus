"""W2-24 traced STOCK z8 (the VM the 7ae3 C9X runner actually uses: runner_for_spec sets r._vm = Z8PLAIN).
Built by source injection, log appends only: every fetch (who, pc, op, regs, fz, fc) and every byte write
(who, pc_of_fetching_instruction, addr, old, new). pair_t() mirrors W2-3 common.pair() exactly and is
checked against it bit-for-bit in q1_trace.py."""
import pathlib, sys, types, random
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C  # noqa: E402


def build():
    src = pathlib.Path(C.Z8PLAIN.__file__).read_text()
    f_old = "        op = mem[pc]\n"
    assert src.count(f_old) == 1
    src = src.replace(f_old, f_old + "        _CUR[0] = pc\n        if _TR is not None: _TR.append((_WHO[0], pc, op, tuple(r), fz, fc))\n")
    w_old = "        pv = ctx.prov\n"
    assert src.count(w_old) == 1
    src = src.replace(w_old, "        if _WL is not None: _WL.append((_WHO[0], _CUR[0], a, mem[a], val & 0xFF))\n" + w_old)
    l_old = "                for _ in range(n):\n                    v = rd(src)\n"
    assert src.count(l_old) == 1
    src = src.replace(l_old, "                if _LD is not None: _LD.append((_WHO[0], _CUR[0], src, dst, n, tuple(r)))\n" + l_old)
    m = types.ModuleType("z8_traced_plain")
    m.__dict__.update({"_TR": None, "_WL": None, "_LD": None, "_WHO": [0], "_CUR": [0]})
    exec(compile(src, "z8_traced_plain", "exec"), m.__dict__)
    return m


T = build()


def pair_t(r, ga, gb, sa=C.ZERO, sb=C.ZERO):
    """common.pair() with the traced VM; returns (na, nb, ctxs, trace, writes, after0, ldirs)."""
    n = r.L
    tape = bytearray(C.world._pow2(2 * n))
    tape[0:len(ga)] = ga
    tape[n:n + len(gb)] = gb
    rng = random.Random(0)
    T._TR, T._WL, T._LD = [], [], []
    ctxs, after0 = [None, None], None
    for who, start, st in ((0, 0, sa), (1, n, sb)):
        T._WHO[0] = who
        ctx = T.Ctx(tape, start, n, policy=T.ARENA, rng=rng, copy_mut_rate=0.0, sense=who)
        ctx.regs = None if st[0] is None else list(st[0])
        ctx.fz, ctx.fc = st[1], st[2]
        T.run(ctx, start, r.t["slice"], ops_enabled=r._ops_mask())
        ctxs[who] = ctx
        if who == 0:
            after0 = (bytes(tape[0:n]), bytes(tape[n:2 * n]))
    tr, wl, ld = T._TR, T._WL, T._LD
    T._TR = T._WL = T._LD = None
    return bytes(tape[0:n]), bytes(tape[n:2 * n]), ctxs, tr, wl, after0, ld
