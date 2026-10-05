"""R7 probe apparatus: GENOME-PARAMETERISED DONOR (donor_g) for the W4 GTC (genome transfer-correlation) probe.

The improver's mutable object is a RULE that maps the donor's own traces to its next search/selection behaviour.
It is never content (W4 s0.1): a content-like parameter would be a library in disguise.
donor_g(genome, args) is a COPY of a18.donor (unchanged logic) with genome hooks. With genome g0 it must equal
a18.donor exactly. That is the conformance gate (conformance_g0()).

Genomes (W4 s6.2):
  g0  I_0: the ancestral improver (a18.donor)
  g2  hits_per_obs = 2: observation keeps up to 2 hits per OBSERVE cell (more traces; content-free)
  g3  trace-frequency proposal ORDER: each candidate entry is split so that bodies whose top-level operator is the
      most frequent operator among the donor's own SOLVED observation programs are walked first (recomputed from
      zero per donor; Probe's lesson: update only from solved programs)
  g4  replace-subsumed insertion: a candidate entry replaces START entries whose bodies it subsumes
  g5  observed-finals (P15, the PLANTED OVERFITTER): candidate entry finals := the finals of the donor's observed
      programs. W4 P-B: 37x smaller entries, but they cover only about 9% of transfer finals
  (g1 P18 dovetail is DEFERRED: it needs a rewrite of the search loop. Declared, not hidden.)
"""
import time
from collections import Counter

import paths  # noqa: F401
import a17
import a18
from a18 import FR, G, T3D, E

GENOMES = {
    "g0": {},
    "g2": {"hits_per_obs": 2},
    "g3": {"order": "trace_freq"},
    "g4": {"insert": "replace_subsumed"},
    "g5": {"finals": "observed"},
    # R7E (DEV-7): endogenous-route rules (content-free) + known-answer controls
    "g8": {"select": "mean_positive"},          # selection eligibility: mean paired saving > 0 (I_0: lower95 > 0)
    "g9": {"derive_from": "observe+validate"},  # LGG derivation also from VALIDATE-cell hits (more traces)
    "ORACLE": {"plant": "G1"},                  # positive control: G1 schema entry offered as an extra candidate
    "NULL": {"plant": "OFF"},                   # negative control: an OFF schema entry offered as an extra candidate
    # T09 (DEV-9): subset-benefit selection criterion (content-free) + its planted controls
    "g10": {"select": "subset"},
    "ORACLE10": {"plant": "G1", "select": "subset"},
    "NULL10": {"plant": "OFF", "select": "subset"},
}
SUBSET_TAU = 1000          # a material per-family saving (charges)
OFF_SCHEMA = "math.gcd(abs((acc // {H})), abs(first))"   # A22/A23 OFF_0


def _top_op(body):
    """Top-level operator of a body expression: gcd / pow / + - * // % at paren depth 1 / atom."""
    b = body.strip()
    if b.startswith("math.gcd"):
        return "gcd"
    if b.startswith("pow("):
        return "pow"
    depth = 0
    for i, ch in enumerate(b):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 1:
            for op in (" // ", " + ", " - ", " * ", " % "):
                if b.startswith(op, i):
                    return op.strip()
    return "atom"


def _apply(genome, entry, start, observed):
    """Return the candidate library [entry'] + start' under the genome's rules (g0: [entry] + start)."""
    g = GENOMES[genome]
    e = dict(entry)
    if g.get("finals") == "observed":
        fin = sorted({o["program"][3] for o in observed if o["program"][0] == "fold"})
        if fin:
            e["finals"] = fin
    st = list(start)
    if g.get("insert") == "replace_subsumed":
        eb = set(e["bodies"]) if e.get("bodies") is not None else set(T3D.instantiate(e.get("schema") or ""))
        st = [s for s in st if not (s.get("bodies") and set(s["bodies"]) <= eb and set(s["inits"]) <= set(e["inits"])
                                    and set(s["finals"]) <= set(e["finals"]))]
    if g.get("order") == "trace_freq":
        ops = Counter(_top_op(o["program"][2]) for o in observed if o["program"][0] == "fold")
        if ops:
            top = ops.most_common(1)[0][0]
            bodies = e["bodies"] if e.get("bodies") is not None else T3D.instantiate(e["schema"])
            first = [b for b in bodies if _top_op(b) == top]
            rest = [b for b in bodies if _top_op(b) != top]
            if first and rest:
                e1 = dict(e, bodies=first, name=e.get("name", "g2_new") + "_tf")
                e2 = dict(e, bodies=rest)
                return [e1, e2] + st
    return [e] + st


