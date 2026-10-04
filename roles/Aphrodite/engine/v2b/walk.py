"""Resumable exact walker.

a18.fast_cost returns the FIRST dev-consistent program and its charge. Many first hits are spurious: they are
consistent on the dev cell but fail the tribunal. W7 found 12 of 13 T4-failing PRISTINE first hits at 250k were
query-1/2 artifacts, and W2 found 25 spurious fallback hits at 4M. Historical "capability" therefore read
"first hit within budget", while the tribunal re-checked only that one hit.

iter_hits(lib, cell, cap) yields EVERY dev-consistent program, in the identical traversal and charge
accounting as a18.fast_cost (same fair.keyed calls; same charge for failing accumulators). It lets the
capability endpoint walk past spurious hits to the first TRIBUNAL-QUALIFIED program.

Conformance (tests/test_walk.py; conformance_v2b.py): for every (library, cell) pair the first yield equals
a18.fast_cost(lib, cell, cap), both charge and program, and a cap with no hit yields nothing.
"""
import paths  # noqa: F401
import a17
import a18
from a18 import FR, G

import fasteval as FE


def iter_hits(lib, cell, cap):
    """Yield (charge, program) for every dev-consistent program, in walk order, up to charge `cap`."""
    seed = cell.seed
    pinfo = [(n[:-1], n[0], n[-1], (n[:-1][-1] if len(n) > 1 else 0), gold) for n, gold in cell.parsed]
    st = {"n": 0}

    def finals_iter(accs, finals, head):
        for f in finals:
            if st["n"] >= cap:
                return
            st["n"] += 1
            ffn = FE.fn(f)
            ok = True
            for a, (_v, fst, lst, vl, gold) in zip(accs, pinfo):
                got = FE._final(ffn, a, vl, fst, lst)
                if got is None or str(got) != gold:
                    ok = False
                    break
            if ok:
                yield st["n"], head + (f,)

    def block(inits, bodies, finals):
        for i in inits:
            ifn = FE.fn(i)
            for b in bodies:
                if st["n"] >= cap:
                    return
                bfn = FE.fn(b)
                accs = [FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _vl, _g in pinfo]
                if any(a is FE._FAIL for a in accs):
                    st["n"] = min(cap, st["n"] + len(finals))
                    continue
                yield from finals_iter(accs, finals, ("fold", i, b))

    for e, bodies in zip(lib.entries, lib._bodies):
        yield from block(FR.keyed(e["inits"], seed, "init"), FR.keyed(bodies, seed, "body"),
                         FR.keyed(e["finals"], seed, "final"))
        if st["n"] >= cap:
            return
    fs = FR.keyed(G.FINAL_SPACE, seed, "g4final")
    for f in fs:
        if st["n"] >= cap:
            return
        st["n"] += 1
        ffn = FE.fn(f)
        ok = True
        for _v, fst, lst, _vl, gold in pinfo:
            got = FE._final(ffn, 0, 0, fst, lst)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok:
            yield st["n"], ("expr", f)
    yield from block(FR.keyed(G.INIT_SPACE, seed, "g4init"), FR.keyed(G.BODY_SPACE, seed, "g4body"), fs)


def first_hit(lib, cell, cap):
    for ch, prog in iter_hits(lib, cell, cap):
        return ch, prog
    return cap, None


def first_qualified(lib, cell, cap, qualify, max_spurious=10_000):
    """Walk to the first program for which qualify(prog) is True.
    Returns {charge, program, spurious_before, censored}. censored=True means no qualified program was found
    at or below cap, so the D value is a lower bound."""
    spur = 0
    for ch, prog in iter_hits(lib, cell, cap):
        if qualify(prog):
            return {"charge": ch, "program": list(prog), "spurious_before": spur, "censored": False}
        spur += 1
        if spur >= max_spurious:
            return {"charge": ch, "program": None, "spurious_before": spur, "censored": True,
                    "stopped": "max_spurious"}
    return {"charge": cap, "program": None, "spurious_before": spur, "censored": True}


def conformance(n_pairs=200, cap=None, seed="APHRODITE/V2B/WALK-CONF/v1"):
    """Differential check of first_hit against a18.fast_cost on random (library, cell) pairs in W5."""
    import random
    import identity as I
    a18.use_world("W5")
    cap = cap or a17.ESCROW
    rng = random.Random(I._seed(seed))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    libs = [FR.pristine().entries, a17.L1_entries()]
    for w in rng.sample(a18.compositions(a18.G1), 6):
        libs.append([a17.schema_entry("g2_new", w)] + FR.pristine().entries)
    mism = []
    for k in range(n_pairs):
        body = rng.choice(G.BODY_SPACE)
        spec = {"walkconf": (body, rng.choice(finals), rng.choice(G.H1_SPACE))}
        prov = a17.Prov(spec)
        cell = FR.Cell(prov, "walkconf", k, rng.choice([4, 6, 8]), label="V2B-WALK-CONF")
        lib = FR.KLib(rng.choice(libs))
        a = a18.fast_cost(lib, cell, cap)
        b = first_hit(lib, cell, cap)
        if a[0] != b[0] or (a[1] is None) != (b[1] is None) or (a[1] and tuple(a[1]) != tuple(b[1])):
            mism.append([list(spec["walkconf"]), a[0], b[0]])
    return {"pairs": n_pairs, "cap": cap, "mismatches": len(mism), "examples": mism[:5]}
