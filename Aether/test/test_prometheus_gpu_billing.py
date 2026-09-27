"""Provider billing reconciliation and the rate source (RUNPOD_ENGINEERING_04).

The regression this file exists for: through Iteration 4 the launcher ran
on SECURE cloud but priced runs from a table that mixed in COMMUNITY
prices. Provider billing showed the 4090 billed at 2.18x its quote and the
A4000 at 1.49x, while billed SECONDS matched the controller to <= 7%.
"""

import json
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_RUNPOD = os.path.join(os.path.dirname(_HERE), "runpod")
if _RUNPOD not in sys.path:
    sys.path.insert(0, _RUNPOD)

from prometheus_gpu import billing, cost  # noqa: E402

# Observed 2026-09-27 from the provider: (securePrice, communityPrice).
OBSERVED = {
    "NVIDIA RTX A4000": (0.25, 0.17),
    "NVIDIA GeForce RTX 4090": (0.74, 0.34),
    "NVIDIA RTX A5000": (0.27, 0.16),
    "NVIDIA L4": (0.49, 0.44),
    "NVIDIA A40": (0.49, 0.35),
}


@pytest.fixture(autouse=True)
def _clear_live():
    saved = dict(cost._LIVE)
    cost._LIVE.clear()
    yield
    cost._LIVE.clear()
    cost._LIVE.update(saved)


def test_fallback_table_is_secure_not_community():
    for gpu, (secure, community) in OBSERVED.items():
        assert cost.hourly_for(gpu) == pytest.approx(secure), gpu
        if community != secure:
            assert cost.hourly_for(gpu) != pytest.approx(community), gpu


def test_live_quote_overrides_the_table_and_is_attributed():
    n = cost.refresh_quotes(fetch=lambda: [
        {"id": "NVIDIA RTX A5000", "securePrice": 0.31},
        {"id": "NVIDIA L4", "securePrice": None}])
    assert n == 1
    assert cost.hourly_for("NVIDIA RTX A5000") == pytest.approx(0.31)
    assert cost.quote_source("NVIDIA RTX A5000").startswith("provider securePrice")
    assert cost.hourly_for("NVIDIA L4") == pytest.approx(0.49)
    assert "static SECURE table" in cost.quote_source("NVIDIA L4")
    assert "guess" in cost.quote_source("NVIDIA Imaginary 9000")


def test_refresh_never_raises_and_falls_back():
    def boom():
        raise OSError("no network")
    assert cost.refresh_quotes(fetch=boom) == 0
    assert cost.hourly_for("NVIDIA A40") == pytest.approx(0.49)


def test_actual_cost_names_its_quote_source():
    out = cost.actual(3600.0, 0.27, quote_source="provider securePrice read X")
    assert out["usd_estimated"] == pytest.approx(0.27)
    assert out["billing_reconciled"] is False
    assert out["quote_source"] == "provider securePrice read X"


def _receipt(tmp_path, name, pod_id, rate, elapsed, gpu):
    rec = {"run_id": name, "gpu_used": gpu,
           "pods": [{"id": pod_id}],
           "cost": {"hourly_usd": rate, "elapsed_s": elapsed,
                    "usd_estimated": round(elapsed / 3600.0 * rate, 5)}}
    (tmp_path / (name + ".json")).write_text(json.dumps(rec), encoding="utf-8")


def test_reconcile_joins_billing_to_receipts(tmp_path):
    # The shape of the real finding: a 4090 run quoted at the community
    # price and billed at the secure one, split across two day buckets.
    _receipt(tmp_path, "r1", "podA", 0.34, 311.7, "NVIDIA GeForce RTX 4090")
    _receipt(tmp_path, "r2", "podB", 0.27, 100.0, "NVIDIA RTX A5000")
    _receipt(tmp_path, "r3", "podC", 0.27, 50.0, "NVIDIA RTX A5000")
    rows = [
        {"podId": "podA", "amount": 0.04, "timeBilledMs": 200000, "diskSpaceBilledGB": 10},
        {"podId": "podA", "amount": 0.024006, "timeBilledMs": 110800, "diskSpaceBilledGB": 10},
        {"podId": "podB", "amount": 0.0075, "timeBilledMs": 100000, "diskSpaceBilledGB": 20},
        {"podId": "legacy", "amount": 2.0, "timeBilledMs": 14000000, "diskSpaceBilledGB": 900},
    ]
    out = billing.reconcile(str(tmp_path), rows)
    by = {r["pod_id"]: r for r in out["rows"]}
    a = by["podA"]
    assert a["status"] == "BILLED"
    assert a["billed_usd"] == pytest.approx(0.064006)
    assert a["billed_s"] == pytest.approx(310.8)
    assert a["billed_over_estimate"] == pytest.approx(0.064006 / 0.02944, rel=1e-3)
    assert a["billed_usd_per_billed_h"] == pytest.approx(0.7414, rel=1e-3)
    assert by["podC"]["status"] == "NOT_YET_BILLED_OR_NOT_VISIBLE"
    assert "billed_usd" not in by["podC"]
    assert [u["pod_id"] for u in out["billed_pods_without_receipt"]] == ["legacy"]
    assert out["totals"]["billed_usd_unmatched"] == pytest.approx(2.0)


def test_billing_rows_never_become_free_when_missing(tmp_path):
    _receipt(tmp_path, "r1", "podZ", 0.49, 60.0, "NVIDIA A40")
    out = billing.reconcile(str(tmp_path), [])
    assert out["rows"][0]["status"].startswith("NOT_YET_BILLED")
    assert out["totals"]["billed_usd_matched"] == 0.0
