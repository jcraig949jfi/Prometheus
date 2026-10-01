"""Step 8: when the random partner's pc enters the side-1 copier's half (world order, s4 victims), WHERE does it
enter (first pc offset within the copier) and does that predict damage vs a clean (often partner-built) copy?
Hypothesis: entering at/before the copier's register set-up reproduces the copier's own copy (harmless, child built
by the partner from parental bytes); entering past it runs the copier's LDIR with the partner's registers (smear)."""
import json, pathlib, collections
from _env import A, ROWS, shabytes, traced_dense
from s4_order_and_interference import interact2
import p11

T = traced_dense()
side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
out = {}
for r in side1:
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); A.env(r["vm"], r["cell"]); n = P["n"]
    # the copier's own entry trace (no partner): pcs it executes before its first LDIR
    T._TR = []; T._LD = []
    interact2(T, P, bytes([0x76]) * n, G, (0, 1))
    own = [pc - n for w, pc, op in T._TR if w == 2]
    first_ld_pc = min([x[5] for x in T._LD if x[0] == 2], default=None)
    T._TR = T._LD = None
    pre_ldir_path = []
    for pc in own:
        if first_ld_pc is not None and pc + n == ((first_ld_pc - 1) & 0x7f):
            break
        pre_ldir_path.append(pc)
    by = collections.defaultdict(collections.Counter)
    for j in range(60):
        vb = shabytes("W2-16", r["key"], j, n=n)
        T._TR = []
        tape, _, snaps, _ = interact2(T, P, vb, G, (0, 1))
        tr = T._TR; T._TR = None
        ent = next((pc - n for w, pc, op in tr if w == 1 and n <= pc < 2 * n), None)
        if ent is None:
            continue
        pre = snaps[0][n:2 * n] != G
        good = p11.fidelity(G, bytes(tape[0:n])) >= 0.9
        where = "ON_SETUP_PATH" if ent in pre_ldir_path[:1] else ("ON_PATH_LATER" if ent in pre_ldir_path else "OFF_PATH")
        by[where]["n"] += 1; by[where]["pre_damage"] += pre; by[where]["good"] += good
    out[r["key"]] = {"copier_pre_LDIR_path": pre_ldir_path, "by_entry": {k: dict(v) for k, v in by.items()}}
    print(r["key"], pre_ldir_path[:12], {k: dict(v) for k, v in by.items()})
agg = collections.defaultdict(collections.Counter)
for v in out.values():
    for k, c in v["by_entry"].items():
        agg[k].update(c)
out["_aggregate"] = {k: dict(v) for k, v in agg.items()}
print(out["_aggregate"])
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
