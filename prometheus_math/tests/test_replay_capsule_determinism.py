"""Test-local replay-determinism harness for KillVector / KillComponent.

Per inbox ticket T-2026-05-07-T012 (P1-high, Aporia 2026-05-07): replay
capsules must be deterministically reproducible. The substrate's
proposed ReplayCapsule primitive is at proposal stage only
(stoa/proposals/2026-04-25-aporia-replay-capsule-primitive.md) and the
``sigma_kernel/replay_capsule.py`` + ``prometheus_math/replay_engine.py``
modules referenced in the ticket's context_files don't exist yet.

This module constructs a TEST-LOCAL replay capsule that captures the
inputs needed to reproduce a kill record's content-addressed
serialization, then asserts bit-identical reproduction. NOT the
substrate's official ReplayCapsule (which is a separate, larger work);
when the official primitive lands, this test should be the first to be
rewritten against the official API.

NO contract change to KillVector / KillComponent / sigma_kernel — the
_ReplayCapsule helper lives entirely in this test module.

Bit-identical replay is the load-bearing prerequisite for every
downstream determinism guarantee:
  * Kill-cluster embeddings only stay stable if the underlying KillVector
    serializations are bit-identical across runs.
  * The Synthesizer's reproducibility-hash trigger only fires correctly
    when ``re_compute_hash(kill_record) == captured_hash``.
  * Cross-machine determinism (T-2026-05-07-T013) builds on this — a
    record that doesn't replay deterministically on one machine can't
    be expected to match on another.

Properties tested
-----------------
  1. **Per-record determinism (×20)** — for each of the 20
     ``ALL_COMPONENT_NAMES`` component types, build a representative
     KillVector, capture it, replay it, assert SHA256 equality.

  2. **Cross-replay determinism (K=10)** — replay each captured
     record 10 times; all 10 replays must produce identical SHA256
     hashes. Catches non-deterministic dict-ordering bugs.

  3. **JSON round-trip stability** — ``KillVector → to_json →
     from_json → to_json`` produces the byte-identical JSON string.

  4. **Canonical-form determinism** — two KillVectors with the same
     content (built independently) serialize to identical SHA256.
     This is the load-bearing "two machines, same code, same data,
     same hash" property.

  5. **Timing variance (soft-fail)** — record per-replay wall-time;
     report mean / std as INFORMATIONAL via pytest's stderr capture
     (never fails the test). Per acceptance criterion #4.

Acceptance criteria (per T-2026-05-07-T012):
  1. Module at prometheus_math/tests/test_replay_capsule_determinism.py  OK (file ownership)
  2. >=20 representative kill records spanning all KillVector v2 types   OK (20, one per ALL_COMPONENT_NAMES)
  3. Bit-identical reproduction (hash equality)                          OK (SHA256 over canonical JSON)
  4. Memory/timing variance as soft-fail                                 OK (timing reported, never asserts)
  5. NO contract change                                                  OK (test-local capsule)
  6. 344+ existing tests pass                                            OK (verified at commit)
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import pytest

from prometheus_math.kill_vector import (
    ALL_COMPONENT_NAMES,
    KillComponent,
    KillVector,
)


# ---------------------------------------------------------------------------
# Test-local replay capsule helper
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _ReplayCapsule:
    """TEST-LOCAL replay capsule. Captures the inputs needed to reproduce
    a KillVector's content-addressed serialization.

    Three fields:
      * ``captured_dict``: the KillVector.to_dict() output at capture time
      * ``captured_canonical_json``: the canonical-JSON serialization
        (sort_keys=True, separators tight) used as the bit-identity oracle
      * ``captured_sha256``: SHA256 over ``captured_canonical_json``

    This is INTENTIONALLY minimal — it captures only the data needed to
    reproduce the serialization, not the full ReplayCapsule the substrate
    proposal envisions (which would also capture data_snapshot_id,
    operator_versions, seed sequence, etc.). When the official
    ReplayCapsule primitive lands at sigma_kernel/replay_capsule.py, this
    helper should be deleted in favour of testing the official API.
    """

    captured_dict: Dict[str, Any]
    captured_canonical_json: str
    captured_sha256: str

    @classmethod
    def capture(cls, kv: KillVector) -> "_ReplayCapsule":
        d = kv.to_dict()
        # Strip non-content timestamp so capsule comparison is
        # content-addressed (timestamp is wall-clock at construction;
        # would otherwise spuriously vary across capture/replay calls).
        # Per ReplayCapsule proposal §"Bit-identity check": SHA256 of
        # the canonicalized output JSON, where canonicalization removes
        # incidental fields.
        d_for_hash = {k: v for k, v in d.items() if k != "timestamp"}
        canonical = json.dumps(
            d_for_hash, sort_keys=True, separators=(",", ":"), default=str
        )
        sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(
            captured_dict=d,
            captured_canonical_json=canonical,
            captured_sha256=sha,
        )

    def replay(self) -> KillVector:
        """Reconstruct the KillVector from the captured dict."""
        return KillVector.from_dict(self.captured_dict)

    def assert_deterministic(self) -> Tuple[str, str]:
        """Replay once, recompute the bit-identity oracle, assert match.

        Returns ``(captured_sha256, replayed_sha256)`` for diagnostics.
        Raises AssertionError on mismatch.
        """
        replayed_kv = self.replay()
        replayed_capsule = _ReplayCapsule.capture(replayed_kv)
        if replayed_capsule.captured_sha256 != self.captured_sha256:
            raise AssertionError(
                f"replay determinism violation:\n"
                f"  captured: {self.captured_sha256}\n"
                f"  replayed: {replayed_capsule.captured_sha256}\n"
                f"  diff_canonical_chars: "
                f"{_first_diff(self.captured_canonical_json, replayed_capsule.captured_canonical_json)}"
            )
        return self.captured_sha256, replayed_capsule.captured_sha256


def _first_diff(a: str, b: str) -> str:
    """Return a short diagnostic of the first divergent characters."""
    for i, (ca, cb) in enumerate(zip(a, b)):
        if ca != cb:
            return f"index={i} a={a[max(0,i-10):i+10]!r} b={b[max(0,i-10):i+10]!r}"
    if len(a) != len(b):
        return f"length differs: {len(a)} vs {len(b)}"
    return "no diff"


# ---------------------------------------------------------------------------
# Fixture corpus: 20 representative KillVectors, one per component type
# ---------------------------------------------------------------------------


def _representative_kill_vector_for_component(component_name: str) -> KillVector:
    """Build a KillVector containing one triggered component of the given
    type plus 1-2 untriggered other components. Margin/unit chosen
    type-appropriately so the captured serialization exercises the full
    KillComponent surface (margin / margin_unit / metadata / triggered)."""
    # Pick a margin/unit based on the component name's apparent semantics.
    if component_name.startswith("F1"):
        margin, unit = 0.97, "p_value"
    elif component_name.startswith("F6"):
        margin, unit = -2.5, "z_score"
    elif component_name.startswith("F9"):
        margin, unit = 0.18, "absolute"
    elif component_name.startswith("F11"):
        margin, unit = 0.02, "absolute"
    elif component_name.startswith("catalog:"):
        margin, unit = 0.0, "hamming"
    elif component_name in ("out_of_band", "reciprocity", "irreducibility"):
        margin, unit = 0.5, "absolute"
    else:
        # v2 component types — varied per-component
        margin, unit = 1.0, "boolean"

    triggered_comp = KillComponent(
        falsifier_name=component_name,
        triggered=True,
        margin=margin,
        margin_unit=unit,
        metadata={"k_v": "deterministic_fixture", "n": 7},
        precision_dps=30,
        method="exact",
        convergence_status="converged",
        stability=0.95,
    )
    # Add an untriggered second component to exercise multi-component path.
    other_name = next(
        n for n in ALL_COMPONENT_NAMES if n != component_name
    )
    other_comp = KillComponent(
        falsifier_name=other_name,
        triggered=False,
    )
    return KillVector(
        components=(triggered_comp, other_comp),
        candidate_hash=f"hash_{component_name}_replay_fixture",
        operator_class=f"DeterministicFixture@{component_name}",
        region_meta={"degree": 14, "alphabet": "pm5", "fixture": True},
        timestamp=0.0,  # deterministic fixed timestamp
    )


@pytest.fixture(scope="module")
def representative_capsules() -> List[Tuple[str, _ReplayCapsule]]:
    """20 representative replay capsules, one per ALL_COMPONENT_NAMES entry."""
    out: List[Tuple[str, _ReplayCapsule]] = []
    for name in ALL_COMPONENT_NAMES:
        kv = _representative_kill_vector_for_component(name)
        capsule = _ReplayCapsule.capture(kv)
        out.append((name, capsule))
    assert len(out) == 20  # acceptance #2: exactly the 20 v2 component types
    return out


# ---------------------------------------------------------------------------
# Property 1 — Per-record bit-identical replay
# ---------------------------------------------------------------------------


class TestProperty1PerRecordReplayDeterminism:
    """Per acceptance #3: bit-identical reproduction (hash equality) for
    each of the 20 representative records."""

    def test_each_of_20_records_replays_to_identical_sha256(
        self, representative_capsules: List[Tuple[str, _ReplayCapsule]],
    ) -> None:
        for name, capsule in representative_capsules:
            captured, replayed = capsule.assert_deterministic()
            assert captured == replayed, (
                f"determinism fail for {name}: {captured} vs {replayed}"
            )


# ---------------------------------------------------------------------------
# Property 2 — Cross-replay determinism (K=10 replays)
# ---------------------------------------------------------------------------


class TestProperty2CrossReplayDeterminism:
    """K=10 repeated replays per record must all produce identical SHA256.
    Catches dict-ordering / non-deterministic-iteration bugs that a
    single replay would miss."""

    K_REPLAYS = 10

    def test_k_replays_all_produce_identical_sha256(
        self, representative_capsules: List[Tuple[str, _ReplayCapsule]],
    ) -> None:
        for name, capsule in representative_capsules:
            hashes = []
            for _ in range(self.K_REPLAYS):
                replayed_kv = capsule.replay()
                replay_capsule = _ReplayCapsule.capture(replayed_kv)
                hashes.append(replay_capsule.captured_sha256)
            assert len(set(hashes)) == 1, (
                f"non-deterministic replay for {name}: {len(set(hashes))} "
                f"distinct hashes across {self.K_REPLAYS} replays. Sample: "
                f"{hashes[:3]}"
            )
            # And all match the original captured hash.
            assert hashes[0] == capsule.captured_sha256


# ---------------------------------------------------------------------------
# Property 3 — JSON round-trip byte stability
# ---------------------------------------------------------------------------


class TestProperty3JsonRoundTripStability:
    """KillVector.to_json -> from_json -> to_json must produce the
    byte-identical JSON string."""

    def test_to_json_from_json_to_json_is_byte_identical(
        self, representative_capsules: List[Tuple[str, _ReplayCapsule]],
    ) -> None:
        for name, capsule in representative_capsules:
            kv = capsule.replay()
            j1 = kv.to_json()
            kv_back = KillVector.from_json(j1)
            j2 = kv_back.to_json()
            assert j1 == j2, (
                f"to_json/from_json round-trip not byte-identical for {name}: "
                f"len(j1)={len(j1)}, len(j2)={len(j2)}, "
                f"first_diff={_first_diff(j1, j2)}"
            )


# ---------------------------------------------------------------------------
# Property 4 — Canonical-form determinism (independent constructions)
# ---------------------------------------------------------------------------


class TestProperty4CanonicalFormDeterminism:
    """Two KillVectors built independently from the same content must
    serialize to identical SHA256. Load-bearing 'two machines, same
    code + data, same hash' property."""

    def test_independent_constructions_yield_same_sha256(
        self, representative_capsules: List[Tuple[str, _ReplayCapsule]],
    ) -> None:
        for name, capsule in representative_capsules:
            kv_a = _representative_kill_vector_for_component(name)
            kv_b = _representative_kill_vector_for_component(name)
            cap_a = _ReplayCapsule.capture(kv_a)
            cap_b = _ReplayCapsule.capture(kv_b)
            assert cap_a.captured_sha256 == cap_b.captured_sha256, (
                f"independent constructions diverge for {name}: "
                f"{cap_a.captured_sha256} vs {cap_b.captured_sha256}"
            )


