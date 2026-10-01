import gzip, json, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parents[6]
rows = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
print(len(rows), sorted(rows[0].keys()))
FLIP = "4b848d80 603723a7 d3f36006 50060cf9 56cdba0a d99833cb f476a3ca f4e59e61 fc6972d4".split()
XOR = "93b9eeeb 89a6a9cd d01883ed 33505249 b3549a65 247e0d43 4ca24b85".split()
MAJ = "fded1681 3c3d996a 626aa72f e341694d 070257d7 13a086e9 3d20243a".split()
keys = ["topology","n_sites","radius","dest_mode","fanout","update_mode","update_period","update_p","rules","setrule","wimm","prog_len","state_dim","payload_width","channels","e_income","e_max","c_emit","c_op","c_mem","loss","lat_base","lat_hop","lat_jitter","decay_shift","cap","collision","noise","dup","mut_site","plastic_route"]
def show(r):
    p=r["physics"]; e=r["env"]
    print(r["cell_id"][:8], r["kind"], e["family"], "d",e["d"],"delta",e["delta"],"tr",e["trials"], {k:p[k] for k in keys})
cnt=collections.Counter()
for r in rows:
    p=r["physics"]
    if p["c_op"]>0 or p["c_emit"]>0: cnt[(r["env"]["family"], r["kind"], p["c_op"],p["c_emit"],p["e_income"],p["e_max"],p["c_mem"])]+=1
for k,v in sorted(cnt.items()): print(k,v)
for grp in (FLIP,XOR,MAJ):
    for c in grp:
        for r in rows:
            if r["cell_id"].startswith(c) and r["kind"]=="evolve": show(r)
