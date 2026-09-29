"""Q4 representatives: executed-instruction listings (donor context, SELF disabled, fresh state) up to the first
block-copy, for 8 SELF-free competent genomes chosen by rule (one per motif class, highest rate_noself, ties by hex).
Writes q4_reps.json and q4_reps.txt. One process."""
import json
import random

import corpus_analysis as ca


def listing(world, r, g, side, victim, mask):
    n = r.L
    tl = world._pow2(2 * n)
    z = world.z8
    tape = bytearray(tl)
    tape[0:n] = (g + bytes(n))[:n] if side == 0 else victim
    tape[n:2 * n] = victim if side == 0 else (g + bytes(n))[:n]
    if side == 1:
        c0 = z.Ctx(tape, 0, n, policy=z.ARENA, rng=random.Random(1), copy_mut_rate=0.0, sense=0)
        z.run(c0, 0, r.t["slice"], ops_enabled=mask)
    pre = bytes(tape)
    start = side * n
    dense = ca.vm_is_dense(z)
    rows, prev = [], [0] * 8
    for b in range(0, r.t["slice"] + 1):
        t2 = bytearray(pre)
        c = z.Ctx(t2, start, n, policy=z.ARENA, rng=random.Random(1), copy_mut_rate=0.0, sense=side)
        pc = z.run(c, start, b, ops_enabled=mask) if b else start
        regs = c.regs if b else [0] * 8
        if rows:
            ch = ["%s=%02X" % (nm, regs[i]) for i, nm in enumerate("BCDEHL") if regs[i] != prev[i]]
            if regs[7] != prev[7]:
                ch.append("A=%02X" % regs[7])
            rows[-1] += ("   ; " + " ".join(ch)) if ch else ""
        code = bytes(t2[(pc + i) % tl] for i in range(4))
        txt = ca.dis_dense(code, "DENSE" if dense else "PLAIN")[0].split("  ", 1)[1]
        rel = (pc - start) % tl
        rows.append("%+04d  %s" % (rel if rel < 64 else rel - tl, txt))
        prev = list(regs)
        op, op2 = t2[pc % tl], t2[(pc + 1) % tl]
        if (op == 0xED and op2 in (0xB0, 0xB8)) or (dense and op in (0xE5, 0xE7)):
            rows[-1] += "   <- HL=%04X DE=%04X BC=%04X (HL&127=%d, DE&127=%d)" % (
                (regs[4] << 8) | regs[5], (regs[2] << 8) | regs[3], (regs[0] << 8) | regs[1],
                regs[5] & 127, regs[3] & 127)
            break
    return rows


def main():
    q = json.load(open(ca.HERE / "q4_provenance.json"))

    def cls(d):
        s = "0" if d["side_pass_10"][0] >= d["side_pass_10"][1] else "1"
        e = d["side"][s]
        if not e:
            return None
        base = 64 * int(s)
        hl = (e["HL"] - base) % 128
        err = hl if e["kind"] == "LDIR" else (hl - 63) % 128
        return (d["vm"], d["cell"], s, e["kind"], err)

    want = [("DENSE", "7ae3", "0", "LDIR", 0), ("DENSE", "7ae3", "0", "LDDR", 1), ("DENSE", "ffa6", "0", "LDIR", 0),
            ("DENSE", "ffa6", "0", "LDDR", 1), ("DENSE", "ffa6", "0", "LDIR", 127), ("DENSE", "ffa6", "1", "LDIR", 0),
            ("PLAIN", "7ae3", "0", "LDDR", 1)]
    picks = []
    for w in want:
        c = sorted([d for d in q if cls(d) == w and not d.get("nocopy_donor")], key=lambda d: (-d["rate_noself"], d["hex"]))
        if c:
            picks.append(c[0])
    nd = sorted([d for d in q if d.get("nocopy_donor") == "NO_COPY"], key=lambda d: (-d["rate_noself"], d["hex"]))
    if nd:
        picks.append(nd[0])
    out, txt = [], []
    for d in picks:
        world, r = ca.env(d["vm"], d["cell"])
        g = bytes.fromhex(d["hex"])
        mask = r._ops_mask() & ~0x02
        vr = random.Random(("CORPUS-Q4", d["hex"]).__repr__())
        victim = bytes(vr.randrange(256) for _ in range(r.L))
        s = 0 if d["side_pass_10"][0] >= d["side_pass_10"][1] else 1
        rows = listing(world, r, g, s, victim, mask)
        out.append({"class": cls(d), "hex": d["hex"], "origin_run": d["origin_run"], "rate_noself": d["rate_noself"],
                    "side_pass_10": d["side_pass_10"], "nocopy_donor": d.get("nocopy_donor"), "executed": rows,
                    "static_dis": ca.dis_dense(g, d["vm"])})
        txt.append("=== %s  %s  rate_noself=%.2f  side_pass_10=%s  %s\n%s\n" % (
            cls(d), d["origin_run"], d["rate_noself"], d["side_pass_10"], d["hex"], "\n".join(rows)))
    (ca.HERE / "q4_reps.json").write_text(json.dumps(out, indent=1))
    (ca.HERE / "q4_reps.txt").write_text("\n".join(txt))
    print("\n".join(txt))


if __name__ == "__main__":
    main()