# ---------------------------------------------------------------------------
# Property 5 — Timing variance soft-fail (informational)
# ---------------------------------------------------------------------------


class TestProperty5TimingVarianceSoftFail:
    """Per acceptance #4: report timing variance as INFORMATIONAL.
    Never asserts on timing — the goal is observability, not gating."""

    def test_replay_timing_reported(
        self,
        representative_capsules: List[Tuple[str, _ReplayCapsule]],
        capsys: pytest.CaptureFixture,
    ) -> None:
        timings_us: List[float] = []
        for name, capsule in representative_capsules:
            t0 = time.perf_counter()
            for _ in range(5):
                _ = capsule.replay()
            elapsed_us = (time.perf_counter() - t0) * 1e6 / 5.0
            timings_us.append(elapsed_us)
        mean = sum(timings_us) / len(timings_us)
        var = sum((t - mean) ** 2 for t in timings_us) / len(timings_us)
        std = var ** 0.5
        # Print to stderr via sys.stderr (pytest's capsys captures both stdout
        # and stderr; we use stderr so it shows even with -q).
        print(
            f"\n[T012 replay-timing] mean={mean:.1f}us std={std:.1f}us "
            f"min={min(timings_us):.1f}us max={max(timings_us):.1f}us "
            f"n={len(timings_us)}",
            file=sys.stderr,
        )
        # NO assertion — timing is informational only per acceptance #4.


