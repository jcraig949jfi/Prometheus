"""P3: N1 magnet_rate.py protocol (copied logic, fixed string seeds) for the 7ae3 founder in its OWN cell, under
STOCK (campaign z8), HARV_HALT, HARV_WRAP (PLAIN builds). N2 prediction = 0.5 x side-0 predecessor-accepted overwrite
rate. Also founder knockouts (SELF 23-24, LDIR 52-53) as N1 did, and authorship of changed bytes.
The predecessor ruler (p11.predecessor_accepts on fidelities) is VM-free; the interaction runs on the arm's VM."""
import json, os, pathlib, random, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[1] / "campaigns"
sys.path[:0] = [str(CAMP / "c9x-explore-2026-09-24" / "x_donor_swap"), str(CAMP / "z80atlas-verify-2026-09-22")]
import world, z8, p11, run_ds  # noqa: E402
import _harv as H  # noqa: E402

N = 1500
g = run_ds.donor_genome()
sp = "7ae3f9c1437c8000-s54765-tL-a0"
a = run_ds.cells()[sp]
r = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
n = r.L; tl = world._pow2(2 * n)
kw = dict(n=n, tape_len=tl, budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=r.copy_mut)
variants = {"intact": g}
for name, pos in (("ko_self", (23, 24)), ("ko_ldir", (52, 53))):
    b = bytearray(g)
    for i in pos:
        b[i] = 0
    variants[name] = bytes(b)
t0 = time.time()
out = {"cell": sp, "ops_mask": r._ops_mask(), "L": n, "slice": r.t["slice"], "arms": {}}
for arm in ("STOCK", "HARV_HALT", "HARV_WRAP"):
    vm = z8 if arm == "STOCK" else H.plain(arm)
    res = {}
    for ctxname in ("zero", "random"):
        for vname, fg in variants.items():
            R = random.Random("W2-23-P3-%s-%s" % (ctxname, vname))   # same draws in every arm
            hits = {0: 0, 1: 0}; auth = [0, 0]; harv_hit = 0
            for t in range(N):
                pb = bytes(R.randrange(256) for _ in range(n))
                side = t % 2
                st_f = (None, 0, 0) if ctxname == "zero" else ([R.randrange(256) for _ in range(8)], 0, 0)
                st_p = (None, 0, 0) if ctxname == "zero" else ([R.randrange(256) for _ in range(8)], 0, 0)
                ga, gb = (fg, pb) if side == 0 else (pb, fg)
                sa, sb = (st_f, st_p) if side == 0 else (st_p, st_f)
                if arm != "STOCK":
                    vm._HITS[0] = 0
                tape, prov, lit, wo = p11.interact(vm, ga=ga, gb=gb, st_a=sa, st_b=sb, rng=random.Random(t), **kw)
                if arm != "STOCK":
                    harv_hit += vm._HITS[0] > 0
                h0 = 0 if side == 0 else n
                fh = bytes(tape[h0:h0 + n])
                if p11.predecessor_accepts(p11.fidelity(fh, pb), p11.fidelity(fh, fg), wo[1 - side], n):
                    hits[side] += 1
                    who = [prov[h0 + i] for i in range(n) if fh[i] != fg[i]]
                    auth[0] += sum(1 for x in who if x == side + 1); auth[1] += sum(1 for x in who if x == 2 - side)
            res["%s/%s" % (ctxname, vname)] = {"side0": hits[0], "side1": hits[1], "n_per_side": N // 2,
                                                "bytes_by_founder_ctx": auth[0], "bytes_by_partner_ctx": auth[1],
                                                "interactions_with_harv_hit": harv_hit,
                                                "N2_epoch1_pred": round(0.5 * hits[0] / (N // 2), 4)}
    out["arms"][arm] = res
    print(arm, json.dumps({k: (v["side0"], v["side1"], v["N2_epoch1_pred"]) for k, v in res.items()}), round(time.time() - t0, 1), flush=True)
out["seconds"] = round(time.time() - t0, 1)
HERE.joinpath("p3_n2.json").write_text(json.dumps(out, indent=1))
