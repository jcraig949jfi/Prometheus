"""NYX_PREDICTION_PACKET schema: the frozen packets still validate and hash to their FREEZE files; novelty_kind
(Harmonia #381 ASK H4, 2026-09-18) is optional, vocabulary-checked when present."""
import copy
import json
from pathlib import Path

from nyx.atlas.predictions import schema as ps

ROOT = Path(__file__).resolve().parents[1] / "atlas" / "predictions"


def _load(pid):
    return json.loads((ROOT / f"{pid}.json").read_text(encoding="utf-8"))


def test_frozen_packets_validate_and_match_their_freeze_files():
    for pid in ("MECH-PARTICLES-ESSTRIGGER-001", "MECH-PARTICLES-ESSTRIGGER-002"):
        p = _load(pid)
        assert ps.validate(p) == []
        frozen = (ROOT / f"{pid}.FREEZE").read_text(encoding="utf-8").split()[0]
        assert ps.packet_hash(p) == frozen, pid


def test_novelty_kind_optional_but_vocabulary_checked():
    p = _load("MECH-PARTICLES-ESSTRIGGER-002")
    q = copy.deepcopy(p)
    q["interventions"][0]["novelty_kind"] = "behavior"
    assert ps.validate(q) == []
    bad = copy.deepcopy(p)
    bad["interventions"][0]["novelty_kind"] = "novel"
    errs = ps.validate(bad)
    assert any("novelty_kind" in x for x in errs)
    assert set(ps.NOVELTY_KINDS) == {"structure", "behavior", "observer", "consequential"}
