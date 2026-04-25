"""Tests for prometheus_math.databases.cremona — Cremona ecdata local mirror.

Most tests are gated behind ``PROMETHEUS_DOWNLOAD_CREMONA=1``: the
underlying mirror is ~88 MB at the default conductor cap, so we don't
auto-download in CI. Tests that don't need the live mirror (parsing,
fallback behavior, label normalization) run unconditionally.

Authority cross-checks (run with the mirror present):

  * 11.a1 (LMFDB)  — ainvs [0,-1,1,-10,-20], conductor 11, rank 0
                     (note: in Cremona's labeling this curve is 11a1)
  * 37.a1          — ainvs [0,0,1,-1,0], conductor 37, rank 1,
                     regulator ~ 0.0511114082399688

References:
  * John Cremona's ecdata, github.com/JohnCremona/ecdata
  * docs/file-format.txt in that repo
  * LMFDB ec_curvedata table (cross-check authority)
"""
from __future__ import annotations

import importlib
import os

import pytest

from prometheus_math.databases import cremona, _local


# ---------------------------------------------------------------------------
# Gating
# ---------------------------------------------------------------------------

DOWNLOAD_FLAG = "PROMETHEUS_DOWNLOAD_CREMONA"


def _allow_download() -> bool:
    return os.environ.get(DOWNLOAD_FLAG, "").strip() in {"1", "true", "TRUE", "yes"}


def _mirror_present() -> bool:
    return cremona.has_local_mirror()


# If downloads are allowed, materialize the minimal mirror at COLLECTION
# time so the eager-evaluated skipif decorators below see the mirror.
# We only fetch the smallest block (00000-09999) which covers anchors
# 11.a1 and 37.a1 — about 8 MB across the three families. If the mirror
# is already there but the sidecar isn't, this will also stamp the
# sidecar so subsequent no-op tests don't write a weak version.
if _allow_download():
    try:
        cremona.update_mirror(conductor_max=99,
                              families=("allcurves", "allbsd", "alllabels"))
    except Exception:
        # If the bootstrap download fails, the @needs_mirror tests will
        # skip cleanly; the parser tests still run.
        pass


needs_mirror = pytest.mark.skipif(
    not _mirror_present(),
    reason="Cremona local mirror not present "
           f"(set {DOWNLOAD_FLAG}=1 and run update_mirror to enable)",
)

needs_download = pytest.mark.skipif(
    not _allow_download(),
    reason=f"Set {DOWNLOAD_FLAG}=1 to allow ~88 MB download for tests",
)


# ---------------------------------------------------------------------------
# Parser unit tests (no network, no mirror)
# ---------------------------------------------------------------------------

class TestParserBasics:
    """The text -> dict pipeline must round-trip the canonical anchors
    correctly, otherwise everything else is a sham."""

    def test_parse_ainvs_canonical(self):
        # Authority: trefoil-of-EC, 11a1 ainvs as published in
        # Cremona's allcurves.00000-09999.
        out = cremona._parse_ainvs("[0,-1,1,-10,-20]")
        assert out == [0, -1, 1, -10, -20]

    def test_parse_ainvs_handles_whitespace(self):
        assert cremona._parse_ainvs("[0, 0, 1, -1, 0]") == [0, 0, 1, -1, 0]

    def test_parse_ainvs_rejects_garbage(self):
        assert cremona._parse_ainvs("not a vector") is None
        assert cremona._parse_ainvs("[1,2,3,a,5]") is None
        assert cremona._parse_ainvs("") is None

    def test_parse_allcurves_line_for_11a1(self):
        """Authority: '11 a 1 [0,-1,1,-10,-20] 0 5' is the canonical
        Cremona 11a1 line. References: ecdata/allcurves/allcurves.00000-09999
        first line; Cremona Algorithms for Modular Elliptic Curves (1997)
        Appendix A.
        """
        rec = cremona._parse_allcurves_line("11 a 1 [0,-1,1,-10,-20] 0 5")
        assert rec["conductor"] == 11
        assert rec["isogeny_class"] == "a"
        assert rec["curve_index"] == 1
        assert rec["ainvs"] == [0, -1, 1, -10, -20]
        assert rec["rank"] == 0
        assert rec["torsion"] == 5
        assert rec["cremona_label"] == "11a1"

    def test_parse_allbsd_line_for_37a1(self):
        """Authority: regulator of 37a1 is 0.0511114082399688 in
        ecdata/allbsd/allbsd.00000-09999, matching LMFDB's regulator
        for 37.a1.
        """
        line = ("37 a 1 [0,0,1,-1,0] 1 1 1 5.98691729246392 "
                "0.305999773834052 0.0511114082399688 1.00000000000000")
        rec = cremona._parse_allbsd_line(line)
        assert rec["conductor"] == 37
        assert rec["ainvs"] == [0, 0, 1, -1, 0]
        assert rec["rank"] == 1
        assert rec["torsion"] == 1
        assert rec["tamagawa"] == 1
        assert abs(rec["regulator"] - 0.0511114082399688) < 1e-12
        assert abs(rec["real_period"] - 5.98691729246392) < 1e-12
        assert rec["sha_an"] == 1  # int

    def test_parse_allbsd_returns_none_on_short_line(self):
        assert cremona._parse_allbsd_line("11 a 1 [0,-1,1,-10,-20]") is None
        assert cremona._parse_allbsd_line("") is None
        assert cremona._parse_allbsd_line("garbage line here") is None

    def test_parse_alllabels_line_basic(self):
        # Authority: from alllabels.00000-09999 — Cremona 11a1 maps to
        # LMFDB 11.a2 (the labels disagree on the FIRST class!).
        pair = cremona._parse_alllabels_line("11 a 1 11 a 2")
        assert pair == ("11a1", "11.a2")

    def test_parse_alllabels_rejects_mismatched_conductor(self):
        # Defensive: same line shape but conductor disagrees -> None
        assert cremona._parse_alllabels_line("11 a 1 12 a 2") is None


