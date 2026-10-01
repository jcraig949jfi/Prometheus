"""W2-I: MAJ sensor placement uses OUT-distance from the actuator (envs.build: _pick_at(g, M[a], d)),
but MAJ signal flows sensor -> actuator. On directed graphs (C1 random; smallworld after one-sided
rewiring) the two differ. For every C1 MAJ row on random/smallworld, compare the nominal d with the
signal-direction hops (BFS sensor -> actuator) over 32 placement worlds. Also XOR/RELAY for contrast.
No dynamics are run (placement only)."""
import collections, json
from w2i_common import *
out = collections.defaultdict(list)
seen = {}
for r in rows():
    if r["wave"] == "A0" or r["env"]["family"] not in ("MAJ", "RELAY") or r["physics"]["topology"] not in ("random", "smallworld"):
        continue
    ph = Physics.from_dict(r["physics"]).validate(); env = envs.EnvSpec(**r["env"])
    key = (ph.digest(), json.dumps(env.to_dict(), sort_keys=True))
    if key not in seen:
        S = seeds_for(0x22, 32)
        seen[key] = signal_hops(ph, env, S)
    h = seen[key]
    tot = sum(h.values()); eq = h.get(str(env.d), 0)
    ex = sum(c for k, c in h.items() if int(k) > env.d)
    out[(env.family, ph.topology)].append({"cell": r["cell_id"][:8], "kind": r["kind"], "wave": r["wave"], "d": env.d,
        "hops": h, "frac_more_than_d": round(ex / tot, 3),
        "held": r["result"].get("held", {}).get("acc"), "lo99": r["result"].get("held", {}).get("lo99")})
summ = {}
for k, v in out.items():
    ev = [x for x in v if x["kind"] == "evolve"]
    summ["%s/%s" % k] = {"rows": len(v), "evolve_rows": len(ev),
        "mean_frac_sensor_hops_gt_d": round(float(np.mean([x["frac_more_than_d"] for x in v])), 3),
        "evolve_signal_rows": sum(1 for x in ev if (x["lo99"] or 0) > .55)}
print(json.dumps(summ, indent=1))
(OUT / "maj_direction_census.json").write_text(json.dumps({"summary": summ, "rows": {"%s/%s" % k: v for k, v in out.items()}}, indent=1))
