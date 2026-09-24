"""World graph, law ledger lifecycle, quotient, Atlas export."""
import json

import pytest

from prometheus.cosmos.atlas_export import export
from prometheus.cosmos.pipeline import Chamber
from prometheus.cosmos.quotient import quotient
from prometheus.cosmos.store import Store
from prometheus.cosmos.substrates import visible


@pytest.fixture
def chamber(tmp_path):
    st = Store(tmp_path / "s")
    return Chamber(list(visible().values()), store=st, campaign="t"), st


def test_edges_and_nodes_record_transformations(chamber):
    ch, st = chamber
    fam = ch.fams["regs"]
    p = dict(V=8, H=16, K=4, R=1.0, bitcost=4e-3, q=0.003)
    base = ch.observe("regs", p)
    for k, q in fam.deform(p):
        ch.observe("regs", q, parent=base["world_id"], edge_kind="DEFORMATION_OF", delta={"knob": k})
    ch.observe("regs", fam.sham(p), parent=base["world_id"], edge_kind="CONTROL_OF", delta={"control": "sham"})
    st.commit()
    c = st.counts()
    assert c["edges"] == len(fam.deform(p)) + 1
    assert st.edge_counts()["CONTROL_OF"] == 1
    with pytest.raises(ValueError):
        st.add_edge(base["world_id"], base["world_id"], "DEFORMATION_OF", {})
    with pytest.raises(ValueError):
        st.add_edge("a", "b", "NOT_A_KIND", {})


def test_law_lifecycle_keeps_failed_predecessors(tmp_path):
    st = Store(tmp_path)
    body = {"law": {"law": "C <= 0.3", "atoms": [[["var", "C"], 0.3, 1.0]], "complexity": 1}, "cmap": "v1"}
    a = st.propose_law(body)
    st.event(a, "ATTACKED")
    st.event(a, "FAILED", "counterexample")
    b = st.propose_law(dict(body, cmap="v2"), parent=a)
    fh = st.freeze_law(b)
    assert st.freeze_law(b) == fh                        # freezing is idempotent, never re-hashed
    la, lb = st.law(a), st.law(b)
    assert [e["status"] for e in la["events"]] == ["PROPOSED", "ATTACKED", "FAILED", "REVISED"]
    assert lb["parent"] == a and lb["version"] == 2 and lb["freeze_hash"] == fh
    assert len(st.laws()) == 2
    assert st.receipts.verify() is None


def test_quotient_compresses_and_marks_boundaries(chamber):
    ch, st = chamber
    p = dict(V=8, H=16, K=4, R=1.0, bitcost=4e-3, q=0.003)
    base = ch.observe("regs", p)
    for c in (1e-4, 3e-4, 0.064, 0.128):
        ch.observe("regs", dict(p, bitcost=c), parent=base["world_id"], edge_kind="DEFORMATION_OF", delta={})
    q = quotient(ch.log, ch.edges)
    assert q["n_nodes"] == 5 and q["n_classes"] < 5
    assert 0 < q["boundary_edge_fraction"]["DEFORMATION_OF"] <= 1


def test_atlas_export_shapes(chamber, tmp_path):
    ch, st = chamber
    p = dict(V=8, H=16, K=4, R=1.0, bitcost=4e-3, q=0.003)
    base = ch.observe("regs", p)
    ch.observe("regs", dict(p, q=0.01), parent=base["world_id"], edge_kind="DEFORMATION_OF", delta={"knob": "q"})
    st.commit()
    n = export(tmp_path / "s", tmp_path / "atlas")
    assert n == {"edges": 1, "facts": 2}
    e = json.loads((tmp_path / "atlas" / "atlas_edge.jsonl").read_text().splitlines()[0])
    assert e["relation"] == "DEFORMATION_OF" and e["dst_key"] == base["world_id"] and e["basis"] == "DECLARED"


