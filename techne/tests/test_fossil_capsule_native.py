"""TECHNE-115 close: the native (Flax) observer column enters EXISTING capsules by touching two cells.

Harmonia landed HARM55_FLAX_NATIVE_2026-09-30.json (HARM-55/56 closed at 68036a8ae). `capsule build`
would rebuild whole capsules and drop the captured original-observer internals, so `fill-native`
exists. Controls:

  positive   a PENDING capsule + a Flax file with its key -> FILLED, score + scorer identity present,
             and NOTHING ELSE in the capsule differs
  negative   a Flax file without the key -> NO_SCORE, capsule unchanged, still PENDING
  cheat      a capsule that already carries a DIFFERENT native score -> CONFLICT, unchanged
             (a second Flax file must never silently replace a recorded score)
  idempotent the same score again -> ALREADY, unchanged
  tree       every tracked rollout capsule's native score equals the committed Flax file's score for
             its key, names that file with its sha256, and keeps its observer internals
"""
import copy
import json

import pytest

from techne.fossils import capsule, vault

FLAX = vault.REPO / "techne" / "acquisition" / "poet_alife" / "HARM55_FLAX_NATIVE_2026-09-30.json"
CAPSULES = sorted(vault.SPECIMENS.glob("asal-rollout-*/CAPSULE.json"))

IDENT = {"scorer": "s", "jax": "0", "jaxlib": "0", "flax": "0", "transformers": "0", "model": "m",
         "weights_files_sha256": {"w": "a" * 64}, "body_commit": "c", "body_tree_sha256": "t"}


def _flax(score=0.5, key="S9_1"):
    return {"identity": dict(IDENT), "scores": {key: score},
            "rows": {key: {"crossings_flax": {"garbage_mean": True}, "d_clip_flax": 0.1, "class_flax": "K", "signed_diff": 1e-7}},
            "_source_path": "x/flax.json", "_source_sha256_lf": "f" * 64}


def _pending():
    return {"specimen_id": "asal-rollout-S9_1", "native_observer": capsule.native_block("S9_1", None),
            "classification": {"class": "K", "procedure": "p", "class_under_native_observer": "PENDING"},
            "observer_internals": {"status": "PRESENT", "per_frame_max_similarity_to_earlier": [0.0, 0.9]},
            "original_observer": {"score": 0.5}, "preservation_reason": "r"}


def test_positive_fill_touches_two_cells_and_nothing_else():
    c = _pending()
    before = copy.deepcopy(c)
    out, status = capsule.fill_native(c, _flax())
    assert status == "FILLED"
    assert c == before                                           # the input is not mutated
    n = out["native_observer"]
    assert n["score"] == 0.5 and n["identity"]["scorer"] == "s" and n["identity"]["weights_files_sha256"]
    assert n["source_file"] == "x/flax.json" and n["source_file_sha256_lf"] == "f" * 64
    assert out["classification"]["class_under_native_observer"] == "K"
    rest = lambda d: {k: v for k, v in d.items() if k not in ("native_observer", "classification")}
    assert rest(out) == rest(before)
    assert {k: v for k, v in out["classification"].items() if k != "class_under_native_observer"} == \
           {k: v for k, v in before["classification"].items() if k != "class_under_native_observer"}


def test_negative_no_score_for_this_key_stays_pending():
    c = _pending()
    out, status = capsule.fill_native(c, _flax(key="S9_2"))
    assert status == "NO_SCORE" and out == c and out["native_observer"]["status"] == "PENDING"


def test_cheat_control_a_different_recorded_score_is_never_replaced():
    filled, _ = capsule.fill_native(_pending(), _flax(score=0.5))
    out, status = capsule.fill_native(filled, _flax(score=0.75))
    assert status == "CONFLICT" and out == filled and out["native_observer"]["score"] == 0.5


def test_idempotent_same_score_again():
    filled, _ = capsule.fill_native(_pending(), _flax(score=0.5))
    out, status = capsule.fill_native(filled, _flax(score=0.5))
    assert status == "ALREADY" and out == filled


@pytest.mark.skipif(not (FLAX.exists() and CAPSULES), reason="no Flax column or no capsules on this tree")
def test_tracked_capsules_carry_the_committed_flax_column():
    flax = json.loads(FLAX.read_text(encoding="utf-8"))
    sha = capsule.lf_sha256(FLAX)
    bad = []
    for p in CAPSULES:
        c = json.loads(p.read_text(encoding="utf-8"))
        key = c["specimen_id"][len("asal-rollout-"):]
        n = c["native_observer"]
        if key not in flax["scores"]:
            continue
        if n.get("score") != flax["scores"][key]:
            bad.append((key, "native score %r != Flax file %r" % (n.get("score"), flax["scores"][key])))
        elif n.get("source_file_sha256_lf") != sha:
            bad.append((key, "does not name the Flax file by sha256"))
        elif c["classification"].get("class_under_native_observer") in (None, "PENDING"):
            bad.append((key, "class_under_native_observer not filled"))
        if capsule.validate(c):
            bad.append((key, capsule.validate(c)))
    assert not bad, bad[:5]
