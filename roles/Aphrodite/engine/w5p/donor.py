"""W5P donor: gtc.donor_g (unchanged logic) + bounded representation promotion + two-ledger cost accounting.

donor_w5p(genome, args, ...) is a COPY of engine/v2b/gtc.donor_g with four hooks; with an empty promotion registry
every hook is the identity and the output equals donor_g's (NO-OP CONTINUITY, tests/test_w5p.py):

  (P1) PROMOTE   every schema carried by the START library (entry "schema" / "schemas", i.e. the inherited / transplanted
                 abstractions) and every serialized promoted record an entry carries ("promoted") is loaded into a
                 registry of Promoted primitives (promote.py). The START library itself is NOT changed (transplant
                 fidelity): the walk, OBSERVE and coverage are byte-identical to donor_g's.
  (P2) RECOGNISE certified class member bodies are additionally read in promoted form (promote.forms / fold_term).
  (P3) DERIVE    promote.derive_schemas = tier3d D4 over plain bodies (exactly W5) UNION D4 over promoted forms; a
                 promoted node is one node to the LGG, so a derived schema can contain P (dependency depth 2).
  (P4) PROPOSE   candidate entries instantiate schemas with promote.instantiate (W5 filler set + P(atom) fillers; W5P
                 depth rule counting P as one node); entries store EXPANDED base bodies plus the promoted-form schema,
                 its expansion and the lineage records, so any downstream walker / tribunal runs unchanged.
After selection, every selected schema is itself promoted (record returned, never applied inside this donor): that is
the artifact a next generation inherits. The selection rule is pluggable (rule name or callable).

Cost: both ledgers are kept. search_charges = donor_g's meta_charges (1 per candidate evaluated). Execution units =
for every candidate the walk evaluated (OBSERVE searches and every selection-cell walk), the node count of the program
as EXPANDED into base DSL (init + body + final) -- and, beside it, the same programs billed with each promoted node as
one node, so promotion overhead (expanded / promoted) is visible and a macro is never billed as one operation.
"""
import hashlib
import json
import time
from typing import Callable, Dict, List, Optional

from . import _paths  # noqa: F401
from . import promote as W

GRAMMAR = W.GRAMMAR


def _mods():
    """Engine modules, imported lazily so the caller controls import order (a18.TAG is read at a18's first import)."""
    import a17
    import a18
    import gtc
    from a18 import E, FR, G, T3D
    return a17, a18, gtc, E, FR, G, T3D


def entry_sha(entry) -> str:
    return hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()


# ================================================================ selection rules (pluggable)
_ORIG = {}


def _orig():
    a17, _a18, gtc, *_ = _mods()
    if not _ORIG:
        _ORIG["I0"], _ORIG["subset"], _ORIG["mean_positive"] = a17.select, gtc._select_subset, gtc._select_mean_positive
    return _ORIG


# rule -> (gtc genome, excluded candidate names): the Beta-02 RULES table (b02.RULES) restated
RULES = {"g0": ("g0", ()), "I0": ("g0", ()), "g0x": ("g0", ("MEMORISE",)),
         "g10": ("g10", ()), "g11": ("g10", ("MEMORISE",))}


def selector(genome: str, exclude=()) -> Callable:
    """The selection function donor_g would use for `genome`, with `exclude` candidate names removed first (exactly as
    b02._set_rule does it)."""
    _a17, _a18, gtc, *_ = _mods()
    o = _orig()
    g = gtc.GENOMES[genome]
    fn = (o["mean_positive"] if g.get("select") == "mean_positive" else
          o["subset"] if g.get("select") == "subset" else o["I0"])
    if not exclude:
        return fn
    ex = set(exclude)
    return lambda c, st, cells: fn({k: v for k, v in c.items() if k not in ex}, st, cells)


