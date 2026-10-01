import json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parents[1] / "campaigns" / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
import world
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
class Stop(Exception): pass
E = int(sys.argv[2])
class R(world.Runner):
    def step(self):
        super().step()
        if self.epoch >= E: raise Stop
r = R(dict(arm["cell"], atlas_axis="NONE"), int(sys.argv[1]), tier=arm["tier"], implant="ACTUAL_GENOME",
      implant_bytes=bytes.fromhex(arm["kwargs"]["implant_hex"]))
try: r.run()
except Stop: pass
births = [e for e in r.lineage if e["kind"] == "birth"]
cp = {e["child"]: e["parent"] for e in births if e["causal"]}
allp = {e["child"]: e["parent"] for e in births}
d, per = r._depths(cp)
node = max(per, key=per.get)
chain = [node]
while chain[-1] in cp: chain.append(cp[chain[-1]])
root = chain[-1]
# walk root through all edges to its ultimate ancestor
up = [root]
while up[-1] in allp: up.append(allp[up[-1]])
f0 = 0
print("depth", d, "chain root", root, "root's all-edge ancestors", up[:10], "len", len(up))
born = {e["child"]: e for e in births}
print("root birth", born.get(root))
print("first births", births[:8])
print("n births", len(births), "n causal", len(cp))
print("chain", chain[::-1][:40])
anc_of = {}
for e in births: anc_of[e["child"]] = e["parent"]
print("chain epochs", [born[c]["epoch"] for c in chain[::-1] if c in born][:40])
if len(sys.argv) > 3:
    m = json.load(open(sys.argv[3]))["members"]
    print("in family:", [str(c) in m for c in chain[::-1]])
root = chain[-1]
up = [root]
while up[-1] in allp: up.append(allp[up[-1]])
print("root", root, "born", born.get(root, {}).get("epoch"), "all-edge ancestry", up, [born.get(u, {}).get("epoch") for u in up])
print("root ancestor oid < 256 (background original)?", up[-1] < 256)
