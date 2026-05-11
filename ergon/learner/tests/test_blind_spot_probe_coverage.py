"""Track 3 (ergon/PROMPT_2026-05-11_substrate_first.md) — assert the
5 confirmed blind-spots all have probe representation in the Tier-1 eval set.

The 5 must-have BS per James's prompt (BS-002 Lefschetz explicitly NOT
required at this stage; see manifest $note):

  - BS-001 Cohen 1963 CH-independence
  - BS-003 Helfgott 2013 ternary Goldbach
  - BS-004 Faltings 1983 Mordell
  - BS-005 McKay 1978 monstrous moonshine
  - BS-006 Margulis 1974 arithmeticity

Failing test = corpus gap. Designed to be a CI gate when CI lands.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Set

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = _REPO_ROOT / "ergon" / "learner" / "eval" / "v1_0_eval_set_manifest.json"
BLIND_SPOTS_JSON = (
    _REPO_ROOT / "aporia" / "calibration" / "learner_known_blind_spots_v1.json"
)

REQUIRED_BS_IDS: Set[str] = {
    "BS-001",  # Cohen 1963 CH-independence
    "BS-003",  # Helfgott 2013 ternary Goldbach
    "BS-004",  # Faltings 1983 Mordell
    "BS-005",  # McKay 1978 monstrous moonshine
    "BS-006",  # Margulis 1974 arithmeticity
}


@pytest.fixture(scope="module")
def manifest() -> dict:
    """Load the Tier-1 eval-set manifest."""
    assert MANIFEST_PATH.exists(), (
        f"manifest missing at {MANIFEST_PATH} — Track 3 cannot run without it"
    )
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def calibration_blind_spots() -> dict:
    """Load the canonical BS calibration JSON for cross-check."""
    assert BLIND_SPOTS_JSON.exists(), (
        f"calibration BS json missing at {BLIND_SPOTS_JSON}"
    )
    with open(BLIND_SPOTS_JSON, encoding="utf-8") as f:
        return json.load(f)


class TestBlindSpotProbeCoverage:
    """The Track 3 assertions: required BS appear in the manifest with the
    correct probe-coverage flag."""

    def test_manifest_has_bs_blind_spots_section(self, manifest: dict) -> None:
        assert "bs_blind_spots" in manifest, (
            "manifest missing required 'bs_blind_spots' section"
        )
        assert isinstance(manifest["bs_blind_spots"], list)
        assert len(manifest["bs_blind_spots"]) >= 5, (
            "fewer than 5 BS entries in manifest; expected at least 5 required"
        )

    def test_all_required_bs_present(self, manifest: dict) -> None:
        present_ids = {entry["id"] for entry in manifest["bs_blind_spots"]}
        missing = REQUIRED_BS_IDS - present_ids
        assert not missing, (
            f"required BS missing from manifest: {sorted(missing)}. "
            "Each must appear with must_have_probe=True per "
            "ergon/PROMPT_2026-05-11_substrate_first.md Track 3."
        )

    def test_required_bs_marked_must_have_probe(self, manifest: dict) -> None:
        by_id = {entry["id"]: entry for entry in manifest["bs_blind_spots"]}
        failures: List[str] = []
        for bs_id in REQUIRED_BS_IDS:
            entry = by_id.get(bs_id)
            if entry is None:
                failures.append(f"{bs_id}: missing entry")
                continue
            if not entry.get("must_have_probe"):
                failures.append(
                    f"{bs_id}: must_have_probe is False/missing in manifest"
                )
        assert not failures, "\n".join(failures)

    def test_each_required_bs_has_topic_string(self, manifest: dict) -> None:
        by_id = {entry["id"]: entry for entry in manifest["bs_blind_spots"]}
        for bs_id in REQUIRED_BS_IDS:
            entry = by_id[bs_id]
            assert entry.get("topic"), (
                f"{bs_id}: empty or missing 'topic' field — probes cannot be "
                "generated without a topic anchor"
            )

    def test_manifest_bs_topics_match_calibration_source(
        self, manifest: dict, calibration_blind_spots: dict,
    ) -> None:
        """Manifest's BS topics must reference the same blind-spot entries
        as `aporia/calibration/learner_known_blind_spots_v1.json`. Drift
        between the two sources is itself a corpus gap."""
        manifest_by_id = {entry["id"]: entry for entry in manifest["bs_blind_spots"]}
        calibration_by_id = {
            entry["id"]: entry for entry in calibration_blind_spots["entries"]
        }
        for bs_id in REQUIRED_BS_IDS:
            assert bs_id in calibration_by_id, (
                f"{bs_id} missing from calibration JSON at {BLIND_SPOTS_JSON}"
            )
            manifest_topic = manifest_by_id[bs_id]["topic"].lower()
            calibration_topic = calibration_by_id[bs_id]["topic"].lower()
            # Topic strings should share the prover's name at minimum.
            manifest_prover_words = {
                w for w in manifest_topic.split() if w[0:1].isupper() or len(w) > 4
            }
            calibration_prover_words = {
                w for w in calibration_topic.split() if w[0:1].isupper() or len(w) > 4
            }
            overlap = manifest_prover_words & calibration_prover_words
            assert overlap, (
                f"{bs_id}: manifest topic {manifest_topic!r} shares no "
                f"recognizable word with calibration topic {calibration_topic!r}"
            )

    def test_kc_anchors_section_exists(self, manifest: dict) -> None:
        """Probe-coverage discipline: KC anchors must also be present so
        that calibration preservation (Gate 1) can be measured against the
        BS coverage. A manifest with BS but no KC is unbalanced."""
        assert "kc_anchors" in manifest, (
            "manifest missing 'kc_anchors' section — Gate 1 calibration "
            "preservation requires positive recovery probes"
        )
        assert len(manifest["kc_anchors"]) >= 9, (
            "fewer than 9 KC anchors in manifest; pilot LoRA spec requires "
            "the 9 KC-001..KC-009 + KC-AGW-LOCK"
        )

    def test_required_bs_in_calibration_source_at_correct_count(
        self, calibration_blind_spots: dict,
    ) -> None:
        """Substrate-grade cross-check: the calibration JSON should have at
        least 6 BS entries (5 required + BS-002 deferred). If this fails,
        either a BS was removed from calibration (regression) or new BS
        haven't been integrated."""
        ids = {entry["id"] for entry in calibration_blind_spots["entries"]}
        assert REQUIRED_BS_IDS.issubset(ids), (
            f"required BS missing from calibration JSON: "
            f"{sorted(REQUIRED_BS_IDS - ids)}"
        )