def _select_mean_positive(cands, start, cells):
    """a17.select with ONE rule changed: eligible iff mean paired saving > 0 (I_0 requires lower95 > 0)."""
    libs = {n: FR.KLib(e) for n, e in cands.items()}
    costs = {n: [c.cost(l)[0] for c in cells] for n, l in libs.items()}
    table = {}
    for n in cands:
        row = FR.paired_summary(costs["INHERITED"], costs[n])
        row.update({"sha256": libs[n].sha256(), "size": libs[n].size(),
                    "eligible": n != "INHERITED" and row["mean_paired_saving"] > 0})
        table[n] = row
    elig = [n for n in table if table[n]["eligible"]]
    chosen = (min(elig, key=lambda n: (-table[n]["mean_paired_saving"], table[n]["size"], table[n]["sha256"]))
              if elig else "INHERITED")
    return chosen, table, sum(sum(v) for v in costs.values())


def _select_subset(cands, start, cells):
    """Subset-benefit criterion. Per candidate and per VALIDATE family f, s_f = the mean paired saving over f's cells.
    G = sum of positive s_f; L = -(sum of negative s_f). Eligible iff some s_f >= SUBSET_TAU AND L <= G. Choose the max
    (G - L), with ties broken by size and then sha256. I_0 instead requires lower95 > 0 over ALL cells pooled."""
    from collections import defaultdict
    libs = {n: FR.KLib(e) for n, e in cands.items()}
    costs = {n: [c.cost(l)[0] for c in cells] for n, l in libs.items()}
    fam_of = [c.family if hasattr(c, "family") else getattr(c, "name", str(i)) for i, c in enumerate(cells)]
    table = {}
    for n in cands:
        per = defaultdict(list)
        for f, a, b in zip(fam_of, costs["INHERITED"], costs[n]):
            per[f].append(a - b)
        sf = {f: sum(v) / len(v) for f, v in per.items()}
        G = sum(x for x in sf.values() if x > 0)
        L = -sum(x for x in sf.values() if x < 0)
        row = FR.paired_summary(costs["INHERITED"], costs[n])
        row.update({"sha256": libs[n].sha256(), "size": libs[n].size(), "G": G, "L": L,
                    "eligible": n != "INHERITED" and max(sf.values(), default=0) >= SUBSET_TAU and L <= G})
        table[n] = row
    elig = [n for n in table if table[n]["eligible"]]
    chosen = (min(elig, key=lambda n: (-(table[n]["G"] - table[n]["L"]), table[n]["size"], table[n]["sha256"]))
              if elig else "INHERITED")
    return chosen, table, sum(sum(v) for v in costs.values())


