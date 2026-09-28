"""Known-answer tests for the recertification harness: planted TRUE instances must come out LABEL_OK; planted
IMPOSTORS (structure without behaviour; behaviour by a different mechanism; label with nothing behind it) must be
caught, each with its own verdict. Run BEFORE the label runs; exit 0 = every check passed.

    python3 test_known_answers.py      -> prints one line per check, writes KNOWN_ANSWERS.json
"""
from __future__ import annotations

import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recert as R  # noqa: E402

RESULTS = []


def check(name, got, want, detail=""):
    ok = got == want
    RESULTS.append({"check": name, "want": want, "got": got, "pass": ok, "detail": detail})
    print("%-5s %-62s want %-38s got %s  %s" % ("PASS" if ok else "FAIL", name, want, got, detail))


def rnd(seed, n, avoid=()):
    r = random.Random(seed)
    return bytes(b for b in (r.choice([x for x in range(256) if x not in avoid]) for _ in range(n)))


# ---------------------------------------------------------------- the verdict table itself
def t_verdict():
    V = R.verdict
    check("verdict: no behaviour, no structure", V(False, 0.0, None), "LABEL_PROVENANCE_ONLY")
    check("verdict: no behaviour, structure", V(True, 0.0, None), "STRUCTURE_WITHOUT_BEHAVIOUR")
    check("verdict: behaviour, wrong mechanism", V(True, 1.0, False), "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM")
    check("verdict: behaviour in few envs, right mechanism", V(True, 0.2, True), "LABEL_CONTEXT_DEPENDENT")
    check("verdict: behaviour everywhere, right mechanism", V(False, 1.0, True), "LABEL_OK")
    check("verdict: behaviour, mechanism n/a", V(True, 0.9, None), "LABEL_OK")
    check("verdict: unlabelled capable object (false negative)", V(True, 1.0, True, labelled=False), "UNLABELLED_LABEL_OK")


# ---------------------------------------------------------------- L1 BEE self-replicator
def t_l1():
    import l1_bee_sr as M
    from bee_engine import vm
    s = {"L": 64, "allow_copyall": False, "layout": "SHARED", "ldir": "on", "undefined": "NOP", "strict": True,
         "budget": 256, "representation": "Z80_64", "reproduction": "ENDOGENOUS_COPY", "read_gate": "ABR"}
    L = 64
    copy_free = (vm.LDI, vm.LDIR, vm.COPYALL)

    def pad(code, seed):
        return bytes(code) + rnd(seed, L - len(code), avoid=copy_free)

    rep = pad(vm.replicator(L), 1)
    ldi_loop = pad(bytes([vm.LD_S_n, 0, vm.LD_T_n, L, vm.LD_B_n, L, vm.LDI, vm.DJNZ_d, 0xFD, vm.HALT]), 2)
    dead = pad(bytes([vm.HALT]) + vm.replicator(L), 3)                 # copy routine present, never reached
    blank = bytes(L)                                                  # nothing at all
    # painter: LD T,64 ; loop: LD (T),A ; INC T ; DJNZ loop  -- writes zeros over the window; tape = code + zeros,
    # so the painted window is >= 0.9 identical to the tape without any byte of the tape being read
    painter = bytes([vm.LD_T_n, L, vm.LD_pT_A, vm.INC_T, vm.DJNZ_d, 0xFC]) + bytes(L - 6)
    cases = [("L1 true: LDIR replicator + random tail", rep, True, "LABEL_OK"),
             ("L1 true: LDI byte-loop replicator", ldi_loop, True, "LABEL_OK"),
             ("L1 impostor: copy routine behind HALT", dead, True, "STRUCTURE_WITHOUT_BEHAVIOUR"),
             ("L1 impostor: blank tape carrying the label", blank, True, "LABEL_PROVENANCE_ONLY"),
             ("L1 impostor: zero painter (no byte of the tape read)", painter, True, "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM"),
             ("L1 control: unlabelled replicator", rep, False, "UNLABELLED_LABEL_OK")]
    for name, tape, lab, want in cases:
        o = M.Obj("KA:" + name, tape, s, {"label_then": "planted"}, labelled=lab)
        r = R.recertify_one(M.LABEL, o)
        c = r["causal"]
        check(name, r["now"], want, "rate=%.2f T=%s bits=%s" % (r["behavioural"]["pass_rate"], c.get("transmission"),
                                                               c.get("bits_transmitted")))
    # the world's own copy-op rule must NOT accept the painter (it does not claim to): documents the rule's scope
    f, wr, *_ = M.reproduce(painter, s, 42, bytes(L))
    check("L1 painter: functional test passes, world copy-op rule rejects", (f, wr), (True, False))