# ---------------------------------------------------------------------------
# Label normalization (composition with internal helper)
# ---------------------------------------------------------------------------

class TestLabelNormalization:
    """Composition test: every accepted label form should round-trip
    consistently into one of the two index keys."""

    def test_lmfdb_dot_form(self):
        cl, ll = cremona._normalize_label("37.a1")
        assert cl == "37a1"
        assert ll == "37.a1"

    def test_cremona_compact_form(self):
        cl, ll = cremona._normalize_label("11a1")
        assert cl == "11a1"
        assert ll is None  # caller can't commit; we have no map yet

    def test_id_with_spaces(self):
        cl, ll = cremona._normalize_label("389 a 1")
        assert cl == "389a1"

    def test_normalize_garbage(self):
        cl, ll = cremona._normalize_label("not a label")
        assert cl is None and ll is None
        cl, ll = cremona._normalize_label("")
        assert cl is None and ll is None
        cl, ll = cremona._normalize_label(None)
        assert cl is None and ll is None


# ---------------------------------------------------------------------------
# Range / partitioning
# ---------------------------------------------------------------------------

class TestRangePartitioning:
    """The conductor partitioning must match upstream's directory layout."""

    def test_range_tag_zero_padded_below_10k(self):
        # Authority: upstream filename is 'allcurves.00000-09999'
        assert cremona._range_tag(0) == "00000-09999"

    def test_range_tag_unpadded_above_10k(self):
        # Authority: upstream 'allcurves.10000-19999', '100000-109999'
        assert cremona._range_tag(10_000) == "10000-19999"
        assert cremona._range_tag(100_000) == "100000-109999"

    def test_range_partition_covers_both_sides_of_10k_boundary(self):
        # Property: the partition covers every conductor up to the cap
        # exactly once, and the boundary at 10K is handled (the
        # zero-padding gate).
        ranges = cremona._ranges_up_to(20_000)
        los = [lo for lo, _ in ranges]
        assert los == [0, 10_000, 20_000]

    def test_range_partition_is_sorted_and_dense(self):
        # Property: ranges are strictly increasing and contiguous.
        ranges = cremona._ranges_up_to(50_000)
        los = [lo for lo, _ in ranges]
        assert los == sorted(los)
        for a, b in zip(los, los[1:]):
            assert b - a == 10_000


# ---------------------------------------------------------------------------
# Mirror / probe (safe to run without download)
# ---------------------------------------------------------------------------

