import json, pathlib
A = {"b59e6c3a": .707, "311c465f": .715, "95649e2c": .648}
for c, astar in A.items():
    f = pathlib.Path(f"out/search_{c}.json")
    if not f.exists(): continue
    d = json.loads(f.read_text())
    print(c, "champion_analysis", [round(x, 3) for x in d["champion_analysis"]], "A*", astar)
    for arm in ("A_orig", "B_fixed_L", "C_fixed_RL"):
        v = [d[k]["analysis"][0] for k in sorted(d) if k.startswith(arm + "/")]
        if v: print("  ", arm, [round(x, 3) for x in v], "reach", sum(x >= astar for x in v), "/", len(v))