# ================================================================ cost meter (two ledgers)
class Meter:
    """Static execution units of every candidate a walk evaluated. A walk of n charges evaluated exactly the first n
    candidates of lib.candidates(seed) (fair.search_collect, a18.fast_cost and walk.iter_hits all charge one per
    candidate in that order, including candidates whose accumulator fails), so the units are computed arithmetically
    over the same keyed blocks without re-running the walk."""

    def __init__(self, form_map: Dict[str, str], reg):
        self.form_map, self.reg = form_map, reg
        self._exp, self._pro = {}, {}
        self.led = {}

    def _sz(self, s):
        n = self._exp.get(s)
        if n is None:
            n = self._exp[s] = W.nodes(W.parse(s))
        return n

    def _szp(self, s):
        f = self.form_map.get(s)
        if f is None:
            return self._sz(s)
        n = self._pro.get(f)
        if n is None:
            n = self._pro[f] = W.nodes(W.parse(f))
        return n

    def walk_units(self, lib, seed: int, n: int):
        _a17, _a18, _gtc, _E, FR, G, _T3D = _mods()
        left, ue, up = n, 0, 0

        def block(inits, bodies, finals):
            nonlocal left, ue, up
            if left <= 0:
                return
            fe = [self._sz(f) for f in finals]
            se, nf = sum(fe), len(finals)
            for i in inits:
                si = self._sz(i)
                for b in bodies:
                    if left <= 0:
                        return
                    sbe, sbp = self._sz(b), self._szp(b)
                    k = min(left, nf)
                    part = se if k == nf else sum(fe[:k])
                    ue += k * (si + sbe) + part
                    up += k * (si + sbp) + part
                    left -= k
        for e, bodies in zip(lib.entries, lib._bodies):
            block(FR.keyed(e["inits"], seed, "init"), FR.keyed(bodies, seed, "body"), FR.keyed(e["finals"], seed, "final"))
            if left <= 0:
                return ue, up
        fs = FR.keyed(G.FINAL_SPACE, seed, "g4final")
        for f in fs:
            if left <= 0:
                return ue, up
            ue += self._sz(f)
            up += self._sz(f)
            left -= 1
        block(FR.keyed(G.INIT_SPACE, seed, "g4init"), FR.keyed(G.BODY_SPACE, seed, "g4body"), fs)
        return ue, up

    def add(self, phase: str, lib, seed: int, n: int):
        ue, up = self.walk_units(lib, seed, n)
        d = self.led.setdefault(phase, {"walks": 0, "search_charges": 0, "expanded_exec_units": 0,
                                        "promoted_exec_units": 0})
        d["walks"] += 1
        d["search_charges"] += n
        d["expanded_exec_units"] += ue
        d["promoted_exec_units"] += up

    def summary(self) -> Dict:
        tot = {"walks": 0, "search_charges": 0, "expanded_exec_units": 0, "promoted_exec_units": 0}
        for d in self.led.values():
            for k in tot:
                tot[k] += d[k]
        tot["promotion_overhead_ratio"] = (round(tot["expanded_exec_units"] / tot["promoted_exec_units"], 6)
                                           if tot["promoted_exec_units"] else None)
        tot["expanded_units_per_charge"] = (round(tot["expanded_exec_units"] / tot["search_charges"], 4)
                                            if tot["search_charges"] else None)
        return {"by_phase": self.led, "total": tot}


class MeteredCell:
    """Proxy for a fair.Cell: identical cost() result; also bills the walk to the meter."""

    def __init__(self, cell, meter: Optional[Meter], phase="select"):
        self._c, self._m, self._phase = cell, meter, phase

    def __getattr__(self, k):
        return getattr(self._c, k)

    def cost(self, lib, *a, **kw):
        r = self._c.cost(lib, *a, **kw)
        if self._m is not None:
            self._m.add(self._phase, lib, self._c.seed, r[0])
        return r


# ================================================================ promotion of a start library
def promote_start(start: List[Dict], reg=None, kind="inherited_entry") -> Dict:
    """P1: registry of promoted primitives from a START library. Order: entry order; within an entry its carried
    records ("promoted", verified), then its "schema", then its "schemas". Deterministic and arm-blind: every schema
    in any start library is promoted by the same rule."""
    reg = {} if reg is None else reg
    for e in start:
        if e.get("promoted"):
            W.load_records(e["promoted"], reg)
        sch = ([e["schema"]] if e.get("schema") else []) + list(e.get("schemas", []))
        for s in sch:
            W.register(reg, W.Promoted.from_schema(s, reg, entry_sha(e), kind))
    return reg