class TestMirrorAndProbe:
    """probe() and mirror_info() must always return a usable shape."""

    def test_probe_returns_bool(self):
        # Edge: probe must never raise even if the network is dark.
        result = cremona.probe(timeout=2.0)
        assert isinstance(result, bool)

    def test_mirror_info_shape(self):
        # Property: mirror_info() returns a dict with the documented keys
        # whether or not a mirror exists.
        info = cremona.mirror_info()
        for k in ("present", "n_curves", "size_bytes", "files",
                  "conductor_blocks", "last_refresh_iso", "path"):
            assert k in info, f"mirror_info() missing {k!r}"
        assert isinstance(info["present"], bool)
        assert isinstance(info["n_curves"], int)
        assert isinstance(info["files"], dict)

    def test_mirror_info_path_is_under_data_dir(self):
        # Composition: mirror_info().path matches _local.dataset_path("cremona")
        info = cremona.mirror_info()
        expected = str(_local.dataset_path("cremona"))
        assert info["path"] == expected


# ---------------------------------------------------------------------------
# Fallback behavior (no mirror or no match -> LMFDB fallback)
# ---------------------------------------------------------------------------

class TestFallback:
    """When the mirror is empty or doesn't have a row, we should
    cleanly fall back to LMFDB rather than blow up."""

    def test_lookup_with_fallback_disabled_returns_empty(self):
        # If we have no mirror AND we disable the fallback, we should get
        # a clean empty list rather than a NameError or stale LMFDB call.
        if cremona.has_local_mirror():
            pytest.skip("local mirror is present; this test only exercises "
                        "the no-mirror path")
        rows = cremona.elliptic_curves(label="11.a1",
                                       fall_back_to_lmfdb=False)
        assert rows == []

    def test_bogus_ainvs_returns_none(self):
        # Edge: malformed input, doesn't crash, returns None.
        assert cremona.lookup_by_ainvs(None) is None
        assert cremona.lookup_by_ainvs([]) is None
        assert cremona.lookup_by_ainvs([1, 2, 3]) is None
        # Note: a 5-tuple of weird ints may legitimately not be in the
        # mirror — that should also return None.
        assert cremona.lookup_by_ainvs([0, 0, 0, 0, 999_999_999]) is None


# ---------------------------------------------------------------------------
# Authority + composition tests — REQUIRE the mirror.
# ---------------------------------------------------------------------------

@needs_mirror
class TestAuthorityWithMirror:
    """These tests require the local mirror to actually be present.

    They cross-check our parsed values against the canonical anchors in
    Cremona's ecdata. Authority sources cited inline.
    """

    def test_lookup_11a1_by_ainvs(self):
        """Authority: ecdata/allcurves/allcurves.00000-09999 line 1:
        '11 a 1 [0,-1,1,-10,-20] 0 5'.

        This is also LMFDB curve 11.a2 (the Cremona/LMFDB labels disagree
        for the 11a class). We check against Cremona's ainvs.
        """
        row = cremona.lookup_by_ainvs([0, -1, 1, -10, -20])
        assert row is not None, "11a1 missing from local mirror"
        assert row["conductor"] == 11
        assert row["rank"] == 0
        assert row["cremona_label"] == "11a1"
        # torsion = 5 (Z/5Z), the canonical 11a1 torsion subgroup
        assert row["torsion"] == 5

    def test_lookup_37a1_regulator(self):
        """Authority: ecdata/allbsd/allbsd.00000-09999, line for 37 a 1:
        REG = 0.0511114082399688 (Cremona-published). LMFDB 37.a1 has
        the same ainvs and the same regulator to 1e-15 — see
        ec_curvedata.regulator at lmfdb_label='37.a1'.
        """
        row = cremona.lookup_by_ainvs([0, 0, 1, -1, 0])
        assert row is not None, "37a1 missing from local mirror"
        assert row["conductor"] == 37
        assert row["rank"] == 1
        # regulator should be present iff allbsd is mirrored. The default
        # update_mirror() pulls allbsd, so this is the normal case.
        assert "regulator" in row, ("regulator missing — was allbsd "
                                    "downloaded?")
        assert abs(row["regulator"] - 0.0511114082399688) < 1e-9

    def test_elliptic_curves_label_lookup_lmfdb_form(self):
        """Composition: elliptic_curves('37.a1') routes through label
        normalization, finds the cremona row with ainvs [0,0,1,-1,0],
        and returns it."""
        rows = cremona.elliptic_curves(label="37.a1")
        assert len(rows) == 1
        assert rows[0]["ainvs"] == [0, 0, 1, -1, 0]
        assert rows[0]["conductor"] == 37
        assert rows[0]["rank"] == 1


# ---------------------------------------------------------------------------
# Property test: every loaded row's conductor lies in its file's range.
# ---------------------------------------------------------------------------

