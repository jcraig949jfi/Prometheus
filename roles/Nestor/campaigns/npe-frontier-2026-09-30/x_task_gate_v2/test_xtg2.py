"""X-TASK-GATE v2 known-answer and regression tests.  python -B test_xtg2.py   (exit 0 = all pass)

KA   static known answers (xtg2.selftest): CT_UA competent; CT_U and COPY_ONLY use 0; CT_U passes the OLD
     bridge+reader ruler (the defect being repaired); world witness 1.0; echo-base and always-transform 0.
RG-1 cache: same genome, different task identity -> no cross-task hit (W2-8 D1).
PV-1 a P-11 birth from a competent CT_UA donor onto a non-competent partner is P11 / P11_TX, inherits the
     donor's competence root and counts one P11 transmission hop.
PV-2 an in-place (ATOMIC) mutation that CREATES competence is origin MUT with a new root, never *_TX.
PV-3 ordering regression (found in Flight 1): the donor half is mutated in place in the same interaction and
     loses competence; the child it built from its PRE-interaction genome is still P11_TX, not *_CREATED.
GT-1 SHUF gate reads competence from two other organisms; TG from the pair (structural check on the code path).
"""
from __future__ import annotations

import pathlib
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import xtg2  # noqa: E402


def _fresh(arm="PAIR_POS", seed=43_950_000):
    r = xtg2.make_runner(arm, seed, epochs=5)
    for i in range(4):
        o = r._place(r._seed_genome(), i, niche=0)
        o.energy = 600
    return r


def _set(r, o, g):
    r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
    r.mem[o.slot:o.slot + len(g)] = g
    o.length = len(g)


def _convert_once(patch_third_mutation=None, max_tries=60):
    """Drive CT_UA (side 0) x random partner (side 1) through the REAL _pair_interact until a P-11 birth."""
    for t in range(max_tries):
        r = _fresh(seed=43_950_000 + t)
        a, b = [o for o in r.orgs if o.alive][:2]
        _set(r, a, xtg2.CT_UA)
        r._init_state()
        calls = []
        if patch_third_mutation is not None:
            orig = r._mutate

            def m(g, _orig=orig):
                calls.append(1)
                return patch_third_mutation if len(calls) == 3 else bytes(g)
            r._mutate = m
        else:
            r._mutate = lambda g: bytes(g)
        oid_b = b.oid
        r._pair_interact(0, a, b)
        if b.oid != oid_b and r.st[b]["prov"] == "P11":
            return r, a, b
    raise AssertionError("no P-11 conversion in %d tries" % max_tries)


def test_known_answers():
    res = xtg2.selftest()
    assert res["pass"]


def test_pv1_transmission():
    r, a, b = _convert_once()
    sa, sb = r.st[a], r.st[b]
    assert sa["origin"] == "INIT" and sa["root"] is not None
    assert sb["origin"] == "P11_TX", sb
    assert sb["root"] == sa["root"] and sb["tx_p11"] == 1 and sb["donor_comp"] is True


def test_pv2_mutation_created():
    r = _fresh()
    a, b = [o for o in r.orgs if o.alive][:2]
    _set(r, a, xtg2.CT_U)                 # copier that reads but does not use: not competent
    r._init_state()
    assert r.st[a]["comp"] is False
    oid_a = a.oid
    ct_u = xtg2.CT_U
    r._mutate = lambda g: xtg2.CT_UA if bytes(g) == ct_u else bytes(g)   # mutation turns CT_U into CT_UA in place
    r._pair_interact(0, a, b)
    if a.oid == oid_a:                    # a not overwritten -> in-place path
        assert r.st[a]["origin"] == "MUT" and r.st[a]["comp"] is True, r.st[a]
        assert r.roots[r.st[a]["root"]]["kind"] == "MUT"
    else:
        raise AssertionError("partner overwrote CT_U; choose another seed")


def test_pv3_donor_mutated_same_interaction():
    r, a, b = _convert_once(patch_third_mutation=xtg2.COPY_ONLY)
    assert r._genome(a) == xtg2.COPY_ONLY and r.st[a]["comp"] is False and r.st[a]["root"] is None
    assert r.st[b]["origin"] == "P11_TX", r.st[b]


def test_gt1_gate_code_path():
    import inspect
    src = inspect.getsource(xtg2.make_runner)
    assert 'if gate == "TG":' in src and "c_, d_ = a_, b_" in src
    assert "shuf_rng.randrange(len(alive))" in src


if __name__ == "__main__":
    fails = 0
    for name, f in sorted(globals().items()):
        if name.startswith("test_") and callable(f):
            try:
                f()
                print("PASS", name)
            except Exception as e:      # noqa: BLE001
                fails += 1
                print("FAIL", name, repr(e))
    sys.exit(1 if fails else 0)
