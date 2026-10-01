"""P2: W2-3 K3 single-site chain (k3_site_hazard.chain unchanged, same seeds, 40 chains/cell) with the runner's VM
swapped to the arm's PLAIN-z8 build. Usage: python -B p2_k3.py ARM  (STOCK | HARV_HALT | HARV_WRAP).
STOCK uses the campaign z8 module itself (exact reproduction target 24/40, 17/40).
Also K3 part1 per-interaction rates (unchanged code) under the arm."""
import json, pathlib, random, sys, time
sys.dont_write_bytecode = True
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]   # k3_site_hazard parses sys.argv[1] at import
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C  # noqa: E402
import k3_site_hazard as K  # noqa: E402
import _harv as H  # noqa: E402

arm = ARGV[0]
CH = int(ARGV[1]) if len(ARGV) > 1 else 40
vm = C.Z8PLAIN if arm == "STOCK" else H.plain(arm)
t0 = time.time()
res = {"arm": arm}
x7 = C.run_ds.donor_genome()
for sp in K.CELLS:
    r = C.runner_for_spec(sp)
    r._vm = vm
    x = r._pad(x7)
    # same-physics check: C.pair routes through r._vm
    o = C.pair(r, x, C.rand_genome(random.Random(1), r.L))
    assert C.world.z8 is vm
    rec = {"part1": K.part1(r, x, random.Random("K3-" + sp[:4]))}
    hits0 = getattr(vm, "_HITS", [0])[0]
    ch = [K.chain(r, x, random.Random("K3-chain-%s-%d" % (sp[:4], c))) for c in range(CH)]
    lost = [e for e, _ in ch if e is not None]
    rec["chains"] = {"n": CH, "relabelled_by_T": len(lost), "share": len(lost) / CH, "epochs": sorted(lost),
                     "converted_any": sum(cv > 0 for _, cv in ch),
                     "harv_hits_during_chains": getattr(vm, "_HITS", [0])[0] - hits0}
    res[sp[:4]] = rec
    print(arm, sp[:4], json.dumps(rec["chains"])[:250], round(time.time() - t0, 1), flush=True)
res["cpu_s"] = round(time.time() - t0, 1)
HERE.joinpath("p2_k3_%s.json" % arm).write_text(json.dumps(res, indent=1))