def donor_g(genome, args):
    """a18.donor with genome hooks. args = (cat, kind, r, fams, specs, panel, compose)."""
    a18.worker_init()
    import ruler_v2 as R
    g = GENOMES[genome]
    cat, kind, r, fams, specs, panel, compose = args[:7]
    start_override = args[7] if len(args) > 7 else None
    t0 = time.perf_counter()
    prov = a17.Prov(specs)
    if start_override is not None:
        start, held = start_override, []
    else:
        start, held = a18.start_library(kind, panel)
    base, cov = FR.KLib(start), a17.coverage(start)
    size = {f["name"]: f["qualified_dev_size"] for f in fams}
    obs_f = [f["name"] for f in fams if f["role"] == "OBSERVE"]
    val_f = [f["name"] for f in fams if f["role"] == "VALIDATE"]
    meta, observed = 0, []
    mh = g.get("hits_per_obs", 1)
    for fam in obs_f:
        for c in range(a17.R_OBS):
            cell = FR.Cell(prov, fam, r * a17.R_OBS + c, size[fam], label="%s-%s-obs/r%d" % (a18.TAG, cat, r))
            esc = E.Escrow(a17.ESCROW)
            hits = FR.search_collect(base, cell.parsed, esc, a17.ESCROW, cell.seed, max_hits=mh)
            meta += esc.spent
            for h in hits[:mh]:
                observed.append({"family": fam, "program": list(h[0]), "parsed": cell.parsed})
    if g.get("derive_from") == "observe+validate":
        for fam in val_f:
            for c in range(a17.R_OBS):
                cell = FR.Cell(prov, fam, r * a17.R_OBS + c, size[fam], label="%s-%s-obsv/r%d" % (a18.TAG, cat, r))
                esc = E.Escrow(a17.ESCROW)
                hits = FR.search_collect(base, cell.parsed, esc, a17.ESCROW, cell.seed, max_hits=mh)
                meta += esc.spent
                for h in hits[:mh]:
                    observed.append({"family": fam, "program": list(h[0]), "parsed": cell.parsed})
    classes, certs = a17.certified_classes(observed, cov)
    derived = T3D.derive_schemas([c["member_bodies"] for c in classes])
    cells = [FR.Cell(prov, f, r * a17.R_VAL + j, size[f], label="%s-%s-val/r%d" % (a18.TAG, cat, r))
             for f in val_f for j in range(a17.R_VAL)]
    raw = [{"schema": w, "origin": "COMPOSITION", "of": s} for s in held for w in a18.compositions(s)] if compose else []
    comp = [c for c in raw if a18.hits_any_cell(c["schema"], cells)]
    cands = a17.candidates_from(derived, start, classes)
    for k, c in enumerate(comp):
        cands["SCHEMA_%d" % (len(derived) + k)] = [a17.schema_entry("g2_new", c["schema"])] + start
    if genome != "g0":
        for name in list(cands):
            if name == "INHERITED":
                continue
            ent = cands[name][0]
            cands[name] = _apply(genome, ent, start, observed)
    if g.get("plant"):
        sch = a18.G1 if g["plant"] == "G1" else OFF_SCHEMA
        cands["SCHEMA_%d" % (len(derived) + len(comp))] = [a17.schema_entry("g2_new", sch)] + start
        comp = comp + [{"schema": sch, "origin": "PLANTED_" + g["plant"]}]
    if g.get("select") == "mean_positive":
        chosen, table, vcost = _select_mean_positive(cands, start, cells)
    elif g.get("select") == "subset":
        chosen, table, vcost = _select_subset(cands, start, cells)
    else:
        chosen, table, vcost = a17.select(cands, start, cells)
    meta += vcost
    allc = derived + comp
    sel = None
    if chosen.startswith("SCHEMA_") and chosen != "SCHEMA_ALL":
        sel = allc[int(chosen.split("_")[1])]["schema"]
    sp = R.span_of_schema(a18.G1)
    tsp = R.traj_span(R.reexpression_bodies(a18.G1))
    sel_v = R.verdict_full(sel, a18.G1, sp, tsp) if sel else None
    rel_held = R.relations(sel, held[0]) if (sel and held) else None
    return {"catalog": cat, "donor": kind, "replicate": r, "compose": compose, "genome": genome,
            "n_derived": len(derived), "n_composed_raw": len(raw), "n_composed_candidates": len(comp),
            "observed_families": sorted({o["family"] for o in observed}), "n_observed": len(observed),
            "classes": len(classes), "selected": chosen, "selected_schema": sel,
            "selected_origin": (allc[int(chosen.split("_")[1])].get("origin", "LGG") if sel else None),
            "selected_entries": cands[chosen],
            "selection_table": {k: {x: v[x] for x in ("mean_paired_saving", "lower95_one_sided", "eligible")}
                                for k, v in table.items()},
            "NOVELTY_vs_G1": bool(sel_v and sel_v["NEW_FINAL"]),
            "COMPOSES_held": bool(rel_held and rel_held["COMPOSES"]),
            "REFINES_held": bool(rel_held and rel_held["REFINES"]),
            "meta_charges": meta, "seconds": round(time.perf_counter() - t0, 1)}


def conformance_g0(jobs):
    """donor_g('g0') must equal a18.donor on every job (selected schema/entries/table/meta charges)."""
    out = []
    for args in jobs:
        a = a18.donor(args)
        b = donor_g("g0", args)
        keys = ("selected", "selected_schema", "selected_entries", "selection_table", "meta_charges", "n_derived",
                "n_composed_candidates", "classes")
        out.append({"catalog": args[0], "kind": args[1], "equal": all(a[k] == b[k] for k in keys),
                    "diff": [k for k in keys if a[k] != b[k]]})
    return out
