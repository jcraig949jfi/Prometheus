"""W2-6 check C7b (T6 vs T7, BASE miss): chain the founder through K successive world interactions with fresh random
partners (its own content + context carried, as on the pair tape), under BASE vs ATOMIC write-back, and record its
conversion probability and survival (not overwritten) at each step. A T6 'iterated map' reading of erosion predicts
conversion decays with steps under BASE only; the plain offspring law T7 uses is step-invariant.
Same physics/harness as c7_t6_t7_base_closure.py (imported). Output c7b_base_chain.json.
"""
import json, random, sys, time
sys.argv = sys.argv[:1] + ["1"]          # c7 runs its own N=1 demo on import; harmless
import c7_t6_t7_base_closure as C        # noqa: E402

K, N = 12, 250
t0 = time.process_time()
rng = random.Random(77)
out = {}
for name, base in (("BASE", C.world.Runner), ("ATOMIC", C.run_ds.runner_cls(C.world))):
    h = C.harness(base, 99)
    conv = [0] * K; alive = [0] * K; byt = [0] * K
    for i in range(N):
        g, st = C.G7, (None, 0, 0)
        side = i % 2
        for k in range(K):
            pg = bytes(rng.randrange(256) for _ in range(64))
            a = C.one(h, g, st, pg, rng.randrange(2))
            alive[k] += 1
            conv[k] += a["conv"]
            if a["hijacked"]:
                break
            g, st = a["d_after"]
            byt[k] += sum(1 for x, y in zip(g, C.G7) if x != y)
    out[name] = {"step_conv": [round(c / a_, 3) if a_ else None for c, a_ in zip(conv, alive)],
                 "step_alive": alive, "bytes_from_founder": [round(b / a_, 1) if a_ else None for b, a_ in zip(byt, alive)],
                 "expected_offspring_K": round(sum(conv) / N, 3)}
    print(name, out[name], round(time.process_time() - t0, 1), flush=True)
out["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(out, open(C.HERE / "c7b_base_chain.json", "w"), indent=1)
