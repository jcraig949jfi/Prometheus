"""Tests for residue revocation primitive (Phase 1B ITER-39)."""
from __future__ import annotations

import pytest

from charon.agents.erebos._residue_revocation import (
    DEFAULT_REGISTRY,
    RevocationRecord,
    RevocationRegistry,
)


# ---------------------------------------------------------------------
# Basic revoke / is_revoked
# ---------------------------------------------------------------------

def test_fresh_registry_has_no_revocations():
    reg = RevocationRegistry()
    assert len(reg) == 0
    assert reg.is_revoked("any_row") is False


def test_revoke_appends_record():
    reg = RevocationRegistry()
    rec = reg.revoke(
        "row_g10_v1_001",
        superseded_by="row_g10_v2_005",
        reason="BOCPD posterior supersedes max/mean ratio",
    )
    assert isinstance(rec, RevocationRecord)
    assert rec.row_id == "row_g10_v1_001"
    assert rec.superseded_by == "row_g10_v2_005"
    assert reg.is_revoked("row_g10_v1_001") is True
    assert len(reg) == 1


def test_revoke_empty_row_id_raises():
    reg = RevocationRegistry()
    with pytest.raises(ValueError, match="row_id"):
        reg.revoke("")


def test_revoke_is_idempotent_on_identical_call():
    """Calling revoke twice with the same row_id + superseded_by +
    reason returns the same record (no second record appended)."""
    reg = RevocationRegistry()
    r1 = reg.revoke("row_X", superseded_by="row_Y", reason="r")
    r2 = reg.revoke("row_X", superseded_by="row_Y", reason="r")
    assert r1 is r2
    assert len(reg) == 1


def test_revoke_appends_second_record_on_different_supersession():
    """A second revoke with different superseded_by appends a
    second record (substrate-anomaly signal worth surfacing)."""
    reg = RevocationRegistry()
    reg.revoke("row_X", superseded_by="row_Y", reason="first")
    reg.revoke("row_X", superseded_by="row_Z", reason="second")
    assert len(reg) == 2
    recs = reg.revocations_for("row_X")
    assert len(recs) == 2
    assert recs[0].superseded_by == "row_Y"
    assert recs[1].superseded_by == "row_Z"


def test_revoke_appends_second_record_on_different_reason():
    reg = RevocationRegistry()
    reg.revoke("row_X", superseded_by="row_Y", reason="r1")
    reg.revoke("row_X", superseded_by="row_Y", reason="r2")
    assert len(reg) == 2


# ---------------------------------------------------------------------
# Revocations carry timestamps
# ---------------------------------------------------------------------

def test_revocation_record_has_iso_timestamp():
    reg = RevocationRegistry()
    rec = reg.revoke("row_A", superseded_by="row_B", reason="r")
    assert rec.ts  # non-empty
    # Should parse as ISO-8601
    from datetime import datetime
    parsed = datetime.fromisoformat(rec.ts)
    assert parsed.tzinfo is not None  # has timezone (UTC)


def test_revocation_record_is_frozen():
    reg = RevocationRegistry()
    rec = reg.revoke("row_A", superseded_by="row_B", reason="r")
    with pytest.raises((AttributeError, Exception)):
        rec.row_id = "tampered"  # type: ignore[misc]


# ---------------------------------------------------------------------
# revocations_for / superseded_by
# ---------------------------------------------------------------------

def test_revocations_for_returns_empty_for_unknown_row():
    reg = RevocationRegistry()
    assert reg.revocations_for("never_revoked") == []


def test_superseded_by_returns_most_recent():
    reg = RevocationRegistry()
    reg.revoke("row_X", superseded_by="row_old", reason="r")
    reg.revoke("row_X", superseded_by="row_new", reason="r2")
    assert reg.superseded_by("row_X") == "row_new"


def test_superseded_by_returns_none_for_unrevoked():
    reg = RevocationRegistry()
    assert reg.superseded_by("never_revoked") is None


def test_superseded_by_returns_none_when_revoke_had_no_successor():
    reg = RevocationRegistry()
    reg.revoke("row_X", superseded_by=None, reason="manual override")
    assert reg.superseded_by("row_X") is None
    assert reg.is_revoked("row_X") is True


# ---------------------------------------------------------------------
# filter_active (Layer 2 query helper)
# ---------------------------------------------------------------------

