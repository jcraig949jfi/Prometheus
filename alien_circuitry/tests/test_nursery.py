"""Nursery ledger schema and provenance tests."""
import json, os
from alien_circuitry.nursery.build_nursery_md import load, REQUIRED, STATUS_VOCAB

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ledger_loads_and_has_required_fields():
    rows = load(); assert len(rows) >= 10
    for r in rows:
        for k in REQUIRED: assert k in r, (r["id"], k)


def test_ac01_entry_cites_committed_artifacts():
    rows = {r["id"]: r for r in load()}; e = rows["NUR-001"]
    for p in e["origin"]["results"] + [e["origin"]["receipt"]]:
        assert os.path.exists(os.path.join(HERE, "..", p)), p


def test_status_vocab_is_closed():
    for r in load():
        for tok in str(r["status"]).replace(",", " ").replace("-in-AC01", "").replace("-elsewhere", "").split():
            assert tok in STATUS_VOCAB


def test_cp_vs_c6_negative_is_on_disk():
    p = os.path.join(HERE, "results", "ac01d", "nursery", "cp_vs_c6_failure_geometry.json"); assert os.path.exists(p)
    r = json.load(open(p)); assert r["error_corr"] > 0.5 and abs(r["R2_of_stacked_ridge"] - max(r["R2_cp"], r["R2_c6"])) < 0.05
