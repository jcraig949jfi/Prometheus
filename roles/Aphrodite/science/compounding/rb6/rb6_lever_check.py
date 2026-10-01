"""RB-6 LEVER CHECK -- forensic, not a disposition.

Question: does the fixed improver (a17.donor: observe -> certified classes ->
single-hole LGG -> paired selection) have LEVERS in this DSL? I.e. do hand-set
improver variants, run on the SAME observations with the SAME fixed initial
library, select DIFFERENT schemas?

Variants (all share one observe stage per supply, so differences are due to the
improver alone, not to observation noise):
  V0_BASE    single-hole LGG; select by paired mean saving vs INHERITED with the
             one-sided 95% gate (a17.select, reproduced over cached costs).
  V1_H2ONLY  exactly-two-hole LGG candidates (plus INHERITED / MEMORISE).
  V1_H12     one- or two-hole LGG candidates.
  V2_LOOK    single-hole candidates; among gate-eligible ones select by a
             2-step LOOKAHEAD (CMP proxy): the number of distinct single-hole
             schemas the NEXT generation could derive from the same
             observations with the candidate library's coverage that are not
             already in this generation's candidate set; ties -> V0 order.
  V3_MEDIAN  single-hole; select by median paired saving (gate unchanged).
             (Free: reuses V0 costs.)
Measured per supply and variant: the selected candidate, its schema(s), its
paired saving on the selection cells (V1-like efficiency), whether the
selected schema is G1-built (V3-like compounding proxy: a non-trivial
'(acc + ...)' schema), the tribunal-free ruler flag (V4 proxy, tier3e
semantics, KNOWN false-positive channels), and the paired saving on a
HELD-OUT set of cells of the validate families (fresh labels).

Supplies: the K5 regime reconstruction (same rng string as K5), a subset.
Fixed initial library: L1 (= [G1] + PRISTINE), the donor_G1 start, because
that is where K5 found selectable compounding; PRISTINE optionally.
Labels are forensic ("RB6-..."). <= 2 workers. Engine files are imported,
never modified.
"""
import json
import os
import random
import statistics
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
APH = HERE.parents[2]
ENG = APH / "engine"
SPK = APH / "science" / "frontier" / "spikes"
sys.path.insert(0, str(ENG))
os.environ["A17_FASTEVAL"] = "1"
import a17  # noqa: E402
import engine as E  # noqa: E402
import fair as FR  # noqa: E402
import identity as I  # noqa: E402
import tier3d as T3D  # noqa: E402
import tier3e as T3E  # noqa: E402
import basis_v4 as G  # noqa: E402

LET = "abcdefghijklmnopqrstuvwxyz"
R_HOLD = 4
MAX_H2 = 10          # cap on two-hole schemas validated per supply (by n_pairs)


