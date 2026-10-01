"""W2-49 a1: re-score EW-1/EW-1b/EW-2 (+EW-4) on W2-29 FULL under W2-45's frozen rule, with the replayed trajectories
replacing every EW-1/EW-1b unknown. Scoring functions are taken VERBATIM from W2-45 a1_score.py via ast (not imported:
importing it would re-run and overwrite W2-45's json). python -B a1_rescore.py -> a1_rescore.json"""
import ast, json, math, pathlib
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
src = (W / "W2-45_early_warning" / "a1_score.py").read_text()
tree = ast.parse(src)
keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in
        ("wilson", "from_traj", "from_genomes", "from_summary", "score", "outcomes")]
ns = {"math": math, "T": 163}
exec(compile(ast.Module(body=keep, type_ignores=[]), "a1_score_funcs", "exec"), ns)
from_traj, from_genomes, from_summary, score, outcomes, wilson = (ns[k] for k in
    ("from_traj", "from_genomes", "from_summary", "score", "outcomes", "wilson"))
T = 163
OBS = ["EW1", "EW1b", "EW2", "EW4"]


def load(p):
    return [json.loads(l) for l in open(p)]


full = load(W / "W2-29_residue" / "runs_FULL.jsonl")
gen = {d["s"]: d for d in load(W / "W2-29_residue" / "genomes_FULL.jsonl")}
rep = {d["s"]: d for d in load(HERE / "runs_replay.jsonl")}
aud = {d["s"]: d for d in load(HERE / "runs_tier2_audit.jsonl")}
out = {"n_replayed": len(rep), "n_tier2_audit": len(aud)}

# ---- bit-exactness + trajectory self-consistency ----
bx = dict(replay_mismatch=[s for s, d in rep.items() if d["bitexact_mismatch"]],
          audit_mismatch=[s for s, d in aud.items() if d["bitexact_mismatch"]])
tc = []
for s, d in list(rep.items()) + list(aud.items()):
    tr = d["traj"]
    ok = len(tr) == d["epochs"] and tr[-1][2] == d["B"] and tr[-1][3] == d["Bxk"] and tr[-1][1] == d["A_end"] \
        and tr[-1][0] == d["N_end"] and max(t[1] for t in tr) == d["maxA"] and all(tr[i][2] <= tr[i + 1][2] for i in range(len(tr) - 1))
    if not ok:
        tc.append(s)
bx["traj_inconsistent"] = tc
# genome rows of replayed E27 seeds identical to genomes_FULL.jsonl
bx["genomes_identical"] = {s: (sorted(map(tuple, rep[s]["genomes"])) == sorted(map(tuple, gen[s]["genomes"])))
                           for s in rep if s in gen}
# traj lies inside W2-45's genome bounds
bx["traj_within_W245_bounds"] = {}
for s in rep:
    if s in gen:
        a = from_genomes(gen[s]["genomes"], rep[s]["B"])
        tr = rep[s]["traj"]
        Be = {e: tr[min(e, len(tr)) - 1][2] for e in (5, 10, 15, 20)}
        bx["traj_within_W245_bounds"][s] = {k: [Be[int(k[1:])], v, v[0] <= Be[int(k[1:])] <= v[1]] for k, v in a["_bounds"].items()}
out["bitexact"] = bx

# ---- tier-2 audit: did any frozen-inferred negative actually fire? ----
out["tier2_audit"] = []
for s, d in sorted(aud.items()):
    a = from_traj(d["traj"])
    last_birth_ep = max([i + 1 for i in range(len(d["traj"])) if d["traj"][i][2] > (d["traj"][i - 1][2] if i else 0)], default=0)
    out["tier2_audit"].append(dict(s=s, B=d["B"], epochs=d["epochs"], EW1=a["EW1"], EW1b=a["EW1b"],
                                   last_causal_birth_epoch=last_birth_ep, B10=d["traj"][9][2]))