def test_null_pool_crash_falls_back_to_serial(monkeypatch):
    """A broken process pool must not kill a campaign: the null is recomputed with fewer workers / serially."""
    import numpy as np
    import concurrent.futures
    from concurrent.futures.process import BrokenProcessPool
    from prometheus.cosmos import miner

    class Boom:
        def __init__(self, *a, **k):
            raise BrokenProcessPool("simulated child death")

    monkeypatch.setattr(concurrent.futures, "ProcessPoolExecutor", Boom)
    rng = np.random.default_rng(0)
    n = 60
    X = {"C": rng.uniform(0, 1, n), "N": rng.uniform(0, 1, n), "K": rng.integers(0, 5, n).astype(float), "G": np.full(n, 0.5)}
    y = (X["C"] < 0.4).astype(int)
    M = miner.Miner(X, y, np.repeat(["a", "b", "c"], 20), max_size=3, conj=False)
    before = len(miner.NULL_POOL_FAILURES)
    got = M._null_scores([rng.permutation(y) for _ in range(3)], workers=4)
    assert len(got) == 3 and len(miner.NULL_POOL_FAILURES) > before


def test_two_sided_flips_on_a_band_law():
    """The G6 defect: a band law has two flips along C -> C f. Both must be found; the grid edge is not a flip."""
    from prometheus.cosmos.broker import two_sided_flips
    from prometheus.cosmos.miner import Law
    band = Law(atoms=[(("var", "C"), 0.4, 1.0), (("mul", ("var", "C"), ("var", "K")), 0.2, -1.0)], complexity=5)
    band.alpha, band.scales = 50.0, [1.0, 1.0]
    r = two_sided_flips(band, {"C": 0.1, "N": 0.0, "K": 4.0, "G": 0.5})
    assert r["pays_at_1"]
    assert abs(r["f_hi"] - 4.0) / 4.0 < 0.01          # C*f <= 0.4  -> f_hi = 4
    assert abs(r["f_lo"] - 0.5) / 0.5 < 0.01          # C*f*K >= 0.2 -> f_lo = 0.5
    one = Law(atoms=[(("var", "C"), 0.4, 1.0)], complexity=1)
    one.alpha, one.scales = 50.0, [1.0]
    r1 = two_sided_flips(one, {"C": 0.1, "N": 0.0, "K": 4.0, "G": 0.5})
    assert r1["f_lo"] is None and abs(r1["f_hi"] - 4.0) / 4.0 < 0.01


def test_adversary_rounds_attack_fresh_worlds():
    """C0s defect: repeated rounds must not re-fire already-observed worlds."""
    import numpy as np
    from prometheus.cosmos.adversary import attack
    from prometheus.cosmos.contract import coords_of
    from prometheus.cosmos.miner import Law
    from prometheus.cosmos.world import world_id
    fams = visible()
    fam = fams["regs"]
    rng = np.random.default_rng(0)
    sp = fam.space()
    pool = []
    for _ in range(120):
        p = {k: v[rng.integers(len(v))] for k, v in sp.items()}
        pool.append({"family": "regs", "world_id": world_id(fam, p), "params": p,
                     "coords": coords_of(fam, p, "v1"), "coords_v2": coords_of(fam, p, "v2"), "coords_v3": coords_of(fam, p, "v3")})
    L = Law(atoms=[(("var", "C"), 0.3, 1.0)], complexity=1)
    L.alpha, L.scales = 20.0, [1.0]
    ch = Chamber([fam], campaign="t")
    attack(L, ch, {"regs": pool}, np.random.default_rng(1), per_family=16)
    n1 = len(ch.log)
    first = [r["world_id"] for r in ch.log if r["purpose"].startswith("attack:") and r["purpose"] != "attack:coordpres"]
    attack(L, ch, {"regs": pool}, np.random.default_rng(2), per_family=16)
    second = [r["world_id"] for r in ch.log[n1:] if r["purpose"].startswith("attack:") and r["purpose"] != "attack:coordpres"]
    assert first and second
    assert not (set(first) & set(second))
