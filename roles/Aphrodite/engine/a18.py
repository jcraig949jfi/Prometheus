"""AMENDMENT 18 -- ABSTRACTION COMPOUNDING ASSAY C1 (driver).

The program is ABSTRACTION COMPOUNDING (operator, 2026-09-27). This driver
never writes a BOUNDED_RSI label. It is built on a17.py (imported, unmodified)
and adds:
  - WORLD W5: the depth-3 body space G5 (a17.g5_bodies) as the instantiation
    space and search fallback for EVERY arm (equal expressivity), switched
    in-process only;
  - a cached fallback ordering (throughput only; identical order);
  - the COMPOSITION MOVE (treatment-blind): for every schema S the donor's
    START library holds, candidate schemas wrap(S, op, atom) for every
    primitive op, atom in BODY_ATOMS and both argument orders, kept iff they
    have >= 2 in-space instantiations; they compete in the unchanged paired
    selection alongside the LGG-derived candidates;
  - ruler v2 (science/compounding/rb1/ruler_v2.py) for NOVELTY and the
    structural relations (COMPOSES / REFINES);
  - a pluggable tribunal (T4 via tribunal_t4, or MetaTribunal) for qualified
    recipients.
Stages: see AMENDMENT_18_*.md. Process pools are throughput only.
"""
import json
import os
import random
import sys
import time
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "science" / "compounding" / "rb1"))
import a17                    # noqa: E402
import basis_v4 as G          # noqa: E402
import engine as E            # noqa: E402
import fair as FR             # noqa: E402
import identity as I          # noqa: E402
import tier3d as T3D          # noqa: E402

G1 = "(acc + {H})"
TAG = os.environ.get("A18_TAG", "A18")