def test_filter_active_passes_through_unrevoked_rows():
    reg = RevocationRegistry()
    rows = [
        {"row_id": "a", "verdict": "PROMOTED"},
        {"row_id": "b", "verdict": "REJECTED"},
        {"row_id": "c", "verdict": "PROMOTED"},
    ]
    out = reg.filter_active(rows)
    assert out == rows


def test_filter_active_strips_revoked_rows():
    reg = RevocationRegistry()
    reg.revoke("b", superseded_by="d", reason="superseded")
    rows = [
        {"row_id": "a", "verdict": "PROMOTED"},
        {"row_id": "b", "verdict": "REJECTED"},
        {"row_id": "c", "verdict": "PROMOTED"},
    ]
    out = reg.filter_active(rows)
    assert len(out) == 2
    assert all(r["row_id"] != "b" for r in out)


def test_filter_active_uses_id_field_when_row_id_absent():
    reg = RevocationRegistry()
    reg.revoke("b", superseded_by="d", reason="r")
    rows = [
        {"id": "a"},
        {"id": "b"},
    ]
    out = reg.filter_active(rows)
    assert len(out) == 1
    assert out[0]["id"] == "a"


def test_filter_active_passes_rows_without_id():
    """Rows with no row_id/id should pass through (presumed
    un-revokable)."""
    reg = RevocationRegistry()
    reg.revoke("b", superseded_by="d", reason="r")
    rows = [
        {"no_id_here": True},
        {"row_id": "b"},
    ]
    out = reg.filter_active(rows)
    assert len(out) == 1
    assert out[0]["no_id_here"] is True


def test_filter_active_empty_iter_returns_empty():
    reg = RevocationRegistry()
    assert reg.filter_active([]) == []


# ---------------------------------------------------------------------
# Module-level convenience API
# ---------------------------------------------------------------------

def test_module_level_convenience_api(monkeypatch):
    """Module-level revoke / is_revoked / filter_active operate
    on DEFAULT_REGISTRY. Patch the registry to avoid cross-test
    pollution."""
    from charon.agents.erebos import _residue_revocation as mod
    fresh = RevocationRegistry()
    monkeypatch.setattr(mod, "DEFAULT_REGISTRY", fresh)
    mod.revoke("row_Z", superseded_by="row_Z2", reason="t")
    assert mod.is_revoked("row_Z") is True
    out = mod.filter_active([{"row_id": "row_Z"}, {"row_id": "row_other"}])
    assert len(out) == 1
    assert out[0]["row_id"] == "row_other"


# ---------------------------------------------------------------------
# Integration: simulated Phase 1A retrofit revoking v1
# ---------------------------------------------------------------------

def test_simulated_g10_v2_supersedes_g10_v1():
    """When G10 v2 BOCPD lands, it can revoke G10 v1's prior
    Lehmer-cliff row. Layer 2 then queries via filter_active and
    sees only the v2 row."""
    reg = RevocationRegistry()

    ledger_rows = [
        {
            "row_id": "row_g10_v1_lehmer_001",
            "loader_id": "g10_lehmer_threshold_sweep",
            "kill_pattern": "sharp_boundary_detected",
            "verdict": "REJECTED",
        },
        {
            "row_id": "row_g10_v2_lehmer_001",
            "loader_id": "g10_lehmer_bocpd_sweep",
            "kill_pattern": "sharp_boundary_detected_bocpd",
            "verdict": "REJECTED",
            "interior_spike_threshold": 1.30,
        },
    ]

    reg.revoke(
        "row_g10_v1_lehmer_001",
        superseded_by="row_g10_v2_lehmer_001",
        reason=(
            "BOCPD posterior detector (ITER-32) supersedes max/mean "
            "ratio: graded confidence + cold-start-excluded interior "
            "spike localization. Same Salem cliff at M=1.30; new "
            "row carries the boundary localization field."
        ),
    )

    active = reg.filter_active(ledger_rows)
    assert len(active) == 1
    assert active[0]["row_id"] == "row_g10_v2_lehmer_001"

    # Audit trail preserved -- the v1 row is still in the underlying
    # ledger_rows list; only the QUERY filters it out.
    assert any(r["row_id"] == "row_g10_v1_lehmer_001" for r in ledger_rows)

    # And the revocation chain is queryable for audit
    assert reg.superseded_by("row_g10_v1_lehmer_001") == "row_g10_v2_lehmer_001"
