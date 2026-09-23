"""Holdout leakage guards: engineered, not promised."""
import ast
import json
from pathlib import Path

import pytest

from prometheus.cosmos import broker
from prometheus.cosmos.hashing import file_sha
from prometheus.cosmos.store import Store

PKG = Path(__file__).resolve().parents[1]
COMMITMENT = "48e709653f2bbda12c6b1d1c499d801339ec7897e9bf3081764c50691cfa8265"
MINING_SIDE = ["miner.py", "pipeline.py", "sampler.py", "adversary.py", "phenomenon.py", "world.py",
               "independence.py", "store.py", "contract.py", "substrates/regs.py", "substrates/ring.py",
               "substrates/ca.py", "substrates/__init__.py"]


def _imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module)
            out |= {n.module + "." + a.name for a in n.names}
    return out


@pytest.mark.parametrize("rel", MINING_SIDE)
def test_mining_side_never_imports_the_holdout(rel):
    p = PKG / rel
    if not p.exists():
        pytest.skip("not built yet")
    bad = [m for m in _imports(p) if "holdout" in m or "broker" in m]
    assert not bad, bad
    assert "sealed_spec" not in p.read_text(encoding="utf-8")


def test_holdout_family_refuses_import_outside_broker():
    with pytest.raises(ImportError):
        import prometheus.cosmos.holdout.well  # noqa: F401


def test_sealed_spec_matches_commitment_and_family_source():
    spec = broker.load_spec(COMMITMENT)
    assert len(spec["worlds"]) == 240
    assert spec["family_src_sha"] == file_sha(PKG / "holdout" / "well.py")


def test_broker_refuses_a_wrong_commitment():
    with pytest.raises(broker.SealBroken):
        broker.load_spec("0" * 64)


def test_broker_refuses_an_unfrozen_law(tmp_path):
    st = Store(tmp_path)
    lid = st.propose_law({"law": {"law": "C <= 0.3", "atoms": [[["var", "C"], 0.3, 1.0]], "complexity": 1,
                                  "alpha": 10.0, "scales": [1.0]}})
    with pytest.raises(broker.SealBroken):
        broker.adjudicate(st, lid, COMMITMENT)


def test_seed_streams_are_disjoint_between_visible_and_holdout():
    spec = json.loads((PKG / "holdout" / "sealed_spec.json").read_text(encoding="utf-8"))
    assert len(spec["nonce"]) == 32
    from prometheus.cosmos.hashing import derive_seed
    a = {derive_seed("c0", "regs", i, 0) for i in range(200)}
    b = {derive_seed("c0-holdout-" + spec["nonce"], "well", i, 0) for i in range(200)}
    assert not (a & b)


def test_receipt_chain_detects_tampering(tmp_path):
    from prometheus.cosmos.hashing import ReceiptChain
    rc = ReceiptChain(tmp_path / "r.jsonl")
    for i in range(5):
        rc.append("x", {"i": i})
    assert rc.verify() is None
    lines = (tmp_path / "r.jsonl").read_text().splitlines()
    lines[2] = lines[2].replace('"i":2', '"i":7')
    (tmp_path / "r.jsonl").write_text("\n".join(lines) + "\n")
    assert rc.verify() == 2


def test_sampler_pool_rows_carry_no_outcome_fields():
    """Strategies see unqueried worlds through pool rows; those must be spec-side only."""
    import inspect
    from prometheus.cosmos import campaign0
    src = inspect.getsource(campaign0.run)
    assert 'POOL_FIELDS = ("family", "lineage", "world_id", "params", "coords", "coords_v2", "coords_v3")' in src
