"""Effective-physics canonicaliser derived from engine.py/topology.py/envs.py semantics.
Two (physics, env) pairs with equal canon() must give bit-identical traces and stats
(mailbox length LM may differ; it is not dynamics)."""
def canon(ph: dict, env: dict) -> tuple:
    p = dict(ph); e = dict(env)
    topo = p["topology"]
    if topo != "random": p["k_random"] = None
    if topo not in ("ring", "torus"): p["radius"] = None
    if topo != "smallworld": p["rewire"] = None
    if topo in ("random",) : pass
    if topo == "global": p["dest_mode"] = "sample"
    if p["dest_mode"] == "all" and topo != "global": p["fanout"] = None
    w_read = topo != "global" and p["dest_mode"] == "sample"
    if not w_read or not p["plastic_route"]:
        p["plastic_route"] = 0
    if not p["plastic_route"]: p["adapt_shift"] = None   # w never read or never written
    # NOTE plastic_route=1 under dest_mode all still writes w (not read) -> stats differ only
    if p["cap"] == 0 or p["collision"] == "none": p["cap"] = 0; p["collision"] = "none"
    if p["rules"] == 1: p["setrule"] = None
    maxd = p["radius"] if topo in ("ring", "torus") else 1
    if p["loss"] == 0 or maxd == 1: p["loss_per_hop"] = None
    # latency: on dist==1 tables delay = lat_base+lat_hop+U(jitter); clamp at 1
    if maxd == 1:
        p["lat_base"] = max(1, p["lat_base"] + p["lat_hop"]); p["lat_hop"] = 0
    if p["update_mode"] == "sync": p["update_p"] = None
    else: p["update_period"] = None
    if p["update_mode"] == "sync" and p["update_period"] == 1: pass
    if p["mut_site"] == 0: pass
    p["topo_seed"] = p["topo_seed"] if topo in ("random", "smallworld") else None
    fam = e["family"]
    if fam != "HOLD": e["gap"] = None
    if fam == "HOLD": e["delta"] = None; e["d"] = None
    if fam != "FLIP": e["block"] = None
    if topo == "global": e["d"] = None
    return tuple(sorted(p.items())), tuple(sorted(e.items()))
