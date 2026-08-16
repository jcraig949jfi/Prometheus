"""Tests for the F-generic specificity control (Charon's contract).

Two of these are the arm's actual guarantees rather than unit tests: `test_no_verdict_tokens`
(the text can never collide with the frozen extractor) and `test_no_repetition_padding` (the
match is never bought with repeated advice). If either fails, the arm is not admissible.
"""

from __future__ import annotations

import pytest

from ergon.probe.assemble import count_tokens
from ergon.probe.extract import _VERDICT_TOKEN
from ergon.probe.f_generic import (
    DEFAULT_TOLERANCE,
    PRINCIPLES,
    PREAMBLE,
    GenericPacket,
    pool_tokens,
    render_all,
    render_f_generic,
    units,
)

# --------------------------------------------------------------------------- text contract


def test_no_verdict_tokens():
    """Zero whole-word true/false anywhere. The frozen extractor must never fire on this arm."""
    assert _VERDICT_TOKEN.search(render_all()) is None


def test_every_principle_has_every_tier():
    for i, principle in enumerate(PRINCIPLES, start=1):
        for tier in ("headline", "note", "signature", "check"):
            assert principle[tier].strip(), f"principle {i} missing {tier}"


def test_units_are_unique_and_ordered_tier_major():
    uids = [u.uid for u in units()]
    assert len(uids) == len(set(uids))
    assert uids[0] == "preamble"
    n = len(PRINCIPLES)
    # tier-major: every headline precedes the first elaboration
    assert uids[1 : n + 1] == [f"headline:{i}" for i in range(1, n + 1)]
    assert uids[n + 1] == "note:1"


def test_no_repetition_padding():
    """No unit text appears twice in the full render — length is never bought by repeating."""
    texts = [u.text for u in units()]
    assert len(texts) == len(set(texts))


def test_render_is_deterministic():
    assert render_all() == render_all()
    a, b = render_f_generic(2000), render_f_generic(2000)
    assert (a.text, a.tokens, a.status) == (b.text, b.tokens, b.status)


# --------------------------------------------------------------------------- matching


@pytest.mark.parametrize(
    "target", [120, 300, 700, 1500, 2400, 3300, 4200, 5600, 6800, 8000, 8400]
)
def test_matches_within_tolerance(target):
    pkt = render_f_generic(target)
    assert pkt.status == "MATCHED", f"{target} -> {pkt.status} at {pkt.tokens} tokens"
    assert target * (1 - DEFAULT_TOLERANCE) <= pkt.tokens <= target * (1 + DEFAULT_TOLERANCE)


def test_never_exceeds_ceiling_at_any_target():
    """The +5% ceiling is hard at every target from tiny to well past the pool."""
    for target in range(20, 9000, 37):
        pkt = render_f_generic(target)
        assert pkt.tokens <= target * (1 + DEFAULT_TOLERANCE) + 1e-9, target


def test_saturates_rather_than_padding():
    """Beyond the pool, the arm reports SATURATED — it does not repeat itself to fill."""
    pkt = render_f_generic(pool_tokens() * 3)
    assert pkt.status == "SATURATED"
    assert pkt.text == render_all()


def test_under_floor_for_tiny_targets():
    pkt = render_f_generic(1)
    assert pkt.status == "UNDER-FLOOR"
    assert pkt.text == ""


def test_status_vocabulary_is_closed():
    allowed = {"MATCHED", "SATURATED", "UNDER-FLOOR", "UNMATCHABLE-GRANULARITY"}
    for target in range(5, 8500, 53):
        assert render_f_generic(target).status in allowed


def test_only_matched_is_admissible():
    assert render_f_generic(2000).matched is True
    assert render_f_generic(pool_tokens() * 3).matched is False


def test_strongest_material_is_always_present_first():
    """Growth adds weaker material; it never displaces the top of the priority order."""
    short = render_f_generic(400)
    long = render_f_generic(3000)
    assert short.unit_ids == long.unit_ids[: len(short.unit_ids)]
    assert PREAMBLE in short.text


def test_header_is_auditable():
    pkt = render_f_generic(1200)
    hdr = pkt.header()
    assert hdr["arm"] == "F-generic"
    assert hdr["target_tokens"] == 1200
    assert hdr["tokens"] == count_tokens(pkt.text)
    assert hdr["status"] == "MATCHED"


def test_zero_target_rejected():
    with pytest.raises(ValueError):
        render_f_generic(0)


def test_packet_is_plain_data():
    assert isinstance(render_f_generic(900), GenericPacket)
