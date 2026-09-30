"""Build the blinded pilot dataset and its separate answer key.

    python -m hecate.alien.dataset build        # -> hecate/alien/data/{public,answer_key}.json

Counts (directive): 20 KNOWN, 40 ALIEN_LAWFUL, 40 MATCHED_NOISE, 8 alien + 4
known + 8 null per family (tab, graph, rewrite, vm, map).
ALIEN: 32 standard + 8 adversarial (noisy-looking lawful: linear change of
coordinates on tab/map, long-cycle vm).
NULL: 22 incompressible tables of a matched alien, alternating CONJ
(relabelled: s -> sigma(f(sigma^-1(s))), identical orbit structure; used
unless the planted property is itself orbit-structural, in which case
SCRAMBLE, input-scrambled: s -> f(pi(s))) and DSCRAMBLE (increment-scrambled:
s -> s + [f(pi(s)) - pi(s)], one component tweaked on ~30% of states; keeps
the change-rate and step-size distribution, destroys the rule),
10 DESTROY (same generator, planting constraint removed: compact rule),
8 SEDUCTIVE (small random per-state increments: incompressible but
locally smooth), matched to the 8 adversarial aliens.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

from hecate.alien import generate as G
from hecate.alien import verify as V
from hecate.alien.systems import (all_states, clamp_run, dims_of, header, index,
                                  remove_edge, show, step, trajectory)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("HECATE_ALIEN_DATA") or os.path.join(HERE, "data")
SEED = int(os.environ.get("HECATE_ALIEN_SEED") or 20260930)

STANDARD_PLAN = {                      # family -> list of (generator, arg)
    "tab": [("tab_local", "lin"), ("tab_local", "lin"), ("tab_local", "cyc"),
            ("tab_rev", None), ("tab_local", None)],
    "graph": [("graph_flow", None)] * 4 + [("graph_attr", None)] * 4,
    "rewrite": [("rewrite", "term")] * 4 + [("rewrite", "cycle")] * 4,
    "vm": [("vm", "lin")] * 6,
    "map": [("map_sym", None)] * 3 + [("map_shear", None)] * 2,
}
ADV_PLAN = {"tab": 3, "map": 3, "vm": 2}
DESTROY_PER_FAMILY = 2
N_OBS_TRAJ, OBS_STEPS = 8, 10


def _gen(rng, name, arg):
    if name == "tab_local":
        return G.g_tab_local(rng, arg, zero_p=0.4 if arg else 0.7)
    if name == "tab_rev":
        return G.g_tab_rev(rng)
    if name == "graph_flow":
        return G.g_graph_flow(rng)
    if name == "graph_attr":
        return G.g_graph_attr(rng)
    if name == "rewrite":
        return G.g_rewrite(rng, arg)
    if name == "vm":
        return G.g_vm(rng, arg)
    if name == "map_sym":
        return G.g_map_sym(rng)
    if name == "map_shear":
        return G.g_map_shear(rng)
    raise ValueError(name)


def _accept(p, props, known_fam, log):
    tbl = V.table(p)
    if not all(G.check_prop(p, pr, tbl) for pr in props):
        return None
    ok, why = G.analogue_ok(p, known_fam, tbl)
    if not ok:
        log.append(why)
        return None
    return tbl


def make_alien(rng, fam, name, arg, known_fam, log, adversarial=False):
    for attempt in range(400):
        if adversarial and fam == "tab":
            base, props, note = G.g_tab_local(rng, "lin")
            p, props = G.linmix(rng, base, props, 5, 5)
            note = "latent " + note + ", observed through a random invertible linear map mod 5"
        elif adversarial and fam == "map":
            base, props, note = G.g_map_sym(rng)
            p, props = G.linmix(rng, base, props, G.P, 2)
            note = "latent " + note + ", observed through a random invertible linear map mod 31"
        elif adversarial and fam == "vm":
            p, props, note = G.g_vm(rng, "long")
        else:
            p, props, note = _gen(rng, name, arg)
        tbl = _accept(p, props, known_fam, log)
        if tbl is not None:
            return p, props, note, attempt + 1
    raise RuntimeError(f"could not generate {fam} {name} {arg} adv={adversarial}")


def make_null(rng, alien, props, kind):
    for attempt in range(400):
        if kind == "CONJ":
            q = {"family": alien["family"], "wrap": "conj", "base": alien,
                 "perm_seed": int(rng.randint(1, 2 ** 31 - 1))}
        elif kind == "DSCRAMBLE":
            q = {"family": alien["family"], "wrap": "delta", "base": alien,
                 "perm_seed": int(rng.randint(1, 2 ** 31 - 1)),
                 "tweak_seed": int(rng.randint(1, 2 ** 31 - 1))}
        elif kind == "SCRAMBLE":
            # a permutation-scramble of a bijection is a bijection, so a
            # bijective alien is scrambled with replacement (random function)
            q = {"family": alien["family"], "wrap": "scramble", "base": alien,
                 "perm_seed": int(rng.randint(1, 2 ** 31 - 1)),
                 "with_replacement": any(pr["type"] == "bijective" for pr in props)}
        elif kind == "SEDUCTIVE":
            q = {"family": alien["family"], "wrap": "smooth", "seed": int(rng.randint(1, 2 ** 31 - 1))}
            if alien["family"] == "graph" or alien.get("base", {}).get("family") == "graph":
                q["edges"] = alien["edges"]
        else:
            base = alien.get("base", alien)
            q = G.destroy(rng, base)
        tbl = V.table(q)
        primary = [pr for pr in props if pr.get("primary", True)]
        if not any(G.check_prop(q, pr, tbl) for pr in primary):
            return q, attempt + 1
    raise RuntimeError(f"null {kind} kept the planted property")


def _obs(rng, p, dims):
    starts = set()
    trajs = []
    while len(trajs) < N_OBS_TRAJ:
        s = tuple(int(rng.randint(0, d)) for d in dims)
        if s in starts:
            continue
        starts.add(s)
        trajs.append(trajectory(p, s, OBS_STEPS))
    return trajs


def _unseen(rng, dims, seen, k):
    out = []
    while len(out) < k:
        s = tuple(int(rng.randint(0, d)) for d in dims)
        if s not in seen and s not in out:
            out.append(s)
    return out


def packet(rng, p):
    """Public observations + hidden answers for T2, T3, T5/T6 eval."""
    dims = dims_of(p)
    trajs = _obs(rng, p, dims)
    seen = {s for t in trajs for s in t}
    q2 = _unseen(rng, dims, seen, 12)
    ivs = []
    first_var = 1 if p["family"] == "vm" else 0
    for s in _unseen(rng, dims, seen | set(q2), 3):
        var = int(rng.randint(first_var, len(dims)))
        val = int(rng.randint(0, dims[var]))
        ivs.append({"type": "clamp", "start": s, "var": var, "val": val,
                    "answer": clamp_run(p, s, var, val, 3)})
    base = p
    while base.get("wrap") in ("scramble", "linmix", "delta", "conj"):
        base = base["base"]
    if p["family"] == "graph":
        e = base["edges"][int(rng.randint(0, len(base["edges"])))] if "edges" in base else None
        if e is None:
            e = p.get("edges", [[0, 1]])[0]
        s = _unseen(rng, dims, seen | set(q2), 1)[0]
        ivs.append({"type": "remove_link", "start": s, "edge": e,
                    "answer": trajectory(_edge_removed(p, e), s, 3)[1:]})
    else:
        s = _unseen(rng, dims, seen | set(q2), 1)[0]
        var = int(rng.randint(first_var, len(dims)))
        val = int(rng.randint(0, dims[var]))
        ivs.append({"type": "clamp", "start": s, "var": var, "val": val,
                    "answer": clamp_run(p, s, var, val, 3)})
    evs = _unseen(rng, dims, seen, 200)
    return {
        "trajs": trajs, "q2": q2, "a2": [step(p, s) for s in q2], "ivs": ivs,
        "eval_states": evs, "eval_next": [step(p, s) for s in evs],
    }


def _edge_removed(p, e):
    if p.get("wrap") in ("scramble", "delta", "conj"):
        return p                           # a scrambled table has no links to remove
    if p.get("wrap") == "smooth":
        return p
    return remove_edge(p, e)


def public_view(sid, p, pk):
    return {
        "id": sid,
        "header": header(p),
        "observations": [[show(p, s) for s in t] for t in pk["trajs"]],
        "t2_queries": [show(p, s) for s in pk["q2"]],
        "t3_interventions": [
            {"type": iv["type"], "start": show(p, iv["start"]),
             **({"position": iv["var"], "value": iv["val"]} if iv["type"] == "clamp"
                else {"link": f"{iv['edge'][0]}-{iv['edge'][1]}"})}
            for iv in pk["ivs"]],
    }


def build(seed=SEED):
    rng = np.random.RandomState(seed)
    known = G.known_pool(rng)
    known_by_fam = {}
    for k in known:
        known_by_fam.setdefault(k["family"], []).append(k)
    entries, log = [], []
    n_scr = 0
    for kn in known:
        entries.append({"class": "KNOWN_LAWFUL", "null_type": None, "family": kn["family"],
                        "params": kn, "planted": [], "known_analogue": kn["kind"],
                        "generator": "known:" + kn["kind"], "matched_to": None})
    for fam, plan in STANDARD_PLAN.items():
        aliens = []
        for name, arg in plan:
            p, props, note, tries = make_alien(rng, fam, name, arg, known_by_fam[fam], log)
            aliens.append((p, props, note, tries, False))
        for _ in range(ADV_PLAN.get(fam, 0)):
            p, props, note, tries = make_alien(rng, fam, None, None, known_by_fam[fam], log, True)
            aliens.append((p, props, note, tries, True))
        n_destroy = 0
        for i, (p, props, note, tries, adv) in enumerate(aliens):
            aid = len(entries)
            entries.append({"class": "ALIEN_LAWFUL", "null_type": None, "family": fam,
                            "params": p, "planted": props, "known_analogue": None,
                            "analogue_note": note, "adversarial": adv,
                            "generator": f"{fam}:{p.get('kind', p.get('wrap'))}",
                            "resamples": tries, "matched_to": None})
            if adv:
                kind = "SEDUCTIVE"
            elif n_destroy < DESTROY_PER_FAMILY:
                kind, n_destroy = "DESTROY", n_destroy + 1
            else:
                orbit_prop = any(pr["type"] in ("bijective", "all_orbits_fixed", "long_cycle")
                                 for pr in props if pr.get("primary", True))
                kind = ("SCRAMBLE" if orbit_prop else "CONJ") if n_scr % 2 == 0 else "DSCRAMBLE"
                n_scr += 1
            q, ntries = make_null(rng, p, props, kind)
            entries.append({"class": "MATCHED_NOISE", "null_type": kind, "family": fam,
                            "params": q, "planted": [], "known_analogue": None,
                            "planted_of_match_fails": True, "adversarial": kind == "SEDUCTIVE",
                            "generator": f"null:{kind}", "resamples": ntries,
                            "matched_to": aid})
            entries[aid]["matched_to"] = len(entries) - 1
    ids = rng.choice(np.arange(10000, 99999), len(entries), replace=False)
    order = rng.permutation(len(entries))
    public, key = [], {}
    idmap = {i: f"SYS-{int(ids[i]):05d}" for i in range(len(entries))}
    for j in order:
        e = entries[j]
        sid = idmap[j]
        p = e["params"]
        pk = packet(rng, p)
        pub = public_view(sid, p, pk)
        obs_text = "\n".join(" ; ".join(t) for t in pub["observations"])
        tbl = V.table(p)
        k = dict(e)
        k.update(id=sid, matched_to=idmap[e["matched_to"]] if e["matched_to"] is not None else None,
                 lawful=e["class"] != "MATCHED_NOISE" or e["null_type"] == "DESTROY",
                 verification_tests=[{"prop": pr, "result": G.check_prop(p, pr, tbl)} for pr in e["planted"]],
                 nuisance=V.nuisance(p, obs_text, tbl),
                 answers={"t2": [list(s) for s in pk["a2"]],
                          "t3": [[list(s) for s in iv["answer"]] for iv in pk["ivs"]],
                          "t3_spec": [{kk: (list(vv) if isinstance(vv, tuple) else vv)
                                       for kk, vv in iv.items() if kk != "answer"} for iv in pk["ivs"]],
                          "q2_states": [list(s) for s in pk["q2"]],
                          "eval_states": [list(s) for s in pk["eval_states"]],
                          "eval_next": [list(s) for s in pk["eval_next"]]},
                 seed=seed)
        public.append(pub)
        key[sid] = k
    return public, key, log


def _json(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, default=int)


if __name__ == "__main__" and sys.argv[1:] == ["build"]:
    public, key, log = build()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "public.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(public, indent=1, sort_keys=True, ensure_ascii=True, default=int) + "\n")
    with open(os.path.join(OUT, "answer_key.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(key, indent=1, sort_keys=True, ensure_ascii=True, default=int) + "\n")
    from collections import Counter
    print(Counter((v["class"], v["null_type"]) for v in key.values()))
    print(Counter(v["family"] for v in key.values()))
    print("analogue rejections:", Counter(log).most_common(8))