def log(m):
    print("[a18 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


# ---------------------------------------------------------------- world W5
_WORLD = None
_ORIG_KEYED = FR.keyed


def use_world(name):
    """'W5' switches instantiation space + fallback to G5 for every arm."""
    global _WORLD
    if name == _WORLD:
        return
    if name == "W5":
        g5 = a17.g5_bodies()
        G.BODY_SPACE = g5
        FR._BODY_SET = set(g5)
        T3D._STRUCT_TO_BODY = None
        FR.keyed = _keyed_cached
    _WORLD = name


@lru_cache(maxsize=64)
def _fallback_order(seed, slot, n):
    return _ORIG_KEYED(G.BODY_SPACE, seed, slot)


def _keyed_cached(items, seed, slot):
    """Identical order to fair.keyed; memoised only for the fallback body list
    (the same object for every library), which dominates cost in W5."""
    if items is G.BODY_SPACE:
        return _fallback_order(seed, slot, len(items))
    return _ORIG_KEYED(items, seed, slot)


def worker_init():
    a17.worker_init()
    use_world(os.environ.get("A18_WORLD", "W5"))
    install_fast_cost()


# ---------------------------------------------------------------- composition move
@lru_cache(maxsize=None)
def compositions(schema):
    out = []
    for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
        for a in G.BODY_ATOMS:
            for w in (tmpl.format(schema, a), tmpl.format(a, schema)):
                if len(T3D.instantiate(w)) >= 2:
                    out.append(w)
    return list(dict.fromkeys(out))


def start_library(kind, panel):
    """kind: 'P' (PRISTINE) or a panel key ('G1', 'SHAM_0', 'RANDOM_0', ...)."""
    if kind == "P":
        return FR.pristine().entries, []
    s = panel[kind]
    return [a17.schema_entry("inherited", s)] + FR.pristine().entries, [s]


# ---------------------------------------------------------------- exact screen
def hits_any_cell(schema, cells):
    """True iff the schema's entry (inits H1 x instantiations x FINAL_SPACE)
    contains a program consistent with the dev examples of at least one cell.
    A candidate that fails this can only ADD cost on every cell (its entry is
    walked first and never hits), so its paired saving is <= 0 everywhere and it
    can never be eligible: dropping it cannot change the selection. Exact."""
    sys.path.insert(0, str(HERE / "accel"))
    import fasteval as FE
    bodies = T3D.instantiate(schema)
    for cell in cells:
        ex = cell.parsed
        pinfo = [(n[:-1], n[0], n[-1], (n[:-1][-1] if len(n) > 1 else 0), gold) for n, gold in ex]
        for b in bodies:
            bfn = FE.fn(b)
            for i in G.H1_SPACE:
                ifn = FE.fn(i)
                accs = [FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _vl, _g in pinfo]
                if any(a is FE._FAIL for a in accs):
                    continue
                for f in G.FINAL_SPACE:
                    ffn = FE.fn(f)
                    if all(str(FE._final(ffn, a, vl, fst, lst)) == gold
                           for a, (_v, fst, lst, vl, gold) in zip(accs, pinfo)):
                        return True
    return False


# ---------------------------------------------------------------- the donor (C1)
def donor(args):
    """a17.donor + composition candidates. Records the full trace and the
    ladder stages that are knowable at donor level."""
    worker_init()
    import ruler_v2 as R
    cat, kind, r, fams, specs, panel, compose = args
    t0 = time.perf_counter()
    prov = a17.Prov(specs)
    start, held = start_library(kind, panel)
    base, cov = FR.KLib(start), a17.coverage(start)
    size = {f["name"]: f["qualified_dev_size"] for f in fams}
    obs_f = [f["name"] for f in fams if f["role"] == "OBSERVE"]
    val_f = [f["name"] for f in fams if f["role"] == "VALIDATE"]
    meta, observed = 0, []
    for fam in obs_f:
        for c in range(a17.R_OBS):
            cell = FR.Cell(prov, fam, r * a17.R_OBS + c, size[fam], label="%s-%s-obs/r%d" % (TAG, cat, r))
            esc = E.Escrow(a17.ESCROW)
            hits = FR.search_collect(base, cell.parsed, esc, a17.ESCROW, cell.seed, max_hits=1)
            meta += esc.spent
            if hits:
                observed.append({"family": fam, "program": list(hits[0][0]), "parsed": cell.parsed})
    classes, certs = a17.certified_classes(observed, cov)
    derived = T3D.derive_schemas([c["member_bodies"] for c in classes])
    cells = [FR.Cell(prov, f, r * a17.R_VAL + j, size[f], label="%s-%s-val/r%d" % (TAG, cat, r))
             for f in val_f for j in range(a17.R_VAL)]
    raw = [{"schema": w, "origin": "COMPOSITION", "of": s} for s in held for w in compositions(s)] if compose else []
    comp = [c for c in raw if hits_any_cell(c["schema"], cells)]      # exact screen (AMENDMENT 18 s0)
    cands = a17.candidates_from(derived, start, classes)              # SCHEMA_ALL over LGG-derived only
    for k, c in enumerate(comp):
        cands["SCHEMA_%d" % (len(derived) + k)] = [a17.schema_entry("g2_new", c["schema"])] + start
    chosen, table, vcost = a17.select(cands, start, cells)
    meta += vcost
    allc = derived + comp
    sel = None
    if chosen.startswith("SCHEMA_") and chosen != "SCHEMA_ALL":
        sel = allc[int(chosen.split("_")[1])]["schema"]
    sp = R.span_of_schema(G1)
    tsp = R.traj_span(R.reexpression_bodies(G1))
    sel_v = R.verdict_full(sel, G1, sp, tsp) if sel else None
    rel_held = R.relations(sel, held[0]) if (sel and held) else None
    return {"catalog": cat, "donor": kind, "replicate": r, "compose": compose,
            "n_derived": len(derived), "n_composed_raw": len(raw), "n_composed_candidates": len(comp),
            "observed_families": sorted({o["family"] for o in observed}), "classes": len(classes),
            "selected": chosen, "selected_schema": sel,
            "selected_origin": (allc[int(chosen.split("_")[1])].get("origin", "LGG")
                                if sel else None),
            "selected_entries": cands[chosen],
            "selection_table": {k: {x: v[x] for x in ("mean_paired_saving", "lower95_one_sided", "eligible")}
                                for k, v in table.items()},
            "NOVELTY_vs_G1": bool(sel_v and sel_v["NEW_FINAL"]),
            "COMPOSES_held": bool(rel_held and rel_held["COMPOSES"]),
            "REFINES_held": bool(rel_held and rel_held["REFINES"]),
            "meta_charges": meta, "seconds": round(time.perf_counter() - t0, 1)}


if __name__ == "__main__":
    use_world("W5")
    print(len(G.BODY_SPACE), len(compositions(G1)), compositions(G1)[:6])


# ---------------------------------------------------------------- panel and supply
def _random_schema(rng):
    b = rng.choice(G.BODY_SPACE[:10842] if len(G.BODY_SPACE) > 10842 else G.BODY_SPACE)
    t = I.normalise(I.parse(b))
    paths = []

    def walk(x, p):
        for i, a in enumerate(x[1]):
            paths.append(p + (i,))
            walk(a, p + (i,))
    walk(t, ())
    if not paths:
        return None
    path = rng.choice(paths)

    def put(x, p):
        if not p:
            return ("hole", [])
        op, args = x
        args = list(args)
        args[p[0]] = put(args[p[0]], p[1:])
        return (op, args)
    return T3D.schema_src(put(t, path))


def build_panel(n_sham=4, n_off=1, seed="APHRODITE/A18/PANEL/v1"):
    """G1 + n_sham matched sham abstractions (ON-path controls: their
    compositions ARE supplied) + n_off OFF-path schemas (inherited, never
    supplied). Every panel schema: NEW_FINAL vs G1 (a genuinely different
    abstraction), >= 20 accumulating W5 instantiations, >= 20 compositions."""
    import ruler_v2 as R
    use_world("W5")
    sp, tsp = R.span_of_schema(G1), R.traj_span(R.reexpression_bodies(G1))
    rng = random.Random(I._seed(seed))
    panel, tries = {"G1": G1}, 0
    need = [("SHAM_%d" % k) for k in range(n_sham)] + [("OFF_%d" % k) for k in range(n_off)]
    seen = {G1}
    while need and tries < 20000:
        tries += 1
        s = _random_schema(rng)
        if not s or s in seen:
            continue
        seen.add(s)
        v = R.verdict_full(s, G1, sp, tsp)
        if not v["NEW_FINAL"] or v["accumulating"] < 20:
            continue
        if len(compositions(s)) < 20:
            continue
        panel[need.pop(0)] = s
    return panel


def supply_bodies(panel, on_path_keys):
    """Constructed supply: for each ON-path panel schema, the accumulating
    in-space instantiations of its compositions (equal share per schema)."""
    import ruler_v2 as R
    out = {}
    for k in on_path_keys:
        bodies = []
        for w in compositions(panel[k]):
            bodies += [b for b in T3D.instantiate(w) if R.accumulating(b)]
        out[k] = sorted(set(bodies))
    return out


# ---------------------------------------------------------------- exact fast cost (gated)
def fast_cost(lib, cell, escrow=None):
    """Exact re-implementation of fair.Cell.cost(lib): walks lib.candidates in
    the IDENTICAL order (same keyed() calls) but evaluates each (init, body)
    accumulator once per example and memoises final checks per accumulator
    tuple. Returns (charge_of_first_hit or escrow, program or None). Admitted
    only when gate_fast_cost() reports 0 mismatches."""
    sys.path.insert(0, str(HERE / "accel"))
    import fasteval as FE
    escrow = escrow or a17.ESCROW
    seed = cell.seed
    pinfo = [(n[:-1], n[0], n[-1], (n[:-1][-1] if len(n) > 1 else 0), gold) for n, gold in cell.parsed]
    n = 0
    def check_finals(accs, finals, prog_head):
        nonlocal n
        for f in finals:
            if n >= escrow:
                return None
            n += 1
            ffn = FE.fn(f)
            ok = True
            for a, (_v, fst, lst, vl, gold) in zip(accs, pinfo):
                got = FE._final(ffn, a, vl, fst, lst)
                if got is None or str(got) != gold:
                    ok = False
                    break
            if ok:
                return prog_head + (f,)
        return None

    def block(inits, bodies, finals):
        nonlocal n
        for i in inits:
            ifn = FE.fn(i)
            for b in bodies:
                if n >= escrow:
                    return None
                bfn = FE.fn(b)
                accs = [FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _vl, _g in pinfo]
                if any(a is FE._FAIL for a in accs):
                    n = min(escrow, n + len(finals))
                    continue
                hit = check_finals(accs, finals, ("fold", i, b))
                if hit:
                    return hit
        return None

    for e, bodies in zip(lib.entries, lib._bodies):
        hit = block(FR.keyed(e["inits"], seed, "init"), FR.keyed(bodies, seed, "body"),
                    FR.keyed(e["finals"], seed, "final"))
        if hit:
            return n, hit
        if n >= escrow:
            return escrow, None
    fs = FR.keyed(G.FINAL_SPACE, seed, "g4final")
    for f in fs:
        if n >= escrow:
            return escrow, None
        n += 1
        ffn = FE.fn(f)
        ok = True
        for _v, fst, lst, _vl, gold in pinfo:
            got = FE._final(ffn, 0, 0, fst, lst)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok:
            return n, ("expr", f)
    hit = block(FR.keyed(G.INIT_SPACE, seed, "g4init"), FR.keyed(G.BODY_SPACE, seed, "g4body"), fs)
    return (n, hit) if hit else (escrow, None)


def install_fast_cost():
    if os.environ.get("A18_FASTCOST") == "1":
        FR.Cell.cost = lambda self, lib, escrow=a17.ESCROW: fast_cost(lib, self, escrow)


def gate_fast_cost(n_pairs=400, seed="APHRODITE/A18/FASTCOST-GATE/v1"):
    """Differential gate: fast_cost vs the reference Cell.cost on random
    (library, cell) pairs in the current world. Libraries: PRISTINE, L1,
    G1-composition candidates, random-schema entries; cells: random W5
    families (including unsolvable ones, so fallback walks are exercised)."""
    rng = random.Random(I._seed(seed))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    libs = [FR.pristine().entries, a17.L1_entries()]
    for w in rng.sample(compositions(G1), 6):
        libs.append([a17.schema_entry("g2_new", w)] + FR.pristine().entries)
    mism, rows = [], 0
    ref_cost = FR.Cell.cost.__wrapped__ if hasattr(FR.Cell.cost, "__wrapped__") else FR.Cell.cost
    for k in range(n_pairs):
        body = rng.choice(G.BODY_SPACE)
        spec = {"gatefam": (body, rng.choice(finals), rng.choice(G.H1_SPACE))}
        prov = a17.Prov(spec)
        cell = FR.Cell(prov, "gatefam", k, rng.choice([4, 6, 8]), label="A18-FASTCOST-GATE")
        lib = FR.KLib(rng.choice(libs))
        a = ref_cost(cell, lib)
        b = fast_cost(lib, cell)
        rows += 1
        if a[0] != b[0] or (a[1] is None) != (b[1] is None) or (a[1] and tuple(a[1]) != tuple(b[1])):
            mism.append([list(spec["gatefam"]), a[0], b[0]])
    return {"pairs": rows, "mismatches": len(mism), "examples": mism[:5]}