def schema_entry(name: str, schema: str, reg, form_map=None) -> Dict:
    """a17.schema_entry under W5P. P-free schema + empty registry -> identical to a17.schema_entry."""
    a17, _a18, _gtc, _E, _FR, G, _T3D = _mods()
    e = {"name": name, "inits": list(G.H1_SPACE), "bodies": W.instantiate(schema, reg, form_map),
         "finals": list(G.FINAL_SPACE), "schema": schema}
    if W.has_promoted(schema):
        t = W.parse(schema)
        e["schema_expansion"] = W.expand(schema, reg)
        e["promoted"] = W.lineage_records(reg, sorted(set(W.prims_in(t))))
    return e


def candidates_from(derived, start, classes, reg, form_map=None) -> Dict:
    """a17.candidates_from under W5P (same names, same order)."""
    _a17, _a18, _gtc, _E, _FR, G, _T3D = _mods()
    cands = {"INHERITED": start,
             "MEMORISE": [{"name": "memorised", "inits": list(G.H1_SPACE),
                           "bodies": sorted({b for c in classes for b in c["member_bodies"]}),
                           "finals": list(G.FINAL_SPACE)}] + start}
    inst = {}
    for k, d in enumerate(derived):
        e = schema_entry("g2_new", d["schema"], reg, form_map)
        inst[d["schema"]] = e["bodies"]
        cands["SCHEMA_%d" % k] = [e] + start
    if len(derived) > 1:
        allb = list(dict.fromkeys(b for d in derived for b in inst[d["schema"]]))
        e = {"name": "g2_new", "inits": list(G.H1_SPACE), "bodies": allb, "finals": list(G.FINAL_SPACE),
             "schemas": [d["schema"] for d in derived]}
        ps = sorted({p for d in derived for p in W.prims_in(W.parse(d["schema"]))})
        if ps:
            e["promoted"] = W.lineage_records(reg, ps)
        cands["SCHEMA_ALL"] = [e] + start
    return cands


# ================================================================ O1: observation of promoted applications (opt-in)
def o1_entry(reg, start, form_map=None) -> Optional[Dict]:
    """O1 observation entry (Beta-03 O1 repair; OFF by default). Bodies = the W5P instantiations (promote.instantiate:
    the same filler set and depth/shape rule as every W5P candidate entry) of Q[{H} := P({H})] for every ORDERED pair
    (Q, P) of promoted primitives in the registry (Q == P included), Q then P in id order; bodies already in a START
    entry are dropped (the ordinary observation walk already covers them). inits H1, finals FINAL_SPACE (as
    a17.schema_entry). The contexts are the arm's OWN promoted schemas -- the only one-hole contexts the arm has; no
    other context, motif or truth enters. Empty registry -> None (no walk, no charge)."""
    _a17, _a18, _gtc, _E, _FR, G, _T3D = _mods()
    if not reg:
        return None
    have = {b for e in start for b in e.get("bodies", [])}
    bodies, schemas = [], []
    for q in sorted(reg):
        for p in sorted(reg):
            sch = reg[q].schema.replace(W.HOLE, "%s(%s)" % (p, W.HOLE))
            schemas.append(sch)
            bodies += [b for b in W.instantiate(sch, reg, form_map) if b not in have]
    bodies = list(dict.fromkeys(bodies))
    if not bodies:
        return None
    return {"name": "o1_observe", "inits": list(G.H1_SPACE), "bodies": bodies, "finals": list(G.FINAL_SPACE),
            "o1_schemas": schemas}


def o1_walk(entry, cell, escrow: int, max_hits: int):
    """Walk ONLY the O1 entry (no fallback) in keyed order with the standard charge rule (walk.iter_hits ==
    a18.fast_cost == fair.search_collect order and charges); own escrow per cell = the donor's escrow.
    Returns (hits, charges_spent, lib)."""
    _a17, _a18, _gtc, _E, FR, _G, _T3D = _mods()
    import walk
    lib = FR.KLib([entry])
    cap = min(escrow, len(entry["inits"]) * len(entry["bodies"]) * len(entry["finals"]))
    hits = []
    for ch, prog in walk.iter_hits(lib, cell, cap):
        hits.append((prog, entry["name"], ch))
        if len(hits) >= max_hits:
            return hits, ch, lib
    return hits, cap, lib


