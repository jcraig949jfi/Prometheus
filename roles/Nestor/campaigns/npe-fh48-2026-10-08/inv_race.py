"""Pairwise copy-race assay on the real pair tape: after side 0 then side 1 execute (fresh registers, no world
mutation, copy errors off), which genome occupies each half? With task inputs (r = 0 / r = 1, ONTAPE world) and
without (IN returns 0, the DIR/RANDOM worlds)."""
import json, random, sys
sys.dont_write_bytecode = True
import arch, fh


def race(g0, g1, inputs0=(), inputs1=(), n=64):
    r = arch._tape_runner()          # FIRST: installs the dense VM on world.z8 (fetching z8 before this got the plain VM)
    import world
    z8 = world.z8
    tape = bytearray(128)
    tape[0:64] = g0
    tape[64:128] = g1
    outs = []
    for who, start, inp in ((0, 0, inputs0), (1, 64, inputs1)):
        c = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=random.Random(who), copy_mut_rate=0.0, sense=who, inputs=inp)
        z8.run(c, start, r.t["slice"], ops_enabled=r._ops_mask())
        outs.append(c.outputs[0] if c.outputs else None)
    h0, h1 = bytes(tape[0:64]), bytes(tape[64:128])

    def who_(h):
        return "A" if h == g0 else "B" if h == g1 else "other"
    return who_(h0), who_(h1), outs


if __name__ == "__main__":
    s = json.load(open("runs/X-ONTAPE/MINE_ONTAPE_44900007.json"))
    INV = bytes.fromhex([t for t in s["2000"]["top"] if t["u"] == 0.0][0]["hex"])
    CT = fh.PLANTS["CT_UA"]
    ep = (17, 200)    # v, key
    for name, (A, B) in {"CT_UA first, INV second": (CT, INV), "INV first, CT_UA second": (INV, CT),
                         "CT_UA vs CT_UA": (CT, CT)}.items():
        for lab, i0, i1 in (("no inputs (DIR world)", (), ()),
                            ("inputs r=0", (ep[0], ep[1], 0), (ep[0], ep[1], 0)),
                            ("inputs r=1", (ep[0], ep[1], 1), (ep[0], ep[1], 1))):
            print("%-26s %-22s halves after = %s" % (name, lab, race(A, B, i0, i1)[:2]))