def fam_name(i):
    return "kf_%s%s%s" % (LET[i // 676 % 26], LET[i // 26 % 26], LET[i % 26])


# ------------------------------------------------------------ two-hole LGG
def derive_multi(member_bodies_by_class, max_holes):
    """As tier3d.derive_schemas but keeps LGGs with 1..max_holes DISTINCT holes
    (non-root). Returns {n_holes: [{schema_term, schema, n_pairs}]}."""
    found = {}
    for ci in range(len(member_bodies_by_class)):
        for cj in range(ci + 1, len(member_bodies_by_class)):
            for a in member_bodies_by_class[ci]:
                ta = I.normalise(I.parse(a))
                for b in member_bodies_by_class[cj]:
                    tb = I.normalise(I.parse(b))
                    g, table = T3D.lgg(ta, tb)
                    if not (1 <= len(table) <= max_holes) or g[0].startswith("hole"):
                        continue
                    key = src_multi(g)
                    if key not in found:
                        found[key] = {"term": g, "n_holes": len(table), "n_pairs": 0}
                    found[key]["n_pairs"] += 1
    return found


def src_multi(t):
    op, args = t
    if op.startswith("hole"):
        return "{H%s}" % op.split(":")[1]
    if op.startswith("var:") or op.startswith("const:"):
        return I.to_src(t)
    return T3D._emit(op, [src_multi(a) for a in args])


_FILL = None


def fillers():
    global _FILL
    if _FILL is None:
        _FILL = [I.parse(f) for f in FR.LEVEL1]
        T3D.in_space_body("acc")            # initialise the structure map
    return _FILL


def depth_of_holes(t, d=0, out=None):
    if out is None:
        out = {}
    op, args = t
    if op.startswith("hole"):
        out[op] = max(out.get(op, 0), d)
    for a in args:
        depth_of_holes(a, d + 1, out)
    return out


def subst(t, env):
    op, args = t
    if op.startswith("hole"):
        return env[op]
    return (op, [subst(a, env) for a in args])


def instantiate_multi(term):
    """In-space instantiations of a multi-hole schema: every LEVEL1 filler per
    hole, normalised, mapped to its structurally identical BODY_SPACE body
    (the Tier-3C filler rule, as tier3d.instantiate)."""
    F = fillers()
    atoms = [f for f in F if not f[1]]
    holes = sorted(depth_of_holes(term).items())
    pools = [atoms if d >= 2 else F for _h, d in holes]
    out = []

    def rec(k, env):
        if k == len(holes):
            s = I.term_str(I.normalise(subst(term, env)))
            b = T3D._STRUCT_TO_BODY.get(s)
            if b is not None:
                out.append(b)
            return
        for f in pools[k]:
            env[holes[k][0]] = f
            rec(k + 1, env)
    rec(0, {})
    return list(dict.fromkeys(out))


def ruler_new(bodies):
    new = [b for b in bodies if T3E._mentions(b, "v") and T3E.body_key(b) not in T3E.g1_mechanisms()]
    return bool(new), len(new)


def g1_built(schema):
    return schema.startswith("(acc + ") and schema not in ("(acc + {H})", "(acc + {H0})")


# ------------------------------------------------------------ one supply
def run_supply(args):
    a17.worker_init()
    key, fams, specs, start_kind = args
    t0 = time.perf_counter()
    prov = a17.Prov(specs)
    a17.M.use_provider(prov)
    start = a17.L1_entries() if start_kind == "L1" else FR.pristine().entries
    base, cov = FR.KLib(start), a17.coverage(start)
    size = {f["name"]: f["qualified_dev_size"] for f in fams}
    obs_f = [f["name"] for f in fams if f["role"] == "OBSERVE"]
    val_f = [f["name"] for f in fams if f["role"] == "VALIDATE"]
    lab = "RB6-%s-%s" % (key, start_kind)
    observed, obs_charges = [], 0
    for fam in obs_f:
        for c in range(a17.R_OBS):
            cell = FR.Cell(prov, fam, c, size[fam], label=lab + "-obs")
            esc = E.Escrow(a17.ESCROW)
            hits = FR.search_collect(base, cell.parsed, esc, a17.ESCROW, cell.seed, max_hits=1)
            obs_charges += esc.spent
            if hits:
                observed.append({"family": fam, "program": list(hits[0][0]), "parsed": cell.parsed})
    classes, _certs = a17.certified_classes(observed, cov)
    mb = [c["member_bodies"] for c in classes]
    multi = derive_multi(mb, 2)
    one = [{"schema": T3D.schema_src(v["term"]), "bodies": T3D.instantiate(T3D.schema_src(v["term"])),
            "n_pairs": v["n_pairs"], "holes": 1} for v in multi.values() if v["n_holes"] == 1]
    # sanity: our 1-hole set must equal tier3d.derive_schemas
    ref = sorted(d["schema"] for d in T3D.derive_schemas(mb))
    assert sorted(o["schema"] for o in one) == ref, (ref, [o["schema"] for o in one])
    two_all = [v for v in multi.values() if v["n_holes"] == 2]
    two_all.sort(key=lambda v: (-v["n_pairs"], src_multi(v["term"])))
    two = []
    for v in two_all:
        bodies = instantiate_multi(v["term"])
        if len(bodies) >= 2:
            two.append({"schema": src_multi(v["term"]), "bodies": bodies, "n_pairs": v["n_pairs"], "holes": 2})
        if len(two) >= MAX_H2:
            break
    # candidate libraries (a17.candidates_from shape; entries carry explicit bodies)
    def entry(name, bodies):
        return {"name": name, "inits": list(G.H1_SPACE), "bodies": list(bodies), "finals": list(G.FINAL_SPACE)}
    mem = sorted({b for c in classes for b in c["member_bodies"]})
    cands = {"INHERITED": start, "MEMORISE": [entry("memorised", mem)] + start}
    for k, d in enumerate(one):
        cands["S1_%d" % k] = [entry("g2_new", d["bodies"])] + start
    if len(one) > 1:
        cands["S1_ALL"] = [entry("g2_new", dict.fromkeys(b for d in one for b in d["bodies"]))] + start
    for k, d in enumerate(two):
        cands["S2_%d" % k] = [entry("g2_new", d["bodies"])] + start
    if len(two) > 1:
        cands["S2_ALL"] = [entry("g2_new", dict.fromkeys(b for d in two for b in d["bodies"]))] + start
    if one and two:
        cands["S12_ALL"] = [entry("g2_new", dict.fromkeys(b for d in one + two for b in d["bodies"]))] + start
    # costs on selection cells (a17 geometry: R_VAL cells per validate family) + held-out cells
    sel_cells = [FR.Cell(prov, f, j, size[f], label=lab + "-val") for f in val_f for j in range(a17.R_VAL)]
    hold_cells = [FR.Cell(prov, f, j, size[f], label=lab + "-hold") for f in val_f for j in range(R_HOLD)]
    cache = {}

    def costs(name, cells, tag):
        lib = FR.KLib(cands[name])
        k = (lib.sha256(), tag)
        if k not in cache:
            cache[k] = [c.cost(lib)[0] for c in cells]
        return cache[k]
    sel_cost = {n: costs(n, sel_cells, "sel") for n in cands}
    rows = {}
    for n in cands:
        r = FR.paired_summary(sel_cost["INHERITED"], sel_cost[n])
        d = [p - c for p, c in zip(sel_cost["INHERITED"], sel_cost[n])]
        r["median_paired_saving"] = statistics.median(d)
        r["size"] = FR.KLib(cands[n]).size()
        r["eligible"] = n != "INHERITED" and r["lower95_one_sided"] > 0
        rows[n] = r

    def pick(names, score):
        el = [n for n in names if rows[n]["eligible"]]
        if not el:
            return "INHERITED"
        def neg(x):
            return tuple(-y for y in x) if isinstance(x, tuple) else (-x,)
        return min(el, key=lambda n: neg(score(n)) + (rows[n]["size"], n))
    base_names = ["INHERITED", "MEMORISE"] + [n for n in cands if n.startswith("S1_")]
    h2_names = ["INHERITED", "MEMORISE"] + [n for n in cands if n.startswith("S2_")]
    h12_names = base_names + [n for n in cands if n.startswith("S2_") or n == "S12_ALL"]
    sel = {"V0_BASE": pick(base_names, lambda n: rows[n]["mean_paired_saving"]),
           "V1_H2ONLY": pick(h2_names, lambda n: rows[n]["mean_paired_saving"]),
           "V1_H12": pick(h12_names, lambda n: rows[n]["mean_paired_saving"]),
           "V3_MEDIAN": pick(base_names, lambda n: rows[n]["median_paired_saving"])}
    # V2 lookahead: next-generation derivable single-hole schemas from each eligible S1 candidate
    this_gen = {d["schema"] for d in one}
    look = {}
    for n in base_names:
        if not rows[n]["eligible"]:
            continue
        cov_n = a17.coverage(cands[n])
        cls_n, _ = a17.certified_classes(observed, cov_n)
        nxt = {d["schema"] for d in T3D.derive_schemas([c["member_bodies"] for c in cls_n])}
        look[n] = {"next_gen": len(nxt), "fresh": sorted(nxt - this_gen)}
    sel["V2_LOOK"] = pick(base_names, lambda n: (len(look.get(n, {}).get("fresh", [])),
                                                 rows[n]["mean_paired_saving"]))

    def schemas_of(n):
        if n in ("INHERITED", "MEMORISE"):
            return []
        grp, idx = n.split("_", 1)
        pool = {"S1": one, "S2": two, "S12": one + two}[grp]
        if idx == "ALL":
            return [d["schema"] for d in pool]
        return [pool[int(idx)]["schema"]]

    def bodies_of(n):
        return [b for e in cands[n][:1] for b in e["bodies"]] if n not in ("INHERITED",) else []
    hold_base = costs("INHERITED", hold_cells, "hold")
    out = {}
    for v, n in sel.items():
        hc = costs(n, hold_cells, "hold")
        hs = FR.paired_summary(hold_base, hc)
        sch = schemas_of(n)
        rn = ruler_new(bodies_of(n)) if sch else (False, 0)
        out[v] = {"selected": n, "schemas": sch, "sel_mean_saving": rows[n]["mean_paired_saving"],
                  "hold_mean_saving": hs["mean_paired_saving"], "hold_lower95": hs["lower95_one_sided"],
                  "g1_built": any(g1_built(s) for s in sch), "ruler_new": rn[0], "ruler_new_bodies": rn[1],
                  "lib_size": rows[n]["size"]}
    return {"supply": key, "start": start_kind, "n_observed": len(observed), "n_classes": len(classes),
            "one_hole": [(d["schema"], len(d["bodies"]), d["n_pairs"]) for d in one],
            "two_hole_total": len(two_all),
            "two_hole_validated": [(d["schema"], len(d["bodies"]), d["n_pairs"]) for d in two],
            "table": {n: {k: rows[n][k] for k in ("mean_paired_saving", "median_paired_saving",
                                                  "lower95_one_sided", "eligible", "size")} for n in rows},
            "lookahead": look, "variants": out, "obs_charges": obs_charges,
            "seconds": round(time.perf_counter() - t0, 1)}


def supplies(which):
    rows = json.loads((SPK / "K2_ADMISSIBLE_SOLVABILITY.json").read_text())["rows"]
    pool = []
    for i, r in enumerate(rows):
        if r["Q2_size"] is None or r["PRISTINE"]["solved"] + r["L1"]["solved"] == 0:
            continue
        pool.append(dict(r, name=fam_name(i)))
    ng = [r for r in pool if not r["g1_body"]]
    g1 = [r for r in pool if r["g1_body"]]
    gcd = [r for r in ng if r["op"] == "gcd"]
    rng = random.Random("APHRODITE/FRONTIER/K5/v1")      # K5's regime draw, reproduced
    regimes = {}
    for k in range(6):
        if len(gcd) >= 7:
            s = rng.sample(gcd, 7)
            regimes["GCD_RICH_%d" % k] = (s[:4], s[4:])
        s = rng.sample(ng, 7)
        regimes["NONG1_MIX_%d" % k] = (s[:4], s[4:])
        a, b = rng.sample(g1, 2), rng.sample(ng, 5)
        regimes["G1_PLUS_%d" % k] = (a + b[:2], b[2:])
    out = []
    for key in which:
        obs, val = regimes[key]
        fams = ([dict(f, role="OBSERVE", qualified_dev_size=f["Q2_size"]) for f in obs]
                + [dict(f, role="VALIDATE", qualified_dev_size=f["Q2_size"]) for f in val])
        specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fams}
        out.append((key, fams, specs))
    return out


if __name__ == "__main__":
    which = sys.argv[1].split(",")
    start_kind = sys.argv[2] if len(sys.argv) > 2 else "L1"
    tag = sys.argv[3] if len(sys.argv) > 3 else "run"
    jobs = [(k, f, s, start_kind) for k, f, s in supplies(which)]
    t0 = time.perf_counter()
    res = []
    with ProcessPoolExecutor(2, initializer=a17.worker_init) as ex:
        for r in ex.map(run_supply, jobs, chunksize=1):
            res.append(r)
            with open(HERE / ("RB6_LEVER_CHECK_%s.partial.jsonl" % tag), "a") as fh:   # survives a kill
                fh.write(json.dumps(r, default=str) + "\n")
            print(r["supply"], r["start"], "classes", r["n_classes"], "1h", len(r["one_hole"]),
                  "2h", r["two_hole_total"], "->", len(r["two_hole_validated"]), "sec", r["seconds"], flush=True)
            for v, o in r["variants"].items():
                print("   %-10s %-9s %-60s sel %9.0f hold %9.0f g1b %d new %d" % (
                    v, o["selected"], ";".join(o["schemas"])[:60], o["sel_mean_saving"],
                    o["hold_mean_saving"], o["g1_built"], o["ruler_new"]), flush=True)
    spread = Counter()
    for r in res:
        v = r["variants"]
        base = v["V0_BASE"]["selected"], tuple(v["V0_BASE"]["schemas"])
        for name, o in v.items():
            spread[name] += (o["selected"], tuple(o["schemas"])) != base
    summary = {"n_supplies": len(res), "differs_from_V0": dict(spread),
               "distinct_selections_per_supply": [len({tuple(o["schemas"]) for o in r["variants"].values()}) for r in res],
               "wall_seconds": round(time.perf_counter() - t0, 1)}
    print(json.dumps(summary))
    (HERE / ("RB6_LEVER_CHECK_%s.json" % tag)).write_text(json.dumps(
        {"forensic": "RB6 lever check -- forensic, not a disposition", "start": start_kind,
         "summary": summary, "rows": res}, indent=1, default=str))
