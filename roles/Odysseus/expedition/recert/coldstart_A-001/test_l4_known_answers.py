"""Known-answer tests for L4 (ENVGATE founder "copier"). Planted TRUE instances must come out LABEL_OK; planted impostors
must be caught with their own verdict. Hand-built tapes only (the neighbour set reads LINEAGES.json tapes as ENVIRONMENTS;
no founder outcome is read). Exit 0 = every check passed.

    python3 test_l4_known_answers.py      -> prints one line per check, writes L4_KNOWN_ANSWERS.json
"""
from __future__ import annotations

import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recert as R  # noqa: E402
import l4_envgate_copier as M  # noqa: E402
from archaeon.z80atlas import tasks as T  # noqa: E402
from archaeon.z80atlas.vm import I  # noqa: E402
from archaeon.envgate import ruler as RU  # noqa: E402

RESULTS = []
G = 32


def check(name, got, want, detail=""):
    ok = got == want
    RESULTS.append({"check": name, "want": want, "got": got, "pass": ok, "detail": detail})
    print("%-5s %-60s want %-38s got %-38s %s" % ("PASS" if ok else "FAIL", name, want, got, detail))


def pad(code):
    return T.pad(code, G)


COPY_LOOP = [I(28), I(2, 3, 1), I(20), I(6, 3), I(16), 0xFC, I(23)]      # LD A,LEN; LD D,A; COPY; DEC D; JNZ -4; HALT
ungated = pad(T.replicator(True))                                        # the census ruler's own positive control
gated = pad([I(21, 2), I(1, 1), 0] + COPY_LOOP)                          # IN C (dest = input byte); exact only at x = 128
shifted = pad([I(1, 1), 1, I(1, 2), 128] + COPY_LOOP)                    # source = 1: a k = 1 shifted copy (NEAR by span)
blank = bytes(G)                                                         # all NOP
dead = pad([I(23)] + T.replicator(True))                                 # COPY present, behind HALT
# zero painter: LD B,32; LD C,128; loop: LD (C),A; INC C; DJNZ loop -- A = 0, no HALT; tape = 8 code bytes + 24 zeros, so
# the painted window is 0.75 identical to the tape without a byte of the tape being read
painter = pad([I(1, 1), 32, I(1, 2), 128, I(18, 2, 1), I(5, 2), I(27), 0xFC])
# empty-neighbour-only copier: LD A,(159); OR A,A; JNZ -> HALT; else the replicator. Any non-zero last neighbour byte stops it
ctx = pad([I(19, 0, 0), 159, I(9, 0), I(16), 10] + T.replicator(True))

CASES = [("L4 true: ungated replicator (census ruler control)", ungated, True, "LABEL_OK", "EXACT_UNGATED"),
         ("L4 true: input-gated copier (IN C; exact at 128 only)", gated, True, "LABEL_OK", "EXACT_GATED"),
         ("L4 true: shifted copier (k=1, NEAR by span)", shifted, True, "LABEL_OK", "NEAR_COPIER"),
         ("L4 impostor: blank tape carrying the label", blank, True, "LABEL_PROVENANCE_ONLY", "INERT"),
         ("L4 impostor: copy routine behind HALT", dead, True, "STRUCTURE_WITHOUT_BEHAVIOUR", "INERT"),
         ("L4 impostor: zero painter (ruler says NEAR_COPIER)", painter, True, "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM", "NEAR_COPIER"),
         ("L4 impostor: copies only into an empty neighbour", ctx, True, "LABEL_CONTEXT_DEPENDENT", "EXACT_UNGATED"),
         ("L4 control: unlabelled replicator", ungated, False, "UNLABELLED_LABEL_OK", "EXACT_UNGATED")]


def main():
    for name, tape, lab, want, want_cls in CASES:
        o = M.Obj("KA:" + name, tape, {"label_then": "planted"}, labelled=lab)
        r = R.recertify_one(M.LABEL, o)
        c = r["causal"]
        check(name, r["now"], want, "rate=%.2f T=%s k=%s bits=%s" % (r["behavioural"]["pass_rate"], c.get("transmission"),
                                                                       c.get("offset_k"), c.get("bits_transmitted")))
        check(name + " [frozen ruler class]", RU.measure(tape)["class"], want_cls)
    n_ok = sum(r["pass"] for r in RESULTS)
    print("%d/%d L4 known-answer checks passed" % (n_ok, len(RESULTS)))
    json.dump({"passed": n_ok, "total": len(RESULTS), "checks": RESULTS},
              open(os.path.join(HERE, "L4_KNOWN_ANSWERS.json"), "w"), indent=1, default=str)
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