# ---------------------------------------------------------------------------
# Sanity: substrate-count invariant (ensures the test stays in sync)
# ---------------------------------------------------------------------------


def test_capsule_corpus_covers_all_20_v2_component_types(
    representative_capsules: List[Tuple[str, _ReplayCapsule]],
) -> None:
    """Sanity boundary: if ALL_COMPONENT_NAMES grows beyond 20, this test
    forces the determinism corpus to extend along with it."""
    names = {name for name, _ in representative_capsules}
    assert names == set(ALL_COMPONENT_NAMES), (
        f"capsule corpus drift: missing {set(ALL_COMPONENT_NAMES) - names}, "
        f"extra {names - set(ALL_COMPONENT_NAMES)}"
    )


# ---------------------------------------------------------------------------
# Sanity: capsule replay does NOT mutate the captured state
# ---------------------------------------------------------------------------


def test_replay_does_not_mutate_capsule(
    representative_capsules: List[Tuple[str, _ReplayCapsule]],
) -> None:
    """A replay must be a pure read; the capsule's captured fields must
    survive the replay unchanged."""
    for name, capsule in representative_capsules:
        original_dict = dict(capsule.captured_dict)
        original_canonical = capsule.captured_canonical_json
        original_sha = capsule.captured_sha256
        _ = capsule.replay()
        assert capsule.captured_dict == original_dict
        assert capsule.captured_canonical_json == original_canonical
        assert capsule.captured_sha256 == original_sha
