"""W2-36 instrumented CVT-R. Read-only on Artemis's code: imports certs (unchanged) through W2-16's _env, and
re-implements certs.cvt's loop ONLY to keep the per-draw lineages that certs.cvt discards. selftest() asserts the
re-implementation's rows are identical to certs.cvt's and its score identical to certs.score's.

Step function = adapter.make_step semantics (pair interaction, FRESH registers, cmr 0, victim bytes
sha256("VICTIM", sid, g, k)), with an optional victim override (HALT = no partner run) and a provenance capture.
"""
from __future__ import annotations
import pathlib, random, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
from _env import A, ROWS, certs, FRESH, shabytes, row  # noqa: E402
import p11  # noqa: E402

FID_FLOOR = 0.9


def make_step(z, P, side, sid, victim="RAND"):
    n = P["n"]

    def step(G, g, k):
        if victim == "RAND":
            vb = shabytes("VICTIM", sid, g, k, n=n)
        elif victim == "HALT":
            vb = bytes([0x76]) * n
        else:
            raise ValueError(victim)
        ga, gb = (G, vb) if side == 0 else (vb, G)
        tape, _, _, _ = p11.interact(z, n=n, tape_len=P["tape_len"], ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                     budget=P["budget"], ops_mask=P["mask"], cmr=0.0, rng=random.Random(0))
        v0 = n if side == 0 else 0
        return bytes(tape[v0:v0 + n])
    return step


def cvt_full(stepfn, G0, sid):
    """certs.cvt loop, identical semantics, but also returns every variant lineage."""
    cache = {}

    def st(G, g, k):
        key = (G, g, k)
        r = cache.get(key)
        if r is None:
            r = cache[key] = stepfn(G, g, k)
        return r

    def lineage(G, k):
        out = []
        for g in range(1, certs.GENS + 1):
            G = st(G, g, k)
            out.append(G)
        return out

    base = [lineage(G0, k) for k in range(certs.DRAWS)]
    rows, lins = [], []
    for i in range(len(G0)):
        for x in certs.variant_values(G0, i, False, sid):
            Gv = G0[:i] + bytes([x]) + G0[i + 1:]
            lin = [lineage(Gv, k) for k in range(certs.DRAWS)]
            d = [certs._defined([certs._delta(lin[k][g], base[k][g]) for k in range(certs.DRAWS)])
                 for g in range(certs.GENS)]
            rows.append((i, x, d))
            lins.append(lin)
    return rows, base, lins


def cr_index(rows):
    """indices of rows certs.score counts as CVT-R (verbatim clause of certs.py:73)."""
    out = []
    for j, r in enumerate(rows):
        d = r[2]
        if d[0] and d[1] and ((d[2] is not None and d[2] == d[1]) or (d[3] is not None and d[3] == d[1])):
            out.append(j)
    return out


def fid(a, b):
    return p11.fidelity(a, b)


def analyse(G0, rows, base, lins):
    """Per-seed diagnostics + the repaired rule R* (per seed)."""
    n = len(G0)
    D, NG = certs.DRAWS, certs.GENS
    # base-lineage fidelity floor: >= FID_FLOOR at g = 1, 2, 3 in >= 2 of 3 draws
    bfid = [[fid(base[k][g], G0) for g in range(NG)] for k in range(D)]
    base_ok = sum(all(bfid[k][g] >= FID_FLOOR for g in range(3)) for k in range(D)) >= 2
    cr = cr_index(rows)
    lit_g2 = lit_rec = inh_ok = vf_ok = rstar = 0
    rstar_classes = set()
    cr_detail = []
    # inheritance over ALL variants (not only cr): literal carriage of (i, x) at site i, minus base baseline
    inh_v = [0] * NG
    inh_b = [0] * NG
    for j, (i, x, d) in enumerate(rows):
        lin = lins[j]
        for g in range(NG):
            for k in range(D):
                inh_v[g] += lin[k][g][i] == x
                inh_b[g] += base[k][g][i] == x
    for j in cr:
        i, x, d = rows[j]
        lin = lins[j]
        rg = 2 if (d[2] is not None and d[2] == d[1]) else 3
        sig2 = dict(d[1])
        a = sig2.get(i) == x                       # parent's specific variant is in the g2 class
        lit_g2 += a
        lit_rec += a                               # recurring class == g2 class, so same membership
        # R* (b): parent's variant carried at its own site in >= 2/3 draws at g1, g2 and the recurrence gen,
        #         AND above the same-draw base baseline (base child shows x at i in 0 of those draws)
        def carried(g):
            v = sum(lin[k][g][i] == x for k in range(D))
            b = sum(base[k][g][i] == x for k in range(D))
            return v - b >= 2
        inh = carried(0) and carried(1) and carried(rg)
        inh_ok += inh
        Gv = G0[:i] + bytes([x]) + G0[i + 1:]
        vfid = [[fid(lin[k][g], Gv) for g in range(NG)] for k in range(D)]
        vok = sum(all(vfid[k][g] >= FID_FLOOR for g in range(3)) for k in range(D)) >= 2
        vf_ok += vok
        ok = inh and vok and base_ok
        rstar += ok
        if ok:
            rstar_classes.add(d[1])
        if len(cr_detail) < 400:
            cr_detail.append({"i": i, "x": x, "sig_len": len(d[1]), "variant_in_sig": a, "inherited": inh,
                              "variant_fid_ok": vok,
                              "variant_fid_g123_draw_mean": [round(sum(vfid[k][g] for k in range(D)) / D, 3)
                                                             for g in range(3)]})
    nv = len(rows) * D
    return {
        "CVTR_accept": len(cr) >= 1, "CVTR_n": len(cr), "CVTR_classes": len({rows[j][2][1] for j in cr}),
        "base_fid_by_draw_gen": [[round(v, 3) for v in r] for r in bfid], "base_fid_floor_ok": base_ok,
        "cr_variant_in_sig": lit_g2, "cr_inherited": inh_ok, "cr_variant_fid_ok": vf_ok,
        "inherit_rate_variant_by_gen": [round(v / nv, 4) for v in inh_v],
        "inherit_rate_base_by_gen": [round(v / nv, 4) for v in inh_b],
        "RSTAR_n": rstar, "RSTAR_classes": len(rstar_classes), "RSTAR_accept": rstar >= 1,
        "cr_detail_head": cr_detail[:12],
    }


def run_one(G, vm, cell, side, sid, victim="RAND", P=None, z=None, keep=False):
    if P is None:
        P = A.params(vm, cell)
        _, _, z = A.env(vm, cell)
    rows, base, lins = cvt_full(make_step(z, P, side, sid, victim), G, sid)
    out = analyse(G, rows, base, lins)
    out["score"] = certs.score(rows, P["n"])
    if keep:
        out["_rows"], out["_base"], out["_lins"] = rows, base, lins
    return out


def selftest(G, vm, cell, side, sid):
    """my loop == certs.cvt rows; my cr == certs.score CVTR.n; RAND step == adapter.make_step."""
    P = A.params(vm, cell)
    _, _, z = A.env(vm, cell)
    st_a = A.make_step(z, P["n"], P["tape_len"], P["budget"], P["mask"], side, sid)
    rows_a, base_a = certs.cvt(st_a, G, sid, False)
    rows_m, base_m, _ = cvt_full(make_step(z, P, side, sid), G, sid)
    sc = certs.score(rows_a, P["n"])
    return {"rows_identical": rows_a == rows_m, "base_identical": base_a == base_m,
            "cr_n_identical": len(cr_index(rows_m)) == sc["CVTR"]["n"], "score": sc["CVTR"]}
