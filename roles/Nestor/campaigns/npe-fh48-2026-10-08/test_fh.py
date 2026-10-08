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


def test_xp1_extra_plants():
    import exp
    ctw = exp.CT_W
    r = fh.make_runner(SEED, dict(epochs=1, extra_plants=[ctw]))
    r.run()
    gs = [r._genome(o) for o in r.orgs]
    assert gs[0][:7] == fh.PLANTS["CT_UA"][:7]
    assert r.roots and sum(1 for k in r.roots if k["kind"] == "INIT") == 2


def test_js1_bytes_plant_row_serializes():
    """DEF-FH-2 regression: run_one with a bytes plant and bytes extra plant must write its row."""
    import tempfile, json, exp
    d = tempfile.mkdtemp()
    rec = fh.run_one("T", "JS", SEED, dict(epochs=2, plant=exp.ct_ua_add(0x24), extra_plants=[exp.CT_W]), d)
    assert json.loads(open(d + "/JS_%d.json" % SEED).read())["cfg"]["plant"]["hex"] == exp.ct_ua_add(0x24).hex()


def _ontape_rate(plant, n=80, side=0):
    import random
    rng = random.Random(46_000_000)
    ok = tot = conv_ok = conv_tot = 0
    for k in range(n):
        r = fh.make_runner(46_000_000 + k, dict(epochs=1, plant=None, order="ONTAPE", gate="CONST", p_const=1.0))
        a = r._place(fh.PLANTS[plant], 0, niche=0)
        b = r._place(bytes(rng.randrange(256) for _ in range(64)), 1, niche=0)
        r._init_state()
        r._mutate = lambda x: bytes(x)
        before = list(r.ontape_n)
        oid = b.oid
        r._pair_interact(0, a, b)
        ok += r.ontape.get(a, 0) > 0
        tot += 1
        if b.oid != oid:
            conv_tot += 1
            conv_ok += r.ontape.get(b, 0) > 0
    return ok / tot, conv_ok / max(1, conv_tot)


def test_ot1_ontape_known_answers():
    """ONTAPE ruler: CT_UA answers correctly on the tape (donor and its fresh copy); CT_U ~ half (r = 0 only);
    COPY_ONLY never; the offline scorer is not used."""
    ua, ua_copy = _ontape_rate("CT_UA")
    u, _ = _ontape_rate("CT_U")
    co, _ = _ontape_rate("COPY_ONLY")
    print("ontape CT_UA", ua, "copy", ua_copy, "CT_U", u, "COPY_ONLY", co)
    assert ua >= 0.95 and ua_copy >= 0.85, (ua, ua_copy)
    assert 0.3 <= u <= 0.7, u
    assert co == 0.0, co


def test_tr1_tape_ruler_matches_independent_and_controls():
    """fh _tape_self == arch.tape_use(g, g) (independent implementation); CT_UA 1.0, CT_U 0, COPY_ONLY 0."""
    import arch
    r = fh.make_runner(SEED, dict(epochs=1, plant=None))
    for k in ("CT_UA", "CT_U", "COPY_ONLY"):
        g = fh.PLANTS[k]
        assert abs(r._tape_self(g) - arch.tape_use(g, g)) < 1e-12, k
    assert r._tape_self(fh.PLANTS["CT_UA"]) == 1.0
    assert r._tape_self(fh.PLANTS["CT_U"]) == 0.0 and r._tape_self(fh.PLANTS["COPY_ONLY"]) == 0.0


def test_le1_long_horizon_not_capped():
    """DEF-FH-3 regression: epochs above the tier's 2000 must be honoured (old: silently capped at 2000)."""
    assert fh.make_runner(SEED, dict(epochs=8000)).t["epochs"] == 8000
    assert fh.make_runner(SEED, dict(epochs=50)).t["epochs"] == 50
    assert fh.make_runner(SEED, dict()).t["epochs"] == 2000


G1_ABR_MUTANT = "ed327dee405fe5db0047db0d4fdb305779fe02380e78a9477afe00782802c625d31076dfd300f99ea4640e3f4c1e25bf1342749d6de3628982c8ffa00dc27ef5"


def test_tr2_partner_gets_inputs():
    """DEF-FH-4 regression: a lineage from X-ONTAPE-LONG seed 45300004 whose answer-before-read branch is mutated
    (byte 35) wrecks the scored half only when the PARTNER runs without inputs. Old ruler: 0.5; corrected: >= 0.75.
    Controls unchanged."""
    import arch
    g = bytes.fromhex(G1_ABR_MUTANT)
    assert arch.tape_use(g, g, partner_inputs=False) == 0.5
    assert arch.tape_use(g, g) >= 0.75
    r = fh.make_runner(SEED, dict(epochs=1, plant=None))
    assert r._tape_self(g) == arch.tape_use(g, g)
    for k, want in (("CT_UA", 1.0), ("CT_U", 0.0), ("COPY_ONLY", 0.0)):
        assert arch.tape_use(fh.PLANTS[k], fh.PLANTS[k]) == want, k


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
