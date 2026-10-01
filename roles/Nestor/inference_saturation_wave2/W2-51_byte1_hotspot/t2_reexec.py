"""W2-51 t2: which instruction writes byte 1 in the WORLD's byte-1 in-place events.
For every in-place event of a tracked family organism (W2-26 s1_out hist, pre-genome family) that changed byte 1,
take the matching W2-41 r1_out row (same run, oid, epoch: own genome + carried context, partner genome + partner
carried context, side) and re-execute that one interaction statically on the stock traced VM (W2-24 tvm.pair_t,
copy errors OFF). Report: reproduction (re-executed byte 1 == recorded post-execution byte 1, and full
own-half equality), the last writer of byte 1 (actor self/partner; which half's code; pc within that half;
opcode), and for LDIR writes the (src, dst, n) and whether byte 1 is the first/last byte of the LDIR's
footprint in that half. Also the same for DONOR_PRE births (donor's own byte 1 changed during the birth
interaction, then copied) - matched on the parent's r1 row.
python -B t2_reexec.py -> t2_reexec.json"""
import gzip, json, pathlib, sys, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
sys.path.insert(0, str(W / "W2-24_keep_variant"))
from tvm import C, pair_t  # noqa: E402
S1 = W / "W2-26_switch_source" / "s1_out"
R1 = W / "W2-41_carried_context" / "r1_out"
r = C.runner_for_spec(C.run_ds.DONOR)
n = r.L
OPN = {0xED: "ED-op", 0x02: "LD (BC),A", 0x12: "LD (DE),A", 0x77: "LD (HL),A", 0x36: "LD (HL),n"}


def opname(op, op2):
    if op == 0xED:
        return "ED"
    if 0x70 <= op <= 0x77 and op != 0x76:
        return "LD (HL),r"
    return OPN.get(op, "%02x" % op)


def ctx(regs, fz, fc):
    return (None if regs is None else list(regs), bool(fz), bool(fc))


agg = collections.Counter(); agg_rep = collections.Counter(); agg_ld = collections.Counter()
agg_w = collections.defaultdict(collections.Counter)
rows_out = []
for p in sorted(S1.glob("*.json")):
    lab = p.stem
    d = json.loads(p.read_text())
    imp = bytes.fromhex(d["implant"])

    def fam(g):
        return sum(x == y for x, y in zip(g, imp)) >= 51

    births = {int(k): v for k, v in d["births"].items()}
    hist = {int(k): v for k, v in d["hist"].items()}
    r1 = json.load(gzip.open(R1 / (lab + ".json.gz"), "rt"))
    G = [bytes.fromhex(h) for h in r1["genomes"]]
    idx = {(row[1], row[0]): row for row in r1["rows"]}
    targets = []
    for oid, evs in hist.items():
        for ev in evs:
            if any(x[0] == 1 for x in ev["ex"]):
                targets.append(("INPLACE", oid, ev))
    for c, b in births.items():
        dg, xg, g = bytes.fromhex(b["dg"]), bytes.fromhex(b["xg"]), bytes.fromhex(b["g"])
        if g[1] != dg[1] and xg[1] != dg[1] and bytes.fromhex(b["prov"])[1] == b["pside"] + 1:
            for ev in hist.get(b["p"], []):
                if ev["e"] == b["e"] and any(x[0] == 1 and x[2] == xg[1] for x in ev["ex"]):
                    targets.append(("DONOR_PRE", b["p"], ev))
    for kind, oid, ev in targets:
        row = idx.get((oid, ev["e"]))
        if row is None:
            agg[(kind, "no_r1_row(nonfamily_pre)")] += 1
            continue
        g = G[row[4]]
        side = row[3]
        assert side == ev["side"]
        pg = G[row[8]]
        sx, sy = ctx(row[5], row[6], row[7]), ctx(row[9], row[10], row[11])
        ga, gb, sa, sb = (g, pg, sx, sy) if side == 0 else (pg, g, sy, sx)
        na, nb, ctxs, tr, wl, a0, ld = pair_t(r, ga, gb, sa, sb)
        fin = na if side == 0 else nb
        rec = bytearray(g)
        for j, old, new, pv in ev["ex"]:
            rec[j] = new
        b1ok = fin[1] == rec[1]
        full = fin == bytes(rec)
        agg_rep[(kind, b1ok, full)] += 1
        A1 = side * n + 1
        last = [w for w in wl if w[2] == A1 and w[3] != w[4]]
        if not last:
            agg[(kind, "no_write_in_reexec")] += 1
            continue
        who, wpc = last[-1][0], last[-1][1]
        actor = "self" if who == side else "partner"
        codehalf = "own" if (wpc // n) == side else "partner"
        loc = wpc % n
        fe = [t for t in tr if t[0] == who and t[1] == wpc]
        op = fe[-1][2] if fe else None
        regs = fe[-1][3] if fe else None
        nm = opname(op, None)
        if op == 0xED:
            # find LDIR record at this pc
            lds = [l for l in ld if l[0] == who and l[1] == wpc]
            nm = "LDIR/LDDR"
            if lds:
                lw, lpc, src, dst, cnt, lregs = lds[-1]
                dst7 = dst & 127; src7 = src & 127
                off = (A1 - dst7) % 128
                pos = "first" if off == 0 else ("last" if off == min(cnt, 128) - 1 else "mid")
                agg_ld[(kind, actor, codehalf, loc, "src-dst=%d" % ((src7 - dst7) % 128), "dst%d" % dst7, "n<=2" if cnt <= 2 else ("n<64" if cnt < 64 else "n>=64"), pos)] += 1
        ch = [j for j in range(n) if fin[j] != g[j]]
        key = (kind, actor, codehalf, loc, nm)
        agg_w[kind][key[1:]] += 1
        rows_out.append({"run": lab, "kind": kind, "oid": oid, "e": ev["e"], "side": side, "b1": "%02x>%02x" % (g[1], rec[1]),
                         "repro_b1": b1ok, "repro_full": full, "actor": actor, "code_half": codehalf, "pc": loc,
                         "op": nm, "regs_at_fetch": regs, "n_changed": len(ch), "changed_lo_hi": [ch[0], ch[-1]] if ch else None,
                         "own_ctx": row[5], "partner_ctx": row[9], "pre_fam": fam(g)})

out = {"n_targets": len(rows_out), "repro": {"%s|%s|%s" % k: v for k, v in agg_rep.items()},
       "skipped": {"%s|%s" % k: v for k, v in agg.items()},
       "writer": {k: {"|".join(map(str, kk)): vv for kk, vv in v.most_common(25)} for k, v in agg_w.items()},
       "ldir": {"|".join(map(str, k)): v for k, v in agg_ld.most_common(30)},
       "rows": rows_out}
(HERE / "t2_reexec.json").write_text(json.dumps(out, indent=1))
print(out["n_targets"], out["repro"], out["skipped"])
for k, v in out["writer"].items():
    print(k, json.dumps(v))
print(json.dumps(out["ldir"], indent=0))
