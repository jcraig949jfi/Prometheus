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
