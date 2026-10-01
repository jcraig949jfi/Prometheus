"""P2 residual diagnosis (after scoring). Re-runs k3_site_hazard.chain's exact logic (copied, + instrumentation)
under HARV_HALT, same seeds, and at each relabel records: the partner's fidelity to the ORIGINAL implant (was it a
converted copy of the implant?), the partner's side, and who authored the changed implant bytes (prov).
Asserts the instrumented chain reproduces p2_k3_HARV_HALT.json epochs."""
import json, pathlib, random, sys, time
sys.dont_write_bytecode = True
ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C  # noqa: E402
import k3_site_hazard as K  # noqa: E402
import _harv as H  # noqa: E402
arm = ARGV[0] if ARGV else "HARV_HALT"
vm = C.Z8PLAIN if arm == "STOCK" else H.plain(arm)
ref = json.loads(HERE.joinpath("p2_k3_%s.json" % arm).read_text())


def chain(r, x0, rng):
    n = r.L; x = x0
    pool = [C.rand_genome(rng, n) for _ in range(255)]
    pctx = [C.ZERO] * 255; sx = C.ZERO; conv = 0; converted = set()
    for e in range(K.T):
        j = rng.randrange(255); k = rng.randrange(255)
        o0 = C.pair(r, pool[j], pool[k], pctx[j], pctx[k], r.copy_mut, rng)
        pctx[j], pctx[k] = o0["ctx"][0], o0["ctx"][1]
        y = pool[j]; s = rng.randrange(2)
        o = C.outcome(r, x, y, s, sx, pctx[j], r.copy_mut, rng)
        sx, pctx[j] = o["cx"], o["cy"]
        if o["imp_prom"]:
            return {"epoch": e, "implant_side": s, "partner_fid_to_implant_now": round(C.FID(x, y), 3),
                    "partner_fid_to_original_implant": round(C.FID(x0, y), 3),
                    "partner_was_converted_slot": j in converted,
                    "implant_fid_to_original": round(C.FID(x0, x), 3), "wo": o["raw"]["wo"]}
        if o["conv_prom"]:
            conv += 1; pool[j] = o["ny"]; converted.add(j)
        x = r._mutate(x); pool[j] = r._mutate(pool[j])
    return None


t0 = time.time(); out = {"arm": arm}
x7 = C.run_ds.donor_genome()
for sp in K.CELLS:
    r = C.runner_for_spec(sp); r._vm = vm; x = r._pad(x7)
    ev = [chain(r, x, random.Random("K3-chain-%s-%d" % (sp[:4], c))) for c in range(40)]
    ev = [e for e in ev if e]
    assert sorted(e["epoch"] for e in ev) == ref[sp[:4]]["chains"]["epochs"], "instrumented chain diverged"
    out[sp[:4]] = ev
    print(sp[:4], json.dumps(ev), round(time.time() - t0), flush=True)
HERE.joinpath("p2b_residual_%s.json" % arm).write_text(json.dumps(out, indent=1))
