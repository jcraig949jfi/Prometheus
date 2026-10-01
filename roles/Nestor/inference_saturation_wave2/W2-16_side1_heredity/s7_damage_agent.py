"""Step 7: what in the random first-mover does the damage? For each WORLD interaction of s4 (side-1 donors, 60 victims
each), log the partner context's LDIRs (traced VM) and count damage events with / without a partner LDIR, and the bytes
written by partner LDIRs. Then the VM dependence: rate at which 300 steps of uniform-random side-0 code change ANY byte
of side 1 (inert side-1 content = 64 x 0x76, never executed), on the DENSE VM (1-byte LDIR/LDDR opcodes 0xE5/0xE7)
vs the PLAIN VM (LDIR only as ED B0/B8), same cell parameters (ffa6), 2000 random halves."""
import json, pathlib, collections
from _env import A, ROWS, shabytes, traced_dense
from s4_order_and_interference import interact2

T = traced_dense()
side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
c = collections.Counter()
for r in side1:
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); A.env(r["vm"], r["cell"]); n = P["n"]
    for j in range(60):
        vb = shabytes("W2-16", r["key"], j, n=n)
        T._LD = []
        _, _, snaps, _ = interact2(T, P, vb, G, (0, 1))
        ld = T._LD; T._LD = None
        vld = [x for x in ld if x[0] == 1]
        pre = snaps[0][n:2 * n] != G
        key = ("PRE_DAMAGE" if pre else "CLEAN") + ("_with_partner_LDIR" if vld else "_no_partner_LDIR")
        c[key] += 1
        if pre:
            c["pre_damage_partner_LDIR_bytes_sum"] += sum(min(x[3], 300) for x in vld)
            # where was the partner's LDIR opcode? (pc after decode: -1 dense opcode / -2 ED form; use -1..-2 both in half)
            locs = set("IN_COPIER_CODE" if n <= ((x[5] - 1) & 0x7f) < 2 * n else "IN_PARTNER_CODE" for x in vld)
            for l in locs:
                c["pre_damage_partner_LDIR_" + l] += 1
            if locs == {"IN_COPIER_CODE"}:
                c["pre_damage_ONLY_copier_code_LDIR"] += 1
res = {"side1_world": dict(c)}
print(res)
P = A.params("DENSE", "ffa6")
vmres = {}
for vm in ("DENSE", "PLAIN"):
    _, _, z = A.env(vm, "ffa6")
    hit = 0
    for j in range(2000):
        vb = shabytes("W2-16-VM", j, n=64)
        _, _, snaps, _ = interact2(z, P, vb, bytes([0x76]) * 64, (0,))
        hit += snaps[0][64:128] != bytes([0x76]) * 64
    vmres[vm] = {"n": 2000, "side1_changed_by_random_side0": hit, "rate": round(hit / 2000, 3)}
res["vm_dependence"] = vmres
print(vmres)
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(res, indent=1))
