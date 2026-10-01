"""Sanity of the static classifier on known plants, then classify all 678 C1 evolve champions."""
from r_common import *
from static_cls import classify_genome, classify_rule
import collections
import sys
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))
ph = Physics(topology="ring", n_sites=36, radius=1, dest_mode="all", lat_base=1, noise=64,
             payload_width=2, channels=1, prog_len=16, state_dim=4)
lin = plants.assemble(ph, [("CONST", "EMIT", 0, 0, 1), ("SHR", "PAY0", "SENSE", 5, 0), ("MOV", "S0", "IN0_0", 0, 0)])
checks = {
    "relay_flood(expect THRESH)": classify_rule(ph, plants.relay_flood(ph)),
    "hold_latch(expect THRESH)": classify_rule(ph, plants.hold_latch(ph)),
    "common_mode linear toy(expect LINEAR comm)": classify_rule(ph, lin),
    "S0=SENSE+IN0_0 via T (expect LINEAR)": classify_rule(ph, plants.assemble(ph, [("ADD", "T0", "SENSE", "IN0_0", 0), ("MOV", "S0", "T0", 0, 0)])),
    "S0=GT(T0) then overwritten by MOV IN (expect LINEAR)": classify_rule(ph, plants.assemble(ph, [("GT", "S0", "SENSE", "ZERO", 0), ("MOV", "S0", "IN0_0", 0, 0)])),
    "accumulate S0+=IN (expect LINEAR, loop)": classify_rule(ph, plants.assemble(ph, [("ADD", "S0", "S0", "IN0_0", 0)])),
    "S1=GT(SENSE); S0=S1 next tick via MOV before (expect THRESH, loop)": classify_rule(ph, plants.assemble(ph, [("MOV", "S0", "S1", 0, 0), ("GT", "S1", "SENSE", "ZERO", 0)])),
    "T reg not carried: S0=T0 before T0 write (expect NOINPUT)": classify_rule(ph, plants.assemble(ph, [("MOV", "S0", "T0", 0, 0), ("MOV", "T0", "SENSE", 0, 0)])),
}
for k, v in checks.items():
    print(k, "->", v["cls"], v["kinds"], v["ops"])
E = [r for r in rows() if r["kind"] == "evolve"]
res = []
for r in E:
    ph, env = spec_of(r)
    c = classify_genome(ph, genome_of(r))
    res.append({"cell": r["cell_id"], "wave": r["wave"], "fam": r["env"]["family"], "noise": r["physics"]["noise"],
                "SIG": bool(r["labels"]["SIGNAL"]), "held": r["result"]["held"]["acc"], "rules": ph.rules,
                "setrule": ph.setrule, "wimm": ph.wimm, "cls": c["cls"],
                "kinds": sorted(set(k for p in c["rules"] for k in p["kinds"])),
                "per_rule": [p["cls"] for p in c["rules"]]})
save("static_all.json", res)
print(collections.Counter(x["cls"] for x in res))
