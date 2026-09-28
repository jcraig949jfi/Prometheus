"""Counter-example CX-5a: BEE adapter reads 'copied from the writer's own region' (source ADDRESS < L) as writer IBD.
Runs Bellerophon's own traced VM (traced_replay._install, unmodified) on a 2L pair-execution memory, rebuilds the row
exactly as traced_replay._register_offspring does, and feeds it to archaeon.attribution.assay.bee_records."""
import os, sys, random
REPO = os.path.expanduser("~/Prometheus-worktrees/rev1")
sys.path.insert(0, REPO); sys.path.insert(0, REPO + "/roles/Bellerophon/forensics_2026-09-23/tools")
import traced_replay as TR
vm, W = TR._install()
from archaeon.attribution import assay as A, schema as S, classify as K

L = 64
rng = random.Random(1)
b = bytes(rng.randrange(0x80, 0xFF) for _ in range(L))        # partner/occupant tape (bytes >=0x80: never executed here)
code = bytes([0x01, 0x99,  0x08, 112,  0x11,                  # A=0x99; T=112; (T)=A      -> 1 non-copy write into the window
              0x07, 64,  0x08, 20,  0x03, 44,  0x15,          # S=64 T=20 C=44 LDIR  : partner bytes -> writer's scratch [20,64)
              0x07, 20,  0x08, 64,  0x03, 44,  0x15,          # S=20 T=64 C=44 LDIR  : scratch -> window (src < L)
              0xFF])
a = code + bytes(L - len(code))
mem = bytearray(256); mem[:L] = a; mem[L:2 * L] = b
TR._ACC.update(L=L, writes={}, own_steps=0, win_steps=0, other_steps=0, prior=b, writer_tape=a)
tr = vm.execute(mem, 2 * L, 0, 500, [])
child, new_a = bytes(mem[L:2 * L]), bytes(mem[:L])
ws = TR._ACC["writes"]
# ---- row, formula-for-formula from traced_replay._register_offspring (parent.tape == new_a at that point in world.step)
fid_w = 1.0 - sum(x != y for x, y in zip(child, new_a)) / L
fid_t = 1.0 - sum(x != y for x, y in zip(child, b)) / L
material = "target" if fid_t > fid_w else "writer"
own = sum(1 for _, (src, pc, op) in ws.items() if op in TR.COPY_OPS and src is not None and src < L)
byown = sum(1 for _, (src, pc, op) in ws.items() if op in TR.COPY_OPS and src is not None and src < L and pc < L)
row = [0, 1, 2, "PAIR_EXECUTION", round(fid_w, 3), round(fid_t, 3), material, len(ws), own, byown,
       sum(child[k] != b[k] for k in range(L)), 0, 0, TR._ACC["own_steps"], TR._ACC["win_steps"], TR._ACC["other_steps"], 0,
       round(1 - sum(x != y for x, y in zip(child, a)) / L, 3), 0, 0]
cp = {"own_region": byown, "self_copied": 0, "foreign": 0, "elsewhere": 0}
true_partner_bytes = sum(child[k] == b[k] for k in range(L))
rec, = A.bee_records({"births_rows": [row], "codeprov": [cp], "rid": "toy"})
print("row:", row)
print("ground truth: child bytes identical to partner's original bytes at the same locus:", true_partner_bytes, "/", L)
print("native label (resemblance):", material)
print("adapter donors (IBD):", S.donors(rec), " invalid:", S.check(rec), " class:", K.production_class(rec))
top = max(S.donors(rec), key=S.donors(rec).get)
print("assay counts this birth under 'native_label_target_but_IBD_majority_writer':", material == "target" and top == "bee:1")
