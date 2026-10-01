"""report.py (a) counts 22 wave-C HOLD "env variant" rows as TRANSFER_SUPPORT although HOLD never
reads d/delta (envs.py:155-167) and every one is on its source's physics: the generated summary.json
says 23 TRANSFER_SUPPORT while C1_REPORT F5 says they are not counted. The patch ADDS
condition_changed / TRANSFER_SUPPORT_EFFECTIVE (the legacy key is unchanged). (b) P1 is preregistered
on the PHYS track (PREREG s12) but score_predictions does not filter on track. Both FAIL on current
code (missing keys; P1 accepts an evo-track verdict) and PASS with
patches/report_transfer_effective_p1_track.diff. Neutrality: every legacy summary value recomputed
from the C1 rows equals the committed c1_report/summary.json."""
import gzip
import json
import shutil

from prometheus.ananke import campaign as C
from prometheus.ananke import report


def _build(tmp_path, repo):
    src = repo / "roles/Ananke/pte/c1_rows"
    with gzip.open(src / "cells.jsonl.gz", "rb") as f, open(tmp_path / "cells.jsonl", "wb") as g:
        shutil.copyfileobj(f, g)
    for n in ("boundaries_B.json", "boundaries_verdicts.json", "run_meta.json", "log.txt"):
        shutil.copy(src / n, tmp_path / n)
    return report.build(tmp_path, C.CampaignConfig())


def test_effective_transfer_support(tmp_path, repo):
    ct = _build(tmp_path, repo)["C_transfer"]
    assert all("TRANSFER_SUPPORT_EFFECTIVE" in t for t in ct)
    assert sum(t["TRANSFER_SUPPORT"] for t in ct) == 23
    eff = [t for t in ct if t["TRANSFER_SUPPORT_EFFECTIVE"]]
    assert len(eff) == 1 and eff[0]["from"] == "RELAY" and eff[0]["to"] == "RELAY"
    assert eff[0]["variant"]["d"] == 1 and eff[0]["variant"]["delta"] == 4


def test_legacy_summary_unchanged(tmp_path, repo):
    S = _build(tmp_path, repo)
    old = json.load(open(repo / "roles/Ananke/pte/c1_report/summary.json"))
    new = json.loads(json.dumps(S, default=str))
    for t in new["C_transfer"]:
        t.pop("TRANSFER_SUPPORT_EFFECTIVE", None)
        t.pop("condition_changed", None)
    for k in ("n_rows", "cells_per_wave", "A0", "A1", "anomalies", "boundary_counts", "C_transfer",
              "C_reevolve", "D", "E", "predictions"):
        assert new[k] == old[k], k


def test_p1_requires_phys_track():
    verd = [{"family": "RELAY", "metric": "plant", "dial": "delta", "label": "PHASE_BOUNDARY_SUPPORTED",
             "track": "evo", "between": [0, 1]}]
    S = {"A0": {}, "C_transfer": [], "anomalies": {}, "E": []}
    P = report.score_predictions(S, [], [], [], verd, C.CampaignConfig())
    assert P["P1"]["held"] is False, "P1 (phys track, PREREG s12) accepted an evo-track boundary"