# ---------------------------------------------------------------- L2 NPE P-11
def t_l2():
    import l2_npe_p11 as M
    z8 = M.z8
    n = 96
    cell = {"representation": "Z8_SHARED", "copy_primitive": "BLOCK", "reproduction": "PAIR_EXECUTION",
            "self_location": "PRIMITIVE", "mutation_rate": "LOW"}
    kw = dict(budget=1000, cmr=0.0, mask=0x01 | 0x02 | 0x08 | 0x20)       # test_p11.py's fixture settings

    def prog(src, seed):
        code, _ = z8.asm(src)
        return code + rnd(seed, n - len(code))

    copier = prog("SELF\nLD A,L\nXOR 96\nLD E,A\nLD D,0\nLDIR\nHALT", 11)   # side-agnostic: DE = own base XOR 96
    abs_copier = prog("SELF\nLD DE,96\nLDIR\nHALT", 12)                   # test_p11 BLOCK_COPIER: works from side 0 only
    # zero painter with an LDIR smear: LD HL,96 ; LD (HL),0 ; LD DE,97 ; LD BC,95 ; LDIR -- genome = code + zeros:
    # 9 non-zero bytes of 96, so the smeared (all-zero) victim is 0.906 identical to the donor: P-11 C2 passes
    code, _ = z8.asm("LD HL,96\nLD (HL),0\nLD DE,97\nLD BC,95\nLDIR")
    painter = code + bytes(n - len(code))
    bare = z8.asm("LDIR\nHALT")[0] + rnd(13, n - 3)                       # register-state-dependent bare LDIR
    r0 = bytes(b for b in rnd(14, n) if True)
    noop = bytes(b if b != 0xED else 0x00 for b in r0)
    cases = [("L2 true: side-agnostic block copier", copier, "LABEL_OK"),
             ("L2 impostor: LDIR-smear zero painter (passes P-11)", painter, "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM"),
             ("L2 impostor: bare LDIR, addresses from registers", bare, "STRUCTURE_WITHOUT_BEHAVIOUR"),
             ("L2 impostor: random genome carrying the label", noop, "LABEL_PROVENANCE_ONLY")]
    for name, g, want in cases:
        o = M.Obj("KA:" + name, g, cell, "L", {"label_then": "planted"}, **kw)
        r = R.recertify_one(M.LABEL, o)
        c = r["causal"]
        check(name, r["now"], want, "rate=%.2f T=%s fresh=%s" % (r["behavioural"]["pass_rate"], c.get("transmission"),
                                                                c.get("fresh_state_pass_rate")))
    # boundary case: test_p11's absolute-address copier copies only from tape side 0, i.e. in at most half the
    # environments (and a randomized victim on side 0 runs FIRST and can damage it). Expected: mechanism OK, rate
    # <= 0.5, verdict at the LABEL_OK / LABEL_CONTEXT_DEPENDENT boundary. (First predicted plain CONTEXT_DEPENDENT; the
    # rate came out 0.50 under one seed and 0.44 under another, so the check asserts the bracket, not a single value.)
    o = M.Obj("KA:L2 boundary absolute copier", abs_copier, cell, "L", {"label_then": "planted"}, **kw)
    r = R.recertify_one(M.LABEL, o)
    br = (r["causal"].get("ok") is True and 0.3 <= r["behavioural"]["pass_rate"] <= 0.5
          and r["now"] in ("LABEL_OK", "LABEL_CONTEXT_DEPENDENT"))
    check("L2 boundary: absolute-address copier (side 0 only)", br, True,
          "now=%s rate=%.2f T=%s" % (r["now"], r["behavioural"]["pass_rate"], r["causal"].get("transmission")))
    # P-11 itself (fresh registers, donor on side 0) accepts the painter: the certificate cannot tell painting from copying
    o = M.Obj("KA:painter-direct", painter, cell, "L", {}, **kw)
    a = M.assay(o, painter, {"side": 0, "warm": 0, "ws": 0})
    check("L2 painter: p11.assay passes it directly (FR-011 claim)", bool(a["pass"]), True,
          "draws_passed=%d fid=%.3f" % (a["draws_passed"], a["draws"][0]["fid_final"]))


# ---------------------------------------------------------------- L3 BEE competent solver
def t_l3():
    import l3_bee_solver as M
    from bee_engine import vm
    from prometheus.z80atlas.tasks import Task
    s = {"L": 64, "allow_copyall": False, "layout": "SHARED", "ldir": "on", "undefined": "NOP", "strict": True,
         "budget": 256, "representation": "Z80_64", "reproduction": "ENDOGENOUS_COPY", "read_gate": "ABR"}
    L = 64
    inc = Task("INC", k=0)

    def pad(code, seed):
        return bytes(code) + rnd(seed, L - len(code))

    true = pad(vm.witness_inc(), 21)
    # correct only with a zero byte at window offset 5: A = x + window[5] + 1
    win_dep = pad(bytes([vm.IN_A, vm.LD_B_A, vm.LD_S_n, L + 5, vm.LD_A_pS, vm.ADD_A_B, vm.INC_A, vm.OUT_A, vm.HALT]), 22)
    # reads the input region as memory (never executes IN): right answers, not by the port the gate accounts for
    by_addr = pad(bytes([vm.LD_S_n, vm.IN_BASE, vm.LD_A_pS, vm.INC_A, vm.OUT_A, vm.HALT]), 23)
    echo = pad(bytes([vm.IN_A, vm.OUT_A, vm.HALT]), 24)                   # labelled an INC solver; it echoes
    cases = [("L3 true: INC witness", true, "LABEL_OK"),
             ("L3 impostor: right only with an empty window", win_dep, "LABEL_CONTEXT_DEPENDENT"),
             ("L3 impostor: input read by address, not IN", by_addr, "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM"),
             ("L3 impostor: ECHO tape carrying an INC label", echo, "LABEL_PROVENANCE_ONLY")]
    for name, t, want in cases:
        o = M.Obj("KA:" + name, t, s, inc, {"label_then": "planted"})
        r = R.recertify_one(M.LABEL, o)
        c = r["causal"]
        check(name, r["now"], want, "rate=%.3f ko=%s" % (r["behavioural"]["pass_rate"], c.get("accuracy_after_IN_knockout")))


def main():
    t_verdict()
    t_l1()
    t_l2()
    t_l3()
    n_ok = sum(r["pass"] for r in RESULTS)
    print("%d/%d known-answer checks passed" % (n_ok, len(RESULTS)))
    json.dump({"passed": n_ok, "total": len(RESULTS), "checks": RESULTS},
              open(os.path.join(HERE, "KNOWN_ANSWERS.json"), "w"), indent=1, default=str)
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
