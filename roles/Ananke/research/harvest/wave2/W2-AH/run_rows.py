"""W2-AH: score frugal plants on every C1 economy-transect row (waves B, B2) on the row's OWN physics and OWN plant
seeds (campaign.plant_viability: world_seeds(H_int(search_seed,0x9147),32), prog_len max(L,12)).
RELAY rows: F0, F1 (+ relay_flood KA on 'high' rows). MAJ b1 rows: W2-Z MAJ members (copied verbatim from
W2-Z/run_maj.py MEMBERS, read-only) + relay_flood KA on 'high' rows. Eager CPU, 2 threads."""
import sys
from w2ah_common import *
sys.path.insert(0, str(HERE.parent / "W2-Z"))
src = (HERE.parent / "W2-Z" / "run_maj.py").read_text()
ns = {}
exec(src[src.index("MEMBERS = {"):src.index("def genome")], ns)          # the MEMBERS dict only
MAJM = ns["MEMBERS"]
ck = hc.Clock()
which = sys.argv[1]
out = []
for r in hc.rows():
    if r["wave"] not in ("B", "B2") or r["extra"].get("transect") != "economy": continue
    fam, base = r["env"]["family"], r["extra"]["base"]
    if which == "RELAY" and fam != "RELAY": continue
    if which == "MAJ" and not (fam == "MAJ" and base == 1): continue
    ph, env = cell(r); p12 = ph.replace(prog_len=max(ph.prog_len, 12)).validate()
    seeds = plant_seeds(r)
    lvl = r["levels"]["economy"]
    o = {"cell": r["cell_id"], "wave": r["wave"], "family": fam, "base": base, "li": r["extra"]["level_index"],
         "rep": r["extra"].get("rep", 0), "economy": lvl, "recorded": r["result"]["plant"]["acc"]}
    gens = {}
    if fam == "RELAY":
        gens = {n: genome(p12, n) for n in ("F0", "F1")}
    else:
        for n, b in MAJM.items():
            gens[n] = hc.bc(p12, A(p12, b))
    if lvl == "high":
        gens["relay_flood"] = genome(p12, "relay_flood")
    for n, g in gens.items():
        a = hc.evaluate(p12, g, env, seeds)
        o[n] = round(a["acc"], 4); o[n + "_lo99"] = round(a["lo99"], 4); o[n + "_emit_per_world"] = a["stats"]["emitters"] / 32
    if "relay_flood" in o:
        o["ka_match"] = abs(o["relay_flood"] - o["recorded"]) < 1e-3
    out.append(o); print(o, ck.done(), flush=True)
save(f"rows_{which}.json", {"rows": out, "compute": ck.done()})
print(ck.done())
