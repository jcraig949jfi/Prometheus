"""A1: the client must outwait the engine's lock wait, and the relationship
must be DERIVED, not two numbers that happen to match.

Measured on M1, 2026-09-10 (deploy/WRITE_PATH_PROFILE_2026-09-10.json): the
engine's configured busy wait is 30 000 ms and the wait it actually runs is
33.11 s, because SQLite's busy handler accumulates sleep time. The client's old
socket timeout was ALSO 30 s, so it abandoned a write ~3 s before the engine
did -- and the engine then committed it. Vivarium's rows that died "after the
experiment was committed" carry exactly that signature.

Three controls. Positive: the shipped default exceeds the measured overshoot.
Cheat: a default set to the engine bound itself (the old value) is REJECTED by
the same predicate, so the test can fail. Structural: the default is computed
from the engine bound, so moving one without the other trips the test.

The engine's own default is read from Store's signature rather than restated,
so this test does not touch sfe/*.py (engine_source_hash unchanged) and still
breaks if the engine bound moves without the client following.
"""
from __future__ import annotations

import inspect
import json
import os
import sys

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CLIENT_ROOT = os.path.join(os.path.dirname(_ENGINE_ROOT), "SerendipityFoundryClient")
if _CLIENT_ROOT not in sys.path:
    sys.path.insert(0, _CLIENT_ROOT)

from sfclient import client as sfclient_mod  # noqa: E402
from sfe.store import Store  # noqa: E402

PROFILE = os.path.join(_ENGINE_ROOT, "deploy", "WRITE_PATH_PROFILE_2026-09-10.json")


def _engine_default_timeout() -> float:
    return float(inspect.signature(Store.__init__).parameters["timeout"].default)


def _measured_overshoot_s() -> float:
    with open(PROFILE, encoding="utf-8") as fh:
        return float(json.load(fh)["deadlines"]["engine_lock_wait_s"])


def _client_outwaits_engine(client_timeout: float) -> bool:
    return client_timeout > _measured_overshoot_s() > 0


def test_client_constant_tracks_engine_default():
    # The number the client believes about the engine IS the engine's number.
    assert sfclient_mod.ENGINE_BUSY_TIMEOUT_S == _engine_default_timeout()


def test_default_timeout_exceeds_measured_engine_lock_wait():
    # Positive control: the shipped default clears the measured 33.11 s.
    assert _client_outwaits_engine(sfclient_mod.DEFAULT_TIMEOUT_S)
    assert sfclient_mod.DEFAULT_TIMEOUT_S == \
        sfclient_mod.ENGINE_BUSY_TIMEOUT_S * sfclient_mod.DEADLINE_MARGIN


def test_engine_client_uses_the_derived_default():
    ec = sfclient_mod.EngineClient("http://x")
    assert ec.timeout == sfclient_mod.DEFAULT_TIMEOUT_S


def test_cheat_control_old_default_is_rejected():
    # The value shipped before A1 -- equal to the engine bound -- must FAIL the
    # predicate, or the predicate measures nothing.
    assert not _client_outwaits_engine(_engine_default_timeout())


def test_margin_covers_the_overshoot_with_room():
    # The overshoot is ~10% today; the margin is 50%. If the measurement ever
    # exceeds the margin, this is the line to read before touching numbers.
    assert _measured_overshoot_s() < sfclient_mod.DEFAULT_TIMEOUT_S * 0.9