# ---- rescoring ----
units, per, src_tag = [], [], {}
for r in full:
    o = outcomes(r)
    s = r["s"]
    if s in rep:
        a = from_traj(rep[s]["traj"]); tag = "traj"
        if a["_short"]:
            raise SystemExit("short alive traj %d" % s)
        if s in gen:  # EW2 etc: keep W2-45's genome-derived value only where traj not used; traj supersedes
            pass
    elif s in gen:
        a = from_genomes(gen[s]["genomes"], r["B"]); tag = "genome"
    else:
        a = from_summary(r, tier2=True); tag = "summary"
    src_tag[s] = tag
    units.append((a, o))
    per.append(dict(s=s, B=r["B"], Bxk=r["Bxk"], stop=r["stop"], epochs=r["epochs"], src=tag,
                    **{k: a[k] for k in OBS}))
out["source_counts"] = {t: sum(v == t for v in src_tag.values()) for t in ("traj", "genome", "summary")}
for tgt in ("xk", "B"):
    for ob in OBS:
        out["%s|%s" % (ob, tgt)] = score(units, ob, tgt)


# ---- false-alarm composition ----
def stratum(p):
    if p["Bxk"] >= T:
        return "runaway_xk"
    if p["B"] >= 27:
        return "intermediate(B27-162 or B>=163,Bxk<163)"
    return "small(B<27)"


comp = {}
for ob in ("EW1", "EW1b", "EW2"):
    c = {}
    for p in per:
        st = stratum(p)
        d = c.setdefault(st, {"n": 0, "fire": 0, "unknown": 0, "fire_seeds": []})
        d["n"] += 1
        if p[ob] is None:
            d["unknown"] += 1
        elif p[ob]:
            d["fire"] += 1
            if st != "runaway_xk":
                d["fire_seeds"].append(p["s"])
    comp[ob] = c
out["fa_composition_xk"] = comp
out["replayed_rows"] = [dict(p, B5=rep[p["s"]]["traj"][4][2] if len(rep[p["s"]]["traj"]) >= 5 else None,
                             B10=rep[p["s"]]["traj"][min(10, len(rep[p["s"]]["traj"])) - 1][2],
                             B15=rep[p["s"]]["traj"][min(15, len(rep[p["s"]]["traj"])) - 1][2],
                             B20=rep[p["s"]]["traj"][min(20, len(rep[p["s"]]["traj"])) - 1][2],
                             maxstep11_20=max(rep[p["s"]]["traj"][min(e, len(rep[p["s"]]["traj"])) - 1][2]
                                              - rep[p["s"]]["traj"][min(e - 1, len(rep[p["s"]]["traj"])) - 1][2]
                                              for e in range(11, 21)))
                        for p in per if p["s"] in rep]
json.dump(out, open(HERE / "a1_rescore.json", "w"), indent=1, default=str)

print("bitexact", {k: v for k, v in bx.items() if k != "traj_within_W245_bounds"})
print("bounds", bx["traj_within_W245_bounds"])
print("sources", out["source_counts"])
for k, v in out.items():
    if isinstance(v, dict) and "imp0" in v:
        c0, c1 = v["imp0"], v["imp1"]
        print("%-10s tp %d fn %d fp %d tn %d | hit %s fa %s ppv %s | unk %d -> imp1 fp %d | %s" % (
            k, c0["tp"], c0["fn"], c0["fp"], c0["tn"], c0["hit"], c0["fa"], c0["ppv"], v["n_unknown"], c1["fp"], v["verdict"]))
for ob, c in comp.items():
    print(ob, {k: (v["n"], v["fire"], v["unknown"], v["fire_seeds"]) for k, v in c.items()})
print("tier2 audit fires:", [(t["s"], t["EW1"], t["EW1b"], t["last_causal_birth_epoch"]) for t in out["tier2_audit"] if t["EW1"] or t["EW1b"]],
      "max last birth epoch", max(t["last_causal_birth_epoch"] for t in out["tier2_audit"]))
