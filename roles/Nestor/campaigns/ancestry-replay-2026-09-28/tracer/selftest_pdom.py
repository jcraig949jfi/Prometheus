"""ctrl_deps_pdom (Amendment C7.1) checks: (1) enabling pdom never changes values (random pair interactions vs z8.run);
(2) K22: the store inside the guarded fallthrough carries the guard's source in its pdom scope; (3) K31: the store AFTER the
join has an EMPTY pdom scope (C7's documented implicit-flow miss) while the primary ctrl still holds the source; (4) a
program that never HALTs: pdom scope == slice scope (ipdom None)."""
import json, random, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_shadow as T, z8shadow as S, npe_fixtures as NF, check_fixtures as CF, observe as O


def run_pdom(f):
    p = CF.pre_of(f)
    lab = S.initial_tape_labels(bytes(p.g[0]), bytes(p.g[1]), p.n, p.size)
    rl, fl = {}, {}
    for s in (0, 1):
        rl[s], fl[s] = S.initial_reg_labels(s, p.regs[s])
    sh = S.Shadow(bytes(p.g[0]) + bytes(p.g[1]), lab, p.regs, rl, p.flags, fl, p.budget, p.mask, pdom=True)
    sh.run_pair(p.n)
    last = {}
    for st in sh.stores:
        last[st.addr] = st
    return sh, last


def main():
    rng = random.Random(7)
    mism = 0
    for _ in range(600):
        case = T.rand_case(rng)
        wt, wo = T.world_pair(*case)
        tape, regs, flags, budget, mask = case
        lab = S.initial_tape_labels(tape[:32], tape[32:], 32, 64)
        rl, fl = {}, {}
        for s in (0, 1):
            rl[s], fl[s] = S.initial_reg_labels(s, regs[s])
        sh = S.Shadow(tape, lab, regs, rl, flags, fl, budget, mask, pdom=True)
        sh.run_pair(32)
        mism += bytes(sh.mem) != wt
    fx = {f["name"]: f for f in NF.fixtures()}
    _sh, last = run_pdom(fx["K22_guard_not_taken"])
    k22 = "E|a|6" in {O.enc_base(b) for b in last[19].ctrl_pdom}
    _sh, last = run_pdom(fx["K31_K11_bit_decoder"])
    st = last[12]
    k31_primary = "E|a|3" in {O.enc_base(b) for b in st.ctrl}
    k31_pdom_empty = len(st.ctrl_pdom) == 0
    # never-HALTing loop: JR -2 forever after a guarded region -> ipdom None -> pdom == slice scope at the store
    code = NF.asm("""
        LD HL, 3
        LD A, (HL)
        CP 0
        JRZ skip
    skip:
        LD HL, 27
        LD (HL), 0x11
    spin:
        JR spin
    """)
    f = NF.fx("PDOM_nohalt", NF.A_HALT, NF.half(code), {})
    _sh, last = run_pdom(f)
    st = last[27]
    nohalt = {O.enc_base(b) for b in st.ctrl_pdom} == {O.enc_base(b) for b in st.ctrl_slice}
    res = {"values_unchanged_600": mism == 0, "K22_guard_in_pdom": k22, "K31_primary_has_source": k31_primary,
           "K31_pdom_empty_after_join": k31_pdom_empty, "nohalt_pdom_equals_slice": nohalt}
    res["pass"] = all(res.values())
    print(json.dumps(res))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
