"""Portable specimen capsule (directive 6 s3): positive, missing-field, and the two cheats the directive warns about."""
from __future__ import annotations

import copy

import numpy as np

from techne.fossils import capsule

GOOD = {
    "schema": capsule.SCHEMA, "specimen_id": "asal-rollout-TEST", "written_utc": "2026-09-19T00:00:00Z", "written_by": "test",
    "source_bodies": [{"specimen": "lenia-chan-2019"}], "lineage": {"stage": "S0"}, "params": {"R": 13}, "initial_condition": {"ic": "IC-CAT:O2u"}, "seed": None,
    "frames": {"file": "x.npy", "sha256": "a" * 64, "shape": [8, 128, 128], "dtype": "uint8", "sampling": "steps 0..224"},
    "replay": {"instrument": "regen", "instrument_sha256_lf": "b" * 64, "how": "step 256"},
    "original_observer": {"score": 0.8, "identity": {"scorer": "torch clip", "weights_sha256": "c" * 64}},
    "native_observer": {"status": "PENDING", "how_to_obtain": "runbook", "score": None, "identity": None},
    "alive": True, "classification": {"class": "GENUINE_DYNAMICAL_NOVELTY", "procedure": "classify()"},
    "preservation_reason": "test", "provenance": {"experiment": "e", "rows_sha256_lf": "d" * 64, "manifest_sha256_lf": "e" * 64},
    "relatives": [], "evidence": [{"path": "p", "sha256": "f" * 64}], "observer_internals": {"status": "NOT_CAPTURED"},
}


def test_positive_capsule_validates():
    assert capsule.validate(copy.deepcopy(GOOD)) == []


def test_missing_field_is_named():
    c = copy.deepcopy(GOOD); del c["replay"]
    assert any("missing field: replay" in w for w in capsule.validate(c))


def test_cheat_native_score_without_scorer_identity_is_refused():
    c = copy.deepcopy(GOOD); c["native_observer"] = {"score": 0.79, "identity": {}}
    assert any("without a scorer identity" in w for w in capsule.validate(c))


def test_cheat_replay_as_a_bare_host_path_is_refused():
    c = copy.deepcopy(GOOD); c["replay"] = {"instrument": "C:/somewhere/frames", "instrument_sha256_lf": None, "how": ""}
    assert any("replay lacks" in w for w in capsule.validate(c))


def test_original_observer_may_not_be_pending():
    c = copy.deepcopy(GOOD); c["original_observer"] = {"status": "PENDING", "how_to_obtain": "x"}
    assert any("original_observer may not be PENDING" in w for w in capsule.validate(c))


def test_per_frame_internals_reproduce_the_score():
    rng = np.random.default_rng(1); z = rng.normal(size=(8, 512)); z /= np.linalg.norm(z, axis=-1, keepdims=True)
    d = capsule.per_frame_internals(z)
    k = np.tril(z @ z.T, k=-1); expected = float(k.max(axis=-1).mean())
    assert abs(float(np.mean(d["per_frame_max_similarity_to_earlier"])) - expected) < 1e-12
    assert d["per_frame_max_similarity_to_earlier"][0] == 0.0 and len(d["embedding_sha256_per_frame"]) == 8
