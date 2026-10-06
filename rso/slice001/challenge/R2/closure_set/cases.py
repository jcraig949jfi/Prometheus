"""C-004-T048 R2 closure re-check: fresh cases against the frozen second-repair code (attack tooling, never
production).

Written by Pallas[m2-1500b878] before any outcome was observed and before any test body under
rso/slice001/tests/ was opened. Every case is an edit of the committed S4 G0 bundle (rso/slice001/s4/G0, real
executions, cumulative inventory of 232 rows), built with the fixtures' own helpers (fixtures/evidence_cases.py)
so the shapes are the ones the consumer reads. Expected verdicts live in expected.json and CLOSURE_SET.md, not
here. None of these cases replays an S4 case (those are T046's regressions).
"""
import hashlib

from rso.slice001 import evidence as EV
from rso.slice001.fixtures import evidence_cases as F

EARLIER = "2026-10-03T23:00:00Z"      # S2 manifest row: before F.REGISTERED_AT (2026-10-04T00:00:00Z)
LATER_ROW = "2026-10-04T00:30:00Z"    # superset manifest row: after the S4 rows, before F.FIRST_CHECK (01:00)
VICTIM = "rcpt:REG:PRESERVE:STANDARD"


def _terminal(rows):
    return rows + [{"kind": "TERMINAL", "row_count": len(rows)}]


def sound_superset_manifest(base, s2_manifest):
    """R2.SOUND.SUPERSET_MANIFEST (C1 surface). The keeper holds THREE verified manifests: the S2 G0 manifest
    (registered earlier; same 25 node ids, other artifacts), the S4 G0 manifest (this bundle's), and a 26-node
    manifest registered later whose nodes are the S4 nodes with their S4 artifacts PLUS one node this bundle does
    not present (a superset production). The consumer is handed the S4 bundle and all three blobs. B5.2/B5.3:
    custody qualifies against the row whose blob is THIS bundle's manifest. Expected: custody QUALIFIED citing
    the S4 manifest row, and every decision byte-identical to the single-manifest keeper control."""
    d = base.dicts()
    bd = F.make_bundle(d, base=base)
    extra = F.make_receipt_dict("LAGD", "OBSERVER", "run-r2-extra", observer="BOOKKEEP")
    sup = dict(d)
    sup[extra["node_id"]] = extra
    superset = F.manifest_of(sup)
    rows = ([F.row("EVIDENCE_MANIFEST", hashlib.sha256(s2_manifest).hexdigest(), at=EARLIER,
                   path="fixtures/G0_S2/MANIFEST.json")]
            + F.keeper_rows(d, bd, base=base)
            + [F.row("EVIDENCE_MANIFEST", hashlib.sha256(superset).hexdigest(), at=LATER_ROW,
                     path="fixtures/G0_SUPERSET/MANIFEST.json")])
    store = EV.FixtureStore(rows)
    blob_map = {"fixtures/G0/MANIFEST.json": F.manifest_of(d), "fixtures/G0_S2/MANIFEST.json": s2_manifest,
                "fixtures/G0_SUPERSET/MANIFEST.json": superset}
    anchors = EV.anchors_from_keeper(store, blob_map)
    c = F._case("R2_SUPERSET_MANIFEST", bd, anchors, [], base)
    c.store = store
    return c


def _cite_new_row(base, run_id, start_utc, end_utc, status="COMPLETED", cpu_us=1500000, artifact_bytes=0):
    """REG's PRESERVE receipt cites a NEW inventory row of its own node (same full node id); the row is
    appended to the cumulative inventory; the receipt's own S4 row stays, uncited. Anchors re-made from the
    edited receipts (the producer that cites this run also signs the manifest), as S4.PROBE.STALE_RUN did."""
    d = base.dicts()
    d[VICTIM]["execution"]["run_id"] = run_id
    inv = base.inventory(d)
    rows = inv[:-1]
    rows.append({"artifact_bytes": artifact_bytes, "cpu_us": cpu_us, "end_utc": end_utc, "kind": "RUN",
                 "launch_kind": "RECEIPT", "node_id": VICTIM, "run_id": run_id, "start_utc": start_utc,
                 "status": status, "supplied_by": "rso.slice001.s2_bundle.build_bundle"})
    return F._case("R2_" + run_id.split("/")[-1].upper().replace("-", "_"),
                   F.make_bundle(d, inventory=_terminal(rows), base=base), F.retained(d), base.stage_rows(), base)


def broken_later_window_run(base):
    """R2.BROKEN.LATER_WINDOW_RUN (B3.3 surface; v1.0.5 Y1). The S4 PRESERVE receipt of REG (created
    2026-10-06T00:00:53Z, its own run 00:00:56-00:00:57Z) cites a COMPLETED run of the SAME full node id from a
    LATER launch window, a day after the S4 launch ended; the cumulative inventory holds both rows. Mirror of
    S4.PROBE.STALE_RUN: an earlier window's run is now refused; a later window's run did not launch or produce
    this receipt either. Expected: G-INV FAIL RECEIPT_WITHOUT_RUN:rcpt:REG:PRESERVE:STANDARD; CL-RET(REG)
    NOT_ELIGIBLE, UNMET; the other claims identical to the baseline."""
    return _cite_new_row(base, "g0-r2later-00000000-1/later-window", "2026-10-07T12:00:00Z", "2026-10-07T12:00:01Z")


def probe_overlap_run(base):
    """R2.PROBE.OVERLAP_RUN (unscored; the author-declared escape FD-T046-1). A second COMPLETED run of the same
    node whose window OVERLAPS the S4 launch (00:00:55-00:01:10Z) is cited instead of the receipt's own row."""
    return _cite_new_row(base, "g0-r2overlap-00000000-1/overlap", "2026-10-06T00:00:55Z", "2026-10-06T00:01:10Z")


def probe_failed_row_cited(base):
    """R2.PROBE.FAILED_ROW_CITED (unscored). The receipt cites a row of its own node, inside the S4 window, whose
    status is FAILED (a run that produced no receipt); its own COMPLETED row stays, uncited."""
    return _cite_new_row(base, "g0-r2failed-00000000-1/failed", "2026-10-06T00:00:56Z", "2026-10-06T00:00:58Z",
                         status="FAILED", artifact_bytes=None)