@needs_mirror
class TestProperties:
    """Invariants that must hold across every row we loaded."""

    def test_every_row_has_required_keys(self):
        info = cremona.mirror_info()
        cremona._ensure_loaded(info.get("conductor_blocks", [0])[-1] + 9999)
        rows = cremona._cache["all_rows"] or []
        assert len(rows) > 0, "no rows loaded — mirror is empty?"
        for r in rows[:200]:  # sample for speed
            for k in ("conductor", "ainvs", "rank", "cremona_label"):
                assert k in r, f"row missing {k!r}: {r}"
            assert isinstance(r["ainvs"], list)
            assert len(r["ainvs"]) == 5
            assert all(isinstance(x, int) for x in r["ainvs"])
            assert isinstance(r["conductor"], int)
            assert r["conductor"] >= 11  # smallest conductor in ecdata

    def test_row_conductor_matches_block_partition(self):
        """Property: every entry's conductor falls inside the 10K block
        whose file produced it."""
        info = cremona.mirror_info()
        rows = cremona._cache["all_rows"] or []
        for r in rows:
            block_lo = (r["conductor"] // 10_000) * 10_000
            assert block_lo in info["conductor_blocks"], (
                f"row with conductor {r['conductor']} loaded but "
                f"block {block_lo} not in {info['conductor_blocks']}"
            )

    def test_no_duplicate_cremona_labels(self):
        rows = cremona._cache["all_rows"] or []
        labels = [r["cremona_label"] for r in rows]
        assert len(labels) == len(set(labels)), "duplicate Cremona label"

    def test_ranks_are_non_negative(self):
        # Property: rank >= 0 for every elliptic curve over Q.
        rows = cremona._cache["all_rows"] or []
        bad = [r for r in rows if r.get("rank") is not None and r["rank"] < 0]
        assert bad == [], f"negative rank in: {bad[:3]}"


# ---------------------------------------------------------------------------
# Composition: cremona <-> lmfdb must agree on rows present in both.
# ---------------------------------------------------------------------------

def _lmfdb_online() -> bool:
    try:
        from prometheus_math.databases import lmfdb as _l
        c = _l.connect(timeout=5)
        c.close()
        return True
    except Exception:
        return False


@needs_mirror
@pytest.mark.skipif(not _lmfdb_online(),
                    reason="LMFDB Postgres mirror unreachable")
class TestComposition:
    """When BOTH backends are available, they must agree on the rows
    they both have. This is the hardest test to write but the most
    valuable: it catches silent parsing bugs."""

    def test_cremona_and_lmfdb_agree_on_37a1(self):
        from prometheus_math.databases import lmfdb as _l
        cre_row = cremona.elliptic_curves(label="37.a1")
        lm_row = _l.elliptic_curves(label="37.a1")
        assert len(cre_row) == 1
        assert len(lm_row) == 1
        assert cre_row[0]["ainvs"] == lm_row[0]["ainvs"]
        assert cre_row[0]["conductor"] == lm_row[0]["conductor"]
        assert cre_row[0]["rank"] == lm_row[0]["rank"]

    def test_cremona_regulator_matches_lmfdb(self):
        """BSD-spine composition: regulator is computed independently by
        Cremona's mwrank and by LMFDB's pipeline (which itself uses
        Cremona's data, so this is mostly a parsing check). Tolerance
        1e-6 to absorb float -> Decimal -> float round trips."""
        from prometheus_math.databases import lmfdb as _l
        cre = cremona.lookup_by_ainvs([0, 0, 1, -1, 0])
        lm_rows = _l.elliptic_curves(label="37.a1")
        assert cre is not None and len(lm_rows) == 1
        assert "regulator" in cre, "allbsd missing — re-run update_mirror"
        assert abs(cre["regulator"] - lm_rows[0]["regulator"]) < 1e-6


# ---------------------------------------------------------------------------
# Edge case: update_mirror with an empty range (sanity, no download).
# ---------------------------------------------------------------------------

class TestUpdateMirrorEdges:
    """update_mirror() must behave well at trivial extremes."""

    def test_empty_families_list_no_op(self):
        # Edge: passing families=() must not raise; just reports zero work.
        result = cremona.update_mirror(conductor_max=1,
                                       families=(),
                                       force=False)
        assert isinstance(result, dict)
        assert result["downloaded"] == []
        assert result["refreshed"] is False
        assert "no work" in result["message"] or "up to date" in result["message"]
