"""campaign.classify on a row with NO twin assay (kind "transfer", campaign.py:268-278) must not
record REACH_BEYOND_HOP = False ("measured, absent"); it was never measured. FAILS on current code
(classify defaults tw.get("beyond_hop", 0) -> False; all 99 C1 transfer rows carry False), PASSES
with patches/classify_transfer_reach_none.diff. Neutrality: every evolve row's recomputed labels
equal the stored C1 labels, and every other transfer label is unchanged."""
import json

from prometheus.ananke import campaign as C


def _cfg(repo):
    fz = json.load(open(repo / "roles/Ananke/pte/FREEZE_PTE_C1.json"))["config"]
    return C.CampaignConfig(**{k: (tuple(v) if k in ("families", "e_sizes") else v) for k, v in fz.items()})


def test_transfer_row_reach_is_not_measured(c1_rows, repo):
    cfg = _cfg(repo)
    tr = [r for r in c1_rows if r["kind"] == "transfer"]
    assert len(tr) == 99 and all("twin" not in r["result"] for r in tr)
    assert all(C.classify(r, cfg)["REACH_BEYOND_HOP"] is None for r in tr)


def test_evolve_labels_unchanged(c1_rows, repo):
    cfg = _cfg(repo)
    ev = [r for r in c1_rows if r["kind"] == "evolve"]
    assert len(ev) == 678
    assert all(C.classify(r, cfg) == r["labels"] for r in ev)


def test_transfer_other_labels_unchanged(c1_rows, repo):
    cfg = _cfg(repo)
    for r in (r for r in c1_rows if r["kind"] == "transfer"):
        a, b = C.classify(r, cfg), dict(r["labels"])
        a.pop("REACH_BEYOND_HOP")
        b.pop("REACH_BEYOND_HOP")
        assert a == b