# ================================================================ the donor
def donor_w5p(genome: str, args, *, select=None, exclude=(), promote: bool = True, extra_promoted=None,
              meter: bool = True, o1: bool = False) -> Dict:
    """gtc.donor_g(genome, args) with W5P promotion.

    args     = (cat, kind, r, fams, specs, panel, compose[, start_override]) exactly as donor_g.
    select   = None (donor_g's rule for `genome`) | a callable (cands, start, cells) -> (chosen, table, vcost).
    exclude  = candidate names removed before selection (('MEMORISE',) gives g11 from genome g10, g0x from g0).
    promote  = False disables P1 (empty registry) -> donor_g's output exactly.
    extra_promoted = serialized promoted records to add to the registry (verified) -- e.g. a lineage carried
               out-of-band. Default None.
    o1       = O1 repair (default False): after each ordinary observation walk, a SECOND walk per observation cell over
               the O1 entry only (o1_entry), same escrow, same max hits; its hits join the observations. Billed on
               both ledgers (phase "observe_o1") and in meta_charges. OFF -> this function's output is unchanged.
    """
    a17, a18, gtc, E, FR, G, T3D = _mods()
    a18.worker_init()
    import ruler_v2 as R
    g = gtc.GENOMES[genome]
    cat, kind, r, fams, specs, panel, compose = args[:7]
    start_override = args[7] if len(args) > 7 else None
    t0 = time.perf_counter()
    prov = a17.Prov(specs)
    if start_override is not None:
        start, held = start_override, []
    else:
        start, held = a18.start_library(kind, panel)
    # ---- P1 promote (start library unchanged)
    reg = {}
    if extra_promoted:
        W.load_records(extra_promoted, reg)
    if promote:
        promote_start(start, reg)
    promoted_in = sorted(reg)
    form_map: Dict[str, str] = {}
    if reg:                    # inherited bodies that ARE promoted applications are billed as such on the promoted ledger
        pats = W._patterns(reg)
        for e in start:
            if e.get("schema") or e.get("schemas"):
                for b in e.get("bodies", []):
                    f = W.forms(b, reg, pats)
                    if len(f) > 1:
                        form_map.setdefault(b, f[-1])
    met = Meter(form_map, reg) if meter else None
    base, cov = FR.KLib(start), a17.coverage(start)
    o1e = o1_entry(reg, start, form_map) if o1 else None
    o1_rec = {"hits": [], "charges": 0, "walks": 0}
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
            if met:
                met.add("observe", base, cell.seed, esc.spent)
            for h in hits[:mh]:
                observed.append({"family": fam, "program": list(h[0]), "parsed": cell.parsed})
            if o1e is not None:
                oh, osp, olib = o1_walk(o1e, cell, a17.ESCROW, mh)
                meta += osp
                o1_rec["charges"] += osp
                o1_rec["walks"] += 1
                if met:
                    met.add("observe_o1", olib, cell.seed, osp)
                for h in oh[:mh]:
                    observed.append({"family": fam, "program": list(h[0]), "parsed": cell.parsed})
                    o1_rec["hits"].append({"family": fam, "program": list(h[0]), "charge": h[2]})
    if g.get("derive_from") == "observe+validate":
        for fam in val_f:
            for c in range(a17.R_OBS):
                cell = FR.Cell(prov, fam, r * a17.R_OBS + c, size[fam], label="%s-%s-obsv/r%d" % (a18.TAG, cat, r))
                esc = E.Escrow(a17.ESCROW)
                hits = FR.search_collect(base, cell.parsed, esc, a17.ESCROW, cell.seed, max_hits=mh)
                meta += esc.spent
                if met:
                    met.add("observe", base, cell.seed, esc.spent)
                for h in hits[:mh]:
                    observed.append({"family": fam, "program": list(h[0]), "parsed": cell.parsed})
                if o1e is not None:
                    oh, osp, olib = o1_walk(o1e, cell, a17.ESCROW, mh)
                    meta += osp
                    o1_rec["charges"] += osp
                    o1_rec["walks"] += 1
                    if met:
                        met.add("observe_o1", olib, cell.seed, osp)
                    for h in oh[:mh]:
                        observed.append({"family": fam, "program": list(h[0]), "parsed": cell.parsed})
                        o1_rec["hits"].append({"family": fam, "program": list(h[0]), "charge": h[2]})
    classes, certs = a17.certified_classes(observed, cov)
    # ---- P2 + P3 recognise and derive
    derived = W.derive_schemas([c["member_bodies"] for c in classes], reg)
    cells = [FR.Cell(prov, f, r * a17.R_VAL + j, size[f], label="%s-%s-val/r%d" % (a18.TAG, cat, r))
             for f in val_f for j in range(a17.R_VAL)]
    raw = [{"schema": w, "origin": "COMPOSITION", "of": s} for s in held for w in a18.compositions(s)] if compose else []
    comp = [c for c in raw if a18.hits_any_cell(c["schema"], cells)]
    # ---- P4 propose
    cands = candidates_from(derived, start, classes, reg, form_map)
    for k, c in enumerate(comp):
        cands["SCHEMA_%d" % (len(derived) + k)] = [a17.schema_entry("g2_new", c["schema"])] + start
    if genome != "g0":
        for name in list(cands):
            if name == "INHERITED":
                continue
            ent = cands[name][0]
            cands[name] = gtc._apply(genome, ent, start, observed)
    if g.get("plant"):
        sch = a18.G1 if g["plant"] == "G1" else gtc.OFF_SCHEMA
        cands["SCHEMA_%d" % (len(derived) + len(comp))] = [a17.schema_entry("g2_new", sch)] + start
        comp = comp + [{"schema": sch, "origin": "PLANTED_" + g["plant"]}]
    mcells = [MeteredCell(c, met) for c in cells] if met else cells
    if select is not None:
        chosen, table, vcost = select(cands, start, mcells)
    else:
        chosen, table, vcost = selector(genome, exclude)(cands, start, mcells)
    meta += vcost
    allc = derived + comp
    sel = None
    if chosen.startswith("SCHEMA_") and chosen != "SCHEMA_ALL":
        sel = allc[int(chosen.split("_")[1])]["schema"]
    # ruler (W5 instrument) is applied to the EXPANSION, with the W5P instantiations, so it sees base DSL only
    sel_exp = W.expand(sel, reg) if sel else None
    sp = R.span_of_schema(a18.G1)
    tsp = R.traj_span(R.reexpression_bodies(a18.G1))
    sel_inst = W.instantiate(sel, reg) if sel else None
    sel_v = R.verdict_full(sel_exp, a18.G1, sp, tsp, inst=sel_inst) if sel else None
    rel_held = R.relations(sel_exp, held[0]) if (sel and held) else None
    # ---- output promotion: the selected schema(s) as promoted primitives (records only; for the next generation)
    sel_schemas = ([sel] if sel else
                   list(cands[chosen][0].get("schemas", [])) if chosen == "SCHEMA_ALL" else [])
    out_reg = dict(reg)
    selected_promoted = []
    for s in sel_schemas:
        p = W.register(out_reg, W.Promoted.from_schema(s, out_reg, entry_sha(cands[chosen][0]), "selected_entry"))
        selected_promoted.append(p.to_json())
    derived_p = [d["schema"] for d in derived if W.has_promoted(d["schema"])]
    res = {"catalog": cat, "donor": kind, "replicate": r, "compose": compose, "genome": genome,
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
    res["w5p"] = {
        "grammar": GRAMMAR, "promotion_enabled": bool(promote),
        "promoted_in": W.lineage_records(reg, promoted_in) if promoted_in else [],
        "promoted_in_ids": promoted_in,
        "n_derived_with_promoted": len(derived_p), "derived_with_promoted": derived_p,
        "selected_schema_expansion": sel_exp,
        "selected_uses_promoted": bool(sel and W.has_promoted(sel)) or any(W.has_promoted(s) for s in sel_schemas),
        "selected_promoted": selected_promoted,
        "dag_depth_in": W.dag_depth(reg),
        "dag_depth_selected": max((p["depth"] for p in selected_promoted), default=0),
        "dag_depth": W.dag_depth(out_reg),
        "n_bodies_with_promoted_form": len(form_map),
        "cost": met.summary() if met else None,
    }
    if o1:
        res["w5p"]["o1"] = {"enabled": True, "entry_bodies": len(o1e["bodies"]) if o1e else 0,
                            "entry_candidates": (len(o1e["inits"]) * len(o1e["bodies"]) * len(o1e["finals"]))
                            if o1e else 0,
                            "entry_schemas": len(o1e["o1_schemas"]) if o1e else 0,
                            "walks": o1_rec["walks"], "charges": o1_rec["charges"], "n_hits": len(o1_rec["hits"]),
                            "hits": o1_rec["hits"]}
    return res
