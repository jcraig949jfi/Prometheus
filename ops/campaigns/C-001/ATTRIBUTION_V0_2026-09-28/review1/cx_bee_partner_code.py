"""Counter-example CX-5b: in PAIR_EXECUTION the PARTNER's code performs the copy; the BEE adapter still records the writer
as the sole performer (kind organism_code) and the birth as SELF_CONSTRUCTED. The native tracer itself separates the two
(by_own_code = 0, win_steps > 0, codeprov 'foreign'); the adapter keeps those numbers in exec_where/exec_what and ignores them."""
import os, sys, random
REPO = os.path.expanduser("~/Prometheus-worktrees/rev1")
sys.path.insert(0, REPO); sys.path.insert(0, REPO + "/roles/Bellerophon/forensics_2026-09-23/tools")
import traced_replay as TR
vm, W = TR._install()
from archaeon.attribution import assay as A, schema as S, classify as K

L = 64; rng = random.Random(2)
a = bytes(rng.randrange(0x50, 0x80) for _ in range(L))          # undefined opcodes: executes as a NOP sled into the window
SHIFT = int(sys.argv[1]) if len(sys.argv) > 1 else 0                 # 0: full-window copy; 12: shifted copy (label error case)
bcode = bytes([0x07, 0, 0x08, 64 + SHIFT, 0x03, 64 - SHIFT, 0x15, 0xFF])   # partner code: S=0 T=64+SHIFT C=64-SHIFT LDIR, HALT
b = bcode + bytes(rng.randrange(0x50, 0x80) for _ in range(L - len(bcode)))
mem = bytearray(256); mem[:L] = a; mem[L:2 * L] = b
TR._ACC.update(L=L, writes={}, own_steps=0, win_steps=0, other_steps=0, prior=b, writer_tape=a)
vm.execute(mem, 2 * L, 0, 500, [])
child, new_a = bytes(mem[L:2 * L]), bytes(mem[:L]); ws = TR._ACC["writes"]
fid_w = 1 - sum(x != y for x, y in zip(child, new_a)) / L; fid_t = 1 - sum(x != y for x, y in zip(child, b)) / L
own = sum(1 for _, (s, pc, op) in ws.items() if op in TR.COPY_OPS and s is not None and s < L)
byown = sum(1 for _, (s, pc, op) in ws.items() if op in TR.COPY_OPS and s is not None and s < L and pc < L)
foreign = sum(1 for _, (s, pc, op) in ws.items() if op in TR.COPY_OPS and s is not None and s < L and L <= pc < 2 * L)
row = [0, 1, 2, "PAIR_EXECUTION", round(fid_w, 3), round(fid_t, 3), "target" if fid_t > fid_w else "writer", len(ws), own, byown,
       sum(child[k] != b[k] for k in range(L)), 0, 0, TR._ACC["own_steps"], TR._ACC["win_steps"], TR._ACC["other_steps"], 0, 0, 0, 0]
rec, = A.bee_records({"births_rows": [row], "codeprov": [{"own_region": byown, "self_copied": 0, "foreign": foreign, "elsewhere": 0}], "rid": "toy"})
print("row:", row)
print("native: copied_from_own=%d by_own_code=%d own_steps=%d win_steps=%d codeprov foreign=%d" % (own, byown, row[13], row[14], foreign))
print("adapter performers:", rec["carrier"]["performers"], " exec_what:", rec["carrier"]["exec_what"])
print("adapter class:", K.production_class(rec), " producer_ne_donor:", S.producer_ne_donor(rec), " invalid:", S.check(rec))
