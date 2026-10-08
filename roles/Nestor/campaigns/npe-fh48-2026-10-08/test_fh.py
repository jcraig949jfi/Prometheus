"""fh.py known-answer tests.  python -B test_fh.py
EQ-1  default fh (TG, RANDOM order, scales 1, CT_UA) reproduces the FROZEN XTG-v2 runner exactly (same RNG stream):
      trajectory CS/CD/CD_TX at every shared snapshot, P-11 events and depth, on a short run.
LG-1  ledger conservation: competent count after each snapshot == initial + gains - losses.
DIR-1 order=DIR puts the higher-u organism on side 0 (checked through the real _pair_epoch with a spy).
MS-1  mut_scale / copy_scale set world mut_rate and copy_mut as declared; scale 0 gives no mutation calls changing bytes.
"""
import sys, pathlib
sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fh, xtg2

EP = 120
SEED = 43_000_001


def test_eq1_reproduces_xtg2():
    a = xtg2.make_runner("PAIR_POS", SEED, epochs=EP); oa = a.run()
    b = fh.make_runner(SEED, dict(epochs=EP)); ob = b.run()
    ta = {x["e"]: x for x in a.traj}
    shared = [x for x in b.traj if x["e"] in ta]
    assert shared, "no shared snapshots"
    for x in shared:
        y = ta[x["e"]]
        assert (x["CS"], x["CD"], x["CD_TX"], x["p11_born"]) == (y["CS"], y["CD"], y["CD_TX"], y["p11_born"]), (x, y)
    assert oa["p11_events"] == ob["p11_events"] and oa["max_causal_replication_depth"] == ob["max_causal_replication_depth"]
    assert a.n_gate_pass == b.n_inter


def test_lg1_conservation():
    r = fh.make_runner(SEED, dict(epochs=EP)); r.run()
    n0 = sum(1 for k in r.roots if k["kind"] == "INIT")
    for s in r.ledger_series:
        gains = sum(v for k, v in s.items() if k.startswith("GAIN_"))
        losses = sum(v for k, v in s.items() if k.startswith("LOST_"))
        tr = next(x for x in r.traj if x["e"] == s["e"])
        n = round(tr["CS_gate"] * 256)
        assert n == n0 + gains - losses, (s["e"], n, n0, gains, losses)


def test_dir1_order():
    r = fh.make_runner(SEED, dict(epochs=3, order="DIR"))
    seen = []
    orig = r._pair_interact
    def spy(i, a_, b_):
        seen.append((r.cache.u(r._genome(a_)), r.cache.u(r._genome(b_))))
        return orig(i, a_, b_)
    r._pair_interact = spy
    r.run()
    assert seen and all(ua >= ub for ua, ub in seen), [x for x in seen if x[0] < x[1]][:3]
    assert any(ua > ub for ua, ub in seen)


def test_veto1():
    r = fh.make_runner(SEED, dict(epochs=3, order="VETO"))
    seen = []
    orig = r._pair_interact
    def spy(i, a_, b_):
        seen.append((r.cache.u(r._genome(a_)), r.cache.u(r._genome(b_))))
        return orig(i, a_, b_)
    r._pair_interact = spy
    r.run()
    assert seen and all(ua >= ub for ua, ub in seen) and getattr(r, "n_veto", 0) > 0


def test_ms1_scales():
    r = fh.make_runner(SEED, dict(epochs=2, mut_scale=0.5, copy_scale=3.0))
    assert abs(r.mut_rate - 0.001) < 1e-12 and abs(r.copy_mut - 0.006) < 1e-12
    r0 = fh.make_runner(SEED, dict(epochs=2, mut_scale=0.0))
    g = bytes(range(64))
    assert all(r0._mutate(g) == g for _ in range(200))


def test_hk1_instance_mutate_override_respected():
    """DEF-FH-1 regression: an instance-level _mutate override (used by assays to disable mutation) must be used by
    the ledger wrapper and must survive the interaction. Old wrapper: called the class method and deleted the override."""
    import random
    g = fh.PLANTS["CT_UA"]
    rng = random.Random(45_500_000)
    diffs = 0
    for t in range(40):
        r = fh.make_runner(45_500_000 + t, dict(epochs=1, plant=None, copy_scale=0.0))
        a = r._place(g, 0, niche=0)
        b = r._place(bytes(rng.randrange(256) for _ in range(64)), 1, niche=0)
        r._init_state()
        r._mutate = lambda x: bytes(x)
        f0 = r._mutate
        oid = b.oid
        r._pair_interact(0, a, b)
        assert r._mutate is f0, "override removed"
        if b.oid != oid:
            diffs += r._genome(b) != g
        diffs += r._genome(a) != g
    assert diffs == 0, diffs


if __name__ == "__main__":
    fails = 0
    for name, f in sorted(globals().items()):
        if name.startswith("test_") and callable(f):
            try:
                f(); print("PASS", name)
            except Exception as e:
                fails += 1; print("FAIL", name, repr(e))
    sys.exit(1 if fails else 0)
