"""Tests for agora.helpers post_sync / ask_claim / tail_claims.

Pivot Move 2 (per `pivot/harmoniaD.md` §6) ships an ASK_CLAIM dispatch
convention as a substrate primitive. These tests pin the schema discipline
the helpers enforce — without requiring a live Redis. A fake Redis client
captures `xadd` calls and replays `xrevrange` from a controlled buffer.

Run: pytest agora/test_helpers.py
"""
from __future__ import annotations

import time
from typing import Any

import pytest

from agora import helpers


# ---------------------------------------------------------------------------
# Fake Redis: just enough surface for post_sync / tail_claims
# ---------------------------------------------------------------------------

class _FakeRedis:
    def __init__(self) -> None:
        self.streams: dict[str, list[tuple[str, dict[str, str]]]] = {}
        self._counter = 0

    def xadd(self, stream: str, data: dict[str, Any]) -> str:
        # Real Redis assigns IDs as <ms>-<seq>; we use a strictly-increasing
        # counter so age math stays predictable in tests.
        ms = int(time.time() * 1000) + self._counter
        self._counter += 1
        msg_id = '{}-0'.format(ms)
        # Real Redis stores all values as strings — coerce to match.
        coerced = {k: str(v) for k, v in data.items()}
        self.streams.setdefault(stream, []).append((msg_id, coerced))
        return msg_id

    def xrevrange(self, stream: str, count: int = 100) -> list[tuple[str, dict[str, str]]]:
        msgs = list(self.streams.get(stream, []))
        msgs.reverse()
        return msgs[:count]


@pytest.fixture
def fake_redis(monkeypatch):
    fake = _FakeRedis()
    monkeypatch.setattr(helpers, '_get_redis', lambda: fake)
    return fake


@pytest.fixture
def fake_qualified(monkeypatch):
    """Bypass the live qualified-instances roster check."""
    qualified = {
        'Harmonia_M2_sessionA',
        'Harmonia_M2_sessionB',
        'Harmonia_M2_sessionE',
        'Harmonia_M2_auditor',
    }
    monkeypatch.setattr(
        helpers, 'get_qualified_instances', lambda: list(qualified))
    return qualified


# ---------------------------------------------------------------------------
# post_sync schema discipline
# ---------------------------------------------------------------------------

class TestPostSync:

    def test_writes_canonical_trio(self, fake_redis, fake_qualified):
        mid = helpers.post_sync(
            'TEST_EVENT', 'a one-line subject',
            from_='Harmonia_M2_sessionE')
        assert fake_redis.streams['agora:harmonia_sync']
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert data['type'] == 'TEST_EVENT'
        assert data['from'] == 'Harmonia_M2_sessionE'
        assert data['subject'] == 'a one-line subject'
        assert mid.endswith('-0')

    def test_canonicalizes_dated_instance_name(self, fake_redis, fake_qualified):
        helpers.post_sync(
            'TEST', 's', from_='Harmonia_M2_sessionE_20260505')
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert data['from'] == 'Harmonia_M2_sessionE'

    def test_extra_fields_pass_through(self, fake_redis, fake_qualified):
        helpers.post_sync(
            'TEST', 's', from_='Harmonia_M2_sessionE',
            commit='abc123', priority=-1.5)
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert data['commit'] == 'abc123'
        assert data['priority'] == '-1.5'  # coerced to string

    def test_none_values_become_empty_string(self, fake_redis, fake_qualified):
        helpers.post_sync(
            'TEST', 's', from_='Harmonia_M2_sessionE',
            optional_field=None)
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert data['optional_field'] == ''

    def test_rejects_overwriting_reserved_keys(self, fake_redis, fake_qualified):
        # 'type' and 'from' come in via **fields, so the validator catches
        # them with ValueError. 'subject' is a named positional, so Python's
        # argument binding catches a collision with TypeError before the
        # validator runs — both behaviors are defensive against silent
        # schema drift, just by different mechanisms.
        for reserved in ('type', 'from'):
            with pytest.raises(ValueError, match='reserved'):
                helpers.post_sync(
                    'TEST', 's', from_='Harmonia_M2_sessionE',
                    **{reserved: 'sneaky'})
        with pytest.raises(TypeError, match='subject'):
            helpers.post_sync(
                'TEST', 's', from_='Harmonia_M2_sessionE',
                subject='sneaky')

    def test_rejects_unqualified_instance(self, fake_redis, fake_qualified):
        with pytest.raises(ValueError, match='qualified'):
            helpers.post_sync(
                'TEST', 's', from_='Harmonia_M2_NOT_QUALIFIED')

    @pytest.mark.parametrize('msg_type,subject', [
        ('', 'subj'),
        ('TYPE', ''),
    ])
    def test_rejects_missing_required(self, msg_type, subject,
                                       fake_redis, fake_qualified):
        with pytest.raises(ValueError):
            helpers.post_sync(
                msg_type, subject, from_='Harmonia_M2_sessionE')


# ---------------------------------------------------------------------------
# ask_claim — typed wrapper enforcing pivot Move 2 schema
# ---------------------------------------------------------------------------

