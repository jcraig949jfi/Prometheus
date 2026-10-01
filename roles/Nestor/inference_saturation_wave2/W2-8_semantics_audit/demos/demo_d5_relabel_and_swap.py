"""D8 / D9 demonstration: what a pair-tape "birth" leaves behind, through the real `_pair_interact`.

The P-11 assay and the predecessor criterion are STUBBED (the point is the bookkeeping that follows acceptance, not the
assay). One call of `_pair_interact` on two placed organisms with both halves accepted (the mutual case), and one with one
half accepted.
"""
from __future__ import annotations

import _paths
import p11
import run_dd
import run_ds
import world

a = run_ds.cells()[run_dd.CELLS["7ae3"]]
cell = dict(a["cell"], atlas_axis="NONE", pressure="PREDATION")


def fresh():
    r = world.Runner(cell, 3, tier="S", max_epochs=1)
    r.t["epochs"] = 0
    r.run()
    x, y = [o for o in r.orgs if o.alive][:2]
    x.age, y.age, x.comp, y.comp, x.energy = 50, 60, 0.95, 0.10, 123.0
    return r, x, y


stub = {"pass": True, "draws_passed": 3, "draws": [], "C2_majority": True, "C4_majority": True, "C5_majority": True}
saved = (p11.predecessor_accepts, p11.assay, p11.ordinary_diagnostics)
p11.assay = lambda *k, **kw: stub
p11.ordinary_diagnostics = lambda *k, **kw: {}

# (1) mutual acceptance: both halves accepted in one interaction
p11.predecessor_accepts = lambda *k: True
r, x, y = fresh()
ox, oy = x.oid, y.oid
r._pair_interact(0, x, y)
births = [e for e in r.lineage if e["kind"] == "birth"]
mutual = {"x_old": ox, "y_old": oy, "x_new": x.oid, "y_new": y.oid,
          "edges(child<-parent)": [(e["child"], e["parent"]) for e in births],
          "second_edge_parent_is_first_edge_child": births[1]["parent"] == births[0]["child"],
          "causal_depth_reported": r._depths({e["child"]: e["parent"] for e in births})[0]}

# (2) single acceptance: only the half of x is replaced (calls go x then y)
calls = {"n": 0}


def first_only(*k):
    calls["n"] += 1
    return calls["n"] == 1


p11.predecessor_accepts = first_only
r, x, y = fresh()
ox = x.oid
r._pair_interact(0, x, y)
single = {"victim_old_oid": ox, "victim_new_oid": x.oid,
          "slot_owner_still_names_old_oid": r.slot_owner.get(x.slot) == ox,
          "age_after_birth": x.age, "born_after_birth": x.born, "comp_after_birth": x.comp,
          "energy_after_birth": x.energy, "regs_kept": x.regs is not None,
          "birth_niche_has_new_oid": x.oid in r.birth_niche,
          "predation_lookup_finds_victim": next((o for o in r.orgs if o.oid == r.slot_owner.get(x.slot) and o.alive),
                                                None) is not None}
p11.predecessor_accepts, p11.assay, p11.ordinary_diagnostics = saved
_paths.dump("d5_relabel_and_swap.json", {"mutual_acceptance": mutual, "single_acceptance": single})