class TestAskClaim:

    def test_default_emits_ask_claim_type(self, fake_redis, fake_qualified):
        helpers.ask_claim(
            'codify ASK_CLAIM helpers',
            from_='Harmonia_M2_sessionE',
            pivot_move='Move 2')
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert data['type'] == 'ASK_CLAIM'
        assert data['pivot_move'] == 'Move 2'
        assert data['track'] == ''
        assert 'codify' in data['asks']
        assert 'codify' in data['subject']
        assert data['dissent_window_min'] == '60'

    def test_session_open_combines_types(self, fake_redis, fake_qualified):
        helpers.ask_claim(
            'codify ASK_CLAIM helpers',
            from_='Harmonia_M2_sessionE',
            pivot_move='Move 2',
            session_open=True)
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert data['type'] == 'SESSION_OPEN_AND_ASK_CLAIM'

    def test_track_alternative_to_pivot_move(self, fake_redis, fake_qualified):
        helpers.ask_claim(
            'replicate F011 NULL_BSWCD on independent tooling',
            from_='Harmonia_M2_sessionE',
            track='Track D')
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert data['pivot_move'] == ''
        assert data['track'] == 'Track D'

    def test_requires_pivot_move_or_track(self, fake_redis, fake_qualified):
        with pytest.raises(ValueError, match='pivot_move OR track'):
            helpers.ask_claim(
                'something vague', from_='Harmonia_M2_sessionE')

    def test_requires_asks(self, fake_redis, fake_qualified):
        with pytest.raises(ValueError, match='asks'):
            helpers.ask_claim(
                '', from_='Harmonia_M2_sessionE', pivot_move='Move 2')

    def test_custom_dissent_window_passes_through(self, fake_redis, fake_qualified):
        helpers.ask_claim(
            'small claim',
            from_='Harmonia_M2_sessionE',
            pivot_move='Move 2',
            dissent_window_min=15)
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert data['dissent_window_min'] == '15'

    def test_long_subject_is_truncated(self, fake_redis, fake_qualified):
        long_asks = 'x' * 500
        helpers.ask_claim(
            long_asks, from_='Harmonia_M2_sessionE', pivot_move='Move 2')
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert len(data['subject']) <= 160
        assert data['asks'] == long_asks  # full asks preserved

    def test_carries_rationale_and_caveats(self, fake_redis, fake_qualified):
        helpers.ask_claim(
            'codify helpers',
            from_='Harmonia_M2_sessionE',
            pivot_move='Move 2',
            rationale='Move 1 just shipped; Move 2 is uncodified',
            caveats='4 days since last sync activity',
            addressed_to='sessionA + sessionB')
        _, data = fake_redis.streams['agora:harmonia_sync'][-1]
        assert 'shipped' in data['rationale']
        assert '4 days' in data['caveats']
        assert 'sessionA' in data['addressed_to']


# ---------------------------------------------------------------------------
# tail_claims — filters and age-window logic
# ---------------------------------------------------------------------------

class TestTailClaims:

    def test_filters_to_ask_claims_only(self, fake_redis, fake_qualified):
        helpers.post_sync('SOME_OTHER_EVENT', 'noise',
                          from_='Harmonia_M2_sessionA')
        helpers.ask_claim('do thing 1',
                          from_='Harmonia_M2_sessionA', pivot_move='Move 3')
        helpers.post_sync('ACK', 'noise2', from_='Harmonia_M2_sessionB')
        helpers.ask_claim('do thing 2',
                          from_='Harmonia_M2_sessionB', track='Track D',
                          session_open=True)

        out = helpers.tail_claims(n=10)
        assert len(out) == 2
        types = {c['type'] for c in out}
        assert types == {'ASK_CLAIM', 'SESSION_OPEN_AND_ASK_CLAIM'}

    def test_returns_newest_first(self, fake_redis, fake_qualified):
        helpers.ask_claim('first',
                          from_='Harmonia_M2_sessionA', pivot_move='M1')
        helpers.ask_claim('second',
                          from_='Harmonia_M2_sessionB', pivot_move='M2')
        out = helpers.tail_claims(n=10)
        assert out[0]['asks'] == 'second'
        assert out[1]['asks'] == 'first'

    def test_open_only_filters_expired(self, fake_redis, fake_qualified,
                                        monkeypatch):
        # Inject one fresh claim and one whose 1-min window definitely expired.
        helpers.ask_claim(
            'fresh claim',
            from_='Harmonia_M2_sessionA',
            pivot_move='M1',
            dissent_window_min=60)
        helpers.ask_claim(
            'stale claim',
            from_='Harmonia_M2_sessionB',
            pivot_move='M2',
            dissent_window_min=1)

        # Backdate the stale claim by editing its stream ID (fake-redis only).
        stream = fake_redis.streams['agora:harmonia_sync']
        # The stale claim is the second message (index 1).
        old_id, old_data = stream[1]
        backdated_ms = int(time.time() * 1000) - 3 * 60 * 1000  # 3 min old
        stream[1] = ('{}-0'.format(backdated_ms), old_data)

        all_claims = helpers.tail_claims(n=10)
        assert len(all_claims) == 2

        open_claims = helpers.tail_claims(n=10, open_only=True)
        # The 1-min window on stale claim is expired; only fresh remains.
        asks_open = [c['asks'] for c in open_claims]
        assert asks_open == ['fresh claim']

    def test_empty_when_no_claims(self, fake_redis, fake_qualified):
        helpers.post_sync('NOT_A_CLAIM', 'subj',
                          from_='Harmonia_M2_sessionA')
        out = helpers.tail_claims(n=10)
        assert out == []

    def test_carries_age_minutes(self, fake_redis, fake_qualified):
        helpers.ask_claim('x',
                          from_='Harmonia_M2_sessionA', pivot_move='M1')
        out = helpers.tail_claims(n=1)
        assert out[0]['age_min'] >= 0
        assert out[0]['age_min'] < 1  # just posted
